#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, shutil, stat, tempfile, zipfile
from pathlib import Path, PurePosixPath
ROOT='relay-workload-package'; MAX=200*1024*1024

def safe(n):
    p=PurePosixPath(n); return bool(n) and not p.is_absolute() and '..' not in p.parts and '\\' not in n

def sha(p):
    h=hashlib.sha256();
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
    return h.hexdigest()

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('zip'); ap.add_argument('--repo',default='.'); args=ap.parse_args(); src=Path(args.zip).resolve(); repo=Path(args.repo).resolve()
    if not zipfile.is_zipfile(src) or src.stat().st_size>MAX: raise SystemExit('ERROR: invalid/oversized workload ZIP')
    temp=Path(tempfile.mkdtemp(prefix='relay-workload-'))
    try:
        with zipfile.ZipFile(src) as z:
            top=set(); total=0
            for i in z.infolist():
                if not safe(i.filename) or stat.S_ISLNK(i.external_attr>>16): raise SystemExit('ERROR: unsafe ZIP entry')
                top.add(PurePosixPath(i.filename).parts[0]); total+=i.file_size
            if top!={ROOT} or total>500*1024*1024: raise SystemExit('ERROR: invalid workload root/size')
            z.extractall(temp)
        root=temp/ROOT; required=['PACKAGE.json','MANIFEST.json','MISSION.md','authority/REQUIREMENTS.md','scope/IN_SCOPE.md','tasks/WORKMAP.md','completion/COMPLETION_CONTRACT.json','verification/CHECKS.json']
        for r in required:
            if not (root/r).is_file(): raise SystemExit('ERROR: missing '+r)
        man=json.loads((root/'MANIFEST.json').read_text()); listed=man.get('sha256',{})
        actual={str(p.relative_to(root)).replace('\\','/') for p in root.rglob('*') if p.is_file() and p.name!='MANIFEST.json'}
        if set(listed)!=actual: raise SystemExit('ERROR: manifest file set mismatch')
        for rel,d in listed.items():
            if not safe(rel) or sha(root/rel)!=d: raise SystemExit('ERROR: digest mismatch '+rel)
        dest=repo/'project-relay/workload/current'; previous=repo/'project-relay/workload/previous'
        if dest.exists():
            previous.mkdir(parents=True,exist_ok=True); shutil.move(str(dest),str(previous/f'workload-{sha(src)[:12]}'))
        shutil.copytree(root,dest)
        (dest/'ACTIVE_CONTEXT.md').write_text('# Active workload\n\nRead `MISSION.md`, `authority/REQUIREMENTS.md`, `scope/IN_SCOPE.md`, `tasks/WORKMAP.md`, and `completion/COMPLETION_CONTRACT.json`.\n',encoding='utf-8')
        print('RELAY_WORKLOAD_INGESTED_VISIBLE')
        print('entry=project-relay/workload/current/ACTIVE_CONTEXT.md')
    finally: shutil.rmtree(temp,ignore_errors=True)
if __name__=='__main__': raise SystemExit(main())
