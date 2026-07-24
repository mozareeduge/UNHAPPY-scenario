#!/usr/bin/env python3
"""Run a check with process cleanup, full on-disk logs, bounded output, and failure clustering."""
from __future__ import annotations
# 
import argparse, datetime as dt, json, os, re, signal, subprocess, time
from collections import Counter
from pathlib import Path

def slug(v): return re.sub(r"[^A-Za-z0-9._-]+","-",v.strip()).strip("-") or "check"
def normalize(line):
    line=re.sub(r"\b\d+(?:\.\d+)?(?:ms|s)?\b","<n>",line)
    line=re.sub(r"0x[0-9a-fA-F]+","<hex>",line)
    line=re.sub(r"[/\\][^\s:]+(?:[/\\][^\s:]+)+","<path>",line)
    return line.strip()[:300]

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--name",required=True); ap.add_argument("--timeout",type=int,default=900); ap.add_argument("--success-lines",type=int,default=12); ap.add_argument("--failure-lines",type=int,default=80); ap.add_argument("command",nargs=argparse.REMAINDER); args=ap.parse_args()
    cmd=args.command[1:] if args.command[:1]==["--"] else args.command
    if not cmd: ap.error("command required after --")
    root=Path.cwd(); logs=root/"project-relay/run/logs"; logs.mkdir(parents=True,exist_ok=True); stamp=dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ"); stem=f"{stamp}-{slug(args.name)}"; log=logs/f"{stem}.log"; summary=logs/f"{stem}.json"; start=time.monotonic(); timed=False
    kwargs={"cwd":root,"text":True,"stdout":subprocess.PIPE,"stderr":subprocess.STDOUT,"env":os.environ.copy()}
    if os.name!="nt": kwargs["start_new_session"]=True
    proc=subprocess.Popen(cmd,**kwargs)
    try: output,_=proc.communicate(timeout=args.timeout); code=proc.returncode
    except (subprocess.TimeoutExpired,KeyboardInterrupt):
        timed=True
        try:
            if os.name!="nt": os.killpg(proc.pid,signal.SIGTERM)
            else: proc.terminate()
            output,_=proc.communicate(timeout=5)
        except Exception:
            try:
                if os.name!="nt": os.killpg(proc.pid,signal.SIGKILL)
                else: proc.kill()
            except Exception: pass
            output,_=proc.communicate()
        code=124
    output=output or ""; duration=round(time.monotonic()-start,3); log.write_text(output,encoding="utf-8",errors="replace"); lines=[x for x in output.splitlines() if x.strip()]
    clusters=Counter(normalize(x) for x in lines if re.search(r"error|fail|exception|timeout|assert",x,re.I)); top=[{"pattern":k,"count":v} for k,v in clusters.most_common(8)]
    status="PASS" if code==0 else ("TIMEOUT" if timed else "FAIL"); data={"schema_version":"1.0.0","name":args.name,"command":cmd,"status":status,"exit":code,"duration_seconds":duration,"timeout_seconds":args.timeout,"log":str(log.relative_to(root)),"clusters":top}; summary.write_text(json.dumps(data,indent=2)+"\n",encoding="utf-8")
    print(f"CHECK {status}: {args.name}"); print(f"exit={code} duration={duration}s log={log.relative_to(root)} summary={summary.relative_to(root)}")
    if top and code!=0:
        print("--- failure clusters ---"); [print(f"{x['count']}x {x['pattern']}") for x in top]
    limit=args.success_lines if code==0 else args.failure_lines
    if lines: print("--- bounded tail ---"); print("\n".join(lines[-limit:]))
    return code
if __name__=="__main__": raise SystemExit(main())
