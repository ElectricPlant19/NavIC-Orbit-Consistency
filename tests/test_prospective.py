import copy
from datetime import datetime, timezone
from types import SimpleNamespace

import numpy as np
import pytest
from astropy.time import Time, TimeDelta
from astropy.utils import iers

from navic_compare.fitting import satellite, export_omm
from navic_compare.prospective import (immutable, read, digest, ephemeris_payload, eligible_gp,
    issue_models, reference_at, score_issue, load_scores, pair_statistics, build_summary)


def setup_case(geo):
    epoch=geo.toe
    model=satellite(np.array([1.,.001,.001,.05,.1,np.log(1.0027)]),epoch,56759)
    fields=export_omm(model,epoch,{'name':'NVS-01','norad_id':56759},
                      [SimpleNamespace(norad=56759,fields={'OBJECT_ID':'2023-076A'})])
    config={'broadcast_max_age_seconds':7200,'gp_max_age_hours':48,
            'thresholds':{'GEO':{'rms_km':5,'max_km':15}},
            'identity_catalogue':{'I10':{'name':'NVS-01','norad_id':56759,'orbit_class':'GEO'}},
            'current_acquisition':{'benchmark_train_hours':6,'benchmark_step_seconds':300},
            'prospective':{'step_seconds':900,'horizon_hours':1,'reference_wait_hours':.25,'age_bins_hours':[0,.5,1]}}
    gp={'fields':fields,'first_received_at':'2019-12-31T23:59:00Z',
        'element_id':digest(fields),'snapshot_sha256':'gp-original'}
    issue={'issue_id':'test-I10','prn':'I10','issued_at':'2020-01-01T00:00:00Z',
           'model_epoch_utc':'2020-01-01T00:00:00Z','omm':fields,'omm_sha256':digest(fields),
           'training_record_ids':[digest(ephemeris_payload(geo))], 'identity':config['identity_catalogue']['I10'],
           'config':config,'policy':{'step_seconds':900,'horizon_hours':1,'reference_wait_hours':.25,
                                    'age_bins_hours':[0,.5,1]}}
    return config,issue,gp,model


def reference(e,receipt):
    p=ephemeris_payload(e)
    return ({'record_id':digest(p),'ephemeris':p,'first_received_at':receipt,'snapshot_sha256':'nav'},e)


def test_latest_gp_never_uses_future_receipt_or_future_epoch(geo):
    config,issue,gp,_=setup_case(geo); moment=geo.toe+TimeDelta(900,format='sec')
    late={**gp,'first_received_at':'2020-01-01T00:20:00Z'}
    future={**gp,'fields':{**gp['fields'],'EPOCH':'2020-01-01T00:30:00'}}
    assert eligible_gp([late,future],56759,moment,48) is None
    assert eligible_gp([gp,late,future],56759,moment,48) is gp


def test_future_reference_excludes_training_repeated_and_future_toc(geo):
    _,issue,_,_=setup_case(geo)
    later=copy.deepcopy(geo);later.toc=geo.toc+TimeDelta(600,format='sec');later.toc_gps=float(later.toc.gps)
    point=geo.toe+TimeDelta(900,format='sec');asof=geo.toe+TimeDelta(1800,format='sec')
    repeated=reference(geo,'2020-01-01T00:20:00Z')
    unseen=reference(later,'2020-01-01T01:00:00Z')
    assert reference_at([repeated,unseen],issue,point,asof)[0] is None
    assert reference_at([reference(later,'2020-01-01T00:20:00Z')],issue,geo.toe+TimeDelta(300,format='sec'),asof)[0] is None
    result,_=reference_at([repeated,reference(later,'2020-01-01T00:20:00Z')],issue,point,asof)
    assert result[1] is later


