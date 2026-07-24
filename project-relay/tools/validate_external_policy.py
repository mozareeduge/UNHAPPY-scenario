#!/usr/bin/env python3
from __future__ import annotations
# 
import argparse, json, re
from pathlib import Path

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('policy'); args=ap.parse_args()
    p=Path(args.policy); d=json.loads(p.read_text(encoding='utf-8'))
    errors=[]
    if d.get('schema_version')!='1.0.0': errors.append('schema_version')
    systems=d.get('systems')
    if not isinstance(systems,list) or not systems: errors.append('systems')
    else:
        for s in systems:
            if s.get('kind')=='cloudflare-api-mcp':
                if s.get('endpoint')!='https://mcp.cloudflare.com/mcp': errors.append('endpoint')
                if s.get('require_snapshot') is not True: errors.append('snapshot')
                for x in s.get('allowed_read',[]): re.compile(x['path_regex'])
                for x in s.get('allowed_mutations',[]):
                    re.compile(x['path_regex'])
                    if not x.get('id') or not x.get('methods') or x.get('reversible') not in (True,False): errors.append('mutation')
                for x in s.get('forbidden_path_regex',[]): re.compile(x)
    if errors:
        print('EXTERNAL_POLICY_INVALID',','.join(errors)); return 1
    print('EXTERNAL_POLICY_VALID'); return 0
if __name__=='__main__': raise SystemExit(main())
