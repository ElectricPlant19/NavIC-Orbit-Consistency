"""Experimental broadcast-derived SGP4 mean-element fitting with held-out epochs.

This is an independent NavIC product, not CelesTrak SupGP. Fit targets are broadcast
positions, not observations or truth. GP elements supply catalogue metadata only.
"""
from collections import Counter
import numpy as np
from datetime import date,timedelta
from astropy import units as u
from astropy.time import Time,TimeDelta
from astropy.coordinates import ITRS, TEME, CartesianRepresentation, CartesianDifferential
from scipy.optimize import least_squares
from sgp4.api import Satrec, WGS72
from .orbits import broadcast_position
from .rinex import select_ephemeris

DEFAULTS = {
    "enabled": True, "sample_seconds": 300, "train_hours": 18,
    "min_train_coverage": 0.8, "min_validation_coverage": 0.8,
    "min_train_span_hours": 12, "min_validation_span_hours": 4,
    "max_nfev": 400,
    "threshold_calibration": "provisional engineering gates; no absolute accuracy claim",
    "thresholds": {
        "GEO": {"fit_rms_km": 1, "validation_rms_km": 5, "validation_max_km": 10},
        "IGSO": {"fit_rms_km": 1, "validation_rms_km": 5, "validation_max_km": 10}
    }
}

def settings(config):
    supplied = config.get("generator", {})
    result = {**DEFAULTS, **supplied}
    if not 0 < result['train_hours'] < 24:
        raise ValueError('Generator train_hours must be between 0 and 24')
    if result['sample_seconds'] <= 0:
        raise ValueError('Generator sample_seconds must be positive')
    for key in ('min_train_coverage','min_validation_coverage'):
        if not 0 < result[key] <= 1: raise ValueError(f'Invalid {key}')
    return result

def mean_parameters(sat):
    """Nonsingular prograde variables (lambda, e-vector, inclination-vector, log n)."""
    longitude = sat.nodeo + sat.argpo
    return np.array([sat.mo+longitude, sat.ecco*np.cos(longitude), sat.ecco*np.sin(longitude),
                     np.tan(sat.inclo/2)*np.cos(sat.nodeo), np.tan(sat.inclo/2)*np.sin(sat.nodeo),
                     np.log(sat.no_kozai*1440/(2*np.pi))])

def satellite(parameters, epoch, norad):
    longitude, ex, ey, hx, hy, log_n = parameters
    ecc = np.hypot(ex,ey)
    node = np.arctan2(hy,hx) if np.hypot(hx,hy)>1e-14 else 0.0
    peri_long = np.arctan2(ey,ex) if ecc>1e-14 else 0.0
    inc = 2*np.arctan(np.hypot(hx,hy))
    sat = Satrec()
    epoch_days = (epoch.utc.jd1-2433281.5)+epoch.utc.jd2
    sat.sgp4init(WGS72,'i',int(norad),float(epoch_days),0.,0.,0.,float(ecc),
                 float((peri_long-node)%(2*np.pi)),float(inc),
                 float((longitude-peri_long)%(2*np.pi)),float(np.exp(log_n)*2*np.pi/1440),
                 float(node%(2*np.pi)))
    return sat

def osculating_seed(position, velocity):
    """Only an initializer; SGP4 mean elements are subsequently fitted numerically."""
    mu = 398600.8  # WGS72 km^3/s^2, consistent with the fitted SGP4 model.
    r,v = np.asarray(position),np.asarray(velocity)
    length = np.linalg.norm(r)
    h = np.cross(r,v)
    ecc_vector = np.cross(v,h)/mu-r/length
    ecc = np.linalg.norm(ecc_vector)
    semimajor = 1/(2/length-np.dot(v,v)/mu)
    if not 0 <= ecc < .2 or semimajor <= 0: raise ValueError('Seed is outside supported near-geosynchronous geometry')
    inc = np.arctan2(np.hypot(h[0],h[1]),h[2])
    node = np.arctan2(h[0],-h[1]) if np.hypot(h[0],h[1])>1e-12 else 0.0
    p = np.array([np.cos(node),np.sin(node),0.])
    q = np.array([-np.sin(node)*np.cos(inc),np.cos(node)*np.cos(inc),np.sin(inc)])
    peri = np.arctan2(ecc_vector@q,ecc_vector@p) if ecc>1e-12 else 0.0
    true = np.arctan2(r@q,r@p)-peri
    eccentric = np.arctan2(np.sqrt(1-ecc*ecc)*np.sin(true),ecc+np.cos(true))
    mean = eccentric-ecc*np.sin(eccentric)
    rev_day = np.sqrt(mu/semimajor**3)*86400/(2*np.pi)
    return np.array([mean+peri+node,ecc*np.cos(peri+node),ecc*np.sin(peri+node),
                     np.tan(inc/2)*np.cos(node),np.tan(inc/2)*np.sin(node),np.log(rev_day)])

