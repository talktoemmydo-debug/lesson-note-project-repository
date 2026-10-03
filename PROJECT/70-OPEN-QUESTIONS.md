# Decisions on record, and the questions still open

The answer picker dropped once (2 Sep 2026 — the owner answered, the responses arrived empty). So this
file is the durable copy: **answers can be typed straight into the chat, or written into this file.**
Whatever lands here is authoritative for the next session, which should not re-ask what is answered.

## Answered — these are settled, do not re-open

| # | question | the owner's answer | where it bites |
| --- | --- | --- | --- |
| A | How the book reaches the children | **Keep as-is**: A4 landscape, two columns | `docx_out.py`, `book_layout.py` — no portrait/phone edition |
| B | The 13 practice papers | **Only inside the book** | no per-subject files, no separate exam pack |
| C | The answer keys | **Yes — a separate teacher's copy per term**, with keys, marking guidance and the worksheet answers | `60-ROADMAP.md` §1; the pupil book stays key-free |
| D | Where the next stretch of work goes | **Polish these two books, then the next class** | `60-ROADMAP.md` §2 then §3 |
| E | Contents page numbers | Wanted, and they must be real references | already shipped and audited |
| F | Rebalancing the delivered First Term sheets | Allowed (reversed an earlier "leave it alone") | already done, `lines to re-balance: 0` |

## The four questions, and where each stands

**1 · The image style — ANSWERED: `1 · colouring-book line art`** (2 Sep 2026, chosen from four
samples of one identical concept). The house line is written down in `50-IMAGES.md` as an exact prompt
prefix, so all 105 images share it; the four samples stay in `assets/samples/` as the reference for what
was rejected as well as what was taken. Cost, because line art survives a 1-bit PNG: about **1.8 MB** for a class-term's 105 images (measured 17 kB each at print size), not the 17.5 MB the same images cost as JPEG.

**2 · Small children in the pictures — ANSWERED: `full`, faces and all.** In the owner's words: *"Full
children, faces and all. However, double check for errors and correct. Discard the ones that are not
useful immediately to keep the workspace clean."* That is why `50-IMAGES.md` rule 6 is a
generate-inspect-discard loop in the same turn, and why rule 4 forbids generated pseudo-text.

**3 · Where the pictures go — ANSWERED: `embed`, inside the book.** Which makes rule 7 (the page model
must bill an image's height in points before any image ships) the first engineering task, not an
afterthought.

**4 · One lesson per page — ANSWERED: `as-is`.** Leave the flow packed; no forced break per lesson and
no "never split a lesson" rule. The Contents already points at every lesson, and the books stay 142 and
123 pages. `60-ROADMAP.md` §2 is amended to match — do not re-propose it.

## Also answered, so nobody re-asks

| # | question | answer |
| --- | --- | --- |
| A | layout | A4 landscape, two columns, as-is |
| B | the 13 papers | stay inside the book |
| C | keys | yes, a separate **teacher's copy** per term |
| D | order of work | polish these two books, then the next class |
| E | Contents | numbered, and the numbers must be real |
| F | First-Term rebalance | allowed, and done (`lines to re-balance: 0`) |

## Still to be asked of the owner (not blocking)

1. **Which class next** — `notes/README.txt` has said Primary 1 for a while; the alternative on the table
   was Nursery 1 (younger, and the pipeline would need the 30/10/5 shape parameterised for it).
2. **Third Term Nursery 2** — never commissioned. Ask before starting; it is 105 notes and 13 papers.
3. **Whether old classes' images ship out of the workspace** once a second class-term of pictures exists
   (`50-IMAGES.md` rule 10) — not urgent, but the answer decides how many terms live here at once.

## 2 Sep 2026 — Weekly-worksheet answers are not stored as data (teacher's copy gap)

*Readings.* (a) Fabricate the worksheet answers now so the teacher's copy is "complete". (b) Ship the teacher's
copy with the verifiable term-paper keys and marking points, and leave the weekly worksheets un-keyed until their
answers exist as data.

*Taken: (b).* The objective worksheet items were shuffled by a tool that "does not need to know which option is
right", and no sidecar or field carries the correct letter, so any auto-generated worksheet key would be a guess —
a teacher's key with wrong answers is worse than none. The term-paper keys ARE stored (`data/exams/papers/*.key.md`)
and are printed in full. To close this, author a worksheet-key sidecar per subject-term (correct letter per item)
and have `--edition teacher` append it; do not infer answers from the prose.
