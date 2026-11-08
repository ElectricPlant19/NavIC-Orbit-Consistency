from types import SimpleNamespace
import numpy as np
from astropy.time import TimeDelta
from navic_compare.identity import match_identities

def test_declared_identity_is_preserved_without_forcing_geometry(geo,monkeypatch):
    times=geo.toe+TimeDelta([0,60,120],format='sec')
    gps=[SimpleNamespace(norad=101228,name='NVS-03',element_id='set',epoch=geo.toe)]
    config={'broadcast_max_age_seconds':7200,'gp_max_age_hours':48,'gp_allow_future':False,
            'identity_max_km':50,'identity_margin_km':500,'geo_inclination_limit_deg':5,
            'identity_catalogue':{'I10':{'norad_id':101228,'name':'NVS-03','orbit_class':'IGSO','provenance':'test declaration'}}}
    monkeypatch.setattr('navic_compare.identity.propagate_gp',lambda g,t:(None,np.array([100000.,0,0])))
    result=match_identities([geo],gps,times,config)[0]
    assert result['norad_id']==101228 and result['name']=='NVS-03'
    assert result['confirmed'] is False
    assert result['orbit_class']=='IGSO'
    assert result['candidates'][0]['max_test_km']>50000