def propagate(sat,times):
    codes,positions,_ = sat.sgp4_array(np.atleast_1d(times.utc.jd1),np.atleast_1d(times.utc.jd2))
    if np.any(codes) or not np.all(np.isfinite(positions)):
        raise ValueError(f'Invalid fitted SGP4 propagation: {sorted(set(codes.tolist()))}')
    return positions

def fit_mean_elements(times, targets_teme_km, seed, epoch, norad, max_nfev=400):
    """Optimizer receives training arrays only. Held-out data never enter this API."""
    targets = np.asarray(targets_teme_km)
    if len(times)<12 or targets.shape!=(len(times),3): raise ValueError('Insufficient or invalid fitting targets')
    bounds = ([-np.inf,-.15,-.15,-1.,-1.,np.log(.8)],
              [np.inf,.15,.15,1.,1.,np.log(1.2)])
    initial = np.asarray(seed,dtype=float)
    if np.any(initial<=bounds[0]) or np.any(initial>=bounds[1]): raise ValueError('Seed outside supported fitting bounds')
    def residual(parameters):
        try: return (propagate(satellite(parameters,epoch,norad),times)-targets).ravel()
        except ValueError: return np.full(targets.size,1e8)
    def jacobian(parameters):
        # SciPy's generic absolute step is too large for nearly equatorial GEO
        # inclination vectors and can cross SGP4's low-inclination branch.
        steps=[1e-7,1e-8,1e-8,1e-9,1e-9,1e-8]
        columns=[]
        for j,step in enumerate(steps):
            plus=parameters.copy();minus=parameters.copy()
            plus[j]+=step;minus[j]-=step
            columns.append((residual(plus)-residual(minus))/(2*step))
        return np.column_stack(columns)
    solution = least_squares(residual,initial,bounds=bounds,method='trf',jac=jacobian,
                             x_scale=[1,.01,.01,.1,.1,.01],loss='linear',max_nfev=max_nfev,
                             ftol=1e-11,xtol=1e-11,gtol=1e-9)
    model = satellite(solution.x,epoch,norad)
    singular_values = np.linalg.svd(solution.jac,compute_uv=False)
    diagnostics = {'success':bool(solution.success),'message':solution.message,'nfev':solution.nfev,
                   'cost_km2':float(solution.cost),'optimality':float(solution.optimality),
                   'jacobian_rank':int(np.linalg.matrix_rank(solution.jac)),
                   'jacobian_condition':float(singular_values[0]/singular_values[-1]) if singular_values[-1]>0 else None,
                   'initial_rms_km':float(np.sqrt(np.mean(np.sum(residual(initial).reshape(-1,3)**2,axis=1)))),
                   'parameters':solution.x.tolist(),'parameterization':'lambda, e*cos(varpi), e*sin(varpi), tan(i/2)*cos(node), tan(i/2)*sin(node), log(n_rev_day)',
                   'bstar_fixed':0,'mean_motion_derivatives_fixed':[0,0], 'sgp4_branch':model.method}
    return model,diagnostics

def metrics(delta,times):
    if not len(delta): return None
    separation = np.linalg.norm(delta,axis=1)
    maximum = int(np.argmax(separation))
    return {'epochs':len(delta),'rms_km':float(np.sqrt(np.mean(separation**2))),
            'mean_km':float(separation.mean()),'max_km':float(separation[maximum]),
            'max_utc':times[maximum].utc.isot+'Z'}

def evaluate_model(model,times,targets,train_mask):
    """Score a frozen model; validation cannot change its fitted parameters."""
    delta = propagate(model,times)-targets
    return delta,metrics(delta[train_mask],times[train_mask]),metrics(delta[~train_mask],times[~train_mask])

def target_state(e,times):
    half = TimeDelta(.5,format='sec')
    p = broadcast_position(e,times)
    velocity = broadcast_position(e,times+half)-broadcast_position(e,times-half)
    rep = CartesianRepresentation(p.T*u.km).with_differentials(CartesianDifferential(velocity.T*u.km/u.s))
    state = ITRS(rep,obstime=times).transform_to(TEME(obstime=times))
    return state.cartesian.xyz.to_value(u.km).T,state.cartesian.differentials['s'].d_xyz.to_value(u.km/u.s).T

