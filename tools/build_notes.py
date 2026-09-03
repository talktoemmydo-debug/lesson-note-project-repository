#!/usr/bin/env python3
"""
build_notes.py — lesson-note writer for the Mercy Model Schools corpus.

Input : data/note_sources.json   (master sequence + resolved NERDC depth per week)
        templates/house.md       (the school's note layout; {{PLACEHOLDER}} slots)
Output: notes/<subject-slug>.<class-slug>.<term-slug>.jsonl   one line per note

Design rules
  * Calendar weeks (W7 Mid-Term, W10 Revision, W11 Examination, W12 Closing, and any
    row whose kind is `calendar`/`blank`) NEVER get a note — enforced, not trusted.
  * A note may not go below the depth of its matched NERDC week: every subtopic line
    of the resolved `depth_text` must be represented in the note. This is checked by
    `--audit` (token coverage of the depth lines against the written note).
  * Yoruba and General Knowledge are school-generated: no NERDC anchor exists, so
    their records are marked `mode: school-generated` and the audit skips depth-cover.
  * Notes live in ONE JSONL per subject-class-term (never a file per note) to stay
    inside the workspace budget.

Placeholders available to the template:
  {{SUBJECT}} {{CLASS}} {{STREAM}} {{TERM}} {{WEEK}} {{TOPIC}} {{DATE}}
  {{DEPTH_LINES_BULLETS}}  - resolved NERDC subtopic lines as bullets
  {{NERDC_SOURCES}}        - "subject · class · term wk n (pp x-y)" lines
  {{MODE}} {{CONFIDENCE}}  - nerdc-depth | school-generated | upper-band-redistribution
  {{EXPLICIT_SOURCE}}      - the master's own printed 'Source (NERDC)' note, if any

Usage
  python3 tools/build_notes.py --selftest            # 5 pilot notes, layout = NERDC sample shape
  python3 tools/build_notes.py --subject "Basic Science" --class "Nursery 2" --term "1st Term"
  python3 tools/build_notes.py --all --audit
"""
import json, re, sys, argparse, collections, unicodedata, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "data/note_sources.json"
HOUSE = ROOT / "templates/house.md"
OUTDIR = ROOT / "notes"

TERM_ALIAS = {"1st Term": "First Term", "2nd Term": "Second Term", "3rd Term": "Third Term"}

DEFAULT_TEMPLATE = """# {{SUBJECT}} — {{CLASS}}{{STREAM_SUFFIX}} · {{TERM}} · Week {{WEEK}}

**Topic:** {{TOPIC}}
{{SOURCES_BLOCK}}
## Objectives

{{OBJECTIVES}}
## Teaching & Learning Content

{{DEPTH_BULLETS}}

## Evaluation

{{EVAL}}

## Assignment

{{ASSIGN}}
"""


def slug(s):
    s = re.sub(r"[^A-Za-z0-9 ]", "", str(s)).strip().lower()
    return re.sub(r"\s+", "-", s)[:40] or "x"


def depth_lines(rec):
    """Flatten resolved NERDC depth into ordered subtopic lines (dedup, verbatim)."""
    out, seen = [], set()
    for blk in rec["depth_text"]:
        txt = re.sub(r"^\s*[\-\u2022]\s*", "", blk["text"]).strip()
        # 'Day 1 - Light and darkness' is ONE subtopic: mask that dash before splitting
        txt = re.sub(r"(?i)\b(day\s+\d+)\s+-\s+", r"\1 ~DASH~ ", txt)
        # protect dotted abbreviations so 'a.m. and p.m.' is not split as sentences
        txt = re.sub(r"\b([A-Za-z])\.([A-Za-z])\.", r"\1@DOT@\2@DOT@", txt)
        for ln in re.split(r"\n|\s*[\u2022\u2023]\s*|\s+-\s+|\s+(?=-[A-Z])|;\s+|\.\s+(?=[A-Z])", txt):
            ln = ln.replace("@DOT@", ".")
            ln = ln.replace(" ~DASH~ ", " - ")
            ln = re.sub(r"^\s*[\-\u2022\d.]+\s*", "", str(ln)).strip()
            ln = re.sub(r"\s+", " ", ln)
            if len(ln) < 4:
                continue
            k = re.sub(r"[^a-z0-9]", "", ln.lower())[:70]
            if k in seen:
                continue
            seen.add(k)
            out.append({"column": blk["column"], "from": blk["from"], "line": ln})
    return out


