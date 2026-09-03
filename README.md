# Mercy Model Schools — Lesson-Note Project (continued workspace)

**Rebuilt:** 1 September 2026 · **Last work:** 2 September 2026 · **Source of truth:** the three
files in `uploads/`, then the authored sources in `notes/src/` and `data/exams/src/`
**Status:** two complete class-term books shipped — `notes/Nursery 2 - {First,Second} Term.docx`, 105
notes and 13 papers each, Contents printed with page numbers, audits clean.
**If you are a fresh session: read `PROJECT/00-START-HERE.md` first — that folder holds this project's
context, style and history, written so that nothing else needs explaining.**
**Polished 2 Sep 2026** (`reports/polish-2026-09-02.md`, tool: `tools/polish_audit.py`) — 0 defects in both
books. **Third Term is in progress**: 8 of 105 notes and 1 of 13 papers, tracked in
`PROJECT/75-THIRD-TERM.md`; it is not shippable until the other 97 notes are authored.

---

## 0. Why this file exists

The previous workspace hit the 128 MB / 10,000-file budget and was abandoned. Only three artefacts
came over:

| uploaded file | what it is | role |
|---|---|---|
| `uploads/Curriculum-Master-Compilation (1).html` | the **approved sequence**: class → term → week → topic, Nursery 2 → Primary 4, 11 subjects | decides **what is taught, when** |
| `uploads/NERDC-2025-Scheme-Interactive.html` | the NERDC 2025 extract (987-pp PDF → interactive) with a `window.SCHEME_DATA` JSON payload inside | decides **how deep** each topic goes |
| `uploads/README.md` | the old workspace's index | describes files that **did not** survive |

`data/curriculum_master.json`, `data/scheme.json`, the `.docx` and all build scripts were **not**
re-uploaded. Both JSON files are recoverable from the HTML — see §1.

## 1. What was rebuilt (and how it was checked)

Run `bash tools/run.sh`: the whole layer regenerates from `uploads/` alone in ~10 s, deterministically.

### `data/scheme.json` — 100 % recovered (1.76 MB) · `tools/extract_scheme.py`
The NERDC HTML embeds its full dataset as `window.SCHEME_DATA`; it is parsed out verbatim.
**297 sections** (class × subject × term) · **29 subjects** · **3,854 week rows**, of which **3,812**
carry a detail column (`Content` / `Breakdown (Subtopics)` / `Teacher's Activities` / `Pupil's
Activities` / `Learning Resources` / `Materials`) — the depth pool · 24 frontmatter pages ·
**28 sample-lesson-note pages (pp 959–986)**, a complete worked note (Pre-Nursery Health Habits,
weeks 1–4, 7–10) — the only note-format exemplar available, and it survived inside the HTML.

### `data/curriculum_master.json` — recovered by re-parsing the readable edition (1.38 MB) · `tools/parse_master.py`
Every table cell re-derived verbatim with `kind: topic | calendar | blank` per row: the 11 subjects,
their `extra topics` / `Class re-mapping` blocks, Appendix A (current affairs), Appendix B (Primary 5
bridge) and the Source Map.

**Fidelity check against the old README — exact match on all 11 subjects:**

| subject | old | rebuilt | | subject | old | rebuilt |
|---|---|---|---|---|---|---|
| Basic Science | 55 | **55** | | PHE | 55 | **55** |
| CCA | 56 | **56** | | PVS | 56 | **56** |
| CRS | 60 | **60** | | SCS | 56 | **56** |
| Basic Digital Literacy | 56 | **56** | | Yoruba | 65 | **65** |
| Nigerian History | 60 | **60** | | Mathematics & English | 396 | **396** |
| | | | | General Knowledge | 180 | **180** |
| **total** | **1,095** | **1,095** | | | | |

(The 9 NC/Yoruba subjects count **table rows** — each row carries all three term columns — while M&E
and GK are already one row per stream/term. Expanded to one row per *class-term-week* the master
holds **2,133** cells: 1,479 teaching + 613 calendar + 41 blank.)

Quirks reproduced independently, unprompted — evidence nothing was lost:
**13** week-12 `blank in source` rows (CCA P4; CRS all 5; Digital Literacy N2; History N2–P4; PVS N2)
· the two stray `—` cells (Basic Science P4 2nd Term wk4, Nigerian History P4 3rd Term wk9) ·
**SCS Primary 2 running to a week-12 teaching row** · Yoruba 13-row terms with no tone marks · the
Yoruba re-mapping P1→N2 … P5→P4 with P6 dropped.

### `data/note_sources.json` — NEW: the depth layer the note writer consumes (1.75 MB)
`tools/build_note_sources.py`. One record per teaching week: the master row verbatim **plus** the
NERDC section/class/subject/term/week/page-range that sets its minimum depth, the atomised subtopic
lines, and how it was matched.