def export_omm(model,epoch,identity,gps):
    object_id = next((g.fields['OBJECT_ID'] for g in gps if g.norad==identity['norad_id']),None)
    if not object_id: raise ValueError('Missing verified international designator; no export')
    when = epoch.utc.copy();when.precision=6
    return {'OBJECT_NAME':identity['name'],'OBJECT_ID':object_id,'NORAD_CAT_ID':identity['norad_id'],
            'EPOCH':when.isot,'MEAN_MOTION':float(model.no_kozai*1440/(2*np.pi)),
            'ECCENTRICITY':float(model.ecco),'INCLINATION':float(np.degrees(model.inclo)),
            'RA_OF_ASC_NODE':float(np.degrees(model.nodeo)%360),'ARG_OF_PERICENTER':float(np.degrees(model.argpo)%360),
            'MEAN_ANOMALY':float(np.degrees(model.mo)%360),'BSTAR':0.,'MEAN_MOTION_DOT':0.,'MEAN_MOTION_DDOT':0.,
            'EPHEMERIS_TYPE':0,'CLASSIFICATION_TYPE':'U','ELEMENT_SET_NO':1,'REV_AT_EPOCH':0,
            'CENTER_NAME':'EARTH','REF_FRAME':'TEME','TIME_SYSTEM':'UTC','MEAN_ELEMENT_THEORY':'SGP4',
            'COMMENT':'Experimental NAVIC-BROADCAST-FIT; independently generated, not CelesTrak SupGP; REV_AT_EPOCH=0 is unspecified. Fit/holdout limits and source hashes are in fit_summary.json.'}