def sources_block(rec):
    if not rec["nerdc_weeks"]:
        return "**Depth source:** school-generated (no NERDC anchor for this subject).\n"
    L = [f"- {w['subject']} · {w['class']} · {w['term']} wk{w['week']}: {w['topic']} (pp {w['pages']})"
         for w in rec["nerdc_weeks"]]
    return "**Depth source (NERDC 2025):**\n" + "\n".join(L) + "\n"


def objectives(rec, lines):
    """3-5 measurable objectives, one per depth line where there are lines to cover."""
    stem = {"Understanding": "Explain", "Identifying": "Identify", "Comparing": "Compare",
            "Ordering": "Order", "Writing": "Write", "Reading": "Read", "Counting": "Count",
            "Naming": "Name", "Appreciating": "Appreciate", "Care": "Describe the care of"}
    src = lines[:5] if lines else [{"line": rec["topic"]}]
    out = []
    for l in src:
        t = re.sub(r"^\s*", "", l["line"] if isinstance(l, dict) else l)
        first = t.split(":")[0].split(" - ")[0].strip()
        pre = first.split()[0].capitalize() if first.split() else ""
        verb = stem.get(pre, "State") if pre in stem else "State"
        body = first if pre not in stem else first[len(pre):].lstrip(" ").strip()
        body = re.sub(r"\b\d+\s*(days?|terms?)\b", lambda m: m.group(0), body, flags=re.I)
        out.append(f"{verb.lower()} {body.strip(' .').lower()}.")
    return "\n".join(f"{i}. {o}" for i, o in enumerate(out, 1))


def auto_eval(rec, lines):
    n = min(5, max(3, len(lines)))
    stems = [l["line"] for l in lines[:n]] or [rec["topic"]]
    out = []
    for i, st in enumerate(stems, 1):
        key = re.split(r"[:,]|\s-\s", st)[0].strip()
        out.append(f"{i}. Mention/explain: {key.lower()}")
    return "\n".join(out)


def render(rec, tpl):
    lines = depth_lines(rec)
    stream = rec.get("stream")
    body = tpl
    rep = {
        "SUBJECT": rec["subject"], "CLASS": rec["class"],
        "STREAM": stream or "", "TERM": rec["term"], "WEEK": str(rec["week"]),
        "TOPIC": rec["topic"], "DATE": "", "MODE": rec["mode"],
        "CONFIDENCE": f"{rec['confidence']:.2f}",
        "EXPLICIT_SOURCE": rec.get("explicit_source_note") or "",
        "STREAM_SUFFIX": f" — {stream}" if stream else "",
        "SOURCES_BLOCK": sources_block(rec),
        "DEPTH_BULLETS": "\n".join(f"- {l['line']}" for l in lines)
                          or f"- {rec['topic']}  *(depth to be supplied — see reports/gaps.md)*",
        "OBJECTIVES": objectives(rec, lines),
        "NERDC_SOURCES": "\n".join(
            f"{w['subject']} · {w['class']} · {w['term']} wk{w['week']}" for w in rec["nerdc_weeks"]) or "—",
        "EVAL": auto_eval(rec, lines),
        # the school's rule: an assignment is worked by the pupil, alone. Never address a
        # parent or guardian, never ask an adult to teach, supervise or sign.
        "ASSIGN": ("Finish what you began today: "
                   + (lines[0]["line"].lower()[:70] if lines else rec["topic"].lower())
                   + ". Then find one more example of it at home or in the compound, and be "
                     "ready to say it in class tomorrow."),
    }
    for k, v in rep.items():
        body = body.replace("{{" + k + "}}", v)
    # regression tripwire for the generator only: the lesson *content* may legitimately name a
    # parent, but the assignment the template writes must be worked by the pupil alone.
    ADULT = re.compile(r"(?i)dear\s+parent|parents/guardians|parent\s*(?:or|and)\s*guardian|"
r"help\s+your\s+child|ask\s+your\s+child|sign\s+the\s+diary|supervis|oversee|"
r"please\s+ensure|with\s+the\s+help\s+of")
    if ADULT.search(rep["ASSIGN"]):
        raise SystemExit(f"template emits a parent-facing assignment: "
                         f"{rec['subject']} {rec['class']} wk{rec['week']}")
    return body, lines


