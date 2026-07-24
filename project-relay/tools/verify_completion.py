#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, subprocess
from pathlib import Path
from hashutil import file_sha256

def load(p,d): return json.loads(p.read_text(encoding='utf-8')) if p.is_file() else d

def fp(repo):
    r=subprocess.run(['python',str(repo/'project-relay/tools/compute_candidate_fingerprint.py'),'--repo',str(repo)],text=True,capture_output=True,timeout=120)
    if r.returncode: return None
    return load(repo/'project-relay/run/CANDIDATE.json',{}).get('fingerprint')

def valid(repo,p,cid,current):
    rec=load(p,{})
    given=rec.pop('record_sha256',None); actual=hashlib.sha256(json.dumps(rec,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    if given!=actual or rec.get('result')!='PASS' or rec.get('check_id')!=cid: return False
    if rec.get('candidate_before')!=current or rec.get('candidate_after')!=current: return False
    log=rec.get('log',{}); lp=repo/str(log.get('path',''))
    return lp.is_file() and file_sha256(lp)==log.get('sha256')

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--repo',default='.'); args=ap.parse_args(); repo=Path(args.repo).resolve()
    work=repo/'project-relay/workload/current'; contract=load(work/'completion/COMPLETION_CONTRACT.json',{}); current=fp(repo); errors=[]
    if not current: errors.append('candidate fingerprint unavailable')
    for cid in contract.get('required_check_ids',[]):
        folder=repo/'project-relay/run/evidence'/cid; ok=any(valid(repo,p,cid,current) for p in sorted(folder.glob('*.evidence.json'),reverse=True)) if folder.is_dir() else False
        if not ok: errors.append('no current PASS evidence: '+cid)
    manual=contract.get('required_manual_checkpoint_ids',[])
    confirmations=load(repo/'project-relay/run/MANUAL_CONFIRMATIONS.json',{}).get('confirmed',[])
    for mid in manual:
        if mid not in confirmations: errors.append('manual checkpoint pending: '+mid)
    findings=load(repo/'project-relay/run/FINDINGS.json',{'findings':[]})
    blocking=set(contract.get('blocking_finding_levels',['critical','high']))
    for f in findings.get('findings',[]):
        if f.get('status','open')=='open' and f.get('severity') in blocking: errors.append('open blocking finding: '+str(f.get('id')))
    if errors:
        print('RELAY_COMPLETION_NOT_READY'); [print('-',e) for e in errors]; return 1
    print(f'RELAY_COMPLETION_READY fingerprint={current}')
    return 0
if __name__=='__main__': raise SystemExit(main())
