#!/usr/bin/env python3
"""
polish_audit.py — read the authored notes and report the things that make a book feel careless.

The builder (`build_term_doc.py --strict`) checks the school's *rules*: a note for every teaching week,
none for a calendar week, no answers, no grown-up addressee, 30/10/5 papers, page numbers that match the
file. Those are pass/fail, and they are already green. This tool checks *quality*: does every block a
note should have exist and hold the right number of items, is a line too long for a five-year-old's ear,
is there something for the hands to make, does a bullet appear in two different weeks, is the register
grown-up. Everything it reports is fixable in the sources under `notes/src/`.

    python3 tools/polish_audit.py --class "Nursery 2" --term "2nd Term" [--list 12] [--json]

Exit code is 0 when nothing is reported, 1 otherwise — so it can join the build chain once the books are
clean of it. The two tiers matter: `(a defect)` lines want fixing now, `(worth a look)` lines are notes
for the next time a subject is touched.
"""
import argparse
import collections
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# the blocks a note must carry, in this order (notes/README.txt documents the same list)
# Owner's word, 3 Sep 2026: "the 'things to know' section ought to now be 'main content'. You can do
# away with the objective sections."  So the per-week "You will learn to" block is GONE and the body
# block is now "Main content".
BLOCKS = ["Main content", "Words for my notebook", "Let us talk",
          "Worksheet", "My own work"]
# (how to count items, fewest allowed, most allowed) — b bullets, n numbered lines, p prose paragraphs
# The bounds below are the NURSERY floor; every class above it is widened by DEPTH.
SHAPE = {"Main content": ("b", 8, 12),
         "Words for my notebook": ("p", 1, 4), "Let us talk": ("n", 3, 6),
         "Worksheet": ("n", 7, 7), "My own work": ("p", 1, 3)}
# a revision week says "What to revise" where everyone else says "Main content", and may run shorter
ALIAS = {"Main content": (["What to revise"], 5, 12)}   # a revision note may run 5-12

# Notes get more elaborate as the class goes up — same house shape, a fuller body.  Owner's word,
# 3 Sep 2026: "the lesson notes ought to become more elaborate as we move towards the upper classes".
# (Main content lo, Main content hi, Words lo, Words hi)
DEPTH = {"nursery-2": (8, 12, 1, 4), "primary-1": (10, 14, 2, 5), "primary-2": (14, 22, 3, 6),
         "primary-3": (16, 24, 3, 7), "primary-4": (18, 26, 4, 8)}
DEFAULT_DEPTH = (8, 12, 1, 4)

# Word-only subjects: no plate in the book AND no drawing task for the child — "My own work" is
# written or spoken instead.  Owner's word, 3 Sep 2026 added mathematics and english to the list.
WORD_ONLY = {"yoruba", "general-knowledge", "nigerian-history", "social-and-citizenship-studies",
             "christian-religious-studies", "mathematics-english-mathematics",
             "mathematics-english-english-language"}


def class_slug(cls):
    return cls.lower().replace(" ", "-")


def depth_for(cls):
    """The (content lo, content hi, words lo, words hi) bounds this class is held to."""
    return DEPTH.get(class_slug(cls), DEFAULT_DEPTH)
# words a five-year-old's book should not need — each is a register tell, not a vocabulary ban
ADULT = (r"\b(however|therefore|moreover|additionally|furthermore|consequently|utili[sz]e|acquir"
         r"e|demonstrat|approximat|sufficient|necessar|environmental|significan|particular(?:ly)?"
         r"|specific(?:ally)?|individuals?|circumstance|constitute|illustrat|subsequently|in order "
         r"to|as well as the|facilitat|regardin|commence|prior to)\b")
# an adult being addressed or deputised.  Deliberately NOT the bare nouns: "a broken glass is swept up
# by a grown-up" is a safety rule the child must learn, and CRS says "a father on earth is different
# from God".  Those are content.  What is not allowed is the child's own work handing the job over.
ADULT_NOUN = r"(?:parents?|mum|dad|mother|father|grown-?up|adult|guardian|teacher|big brother|sister)"
# the adult must be the one *doing* something for the child.  Naming a relative is not a violation.
DEPUTISE = (rf"(?:{ADULT_NOUN})[^.\n]{{0,42}}?(?:\b(?:help|check|read|write|mark|sign|hold|cut|carry|wash"
            r"|show|tell me|explain|sit with|come with|assist)\b|\bto\s+(?:help|check|read|write)\b)"
            rf"|(?:ask|get|let|have|make|with|from)\s+(?:an?|your|my)?\s*{ADULT_NOUN}"
            r"|please help|the teacher will|teacher should|supervise")
# something for the hands — the drawing, cutting, pasting or tracing that makes a Nursery page Nursery
MAKING = r"\b(draw|colour|color|cut|paste|glue|trace|paint|model|clay|fold|stick|copy|match|colour in)\b"

