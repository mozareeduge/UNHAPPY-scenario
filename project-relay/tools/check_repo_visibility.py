#!/usr/bin/env python3
from pathlib import Path
import argparse, subprocess, sys
PROHIBITED=['.claude/','CLAUDE.local.md']
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--repo',default='.'); args=ap.parse_args(); repo=Path(args.repo).resolve()
    bad=[]
    for p in repo.rglob('*'):
        if '.git' in p.parts: continue
        rel=str(p.relative_to(repo)).replace('\\','/')
        if any(rel==x.rstrip('/') or rel.startswith(x) for x in PROHIBITED): bad.append(rel)
    exclude=repo/'.git/info/exclude'
    if exclude.is_file() and 'Project Relay' in exclude.read_text(encoding='utf-8',errors='ignore'): bad.append('.git/info/exclude modified by Relay')
    if bad:
        print('VISIBLE_SETUP_FAIL'); [print('-',x) for x in sorted(set(bad))]; return 1
    r=subprocess.run(['git','-C',str(repo),'status','--short','--untracked-files=all'],text=True,capture_output=True)
    print('VISIBLE_SETUP_PASS')
    print(r.stdout.strip())
    return 0
if __name__=='__main__': raise SystemExit(main())
