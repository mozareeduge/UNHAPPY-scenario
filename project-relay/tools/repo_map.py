#!/usr/bin/env python3
"""Create a bounded deterministic repository map without model calls or dependency installation."""
from __future__ import annotations
# 
import argparse, ast, json, os, re, subprocess
from collections import Counter, defaultdict
from pathlib import Path

EXCLUDED = {".git", ".claude", "node_modules", ".venv", "venv", "dist", "build", "coverage", "target"}
MAX_FILES = 8000

def tracked(repo: Path) -> list[str]:
    try:
        r = subprocess.run(["git", "-C", str(repo), "ls-files", "-co", "--exclude-standard"], text=True, capture_output=True, timeout=20)
        if r.returncode == 0: return [x for x in r.stdout.splitlines() if x][:MAX_FILES]
    except Exception: pass
    result=[]
    for current, dirs, names in os.walk(repo):
        dirs[:] = [d for d in dirs if d not in EXCLUDED]
        for name in names:
            p=Path(current)/name; result.append(str(p.relative_to(repo)).replace("\\","/"))
            if len(result)>=MAX_FILES: return result
    return result

def symbols(path: Path) -> list[str]:
    try: text=path.read_text(encoding="utf-8", errors="ignore")
    except Exception: return []
    if path.suffix==".py":
        try:
            tree=ast.parse(text); return [n.name for n in ast.walk(tree) if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef,ast.ClassDef))][:100]
        except Exception: return []
    if path.suffix in {".js",".jsx",".ts",".tsx"}:
        pat=re.compile(r"(?:export\s+)?(?:async\s+)?(?:function|class)\s+([A-Za-z_$][\w$]*)|(?:export\s+)?(?:const|let)\s+([A-Za-z_$][\w$]*)\s*=")
        return [a or b for a,b in pat.findall(text)][:100]
    return []

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--repo",default="."); ap.add_argument("--task",default=""); args=ap.parse_args()
    repo=Path(args.repo).resolve(); files=tracked(repo)
    ext=Counter(Path(x).suffix.lower() or "<none>" for x in files); dirs=Counter((Path(x).parts[0] if len(Path(x).parts)>1 else ".") for x in files)
    manifests=[x for x in files if Path(x).name in {"package.json","pyproject.toml","requirements.txt","Cargo.toml","go.mod","pom.xml","build.gradle","Makefile","Dockerfile"}]
    tests=[x for x in files if re.search(r"(^|/)(tests?|__tests__)(/|$)|(?:test|spec)\.[^.]+$",x,re.I)]
    configs=[x for x in files if x.startswith(".github/workflows/") or Path(x).name in {"playwright.config.ts","playwright.config.js","vite.config.ts","vite.config.js","tsconfig.json"}]
    symbol_map={}
    candidates=[x for x in files if Path(x).suffix in {".py",".js",".jsx",".ts",".tsx"}]
    task_terms={t.lower() for t in re.findall(r"[A-Za-z0-9_-]{3,}",args.task)}
    if task_terms:
        candidates.sort(key=lambda x: -sum(term in x.lower() for term in task_terms))
    for rel in candidates[:300]:
        vals=symbols(repo/rel)
        if vals: symbol_map[rel]=vals
    try:
        git=subprocess.run(["git","-C",str(repo),"log","-5","--pretty=%h %s"],text=True,capture_output=True,timeout=10).stdout.splitlines()
    except Exception: git=[]
    data={"schema_version":"1.0.0","file_count":len(files),"truncated":len(files)>=MAX_FILES,"extensions":ext.most_common(30),"top_directories":dirs.most_common(30),"manifests":manifests[:100],"tests":tests[:300],"configs":configs[:100],"symbols":symbol_map,"recent_commits":git,"task_hint":args.task}
    run=repo/"project-relay/run"; run.mkdir(parents=True,exist_ok=True)
    (run/"REPO_MAP.json").write_text(json.dumps(data,indent=2)+"\n",encoding="utf-8")
    lines=["# Bounded repository map",f"- Files: {len(files)}{' (truncated)' if data['truncated'] else ''}",f"- Manifests: {', '.join(manifests[:12]) or 'none'}",f"- Tests: {len(tests)}",f"- Config/workflows: {len(configs)}","","## Top directories"]
    lines += [f"- {k}: {v}" for k,v in dirs.most_common(20)]
    lines += ["","## Symbol-bearing files"]+[f"- {k}: {', '.join(v[:12])}" for k,v in list(symbol_map.items())[:60]]
    (run/"REPO_MAP.md").write_text("\n".join(lines[:180])+"\n",encoding="utf-8")
    print(f"RELAY_REPO_MAP files={len(files)} symbols={len(symbol_map)} path=project-relay/run/REPO_MAP.md")
    return 0
if __name__=="__main__": raise SystemExit(main())
