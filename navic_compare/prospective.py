"""Append-only issuance and future-message validation of serialized SGP4 OMMs.

The Git-tracked history is authoritative; Actions caches are only acquisition aids.
An issued model is never refitted, and each scored forecast epoch is written once.
"""
import csv
import gzip
import hashlib
import io
import json
from datetime import datetime, timezone
from importlib.metadata import version
from pathlib import Path

import numpy as np
from astropy.time import Time, TimeDelta
from sgp4.api import Satrec
from sgp4 import omm

from .acquire import Archive, atomic_json
from .fresh import fit_at_cutoff, supporting_inputs
from .fitting import export_omm, propagate, target_state
from .pipeline import clean, sha
from .rinex import Ephemeris, read_rinex, select_ephemeris
from .timeframes import check_eop, pinned_orientation
from .statefit import V1, V2, LABELS, current_message, fit_message_state

DEFAULTS = {'issue_interval_minutes': 30, 'horizon_hours': 48,
            'step_seconds': 300, 'reference_wait_hours': 3,
            'minimum_reference_coverage': .8,
            'age_bins_hours': [0, 1, 3, 6, 12, 24, 48]}


def utc(value):
    return value if isinstance(value, Time) else Time(datetime.fromisoformat(value.replace('Z', '+00:00')))


def iso(value):
    result = utc(value).utc.copy(); result.precision = 6
    return result.isot + 'Z'


def packed(value):
    return json.dumps(clean(value), sort_keys=True, separators=(',', ':'), allow_nan=False).encode()


def digest(value):
    return hashlib.sha256(packed(value)).hexdigest()


def software():
    return {name: version(name) for name in ('numpy','astropy','pyerfa','sgp4','scipy','requests')}


def code_sha256():
    return hashlib.sha256(b''.join(p.read_bytes() for p in sorted(Path(__file__).parent.glob('*.py')))).hexdigest()


def immutable(path, value):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    body = packed(value)
    if path.exists():
        previous = gzip.decompress(path.read_bytes()) if path.suffix == '.gz' else path.read_bytes()
        if previous != body: raise ValueError(f'Immutable history conflict: {path}')
        return
    with path.open('xb') as stream:
        stream.write(gzip.compress(body, mtime=0) if path.suffix == '.gz' else body)


def read(path):
    raw = Path(path).read_bytes()
    return json.loads(gzip.decompress(raw) if str(path).endswith('.gz') else raw)


def policy(config):
    p = {**DEFAULTS, **config.get('prospective', {})}
    if any(p[k] <= 0 for k in ('issue_interval_minutes', 'horizon_hours', 'step_seconds', 'reference_wait_hours')):
        raise ValueError('Prospective cadence, horizon, step and wait must be positive')
    bins = p['age_bins_hours']
    if bins[0] != 0 or any(b <= a for a, b in zip(bins, bins[1:])) or bins[-1] < p['horizon_hours']:
        raise ValueError('Age bins must increase from zero through the forecast horizon')
    versions = p.get('model_versions', [V1])
    if not versions or len(set(versions)) != len(versions) or any(v not in LABELS for v in versions):
        raise ValueError('Unknown or duplicate prospective model version')
    return p


def ephemeris_payload(e):
    return {'prn': e.prn, 'toc_gps': e.toc_gps, 'toe_gps': e.toe_gps,
            'values': e.values, 'clock': e.clock, 'message': e.message}


def restore_ephemeris(item):
    p = item['ephemeris']
    return Ephemeris(p['prn'], Time(p['toc_gps'], format='gps'), Time(p['toe_gps'], format='gps'),
                     [float('nan') if v is None else v for v in p['values']], p['clock'], p['message'])


