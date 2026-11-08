"""Content-addressed immutable raw archive, retrieval journal, and GP rate guard."""
import hashlib
import json
import os
from pathlib import Path
from datetime import datetime, timezone
from html.parser import HTMLParser
from urllib.parse import urljoin
import re
import statistics
import requests
from .rinex import read_rinex,select_ephemeris,valid_issue
from .orbits import parse_gp

def atomic_json(path, value):
    path = Path(path); path.parent.mkdir(parents=True,exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(value, indent=2, allow_nan=False), encoding="utf-8")
    temp.replace(path)

class Archive:
    def __init__(self, root):
        self.root = Path(root); self.root.mkdir(parents=True,exist_ok=True)
        self.session = requests.Session()
        self.session.headers["User-Agent"] = "NavIC-Orbit-Consistency/0.3 scientific comparison"

    def archive(self, content, suffix, url, metadata=None):
        sha = hashlib.sha256(content).hexdigest()
        path = self.root / "raw" / f"{sha}{suffix}"
        path.parent.mkdir(parents=True,exist_ok=True)
        if not path.exists():
            with path.open("xb") as f: f.write(content)
        elif hashlib.sha256(path.read_bytes()).hexdigest() != sha:
            raise ValueError("Immutable raw archive hash mismatch")
        record = {"sha256": sha, "path": str(path.resolve()), "source":url,
                  "retrieved_at":datetime.now(timezone.utc).isoformat(), **(metadata or {})}
        journal = self.root / "retrievals.jsonl"
        with journal.open("a",encoding="utf-8") as f: f.write(json.dumps(record)+"\n")
        return record

    def fetch(self, url, suffix, gp=False):
        key = hashlib.sha256(url.encode()).hexdigest()
        state_path = self.root / "cache" / f"{key}.json"
        state = json.loads(state_path.read_text()) if state_path.exists() else {}
        def cached_record():
            record=state.get('record')
            if not record: raise ValueError('HTTP cache has no archived body')
            path=Path(record['path'])
            if not path.exists(): path=self.root/'raw'/path.name
            if not path.exists() or hashlib.sha256(path.read_bytes()).hexdigest()!=record['sha256']:
                raise ValueError('Cached archive is missing or its checksum changed')
            return {**record,'path':str(path.resolve())}
        now = datetime.now(timezone.utc).timestamp()
        if gp and now-state.get("last_attempt",0) < 7200:
            if "record" not in state: raise ValueError("GP poll guard: last request failed; wait two hours")
            return {**cached_record(), "cache_reused":True}
        headers = {}
        if state.get("etag"): headers["If-None-Match"] = state["etag"]
        if state.get("modified"): headers["If-Modified-Since"] = state["modified"]
        # Persist attempt before I/O, including failures, to prevent abusive retry loops.
        state["last_attempt"] = now
        atomic_json(state_path,state)
        response = self.session.get(url,headers=headers,timeout=60)
        if response.status_code == 304:
            record = {**cached_record(), "validated_at":datetime.now(timezone.utc).isoformat(), "not_modified":True,'http_status':304}
            with (self.root/"retrievals.jsonl").open("a",encoding="utf-8") as f: f.write(json.dumps(record)+"\n")
            state["record"] = record; atomic_json(state_path,state)
            return record
        response.raise_for_status()
        digest=hashlib.sha256(response.content).hexdigest()
        first=state.get('record',{}).get('first_received_at',state.get('record',{}).get('retrieved_at')) if state.get('record',{}).get('sha256')==digest else None
        record = self.archive(response.content,suffix,url,{
            'http_status':response.status_code,'http_etag':response.headers.get('ETag'),
            'server_last_modified':response.headers.get('Last-Modified'),
            'first_received_at':first or datetime.now(timezone.utc).isoformat()})
        state.update(record=record,etag=response.headers.get("ETag"),modified=response.headers.get("Last-Modified"))
        atomic_json(state_path,state)
        return record

def acquire(day, config, root):
    archive = Archive(root)
    trials, rinex = [], None
    for template in config["sources"]:
        url = template.format(year=day.year,doy=f"{day.timetuple().tm_yday:03}")
        try:
            candidate = archive.fetch(url,".rnx.gz")
            records, header = read_rinex(candidate["path"])
            rinex = candidate
            trials.append({"url":url,"accepted":True,"navic_records":sum(e.prn[0]=="I" for e in records)})
            break
        except (requests.RequestException,ValueError,OSError,EOFError) as exc:
            trials.append({"url":url,"accepted":False,"error":str(exc)})
    atomic_json(Path(root)/"acquisition.json",{"day":str(day),"attempts":trials})
    # Archive GP even when BRDC is unavailable; tomorrow's retrospective job needs it.
    gp = archive.fetch(config["gp_url"],".omm.json",gp=True)
    parse_gp(gp["path"])
    eop = archive.fetch(config["eop_url"],".iers")
    leaps = archive.fetch(config["leaps_url"],".leaps")
    if not rinex: raise ValueError("All broadcast sources failed validation; see data/acquisition.json")
    return {"rinex":rinex,"gp":[gp],"eop":eop,"leaps":leaps,"acquisition_attempts":trials}

class DirectoryLinks(HTMLParser):
    def __init__(self): super().__init__();self.links=[]
    def handle_starttag(self,tag,attrs):
        if tag.lower()=='a': self.links.extend(value for key,value in attrs if key=='href' and value)

