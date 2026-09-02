# Style — how a note, an item and the book must read

Copy the shape below by reading a finished example; the rules here are the parts that are not obvious
from one example. Best exemplars: `notes/src/nursery-2__2nd-term/basic-science.md` (a full subject) and
`data/exams/src/nursery-2__2nd-term__basic-science.txt` (its paper).

## Anatomy of a note (this exact order, `---` between weeks)

```
# <Subject> — <Class> · <Term>                     ← part heading, one per subject file

Weeks 1 to 6, 8 and 9. Week 7 is Mid-Term Break, …  ← prose, says which weeks carry no note and why
*Depth: NERDC 2025 · … pp 494–497.*                 ← provenance line, always italic + *Depth:*

---

### WEEK 3 — TITLE IN CAPS WITH AN EM-DASH

*Depth: NERDC Nursery 3 · <subject> · <term> W<n> (pp …).*

**You will learn to**         • one line per objective, lower case, no full stop, bullet `•`
**Things to know**            • the content, bolding the term being defined, always factual
**Let us talk**               1. numbered questions the class answers aloud, in the child's language
**Words for my notebook**     • 4–8 words with a one-line meaning each
**Worksheet**                 1.–7. exam-style items for THIS lesson (see below)
**My own work**               one thing the child does alone, at home, no adult involved
```

* 105 notes per term; every heading is `### WEEK n — TITLE`, all caps after the dash. `sticky()` in the
  page model assumes that form; the Contents is generated from it.
* Sentences: subject-verb-object, average under 12 words. Present tense. No subordinate chains.
* Address the child as "you"/"me" inside their own notebook ("observe living things around me"), never
  "pupils should". No jargon, no "learners will acquire…", no British private-school register.
* Bolding is for the word being defined and nothing else. No italics for emphasis (italics are reserved
  for the `*Depth:*` line).
* Local content is specific and correct: yam, garri, palm oil, snail, harmattan, Lagos lagoon, Yoruba
  words with their diacritics when the subject is Yoruba. Never "in some countries".

## Worksheet items inside a note

Seven items, mixed: 2–4 single-answer MCQs written inline as `A) … B) … C) … D) …`, one
`Fill in: … ____`, one short-answer "Mention two…", one written product ("Write two sentences on…").
`check_worksheets.py` counts the letters used across a whole term and reports `longest run of one
letter` — a term that comes out badly skewed gets re-worded, not re-lettered.

## The paper (`data/exams/src/<class>__<term>__<subject>.txt`) — exact syntax

```
# <Subject> — <Class> · <Term> · term paper
subject: Basic Science
class: Nursery 2
term: 2nd Term

[objective]                                          ← 30 lines
<stem ending in ___ or a question> || <RIGHT answer> || <distractor> || <distractor> || <distractor>

[subobjective]                                       ← 10 lines
<instruction naming how many> :: <answer> | <answer> | <answer>

[theory]                                             ← 5 lines
<question asking for named items> || <marks>
```

* **The right answer is the first option.** The letter is *not* authored — `make_exam.py` places it and
  balances A–D itself. Never hand-write a letter into a sheet.
* Exactly five `||` fields or `spec_from_lines.py` **silently drops the item**. Check
  `sheets expanded: 13 of 13` after every spec build.
* Distractors must be *plausible and true-sounding but wrong*, of similar length to the answer, and
  never the same word as another item's answer in the same paper.
* Stems that need no blank ("Which of these is…?") are fine; "Fill in:" must not be used inside
  `[objective]` — it fails the shape test.
* A stem must be answerable from that term's notes. `sheet_check.py --class … --term …` says so.

## The book (rendered, never hand-edited)

A4 landscape (29.7 × 21.0 cm), two columns, 0.7 cm gutter with a rule, margins 1.4 / 1.3 cm, body
Calibri 10.5 pt at 1.05 line spacing with 2 pt after each paragraph. Headings are real `Heading 1–4`
styles (so Word's TOC and Navigation pane work) drawn in Calibri Light — that is the template's doing,
leave it. Each part starts on a fresh page; the Contents carries a page number per line with dot leaders.

## Three rules that bit me while authoring Third Term, now gates

* **Never bold a worksheet option.** Bolding the right one prints the answer in the child's book. Bold the
  term in the stem, or in "Things to know" — never after an `A)`. `polish_audit.py` refuses it.
* **`**Worksheet**` is a header line, asterisks and all.** Drop them and the block silently disappears
  from the assembler's view (`check_worksheets.py` reports `n=0`, which is how it was caught).
* **A note must not sound like a mark scheme.** "solution", "marks", "answer", "the teacher guides" and
  friends are in `PLAN_WORDS` in `build_term_doc.py` and fail the build: say "the ORS water the clinic
  gives", not "the ORS solution".

## Tone rules that the builder enforces (see also `10-BRIEF.md`)

No answer text in the book. No adult addressee. No calendar-week note. No length or letter pattern.
Those five are not style advice — `--strict` will not let you ship them.