def test_scores_are_immutable_and_rolling_baseline_updates_only_after_receipt(tmp_path,geo):
    _,issue,gp,_=setup_case(geo);issue['frozen_gp']=gp
    newer=copy.deepcopy(gp);newer['first_received_at']='2020-01-01T00:20:00Z'
    newer['fields']['EPOCH']='2020-01-01T00:18:00';newer['element_id']=digest(newer['fields'])
    later=copy.deepcopy(geo);later.toc=geo.toc+TimeDelta(600,format='sec');later.toc_gps=float(later.toc.gps)
    records=[reference(later,'2020-01-01T00:20:00Z')]
    table=iers.IERS_B.open(iers.IERS_B_FILE)
    result=score_issue(issue,records,[gp,newer],geo.toe+TimeDelta(1800,format='sec'),{},tmp_path,table)
    assert len(result)==2
    rows=list(result.values())
    assert rows[0]['latest_gp']['element_id']==gp['element_id']
    assert rows[1]['latest_gp']['element_id']==newer['element_id']
    assert all(r['frozen_gp']['element_id']==gp['element_id'] for r in rows)
    before=copy.deepcopy(result)
    repeat=score_issue(issue,[],[],geo.toe+TimeDelta(1800,format='sec'),{},tmp_path,table)
    assert repeat==before and load_scores(tmp_path,issue['issue_id'])==before
    assert len(list((tmp_path/'scores'/issue['issue_id']).glob('*')))==1
    audit=read(next((tmp_path/'scores'/issue['issue_id']).glob('*')))
    assert len(audit['code_sha256'])==64 and audit['earth_orientation_status']['prediction_used'] is False
    broken=copy.deepcopy(issue);broken['omm']['MEAN_ANOMALY']+=1
    with pytest.raises(ValueError,match='checksum'):score_issue(broken,records,[gp],geo.toe,{},tmp_path,table)


def test_missing_references_wait_then_finalize_as_gaps(tmp_path,geo):
    _,issue,_,_=setup_case(geo);issue['frozen_gp']=None
    table=iers.IERS_B.open(iers.IERS_B_FILE)
    assert score_issue(issue,[],[],geo.toe+TimeDelta(900,format='sec'),{},tmp_path,table)=={}
    result=score_issue(issue,[],[],geo.toe+TimeDelta(1800,format='sec'),{},tmp_path,table)
    assert len(result)==1
    row=next(iter(result.values()))
    assert row['ours'] is None and 'later_reference_missing' in row['flags']


def test_paired_statistics_use_exact_common_samples():
    rows=[{'utc':'a','ours':{'separation_km':100},'latest_gp':None},
          {'utc':'b','ours':{'separation_km':1,'radial_km':1,'along_km':0,'cross_km':0},
           'latest_gp':{'separation_km':2,'radial_km':2,'along_km':0,'cross_km':0}}]
    p=pair_statistics(rows,'latest_gp')
    assert p['common_epochs']==1 and p['ours']['rms_km']==1
    assert p['rms_reduction_percent']==50 and p['lower_separation_percent']==100


def test_issue_roundtrip_frozen_baseline_and_restart_idempotency(tmp_path,geo,monkeypatch):
    config,_,gp,model=setup_case(geo)
    monkeypatch.setattr('navic_compare.prospective.fit_at_cutoff',lambda *a:(model,{'status':'fitted'}))
    clock=lambda:datetime(2020,1,1,0,0,10,tzinfo=timezone.utc)
    args=([geo],[gp],[SimpleNamespace(norad=56759,fields={'OBJECT_ID':'2023-076A'})],
          {'sha256':'nav','retrieved_at':'2019-12-31T23:59:00Z'},{},config,tmp_path)
    first=issue_models(*args,cutoff=geo.toe,clock=clock)
    assert first[0]['status']=='issued'
    frozen=next((tmp_path/'issues').glob('*.json')).read_bytes()
    assert issue_models(*args,cutoff=geo.toe,clock=clock)==[]
    assert next((tmp_path/'issues').glob('*.json')).read_bytes()==frozen
    issued=read(next((tmp_path/'issues').glob('*.json')))
    assert issued['frozen_gp']['element_id']==gp['element_id']
    assert utc_seconds(issued['issued_at'],issued['model_epoch_utc'])==pytest.approx(10)
    summary=build_summary(tmp_path,geo.toe+TimeDelta(10,format='sec'),config,tmp_path/'dashboard',first)
    assert summary['issue_count']==1 and summary['fleet']['ours'] is None
    assert summary['issues'][0]['status']=='Waiting'


def utc_seconds(a,b):
    from navic_compare.prospective import utc
    return (utc(a)-utc(b)).sec

