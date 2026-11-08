"""Seed an empty CI GP archive from the initial genuine observation, retaining rate limits."""
import json
from pathlib import Path
import shutil
from datetime import datetime
import hashlib

def atomic_json(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    temp=path.with_suffix('.tmp')
    temp.write_text(json.dumps(value,indent=2),encoding='utf-8')
    temp.replace(path)

source=Path('seed/gp')
root=Path('data')
if source.exists():
    for meta_path in source.glob('*.meta.json'):
        meta=json.loads(meta_path.read_text())
        raw=source/(meta['sha256']+'.omm.json')
        target=root/'raw'/raw.name
        if target.exists(): continue
        target.parent.mkdir(parents=True,exist_ok=True)
        if hashlib.sha256(raw.read_bytes()).hexdigest()!=meta['sha256']: raise ValueError('Seed checksum mismatch')
        shutil.copy2(raw,target)
        meta['path']=str(target.resolve())
        root.mkdir(parents=True,exist_ok=True)
        with (root/'retrievals.jsonl').open('a') as f: f.write(json.dumps(meta)+'\n')
        key=hashlib.sha256(meta['source'].encode()).hexdigest()
        cache=root/'cache'/(key+'.json')
        if not cache.exists():
            atomic_json(cache,{'last_attempt':datetime.fromisoformat(meta['retrieved_at']).timestamp(),'record':meta})