| outcome | rows | meaning |
|---|---|---|
| matched to NERDC depth | **1,214** | 99 % of the 1,224 rows that have a NERDC source at all |
| ↳ `upper-band-redistribution` | 239 | Digital Literacy + PVS, pulled from NERDC P4–P6 (your rule) |
| ↳ `nerdc-depth` | 975 | normal resolution |
| GK rows using the school's **own** breakdown as depth | 120 | the master's `Breakdown (Subtopics)` column is itself the depth |
| school-generated | **255** | Yoruba 135 + GK 120 — no NERDC lookup by design |
| no hit | **10** | listed in `reports/gaps.md`, needs manual depth |

**The re-mapping is now measured, not assumed.** Band offset of the depth actually found (positive =
NERDC teaches it in a *higher* class than the master row): `+1` **497** · `+2` **451** · `+3` **71** ·
`+5` **47** · `−1` 42 · `−2` 6 · `−3` 6 · **same band only 94**. A generator keyed on
"master class == NERDC class" would therefore miss ~92 % of the corpus.

**Independent check of the lost pointers — 48/48.** The compilation prints `Source (NERDC)` on the
**48** Primary 4 Mathematics & English rows (`Primary 5` ×24, `Primary 6` ×24; every other row prints
`—`). My independently re-derived pointers **agree with the school's own annotation on all 48** —
including the awkward ones (P4 W1–W4 → NERDC P5; P4 W5–W6/W8 `Fractions` → NERDC P6, where a
verbatim `Fractions` title also exists at P3 and must *not* win). That is the strongest available
evidence that both the recovered master and the depth layer behave like the lost JSON.

**Depth volume:** median 6 subtopic lines per row · p90 ~10 · **111 rows >16 lines** (over-loaded merged weeks, §5) ·
max 39 · a full render carries **11,946** depth lines (audit: 0 notes missing their depth, except the
10 gap rows).

## 2. What is genuinely NOT recoverable

1. **Per-row `teaching content` from the old master JSON** — the readable HTML renders topic strings
   only. **Mitigation:** prose is regenerated from the NERDC depth columns + the sample-note exemplar.
2. **The deep `source_nerdc` pointer strings** for Maths & English — only class-level labels survive
   in the HTML; the rest are re-derived (and validated above, 47/48).
3. The 987-page NERDC PDF, the 8 NC PDFs, the Yoruba PDF, the school `weekly-9` HTML,
   `General-Knowledge-Scheme-of-Work.docx`, **and your house lesson-note template** — the old README
   describes the data files but never fixes the note format.

## 3. Confirmed reading of the corpus relationship

* The master is **the NERDC scheme re-cut for this school**, not a copy: **shifted down a band**
  (NERDC P1/P2 → Nursery 2; P2 → P1; P5/P6 → P4), **merged** (NERDC's `…(Part 1)` + `…(Part 2)`
  printed as one school week; `FOOD: DEFINITION…` + `TYPES AND SOURCES` in one row), and
  **re-banded** (`BASIC SCIENCE AND TECHNOLOGY` → Basic Science + Digital Literacy + PVS;
  `HEALTH HABITS`/`SOCIAL HABITS`/`CIVIC EDUCATION` → PHE/SCS).