def archive_inputs(history, root, support, journal):
    """Persist portable raw snapshots, parsed reference messages and first receipts."""
    history, root = Path(history), Path(root)
    by_hash = {}
    for meta in journal:
        by_hash.setdefault(meta['sha256'], meta)
    observations = []
    for checksum, meta in by_hash.items():
        suffix = '.rnx.gz' if meta['path'].endswith('.rnx.gz') else '.omm.json' if meta['path'].endswith('.omm.json') else None
        if not suffix: continue
        source = Path(meta['path'])
        if not source.exists(): source = root / 'raw' / Path(meta['path'].replace('\\', '/')).name
        if not source.exists(): continue
        body = source.read_bytes()
        if hashlib.sha256(body).hexdigest() != checksum: raise ValueError('Acquisition input checksum mismatch')
        receipt = meta.get('first_received_at') or meta.get('retrieved_at')
        if not receipt: continue
        saved = history / 'inputs' / (checksum + suffix)
        saved.parent.mkdir(parents=True, exist_ok=True)
        if saved.exists():
            if sha(saved) != checksum: raise ValueError('Durable input checksum mismatch')
        else:
            with saved.open('xb') as stream: stream.write(body)
        receipt_path = history / 'receipts' / (checksum + '.json')
        if receipt_path.exists():
            established = read(receipt_path)
            if established['sha256'] != checksum or established['suffix'] != suffix:
                raise ValueError('Durable receipt identity mismatch')
            # Different collectors can first fetch identical bytes at different
            # times. Keep the already established receipt; never rewrite history.
            receipt = established['first_received_at']
        else:
            immutable(receipt_path, {'sha256':checksum,'source':meta['source'],'first_received_at':receipt,'suffix':suffix})
        if suffix == '.rnx.gz': observations.append((checksum, receipt, saved))
    # A record's first-observed time is the earliest actually archived receipt,
    # independent of the order in which the input snapshots are processed.
    for checksum, receipt, saved in sorted(observations, key=lambda x: utc(x[1]).tai.jd):
        marker = history / 'ingested' / (checksum + '.json')
        if marker.exists(): continue
        try:
            records, header = read_rinex(saved, systems='I')
        except (ValueError,OSError,EOFError) as error:
            immutable(marker, {'sha256':checksum,'rejected':str(error)})
            continue
        for e in records:
            payload = ephemeris_payload(e); key = digest(payload)
            destination = history / 'records' / (key + '.json')
            if not destination.exists():
                immutable(destination, {'record_id': key, 'ephemeris': payload,
                    'first_received_at': receipt, 'snapshot_sha256': checksum})
        immutable(marker, {'sha256': checksum, 'header': header})
    versions = {}
    for kind in ('eop', 'leaps'):
        meta = support[kind]; body = Path(meta['path']).read_bytes()
        if hashlib.sha256(body).hexdigest() != meta['sha256']: raise ValueError('Supporting input checksum mismatch')
        destination = history / 'orientation' / (meta['sha256'] + '.' + kind + '.gz')
        destination.parent.mkdir(parents=True, exist_ok=True)
        if not destination.exists():
            with destination.open('xb') as stream: stream.write(gzip.compress(body, mtime=0))
        elif gzip.decompress(destination.read_bytes()) != body: raise ValueError('Orientation archive conflict')
        versions[kind] = {'sha256': meta['sha256'], 'source': meta['source']}
    return versions


def gp_catalogue(history):
    result = []
    for path in sorted((Path(history) / 'receipts').glob('*.json')):
        meta = read(path)
        if meta['suffix'] != '.omm.json': continue
        source = Path(history) / 'inputs' / (meta['sha256'] + meta['suffix'])
        if sha(source) != meta['sha256']: raise ValueError('Archived GP checksum mismatch')
        for fields in read(source):
            result.append({'fields': fields, 'snapshot_sha256': meta['sha256'],
                           'first_received_at': meta['first_received_at'], 'element_id': digest(fields)})
    return result


def eligible_gp(catalogue, norad, epoch, max_age_hours):
    eligible = [g for g in catalogue if int(g['fields']['NORAD_CAT_ID']) == norad
                and utc(g['first_received_at']) <= epoch
                and 0 <= (epoch - Time(g['fields']['EPOCH'].rstrip('Z'), scale='utc')).sec <= max_age_hours * 3600]
    return max(eligible, key=lambda g: (Time(g['fields']['EPOCH'].rstrip('Z'), scale='utc').tai.jd,
                                       utc(g['first_received_at']).tai.jd)) if eligible else None


