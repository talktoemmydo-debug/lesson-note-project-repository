# Roadmap — open work, with the first step already spelled out

Order is the owner's: **polish these two books → then a new class.** The teacher's copy was requested in
the same breath (2 Sep 2026). Images are scheduled last because they change the page model.

## 1. Teacher's copy, one per class-term — **built 2 Sep 2026** (`--edition teacher`), one gap owed

`tools/build_term_doc.py --edition teacher` now writes `notes/<Class> - <Term> - TEACHER COPY.{md,docx}` for all
three terms: the pupil pages plus, per subject, the term paper's key as *letter and answer text* and the Sections B & C
marking points, a "**TEACHER COPY — not for pupils**" line on the front, and a flipped gate — `--strict` no longer
demands "no answer" but the opposite, "every paper must have a key". The pupil no-answer gate is scoped to
`--edition pupil`, so a teacher file can never trip it and nobody is tempted to loosen it. All three build at
`--strict` exit 0 with 129/129 Contents numbers and the page audit clean, and the pupil edition is byte-for-byte
unaffected.

The one thing it does **not** carry is the answers to the 105 weekly worksheets per subject: those answers were
never stored as data (the shuffle tool deliberately "does not need to know which option is right"), so printing them
would mean guessing. That gap is recorded in `70-OPEN-QUESTIONS.md`; the teacher copy ships the worksheets as-is and
the verifiable paper keys, and gains worksheet keys only once they are authored as data.

* File: `notes/<Class> - <Term> - TEACHER COPY.docx` (+ `.md`), **outside** the pupil book, and named so
  nobody mistakes it for one. Not to be confused with `notes/_teacher-edition/`, which holds superseded
  teacher-*voiced* note drafts.
* Contents per subject: the 30/10/5 paper with every answer letter and answer text, the theory marking
  points (the key sidecars already carry them), and the answers to that subject's 105 weekly worksheets.
* Mechanically: reuse `build_term_doc.py`'s assembly but a `--edition teacher` mode that (a) appends each
  `data/exams/papers/exam-*.key.md`, (b) appends each note's worksheet with its answer, (c) **skips the
  pupil-facing "no answer key" gate and instead demands the opposite** — every paper in the book must
  have a key present. The five pupil rules stay, except the two about answers, and the file must print a
  "TEACHER COPY — not for pupils" line on the front so it cannot be handed out by mistake.
* Also: `tools/build_term_doc.py --strict`'s no-answers check must be scoped explicitly to
  `--edition pupil`, otherwise a teacher file will (correctly) fail and someone will loosen the check.
  Loosening the check is the one way this project could quietly ship keys into a child's book.

## 2. ~~Polish the two existing books~~ — **DONE 2 Sep 2026** (`reports/polish-2026-09-02.md`)

All four items landed except the Contents trim, which was declined on the grounds above. The measuring tool
(`tools/polish_audit.py`) stays in the chain: run it after authoring any subject, and it must print
`0 to fix`.

1. ~~One lesson per page~~ — **declined by the owner on 2 Sep 2026**: the flow stays as it is
   (packed pages, 142 and 123 pages, no never-split rule). `plan()` could take the flag someday, but it is
   not wanted work; do not re-propose it. The polish that *is* wanted is items 2–4 below, plus the two
   things the owner asked for in the same breath: the teacher's copy (this file §1) and the picture plan
   (this file §4).
2. **Contents: parts-only mode, or two-tier.** 129 lines is a wall for a Nursery 2 front matter; a
   24-line version (parts only) fits on one page and stays honest. Keep both generators, print the
   choice in the build report.
3. **Picture/drawing cues at Nursery 2 level.** Notes already say things like "Draw the box of a
   computer and put four labels on it" (`basic-digital-literacy.md:115`). Every worksheet should have one
   drawn or coloured item where the subject allows — but see §4: a cue that promises a picture must be
   matched by the page model reserving room for it.
