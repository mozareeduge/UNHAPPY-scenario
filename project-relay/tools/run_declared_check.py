#!/usr/bin/env python3
from __future__ import annotations
import argparse, datetime as dt, hashlib, json, subprocess
from pathlib import Path
from hashutil import file_sha256, atomic_json

def load(p,d): return json.loads(p.read_text(encoding='utf-8')) if p.is_file() else d

def fingerprint(repo):
    tool=repo/'project-relay/tools/compute_candidate_fingerprint.py'
    r=subprocess.run(['python',str(tool),'--repo',str(repo)],text=True,capture_output=True,timeout=120)
    if r.returncode: raise SystemExit(r.stderr or r.stdout)
    return load(repo/'project-relay/run/CANDIDATE.json',{}).get('fingerprint')

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('check_id'); ap.add_argument('--repo',default='.'); args=ap.parse_args(); repo=Path(args.repo).resolve()
    cfg=load(repo/'project-relay/workload/current/verification/CHECKS.json',{})
    check=next((x for x in cfg.get('checks',[]) if x.get('id')==args.check_id),None)
    if not check: raise SystemExit('ERROR: unknown check')
    cmd=check.get('command');
    if not isinstance(cmd,list) or not cmd or not all(isinstance(x,str) for x in cmd): raise SystemExit('ERROR: command must be argv array')
    before=fingerprint(repo); started=dt.datetime.now(dt.timezone.utc).isoformat(); stamp=dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    folder=repo/'project-relay/run/evidence'/args.check_id; folder.mkdir(parents=True,exist_ok=True); log=folder/f'{stamp}.log'
    r=subprocess.run(cmd,cwd=repo,text=True,capture_output=True,timeout=int(check.get('timeout_seconds',900)))
    output=(r.stdout or '')+(('\n'+r.stderr) if r.stderr else ''); log.write_text(output,encoding='utf-8',errors='replace')
    after=fingerprint(repo); result='PASS' if r.returncode==0 and before==after else ('INVALID_CANDIDATE_CHANGED' if before!=after else 'FAIL')
    core={'schema_version':'1.0.0','check_id':args.check_id,'result':result,'candidate_before':before,'candidate_after':after,'command':cmd,'exit_code':r.returncode,'started_at':started,'finished_at':dt.datetime.now(dt.timezone.utc).isoformat(),'log':{'path':str(log.relative_to(repo)),'sha256':file_sha256(log),'bytes':log.stat().st_size},'requirements':check.get('requirements',[]),'scenarios':check.get('scenarios',[])}
    core['record_sha256']=hashlib.sha256(json.dumps(core,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    rec=folder/f'{stamp}.evidence.json'; atomic_json(rec,core)
    print(f'RELAY_CHECK_{result} check={args.check_id} evidence={rec.relative_to(repo)}')
    if output.strip(): print('\n'.join(output.splitlines()[-40:]))
    return 0 if result=='PASS' else 1
if __name__=='__main__': raise SystemExit(main())
