#!/usr/bin/env python3
"""patch_lines.py — replace numbered items in a sheet's [objective] block.  usage:
   python3 tools/patch_lines.py <sheet-name> <<'JSON'  {"3": "stem || ans || t1 || t2 || t3", ...}  JSON
"""
import sys, json, re
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
name = sys.argv[1]
fix = {int(k): v for k, v in json.loads(sys.stdin.read()).items()}
p = ROOT / "data/exams/src" / f"{name}.txt"
lines = p.read_text(encoding="utf-8").splitlines()
out, i, sect, n = [], 0, None, 0
for ln in lines:
    s = ln.strip()
    if s.startswith("["):
        sect = s.strip("[]").lower()
        n = 0
    elif sect == "objective" and s and not s.startswith("#") and "||" in s:
        n += 1
        if n in fix:
            out.append(fix[n]); continue
    out.append(ln)
p.write_text("\n".join(out) + "\n", encoding="utf-8")
print(f"{name}: patched {len(fix)} item(s)")
