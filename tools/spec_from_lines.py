#!/usr/bin/env python3
"""
spec_from_lines.py — expand a hand-written exam sheet (data/exams/src/<stem>.txt) into a spec
(data/exams/<stem>.json) that make_exam.py can render.

Why: authoring 45 questions per subject as JSON is noise. This is the same content, one question per
line, and the tool does the escaping, the counting and the complaint when a line is short.

    subject: Physical and Health Education          <- optional, else taken from the file name
    [objective]      stem || correct option || trap || trap || trap     (exactly 30)
    [subobjective]   stem                                              (exactly 10)
    [theory]         stem || marks                                     (exactly 5, marks optional)

A line may carry marking points after "::" — they are stored in the spec but never printed on the
pupil paper. Any word can be wrapped in ** for emphasis; it is stripped.

    python3 tools/spec_from_lines.py nursery-2__1st-term__physical-and-health-education [...]
    python3 tools/spec_from_lines.py --all --class "Nursery 2" --term "1st Term"
"""
import json, re, sys, argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "data/exams/src"
OUT = ROOT / "data/exams"
SECT = {"objective": "objective", "subobjective": "subobjective", "theory": "theory"}
NEED = {"objective": 30, "subobjective": 10, "theory": 5}


def clean(s):
    return re.sub(r"\s+", " ", re.sub(r"\*", "", s)).strip()


def expand(name, warn=print):
    src = SRC / f"{name}.txt"
    if not src.exists():
        warn(f"  !! no sheet {src.name}")
        return False
    section, rows = None, {"objective": [], "subobjective": [], "theory": []}
    meta = {}
    for raw in src.read_text(encoding="utf-8").splitlines():
        ln = raw.strip()
        if not ln or ln.startswith("#"):
            continue
        m = re.match(r"^\[(\w+)\]$", ln)
        if m:
            section = SECT.get(m.group(1).lower())
            if not section:
                warn(f"  !! {src.name}: unknown section [{m.group(1)}]")
            continue
        if section is None:
            k, _, v = ln.partition(":")
            if " || " not in ln and k.lower() in ("subject", "class", "term", "stream"):
                meta[k.lower()] = clean(v)
                continue
            warn(f"  !! {src.name}: line before any section: {ln[:60]}")
            continue
        parts = [clean(x) for x in ln.split("||")]
        pts = []
        parts[0], _, tail = parts[0].partition("::")
        if tail:
            pts = [clean(x) for x in tail.split("|") if clean(x)]
        if section == "objective":
            if len(parts) != 5:
                warn(f"  !! {src.name}: objective needs stem||answer||3 traps, got {len(parts)}: {ln[:70]}")
                continue
            ans = parts[1]
            dis = [p for p in parts[2:5]]
            if len({x.lower() for x in [ans] + dis}) != 4:
                warn(f"  !! {src.name}: repeated option in: {ln[:70]}")
                continue
            rows["objective"].append({"stem": parts[0], "answer": ans, "distractors": dis})
        elif section == "subobjective":
            rows["subobjective"].append({"stem": parts[0], "points": pts})
        else:
            marks = 2
            if len(parts) > 1 and re.fullmatch(r"\d+", parts[1]):
                marks = int(parts[1])
            rows["theory"].append({"stem": parts[0], "marks": marks, "points": pts})
    # more candidates than the paper can carry is a good problem: take them by even stride so the
    # whole term is sampled, and say what was left out. Too few is a real error — stop and fix it.
    dropped = {}
    for k in NEED:
        if len(rows[k]) > NEED[k]:
            n = NEED[k]
            stride = len(rows[k]) / n
            keep = [rows[k][min(len(rows[k]) - 1, int(i * stride))] for i in range(n)]
            keep = list({id(q): q for q in keep}.values())[:n]      # in order, no repeats
            dropped[k] = len(rows[k]) - len(keep)
            rows[k] = keep
    bad = [f"{k}: {len(rows[k])} (need {NEED[k]})" for k in NEED if len(rows[k]) != NEED[k]]
    if bad:
        warn(f"  !! {src.name}: " + ", ".join(bad) + " — not written")
        return False
    if dropped:
        warn("  note " + ", ".join(f"{k}: {v} extra question(s) not used" for k, v in dropped.items()))
    stem = name.split("__", 2)[-1]
    subj = meta.get("subject") or stem.replace("-", " ").title()
    if meta.get("stream"):
        subj += f" · {meta['stream']}"
    spec = {"subject": subj, "class": meta.get("class", ""), "term": meta.get("term", ""),
            **rows}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f"{name}.json").write_text(json.dumps(spec, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"  wrote data/exams/{name}.json  (30/10/5)")
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("names", nargs="*")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--class", dest="cls")
    ap.add_argument("--term")
    a = ap.parse_args()
    names = list(a.names)
    if a.__dict__["all"]:
        pre = ""
        if a.cls and a.term:
            s = lambda x: re.sub(r"[^a-z0-9]+", "-", x.lower()).strip("-")
            pre = s(a.cls) + "__" + s(a.term) + "__"
        names = [p.stem for p in sorted(SRC.glob(f"{pre}*.txt"))]
    if not names:
        sys.exit("give sheet names or --all [--class --term]")
    ok = sum(1 for n in names if expand(n))
    print("sheets expanded:", ok, "of", len(names))
    if ok != len(names):
        sys.exit(1)


if __name__ == "__main__":
    main()
