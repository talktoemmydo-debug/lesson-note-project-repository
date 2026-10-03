# Architecture — the machinery, and which layer to edit

## The rule that keeps everything honest

**Sources are hand-written; books are generated. Never edit `notes/<Class> - <Term>.{md,docx}` or
`data/exams/papers/exam-*.md` — they are outputs and the next build overwrites them.** Every artefact
below is reproducible from the layer above it, which is why `--strict` can be trusted as proof.

```
uploads/NERDC-2025-Scheme-Interactive.html      the depth of every topic (window.SCHEME_DATA payload)
uploads/Curriculum-Master-Compilation (1).html  what is taught, when: class → term → week → topic
        │  extract_scheme.py · parse_master.py · build_note_sources.py      (research layer, ~10 s)
        ▼
data/scheme.json · data/curriculum_master.json · data/note_sources.json · reports/gaps.md
        │  tools/show.py "Basic Science" "Nursery 2" 3 "2nd Term"   ← read one week's depth
        ▼  AUTHORED BY HAND (this is the real work)
notes/src/<Class>__<term>/<subject>.md          105 lesson notes, one file per subject
data/exams/src/<class>__<term>__<section>.txt   hand-written question sheets, one item per line
        │  spec_from_lines.py --all              sheet → spec JSON   (⚠ drops malformed lines silently)
        ▼
data/exams/<class>__<term>__<subject>.json       {stem, answer, distractors} per item
        │  sheet_lint.py → patch_lines.py        kill the "pick the longest" tell
        │  sheet_check.py                        30/10/5, every item well formed
        │  make_exam.py <spec> --seed 0 --strict  assigns answer letters, writes the paper + key
        ▼
data/exams/papers/exam-<name>.md  (+ .key.md, the key — NEVER printed in a book)
        │  build_term_doc.py --class … --term … --strict
        ▼
notes/<Class> - <Term>.md      the working copy, Contents stamped with page numbers
notes/<Class> - <Term>.docx    the printed book  (A4 landscape, two columns)
```

## Each tool's job

| tool | does |
| --- | --- |
| `book_layout.py` | the **single source of truth for flow and pagination**: `flow_of(md)` classifies every line into `h1/h2/h3/h4/toc/num/bullet/opt/label/para/rule`; `height()` prices a paragraph in points; `plan(flow)` packs the book into pages and returns `heading → page`, the set of forced page breaks, and problems; `stamp_contents()` writes ` · N` into the md Contents; `numbered_flow()` does the same in memory for the renderer. `python3 tools/book_layout.py <book.md>` prints that book's plan summary. |
| `docx_out.py` | renders md → .docx. **Writes a page break at exactly the indices `plan` names and nowhere else**, splits the Contents field where the plan breaks inside the list, applies the house styles, adds the live `TOC` field and the `Page {PAGE}` footer. |
| `build_term_doc.py` | assembles and **validates**: note/paper coverage, the five never-rules, Contents↔heading agreement, page budget, then the post-render audit of the written .docx. `--nodocx` skips the file. `--strict` turns any problem into a non-zero exit. |
| `book_pages.py` | reads the finished .docx without any Word/LibreOffice: counts `<w:br w:type="page"/>` and compares the break structure with the numbers printed in the Contents. `--audit` (default) · `--model` (page-fill distribution vs budget) · `--render` (cross-check with LibreOffice **where it exists**; prints "skipped" here). |
| `make_exam.py` | the only author of answer letters: balanced A–D, no double letters, no ABAB, right option not the longest in >6 items, then writes the paper and the key sidecar. |
| `spec_from_lines.py` / `_rev.py` / `spec_from_paper.py` | sheet ↔ spec, in both directions (the reverse ones are for recovering a sheet from a rendered paper). |
| `sheet_lint.py` | flags lines where the right option is much longer than its traps → re-word with `patch_lines.py`. |
| `polish_audit.py` | grades the authored **notes** (not the papers): block completeness and item counts,
  a line too long for a five-year-old's ear, grown-up register, nothing for the hands to draw or cut, a
  repeated bullet, a bolded worksheet option. `0 to fix` is the shipped state; `shape:` and
  `worth a look` lines are reported and not refused. |
| `gates.py` | the whole proof in one command, cheapest first: manifest, note audit, sheets, papers,
  worksheets, the build (its `--strict` refusal of an unfinished term is reported as `[half]`, never as a
  failure), then the .docx.  Exits 0 only on `ALL CLEAR`.  This is how a turn is closed. |
| `img_import.py` | one plate from a raw generation into the book: flatten bilevel at ≤1200 px, file it at
  `assets/img/<class>/<term>/<subject>/week<n>-<slug>.png`, declare its pixels in `MANIFEST.jsonl`, delete
  the raw, then write the `![alt](path)` line into the note at the end of `**Let us talk**`.  Never
  overwrites.  `--check` reports a reference without a file, a file without a manifest row, or a row whose
  file was deleted — the picture side of `book_pages`. |
| `sheet_check.py` | per class-term: section sizes and item shape. |
| `check_worksheets.py` | the notes' own worksheets: infers which option is correct and reports the term's letter spread. |
| `shuffle_worksheet_options.py` | deterministic re-lettering of worksheet options; run **once**, only when the spread is bad — it edits the notes in place. |
| `build_notes.py`, `build_note_sources.py`, `extract_scheme.py`, `parse_master.py` | the research/bulk layer: the old `data/*.json → notes/*.jsonl` route for a 1,479-note render. Not the shipped path, but it is what tells you a week's depth. |
| `term_pack.py`, `templates/house.md` | print the teaching pack for a class-term; the house note template. |

## The page model, in one paragraph (the subtle part)

Word decides where pages break, and nothing printed by hand can know what it decided. So the pipeline
removes the choice: `book_layout.plan()` measures every paragraph against `COLUMN = 521.6 pt` wide,
`LINE = 13.45 pt`, 2 pt after each paragraph, real heading heights, and fills each page only to
**90 %** of the 1,043 pt a two-column A4 page actually holds; it treats a heading or a `**Worksheet**`
label as *sticky* (its next real item must fit on the same page, because Word's keep-with-next would
otherwise push it down and silently add a page the Contents does not know about); and it reports a
single paragraph taller than a page as a **problem**, not an overflow. `docx_out` then hard-breaks the
document at those boundaries. Result: the number in the Contents is arithmetic over the same breaks the
file contains, and the 10 % reserve means Word can never find a page of its own. Pages are derived from
the break set — `break_before(i)` no-ops if index `i` already opens a page, and that one-line rule is
the difference between correct numbers and every number being one page late.

## Two traps that will bite an editor

* **`build/` is not persisted** between sessions (and neither are caches or `node_modules`-style dirs).
  Papers are therefore written to `data/exams/papers/`; `make_exam.py`'s docstring still says `build/`
  and `notes/README.txt` repeats it — both stale, the code path is `data/exams/papers` (`BUILT`).
* **Patching a `.py` file from inside a Python string** (a `write_file` on generated source) can splice
  a file in half without complaining. After any edit to `tools/*.py` made this way, run
  `python3 -c "import ast,pathlib;ast.parse(pathlib.Path('tools/X.py').read_text())"`.
