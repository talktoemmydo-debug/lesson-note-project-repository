#!/usr/bin/env python3
"""check_worksheets.py — do the notes' own worksheets hide a pattern in the answer letter?

The notes carry no answer key (the pupil book must not), so the correct option is inferred: it is the
only option whose words appear in the teaching part of the same note. Items where more than one option
(or none) is found are skipped as unknown. Reported per subject and for the term, so a class where
every answer is "A" is caught before printing.

    python3 tools/check_worksheets.py --class "Nursery 2" --term "1st Term"
"""
import re, sys, argparse, collections
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "notes/src"
L = "ABCD"

def slug(s): return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")
def key(s): return re.sub(r"[^a-z0-9]", "", re.sub(r"\*", "", s.lower()))

def opts_of(line):
    if len(re.findall(r"\(?[A-D]\)", line)) == 4:
        return [re.sub(r"\s+", " ", x).strip() for x in re.split(r"\(?[A-D]\)", line)[1:]]
    return None

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--class", dest="cls", required=True)
    ap.add_argument("--term", required=True)
    ap.add_argument("--verbose", action="store_true")
    a = ap.parse_args()
    d = SRC / f"{slug(a.cls)}__{slug(a.term)}"
    allk, unknown = [], 0
    for p in sorted(x for x in d.glob("*.md") if not x.name.startswith("_")):
        t = p.read_text(encoding="utf-8")
        ks = []
        for blk in re.split(r"(?=^###\s+WEEK)", t, flags=re.M)[1:]:
            wk = re.match(r"###\s+WEEK\s+(\d+)", blk).group(1)
            teach = key(blk.split("**Worksheet**")[0])
            ws = blk.split("**Worksheet**", 1)[1].split("**My own work**")[0] if "**Worksheet**" in blk else ""
            for ln in ws.splitlines():
                m = re.match(r"^\s*[1-4]\.\s+(.*)$", ln)
                if not m:
                    continue
                o = opts_of(m.group(1))
                if not o:
                    continue
                hits = [i for i, x in enumerate(o) if len(key(x)) >= 3 and key(x) in teach]
                if len(hits) == 1:
                    ks.append(L[hits[0]])
                else:
                    unknown += 1
                    if a.verbose:
                        print(f"   ? {p.stem} wk{wk}: {[x[:18] for x in o]}")
        dist = collections.Counter(ks)
        allk += ks
        run = sum(1 for i in range(len(ks) - 1) if ks[i] == ks[i + 1])
        print(f"{p.stem:36s} n={len(ks):2d} " +
              " ".join(f"{l}={dist.get(l,0)}" for l in L) + f"  adj-repeat={run}")
    dist = collections.Counter(allk)
    print(f"\nterm total: n={len(allk)} " + " ".join(f"{l}={dist.get(l,0)}" for l in L) +
          f" | unknown/skipped={unknown}")
    longest = max((len(list(g)) for _, g in itertools.groupby(allk)), default=0)
    print(f"longest run of one letter: {longest}")

import itertools
if __name__ == "__main__":
    main()
