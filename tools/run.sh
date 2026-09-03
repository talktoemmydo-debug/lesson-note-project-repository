#!/usr/bin/env bash
# Full rebuild of the data layer from uploads/ alone. Deterministic.
set -euo pipefail
cd "$(dirname "$0")/.."
python3 tools/extract_scheme.py          # NERDC HTML  -> data/scheme.json
python3 tools/parse_master.py            # master HTML -> data/curriculum_master.json
python3 tools/build_note_sources.py      # both        -> data/note_sources.json + reports/gaps.md
python3 tools/build_notes.py --all --audit   # depth     -> notes/*.jsonl
# ---- the book itself (pupil edition) -------------------------------------
# python3 tools/build_term_doc.py --class "Nursery 2" --term "1st Term" --strict
#   reads notes/src/<Class>__<Term>/*.md, appends each subject's term paper from build/,
#   writes notes/<Class> - <Term>.md and the .docx (A4 landscape, two columns), then checks the
#   school's rules: a note for every teaching week and none for a calendar week, a worksheet and a
#   piece of my own work in every note, no answer key, no deputation of a parent or a teacher,
#   30/10/5 per subject and patternless answer letters. See notes/README.txt for the paper pipeline.