def key_of(r):
    return (r["subject"], r["class"], r.get("stream"), r["term"], r["week"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--subject"); ap.add_argument("--class", dest="cls")
    ap.add_argument("--term"); ap.add_argument("--week", type=int)
    ap.add_argument("--selftest", action="store_true", help="render the 5 pilot rows")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--audit", action="store_true", help="check depth coverage of each note")
    ap.add_argument("--outdir", default=str(OUTDIR))
    a = ap.parse_args()

    data = json.loads(SRC.read_text(encoding="utf-8"))
    recs = data["records"]
    tpl = HOUSE.read_text(encoding="utf-8") if HOUSE.exists() else DEFAULT_TEMPLATE
    if not HOUSE.exists():
        print("note: templates/house.md not found — using the built-in layout "
              "(NERDC sample-note shape). Drop your house template there and re-run.")

    if a.selftest:
        want = [("Basic Science", "Nursery 2", None, 1), ("Mathematics & English", "Primary 1", "MATHEMATICS", 1),
                ("Yoruba", "Nursery 2", None, 1),
                ("Christian Religious Studies (CRS)", "Nursery 2", None, 1),
                ("Mathematics & English", "Primary 4", "MATHEMATICS", 1)]
        sel = []
        for s, c, st, wk in want:
            r = next((x for x in recs if x["subject"] == s and x["class"] == c and x["week"] == wk
                      and (st is None or x.get("stream") == st)), None)
            if r:
                sel.append(r)
    else:
        def keep(r):
            if a.subject and r["subject"] != a.subject: return False
            if a.cls and r["class"] != a.cls: return False
            if a.term and not (r["term"] == a.term or TERM_ALIAS.get(a.term) == r["term"]
                               or TERM_ALIAS.get(r["term"]) == a.term): return False
            if a.week and r["week"] != a.week: return False
            return True
        sel = [r for r in recs if keep(r)] if (a.all or a.subject or a.cls or a.term or a.week) else []
        if not sel:
            ap.error("nothing selected — use --selftest, or --subject/--class/--term/--week, or --all")

    outdir = Path(a.outdir); outdir.mkdir(parents=True, exist_ok=True)
    by_file = collections.defaultdict(list)
    audit = {"notes": 0, "lines": 0, "uncovered": collections.Counter(), "empty_depth": []}
    for r in sel:
        if r.get("kind") in ("calendar", "blank"):
            print(f"SKIPPED calendar row: {r['subject']} {r['class']} wk{r['week']}")
            continue
        body, lines = render(r, tpl)
        rid = f"{slug(r['subject'])}.{slug(r['class'])}.{slug(r['term'])}.wk{r['week']}"
        rid += f".{slug(r['stream'])}" if r.get("stream") else ""
        fname = f"{slug(r['subject'])}.{slug(r['class'])}.{slug(r['term'])}.jsonl"
        if a.selftest:
            fname = f"pilot.{fname}"
        by_file[fname].append({"id": rid, "note_key": key_of(r), "body": body,
                               "depth_lines": [l["line"] for l in lines],
                               "mode": r["mode"], "confidence": r["confidence"],
                               "nerdc_weeks": r["nerdc_weeks"], "topic": r["topic"]})
        audit["notes"] += 1
        audit["lines"] += len(lines)
        if not lines and r["mode"] != "school-generated":
            audit["empty_depth"].append(rid)

    for fname, rows in by_file.items():
        (outdir / fname).write_text("\n".join(json.dumps(x, ensure_ascii=False) for x in rows) + "\n",
                                    encoding="utf-8")
        print(f"wrote {outdir.name}/{fname}  ({len(rows)} note{'s' if len(rows)!=1 else ''})")

    if a.audit:
        def norm(t):
            t = unicodedata.normalize("NFKD", str(t)).lower()
            return set(re.findall(r"[a-z]{4,}", t))
        print("\n--- depth audit (does each note carry every NERDC subtopic line?) ---")
        for fname, rows in by_file.items():
            for x in rows:
                if x["mode"] == "school-generated":
                    continue
                nt = norm(x["body"])
                # a line with no comparable word (acronym-only, IPA glyphs) cannot be
                # token-checked; the writer still carries it verbatim, so skip it.
                miss = [l for l in x["depth_lines"]
                        if norm(l) and not (norm(l) & nt)]
                if miss:
                    print(f"  {x['id']}: {len(miss)} line(s) not represented, e.g. {miss[0][:60]}")
        print(f"  notes: {audit['notes']} | depth lines carried: {audit['lines']} | "
              f"notes with no depth at all: {len(audit['empty_depth'])}")


if __name__ == "__main__":
    main()
