import copy
import numpy as np
import pytest
from astropy.time import Time,TimeDelta
from navic_compare.fitting import (satellite,propagate,osculating_seed,fit_mean_elements,
                                   evaluate_model,export_omm,generate_models,settings)

@pytest.mark.parametrize('inclination,eccentricity',[(.0001,.00001),(29.,.002)])
def test_synthetic_mean_element_recovery_and_export(inclination,eccentricity,tmp_path):
    from navic_compare.orbits import parse_gp
    import json
    epoch=Time('2020-01-01T00:00:00',scale='utc')
    node=.7;peri=1.1;inc=np.radians(inclination)
    p=np.array([2.4,eccentricity*np.cos(peri),eccentricity*np.sin(peri),np.tan(inc/2)*np.cos(node),np.tan(inc/2)*np.sin(node),np.log(1.0027)])
    truth=satellite(p,epoch,56759)
    times=epoch+TimeDelta(np.arange(0,86400,900),format='sec')
    _,r,v=truth.sgp4(epoch.utc.jd1,epoch.utc.jd2)
    seed=osculating_seed(r,v)
    positions=propagate(truth,times)
    train=np.arange(len(times))<72
    fitted,diagnostics=fit_mean_elements(times[train],positions[train],seed,epoch,56759)
    _,fit,holdout=evaluate_model(fitted,times,positions,train)
    assert diagnostics['success'] and diagnostics['jacobian_rank']==6
    assert fitted.method=='d'
    assert fit['rms_km']<1e-5 and holdout['rms_km']<1e-5
    identity={'norad_id':56759,'name':'test'}
    from types import SimpleNamespace
    row=export_omm(fitted,epoch,identity,[SimpleNamespace(norad=56759,fields={'OBJECT_ID':'2023-076A'})])
    path=tmp_path/'fit.omm.json';path.write_text(json.dumps([row]))
    restored=parse_gp(path)[0]
    np.testing.assert_allclose(propagate(restored.sat,times),propagate(fitted,times),rtol=0,atol=1e-7)

def test_holdout_change_cannot_train_model():
    epoch=Time('2020-01-01T00:00:00',scale='utc')
    p=np.array([1.,.001,.001,.15,.10,np.log(1.0027)])
    truth=satellite(p,epoch,39635)
    times=epoch+TimeDelta(np.arange(0,86400,1200),format='sec')
    positions=propagate(truth,times)
    train=np.arange(len(times))<54
    changed=positions.copy();changed[~train]+=np.array([20.,0,0])
    seed=p+np.array([.001,.00001,-.00001,.00001,.00001,.00001])
    a,_=fit_mean_elements(times[train],positions[train],seed,epoch,39635)
    b,_=fit_mean_elements(times[train],changed[train],seed,epoch,39635)
    np.testing.assert_array_equal(propagate(a,times),propagate(b,times))
    _,fit,held=evaluate_model(b,times,changed,train)
    assert fit['rms_km']<1e-5 and held['rms_km']>19.99

def test_generator_rejects_gaps_and_unconfirmed_identity(geo):
    times=geo.toe+TimeDelta(np.arange(0,86400,600),format='sec')
    identity=dict(prn='I10',norad_id=56759,name='NVS-01',orbit_class='GEO',confirmed=False)
    config={'step_seconds':600,'broadcast_max_age_seconds':7200,'generator':{'sample_seconds':600}}
    summary,exported,rows=generate_models([geo],[identity],[],times,config)
    assert not exported and summary['accepted_count']==0
    assert 'identity_geometry_unconfirmed' in summary['satellites'][0]['reasons']
    assert 'insufficient_holdout_coverage' in summary['satellites'][0]['reasons']
    assert all(row['separation_km'] is None for row in rows)

def test_split_configuration_is_strict():
    with pytest.raises(ValueError): settings({'generator':{'train_hours':24}})
