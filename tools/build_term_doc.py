#!/usr/bin/env python3
"""
build_term_doc.py — assemble one class-term book (all subjects offered to that class) and validate it.

Reads the authored pupil sections in notes/src/<Class>__<Term>/*.md, appends each subject's term
practice paper from build/, writes notes/<Class> - <Term>.md (the working copy) and
notes/<Class> - <Term>.docx (the deliverable: A4 landscape, two columns — see tools/docx_out.py).

The rules this enforces are the school's own:
  1. every teaching week in the master for this class-term has a note, streamed subjects per stream;
  2. no note for a calendar week (Mid-Term, Revision, Examination, Closing) unless the master itself
     prints that week as a teaching row;
  3. the book speaks to the pupil: no teaching steps, no teacher deputation, no answer key, and no
     request to a parent or guardian anywhere in an assignment;
  4. every note carries an exam-style worksheet with objective, fill-in, short-answer and theory parts
     and a "My own work" piece the pupil does alone;
  5. every subject ends with a term paper of 30 objective + 10 sub-objective + 5 theory items;
  6. the answer letters of those papers show no pattern — read from the key sidecar, which is never
     printed in the pupil's book.

Usage: python3 tools/build_term_doc.py --class "Nursery 2" --term "1st Term" [--strict] [--nodocx]
"""
import json, re, argparse, sys, collections, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MASTER = ROOT / "data/curriculum_master.json"
SRC = ROOT / "notes/src"
BUILT = ROOT / "data/exams/papers"
OUT = ROOT / "notes"

# A pupil's book must not read like a lesson plan or a mark scheme.
PLAN_WORDS = re.compile(r"(?i)(\bteacher(?:'s|s)?\s+(?:guides|introduces|shows|demonstrates|provides|"
                        r"asks|writes|draws|explains|tells|says|models|notes)\b|\bthe teacher\b\s+\w+\s+"
                        r"(?:the pupils|pupils)|^\s*(?:Step|Method|Procedure|Presentation)\s+\d|"
                        r"\bObjectives?:\b|\bMaterials?:\b|\bMarking (?:scheme|guide)\b|\bAnswer key\b|"
                        r"\bTeacher's key\b|\b(?:solution|correct answer)\b|\bInstruction(al)? (?:note|point)\b)")
# An assignment may not deputise a grown-up. Speaking ABOUT parents, mothers or fathers is curriculum
# content, not a request to them — so only the request-shaped phrases are caught.
PARENT_WORDS = re.compile(r"(?i)dear\s+parent|parents?\s*(?:or|and|/)\s*guardians?|parents/guardians|"
                          r"help\s+your\s+child|ask\s+your\s+child|let\s+your\s+child|to\s+be\s+done\s+with|"
                          r"sign\s+the\s+diary|supervis\w*|oversee|please\s+ensure|parent to|guardian to|"
                          r"with\s+(?:the\s+help\s+)?of\s+(?:a|an|your|the)\s+\w*(?:adult|parent|guardian|teacher|mum|dad)")
# every note needs these; "Main content" is "What to revise" in a revision note.
# Owner's word, 3 Sep 2026: the "You will learn to" objective block is gone and "Things to know"
# is now "Main content".  The old name is still accepted so a half-migrated tree keeps building.
BLOCKS = [("**Main content", "**Things to know", "**What to revise"),
          ("**Words for my notebook**",), ("**Let us talk**",), ("**Worksheet**",), ("**My own work**",)]
TERM_PRETTY = {"1st Term": "First Term", "2nd Term": "Second Term", "3rd Term": "Third Term"}
CALENDAR = re.compile(r"(?i)mid[- ]?term|revision|examination|closing|awards|break|test\b|vacation")