WEEK_HEAD = re.compile(r"^### WEEK (\d+) — (.+)$")
BLOCK_HEAD = re.compile(r"^\*\*(.+?)\*\*\s*$")
BULLET = re.compile(r"^•\s+(.*)$")
NUMBERED = re.compile(r"^\s*(\d{1,2})[.)]\s+(.*)$")


def notes_of(text):
    """one dict per note: week, title, the heading's line number, and [(block, line, [lines])]."""
    out, cur = [], None
    for i, ln in enumerate(text.splitlines(), start=1):
        m = WEEK_HEAD.match(ln)
        if m:
            if cur:
                out.append(cur)
            cur = {"week": int(m.group(1)), "title": m.group(2), "line": i, "blocks": [], "plain": []}
            continue
        if cur is None:
            continue
        b = BLOCK_HEAD.match(ln)
        if b:
            cur["blocks"].append([b.group(1).strip(), i, []])
        elif cur["blocks"]:
            cur["blocks"][-1][2].append((i, ln))
        else:
            cur["plain"].append((i, ln))
    if cur:
        out.append(cur)
    return out


def sentences(text):
    """the words a five-year-old's ear has to hold at one time.  `·` and `|` separate clauses inside a
    bullet, so they end a "sentence" for this purpose — otherwise "the dog in a kennel · the chicken in
    a coop · the cow in a shed" counts as one 78-word sentence and this tool cries wolf."""
    out = []
    for chunk in re.sub(r"\*\*|\*|`", "", text).split("\n"):
        for s in re.split(r"(?<=[.!?])\s+|[·|]\s+|\s+·\s+", chunk):
            s = s.strip(" -–—")
            if len(s.split()) > 2:
                out.append(s)
    return out


def count_of(kind, body):
    n = 0
    for _, ln in body:
        if kind == "b" and BULLET.match(ln):
            n += 1
        elif kind == "n" and NUMBERED.match(ln):
            n += 1
        elif kind == "p" and ln.strip() and not ln.strip().startswith("!["):
            n += 1
    return n


def srcdir(cls, term):
    slug = f"{cls.lower().replace(' ', '-')}__{term.lower().replace(' term', '-term').replace(' ', '-')}"
    return ROOT / "notes" / "src" / slug