def discover_current_files(html,day):
    parser=DirectoryLinks();parser.feed(html)
    stamp=f'{day.year}{day.timetuple().tm_yday:03}'
    pattern=rf'^(?:BRDC|BRDM)00[A-Z0-9]{{3}}_[RSU]_{stamp}\d{{4}}_(?:01D|01H)_MN\.rnx\.gz$'
    names={name for name in parser.links if re.fullmatch(pattern,name)}
    def priority(name):
        return (0 if name.startswith('BRDC00WRD_S_') else 1 if name.startswith('BRDC00WRD_R_') else 2,name)
    return sorted(names,key=priority)

def assess_current_records(records,now,config):
    from astropy.time import Time
    moment=Time(now)
    satellites=[]
    for prn in sorted({e.prn for e in records if e.prn.startswith('I')}):
        group=[e for e in records if e.prn==prn]
        chosen,flags=select_ephemeris(group,moment,config['broadcast_max_age_seconds'])
        reference=chosen or min(group,key=lambda e:abs(e.toe_gps-float(moment.gps)))
        latest=max(group,key=lambda e:e.toc_gps)
        if reference.health and 'broadcast_unhealthy' not in flags:flags.append('broadcast_unhealthy')
        if reference.ura>=8192 and 'broadcast_ura_unavailable' not in flags:flags.append('broadcast_ura_unavailable')
        if not valid_issue(reference) and 'iodec_reserved' not in flags:flags.append('iodec_reserved')
        satellites.append({'prn':prn,'usable_now':chosen is not None,'flags':flags,
                           'toc_utc':reference.toc.utc.isot+'Z','toe_utc':reference.toe.utc.isot+'Z',
                           'latest_toc_utc':latest.toc.utc.isot+'Z','toe_age_seconds':float((moment-reference.toe).sec),
                           'iodec':reference.iode,'health':reference.health,'ura_m':reference.ura,
                           'ephemeris_key':reference.key,'record_count':len(group)})
    ages=[abs(s['toe_age_seconds']) for s in satellites if s['usable_now']]
    return {'checked_at':now.isoformat(),'satellites':satellites,'satellites_present':len(satellites),
            'usable_satellites':len(ages),'max_usable_toe_age_seconds':max(ages) if ages else None,
            'median_usable_toe_age_seconds':statistics.median(ages) if ages else None,
            'validity_limit_seconds':config['broadcast_max_age_seconds'],
            'validity_basis':config['broadcast_window_basis'],
            'validity_status':'analysis policy only; no independently confirmed ICD fit-interval guarantee',
            'time_assumption':'IRN nominal GPS relationship with pinned/bundled leap handling; available IRUT header correction applied'}

def acquire_current_nav(config,root,now=None):
    """Discover actual UTC-day filenames; never accept an empty/stale-only product."""
    live=now is None
    now=now or datetime.now(timezone.utc)
    if now.tzinfo is None: raise ValueError('Current acquisition needs an aware UTC time')
    now=now.astimezone(timezone.utc);day=now.date()
    archive=Archive(root)
    template=config.get('current_acquisition',{}).get('directory','https://igs.bkg.bund.de/root_ftp/IGS/BRDC/{year}/{doy}/')
    directory=template.format(year=day.year,doy=f'{day.timetuple().tm_yday:03}')
    listing=archive.fetch(directory,'.directory.html')
    names=discover_current_files(Path(listing['path']).read_text(encoding='utf-8'),day)
    attempts=[];candidates=[];parsed=[]
    for name in names:
        url=urljoin(directory,name)
        try:
            record=archive.fetch(url,'.rnx.gz')
            records,header=read_rinex(record['path'],systems='I')
            trial={'source':url,'sha256':record['sha256']}
            attempts.append(trial)
            parsed.append((name,record,records,header,trial))
        except (requests.RequestException,ValueError,OSError,EOFError) as exc:
            attempts.append({'source':url,'accepted':False,'error':str(exc)})
    # Assess every candidate at one physical instant after downloads finish.
    checked=datetime.now(timezone.utc) if live else now
    for name,record,records,header,trial in parsed:
        quality=assess_current_records(records,checked,config)
        accepted=quality['usable_satellites']>=config.get('current_acquisition',{}).get('minimum_usable_satellites',1)
        trial.update(accepted=accepted,assessment=quality)
        if accepted:
            score=(quality['usable_satellites'],-quality['max_usable_toe_age_seconds'],
                   -quality['median_usable_toe_age_seconds'],-names.index(name))
            candidates.append((score,record,quality,header))
    selected=max(candidates,key=lambda item:item[0]) if candidates else None
    record=selected[1] if selected else None
    report={'schema_version':'1.0.0','mode':'current-day acquisition','day_utc':str(day),
            'checked_at':selected[2]['checked_at'] if selected else now.isoformat(),'directory':directory,'directory_sha256':listing['sha256'],
            'discovered_files':names,'attempts':attempts,'accepted':selected is not None,
            'selected_input':record,'freshness':selected[2] if selected else None,
            'selection_rule':'most usable NavIC satellites, then smallest maximum and median absolute toe age; deterministic filename priority breaks ties',
            'notes':['A new HTTP download or modification timestamp does not establish a new ephemeris.',
                     'Unusable satellites remain individual gaps; healthy satellites in the same file can still be used.',
                     'Actual first file receipt is archived. A past toc/toe is not proof of past availability.']}
    atomic_json(Path(root)/'acquisition-current.json',report)
    stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    immutable=Path(root)/'acquisitions'/(stamp+'.json')
    immutable.parent.mkdir(parents=True,exist_ok=True)
    with immutable.open('x',encoding='utf-8') as stream: json.dump(report,stream,indent=2,allow_nan=False)
    if not selected: raise ValueError('No current-day file contains usable NavIC ephemerides; inspect acquisition-current.json')
    return record,report