def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def week_titles(cls, term):
    """The approved teaching set for this class-term, straight from the master corpus."""
    m = json.loads(MASTER.read_text(encoding="utf-8"))
    terms = {term.lower(), TERM_PRETTY.get(term, term).lower()}
    want = []
    for s in m["subjects"]:
        cn = next((c for c in s["classes"] if c["class"] == cls), None)
        if not cn:
            continue
        rows = []
        if cn.get("by_term"):
            for t, rr in cn["by_term"].items():
                if t.lower() in terms:
                    rows += [(None, r) for r in rr]
        else:
            for sname, st in (cn.get("streams") or {}).items():
                for tt in st["terms"]:
                    # a stream's term cell can carry a syllabus title: "FIRST TERM — Myself, My Family"
                    if tt["term"].lower() in terms or any(x in tt["term"].lower() for x in terms):
                        rows += [(sname, r) for r in tt["rows"]]
            for b in cn.get("blocks") or []:
                if any(x in b["heading"].lower() for x in terms):
                    rows += [(None, r) for r in b["rows"]]
        for stream, r in rows:
            topic = r.get("topic") or (r.get("cells") or {}).get("Topic") \
                or next(iter((r.get("cells") or {}).values()), "")
            topic = (topic or "").strip()
            if r.get("kind") == "topic" and topic and topic != "—":
                want.append((s["name"], stream, r["week"], topic))
    return want


def gh_slug(s, used):
    """the anchor a markdown viewer gives this heading (GitHub's rule), numbered on a repeat"""
    a = re.sub(r"[^\w\s-]", "", s.strip().lower(), flags=re.UNICODE).strip()
    a = re.sub(r"\s+", "-", a)
    n = used.get(a, 0)
    used[a] = n + 1
    return a if n == 0 else f"{a}-{n}"


