#!/usr/bin/env python3
"""
term_pack.py — print/author the full teaching pack for one class-term.

This is the input a human (or the model) writes lesson notes from: for every teaching
week of one class in one term it shows the school's own topic row, the resolved NERDC
depth (what must be covered) and the NERDC method columns (how the lesson is run),
plus the calendar/blank weeks that must NOT get a note.

Usage:
    python3 tools/term_pack.py --class "Nursery 2" --term "1st Term" [--subject "Basic Science"]
    python3 tools/term_pack.py --class "Nursery 2" --term "1st Term" --out reports/pack.md
"""
import json, re, argparse, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "data/note_sources.json"
MASTER = ROOT / "data/curriculum_master.json"
TERM_ALIAS = {"1st Term": ("1st Term", "First Term"), "2nd Term": ("2nd Term", "Second Term"),
              "3rd Term": ("3rd Term", "Third Term")}
STOP = set("the a an of and or to in for on with by as is are be into from that this our we you".split())


def lines_of(blocks, cap=10_000):
    out, seen = [], set()
    for blk in blocks:
        txt = re.sub(r"^\s*[\-\u2022]\s*", "", str(blk.get("text", ""))).strip()
        txt = re.sub(r"(?i)\b(day\s+\d+)\s+-\s+", r"\1 ~D~ ", txt)
        for ln in re.split(r"\n|\s*[\u2022\u2023]\s*|\s+-\s+|\s+(?=-[A-Z])|;\s+|\.\s+(?=[A-Z])", txt):
            ln = ln.replace(" ~D~ ", " - ")
            ln = re.sub(r"^\s*[\-\u2022\d.]+\s*", "", str(ln)).strip()
            ln = re.sub(r"\s+", " ", ln)
            ln = ln.replace("@DOT@", ".")
            if len(ln) < 5 or ln.lower() in STOP:
                continue
            k = re.sub(r"[^a-z0-9]", "", ln.lower())[:70]
            if k in seen:
                continue
            seen.add(k)
            out.append(ln)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--class", dest="cls", required=True)
    ap.add_argument("--term", required=True)
    ap.add_argument("--subject")
    ap.add_argument("--out")
    a = ap.parse_args()
    terms = TERM_ALIAS.get(a.term, (a.term, a.term))

    data = json.loads(SRC.read_text(encoding="utf-8"))
    recs = [r for r in data["records"]
            if r["class"] == a.cls and any(t.lower() in str(r["term"]).lower() for t in terms)
            and (not a.subject or r["subject"] == a.subject)]
    if not recs:
        sys.exit(f"no records for {a.cls} / {a.term}"
                 + (f" / {a.subject}" if a.subject else "")
                 + f"\n  terms present for this class: "
                 + ", ".join(sorted({r['term'] for r in data['records'] if r['class'] == a.cls})))

    L = [f"# Teaching pack — {a.cls} · {a.term}", "",
         f"{len(recs)} teaching weeks. Calendar weeks are listed at the end and get no note.", ""]
    cur = None
    n = 0
    for r in recs:
        key = (r["subject"], r.get("stream"))
        if key != cur:
            cur = key
            L.append("\n" + "=" * 78)
            L.append(f"SUBJECT: {r['subject']}" + (f"  ·  STREAM: {r['stream']}" if r.get("stream") else ""))
            L.append("=" * 78)
        n += 1
        L.append(f"\n## wk{r['week']} · {r['topic']}")
        if r.get("explicit_source_note"):
            L.append(f"school pointer: {r['explicit_source_note']}")
        for w in r["nerdc_weeks"]:
            L.append(f"  anchor: NERDC {w['class']} · {w['subject']} · {w['term']} wk{w['week']}"
                     f" '{w['topic']}' (pp {w['pages']}) via {w['via']} off{w['band_offset']:+d}")
        content = lines_of(r["depth_text"])
        method = lines_of(r.get("method_text", []))
        if content:
            L.append("  MUST COVER (depth floor):")
            L += [f"    - {c}" for c in content]
        else:
            L.append("  MUST COVER: (no NERDC depth — school-generated or gap row)")
        if method:
            L.append("  METHOD (NERDC activities/materials, use for the procedure):")
            L += [f"    · {m}" for m in method[:14]]
    m = json.loads(MASTER.read_text(encoding="utf-8"))
    cal = []
    for s in m["subjects"]:
        cn = next((c for c in s["classes"] if c["class"] == a.cls), None)
        if not cn:
            continue
        if cn.get("by_term"):
            for term, rr in cn["by_term"].items():
                if not any(t.lower() in term.lower() for t in terms):
                    continue
                for r in rr:
                    if r["kind"] != "topic":
                        cal.append(f"  {s['name']}: wk{r['week']} [{r['kind']}] {r['topic'][:40]}")
    L += ["", "\n## Calendar / blank weeks in this class-term (NO notes)", f"{len(cal)} rows",
          ] + cal[:80]
    L.append(f"\n**total teaching weeks in this pack: {n}**")
    text = "\n".join(L) + "\n"
    if a.out:
        (ROOT / a.out).write_text(text, encoding="utf-8")
        print(f"wrote {a.out} ({len(text):,} chars, {n} teaching weeks)")
    else:
        print(text)


if __name__ == "__main__":
    main()
