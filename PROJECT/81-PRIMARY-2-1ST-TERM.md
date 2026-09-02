# Primary 2 · First Term — subject-by-subject tracker

Pipeline is class-agnostic (see `80-AUTOLOOP.md` §6). One subject per turn:
author `notes/src/primary-2__1st-term/<subject>.md` + `data/exams/src/primary-2__1st-term__<subject>.txt`,
run the gates, mark the row, append `40-HISTORY.md`, commit + push.

Week shapes are taken straight from `data/curriculum_master.json` (Primary 2 · 1st Term) and vary by
subject. Topic cells are empty for every subject except maths-english, so notes are authored from the
NERDC scheme but must cover exactly the master's teaching weeks.

| # | subject | teaching weeks | state |
| --- | --- | --- | --- |
| 1 | basic-science | 1-6, 8, 9 | ✅ 8 notes · paper ✅ (30/10/5, A=8 B=7 C=7 D=8) · sheet_lint 0 · gates ok |
| 2 | basic-digital-literacy | 1-5, 7, 8, 9 | ✅ 8 notes · paper ✅ (30/10/5, A=7 B=8 C=8 D=7) · sheet_lint 0 · gates ok |
| 3 | christian-religious-studies | 1-6, 8, 9 | ✅ 8 notes · paper ✅ (30/10/5, A=7 B=8 C=7 D=8) · sheet_lint 0 · exempt from plates · gates ok |
| 4 | cultural-and-creative-arts | 1-6, 8, 9 | ✅ 8 notes · paper ✅ (30/10/5, A=8 B=7 C=7 D=8) · sheet_lint 0 · gates ok |
| 5 | general-knowledge | 1-6, 8, 9 (term-stream layout; topics: states & capitals, government, symbols, history, heroes) | ✅ 8 notes · paper ✅ (30/10/5, A=7 B=8 C=8 D=7) · sheet_lint 0 · exempt from plates · gates ok |
| 6 | nigerian-history | 1-6, 8, 9 | ✅ 8 notes · paper ✅ (30/10/5, A=7 B=7 C=8 D=8) · sheet_lint 0 · exempt from plates · gates ok |
| 7 | physical-and-health-education | 1-6, 8, 9 | ✅ 8 notes · paper ✅ (30/10/5, A=8 B=8 C=7 D=7) · sheet_lint 0 · gates ok |
| 8 | prevocational-studies | 1-6, 8, 9 | — |
| 9 | social-and-citizenship-studies | 1-6, 8, 9, 12 | — |
| 10 | yoruba | 1-6, 8, 9 | — |
| 11 | mathematics-english | MATH 1-6, 8 · ENG 1-6, 8, 9 | — |

Plate exemptions (Yoruba, GK, Nigerian History, SCS, CRS) carry no plates — `tools/backfill_ledger.py` EXEMPT.

## Books

| Book | Status |
| --- | --- |
| Pupil copy | — |
| Teacher copy | — |
