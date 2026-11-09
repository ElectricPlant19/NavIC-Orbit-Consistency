"""Experimental SGP4 fit to one already-received navigation-message trajectory.

Forward targets here are predictions of the same broadcast message, never later
messages. Independent later-message scoring belongs to prospective.py.
"""
import numpy as np
from astropy.time import TimeDelta
from .rinex import select_ephemeris
from .fitting import target_state, osculating_seed, fit_mean_elements, propagate, metrics

V1 = 'v1-position-6h'
V2 = 'v2-message-state'
LABELS = {V1: 'V1 · six-hour position fit (control)',
          V2: 'V2 · latest-message state fit (experimental)'}


def current_message(records, cutoff, config):
    allowed = [e for e in records if e.toc_gps <= float(cutoff.gps)]
    return select_ephemeris(allowed, cutoff, config['broadcast_max_age_seconds'])


def fit_message_state(records, cutoff, config, norad):
    e, flags = current_message(records, cutoff, config)
    if e is None:
        return None, {'status': 'no_healthy_current_message', 'flags': flags}
    # Versioned, fixed settings selected in the development replay. Do not tune
    # them from the new issue's future scores.
    times = cutoff + TimeDelta(np.arange(-3600, 3600, 60), format='sec')
    # Include the half-second differentiation stencil inside the toe cutoff.
    valid = abs((times-e.toe).sec) <= config['broadcast_max_age_seconds']-.5
    coverage = float(valid.mean())
    if coverage < .8 or valid.sum() < 12:
        return None, {'status': 'insufficient_message_arc', 'coverage_percent': 100*coverage}
    times = times[valid]
    p, v = target_state(e, times)
    nearest = int(np.argmin(abs((times-cutoff).sec)))
    seed = osculating_seed(p[nearest], v[nearest])
    seed[0] += np.exp(seed[5])*2*np.pi*(cutoff-times[nearest]).sec/86400
    sat, diagnostic = fit_mean_elements(times, p, seed, cutoff, norad,
        config['current_acquisition']['max_nfev'], velocities=v, velocity_scale_seconds=10000)
    ok = diagnostic['success'] and diagnostic['jacobian_rank'] == 6 and sat.method == 'd'
    return sat if ok else None, {
        'status': 'fitted' if ok else 'optimizer_rejected', 'model_version': V2,
        'epoch_utc': cutoff.utc.isot+'Z', 'target_start_utc': times[0].utc.isot+'Z',
        'target_end_inclusive_utc': times[-1].utc.isot+'Z',
        'message_toc_utc': e.toc.utc.isot+'Z', 'message_toe_utc': e.toe.utc.isot+'Z',
        'coverage_percent': 100*coverage, 'target_epochs': len(times),
        'forward_target_epochs': int(((times-cutoff).sec >= 0).sum()),
        'velocity_scale_seconds': 10000, 'differentiation_seconds': 1,
        'fit': metrics(propagate(sat, times)-p, times), 'optimizer': diagnostic,
        'interpretation': 'Experimental conversion of one already-received message to SGP4. '
            'Targets span issue ±1 h within the declared toe cutoff. Forward targets are '
            'broadcast predictions, not future observations. Fit RMS is not forecast RMS.'}
