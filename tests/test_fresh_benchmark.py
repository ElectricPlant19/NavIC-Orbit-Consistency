from datetime import datetime,timezone
from types import SimpleNamespace
import numpy as np
from navic_compare.fresh import benchmark_recency,targets
from astropy.time import Time,TimeDelta

def test_benchmark_uses_common_epochs_and_excludes_late_gp(monkeypatch):
    config={'gp_max_age_hours':48,'current_acquisition':{'benchmark_step_seconds':300,'benchmark_train_hours':6,
        'benchmark_holdout_hours':1,'benchmark_stale_delay_hours':6,'minimum_holdout_coverage':.8}}
    asof=datetime(2020,1,2,12,tzinfo=timezone.utc)
    origin=Time('2020-01-02T11:00:00',scale='utc')
    calls=[]
    def target(group,times,config,cutoff=None):
        return np.tile([42000.,0,0],(len(times),1)),np.tile([0.,3.,0],(len(times),1)),[[] for t in times]
    def fit(group,cutoff,config,norad):
        return SimpleNamespace(offset=1. if abs((cutoff-origin).sec)<1 else 3.),{'status':'fitted'}
    def propagation(sat,times):calls.append(times.utc.isot.tolist());return np.tile([42000.+sat.offset,0,0],(len(times),1))
    monkeypatch.setattr('navic_compare.fresh.targets',target)
    monkeypatch.setattr('navic_compare.fresh.fit_at_cutoff',fit)
    monkeypatch.setattr('navic_compare.fresh.propagate',propagation)
    monkeypatch.setattr('navic_compare.fresh.export_omm',lambda *a:{'COMMENT':'test'})
    gp=SimpleNamespace(norad=56759,snapshot='hash',epoch=origin-TimeDelta(3600,format='sec'))
    identities=[{'prn':'I10','norad_id':56759,'name':'NVS-01','orbit_class':'GEO'}]
    result,rows,models=benchmark_recency([],identities,[gp],[{'sha256':'hash','retrieved_at':'2020-01-02T11:30:00+00:00'}],asof,config)
    c=result['satellites'][0]['comparison']
    assert calls[0]==calls[1] and c['common_epochs']==13
    assert c['fresh_rms_km']==1 and c['delayed_rms_km']==3
    assert result['availability_proven'] is False
    assert result['satellites'][0]['standard_gp']['status']=='no_eligible_snapshot_received_before_origin'

def test_training_target_selection_cannot_use_future_clock_epoch(geo,monkeypatch):
    future=SimpleNamespace(prn=geo.prn,toc_gps=geo.toc_gps+3600)
    observed=[]
    def select(records,time,limit):observed.extend(records);return None,['broadcast_gap']
    monkeypatch.setattr('navic_compare.fresh.select_ephemeris',select)
    times=geo.toe+TimeDelta([0,60],format='sec')
    p,v,flags=targets([geo,future],times,{'broadcast_max_age_seconds':7200},geo.toe)
    assert future not in observed and geo in observed
    assert np.isnan(p).all()
