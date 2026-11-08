"""Current-day input assessment and controlled retrospective recency experiment."""
import csv
import hashlib
import json
import shutil
from pathlib import Path
from datetime import datetime,timezone,timedelta
from importlib.metadata import version
import numpy as np
from astropy.time import Time,TimeDelta
from .acquire import Archive,atomic_json,acquire_current_nav
from .rinex import read_rinex,select_ephemeris
from .timeframes import pinned_orientation,check_eop
from .fitting import target_state,osculating_seed,fit_mean_elements,propagate,metrics,export_omm
from .orbits import parse_gp,select_gp
from .pipeline import clean,sha

def targets(records,times,config,cutoff=None):
    allowed=[e for e in records if cutoff is None or e.toc_gps<=float(cutoff.gps)]
    positions=np.full((len(times),3),np.nan);velocities=positions.copy();flags=[];batches={}
    for i,t in enumerate(times):
        e,notes=select_ephemeris(allowed,t,config['broadcast_max_age_seconds']);flags.append(notes)
        if e: batches.setdefault(e.key,(e,[]))[1].append(i)
    for e,idx in batches.values():positions[idx],velocities[idx]=target_state(e,times[idx])
    return positions,velocities,flags

def fit_at_cutoff(records,cutoff,config,norad):
    policy=config['current_acquisition'];hours=policy['benchmark_train_hours'];step=policy['benchmark_step_seconds']
    times=cutoff+TimeDelta(np.arange(-hours*3600,0,step),format='sec')
    p,v,flags=targets(records,times,config,cutoff)
    valid=np.isfinite(p).all(axis=1)
    coverage=float(valid.mean())
    if coverage<policy['minimum_train_coverage'] or valid.sum()<12:
        return None,{'status':'insufficient_training_coverage','coverage_percent':100*coverage,'epochs':int(valid.sum())}
    first=np.flatnonzero(valid)[0]
    seed=osculating_seed(p[first],v[first])
    # This only initializes the optimizer; final elements are fitted at the issue epoch.
    seed[0]+=np.exp(seed[5])*2*np.pi*(cutoff-times[first]).sec/86400
    sat,diagnostics=fit_mean_elements(times[valid],p[valid],seed,cutoff,norad,policy['max_nfev'])
    delta=propagate(sat,times[valid])-p[valid]
    fit=metrics(delta,times[valid])
    ok=diagnostics['success'] and diagnostics['jacobian_rank']==6 and sat.method=='d'
    return sat if ok else None,{'status':'fitted' if ok else 'optimizer_rejected','epoch_utc':cutoff.utc.isot+'Z',
        'train_start_utc':times[0].utc.isot+'Z','train_end_exclusive_utc':cutoff.utc.isot+'Z',
        'coverage_percent':100*coverage,'fit':fit,'optimizer':diagnostics}

def supporting_inputs(archive,config):
    gp=archive.fetch(config['gp_url'],'.omm.json',gp=True);parse_gp(gp['path'])
    eop=archive.fetch(config['eop_url'],'.iers');leaps=archive.fetch(config['leaps_url'],'.leaps')
    # Earliest receipt of each content snapshot is retained for issue-time GP selection.
    journal=[json.loads(line) for line in (archive.root/'retrievals.jsonl').read_text(encoding='utf-8').splitlines()]
    gps={}
    for item in journal:
        if item['path'].endswith('.omm.json'):gps.setdefault(item['sha256'],item)
    return {'gp':list(gps.values()),'eop':eop,'leaps':leaps},journal

def historical_navigation(journal,current,day):
    seen=set();selected=[]
    # One immutable previous-day file is enough for the default 6h delayed control.
    previous=(day-timedelta(days=1)).strftime('%Y%j')
    for item in reversed(journal):
        if previous not in item.get('source','') or not item['path'].endswith('.rnx.gz') or item['sha256'] in seen:continue
        seen.add(item['sha256'])
        try:
            records,_=read_rinex(item['path'],systems='I')
            records=[e for e in records if e.prn.startswith('I') and e.toc.utc.isot[:10]<str(day)]
            if records: return records,[item]
        except (OSError,ValueError,EOFError):continue
    return [],selected

