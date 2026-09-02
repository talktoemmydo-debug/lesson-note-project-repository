# Third Term, Nursery 2 — progress and the authoring loop

**Shape of the term (verified 2 Sep 2026):** 105 teaching weeks across 13 subject files, the same shape
as First and Second Term. Weeks 1–6, 8 and 9 for every subject; week 7 Mid-Term, 10 Revision,
11 Examination, 12 Closing carry no note — except Yoruba, whose week 11 the school prints as an
"Exam Preparation" teaching row, and Mathematics & English, which is three stream files (Numeracy,
Literacy, Language) of 8 weeks each. 13 papers at 30 objective + 10 sub-objective + 5 theory.

## Status

| subject file | notes | paper | sheet → spec → paper verified | plates |
| --- | --- | --- | --- | --- |
| basic-science | **8 ✅** | **30/10/5 ✅** | ✅ key `A=8 B=7 C=7 D=8`, no adjacency, no ABAB | **8 ✅** |
| cultural-and-creative-arts | **8 ✅** | **30/10/5 ✅** | ✅ key `A=7 B=7 C=8 D=8`, no adjacency, no ABAB, `sheet_lint` 0 | **8 ✅** |
| christian-religious-studies | **8 ✅** | **30/10/5 ✅** | ✅ key `A=8 B=7 C=8 D=7`, no adjacency, no ABAB, `sheet_lint` 0 | **8 ✅** |
| basic-digital-literacy | **8 ✅** | **30/10/5 ✅** | ✅ key `A=7 B=7 C=8 D=8`, no adjacency, no ABAB, `sheet_lint` 0 | **8 ✅** |
| nigerian-history | **8 ✅** | **30/10/5 ✅** | ✅ key `A=8 B=8 C=7 D=7`, no adjacency, no ABAB, `sheet_lint` 0 | **8 ✅** |
| physical-and-health-education | **8 ✅** | **30/10/5 ✅** | ✅ key `A=7 B=8 C=7 D=8`, no adjacency, no ABAB, `sheet_lint` 0 | **8 ✅** |
| prevocational-studies | **8 ✅** | **30/10/5 ✅** | ✅ key `A=7 B=8 C=8 D=7`, no adjacency, no ABAB, `sheet_lint` 0 | **8 ✅** |
| social-and-citizenship-studies | **8 ✅** | **30/10/5 ✅** | ✅ key `A=8 B=7 C=7 D=8`, no adjacency, no ABAB, `sheet_lint` 0 | **7 drawn** · word-only subject now, wk5 exempt |
| *scs week 5* | | | | **closed without a plate** — owner, 2 Sep 2026: *"Nigerian History and Social and Citizenship Studies need no images"*; the raw that was waiting was deleted and nothing is owed here |
| yoruba | **9 ✅** | **30/10/5 ✅** | ✅ key `A=8 B=8 C=7 D=7`, no adjacency, no ABAB, `sheet_lint` 0 on the first pass | **— none by the owner's word** |
| * Yoruba pictures * | | | *owner, 2 Sep 2026: "Yoruba doesn't need images"* — the subject is sound and word, not drawing | no plates, in any term |
| general-knowledge | **8 ✅** | **30/10/5 ✅** | ✅ key `A=8 B=7 C=8 D=7`, no adjacency, no ABAB, `sheet_lint` 0 on the first pass | **— none by the owner's word** |
| mathematics-english-numeracy | **8 ✅** | **30/10/5 ✅** | ✅ key `A=8 B=7 C=8 D=7`, no adjacency, no ABAB, `sheet_lint` 0 | **8 ✅** |
| mathematics-english-literacy | **8 ✅** | **30/10/5 ✅** | ✅ key `A=7 B=8 C=8 D=7`, no adjacency, no ABAB, `sheet_lint` 0 | **8 ✅** |
| mathematics-english-language | **8 ✅** | **30/10/5 ✅** | ✅ key `A=8 B=7 C=7 D=8`, no adjacency, no ABAB, `sheet_lint` 0 | **8 ✅** |