def from_omm(fields):
    epoch = fields['EPOCH'].rstrip('Z')
    if '.' not in epoch: epoch += '.000000'
    model = Satrec(); omm.initialize(model, {**fields, 'EPOCH': epoch})
    return model


def issue_models(records, catalogue, support_gp, source, orientation, config, history, cutoff=None, clock=None):
    """Use only currently received inputs; record actual post-fit issuance time."""
    now = clock or (lambda: datetime.now(timezone.utc))
    cutoff = cutoff or Time(now())
    p = policy(config); slot = int(cutoff.to_datetime(timezone=timezone.utc).timestamp() // (p['issue_interval_minutes'] * 60))
    existing = [read(path) for path in (Path(history) / 'issues').glob('*.json')]
    attempts = []
    if utc(source.get('first_received_at') or source['retrieved_at']) > cutoff:
        raise ValueError('Training input was received after the fitting cutoff')
    pairs = [(prn, model_version) for prn in sorted({e.prn for e in records if e.prn.startswith('I')})
             for model_version in p.get('model_versions', [V1])]
    for prn, model_version in pairs:
        if any(i['prn'] == prn and i['slot'] == slot and i.get('model_version', V1) == model_version for i in existing): continue
        identity = {'prn': prn, **config.get('identity_catalogue', {}).get(prn, {})}
        if not identity.get('norad_id'):
            attempts.append({'prn': prn, 'status': 'identity_missing'}); continue
        group = [e for e in records if e.prn == prn]
        try:
            fitter = fit_at_cutoff if model_version == V1 else fit_message_state
            fitted, diagnostics = fitter(group, cutoff, config, identity['norad_id'])
            if fitted is None:
                attempts.append({'prn': prn, 'model_version': model_version, **diagnostics}); continue
            fields = export_omm(fitted, cutoff, identity, support_gp)
            issued = Time(now())
            if issued < cutoff: raise ValueError('Issue clock precedes training cutoff')
            baseline = eligible_gp(catalogue, identity['norad_id'], issued, config['gp_max_age_hours'])
            fields['COMMENT'] = ('Experimental prospective NAVIC-BROADCAST-FIT '+model_version+'. Frozen at actual issuance; '
                                 'not CelesTrak SupGP or an absolute accuracy product. REV_AT_EPOCH=0 unspecified.')
            serialized = from_omm(fields)
            # Test the actual exported representation, not only the optimizer object.
            probe = cutoff + TimeDelta([0, 60], format='sec')
            if np.max(np.linalg.norm(propagate(serialized, probe) - propagate(fitted, probe), axis=1)) > 1e-6:
                raise ValueError('OMM round-trip changed propagation by more than 1 mm')
            train_times = cutoff + TimeDelta(np.arange(-config['current_acquisition']['benchmark_train_hours'] * 3600, 0,
                config['current_acquisition']['benchmark_step_seconds']), format='sec')
            used = set()
            if model_version == V2:
                e, _ = current_message(group, cutoff, config)
                if e: used.add(digest(ephemeris_payload(e)))
            else:
                for t in train_times:
                    e, _ = select_ephemeris([e for e in group if e.toc_gps <= float(cutoff.gps)], t, config['broadcast_max_age_seconds'])
                    if e: used.add(digest(ephemeris_payload(e)))
            key = cutoff.utc.strftime('%Y%m%dT%H%M%S') + '-' + prn + '-' + digest(fields)[:12]
            item = {'schema_version': '1.1.0', 'issue_id': key, 'model_version': model_version, 'prn': prn, 'identity': identity, 'slot': slot,
                'issued_at': iso(issued), 'model_epoch_utc': iso(cutoff), 'omm': fields, 'omm_sha256': digest(fields),
                'frozen_gp': baseline, 'training_snapshot_sha256': source['sha256'], 'training_record_ids': sorted(used),
                'fit': diagnostics, 'orientation': orientation, 'policy': p, 'config': config, 'software': software(),
                'code_sha256': hashlib.sha256(b''.join(f.read_bytes() for f in sorted(Path(__file__).parent.glob('*.py')))).hexdigest()}
            immutable(Path(history) / 'issues' / (key + '.json'), item)
            attempts.append({'prn': prn, 'model_version': model_version, 'status': 'issued', 'issue_id': key})
        except (ValueError, FloatingPointError) as error:
            attempts.append({'prn': prn, 'model_version': model_version, 'status': 'rejected', 'reason': str(error)})
    return attempts


def reference_at(records, issue, epoch, asof):
    """Later messages only; no future-toc reference and no training-record reuse."""
    issued = utc(issue['issued_at']); allowed = []
    for item, e in records:
        if e.prn != issue['prn'] or item['record_id'] in issue['training_record_ids']: continue
        if not issued < utc(item['first_received_at']) <= asof: continue
        if not float(issued.gps) < e.toc_gps <= float(epoch.gps) + 1e-6: continue
        allowed.append(e)
    chosen, flags = select_ephemeris(allowed, epoch, issue['config']['broadcast_max_age_seconds'])
    if chosen:
        key = digest(ephemeris_payload(chosen))
        return next((item, e) for item, e in records if item['record_id'] == key), []
    return None, ['later_reference_missing', *flags]


def issue_grid(issue, asof):
    start = utc(issue['issued_at']); p = issue['policy']
    last = min(float((asof - start).sec), p['horizon_hours'] * 3600)
    return start + TimeDelta(np.arange(p['step_seconds'], last + 1e-6, p['step_seconds']), format='sec')


def load_scores(history, key):
    result = {}
    for path in sorted((Path(history) / 'scores' / key).glob('*.json.gz')):
        batch = read(path)
        if digest(batch) != path.name.removesuffix('.json.gz'): raise ValueError('Scoring chunk checksum mismatch')
        for row in batch['rows']:
            if row['utc'] in result: raise ValueError('Duplicate immutable forecast epoch')
            result[row['utc']] = row
    return result


def score_issue(issue, records, catalogue, asof, orientation, history, eop):
    if digest(issue['omm']) != issue['omm_sha256']: raise ValueError('Frozen OMM checksum mismatch')
    if issue['frozen_gp'] and digest(issue['frozen_gp']['fields']) != issue['frozen_gp']['element_id']:
        raise ValueError('Frozen GP checksum mismatch')
    previous = load_scores(history, issue['issue_id']); pending = []
    for epoch in issue_grid(issue, asof):
        when = iso(epoch)
        if when in previous: continue
        reference, flags = reference_at(records, issue, epoch, asof)
        if reference is None and (asof - epoch).sec < issue['policy']['reference_wait_hours'] * 3600 - 1e-6: continue
        pending.append((epoch, reference, flags))
    if not pending: return previous
    times = Time([x[0] for x in pending]); orientation_status = check_eop(times, eop)
    ours = from_omm(issue['omm']); frozen = from_omm(issue['frozen_gp']['fields']) if issue['frozen_gp'] else None
    rows = []
    for epoch, reference, flags in pending:
        row = {'utc': iso(epoch), 'forecast_age_hours': round(float((epoch - utc(issue['issued_at'])).sec / 3600),9),
               'model_age_hours': float((epoch - utc(issue['model_epoch_utc'])).sec / 3600),
               'ours': None, 'frozen_gp': None, 'latest_gp': None, 'reference': None, 'flags': flags}
        if reference:
            item, e = reference
            p, v = target_state(e, Time([epoch])); r = p[0]; velocity = v[0]
            radial = r / np.linalg.norm(r); cross = np.cross(r, velocity); cross /= np.linalg.norm(cross); along = np.cross(cross, radial)
            row['reference'] = {'record_id': item['record_id'], 'snapshot_sha256': item['snapshot_sha256'],
                'first_received_at': item['first_received_at'], 'toc_utc': iso(e.toc), 'toe_utc': iso(e.toe),
                'toe_age_seconds': float((epoch - e.toe).sec), 'iodec': e.iode, 'health': e.health, 'ura_m': e.ura}
            latest = eligible_gp(catalogue, issue['identity']['norad_id'], epoch, issue['config']['gp_max_age_hours'])
            for label, model, gp in [('ours', ours, None), ('frozen_gp', frozen, issue['frozen_gp']),
                                     ('latest_gp', from_omm(latest['fields']) if latest else None, latest)]:
                if model is None:
                    row['flags'].append(label + '_missing'); continue
                try:
                    delta = propagate(model, Time([epoch]))[0] - r
                    result = {'separation_km': float(np.linalg.norm(delta)), 'radial_km': float(delta @ radial),
                              'along_km': float(delta @ along), 'cross_km': float(delta @ cross)}
                    if gp:
                        result.update(element_id=gp['element_id'], snapshot_sha256=gp['snapshot_sha256'],
                                      age_hours=float((epoch - Time(gp['fields']['EPOCH'].rstrip('Z'), scale='utc')).sec / 3600),
                                      first_received_at=gp['first_received_at'])
                    row[label] = result
                except ValueError as error: row['flags'].append(label + '_sgp4_error: ' + str(error))
        rows.append(row)
    context_rows = dict(previous)
    jump_limit = issue['config'].get('thresholds', {}).get(issue['identity'].get('orbit_class'), {}).get('jump_km')
    for row in rows:
        previous_row = max((r for r in context_rows.values() if r['utc'] < row['utc']),key=lambda r:r['utc'],default=None)
        if previous_row and 0 < (utc(row['utc'])-utc(previous_row['utc'])).sec <= issue['policy']['step_seconds']*1.5:
            if row['reference'] and previous_row['reference'] and row['reference']['record_id'] != previous_row['reference']['record_id']:
                row['flags'].append('reference_message_change')
            for cohort in ('ours','frozen_gp','latest_gp'):
                a,b = previous_row[cohort],row[cohort]
                if a and b:
                    if cohort=='latest_gp' and a['element_id'] != b['element_id']: row['flags'].append('latest_gp_set_change')
                    if jump_limit and abs(b['separation_km']-a['separation_km']) > jump_limit: row['flags'].append(cohort+'_separation_jump')
        context_rows[row['utc']] = row
    batch = {'issue_id': issue['issue_id'], 'scored_at': iso(asof), 'orientation': orientation, 'rows': rows, 'software': software(),
             'earth_orientation_status':orientation_status,'code_sha256':code_sha256(),
             'software_note': 'Positions in TEME; UT1 and polar motion from pinned orientation. First score is immutable.'}
    name = digest(batch) + '.json.gz'
    immutable(Path(history) / 'scores' / issue['issue_id'] / name, batch)
    return {**previous, **{r['utc']: r for r in rows}}


def statistics(rows, cohort):
    valid = [r for r in rows if r.get(cohort) is not None]
    if not valid: return None
    d = np.array([r[cohort]['separation_km'] for r in valid]); maximum = int(np.argmax(d))
    return {'epochs': len(d), 'rms_km': float(np.sqrt(np.mean(d*d))), 'mean_km': float(d.mean()),
            'p50_km': float(np.median(d)), 'p95_km': float(np.percentile(d, 95)), 'max_km': float(d[maximum]),
            'max_utc': valid[maximum]['utc'],
            'rtn_rms_km': [float(np.sqrt(np.mean([r[cohort][axis]**2 for r in valid]))) for axis in ('radial_km', 'along_km', 'cross_km')]}


def pair_statistics(rows, baseline):
    matched = [r for r in rows if r.get('ours') is not None and r.get(baseline) is not None]
    a, b = statistics(matched, 'ours'), statistics(matched, baseline)
    return {'common_epochs': len(matched), 'ours': a, 'baseline': b,
            'rms_reduction_percent': 100*(b['rms_km']-a['rms_km'])/b['rms_km'] if b and b['rms_km'] > 0 else None,
            'lower_separation_percent': 100*sum(r['ours']['separation_km'] < r[baseline]['separation_km'] for r in matched)/len(matched) if matched else None}


def aggregate(rows, bins):
    def one(group):
        return {'recorded_epochs': len(group), 'reference_epochs': sum(r['reference'] is not None for r in group),
                'ours': statistics(group, 'ours'), 'frozen_pair': pair_statistics(group, 'frozen_gp'),
                'latest_pair': pair_statistics(group, 'latest_gp')}
    result = one(rows)
    result['age_bins'] = [{'start_hours': a, 'end_hours': b, **one([r for r in rows if a < r['forecast_age_hours'] <= b])}
                          for a, b in zip(bins, bins[1:])]
    return result


def build_summary(history, asof, config, dashboard, attempts):
    destination = Path(dashboard) / 'prospective'; destination.mkdir(parents=True, exist_ok=True)
    issues = []; all_rows = []; per_satellite = {}; artifacts = {}; csv_rows = []; per_version = {}
    for path in sorted((Path(history) / 'issues').glob('*.json'), reverse=True):
        issue = read(path); scores = load_scores(history, issue['issue_id']); rows = sorted(scores.values(), key=lambda r: r['utc'])
        metrics = aggregate(rows, issue['policy']['age_bins_hours']); due = len(issue_grid(issue, asof))
        reasons = []
        mature = (asof-utc(issue['issued_at'])).sec >= (issue['policy']['horizon_hours']+issue['policy']['reference_wait_hours'])*3600
        if mature and metrics['reference_epochs'] / max(due, 1) < issue['policy']['minimum_reference_coverage']: reasons.append('insufficient_future_reference_coverage')
        threshold = issue['config']['thresholds'].get(issue['identity'].get('orbit_class'), {})
        if metrics['ours']:
            if metrics['ours']['rms_km'] > threshold.get('rms_km', float('inf')): reasons.append('provisional_rms_threshold')
            if metrics['ours']['max_km'] > threshold.get('max_km', float('inf')): reasons.append('provisional_max_threshold')
        if any('ours_separation_jump' in r['flags'] for r in rows): reasons.append('provisional_jump_threshold')
        status = 'Review' if reasons else 'Complete' if mature else 'Tracking' if metrics['ours'] else 'Waiting'
        model_version = issue.get('model_version', V1)
        entry = {'issue_id': issue['issue_id'], 'model_version': model_version, 'prn': issue['prn'], 'name': issue['identity']['name'],
                 'issued_at': issue['issued_at'], 'model_epoch_utc': issue['model_epoch_utc'], 'status': status,
                 'reasons': reasons, 'expected_due_epochs': due, 'pending_epochs': due-len(rows),
                 'reference_coverage_percent': 100*metrics['reference_epochs']/due if due else None, **metrics}
        issues.append(entry); all_rows.extend(rows); per_satellite.setdefault(issue['prn'], []).extend(rows)
        per_version.setdefault(model_version, {}).setdefault(issue['prn'], []).extend(rows)
        detail = {'issue': issue, 'summary': entry, 'rows': rows}
        name = 'series/' + issue['issue_id'] + '.json'; atomic_json(destination/name, clean(detail)); artifacts[name] = sha(destination/name)
        for age in [{'start_hours':0,'end_hours':issue['policy']['horizon_hours'],**metrics},*metrics['age_bins']]:
            for baseline in ('frozen_pair','latest_pair'):
                pair=age[baseline]
                csv_rows.append({'issue_id':issue['issue_id'],'model_version':model_version,'prn':issue['prn'],'issued_at':issue['issued_at'],
                    'age_start_hours':age['start_hours'],'age_end_hours':age['end_hours'],'baseline':baseline,
                    'common_epochs':pair['common_epochs'],'our_rms_km':pair['ours']['rms_km'] if pair['ours'] else None,
                    'baseline_rms_km':pair['baseline']['rms_km'] if pair['baseline'] else None,
                    'our_mean_km':pair['ours']['mean_km'] if pair['ours'] else None,
                    'our_max_km':pair['ours']['max_km'] if pair['ours'] else None,
                    'our_p95_km':pair['ours']['p95_km'] if pair['ours'] else None,
                    'rms_reduction_percent':pair['rms_reduction_percent'],'lower_separation_percent':pair['lower_separation_percent']})
    bins = policy(config)['age_bins_hours']
    versions = [{'model_version': v, 'label': LABELS.get(v,v),
                 'issue_count': sum(i['model_version']==v for i in issues),
                 'fleet': aggregate([r for rows in satellites.values() for r in rows], bins),
                 'satellites': [{'prn': prn, **aggregate(rows, bins)} for prn, rows in sorted(satellites.items())]}
                for v, satellites in sorted(per_version.items(), reverse=True)]
    summary = {'schema_version': '1.1.0', 'generated_at': iso(asof), 'issue_count': len(issues), 'versions': versions,
        'satellite_count': len(per_satellite), 'first_issue_utc': min((i['issued_at'] for i in issues), default=None),
        'latest_issue_utc': max((i['issued_at'] for i in issues), default=None), 'policy': policy(config),
        'fleet': aggregate(all_rows, bins), 'issues': issues,
        'satellites': [{'prn': prn, 'issue_count': sum(i['prn']==prn for i in issues), **aggregate(rows, bins)} for prn, rows in sorted(per_satellite.items())],
        'last_issuance_attempts': attempts,
        'notes': ['Broadcast consistency, not absolute accuracy. No prospective scores are backfilled from retrospective experiments.',
                  'Reference messages must first arrive after issue, have toc after issue and no later than the checked epoch, and cannot be training records.',
                  'Frozen GP was available at issuance. Latest GP means latest received by each checked epoch; future snapshots are excluded.',
                  'Statistics pool forecast-epoch pairs. Overlapping forecasts share reference epochs and are not independent observations.',
                  'Waiting means future messages have not supplied a score yet. Missing references finalize after the configured wait; first scores are immutable.',
                  'Issue times, model epochs and prediction ages are distinct. Stored OMMs never refit. GEO/IGSO thresholds are provisional.']}
    summary['notes'].append('V1 is the six-hour position-fit control. V2 is an experimental latest-message position-and-motion fit; forward targets come only from the already-received message. Dashboard statistics are separated by version. Replay results are not prospective evidence.')
    atomic_json(destination/'summary.json', clean(summary))
    output = io.StringIO(newline='')
    keys = list(csv_rows[0]) if csv_rows else ['issue_id','prn','issued_at','age_start_hours','age_end_hours','baseline','common_epochs','our_rms_km','baseline_rms_km']
    writer = csv.DictWriter(output, fieldnames=keys); writer.writeheader(); writer.writerows(csv_rows)
    (destination/'statistics.csv').write_text(output.getvalue(), encoding='utf-8', newline='')
    (destination/'report.md').write_text(prospective_report(summary), encoding='utf-8')
    for name in ('summary.json','statistics.csv','report.md'): artifacts[name] = sha(destination/name)
    atomic_json(destination/'latest.json', {'summary':'summary.json','summary_sha256':artifacts['summary.json'],'artifacts':artifacts})
    return summary


def prospective_report(s):
    table = '\n'.join('| '+ ' | '.join([i['prn'], i['model_version'], i['issued_at'], i['status'], str(i['reference_epochs']),
        f"{i['ours']['rms_km']:.4f}" if i['ours'] else '—', str(i['frozen_pair']['common_epochs']), str(i['latest_pair']['common_epochs'])])+' |' for i in s['issues'])
    return f"""# Prospective NavIC SGP4 validation

Updated {s['generated_at']}. {s['issue_count']} immutable issued models across {s['satellite_count']} satellites.

{' '.join(s['notes'])}

Models issue every {s['policy']['issue_interval_minutes']} minutes where fitting coverage and numerical checks permit. V1 fits six hours of already received positions. V2 fits position and motion over issue ±1 hour from one healthy message available at cutoff, within the toe policy including its differentiation stencil. V2 uses 60-second sampling and velocity residuals scaled by 10,000 seconds; Bstar and mean-motion derivatives stay zero. Its future targets are predictions of that message, not later messages. Both versions remain experimental; V2 is a challenger, not an accepted replacement. The serialized OMM is round-trip checked and frozen at actual issuance. Scores span up to {s['policy']['horizon_hours']} hours in {s['policy']['step_seconds']}-second steps. Missing references mature after {s['policy']['reference_wait_hours']} hours. No performance is claimed before later-message scores exist. Filter by model_version in the statistics CSV; pooled legacy fleet totals combine versions and must not be used to judge one fitter.

Both baseline comparisons use identical matched epochs within each comparison, with separate sample counts. RMS reductions and win fractions are descriptive, not significance tests. Latest GP is a rolling operational baseline, not a fair equal-age forecast. Exact snapshot and message identifiers, GP ages and signed RTN residuals are retained for every score. The prediction-age bins begin at actual issuance, not model epoch. Broadcast validity is the declared analysis policy, not an independently confirmed ICD fit guarantee.

| PRN | Model version | Issued UTC | Status | Reference epochs | Our RMS km | Frozen GP common epochs | Latest GP common epochs |
|---|---|---|---|---|---|---|---|
{table}

The Git-tracked history/prospective directory stores original RINEX/GP bytes, first receipts, parsed messages, frozen model documents, compressed pinned EOP/leap versions and immutable scoring chunks. GitHub caches are not the authoritative model archive. No automatic deletion is configured. Git repository size will grow; plan external archival storage as the history expands. The cumulative statistics CSV contains matched-epoch summaries; selected-model epoch CSVs and series JSON retain gaps and cohort identifiers. Blanks are gaps, not zero error.
"""


def run_tracking(config, root='data', history='history/prospective', dashboard='dashboard/dist'):
    archive = Archive(root); support, journal = supporting_inputs(archive, config)
    orientation = archive_inputs(history, root, support, journal)
    catalogue = gp_catalogue(history)
    acquisition = read(Path(root)/'acquisition-current.json') if (Path(root)/'acquisition-current.json').exists() else {}
    selected = acquisition.get('selected_input')
    attempts = []
    with pinned_orientation(support['eop']['path'], support['leaps']['path']) as eop:
        now = Time(datetime.now(timezone.utc)); check_eop(now, eop)
        from astropy.utils import iers
        if iers.LeapSeconds.open(support['leaps']['path']).expires < now: raise ValueError('Leap-second table expired')
        if selected and 0 <= (now-utc(acquisition['checked_at'])).sec <= 3600:
            sources = [Path(history)/'inputs'/(selected['sha256']+'.rnx.gz')]
            # Include already received adjacent-day records for early-UTC fits.
            for meta_path in (Path(history)/'receipts').glob('*.json'):
                meta = read(meta_path)
                if meta['suffix']=='.rnx.gz' and utc(meta['first_received_at'])<=now and (now-utc(meta['first_received_at'])).sec<36*3600:
                    sources.append(Path(history)/'inputs'/(meta['sha256']+'.rnx.gz'))
            records = {}; headers = []
            for source in set(sources):
                marker = Path(history)/'ingested'/(source.name.removesuffix('.rnx.gz')+'.json')
                if marker.exists() and read(marker).get('rejected'): continue
                parsed, header = read_rinex(source, systems='I'); headers.append(header)
                for e in parsed: records[digest(ephemeris_payload(e))]=e
            fit_begin = now-TimeDelta(config['current_acquisition']['benchmark_train_hours']*3600,format='sec')
            check_eop(Time([fit_begin,now+TimeDelta(3601,format='sec')]),eop)
            # Parsed headers are archived; unsupported time-correction notes remain visible.
            gps = []
            from .orbits import parse_gp
            for meta in support['gp']:
                durable = Path(history)/'inputs'/(meta['sha256']+'.omm.json')
                if durable.exists(): gps.extend(parse_gp(durable))
            attempts = issue_models(list(records.values()), catalogue, gps, selected, orientation, config, history)
        else: attempts = [{'status':'no_issue','reason':'current_acquisition_missing_or_older_than_one_hour'}]
        asof = Time(datetime.now(timezone.utc))
        references = []
        for path in (Path(history)/'records').glob('*.json'):
            item = read(path)
            if digest(item['ephemeris']) != item['record_id']: raise ValueError('Archived reference checksum mismatch')
            references.append((item, restore_ephemeris(item)))
        for path in sorted((Path(history)/'issues').glob('*.json')):
            score_issue(read(path), references, catalogue, asof, orientation, history, eop)
    batch = {'checked_at':iso(asof),'orientation':orientation,'attempts':attempts,'software':software(),
             'code_sha256':code_sha256(),'config':config}
    immutable(Path(history)/'runs'/(digest(batch)+'.json'), batch)
    return build_summary(history, asof, config, dashboard, attempts)