def benchmark_recency(records,identities,gps,gp_metadata,asof,config):
    policy=config['current_acquisition'];step=policy['benchmark_step_seconds']
    moment=Time(asof)
    midnight=Time(moment.utc.isot[:10],scale='utc')
    end=midnight+TimeDelta(np.floor((moment-midnight).sec/step)*step,format='sec')
    origin=end-TimeDelta(policy['benchmark_holdout_hours']*3600,format='sec')
    stale_origin=origin-TimeDelta(policy['benchmark_stale_delay_hours']*3600,format='sec')
    times=origin+TimeDelta(np.arange(0,policy['benchmark_holdout_hours']*3600+1e-6,step),format='sec')
    result={'mode':'retrospective controlled input-recency experiment','availability_proven':False,
        'forecast_origin_utc':origin.utc.isot+'Z','validation_end_utc':end.utc.isot+'Z',
        'train_hours':policy['benchmark_train_hours'],'holdout_hours':policy['benchmark_holdout_hours'],
        'delayed_input_hours':policy['benchmark_stale_delay_hours'],'step_seconds':step,'satellites':[],
        'interpretation':'Broadcast agreement only. Current file receipt occurred after the retrospective forecast origin; this is not a verified live forecast or an absolute accuracy assessment.'}
    residuals=[];models=[]
    received={meta['sha256']:Time(datetime.fromisoformat(meta.get('first_received_at') or meta['retrieved_at'])) for meta in gp_metadata if meta.get('first_received_at') or meta.get('retrieved_at')}
    for identity in identities:
        prn=identity['prn'];group=[e for e in records if e.prn==prn]
        item={k:identity.get(k) for k in ('prn','norad_id','name','orbit_class')}
        p,v,flags=targets(group,times,config)
        valid=np.isfinite(p).all(axis=1)
        item.update(reference_epochs=int(valid.sum()),total_epochs=len(times),models={},comparison=None)
        if not identity.get('norad_id'):
            item['reason']='identity_not_in_registry';result['satellites'].append(item);continue
        propagated={}
        for label,cutoff in [('fresh',origin),('delayed',stale_origin)]:
            try:
                sat,info=fit_at_cutoff(group,cutoff,config,identity['norad_id'])
                item['models'][label]=info
                if sat is not None and valid.any():
                    delta=propagate(sat,times[valid])-p[valid]
                    info['validation']=metrics(delta,times[valid]);propagated[label]=delta
                    candidate=export_omm(sat,cutoff,identity,gps)
                    candidate['COMMENT']+=' Retrospective freshness experiment only; source availability at the historical issue time is unproven. Not an operational release.'
                    models.append({'prn':prn,'cohort':label,'omm':candidate})
            except (ValueError,FloatingPointError) as exc:item['models'][label]={'status':'failed','error':str(exc)}
        if valid.mean()<policy['minimum_holdout_coverage']:
            item['reason']='insufficient_common_holdout_coverage'
        elif 'fresh' in propagated and 'delayed' in propagated:
            fresh=item['models']['fresh']['validation']['rms_km'];old=item['models']['delayed']['validation']['rms_km']
            item['comparison']={'common_epochs':int(valid.sum()),'fresh_rms_km':fresh,'delayed_rms_km':old,
                'rms_reduction_percent':100*(old-fresh)/old if old>0 else None,
                'fresh_has_lower_broadcast_disagreement':bool(fresh<old)}
        available=[g for g in gps if g.norad==identity['norad_id'] and g.snapshot in received and received[g.snapshot]<=origin]
        gp,_=select_gp(available,origin,config['gp_max_age_hours'],False)
        if gp and valid.any():
            codes,position,_=gp.sat.sgp4_array(times[valid].utc.jd1,times[valid].utc.jd2)
            if not np.any(codes):
                propagated['standard_gp']=position-p[valid]
                item['standard_gp']={'metrics':metrics(propagated['standard_gp'],times[valid]),
                    'element_id':gp.element_id,'snapshot_sha256':gp.snapshot,'epoch_utc':gp.epoch.utc.isot+'Z',
                    'age_at_issue_hours':float((origin-gp.epoch).sec/3600),'received_before_issue':True}
        if 'standard_gp' not in item:item['standard_gp']={'status':'no_eligible_snapshot_received_before_origin'}
        for j,i in enumerate(np.flatnonzero(valid)):
            for cohort,delta in propagated.items():
                r=p[i]/np.linalg.norm(p[i]);normal=np.cross(p[i],v[i]);normal/=np.linalg.norm(normal);along=np.cross(normal,r)
                residuals.append({'prn':prn,'utc':times[i].utc.isot+'Z','cohort':cohort,'separation_km':float(np.linalg.norm(delta[j])),
                    'radial_km':float(delta[j]@r),'along_km':float(delta[j]@along),'cross_km':float(delta[j]@normal)})
        result['satellites'].append(item)
    pairs=[s['comparison'] for s in result['satellites'] if s.get('comparison')]
    result['comparable_satellites']=len(pairs)
    result['fresh_lower_disagreement_count']=sum(p['fresh_has_lower_broadcast_disagreement'] for p in pairs)
    return result,residuals,models

