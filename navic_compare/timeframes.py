"""Pinned UTC/IRN time and Vallado TEME -> ITRS through Astropy/ERFA."""
from contextlib import contextmanager
import numpy as np
import erfa
from astropy import units as u
from astropy.time import Time, TimeDelta
from astropy.coordinates import TEME, ITRS, CartesianRepresentation
from astropy.utils import iers

iers.conf.auto_download = False
iers.conf.iers_degraded_accuracy = "error"

def utc_grid(day, step):
    if step <= 0:
        raise ValueError("step_seconds must be positive")
    start = Time(str(day), scale="utc")
    # Calendar midnight, not a presumed 86400 SI-second UTC day.
    from datetime import date, timedelta
    end = Time(str(date.fromisoformat(str(day)) + timedelta(days=1)), scale="utc")
    seconds = (end.tai - start.tai).to_value(u.s)
    return start + TimeDelta(np.arange(0, seconds - 1e-7, step), format="sec")

def system_time(calendar_text, correction=None):
    """IRNSST nominally GPS (=TAI-19); optional IRUT polynomial in seconds."""
    nominal = Time(calendar_text, scale="tai") + TimeDelta(19, format="sec")
    if correction:
        a0, a1, ref_sow, ref_week = correction
        ref = ref_week * 604800 + ref_sow
        nominal -= TimeDelta(a0 + a1 * (nominal.gps - ref), format="sec")
    return nominal

def toe_time(toc, sow):
    # Anchor to calendar toc: no ambiguous 10-bit IRN/GPS week rollover.
    gps = float(toc.gps)
    week = np.floor(gps / 604800)
    candidates = (week + np.array([-1, 0, 1])) * 604800 + sow
    return Time(candidates[np.argmin(abs(candidates - gps))], format="gps")

@contextmanager
def pinned_orientation(eop_path, leap_path):
    eop = iers.IERS_A.open(eop_path)
    leaps = iers.LeapSeconds.open(leap_path)
    old = erfa.leap_seconds.get()
    erfa.leap_seconds.set(leaps)
    try:
        with iers.earth_orientation_table.set(eop):
            yield eop
    finally:
        erfa.leap_seconds.set(old)

def check_eop(times, eop):
    _, status = eop.ut1_utc(times, return_status=True)
    if np.any(np.asarray(status) < 0):
        raise ValueError("EOP does not cover comparison epochs; refusing extrapolation")
    _, _, pm_status = eop.pm_xy(times, return_status=True)
    if np.any(np.asarray(pm_status) < 0):
        raise ValueError("Polar motion does not cover comparison epochs")
    return {"ut1_status": sorted(set(np.asarray(status).ravel().tolist())),
            "prediction_used": bool(np.any(np.asarray(status) == iers.FROM_IERS_A_PREDICTION))}

def teme_to_ecef(position_km, times):
    vector = np.asarray(position_km)
    rep = CartesianRepresentation(vector.T * u.km)
    return TEME(rep, obstime=times).transform_to(ITRS(obstime=times)).cartesian.xyz.to_value(u.km).T