4. Doc hygiene, already noticed: `make_exam.py`'s docstring says papers go to `build/` (they go to
   `data/exams/papers/`), `book_layout.py`'s docstring still says a word processor stamps the numbers
   (the plan does), `notes/README.txt` repeats the `build/` line and says "Next class: Primary 1", and
   `README.md` §5 still calls the First Term a 24-of-105-week pilot and cites a deleted
   `tools/renumber_keys.py`. Fixed on 2 Sep 2026 where spotted — re-check before trusting.

## 3. Then the next class — and, first, the rest of Third Term

**Third Term, Nursery 2 is already in progress**: see `75-THIRD-TERM.md` for the subject-by-subject table
and the loop. 97 notes and 12 papers remain. It is the proof that the plan works on a new term, so it
finishes before another class starts.

`notes/README.txt` names **Primary 1**; the owner has not confirmed which class (asked 2 Sep 2026).
The pipeline is class-agnostic: `data/curriculum_master.json` already covers Nursery 2 → Primary 4, so
the work is authoring `notes/src/<Class>__<term>/` and `data/exams/src/`, not new tools. Age-appropriate
item counts for a younger class (Nursery 1) would need the shape test in `sheet_check.py` parameterised
— currently 30/10/5 is hard-coded by spec.

## 4. Images — read `50-IMAGES.md` first, in full

Settled by the owner: embedded in the book, full children with faces, discard what fails, and the
**style is colouring-book line art** (2 Sep 2026), written as an exact prefix in `50-IMAGES.md`. What is
left of the blocking order, in sequence:

1. ~~owner picks a style~~ — done: line art, 2 Sep 2026, prefix written and probed;
2. ~~`tools/img_import.py`~~ — **built, 2 Sep 2026.**  Resize to 1200 px long edge, flatten to bilevel PNG
   (not JPEG: line art encodes to 4.8–14 kB this way, against 121 kB for the same picture as q84 JPEG),
   append the `MANIFEST.jsonl` line with the declared pixel size, delete the raw generation, then insert
   the `![alt](path)` line into the note at the end of `**Let us talk**`.  Refuses to overwrite a plate and
   `--check` reports any reference without a file or any file without a manifest row.
3. the QC gate — **done by eye, on purpose, for now.**  A contact sheet is built from the raw generations
   *after* they are flattened at the print threshold, so a grey fill that would print as a black blob is
   caught in the sheet rather than in the book.  What is checked: no pseudo-text anywhere, limbs and
   fingers complete, the object is the object the note names, figure/ground separation, and a consistent
   child across the subject.  Anything that fails is deleted in the turn that made it.  A script cannot
   yet tell a snail from a yam, so `tools/img_qc.py` is deliberately not written;
4. ~~the page model~~ — **built, 2 Sep 2026.**  `flow_of` emits `("image", path, alt)`; `image_pt()` reads
   the declared pixels from the manifest (the file is opened only if the manifest is silent) and returns
   the height a 12.5 cm figure needs — 193 pt for the house aspect, about a fifth of a page; `height()`
   bills it and `plan()` treats the item as unsplittable; `docx_out._figure` centres it at the same
   `IMAGE_WIDTH_CM`, so the width exists once; `--no-images` strips the references before the plan runs and
   was proven to leave a picture-free book byte-identical to the audited text-only one.
5. ~~only then: one subject's images as a pilot~~ — **in flight, 2 Sep 2026:** Second Term Basic Science,
   8 lessons (there is no week 7 note, it is Mid-Term Break), 8 plates, 90 kB inside a 315 kB book, 145
   pages instead of 143, 129/129 Contents numbers still agreeing with the file, `--audit` CLEAN,
   `polish_audit` still 0 to fix.
   then the rest of the term.

## 5. Housekeeping worth doing once

* `.git` exists in the workspace but **is not a repository** (`git rev-parse` → "not a git repository"),
  so none of this work has history. `git init` + one commit per verified build is cheap (the whole tree
  is 9.7 MB, mostly three large JSONs) and is the only guard against a bad `--all` regeneration.
* Two near-duplicate files sit in `notes/_teacher-edition/` (`basic-science.md` and
  `bs-teacher-edition-backup.md` are the same size, `bs-before.md` beside them) — archive or delete once
  the teacher's copy has a real home, per pruning rule 9.
