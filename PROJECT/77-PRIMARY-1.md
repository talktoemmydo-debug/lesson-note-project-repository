# 77 — Primary 1, First Term: the next class, subject by subject

The owner closed the Nursery 2 loop (three books shipped, backfill closed, teacher's copies built) and said,
2 Sep 2026: *"Continue to primary one ASAP."* The pipeline is class-agnostic — no new tools, just authoring
`notes/src/primary-1__1st-term/<subject>.md` and `data/exams/src/primary-1__1st-term__<subject>.txt`, then the
same gates. Weeks 1–6, 8 and 9 carry notes (week 7 Mid-Term; 10–12 Revision/Examination/Closing).

Run the subject exactly as Nursery 2: notes in the house shape at `polish_audit` **0 to fix**, one 30/10/5 paper
at `exploitable-longest: 0` and `sheet_lint` 0, worksheet letters shuffled so the spread is not skewed, then
`gates.py --class "Primary 1" --term "1st Term"` ending ALL CLEAR (book shows `[half]` until all subjects exist).

| # | subject | state |
| --- | --- | --- |
| 1 | basic-science | ✅ 8 notes · paper ✅ (30/10/5, A=7 B=8 C=8 D=7) · worksheets shuffled · gates ok |
| 2 | basic-digital-literacy | ✅ 8 notes · paper ✅ (30/10/5, A=8 B=8 C=7 D=7) · worksheets shuffled · gates ok |
| 3 | christian-religious-studies | ✅ 8 notes · paper ✅ (30/10/5, A=8 B=7 C=8 D=7) · exempt from plates |
| 4 | cultural-and-creative-arts | ✅ 8 notes · paper ✅ (30/10/5, A=7 B=8 C=7 D=8) · gates ok |
| 5 | general-knowledge | — (no plates owed, exempt) |
| 6 | nigerian-history | — (no plates owed, exempt) |
| 7 | physical-and-health-education | — |
| 8 | prevocational-studies | — |
| 9 | social-and-citizenship-studies | — (no plates owed, exempt) |
| 10 | yoruba | — (no plates owed, exempt) |
| 11 | mathematics-english | streams as in Nursery 2 (numeracy / letter work / language) |

The four word-only exemptions (Yoruba, General Knowledge, Nigerian History, Social & Citizenship Studies) and
CRS carry no plates in any term, Primary 1 included — they sit in `tools/backfill_ledger.py` EXEMPT.