**The term is shut: 105 of 105 notes, 13 of 13 papers, 87 plates in the book.** It builds at **156 pages**
with **129 of 129** Contents lines numbered, `polish_audit` at `0 to fix · 3 to consider`, `key shape n=390 ·
A=99 B=96 C=98 D=97 · repeats 0 · ABAB 0`, `audit : CLEAN`, and `build_term_doc --strict` reports *rule checks:
all clear* — `gates.py` closes `ALL CLEAR` with no `[half]` on the build line.

**What the last subject taught the tools.** Three files share one subject (Numeracy, Letter Work, Language
Domain), and the build groups a file to a part by `bare(title)` — the title with its trailing bracket cut off.
`Mathematics & English · Literacy (Language Domain)` and `… · Literacy (Letter Work)` bare() to the same name, so
each part pasted **both** files in: the book carried 121 notes where 105 were written, and two papers printed
twice. The fix is First and Second Term's shape, now applied to all three Third Term files: one shared title
`# Mathematics & English — Nursery 2 · Third Term` plus a `**Stream: NUMERACY.**` (or `LITERACY — LETTER WORK`,
or `LITERACY — LANGUAGE DOMAIN`) line, which is what the part grouping, the sub-headings and the coverage audit
key off. Yoruba wk1/wk3 also lost four `the teacher says/asks` lines to the plan-voice rule: an action is
`called out`, a question `is asked`.

**The plate debt (re-derived by script, 2 Sep 2026, after four subjects were freed from pictures):**
`python3 tools/backfill_ledger.py` counts it out of `img_import --check` and writes `76-BACKFILL.md` — today
**95 plates owed over 12 files**: Second Term 23 (mathematics-english-numeracy 7, physical-and-health-education 8,
prevocational-studies 8) and First Term 72 (nine files at 8).  **Third Term owes nothing at all**: 105 notes,
13 papers, 87 plates, and its one open SCS gap is closed by the owner's word, not by a drawing.

**Two shapes of turn, and which to use.** A turn can carry either *one subject written and pictured*
(8 notes + 1 paper + 8 plates) or *one subject written plus the previous subject's plates*. Doing the second
here — PHE written, its eight plates left for the next turn's full window — keeps every subject's plates in
one unbroken generation run, which is easier to QC for a consistent child, and wastes nothing: three
generations were left unused rather than filing three of eight.

**The rate, measured, is one subject per turn**: 8 notes + 1 paper + 8 plates fits inside a turn, because the
image tool allows ten generations and a subject needs eight. Nine subjects of Third Term remain (Nigerian
History, PHE, PVS, SCS, Yoruba at 9, GK, and the three Mathematics/English streams), then about 200 pictures
to backfill into First and Second Term at the same rate.

**The plate column is not optional any more** (owner, 2 Sep 2026: the pictures are part of the polish, not a
later phase). Each note gets one plate at its `**Let us talk**` block — see step 2b of the loop and
`PROJECT/50-IMAGES.md`. Basic Science's eight are the sample already inside the Second Term book and CCA's eight are in the Third
Term book. **The ceiling is ten image generations a turn**, so a subject's pictures must be the first thing
made in a turn and not the last — CCA's first two plates were made beside eight others and the remaining six
had to wait a turn.

## The loop, one subject at a time

