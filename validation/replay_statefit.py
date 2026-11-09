"""Reproduce the version-2 chronological replay without network requests.

Run from the repository root: python validation/replay_statefit.py
This writes a retrospective research report, never production issues or scores.
"""
import gzip
import hashlib
import json
import sys
from pathlib import Path
from types import SimpleNamespace
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import numpy as np
from astropy.time import Time, TimeDelta
from navic_compare.prospective import read, restore_ephemeris, utc, reference_at, from_omm, digest
from navic_compare.fitting import propagate, target_state, metrics, export_omm
from navic_compare.statefit import fit_message_state
from navic_compare.timeframes import pinned_orientation, check_eop
from navic_compare.pipeline import clean

folder = Path(__file__).parent / 'statefit-2026-11-09'


def replay():
    bundle = read(folder/'replay-inputs.json.gz')
    refs = [(m, restore_ephemeris(m)) for m in bundle['records']]
    for m, _ in refs:
        if digest(m['ephemeris']) != m['record_id']: raise ValueError('Record checksum mismatch')
    temp = Path('.test-tmp/statefit-orientation'); temp.mkdir(parents=True, exist_ok=True)
    orientation = bundle['orientation']
    for kind in ('eop', 'leaps'):
        checksum = orientation[kind]['sha256']
        body = gzip.decompress((Path('history/prospective/orientation')/(checksum+'.'+kind+'.gz')).read_bytes())
        if hashlib.sha256(body).hexdigest() != checksum: raise ValueError('Orientation checksum mismatch')
        (temp/kind).write_bytes(body)
    result = {'mode': 'retrospective chronological replay; not prospective scores',
              'bundle_sha256': hashlib.sha256((folder/'replay-inputs.json.gz').read_bytes()).hexdigest(),
              'asof': bundle['asof'], 'orientation': orientation, 'periods': []}
    with pinned_orientation(str(temp/'eop'), str(temp/'leaps')) as eop:
        for period in bundle['periods']:
            rows = []
            for issue in period['issues']:
                cutoff = Time(issue['omm']['EPOCH'], scale='utc')
                group = [e for m,e in refs if e.prn==issue['prn'] and utc(m['first_received_at'])<=cutoff]
                sat, info = fit_message_state(group, cutoff, bundle['config'], issue['identity']['norad_id'])
                if sat is None: raise ValueError(info)
                gp = issue['frozen_gp']
                fields = export_omm(sat, cutoff, issue['identity'],
                    [SimpleNamespace(norad=issue['identity']['norad_id'], fields=gp['fields'])])
                models = {'v1': from_omm(issue['omm']), 'v2': from_omm(fields), 'frozen_gp': from_omm(gp['fields'])}
                times = utc(issue['issued_at'])+TimeDelta(np.arange(300, period['hours']*3600+1e-6, 300),format='sec')
                chosen = [reference_at(refs, issue, t, utc(bundle['asof']))[0] for t in times]
                valid = np.array([c is not None and t<=utc(bundle['asof']) for c,t in zip(chosen,times)])
                times = times[valid]; chosen = [c for c,ok in zip(chosen,valid) if ok]
                check_eop(times,eop)
                positions = np.zeros((len(times),3)); batches = {}
                for j,c in enumerate(chosen): batches.setdefault(c[0]['record_id'],(c[1],[]))[1].append(j)
                for e,indices in batches.values(): positions[indices],_ = target_state(e,times[indices])
                residuals = {key: propagate(model,times)-positions for key,model in models.items()}
                scores = {key: metrics(delta,times) for key,delta in residuals.items()}
                epoch_rows = [{'utc': t.utc.isot+'Z', 'reference_record_id': c[0]['record_id'],
                    **{key+'_separation_km':float(np.linalg.norm(delta[j])) for key,delta in residuals.items()}}
                    for j,(t,c) in enumerate(zip(times,chosen))]
                rows.append({'prn':issue['prn'],'original_issue_id':issue['issue_id'],'cutoff':cutoff.utc.isot+'Z',
                             'scores':scores,'fit':info,'v2_omm':fields,'rows':epoch_rows})
            result['periods'].append({'name':period['name'],'requested_hours':period['hours'],'satellites':rows})
    (folder/'replay-results.json').write_text(json.dumps(clean(result),indent=2)+'\n',encoding='utf-8')
    for p in result['periods']:
        print(p['name'],[(s['prn'],{k:round(v['rms_km'],4) for k,v in s['scores'].items()}) for s in p['satellites']])
    return result


if __name__ == '__main__': replay()
