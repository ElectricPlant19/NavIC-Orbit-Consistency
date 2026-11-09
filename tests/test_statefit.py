import copy
import numpy as np
from astropy.time import TimeDelta
from navic_compare.statefit import current_message, fit_message_state

def config():
    return {'broadcast_max_age_seconds':7200,'current_acquisition':{'max_nfev':400}}

def test_latest_message_excludes_future_toc_and_does_not_hide_health(geo):
    later=copy.deepcopy(geo);later.toc_gps+=60
    assert current_message([geo,later],geo.toe,config())[0] is geo
    unhealthy=copy.deepcopy(geo);unhealthy.values[21]=1
    assert current_message([unhealthy],geo.toe,config())[0] is None
    assert fit_message_state([unhealthy],geo.toe,config(),56759)[0] is None

def test_state_fit_never_uses_message_beyond_toe_policy(geo,monkeypatch):
    from navic_compare.fitting import target_state
    visited=[]
    def checked(e,times):
        visited.extend((times-e.toe).sec)
        return target_state(e,times)
    monkeypatch.setattr('navic_compare.statefit.target_state',checked)
    sat,info=fit_message_state([geo],geo.toe,config(),56759)
    assert sat is not None and info['target_epochs']==120
    assert info['forward_target_epochs']==60
    assert max(abs(np.array(visited)))+.5<=7200
    # A currently valid but almost expired message cannot support the required arc.
    sat,info=fit_message_state([geo],geo.toe+TimeDelta(7100,format='sec'),config(),56759)
    assert sat is None and info['status']=='insufficient_message_arc'
