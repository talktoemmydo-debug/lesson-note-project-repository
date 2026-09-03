#!/usr/bin/env python3
"""sheet_lint.py — report exam-sheet lines whose correct option is much longer than its traps.

"Pick the longest" should not answer a paper. Run this on data/exams/src/*.txt after writing a sheet:
    python3 tools/sheet_lint.py nursery-2__1st-term__yoruba [...]     (no name = all sheets)
Exit code 1 if any line is off, so it can gate a build.
"""
import sys, re
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "data/exams/src"

def main():
    names = sys.argv[1:]
    files = [SRC / f"{n}.txt" for n in names] if names else sorted(SRC.glob("*.txt"))
    total = 0
    for f in files:
        bad, inobj, i = [], False, 0
        for ln in f.read_text(encoding="utf-8").splitlines():
            s = ln.strip()
            if s.startswith("["):
                inobj = s.lower() == "[objective]"
                continue
            if not inobj or not s or s.startswith("#") or "||" not in s:
                continue
            i += 1
            parts = [re.sub(r"\s+", " ", x).strip() for x in s.split("||")]
            if len(parts) < 5:
                continue
            ans, traps = parts[1], parts[2:5]
            mx = max((len(t) for t in traps), default=0)
            if len(ans) > mx * 1.3 and len(ans) - mx > 8:
                bad.append((i, len(ans) - mx, ans[:44], traps))
        total += len(bad)
        if bad:
            print(f"\n{f.name}: {len(bad)} item(s) where the right answer is the long one")
            for n, gap, a, t in bad:
                print(f"   L{n} +{gap:3d}  right: {a!r}\n          traps: {[x[:34] for x in t]}")
    print(f"\nlines to re-balance: {total}")
    sys.exit(1 if total else 0)

if __name__ == "__main__":
    main()
