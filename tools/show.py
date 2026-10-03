#!/usr/bin/env python3
"""show.py — print one record of data/note_sources.json:  python3 tools/show.py "<subject>" "<class>" <week> [term]"""
import json, re, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
subj, cls, week = sys.argv[1], sys.argv[2], int(sys.argv[3])
term = (sys.argv[4] if len(sys.argv) > 4 else "2nd Term").lower()
WS = re.compile(r"\s+")
d = json.loads((ROOT / "data/note_sources.json").read_text(encoding="utf-8"))
hit = 0
for r in d["records"]:
    if subj.lower() in r["subject"].lower() and r["class"] == cls and term in str(r["term"]).lower() \
       and r["week"] == week:
        hit += 1
        print("=" * 76)
        print(r["subject"], "|", r.get("stream"), "| wk", r["week"], "|", r["topic"])
        print("mode:", r.get("mode"), "| confidence:", r.get("confidence"), "|", r.get("explicit_source_note") or "")
        for s in r.get("school_depth") or []:
            print("  SCHOOL:", re.sub(r"\s+", " ", str(s))[:400])
        for w in r["nerdc_weeks"]:
            print(f"  anchor: {w['class']} · {w['subject']} · {w['term']} wk{w['week']} · {w['topic'][:56]} "
                  f"(pp {w.get('pages')}) via {w.get('via')} off{w.get('band_offset', 0):+} score {w.get('score')}")
        for b in r["depth_text"]:
            print("  MUST COVER (from", b["from"] + "):")
            for ln in re.split(r"\n|\s+-\s+", WS.sub(" ", b["text"])):
                ln = ln.strip(" -•")
                if len(ln) > 3:
                    print("     -", ln[:200])
        for b in r.get("method_text", []):
            print("  METHOD (from", b["from"] + "):", WS.sub(" ", b["text"])[:600])
if not hit:
    print("no record for", subj, cls, week, term)