def run_current(config,root='data',output='results/fresh',dashboard='dashboard/dist',acquire_only=False):
    selected,acquisition=acquire_current_nav(config,root)
    archive=Archive(root)
    support,journal=supporting_inputs(archive,config)
    current_records,_=read_rinex(selected['path'],systems='I')
    now=datetime.now(timezone.utc)
    history,history_inputs=historical_navigation(journal,selected,now.date())
    records=[e for e in current_records if e.prn.startswith('I')]+history
    prns=sorted({e.prn for e in current_records if e.prn.startswith('I')})
    registry=config.get('identity_catalogue',{})
    identities=[{'prn':prn,**registry.get(prn,{'norad_id':None,'name':'Unconfirmed identity','orbit_class':None})} for prn in prns]
    gp=sum([parse_gp(meta['path']) for meta in support['gp']],[])
    with pinned_orientation(support['eop']['path'],support['leaps']['path']) as eop:
        check_eop(Time(now),eop)
        # The supporting leap table must remain valid through this live assessment.
        from astropy.utils import iers
        if iers.LeapSeconds.open(support['leaps']['path']).expires<Time(now):raise ValueError('Leap-second table expired')
        benchmark,residuals,models=benchmark_recency(records,identities,gp,support['gp'],now,config) if not acquire_only else ({'mode':'not requested'},[],[])
    report=clean({'schema_version':'1.0.0','generated_at':now.isoformat(),'acquisition':acquisition,'benchmark':benchmark,
        'inputs':{'rinex':selected,'historical_rinex':history_inputs,**support},'config':config,
        'code_sha256':hashlib.sha256(b''.join(p.read_bytes() for p in sorted(Path(__file__).parent.glob('*.py')))).hexdigest(),
        'software':{name:version(name) for name in ('numpy','astropy','pyerfa','sgp4','scipy','requests')}})
    run_id=now.strftime('%Y%m%dT%H%M%S%fZ')+'-'+selected['sha256'][:10]
    report['run_id']=run_id;target=Path(output)/run_id;target.mkdir(parents=True,exist_ok=False)
    atomic_json(target/'fresh.json',report);atomic_json(target/'residuals.json',clean(residuals));atomic_json(target/'benchmark-models.json',clean(models))
    if residuals:
        with (target/'residuals.csv').open('w',encoding='utf-8',newline='') as f:
            w=csv.DictWriter(f,fieldnames=list(residuals[0]));w.writeheader();w.writerows(residuals)
    (target/'report.md').write_text(current_report(report),encoding='utf-8')
    atomic_json(target/'checksums.json',{p.name:sha(p) for p in target.iterdir() if p.is_file()})
    destination=Path(dashboard)/'fresh';destination.mkdir(parents=True,exist_ok=True)
    for p in target.iterdir():
        if p.is_file():shutil.copy2(p,destination/p.name)
    atomic_json(destination/'latest.json',{'summary':'fresh.json','summary_sha256':sha(target/'fresh.json'),
        'artifacts':{p.name:sha(p) for p in target.iterdir() if p.is_file()}})
    return report

