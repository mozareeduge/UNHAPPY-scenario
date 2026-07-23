#!/usr/bin/env python3
"""Compute a stable path/content fingerprint for material project state."""
from __future__ import annotations
# 
import argparse, datetime as dt, fnmatch, hashlib, json, os, subprocess
from pathlib import Path, PurePosixPath

def safe(value:str)->bool:
    p=PurePosixPath(value); return bool(value) and not p.is_absolute() and ".." not in p.parts and "\\" not in value

def files_for(repo:Path, patterns:list[str], excludes:list[str])->list[Path]:
    all_files=[]
    try:
        r=subprocess.run(["git","-C",str(repo),"ls-files","-co","--exclude-standard"],text=True,capture_output=True,timeout=30)
        names=r.stdout.splitlines() if r.returncode==0 else []
    except Exception: names=[]
    if not names:
        for current,dirs,files in os.walk(repo):
            dirs[:]=[d for d in dirs if d not in {".git","node_modules",".venv","venv"}]
            names += [str((Path(current)/f).relative_to(repo)).replace("\\","/") for f in files]
    for name in names:
        if any(fnmatch.fnmatch(name,e) or name.startswith(e.rstrip("/")+"/") for e in excludes): continue
        if any(fnmatch.fnmatch(name,p) or name==p or name.startswith(p.rstrip("/")+"/") for p in patterns):
            p=repo/name
            if p.is_file() and not p.is_symlink(): all_files.append(p)
    return sorted(set(all_files),key=lambda p:str(p.relative_to(repo)))

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--repo",default="."); ap.add_argument("--config",default="project-relay/workload/current/operations/CANDIDATE_IDENTITY.json"); args=ap.parse_args()
    repo=Path(args.repo).resolve(); cfg=repo/args.config
    data=json.loads(cfg.read_text(encoding="utf-8")); patterns=data.get("material_paths",[]); excludes=data.get("exclude_patterns",[])+data.get("state_only_paths",[])
    for value in patterns+excludes:
        if not isinstance(value,str) or not safe(value): raise SystemExit(f"ERROR: unsafe fingerprint path {value}")
    paths=files_for(repo,patterns,excludes)
    if not paths: raise SystemExit("ERROR: candidate identity matched no material files")
    h=hashlib.sha256(); manifest=[]
    for p in paths:
        rel=str(p.relative_to(repo)).replace("\\","/"); content=hashlib.sha256(p.read_bytes()).hexdigest(); manifest.append({"path":rel,"sha256":content,"bytes":p.stat().st_size}); h.update(rel.encode()+b"\0"+content.encode()+b"\n")
    try: head=subprocess.run(["git","-C",str(repo),"rev-parse","HEAD"],text=True,capture_output=True,timeout=10).stdout.strip() or None
    except Exception: head=None
    out={"schema_version":"1.0.0","generated_at":dt.datetime.now(dt.timezone.utc).isoformat(),"algorithm":"sha256-path-content-v1","fingerprint":h.hexdigest(),"git_head_context":head,"file_count":len(paths),"files":manifest}
    target=repo/"project-relay/run/CANDIDATE.json"; target.parent.mkdir(parents=True,exist_ok=True); target.write_text(json.dumps(out,indent=2)+"\n",encoding="utf-8")
    print(f"RELAY_CANDIDATE fingerprint={out['fingerprint']} files={len(paths)} path={target.relative_to(repo)}")
    return 0
if __name__=="__main__": raise SystemExit(main())
