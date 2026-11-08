import json
import hashlib
from dataclasses import dataclass
import numpy as np
from astropy.time import Time
from astropy import units as u
from astropy.coordinates import ITRS, TEME, CartesianRepresentation, CartesianDifferential
from sgp4.api import Satrec, WGS72, SGP4_ERRORS
from sgp4 import omm
from .timeframes import teme_to_ecef

MU = 3.986005e14
OMEGA = 7.2921151467e-5

def broadcast_position(e, time):
    """ISRO SPS ICD Appendix A; no BeiDou GEO-specific rotation is applicable."""
    v = e.values
    tk = np.asarray((time - e.toe).to_value(u.s))
    a = v[7] ** 2
    n = np.sqrt(MU / a**3) + v[2]
    mean = v[3] + n * tk
    ecc = mean.copy()
    for _ in range(20):
        step = (ecc - v[5]*np.sin(ecc) - mean) / (1 - v[5]*np.cos(ecc))
        ecc -= step
        if np.max(abs(step)) < 1e-13: break
    else: raise ValueError("Kepler iteration failed")
    phi = np.arctan2(np.sqrt(1-v[5]**2)*np.sin(ecc), np.cos(ecc)-v[5]) + v[14]
    c, s = np.cos(2*phi), np.sin(2*phi)
    arg = phi + v[6]*s + v[4]*c
    radius = a*(1-v[5]*np.cos(ecc)) + v[1]*s + v[13]*c
    inc = v[12] + v[16]*tk + v[11]*s + v[9]*c
    node = v[10] + (v[15]-OMEGA)*tk - OMEGA*v[8]
    x, y = radius*np.cos(arg), radius*np.sin(arg)
    return np.stack([x*np.cos(node)-y*np.cos(inc)*np.sin(node),
                     x*np.sin(node)+y*np.cos(inc)*np.cos(node), y*np.sin(inc)], axis=-1) / 1000

@dataclass
class GP:
    norad: int
    name: str
    epoch: object
    sat: object
    snapshot: str
    element_id: str
    fields: dict

def parse_gp(path):
    from pathlib import Path
    raw = Path(path).read_bytes()
    snapshot = hashlib.sha256(raw).hexdigest()
    rows = json.loads(raw)
    if not isinstance(rows, list) or not rows: raise ValueError("GP JSON must be a nonempty OMM list")
    result = []
    for row in rows:
        for key, expected in [("CENTER_NAME","EARTH"),("REF_FRAME","TEME"),("TIME_SYSTEM","UTC"),("MEAN_ELEMENT_THEORY","SGP4")]:
            if row.get(key, expected) != expected: raise ValueError(f"Unsupported OMM {key}")
        sat = Satrec()
        normalized = {**row, "CLASSIFICATION_TYPE":row.get("CLASSIFICATION_TYPE","U"),
                      "EPHEMERIS_TYPE":row.get("EPHEMERIS_TYPE",0)}
        omm.initialize(sat, normalized)
        epoch = Time(str(row["EPOCH"]).rstrip("Z"), scale="utc")
        eid = hashlib.sha256(json.dumps(row,sort_keys=True).encode()).hexdigest()[:16]
        result.append(GP(int(row["NORAD_CAT_ID"]), row["OBJECT_NAME"], epoch, sat, snapshot, eid, row))
    return result

def select_gp(sets, time, max_age_hours, allow_future=False):
    before = [g for g in sets if (time-g.epoch).sec >= -1e-6]
    if before: chosen = min(before, key=lambda g: abs((time-g.epoch).sec))
    elif sets and allow_future: chosen = min(sets, key=lambda g: abs((time-g.epoch).sec))
    else: return None, ["gp_missing" if not sets else "gp_no_prior_set"]
    age = (time-chosen.epoch).to_value(u.hour)
    if abs(age) > max_age_hours: return None, ["gp_stale"]
    return chosen, (["gp_future_set"] if age < -1e-6 else [])

def propagate_gp(g, times):
    if times.isscalar:
        error, p, v = g.sat.sgp4(times.utc.jd1, times.utc.jd2)
        if error: raise ValueError(f"SGP4 {error}: {SGP4_ERRORS.get(error, 'unknown')}")
        return np.asarray(p), teme_to_ecef(p, times)
    errors, p, v = g.sat.sgp4_array(times.utc.jd1, times.utc.jd2)
    if np.any(errors): raise ValueError(f"SGP4 propagation codes: {sorted(set(errors.tolist()))}")
    return p, teme_to_ecef(p, times)

def rtn_residual(e, times, gp_teme):
    """Use inertial broadcast velocity; ECEF derivatives alone are singular for GEO."""
    from astropy.time import TimeDelta
    p = broadcast_position(e, times)
    half = TimeDelta(0.5,format="sec")
    v = broadcast_position(e, times+half) - broadcast_position(e, times-half)
    rep = CartesianRepresentation(p.T*u.km).with_differentials(CartesianDifferential(v.T*u.km/u.s))
    inertial = ITRS(rep,obstime=times).transform_to(TEME(obstime=times))
    r = inertial.cartesian.xyz.to_value(u.km).T
    vel = inertial.cartesian.differentials["s"].d_xyz.to_value(u.km/u.s).T
    radial = r/np.linalg.norm(r,axis=-1,keepdims=True)
    normal = np.cross(r,vel)
    normal /= np.linalg.norm(normal,axis=-1,keepdims=True)
    along = np.cross(normal,radial)
    delta = gp_teme-r
    return np.stack([np.sum(delta*b,axis=-1) for b in (radial,along,normal)],axis=-1)