def test_versions_issue_once_each_and_summaries_never_mix(tmp_path,geo,monkeypatch):
    from navic_compare.statefit import V1,V2
    config,_,gp,model=setup_case(geo)
    config['prospective']['model_versions']=[V1,V2]
    monkeypatch.setattr('navic_compare.prospective.fit_at_cutoff',lambda *a:(model,{'status':'fitted'}))
    monkeypatch.setattr('navic_compare.prospective.fit_message_state',lambda *a:(model,{'status':'fitted'}))
    args=([geo],[gp],[SimpleNamespace(norad=56759,fields={'OBJECT_ID':'2023-076A'})],
          {'sha256':'nav','retrieved_at':'2019-12-31T23:59:00Z'},{},config,tmp_path)
    clock=lambda:datetime(2020,1,1,0,0,10,tzinfo=timezone.utc)
    first=issue_models(*args,cutoff=geo.toe,clock=clock)
    assert len(first)==2 and all(a['status']=='issued' for a in first)
    assert issue_models(*args,cutoff=geo.toe,clock=clock)==[]
    documents=[read(p) for p in (tmp_path/'issues').glob('*.json')]
    assert {i['model_version'] for i in documents}=={V1,V2}
    assert len({i['issue_id'] for i in documents})==2
    summary=build_summary(tmp_path,geo.toe,config,tmp_path/'dashboard',first)
    assert len(summary['versions'])==2
    assert all(v['issue_count']==1 for v in summary['versions'])


def test_immutable_history_rejects_rewrites(tmp_path):
    p=tmp_path/'issue.json';immutable(p,{'a':1});immutable(p,{'a':1})
    with pytest.raises(ValueError,match='conflict'):immutable(p,{'a':2})


def test_gp_poll_guard_survives_complete_cache_eviction(tmp_path,monkeypatch):
    import hashlib,json,runpy,sys
    from pathlib import Path
    script=Path('scripts/prospective_guard.py').resolve()
    monkeypatch.chdir(tmp_path)
    url='https://example.test/gp';checksum=hashlib.sha256(b'[]').hexdigest()
    (tmp_path/'config').mkdir();(tmp_path/'config/default.json').write_text(json.dumps({'gp_url':url}))
    cache=tmp_path/'data/cache'/(hashlib.sha256(url.encode()).hexdigest()+'.json');cache.parent.mkdir(parents=True)
    raw=tmp_path/'data/raw'/(checksum+'.omm.json');raw.parent.mkdir();raw.write_bytes(b'[]')
    record={'path':str(raw),'sha256':checksum,'source':url,'retrieved_at':'2020-01-01T00:00:00Z'}
    cache.write_text(json.dumps({'last_attempt':123,'etag':'tag','record':record}))
    monkeypatch.setattr(sys,'argv',['guard','save']);runpy.run_path(str(script),run_name='__main__')
    cache.unlink();raw.unlink()
    monkeypatch.setattr(sys,'argv',['guard','restore']);runpy.run_path(str(script),run_name='__main__')
    restored=json.loads(cache.read_text())
    assert restored['last_attempt']==123 and restored['etag']=='tag'
    assert Path(restored['record']['path']).read_bytes()==b'[]'
    assert json.loads((tmp_path/'data/retrievals.jsonl').read_text())['retrieved_at']=='2020-01-01T00:00:00Z'


def test_archive_keeps_bad_download_for_audit_without_poisoning_references(tmp_path,geo):
    import gzip,hashlib
    from test_validity import rinex_text
    from navic_compare.prospective import archive_inputs
    journal=[]
    for n,body in enumerate([b'<html>login page</html>',gzip.compress(rinex_text(geo).encode())]):
        checksum=hashlib.sha256(body).hexdigest();p=tmp_path/'raw'/(checksum+'.rnx.gz');p.parent.mkdir(exist_ok=True);p.write_bytes(body)
        journal.append({'sha256':checksum,'path':str(p),'source':'https://example.test/'+str(n),'retrieved_at':'2020-01-01T00:00:00Z'})
    support={}
    for name in ('eop','leaps'):
        p=tmp_path/name;p.write_bytes(name.encode());support[name]={'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'path':str(p),'source':'test'}
    archive_inputs(tmp_path/'history',tmp_path,support,journal)
    assert len(list((tmp_path/'history/records').glob('*.json')))==1
    rejected=read(tmp_path/'history/ingested'/(journal[0]['sha256']+'.json'))
    assert rejected['rejected'] and len(list((tmp_path/'history/inputs').glob('*.rnx.gz')))==2
    later=copy.deepcopy(journal)
    for meta in later:meta['retrieved_at']='2020-01-01T01:00:00Z'
    archive_inputs(tmp_path/'history',tmp_path,support,later)
    receipt=read(tmp_path/'history/receipts'/(journal[1]['sha256']+'.json'))
    assert receipt['first_received_at']=='2020-01-01T00:00:00Z'
