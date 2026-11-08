"""Keep the shared GP HTTP rate guard alive even after Actions cache eviction."""
import hashlib
import json
import sys
from pathlib import Path
import shutil
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from navic_compare.acquire import atomic_json
from navic_compare.prospective import immutable

config=json.loads(Path('config/default.json').read_text())
key=hashlib.sha256(config['gp_url'].encode()).hexdigest()
cached=Path('data/cache')/(key+'.json')
durable=Path('history/prospective/gp-http-state.json')
if sys.argv[1]=='restore':
    if durable.exists():
        saved=json.loads(durable.read_text());current=json.loads(cached.read_text()) if cached.exists() else {}
        if saved.get('last_attempt',0)>=current.get('last_attempt',0):
            record=saved.get('record')
            if record:
                raw=Path('history/prospective/inputs')/(record['sha256']+'.omm.json')
                if hashlib.sha256(raw.read_bytes()).hexdigest()!=record['sha256']:raise ValueError('GP guard archive checksum mismatch')
                target=Path('data/raw')/raw.name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(raw,target)
                record['path']=str(target.resolve())
                journal=Path('data/retrievals.jsonl');existing=journal.read_text().splitlines() if journal.exists() else []
                if not any(json.loads(line)['sha256']==record['sha256'] for line in existing):
                    with journal.open('a',encoding='utf-8') as stream:stream.write(json.dumps(record)+'\n')
            atomic_json(cached,saved)
elif sys.argv[1]=='save':
    if cached.exists():
        state=json.loads(cached.read_text());record=state.get('record')
        if record:
            source=Path(record['path'])
            if not source.exists():source=Path('data/raw')/Path(record['path'].replace('\\','/')).name
            if hashlib.sha256(source.read_bytes()).hexdigest()!=record['sha256']:raise ValueError('GP guard source checksum mismatch')
            target=Path('history/prospective/inputs')/(record['sha256']+'.omm.json');target.parent.mkdir(parents=True,exist_ok=True)
            if not target.exists():shutil.copyfile(source,target)
            receipt=Path('history/prospective/receipts')/(record['sha256']+'.json')
            if not receipt.exists():immutable(receipt,{'sha256':record['sha256'],'source':record['source'],
                'first_received_at':record.get('first_received_at') or record['retrieved_at'],'suffix':'.omm.json'})
            record['path']=target.name
        atomic_json(durable,state)
else:raise ValueError('Expected restore or save')