* **Digital Literacy and PVS are duplicated across bands**: the same content runs in N2 and P1 and
  their depth lives in NERDC P4–P6 (verified: master N2 "Understanding technology and digital
  devices. Types: computers, tablets, smartphones…" ↔ NERDC P4 F1 wk1–2 "Introduction to / History of
  Digital Devices"). Matching therefore runs on **content text**, upper bands only, for these two.
* **Yoruba and General Knowledge are school-generated** — the NERDC extract has 29 subjects and
  contains neither. Their notes are written from research, no NERDC floor.
* NERDC is the **minimum** extent of depth: a note may not go below what the matched NERDC week lists;
  the school's own wording decides the title and the boundary.
* **Calendar weeks never get notes**: W7 Mid-Term, W10 Revision, W11 Examination, W12
  Closing/Awards (compressed week-9: teaching runs weeks 1–6 and 8–9).
* Current-affairs facts in Appendix A are anchored **31 August 2026** → refresh each academic year.

## 4. Pilot (`notes/PILOT.md`) — 5 notes, one per structural edge case

1. **Ordinary in-band row** — Basic Science N2 T1 W1 *Our Body* (floor: NERDC N3, 8/8 subtopics)
2. **Band-shifted row** — M&E P1 Maths T1 W1 *Whole Numbers 1–100* (floor: NERDC **P2**; its opening
   line "Revision of Primary 1 work" re-pointed, see §5.1)
3. **Subject with no NERDC source** — Yoruba N2 T1 W1 (three strands Ẹ̀dá/Àṣà/Lítírèsọ̀ in one week;
   researched; flagged for the Yoruba teacher)
4. **School splits what NERDC merges** — CRS N2 T1 W1 *God the Creator (Part 1)* (Part 1 pinned to
   NERDC P1 W1; sibling weeks 2–3 correctly excluded because our W2 row carries them)
5. **Over-loaded merged week** — M&E P4 Maths T1 W1 (four NERDC P5 strands in one school week →
   planned as 3 periods)

## 5. Output format (the school's rules, now fixed)

One document **per class per term**, covering every subject offered to that class —
`notes/<Class> - <Term>.md`. Inside it: one note per teaching week, and after each
subject its **term practice paper: 30 objective + 10 sub-objective + 5 theory**.

* **No note for calendar weeks** (Mid-Term, Revision, Examination, Closing).
* **Every lesson note carries an exam-style worksheet** for that lesson.
* **Assignments never address a parent or guardian** — the pupil works them alone.
  `build_notes.py` refuses to render a parent-facing assignment, `build_term_doc.py`
  flags one in an authored section.
* **The book opens with a Contents page that carries page numbers.** Every part (each subject, each
  term practice paper) and every teaching week is listed, read off the headings of the assembled book,
  so the list cannot drift. The numbers are not a forecast of what Word will do:
  `tools/book_layout.py` packs the paragraphs into pages against a deliberately pessimistic budget
  (90 % of the ~1043 pt a two-column A4 page holds), and `tools/docx_out.py` writes a **forced page
  break at every boundary the plan names** — Word is left no page of its own to choose, so a printed
  number is arithmetic, not an estimate. The same file carries a Word `TOC` field over real Heading
  styles (so Word refreshes the list and the Navigation pane works) and a `Page N` footer field.
  `build_term_doc.py --strict` fails if a listed entry points at no heading, if a part is missing from
  the list, if a page is over its budget, or if the numbers and the breaks in the written .docx
  disagree. `python3 tools/book_pages.py --class ... --term ...` re-runs that audit alone; add
  `--render` where LibreOffice exists to compare the plan with a real layout engine.
* **No pattern in the objective keys.** `tools/make_exam.py` authors the *answer text*
  and assigns the letter itself: balanced across A–D, never twice in a row, no ABAB,
  and it fails if the correct option is clearly the longest in more than 6 items of the 30 — that
  is exactly what would reward "always pick the longest".
  The per-lesson worksheets are hand-written next to the prose and get the same treatment from the
  other side: `sheet_lint.py` finds the lines whose right option is the long one, `patch_lines.py`
  rewrites them, `check_worksheets.py` reports the term's letter spread, and
  `shuffle_worksheet_options.py` re-orders options when a term comes out skewed (run once — it is not
  idempotent, and it edits the notes in place).

Authored sections live in `notes/src/<Class>__<term>/<subject>.md`; the document is
assembled and audited by `tools/build_term_doc.py`. Two books are complete and current:
`notes/Nursery 2 - First Term.md` and `notes/Nursery 2 - Second Term.md` — 105 notes each (every
teaching week; weeks 7/10/11/12 carry no note) and 13 papers each at 30 + 10 + 5. A teacher's copy
carrying the keys is wanted and not yet built: see `PROJECT/60-ROADMAP.md` §1.

## 6. Budget discipline

What killed the last workspace: per-subject JSONs + standalone HTML/MD editions + DOCX + build
intermediates. Rule here: **one JSONL per subject-class-term, never one file per note**, and nothing
Current footprint: **9.7 MB / 180 files** (about 8 % of the byte budget, 2 % of the file budget);
a full 1,479-note render is ~4 MB / 165 files and takes 5 seconds. **Pictures are the risk to this
number** — measured on 2 Sep 2026. The house style is colouring-book line art, and line art
survives being flattened to a 1-bit PNG: **~17 kB each, about 1.8 MB for a class-term's 105
images**. The coloured alternatives the owner compared would have cost 9.7–30.2 MB a term, and
raw model output costs 0.3–3 MB *per picture* — which is what actually breaks a workspace. The
ceiling, the naming, the manifest, the discard rule and the size math are in
`PROJECT/50-IMAGES.md`; nothing may be generated before reading it.
`PROJECT/50-IMAGES.md`; nothing may be generated before reading it.

## 7. Files

```
README.md                      this index
PROJECT/                       START HERE for a fresh session: 00-START-HERE, 10-BRIEF, 20-STYLE,
                               30-ARCHITECTURE, 40-HISTORY, 50-IMAGES, 60-ROADMAP
notes/<Class> - <Term>.{md,docx}  the shipped books (generated — edit the sources, never these)
notes/src/<Class>__<term>/       the authored notes, one file per subject
data/exams/                    question sheets (src/), specs (.json), rendered papers (papers/)
tools/book_layout.py            the page model the Contents numbers come from
data/scheme.json               NERDC extract (297 sections, 3,854 weeks, sample notes)
data/curriculum_master.json    recovered master corpus (11 subjects, 1,095 rows)
data/note_sources.json         depth resolved per teaching week (1,479 records)
reports/gaps.md                the 10 unresolved rows + thin ones
notes/PILOT.md                 5 hand-written pilot notes
tools/run.sh                   rebuild everything in ~10 s
tools/{extract_scheme,parse_master,build_note_sources,build_notes}.py
uploads/                       the three files you carried over (untouched)
```
