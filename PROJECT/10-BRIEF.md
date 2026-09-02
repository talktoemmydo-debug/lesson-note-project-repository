# The brief — what the owner requires, in their terms

## The task, standing

For each class-term: assemble the **whole term's teaching notes for every subject that class offers**,
in the school's format, and append **one end-of-term practice paper per subject** made of
**30 objective + 10 sub-objective + 5 theory** items. Deliver as a single `notes/<Class> - <Term>.docx`
plus its `.md` twin. Any new class-term starts by authoring the *notes* in `notes/src/` and the *item
text* in `data/exams/src/` — never by editing a rendered file.

Second Term Nursery 2 is the reference quality bar; First Term is held to the same bar. New work is
judged against them.

## Never, in a pupil-facing document

Enforced by `tools/build_term_doc.py --strict`, which fails the build. Not style preferences — gates.

1. **No answers, keys, marking guidance, or solution hints** anywhere in the book or its `.md`. The key
   lives only in `data/exams/papers/*.key.md`, which is never copied into a book.
2. **Nothing addresses a grown-up.** No "parent", "guardian", "mum or dad", "please help at home",
   "dear teacher". The pupil works alone. Assignments are written *to the child*.
3. **No note for a calendar week.** Mid-Term Break, Revision, Examination and Closing weeks are on the
   school calendar but carry no lesson note. A note that exists for one of those weeks is a bug.
4. **Every note carries both** a `**Worksheet**` block and a `**My own work**` block. No exceptions.
5. **No pattern a child can exploit in the objective key.** No letter twice running across the paper,
   no ABAB, A–D balanced within tolerance, and the correct option must not clearly stand out as the
   longest in more than 6 items of the 30 (`make_exam.py`'s threshold) — otherwise "always pick the
   longest" answers the paper. `make_exam.py --strict` prints `consecutive-repeats=0 · ABAB=0 ·
   exploitable-longest: 0 (slight: N)` and fails on any of the first two being non-zero.

## Also required

* Every teaching week in the master must have exactly one note; every note must be findable in the book.
* Headings are `WEEK n — TITLE` in caps so the Contents and the Word TOC can be generated from them.
* The book opens with a **Contents page listing every part and every week with its page number**
  (added at the owner's request; it is a pupil feature, so it must be readable and it must be *true*).
* Reading level: Nursery 2 is roughly age 5–6. Short sentences, one instruction at a time, familiar
  nouns. The child, not the curriculum, decides the vocabulary.
* Items must be answerable from the notes of that term — the paper is a check on teaching, not a
  surprise. Cross-check: `tools/sheet_check.py` reports whether every answer text appears in the notes.

## Acceptance test for "done"

All four commands in `00-START-HERE.md` green, plus `python3 tools/book_pages.py --class ... --term ...`
printing `audit : CLEAN`. A book is not "done" because the files exist; it is done when a build from
scratch reproduces them with those lines.

## Scope decisions on record

| decision | status |
| --- | --- |
| Two-column A4 landscape, Calibri 10.5, 0.7 cm gutter | confirmed by owner 2 Sep 2026 |
| Papers only inside the book | confirmed 2 Sep 2026 |
| Separate teacher's copy with keys and marking guidance | wanted by owner, not yet built |
| Polish these two books, then a new class | confirmed 2 Sep 2026 |
| Rebalancing the *delivered* First Term sheets | allowed (owner's instruction; reversed an earlier "leave it alone") |
| Third Term Nursery 2 | not commissioned yet — ask before starting |