def contents_block(text):
    """Build '## Contents' from the headings of the assembled book: every subject and every term
    paper is a level-1 line, every teaching week under it a level-2 line. The .docx turns the same
    lines into a real Word TOC field (tools/docx_out.py), so the two never disagree: the list is read
    off the headings, never written by hand."""
    lines, used, open_subject = [], {}, None
    first_h1 = True
    for ln in text.splitlines():
        if ln.startswith("# ") and not ln.startswith("##"):
            h = ln[2:].strip()
            if first_h1:                                 # the book's own title is not contents
                first_h1 = False
                continue
            open_subject = h
            lines.append(f"- **[{h}](#{gh_slug(h, used)})**")
        elif re.match(r"^###\s+WEEK\s+\d", ln):
            if open_subject is None:
                continue
            h = ln[4:].strip()
            lines.append(f"  - [{h}](#{gh_slug(h, used)})")
    if not lines:
        return ""
    parts = [x for x in lines if x.startswith("- **")]
    papers = sum(1 for x in parts if "EXAMINATION PRACTICE" in x)
    lessons = len(lines) - len(parts)
    head = ("## Contents\n\n*"
            + f"{len(parts) - papers} subjects · {lessons} lessons · {papers} term practice papers"
            + ". Each part begins on a fresh page.*\n\n")
    return head + "\n".join(lines) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--class", dest="cls", required=True)
    ap.add_argument("--term", required=True)
    ap.add_argument("--strict", action="store_true", help="exit non-zero on any problem")
    ap.add_argument("--nodocx", action="store_true")
    ap.add_argument("--no-images", dest="no_images", action="store_true",
                    help="build the text-only book; the page model then numbers the text-only pages")
    ap.add_argument("--edition", choices=("pupil", "teacher"), default="pupil",
                    help="teacher appends every paper's key (letters, answer texts, marking points) and "
                         "drops the pupil 'no answer' gate in favour of 'every paper must have a key'")
    a = ap.parse_args()
    TEACHER = a.edition == "teacher"
    SUFFIX = " - TEACHER COPY" if TEACHER else ""

    d = SRC / f"{slug(a.cls)}__{slug(a.term)}"
    sections = sorted(p for p in d.glob("*.md") if not p.name.startswith("_")) if d.exists() else []
    if not sections:
        sys.exit(f"no authored sections in {d}")

    want = week_titles(a.cls, a.term)
    by_subject = collections.defaultdict(list)
    for subj, stream, wk, topic in want:
        by_subject[subj].append((stream, wk, topic))
    read = {p: p.read_text(encoding="utf-8") for p in sections}
    def bare(s):                      # "Cultural and Creative Arts (CCA)" == "Cultural and Creative Arts"
        return re.sub(r"\s*\([^)]*\)\s*$", "", (s or "")).strip()
    def subj_of(p):
        return read[p].splitlines()[0].lstrip("# ").split("—")[0].strip()
    order = [s["name"] for s in json.loads(MASTER.read_text(encoding="utf-8"))["subjects"]
             if s["name"] in by_subject]
    have_subject = {bare(subj_of(p)) for p in sections}
    order = [s for s in order if bare(s) in have_subject] + \
            [subj_of(p) for p in sections if bare(subj_of(p)) not in {bare(s) for s in order}]

    def stream_of(p):
        m = re.search(r"\*\*Stream:\s*([^.*]+)", read[p])
        return m.group(1).strip() if m else None

    # ---------------- assembly: notes by subject, then the term papers ----------------
    body = [f"# {a.cls} — {TERM_PRETTY.get(a.term, a.term)}",
            ""]
    if TEACHER:
        body += ["**TEACHER COPY — not for pupils.** This file carries the term-paper keys, the answer "
                 "texts and the marking points. Keep it out of the pupil's book and out of the classroom "
                 "pile.",
                 ""]
    body += ["*Pupil's book · every subject offered to this class, every teaching week of the term.*"
             if not TEACHER else
             "*Teacher's edition · the pupil pages plus the keys and marking guidance.*",
             "",
            f"**{len(by_subject)} subjects · {len(want)} lessons · "
            f"{sum(1 for r in d.glob('*.md')) } sections.** Weeks 7, 10, 11 and 12 are Mid-Term Break, "
            "Revision, Examination and Closing: no lesson is written for a week the school keeps for "
            "those, except where the school's own table prints a teaching row there.",
            "",
            "Each lesson ends with a worksheet and a piece of my own work; each subject ends with the "
            "term practice paper — 30 objective, 10 sub-objective and 5 theory questions. The contents "
            "page lists every part and every lesson of this book.",
            ""]
    body.append("\n\n---\n\n@@CONTENTS@@\n")

    notes = 0
    covered = set()
    def nkey(s):
        return re.sub(r"[^a-z0-9]", "", (s or "").lower())

    def split_section(text):
        """(subject line, intro paragraph, the notes) of one authored section"""
        lines = text.splitlines()
        title = lines[0].lstrip("# ").strip() if lines and lines[0].startswith("#") else ""
        rest = "\n".join(lines[1:]).strip()
        intro, notes_part = "", rest
        if "\n---" in rest:
            head, notes_part = rest.split("\n---", 1)
            intro = head.strip()
        return title, intro, re.sub(r"^\*\*Stream:[^*]*\*\.?\s*", "", notes_part).strip()

    parts, intros = {}, {}
    for p in sections:
        _title, intro, notes_part = split_section(read[p])
        parts[p] = notes_part
        intros.setdefault(bare(subj_of(p)), []).append(intro)

    for subj in order:
        mine = sorted([p for p in sections if bare(subj_of(p)) == bare(subj)],
                      key=lambda q: (nkey(stream_of(q)), q.stem))
        body.append(f"\n\n---\n\n# {subj}")
        lead = "\n\n".join(x for x in intros[bare(subj)] if x and not x.startswith("**Stream:"))
        if lead:
            body.append("\n" + lead + "\n")
        for q in mine:
            st = stream_of(q)
            if st:
                body.append(f"\n## {st}\n\n" + parts[q])
            else:
                body.append("\n" + parts[q])
            notes += len(re.findall(r"^###\s+WEEK\s+\d+", parts[q], re.M))
            for m in re.finditer(r"^###\s+WEEK\s+(\d+)", parts[q], re.M):
                covered.add((nkey(bare(subj)), nkey(st), int(m.group(1))))

    def teacher_key_block(paper_text, key_text):
        """For the teacher's edition: Section A as 'n. LETTER — answer text', then the sidecar's
        B & C marking guide. The letter comes from the key; the text from the paper's own options,
        so the printed answer is the option the child actually sees."""
        letters = re.findall(r"\d+\.\s*([A-D])\b",
                             key_text.split("**Section A:**")[-1].split("**Sections B")[0])
        a_part = paper_text.split("## Section B")[0]
        items = []                                   # [(stem, {letter: text})]
        for l in a_part.splitlines():
            if re.match(r"^\d+\.\s", l):
                items.append([l.strip(), {}])
            elif items:
                m = re.match(r"^\s*\(?([A-D])\)\s*(.*)$", l)
                if m:
                    items[-1][1][m.group(1)] = m.group(2).strip()
        out = ["", "**Teacher's key — Section A (letter and answer text)**", ""]
        for i, (stem, texts) in enumerate(items):
            L = letters[i] if i < len(letters) else "?"
            out.append(f"{i + 1}. {L} — {texts.get(L, '')}")
        bc = key_text.split("**Sections B")[1] if "**Sections B" in key_text else ""
        if bc.strip():
            out += ["", "**Marking points — Sections B & C**", bc.strip()]
        return "\n".join(out)

    papers, keylets, keyreport = [], [], []
    for subj in order:
        mine = [p for p in sections if bare(subj_of(p)) == bare(subj)]
        mine.sort(key=lambda p: (stream_of(p) or ""))
        for p in mine:
            tag = f"{slug(a.cls)}__{slug(a.term)}__{p.stem}"
            paper, keyfile = BUILT / f"exam-{tag}.md", BUILT / f"exam-{tag}.key.md"
            label = subj + (f" · {stream_of(p)}" if stream_of(p) else "")
            if not paper.exists():
                papers.append(f"\n\n---\n\n# {label} — term practice paper\n\n"
                              "**MISSING** — run `tools/make_exam.py` on "
                              f"`data/exams/{tag}.json`.\n")
                continue
            ptx = paper.read_text(encoding="utf-8").strip()
            papers.append("\n\n---\n\n" + ptx)
            ktx = keyfile.read_text(encoding="utf-8") if keyfile.exists() else ""
            if TEACHER:
                if ktx:
                    papers.append("\n\n" + teacher_key_block(ptx, ktx) + "\n")
                else:
                    papers.append("\n\n**KEY MISSING** — no sidecar for this paper; the teacher's "
                                  "copy must not guess it.\n")
            ks = re.findall(r"\d+\.\s*([A-D])\b", ktx.split("**Section A:**")[-1]
                            .split("**Sections B")[0]) if ktx else []
            keylets += ks
            keyreport.append((label, ks))

    body += papers
    term_pretty = TERM_PRETTY.get(a.term, a.term)
    book = "\n".join(body) + "\n"
    # A picture is a promise the page model has to keep: the plate must be on disk, or the numbers in the
    # Contents would be arithmetic over a book that cannot be laid out.  --no-images is the text-only
    # edition (a copier out of toner still gets a book whose page numbers are true for what it holds).
    plates = sorted(set(re.findall(r"(?m)^!\[[^\]]*\]\(([^)\s]+)", book)))
    if a.no_images:
        book = "\n".join(ln for ln in book.splitlines() if not ln.strip().startswith("![")) + "\n"
        plates = []
    toc = contents_block(book)
    if "@@CONTENTS@@" in book:
        book = book.replace("@@CONTENTS@@", toc.rstrip("\n")
                            or "## What this book holds\n\n" + " · ".join(order))
    # The page numbers are not a forecast of what Word will do. tools/docx_out.py forces a page break
    # at every boundary the plan names, so a heading sits on the page printed beside it — unless some
    # block overflows the page it was given, which is exactly what the measurement watches for. Stamping
    # the numbers changes the length of a line, so the plan is run again: if a number moved, the
    # Contents is refusing to fit its own page and the build stops rather than print a wrong one.
    from book_layout import flow_of, plan, stamp_contents
    pages, _brk, model, info = plan(flow_of(book))
    book, numbered = stamp_contents(book, pages)
    pages2, _brk2, model2, _info2 = plan(flow_of(book))
    if pages2 != pages:
        moved = sum(1 for k in pages if pages2.get(k) != pages[k])
        model.append(f"{moved} page number(s) moved when they were printed — the Contents line is "
                     f"widening the page it sits on; lower FILL in tools/book_layout.py or shorten "
                     f"a heading")
    model = model + model2
    out_md = OUT / f"{a.cls} - {term_pretty}{SUFFIX}.md"
    out_md.write_text(book, encoding="utf-8")
    out_dx, info = None, {}
    if not a.nodocx:
        sys.path.insert(0, str(ROOT / "tools"))
        from docx_out import render
        out_dx, rmodel, rinfo = render(book, OUT / f"{a.cls} - {term_pretty}{SUFFIX}.docx")
        model, info = model + rmodel, rinfo

    # ---------------- validation ----------------
    parts = len(re.findall(r"(?m)^- \*\*\[", book))
    lessons = len(re.findall(r"(?m)^  - \[", book))
    lines_listed = parts + lessons
    problems = [f"the book asks for a picture that is not in the workspace: {r}"
                for r in plates if not (ROOT / r).exists()]
    for p in sections:
        t = read[p]
        for blk in re.split(r"(?=^###\s+WEEK)", t, flags=re.M)[1:]:
            no = re.match(r"###\s+WEEK\s+(\d+)", blk).group(1)
            for alts in BLOCKS:
                if not any(b in blk for b in alts):
                    problems.append(f"{p.stem} wk{no}: missing {alts[0].strip('*')}")
            ws = blk.split("**Worksheet**")[1].split("**My own work**")[0] if "**Worksheet**" in blk else ""
            if ws:
                if not re.search(r"[A-D]\)", ws):
                    problems.append(f"{p.stem} wk{no}: worksheet has no objective options")
                if "____" not in ws:
                    problems.append(f"{p.stem} wk{no}: worksheet has no fill-in")
            for bad in PLAN_WORDS.findall(blk):
                problems.append(f"{p.stem} wk{no}: reads like a lesson plan or a mark scheme — "
                                f"{str(bad)[:40]!r}")
            own = blk.split("**My own work**")
            if len(own) > 1 and PARENT_WORDS.search(own[1]):
                problems.append(f"{p.stem} wk{no}: my own work deputises a grown-up")
            if re.search(r"(?i)\bwith\s+(?:a|the|your)\s+(?:grown[- ]up|adult|parent|mum|dad|mama|papa)\b",
                         own[1] if len(own) > 1 else ""):
                problems.append(f"{p.stem} wk{no}: my own work asks a grown-up to take part")
    for subj, rows in by_subject.items():
        for stream, wk, topic in rows:
            s = nkey(re.sub(r"\s*\([^)]*\)\s*$", "", subj))
            if (s, nkey(stream), wk) in covered or (s, "", wk) in covered:
                continue
            problems.append(f"no note for {subj}" + (f" · {stream}" if stream else "") + f" wk{wk}")
    # papers: counts and patternless letters (the key lives only in the sidecar, never in the book)
    for p in sections:
        tag = f"{slug(a.cls)}__{slug(a.term)}__{p.stem}"
        paper = BUILT / f"exam-{tag}.md"
        if not paper.exists():
            problems.append(f"{p.stem}: no term practice paper")
            continue
        tx = paper.read_text(encoding="utf-8")
        a_part, b_part = tx.split("## Section B")[0], tx.split("## Section B")[1].split("## Section C")[0]
        c_part = tx.split("## Section C")[1]
        got = (len(re.findall(r"(?m)^\d+\.\s", a_part)), len(re.findall(r"(?m)^\d+\.\s", b_part)),
               len(re.findall(r"(?m)^\d+\.\s", c_part)))
        if got != (30, 10, 5):
            problems.append(f"{p.stem}: paper is {got[0]}/{got[1]}/{got[2]}, needs 30/10/5")
        if not TEACHER:                       # the no-answers gate is a pupil property
            for leak in ("Teacher's key", "Answer key", "correct answer is", "marking guide"):
                if leak.lower() in tx.lower():
                    problems.append(f"{p.stem}: the pupil's paper prints an answer — {leak}")
        else:                                  # the teacher's copy demands the opposite: a key present
            if not (BUILT / f"exam-{slug(a.cls)}__{slug(a.term)}__{p.stem}.key.md").exists():
                problems.append(f"{p.stem}: teacher's copy owes a key — the sidecar is missing")

    # contents: every entry must land on a heading that is really in the book. A markdown viewer
    # numbers repeated headings in document order (-1, -2 …), so the check has to number them the
    # same way or a perfectly good link is called dead.
    anchors, all_used = set(), {}
    for ln in book.splitlines():
        if re.match(r"^#{1,6}\s", ln) and not ln.strip().lower() == "## contents":
            anchors.add(gh_slug(ln.lstrip("# ").strip(), all_used))
    listed = re.findall(r"(?m)^ *(?:- )?\*?\*?\[[^\]]+\]\(#([^)]+)\)", book)
    dead = [x for x in listed if x not in anchors]
    if dead:
        problems.append(f"contents: {len(dead)} entry/entries point at no heading — "
                        + ", ".join(dead[:4]))
    if not listed:
        problems.append("contents: the book has no Contents section")
    listed_parts = len(re.findall(r"(?m)^- \*\*\[", book))
    real_parts = len(re.findall(r"(?m)^# ", book)) - 1          # minus the book's own title
    if listed_parts != real_parts:
        problems.append(f"contents: {listed_parts} parts listed, the book has {real_parts}")

    # each paper is judged on its own 30 letters — a repeat across two different papers is not a pattern
    dist = collections.Counter(keylets)
    runs = abab = badbal = 0
    worst = []
    for label, ks in keyreport:
        d = collections.Counter(ks)
        r = sum(1 for i in range(len(ks) - 1) if ks[i] == ks[i + 1])
        ab = sum(1 for i in range(len(ks) - 3) if ks[i] == ks[i + 2] and ks[i + 1] == ks[i + 3]
                 and ks[i] != ks[i + 1])
        spread = (max(d.values()) - min(d.get(l, 0) for l in "ABCD")) if ks else 0
        runs += r; abab += ab
        if len(ks) != 30 or r or ab or spread > 2:
            badbal += 1
            worst.append(f"{label}: n={len(ks)} spread={dict(sorted(d.items()))} repeats={r} ABAB={ab}")
    for x in worst:
        problems.append("key pattern in " + x)
    for x in model:
        problems.append("page model: " + x)
    if numbered and numbered != lines_listed:
        problems.append(f"contents: {lines_listed - numbered} line(s) list a heading the page model "
                        f"did not place — no page number could be printed for them")

    print(f"book      : {out_md.relative_to(ROOT)}  ({out_md.stat().st_size:,} bytes)")
    if out_dx:
        print(f"            {out_dx.relative_to(ROOT)}  ({out_dx.stat().st_size:,} bytes, "
              "landscape, two columns)")
    print(f"notes     : {notes} written · {len(want)} teaching weeks in the master")
    print(f"figures   : {len(plates)} plate(s) billed by the page model at their printed height"
          if plates else "figures   : none in this book")
    print(f"contents  : {parts} parts · {lessons} lessons · {numbered} of {lines_listed} lines carry "
          "a page number"
          + (f" · {info['pages']} pages, held by {info['breaks']} forced breaks, each planned to "
             f"{info['fill']:.0%} of its capacity" if info else " · markdown anchors only")
          + (" · the .docx adds a Word TOC field and a page number in the footer" if out_dx else ""))
    if out_dx:                                    # the numbers are only honest if the file obeys the plan
        from book_pages import audit_problems
        for x in audit_problems(a.cls, a.term, SUFFIX):
            problems.append("page numbers: " + x)
    print(f"papers    : {len([1 for p in sections if (BUILT / f'exam-{slug(a.cls)}__{slug(a.term)}__{p.stem}.md').exists()])}"
          f" of {len(sections)} · answer letters read from the key sidecars")
    if keylets:
        print(f"key shape : n={len(keylets)} " +
              " ".join(f"{l}={dist.get(l, 0)}" for l in "ABCD") +
              f" · consecutive-repeats={runs} · ABAB={abab}")
    if problems:
        print(f"\nPROBLEMS ({len(problems)}):")
        for x in problems[:40]:
            print("   -", x)
    else:
        print("\nrule checks: all clear — every teaching week has a note, every note has a worksheet "
              "and my own work, no note is written for a calendar week, nothing addresses a grown-up, "
              "no answer is printed anywhere, and every subject has its 30/10/5 paper.")
    if a.strict and (problems or runs or abab):
        sys.exit(1)


if __name__ == "__main__":
    main()
