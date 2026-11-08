"""Content-addressed immutable raw archive, retrieval journal, and GP rate guard."""
import hashlib
import json
import os
from pathlib import Path
from datetime import datetime, timezone
import requests
from .rinex import read_rinex
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
        self.session.headers["User-Agent"] = "NavIC-Orbit-Consistency/0.1 scientific comparison"

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
        now = datetime.now(timezone.utc).timestamp()
        if gp and now-state.get("last_attempt",0) < 7200:
            if "record" not in state: raise ValueError("GP poll guard: last request failed; wait two hours")
            return {**state["record"], "cache_reused":True}
        headers = {}
        if state.get("etag"): headers["If-None-Match"] = state["etag"]
        if state.get("modified"): headers["If-Modified-Since"] = state["modified"]
        # Persist attempt before I/O, including failures, to prevent abusive retry loops.
        state["last_attempt"] = now
        atomic_json(state_path,state)
        response = self.session.get(url,headers=headers,timeout=60)
        if response.status_code == 304 and "record" in state:
            record = {**state["record"], "validated_at":datetime.now(timezone.utc).isoformat(), "not_modified":True}
            with (self.root/"retrievals.jsonl").open("a",encoding="utf-8") as f: f.write(json.dumps(record)+"\n")
            state["record"] = record; atomic_json(state_path,state)
            return record
        response.raise_for_status()
        record = self.archive(response.content,suffix,url)
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