def audit(cls, term, list_n=12):
    d = srcdir(cls, term)
    if not d.is_dir():
        raise SystemExit(f"no sources at {d.relative_to(ROOT)}")
    files = sorted(d.glob("*.md"))
    notes, problems, dupes = [], collections.Counter(), []
    for f in files:
        subj = f.stem.replace("-", " ").strip().title()
        for n in notes_of(f.read_text(encoding="utf-8")):
            n["subject"], n["file"], n["stem"] = subj, f.name, f.stem
            notes.append(n)
    c_lo, c_hi, w_lo, w_hi = depth_for(cls)          # this class's depth ladder rung
    LADDER = {"Main content": (c_lo, c_hi), "Words for my notebook": (w_lo, w_hi)}
    for n in notes:
        where = lambda s: f'{n["file"]}:{n["line"]}'
        flag = lambda at, msg: n.setdefault("issues", []).append((at, msg))
        for blk in BLOCKS:
            names, lo, hi = ALIAS.get(blk, ([], *SHAPE[blk][1:]))
            hit = [b for b in n["blocks"] if any(x.lower() in b[0].lower() for x in [blk] + list(names))]
            if hit and names and hit[0][0].lower() in [x.lower() for x in names]:
                lo, hi = max(lo, c_lo), max(hi, c_hi)   # revision variant, widened with the class
            elif blk in LADDER:
                lo, hi = LADDER[blk]                    # an ordinary note is held to its class's rung
            elif hit and names:
                lo, hi = SHAPE[blk][1:]
            if not hit:
                problems[f"missing block: {blk}"] += 1
                flag(where(blk), f"no **{blk}**")
                continue
            kind, _, _ = SHAPE[blk]
            c = count_of(kind, hit[0][2])
            if c < lo or c > hi:
                want = f"{lo}" if hi == lo else f"{lo}-{hi}"
                if c < lo:
                    # Falling SHORT of the class's depth floor is a defect, not a style note: the whole
                    # point of the ladder (owner, 3 Sep 2026) is that upper-class notes get fuller.
                    problems[f"too thin: {blk} has {c} items (class floor {lo})"] += 1
                    flag(where(blk), f"{blk} has {c} items, this class wants at least {lo}")
                else:
                    problems[f"shape: {blk} has {c} items (house shape {want})"] += 1
                    flag(where(blk), f"{blk} has {c} items, wants {want}")
        body = "\n".join(ln for b in n["blocks"] for _, ln in b[2])
        allt = "\n".join([n["title"], body] + [ln for _, ln in n["plain"]])
        # a word-only subject gives the child written or spoken work, not a drawing — no cue required.
        if (n.get("stem") not in WORD_ONLY
                and not re.search(MAKING, allt, re.I) and "\n![" not in "\n" + body):
            problems["nothing for the hands (draw/colour/cut/paste/trace)"] += 1
            flag(where("make"), "no draw/colour/cut/paste cue anywhere in the note")
        for m in re.finditer(ADULT, allt, re.I):
            problems["grown-up register word"] += 1
            flag(where("register"), f"'{m.group(1).lower()}'")
        # an A)-D) option line is not a plea for help — "B) tell the teacher D) cut it" is a *choice*.
        mine = "\n".join(ln for b in n["blocks"] if b[0].lower() in ("my own work", "let us talk")
                         for _, ln in b[2] if not re.search(r"[A-D]\)\s+\S", ln))
        for m in re.finditer(DEPUTISE, mine, re.I):
            problems["deputises a grown-up in the child's own work"] += 1
            flag(where("adult"), f"'{m.group(0).lower()}'")
        # a bolded option in a note's worksheet PRINTS the answer for the child.  Nearly happened while
        # authoring Third Term, so it is now a defect rather than a style note.
        for blk in n["blocks"]:
            if blk[0].lower() != "worksheet":
                continue
            for i, ln in blk[2]:
                m = re.search(r"\bA\)\s", ln)
                if m and "**" in ln[m.start():]:
                    problems["worksheet item with a bolded option (prints the answer)"] += 1
                    flag(f'{n["file"]}:{i}', f"bold after the options: {ln.strip()[:44]}…")
        # a figure reference is markup, not a sentence anybody hears, so it is not measured for length
        body_prose = "\n".join(ln for ln in body.splitlines() if not ln.strip().startswith("!["))
        for s in sentences(re.sub(r"^\s*[•\d.)]+\s*", "", body_prose, flags=re.M)):
            w = len(s.split())
            if w > 40:
                problems["line over 40 words (a defect)"] += 1
                flag(where("long"), f"{w}-word line: {s[:56]}…")
            elif w > 32:
                problems["line of 33-40 words (worth a look)"] += 1
        if "—" in n["title"] and n["title"] != n["title"].upper():
            problems["week title not in caps"] += 1
            flag(where("caps"), n["title"][:44])
    for f in files:                                   # the copy-paste tell, per subject file
        seen = {}
        for n in notes_of(f.read_text(encoding="utf-8")):
            for blk in n["blocks"]:
                for i, ln in blk[2]:
                    m = BULLET.match(ln)
                    if not m:
                        continue
                    key = re.sub(r"[^a-z0-9 ]", "", m.group(1).lower())
                    if len(key) < 25:
                        continue                      # short lines repeat on purpose ("say it once more")
                    first = seen.get(key)
                    if first and first[0] != n["week"]:
                        problems["same bullet in two weeks of a subject"] += 1
                        dupes.append((f.name, i, f"wk{n['week']} repeats wk{first[0]}: {m.group(1)[:56]}"))
                    else:
                        seen.setdefault(key, [n["week"], None])
    nomake = collections.Counter(n["subject"] for n in notes
                                 if any("no draw" in msg for _, msg in n.get("issues", [])))
    return {"class": cls, "term": term, "notes": len(notes), "subjects": len(files),
            "no_make_by_subject": dict(nomake.most_common()), "problems": dict(problems.most_common()),
            "dupes": dupes[:list_n], "dupe_count": len(dupes),
            "worst": sorted([{"note": f'{n["subject"]} wk{n["week"]}', "line": n["line"], "file": n["file"],
                              "issues": n["issues"]} for n in notes if n.get("issues")],
                            key=lambda x: -len(x["issues"]))[:list_n]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--class", dest="cls", default="Nursery 2")
    ap.add_argument("--term", required=True)
    ap.add_argument("--list", type=int, default=12, help="how many worst notes / repeats to print")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    r = audit(a.cls, a.term, a.list)
    advisory = ("worth a look", "shape:")
    defects = sum(v for k, v in r["problems"].items() if not any(a in k for a in advisory))
    if a.json:
        print(json.dumps(r, indent=1))
        sys.exit(1 if defects else 0)
    soft = sum(v for k, v in r["problems"].items() if any(a in k for a in advisory))
    print(f"notes   : {r['notes']} across {r['subjects']} subject files · {defects} to fix"
          f" · {soft} to consider (long lines, block shape — reported, not refused)")
    for k, v in r["problems"].items():
        print(f"  {v:>4}  {k}")
    if r["no_make_by_subject"]:
        print("nothing for the hands, by subject:")
        print("  " + " · ".join(f"{s} {c}" for s, c in r["no_make_by_subject"].items()))
    if r["worst"]:
        print(f"\nworst {min(a.list, len(r['worst']))} notes:")
        for w in r["worst"]:
            print(f"  {w['note']:<34} {w['file']}:{w['line']}")
            for at, msg in w["issues"][:4]:
                print(f"       {at:<34} {msg}")
    if r["dupes"]:
        print("\nsame bullet in two weeks:")
        for f, l, m in r["dupes"]:
            print(f"  {f}:{l}  {m}")
    sys.exit(1 if defects else 0)


if __name__ == "__main__":
    main()
