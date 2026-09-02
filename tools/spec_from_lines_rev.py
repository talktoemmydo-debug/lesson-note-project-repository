#!/usr/bin/env python3
"""spec_from_lines_rev.py — print an existing spec back as a hand-editable sheet (data/exams/src/<name>.txt)."""
import json, sys, re
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
for f in sys.argv[1:]:
    sp = json.loads(Path(f).read_text(encoding="utf-8"))
    name = Path(f).stem
    L = [f"# {sp.get('subject','')} — term paper (converted from the spec; edit here and re-run spec_from_lines.py)",
         f"subject: {re.sub(r'·.*$','',sp.get('subject','')).strip()}",
         f"class: {sp.get('class','')}", f"term: {sp.get('term','')}"]
    if "·" in sp.get("subject",""):
        L.append(f"stream: {sp['subject'].split('·',1)[1].strip()}")
    L += ["", "[objective]"]
    for q in sp["objective"]:
        L.append(" || ".join([q["stem"], q["answer"]] + list(q["distractors"])))
    L += ["", "[subobjective]"]
    for q in sp["subobjective"]:
        pts = " | ".join(q.get("points") or [])
        L.append(q["stem"] + (f" :: {pts}" if pts else ""))
    L += ["", "[theory]"]
    for q in sp["theory"]:
        pts = " | ".join(q.get("points") or [])
        L.append(q["stem"] + f" || {q.get('marks',2)}" + (f" :: {pts}" if pts else ""))
    out = ROOT / "data/exams/src" / f"{name}.txt"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(L) + "\n", encoding="utf-8")
    print("sheet:", out.relative_to(ROOT), len(sp["objective"]), len(sp["subobjective"]), len(sp["theory"]))
