import copy
import json
import numpy as np
from astropy.time import Time,TimeDelta
from navic_compare.rinex import read_rinex,select_ephemeris
from navic_compare.orbits import parse_gp,select_gp
from navic_compare.analysis import summarize
import pytest

def test_broadcast_never_extrapolates(geo):
    assert select_ephemeris([geo],geo.toe+TimeDelta(7200,format='sec'),7200)[0]
    assert select_ephemeris([geo],geo.toe+TimeDelta(7201,format='sec'),7200)==(None,['broadcast_gap'])
    geo.values[21]=1
    assert select_ephemeris([geo],geo.toe,7200)==(None,['broadcast_unhealthy'])

def test_conflicting_iode_is_gap(geo):
    conflicting=copy.deepcopy(geo);conflicting.values[3]=1
    assert select_ephemeris([geo,conflicting],geo.toe,7200)==(None,['iodec_conflict'])
    geo.values[0]=35
    assert select_ephemeris([geo],geo.toe,7200)==(None,['iodec_reserved'])

def rinex_text(geo,version=3.04,prn='I10'):
    header=f'{version:9.2f}           N: GNSS NAV DATA    M                   RINEX VERSION / TYPE\n'
    header+=' '*60+'END OF HEADER\n'
    first=f'{prn} 2020 01 01 00 00 18'+''.join(f'{v:19.12E}' for v in geo.clock)+'\n'
    continuation=''.join('    '+''.join(f'{v:19.12E}' for v in geo.values[i:i+4])+'\n' for i in range(0,28,4))
    return header+('> EPH I10 LNAV\n' if version>=4 else '')+first+continuation

@pytest.mark.parametrize('version',[3.04,4.02])
def test_fixed_width_parser_and_time(tmp_path,geo,version):
    p=tmp_path/'input.rnx';p.write_text(rinex_text(geo,version))
    records,header=read_rinex(p)
    assert header['satellites_present']==['I10']
    assert abs((records[0].toe-geo.toe).sec)<1e-6
    assert records[0].health==0

def test_reject_no_i_and_unsupported_l1(tmp_path,geo):
    p=tmp_path/'input.rnx';p.write_text(rinex_text(geo,prn='G01'))
    with pytest.raises(ValueError,match='no supported'): read_rinex(p)
    p.write_text(rinex_text(geo,4.02).replace('I10 LNAV','I10 L1NV'))
    with pytest.raises(ValueError,match='no supported'): read_rinex(p)

def test_gzip_truncation_is_rejected(tmp_path,geo):
    import gzip
    p=tmp_path/'input.gz';p.write_bytes(gzip.compress(rinex_text(geo).encode())[:-9])
    with pytest.raises((EOFError,OSError)): read_rinex(p)

def test_gp_causal_and_stale_policy():
    from types import SimpleNamespace
    t=Time('2020-01-02T00:00:00',scale='utc')
    old=SimpleNamespace(epoch=t-TimeDelta(3600,format='sec'))
    future=SimpleNamespace(epoch=t+TimeDelta(60,format='sec'))
    assert select_gp([future,old],t,48)[0] is old
    assert select_gp([future],t,48)==(None,['gp_no_prior_set'])
    assert select_gp([future],t,48,True)[1]==['gp_future_set']
    assert select_gp([old],t,0.5)==(None,['gp_stale'])

def test_stats_exclude_gaps_and_compute_status():
    identities=[dict(prn='I10',orbit_class='GEO',confirmed=True)]
    base={'prn':'I10','flags':[],'utc':'t','gp_age_hours':2,'radial_km':0,'along_km':3,'cross_km':0}
    rows=[{**base,'separation_km':3},{**base,'separation_km':4},{**base,'separation_km':None,'flags':['broadcast_gap']}]
    config={'thresholds':{'GEO':{'rms_km':5,'max_km':15,'jump_km':3}}}
    sats,fleet=summarize(rows,identities,config)
    assert sats[0]['rms_km']==np.sqrt(12.5)
    assert sats[0]['status']=='Review'
    assert fleet['satellites_compared']==1 and sats[0]['valid_epochs']==2
