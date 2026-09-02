#!/usr/bin/env python3
"""Check the authoring sheets for a class-term: section sizes and item shape.

    python3 tools/sheet_check.py --class "Nursery 2" --term "2nd Term"

An objective line must read  stem || correct || trap || trap || trap  (five fields).
A sub-objective line must read  stem :: ans | ans  (two or more answers).
A theory line must read  stem || marks.
"""
import argparse, glob, re, sys

def parse(path):
    text = open(path, encoding="utf-8").read()
    meta = dict(re.findall(r"(?m)^([a-z]+):\s*(.*)$", text.split("\n[objective]")[0]))
    def block(name, nxt):
        seg = text.split(f"\n[{name}]\n")
        if len(seg) < 2:
            return []
        body = seg[1].split(f"\n\n[{nxt}]")[0] if nxt else seg[1]
        return [l for l in body.splitlines() if l.strip()]
    return meta, block("objective", "subobjective"), block("subobjective", "theory"), block("theory", "")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--class", dest="cls", required=True)
    ap.add_argument("--term", required=True)
    a = ap.parse_args()
    slug = lambda s: re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")
    files = sorted(glob.glob(f"data/exams/src/{slug(a.cls)}__{slug(a.term)}__*.txt"))
    problems = []
    for f in files:
        name = f.split("__")[-1][:-4]
        meta, obj, sub, th = parse(f)
        if len(obj) != 30: problems.append(f"{name}: objective has {len(obj)} items, needs 30")
        if len(sub) != 10: problems.append(f"{name}: sub-objective has {len(sub)} items, needs 10")
        if len(th) != 5: problems.append(f"{name}: theory has {len(th)} items, needs 5")
        for i, l in enumerate(obj, 1):
            if l.count("||") != 4:
                problems.append(f"{name} obj{i}: needs 5 fields separated by || (found {l.count('||')+1})")
            elif not re.search(r"___|__\s*\|\||\?|\.$|,", l.split("||")[0]):
                problems.append(f"{name} obj{i}: stem has no blank or question mark")
        for i, l in enumerate(sub, 1):
            if "::" not in l: problems.append(f"{name} sub{i}: no '::' between question and answers")
            elif len(l.split("::")[1].split("|")) < 2: problems.append(f"{name} sub{i}: needs two answers or more")
        for i, l in enumerate(th, 1):
            if l.count("||") != 1: problems.append(f"{name} theory{i}: needs 'stem || marks'")
        want = {"subject": True}
        for k in ("class", "term"):
            if not meta.get(k): problems.append(f"{name}: no {k}: line")
        print(f"{name:34s} {len(obj):2d}/{len(sub):2d}/{len(th):2d}  "
              f"subject={meta.get('subject','?')[:34]:34s} stream={meta.get('stream','-')}")
    print(f"\nsheets: {len(files)}")
    if problems:
        print(f"\nPROBLEMS ({len(problems)}):")
        for p in problems: print("   -", p)
        sys.exit(1)
    print("all sheets: 30/10/5, every item well formed")

main()
