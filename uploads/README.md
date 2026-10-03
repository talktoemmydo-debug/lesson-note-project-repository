# Mercy Model Schools — Curriculum Corpus

**Scope:** Nursery 2 → Primary 4 (5 classes × 3 terms) · **Last cleaned:** 31 August 2026
**Purpose:** one place to read everything needed to generate lesson notes and teaching schemes.

---

## The workspace is intentionally tiny — 6 files

### 1. `data/curriculum_master.json` — 🔑 THE master corpus
**The only data file that matters.** 11 subjects, 1,095 week-rows, all classes/terms/weeks:

| # | Subject | Weeks |
|---|---|---|
| 1 | Basic Science | 55 |
| 2 | Cultural and Creative Arts (CCA) | 56 |
| 3 | Christian Religious Studies (CRS) | 60 |
| 4 | Basic Digital Literacy | 56 |
| 5 | Nigerian History | 60 |
| 6 | Physical and Health Education (PHE) | 55 |
| 7 | Prevocational Studies (PVS) | 56 |
| 8 | Social and Citizenship Studies (SCS) | 56 |
| 9 | Yoruba (Ede, Asa, Litireso) | 65 |
| 10 | Mathematics & English (11 streams) | 396 |
| 11 | General Knowledge (10 pillars) | 180 |

Each subject carries: class → term → week rows (`kind: topic / calendar / blank`), teaching
content, calendar weeks (W7 Mid-Term, W10 Revision, W11 Examination, blank W12 where the
source had one), extra-topic blocks, the Yoruba class re-mapping, Maths & English NERDC
depth pointers, GK pillars + areas of concentration + current-affairs snapshot + Primary 5 bridge.

### 2. `data/scheme.json` — NERDC master extract (KEPT by instruction)
The extraction of the original 987-page NERDC 2025 PDF (297 sections, 99 subjects).
Used for **depth** when writing notes (it is the only version with full subtopics), and for the
`source_nerdc` pointers referenced inside the Mathematics & English data of the master.

### 3. `Curriculum-Master-Compilation.html` — readable edition of the master
Everything above, self-contained: Master Matrix, collapsible subjects, shaded calendar weeks,
Current Affairs snapshot, Primary 5 bridge, Source Map. Open this to browse.

### 4. `NERDC-2025-Scheme-Interactive.html` — NERDC interactive edition (KEPT)
The original NERDC work as a navigable web page — the reference backbone for note depth.

### 5. `General-Knowledge-Scheme-of-Work.docx` — the Word deliverable
The GK scheme as a Word document (the only Word file; its content also lives in the master).
Regenerable from the master if ever needed.

### 6. `README.md` — this index.

---

## What was removed (and why it's safe)

- **All source documents** (NERDC PDF, school weekly-9 HTML, Yoruba PDF, the 8 NC PDFs) —
  fully extracted into the master collection first.
- **All per-subject data JSONs** and **standalone HTML/Markdown editions** — programmatically
  verified cell-by-cell against the master before deletion: nothing lost.
- **All extraction/build scripts** — the originals no longer exist, so they were dead code.

## Fidelity notes (quirks preserved as printed)

- SCS source prints `PRIMARY OONE` → extracted as Primary 1; SCS Primary Two genuinely
  runs to a Week-12 teaching row (kept). Yoruba source has a W13 typo (normalised + logged)
  and no tone marks. Digital Literacy Primary 2 W6/W7 row shift (kept as printed).
  Blank W12 rows kept blank.
- Current-affairs facts are anchored **31 August 2026** — refresh for each new academic year.
