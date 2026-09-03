#!/usr/bin/env python3
"""
spec_from_paper.py — rebuild an exam spec JSON from a rendered paper (one-way undo).

Used after a generator run clobbered hand-authored specs: the built markdown already holds every stem,
its four options and the answer letter, so the spec can be rebuilt faithfully.

    python3 tools/spec_from_paper.py build/exam-<class>__<term>__<stem>.md data/exams/<stem>.json
"""
import re, json, sys
from pathlib import Path

p, out = Path(sys.argv[1]), Path(sys.argv[2])
t = p.read_text(encoding="utf-8")
title = re.search(r"(?im)^#\s*EXAMINATION PRACTICE\s+—\s+(.+?)\s*\(", t)
subject = title.group(1).strip().title() if title else p.stem.split("__")[-1].replace("-", " ").title()

keysec = re.search(r"\*\*Section A:\*\*(.*?)(?:\n\n|\Z)", t, re.S)
keys = [m.group(1) for m in re.finditer(r"\d+\.\s*\[?([A-D])\]?", keysec.group(1))] if keysec else []

guide = t.split("marking guide)**")[-1]
points = {}
for m in re.finditer(r"(?m)^(\d+)\.\s*(.*)$", guide):
    pts = [x.strip() for x in m.group(2).split(";") if x.strip() and x.strip() != "—"]
    points[int(m.group(1))] = pts


def items(block, start):
    """(number, stem) for a section's question lines"""
    return [(int(n), re.sub(r"\s+", " ", s).strip())
            for n, s in re.findall(r"(?m)^(\d+)\.\s+(.+?)\s*(?:\(\s*\d+\s+marks?\s*\))?\s*$", block)
            if int(n) >= start]


head = t.split("## Section A")[1].split("## Section B")[0]
raw = re.findall(r"(?m)^(\d+)\.\s+(.+?)\n((?:\s+[A-D]\)\s.*\n?)+)", head)
obj = []
for n, stem, opts in raw:
    n = int(n)
    pairs = re.findall(r"([A-D])\)\s*(.+)", opts)
    if n - 1 >= len(keys) or len(pairs) != 4:
        continue
    ans_letter = keys[n - 1]
    d = dict(pairs)
    obj.append({"stem": re.sub(r"\s+", " ", stem).strip(), "answer": d[ans_letter].strip(),
                "distractors": [d[L].strip() for L in "ABCD" if L != ans_letter]})

rest = t.split("## Section B")[1]
b_txt, c_txt = rest.split("## Section C")
b_txt = re.split(r"(?m)^###\s", b_txt)[0]        # stop at "### Teacher's key"
c_txt = re.split(r"(?m)^(?:###\s|\*\*Sections)", c_txt)[0]
sub = [{"stem": s, "points": points.get(n, [])} for n, s in items(b_txt, 31)]
theory = [{"stem": s, "marks": 2, "points": points.get(n, [])} for n, s in items(c_txt, 41)]

spec = {"subject": subject, "objective": obj, "subobjective": sub, "theory": theory}
out.write_text(json.dumps(spec, indent=1, ensure_ascii=False), encoding="utf-8")
print(f"{out.name}: objective={len(obj)} subobjective={len(sub)} theory={len(theory)}")