```bash
python3 tools/term_pack.py --class "Nursery 2" --term "3rd Term" --out reports/pack-nursery2-t3.md   # once
# 1. read that subject's weeks in the pack — the "MUST COVER" lines are the depth floor
# 2. write notes/src/nursery-2__3rd-term/<subject>.md in the house shape (see PROJECT/20-STYLE.md)
# 2b. one plate per note, from now on (the owner: pictures belong to the polish, 2 Sep 2026):
#     generate into /tmp, flatten-and-inspect as a contact sheet, delete what fails this turn, then
python3 tools/img_import.py --note notes/src/nursery-2__3rd-term/<subject>.md --week N --slug <slug> \
    --src /tmp/gen/x.png --alt "one plain sentence of what the child is shown"
# 3. write data/exams/src/nursery-2__3rd-term__<subject>.txt  — 30 + 10 + 5, correct option first
python3 tools/spec_from_lines.py --all --class "Nursery 2" --term "3rd Term"     # must print "13 of 13" at the end
python3 tools/sheet_check.py --class "Nursery 2" --term "3rd Term"               # "all sheets: 30/10/5"
python3 tools/polish_audit.py --class "Nursery 2" --term "3rd Term"              # "0 to fix"
for f in data/exams/nursery-2__3rd-term__*.json; do python3 tools/make_exam.py "$f" --seed 0 --strict; done
python3 tools/check_worksheets.py --class "Nursery 2" --term "3rd Term"
python3 tools/img_import.py --check                                        # "figures: CLEAN"
# when the 13th subject lands:
python3 tools/build_term_doc.py --class "Nursery 2" --term "3rd Term" --strict
python3 tools/book_pages.py --class "Nursery 2" --term "3rd Term"
```

**Correction, 2 Sep 2026.**  This row read `8 ✅` for basic-science's plates.  It was wrong, and the error was mine: eight pictures for **Second Term** basic-science exist in `assets/img/nursery-2/2nd-term/basic-science/`, and a summary grouped by subject name without checking the term, so their count was read into this term.  `img_import.py --check` now prints coverage per subject file — *"a note is finished when it carries its plate"* — and it says `3rd-term/basic-science: 0 of 8`.  Third Term's Basic Science notes were green, its eight plates were made in the turn that found the error, and `img_import --check` now reports `3rd-term` with no shortfall at all.

## Three traps I hit while writing the first subject — do not repeat them

1. **A worksheet item's options must not be bold.** Bolding the right option prints the answer in the
   pupil's book. `polish_audit.py` now fails on it (`worksheet item with a bolded option`), because I
   nearly shipped eight notes that way. The house rule: bold the *term* in a stem, never an option.
2. **The block header is `**Worksheet**` on its own line, asterisks and all.** If it is lost, the note
   silently has no worksheet block and `check_worksheets.py` counts n=0 — it did to me, via my own
   re-encoding script, and only the audit caught it.
3. **Do not write "solution", "marks", "answer" or a teacher-voice verb in a note.** `build_term_doc.py`
   reads a phrase like "the ORS solution the clinic gives" as mark-scheme text and refuses the book. Say
   "the ORS water the clinic gives". The full list is `PLAN_WORDS` in `tools/build_term_doc.py`.

4. **The `|| ` answer must not be the longest text on its line.** `sheet_lint.py` flags it and the flag is
   real: "leave the house and go to the person at the gate" against three short traps teaches a child that
   length = correct. Fix it by **thickening the traps** ("run back inside for our toys"), not by shortening
   the teaching — and keep the answer's wording identical to the note's, so it stays answerable from the
   lesson (mine is at `basic-science.md:143`).

Also: every `[objective]` stem must end in `___` or a question mark, and the `||` fields need a space on
both sides (`stem ___ || answer || trap || trap || trap`) — `sheet_check.py` warns on both.

## Still open when the notes are done

* **Worksheet letter spread**: at one subject in, the inference reports `n=10 A=2 B=4 C=4 D=0`. Wait
  until the term is complete, then run `shuffle_worksheet_options.py` **once** if the term is heavy.
* The **teacher's copy** (`60-ROADMAP.md` §1) must cover Third Term too — it reads the key sidecars, which
  are already being written for every T3 paper.
* **Pictures** (`50-IMAGES.md`) — the house line is set; the page model still has to learn image height
  before any picture goes into any book.