def generate_models(records,identities,gps,times,config):
    cfg = settings(config)
    if not cfg['enabled']: return {'enabled':False},[],[]
    start = times[0]
    day_end=Time(str(date.fromisoformat(start.utc.isot[:10])+timedelta(days=1)),scale='utc')
    end = start+TimeDelta(cfg['train_hours']*3600,format='sec')
    spacing = int(round(cfg['sample_seconds']/config['step_seconds']))
    if spacing<1 or abs(spacing*config['step_seconds']-cfg['sample_seconds'])>1e-7:
        raise ValueError('Generator sample_seconds must be a multiple of the comparison step')
    sample = times[::spacing]
    is_train = (sample.tai-end.tai).sec < -1e-6
    summary = {'enabled':True,'product':'NAVIC-BROADCAST-FIT','experimental':True,
               'assessment':'model fit and held-out broadcast consistency, not absolute accuracy',
               'not_celestrak_supgp':True,'settings':cfg,
               'train_start_utc':start.utc.isot+'Z','train_end_exclusive_utc':end.utc.isot+'Z',
               'validation_start_utc':end.utc.isot+'Z','validation_end_exclusive_utc':day_end.utc.isot+'Z',
               'initialization':'broadcast TEME position/velocity from training arc; GP used for catalogue metadata only',
               'satellites':[]}
    exported,all_rows = [],[]
    for identity in identities:
        prn=identity['prn'];group=[e for e in records if e.prn==prn]
        targets=np.full((len(sample),3),np.nan);velocities=targets.copy()
        samples=[];batches={}
        for i,time in enumerate(sample):
            # No training ephemeris clock epoch after the split is used.
            allowed=[e for e in group if e.toc_gps<=float(end.gps)] if is_train[i] else group
            e,flags=select_ephemeris(allowed,time,config['broadcast_max_age_seconds'])
            samples.append({'prn':prn,'norad_id':identity['norad_id'],'utc':time.utc.isot+'Z',
                            'partition':'fit' if is_train[i] else 'holdout','separation_km':None,
                            'radial_km':None,'along_km':None,'cross_km':None,
                            'ephemeris_key':e.key if e else None,'flags':flags})
            if e: batches.setdefault(e.key,(e,[]))[1].append(i)
        for e,idx in batches.values(): targets[idx],velocities[idx]=target_state(e,sample[idx])
        usable=np.isfinite(targets).all(axis=1)
        train=usable&is_train;holdout=usable&~is_train
        train_count,holdout_count=int(train.sum()),int(holdout.sum())
        train_coverage=train_count/max(1,int(is_train.sum()))
        holdout_coverage=holdout_count/max(1,int((~is_train).sum()))
        span=lambda mask:float((sample[mask][-1]-sample[mask][0]).sec/3600) if mask.sum()>1 else 0.
        reasons=[]
        if not identity['confirmed']: reasons.append('identity_geometry_unconfirmed')
        if train_coverage<cfg['min_train_coverage'] or span(train)<cfg['min_train_span_hours']: reasons.append('insufficient_fit_coverage')
        if holdout_coverage<cfg['min_validation_coverage'] or span(holdout)<cfg['min_validation_span_hours']: reasons.append('insufficient_holdout_coverage')
        item={k:identity[k] for k in ('prn','norad_id','name','orbit_class')}
        item.update(status='Rejected',reasons=reasons,fit=None,holdout=None,
                    fit_coverage_percent=100*train_coverage,holdout_coverage_percent=100*holdout_coverage,
                    fit_epochs=train_count,holdout_epochs=holdout_count,
                    input_gap_flags=dict(Counter(flag for r in samples for flag in r['flags'])),
                    thresholds=cfg['thresholds'][identity['orbit_class']])
        if reasons:
            summary['satellites'].append(item);all_rows.extend(samples);continue
        try:
            first=np.flatnonzero(train)[0];epoch=sample[first]
            seed=osculating_seed(targets[first],velocities[first])
            model,diagnostics=fit_mean_elements(sample[train],targets[train],seed,epoch,identity['norad_id'],cfg['max_nfev'])
            idx=np.flatnonzero(usable)
            delta,fit,holdout_result=evaluate_model(model,sample[usable],targets[usable],is_train[usable])
            item.update(fit=fit,holdout=holdout_result,optimizer=diagnostics,epoch_utc=epoch.utc.isot+'Z')
            if not diagnostics['success']: reasons.append('optimizer_not_converged')
            if diagnostics['jacobian_rank']<6: reasons.append('fit_not_identifiable')
            if model.method!='d': reasons.append('unexpected_sgp4_branch')
            gate=item['thresholds']
            if fit['rms_km']>gate['fit_rms_km']: reasons.append('fit_rms_gate')
            if holdout_result['rms_km']>gate['validation_rms_km']: reasons.append('holdout_rms_gate')
            if holdout_result['max_km']>gate['validation_max_km']: reasons.append('holdout_max_gate')
            omm=export_omm(model,epoch,identity,gps)
            omm['COMMENT']+=(f" Fit: [{summary['train_start_utc']}, {summary['train_end_exclusive_utc']});"
                             f" held-out validation: [{summary['validation_start_utc']}, {summary['validation_end_exclusive_utc']});"
                             f" fit RMS {fit['rms_km']:.6f} km; validation RMS {holdout_result['rms_km']:.6f} km."
                             ' No validity beyond these tested windows is established.')
            # Validate the exported representation, not just the in-memory optimizer object.
            from sgp4 import omm as omm_parser
            roundtrip=Satrec();omm_parser.initialize(roundtrip,omm)
            roundtrip_error=float(np.max(np.linalg.norm(propagate(roundtrip,sample[usable])-propagate(model,sample[usable]),axis=1)))
            item['export_roundtrip_max_km']=roundtrip_error
            if roundtrip_error>1e-5: reasons.append('export_roundtrip_gate')
            for j,i in enumerate(idx):
                r=targets[i]/np.linalg.norm(targets[i]);normal=np.cross(targets[i],velocities[i]);normal/=np.linalg.norm(normal);along=np.cross(normal,r)
                samples[i].update(separation_km=float(np.linalg.norm(delta[j])),radial_km=float(delta[j]@r),along_km=float(delta[j]@along),cross_km=float(delta[j]@normal))
            if not reasons: item['status']='Accepted';exported.append(omm)
        except (ValueError,FloatingPointError) as exc:
            reasons.append('fitting_failure');item['error']=str(exc)
        item['reasons']=reasons
        summary['satellites'].append(item);all_rows.extend(samples)
    summary['accepted_count']=len(exported)
    summary['rejected_count']=len(identities)-len(exported)
    summary['limitations']=['Experimental engineering thresholds are not calibrated accuracy limits.',
        'Holdout epochs are later and excluded from the optimization; both arcs still share broadcast system/model biases.',
        'No validity outside the tested window is established. This retrospective split is not a live forecast.',
        'BSTAR and mean-motion derivatives are fixed at zero; drag is not estimated for these near-geosynchronous fits.',
        'Published elements reproduce a broadcast trajectory; they are not independent truth or CelesTrak products.']
    return summary,exported,all_rows