def current_report(report):
    a=report['acquisition'];b=report['benchmark'];q=a['freshness']
    rows='\n'.join(f"| {s['prn']} | {s['toe_utc']} | {s['toe_age_seconds']/60:.1f} | {s['health']} | {s['ura_m']} | {'Usable under analysis policy' if s['usable_now'] else ', '.join(s['flags'])} |" for s in q['satellites'])
    comparisons=[]
    for s in b.get('satellites',[]):
        c=s.get('comparison')
        number=lambda value:'—' if value is None else f'{value:.4f}'
        fresh=s.get('models',{}).get('fresh',{}).get('validation',{}).get('rms_km')
        old=s.get('models',{}).get('delayed',{}).get('validation',{}).get('rms_km')
        gp=s.get('standard_gp',{}).get('metrics',{}).get('rms_km')
        reduction=f"{c['rms_reduction_percent']:.1f}%" if c else 'not comparable'
        comparisons.append(f"| {s['prn']} | {s['reference_epochs']} | {number(fresh)} | {number(old)} | {number(gp)} | {reduction} |")
    return f"""# Current-day NavIC acquisition and recency experiment

Run `{report['run_id']}` · generated {report['generated_at']}

Selected source: {a['selected_input']['source']}
SHA-256: `{a['selected_input']['sha256']}`. First received: {a['selected_input'].get('first_received_at') or a['selected_input']['retrieved_at']}.
Server Last-Modified: {a['selected_input'].get('server_last_modified')}. HTTP status: {a['selected_input'].get('http_status')}.
{q['usable_satellites']} of {q['satellites_present']} present satellites usable at the acquisition check time.

| PRN | Selected toe UTC | Age minutes | Health | URA m | Assessment |
|---|---|---|---|---|---|
{rows}

## Validity and freshness

The filename and HTTP modification time do not establish ephemeris freshness. Records are checked individually for health, URA, issue consistency and absolute toe age. Limit: ±{q['validity_limit_seconds']} seconds. Basis: {q['validity_basis']}. This remains a conservative **analysis policy**, not a verified ICD fit-interval guarantee. Unusable records are gaps, never extrapolated. Directory bodies, changed raw files and retrieval events are archived with hashes. A 304 response reuses only a checksum-verified archived body. Acquisition reports are also retained immutably under data/acquisitions.

## Controlled retrospective test

{b.get('interpretation','No benchmark requested.')}

Forecast origin: {b.get('forecast_origin_utc','—')}. Common evaluation ends: {b.get('validation_end_utc','—')}.
The fresh and delayed cohorts use the same {b.get('train_hours','—')}-hour training length, optimizer and sampling; the delayed cohort's inputs stop {b.get('delayed_input_hours','—')} hours earlier. Each model is fitted at its own issue epoch and compared over identical later physical epochs. Training excludes records with toc after its cutoff. This controls numerical time leakage, but toc is not a transmission timestamp: the current file was obtained after the retrospective origin, so actual past availability is **unproven**. This is not a live forecast. Standard GP is frozen at the origin and included only when its snapshot receipt and element epoch both precede the origin.

| PRN | Reference epochs | Fresh model holdout RMS km | Delayed model holdout RMS km | Eligible standard GP RMS km | Reduction vs delayed |
|---|---|---|---|---|---|
{chr(10).join(comparisons)}

These RMS values describe disagreement with valid broadcast trajectories, not absolute accuracy. The cohorts isolate an input-recency scenario; they do not prove universal improvement, calibrated uncertainty or future release validity. Preserve multiple dated snapshots for genuinely prospective validation. Benchmark OMMs are research artifacts and do not replace the daily accepted-model product.
"""
