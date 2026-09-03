# Primary 2 · Third Term — subject-by-subject tracker

Pipeline is class-agnostic (see `80-AUTOLOOP.md` §6). One subject per turn:
author `notes/src/primary-2__3rd-term/<subject>.md` + `data/exams/src/primary-2__3rd-term__<subject>.txt`,
run the gates, mark the row, append `40-HISTORY.md`, commit + push.

Teaching weeks and topics are taken straight from `data/curriculum_master.json` (Primary 2 · 3rd Term)
via `build_term_doc.week_titles` — the master carries real topics for every subject this class, so notes
follow the scheme topics below. 98 teaching weeks in total.

| # | subject | teaching weeks | state |
| --- | --- | --- | --- |
| 1 | basic-science | 1-6, 8, 9 | ✅ 8 notes · paper ✅ (30/10/5, A=7 B=8 C=7 D=8) · sheet_lint 0 · polish 0-to-fix · gates ok |
| 2 | basic-digital-literacy | 1-6, 8, 9 | ✅ 8 notes · paper ✅ (30/10/5, A=8 B=7 C=7 D=8) · sheet_lint 0 · polish 0-to-fix · gates ok |
| 3 | christian-religious-studies | 1-6, 8, 9 | — |
| 4 | cultural-and-creative-arts | 1-6, 8, 9 | — |
| 5 | general-knowledge | 1-6, 8, 9 | — |
| 6 | nigerian-history | 1-6, 8, 9 | — |
| 7 | physical-and-health-education | 1-6, 8, 9 | — |
| 8 | prevocational-studies | 1-6, 8, 9 | — |
| 9 | social-and-citizenship-studies | 1-6, 8, 9, 12 | — |
| 10 | yoruba | 1-6, 8, 9, 11 | — |
| 11 | mathematics-english | MATH 1-6, 8, 9 · ENG 1-6, 8, 9 | — |

Plate exemptions (Yoruba, GK, Nigerian History, SCS, CRS) carry no plates — `tools/backfill_ledger.py` EXEMPT.

## Scheme topics (author to these)

- **basic-science** — Change in Nature; Development change in plants; Growth and development change in animals; Exploring water in our environment; Human body: the mouth, teeth and tongue; Human body: the teeth; Non-living things: rocks; Properties of living and non-living things.
- **basic-digital-literacy** — Phishing awareness; Cyberbullying; Inclusivity in digital content creation; Basics of programming; Introduction to Scratch; Coding with Scratch I; Coding with Scratch II; Sequence in programming.
- **christian-religious-studies** — Jesus prayed to the Father; Jesus gives his life for us on the cross; Jesus gives us a new life (1-3); The Holy Spirit our guide (1-3); Gifts of the Holy Spirit; Living as God's children.
- **cultural-and-creative-arts** — Introduction to art; Nigerian arts; Drawing; Printing; Modelling; Crafts and design; Weaving; Art tools and equipment.
- **general-knowledge** — Money and shopping: the naira and kobo; Markets, trade and work; Great Nigerians II: writers, scientists and artists; World history stories: ancient times; Transport and travel in the world; Important days in Nigeria and the world; Current affairs I: news for young Nigerians; End-of-year GK challenge and quiz olympics.
- **nigerian-history** — The local government chairperson; Leadership quality; Geography and environment (1-2); Nigerian peoples (1-3); Traditional rulers and governance; Family and community living.
- **physical-and-health-education** — Health and hygiene; Athletics III throwing; Athletics IV relay races; Ball games II football basics; Ball games III basketball basics; Ball games IV volleyball basics; Swimming I water safety; Swimming II basic skills.
- **prevocational-studies** — Introduction to animal husbandry; Caring for animals; Kitchen safety I & II; School garden activities; Simple vegetable growing; Nutrition basics; Being helpful at home.
- **social-and-citizenship-studies** — Money and the value of money; Using money wisely; Important phone numbers and their uses; Finding help and protection; Neighbourhood security; Responding to accidents; Peer behaviour and decision making; Introduction to drug abuse; Consequences of trafficking in persons.
- **yoruba** — Àròpò orúkọ àfàrajorúkọ; Ìṣẹ́ ọnà ṣíṣe; Orin àkọ́mọ̀nìwà; Ònkà; Ìpolowo ọjà; Ìmọ̀ ẹ̀rọ kọ̀mpútà; Ìrànwọ́ ara ẹni; Àlọ àpamọ̀; Ìkíní; Ìwò fawẹli; Ìmọ́tótó; Ìró kọ̀ǹsónántì; Àwò oríṣiríṣi; Ìtàn àròsọ; Ònkà 181-200; Orúkọ àmútọ̀runwá; Ẹ̀yà ara ìfọ̀; Kòkòrò àìfojúrí.
- **mathematics-english · MATHEMATICS** — Open sentences; Money; Length; Time; Weight; Capacity; Symmetry; Pictograms.
- **mathematics-english · ENGLISH LANGUAGE** — Reading & grammar; Writing & grammar (1); Reading & comprehension; Grammar & speaking; Grammar & writing; Reading & listening; Writing & grammar (2); Reading & concepts of print.

## Books

| Book | Status |
| --- | --- |
| Pupil copy | — |
| Teacher copy | — |
