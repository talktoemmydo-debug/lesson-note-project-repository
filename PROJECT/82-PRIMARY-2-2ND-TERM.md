# Primary 2 · Second Term — subject-by-subject tracker

Pipeline is class-agnostic (see `80-AUTOLOOP.md` §6). One subject per turn:
author `notes/src/primary-2__2nd-term/<subject>.md` + `data/exams/src/primary-2__2nd-term__<subject>.txt`,
run the gates, mark the row, append `40-HISTORY.md`, commit + push.

Teaching weeks and topics are taken straight from `data/curriculum_master.json` (Primary 2 · 2nd Term)
via `build_term_doc.week_titles` — the master carries real topics for every subject this class, so notes
follow the scheme topics below. 98 teaching weeks in total.

| # | subject | teaching weeks | state |
| --- | --- | --- | --- |
| 1 | basic-science | 1-6, 8, 9 | ✅ 8 notes · paper ✅ (30/10/5, A=7 B=7 C=8 D=8) · sheet_lint 0 · gates ok |
| 2 | basic-digital-literacy | 1-6, 8, 9 | ✅ 8 notes · paper ✅ (30/10/5, A=7 B=7 C=8 D=8) · sheet_lint 0 · gates ok |
| 3 | christian-religious-studies | 1-6, 8, 9 | ✅ 8 notes · paper ✅ (30/10/5, A=7 B=7 C=8 D=8) · sheet_lint 0 · exempt from plates · gates ok |
| 4 | cultural-and-creative-arts | 1-6, 8, 9 | ✅ 8 notes · paper ✅ (30/10/5, A=8 B=7 C=8 D=7) · sheet_lint 0 · gates ok |
| 5 | general-knowledge | 1-6, 8, 9 | ✅ 8 notes · paper ✅ (30/10/5, A=8 B=7 C=7 D=8) · sheet_lint 0 · exempt from plates · gates ok |
| 6 | nigerian-history | 1-6, 8, 9 | ✅ 8 notes · paper ✅ (30/10/5, A=8 B=7 C=8 D=7) · sheet_lint 0 · exempt from plates · gates ok |
| 7 | physical-and-health-education | 1-6, 8, 9 | — |
| 8 | prevocational-studies | 1-6, 8, 9 | — |
| 9 | social-and-citizenship-studies | 1-6, 8, 9, 12 | — |
| 10 | yoruba | 1-6, 8, 9, 11 | — |
| 11 | mathematics-english | MATH 1-6, 8, 9 · ENG 1-6, 8, 9 | — |

Plate exemptions (Yoruba, GK, Nigerian History, SCS, CRS) carry no plates — `tools/backfill_ledger.py` EXEMPT.

## Books

| Book | Status |
| --- | --- |
| Pupil copy | — |
| Teacher copy | — |
