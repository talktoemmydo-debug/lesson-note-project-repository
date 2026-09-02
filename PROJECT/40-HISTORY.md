# History — decisions, dead ends, and the things that look like bugs but are not

Read this before "fixing" something. Newest first.

## 2 Sep 2026 — Contents page numbers, and the page model behind them

* Owner asked for (a) rebalancing the flagged First-Term option texts and (b) a Contents that references
  page numbers. Both done; layout unchanged.
* First attempt printed numbers from a line-count model and claimed success. Reading the **shipped
  .docx** instead showed `agree 0 · mismatched 129` — every number exactly one page late. Two real
  bugs: the packer opened *two* pages for one flow index (the `h1` rule and the orphan-heading rule each
  called `open_page()`) while the renderer writes one break per index; and the break *inside* the
  Contents list was swallowed because the whole list was emitted in one `_toc()` call. Fixed by
  deriving pages from the break set and by splitting the Contents into one group per planned page.
* Then a mutation test (raising the fill budget to 1.45 to see whether the guard fires) showed the model
  never charged for the 2 pt after each paragraph, so the "10 % margin" was partly imaginary. The model
  now includes paragraph spacing and real per-level heading heights — which cost 9 pages (133 → 142)
  and made the margin real. **Lesson kept: measure the shipped artefact, and price the boring parts.**
* `book_pages.py` was rewritten to audit the .docx directly (unzip `word/document.xml`, count
  `<w:br w:type="page"/>`, read each `text<TAB>digits` Contents claim against each `w:val="Heading…"`).
  The old `--stamp` route and `data/exams/<class>__<term>.pages.json` are **gone**, deleted with that
  rewrite. No external renderer is needed on this machine any more.

## 1–2 Sep 2026 — Second Term authored to the First Term bar

* 105 notes across 13 subject files; 13 papers at 30/10/5; keys balanced by `make_exam.py`.
* `sheet_lint` leaks in the *First Term* sheets were fixed by re-wording 7 option texts (owner allowed
  touching the delivered First Term for this only). Re-rendered its 13 papers: key shape unchanged
  (`A=98 B=93 C=102 D=97`), proving the fix moved wording, not answers.
* Contents (front matter) was first added as a plain list + a live Word `TOC` field with
  `updateFields` — numbers then came from Word. That was replaced by the printed-number scheme above.

## Deliberate, and to be left alone

* **First-Term objective blocks hold 42–50 authored items where the paper prints 30.** Large pools are
  sampled by stride so each subject's paper varies by seed. So `sheet_check.py` on **1st Term will never
  go green** — it reports "objective has 42 items, needs 30". Not a bug. Second Term is authored at
  exactly 30/10/5.
* **A part heading and its first lesson can print the same page number** (both say `· 3`). By design: a
  heading is never allowed to sit alone at the foot of a page.
* **One lesson per page is not guaranteed** and never will be: under the old line metric 58–62 % of
  slots were overfull, which is why greedy packing plus forced breaks replaced it. Under-filling is
  harmless; over-filling is the only failure mode, so the model is pessimistic in one direction only.
* **`notes/_teacher-edition/` holds superseded teacher-voiced drafts**, kept only because General
  Knowledge and Nigerian History were re-voiced from them. Do not mine it for content, and do not confuse
  it with the new teacher's copy (which is a *key and marking* document, see `60-ROADMAP.md`).
* **Pupil books are not allowed to contain `____`-free worksheet blanks or "Fill in:" inside
  `[objective]`**; the fill-in lives in the note's worksheet, and `[objective]` items end in `___`.

## Dead ends — do not retry

* **LibreOffice headless on this box: closed.** `svp` VCL plugin missing, `/usr` read-only even under
  `unshare -rm`, Calibri falls back to DejaVu without `FONTCONFIG_FILE`, `xkbcomp` absent so a
  persistent Xvfb won't start, and `unshare -rm` + `cp -as /usr/bin/.` self-loops. `--render` therefore
  reports "skipped" and the .docx audit is the real gate. `pkill -f Xvfb` kills my own shell — use
  `pkill -f 'usr/bin/[X]vfb'` if it ever needs cleaning.
* **`edit_file` on a `.py` file can report success having changed nothing**, and a hand-spliced
  `replace()` on a string literal once produced a half-split module. Verify every such patch with
  `ast.parse` and a re-grep, and prefer line-index splicing.
* **`spec_from_lines.py` silently drops** any line with case-colliding options or not exactly 5 `||`
  fields — count the items after expanding, don't trust the exit code.
* **Never assume worksheet options were shuffled**: `check_worksheets.py` per term is the gate, and
  `shuffle_worksheet_options.py` runs **once** (running it twice is not identity) and only when the term
  comes out letter-heavy. Balanced letters come from authoring + `make_exam.py`, not rejection sampling.
* Numbering is authored **only** through `make_exam.py`; hand-numbered copies drift and get overwritten.
* The old workspace (pre-`uploads/`) died on the 128 MB / 10,000-file budget. That is the reason for the
  discipline in `50-IMAGES.md` and for `README.md` §6.

## Also true, and easy to lose

* Yoruba and General Knowledge papers are **school-generated**, not from the generic pools: their item
  text is authored per week from the notes, and diacritics matter.
* Digital Literacy and Prevocational Studies have **degenerate depth** in the source scheme — their
  topics repeat; don't "fix" it by inventing new content.
* Drafting artefacts (scratch notes, `/tmp/probe.docx`, `/tmp/vdocx.py`, the old `/tmp/lo` install) are
  outside the persisted workspace and should not be relied on.

**2 Sep 2026, later — the pictures became part of the polish.**  The owner had expected the plates to arrive
with the polishing, not after it, so `tools/img_import.py` was written and wired end to end: bilevel PNG at
≤1200 px → `assets/img/<class>/<term>/<subject>/weekN-<slug>.png` → a size row in `MANIFEST.jsonl` → the raw
generation deleted → the `![alt](path)` line inserted at the end of the note's `**Let us talk**` block.
`book_layout` now emits an `image` item and bills it at 193 pt (12.5 cm wide in a 13.1 cm column), so
`plan()` treats a figure as unsplittable before any page number is printed; `docx_out._figure` prints it at
the same shared constant; `--no-images` was proven to leave a text-only book byte-identical to the audited one.
Second Term Basic Science now carries 8 plates (143 → 145 pages, 129/129 Contents numbers still agreeing,
`audit : CLEAN`, 90 kB of pictures in a 315 kB book), and Third Term CCA carries 2 with 6 owed.  Eight raw
generations were read back as a flattened contact sheet and all eight passed; a stray stroke and an occluded
leg were accepted, no plate was thrown out.  Ten image calls a turn is the ceiling, so the remaining six land
next turn with the next subject.

**2 Sep 2026, later again — CCA finished, with its pictures.**  Six more plates (wk3, wk4, wk5, wk6, wk8,
wk9) were generated into `assets/.scratch/`, flattened and read back as one contact sheet before anything was
filed; all six passed on the first look, so nothing was deleted, and the raws went with the contact sheet at
the end of the turn.  `img_import.py` wrote each reference at the end of its note's `**Let us talk**` block.
Third Term is now **16 of 105 notes, 2 of 13 papers, 10 plates**: 23 pages, 20 of 20 Contents lines
numbered, `plan` reporting no problem, `audit : CLEAN`, tallest page 938 of 939 pt, one plate to a page on
pages 11–18, and 89.9 kB of drawings inside a 156 kB .docx.  The page model took six new plates without one
wrong number, which is what rule 7 was bought for.  Two housekeeping facts: the ten-generations-a-turn
ceiling means a subject's pictures are the first thing made in a turn, not the last; and five early style
samples in `MANIFEST.jsonl` carried their size as `kb` instead of `bytes`, so anything reading the manifest
uniformly would have crashed — the rows were backfilled from the files on disk and `img_import.py --check`
still comes out CLEAN.

**2 Sep 2026, later still — CRS finished, BDL written, the rate settled at one subject a turn.**
Christian Religious Studies came in with its eight plates: cross-on-a-hill and the empty tomb, children in a
ring with a lamb, love shown by lifting a fallen friend and sharing an orange, two blank tables of stone on a
mountain, a girl kneeling by a bed with a bird at the window, four panels of the day (sunrise, food, the
gate, the moon), three prayer positions, and a sun–bowl–moon row over a girl reading. **One plate was thrown
out**: the first wk9 came back as a pair of folded hands with no child attached, which is exactly what the
owner's "children drawn fully" rule is for, so it was regenerated as a whole girl holding an open book and
re-checked flattened before filing. CRS also needed three curly quotes normalised, and its paper needed two
stems re-trapped before `sheet_lint` went quiet.

Basic Digital Literacy's eight notes were authored the same turn — one internal part a week (headphones and
care, CPU, RAM, hard drive, motherboard, power supply, cooling, how the parts work together), each keeping
the five-year-old's distance from the abstract by anchoring every part on a thing at home: RAM is work in
both hands, the hard drive is the keeping box, the motherboard is the floor of the house, a power supply is
what a generator is to the house, a machine's holes are its nose. **Its eight plates are deliberately not in
this turn's book**: the generation ceiling is ten a turn and CRS spent nine, and a subject is shipped either
with its pictures or, when authoring has to take the turn, with the plate count written as owed.  Third Term
now stands at **32 of 105 notes, 4 of 13 papers, 16 plates**, 45 pages, 40 of 40 Contents numbers agreeing,
`audit : CLEAN`, `polish_audit 0 to fix`, and the manifest still CLEAN at 29 rows with the scratch folder empty.

**2 Sep 2026, end of the day — BDL pictured, Nigerian History authored, and the audit learned a lesson.**
Basic Digital Literacy's eight plates were made, flattened, read as one contact sheet and all eight filed with
no rejection: headphones and the cup of water kept far away, the thinking box with a chip on top, three blocks
carried in two hands against four blocks in a box (RAM and the hard drive), the keeping box with a house card
and a disc, the joining board with its little doors, the plug and the single round button, the fan with arrows
through the box, and four parts in a row joined by lines.
**One real defect came from them**: a 41-word alt text tripped the long-line rule, which measures prose a child
hears, and a caption is not that. `polish_audit` now exempts `![` lines from the length check *and* the caption
was cut to 29 words, because a 40-word alt is bad practice whoever reads it.
Nigerian History was then authored — traditional rulers, the Emir, Oba and Igwe, title holders, Baale Iyaloja
and Otunba, the Local Government and its chairperson, and leadership in my own day — with its 30/10/5 paper;
its sheet needed a 30th item and six stems re-trapped, and eleven subobjective lines had been typed with `||`
instead of `|`, which `sheet_check` would never have seen because the file was rejected for length first.
Two plates went in at the end of the turn (the ruler on his stool with two caps held in hands; the three
thrones by turban, beaded crown and soft cap), leaving six for the next.  Third Term stands at **40 of 105
notes, 5 of 13 papers, 26 plates**, 56 pages, 50 of 50 Contents numbers agreeing, `audit : CLEAN`, manifest 39
rows CLEAN, scratch empty, workspace 13 MB.

**2 Sep 2026, night — Nigerian History pictured, PHE written, and one plate thrown out for cropping.**
Six plates were made for Nigerian History's remaining weeks — the chief at the palace door, the Baale settling
two neighbours with the Iyaloja at her yam stall and a chief-messenger with a rolled mat, the queue at the
plain slit-box with two children watching, the road mended with the drain and the school bell, the monitor with
her palm up and a line of four behind her, and the village court played by children with two dolls brought
before a boy in an oversized cap.
**The first wk3 was rejected**: its three figures were cut off at the bottom edge by the frame, which is
exactly the cropped-figure rule the owner set, so it was redrawn with an explicit instruction — head to feet,
standing on one ground line, clear white space above and below — and it passed on the second look.  That
sentence ("every figure drawn entirely, well inside the page") is now part of the house prompt for any scene
of standing grown-ups.
Physical and Health Education was then authored: facilities and equipment, football, basketball, table tennis,
chess, video games with the limits stated plainly for a five-year-old, the parts of the body and their
movements, and the everyday moves — bend the knees, hold the load close, push with the legs, one at a time on
the stair.  Its paper needed one stem re-trapped and one mark-scheme line cleaned of a stray `||`; it came out
`A=7 B=8 C=7 D=8 · exploitable-longest: 0`.  Third Term: **48 of 105 notes, 6 of 13 papers, 32 plates**,
69 pages, 60 of 60 Contents numbers agreeing, `audit : CLEAN`, workspace 13 MB.

**2 Sep 2026, the loop closes — PHE pictured, and the project stops needing permission.**  Physical and
Health Education's eight plates were generated, flattened, read as one contact sheet and filed with nothing
rejected: the store box of equipment with two bibs hanging behind it, the inside-of-the-foot shot at a netted
goal with a crouching keeper, the fingertip bounce answered by two raised hands under a low hoop, two
children and a table whose ball may bounce only once, a checkered board sat between a thinking boy and a girl
pinching a piece, a blank-screened tablet abandoned on a stool while both children run out to a ball, five
children doing the five movements in a row, and lift-push-stairs in three groups.  Third Term now holds
**48 of 105 notes, 6 of 13 papers, 40 plates**, its book at 71 pages with 60 of 60 Contents numbers agreeing.

The owner then asked that this stop needing a nudge: *"Until the 3 terms are fully ready, I'm not ready for
any review."*  So the loop is written down in **`PROJECT/80-AUTOLOOP.md`** — the resume rule (any message runs
the next queue item; no re-planning, no re-asking), the turn recipe (pictures first, because the generation
ceiling is ten a turn and a subject's plates must arrive in one run), the closed decisions that are never to
be proposed again, the standing work-around for a genuinely blocked question (log it in `70-OPEN-QUESTIONS.md`,
take the reading that keeps the book right for a child, continue), and what *done* means for a subject, a term
and all three terms.

**`tools/gates.py`** is the other half: ten gates in one command, cheapest first, `[half]` shown for the
build's own `--strict` refusal while notes are still missing — which is the flag working, not a failure — and
a final line of `ALL CLEAR` or the count of failures, with the right exit code.  A turn now ends by reading
one line.  Two small truths from building it: `Path("data/exams")` resolved against the shell's directory and
crashed `relative_to(ROOT)`, so every path in it is rooted to the workspace; and a doc edit that inserted
after the first `## ` heading silently did nothing, because `00-START-HERE.md` has no `## ` headings — the
line is now anchored on text that exists, with an assert in front of it.

**A tick that meant nothing, and the gate that now forbids it.**  The status table claimed Third Term Basic
Science had its eight plates.  It has none: the eight pictures it was counted from belong to *Second* Term
Basic Science, and the check that day grouped the manifest by subject folder without the term in front of it.
Nothing in the harness could have caught it — `img_import.py --check` proved that every reference resolves to
a file and every file to a manifest row, which is trivially true of a note with **no** reference at all.  So
`--check` now counts notes and plates per subject file and prints `0 of 8 notes carry a plate` for every
shortfall, and the summary line reads `6 of 32 subject files fully pictured`.  It is a report, not a refusal,
because an unfinished term must still build; the refusal for a *finished* term belongs to `build_term_doc
--strict`, which already counts notes and weeks.  The picture owed is the whole job now, plainly numbered:
8 here, 57 for the seven unwritten Third Term subjects, 97 for Second Term, 105 for First — **267 plates**, at
eight to ten a turn.

**The correction held, in the very next turn.**  Third Term Basic Science's eight plates were made and filed —
the covered pot with its cup hanging at the neck, the jerry can and the bucket on its stand with a girl lifting
the lid; the boy holding his tummy and the covered cup offered beside a kettle on a wood fire; the camera on
its pole above a padlocked gate, with a whistle and a torch on the guard's table; the four animal homes in a
row; four mothers with their young; the lever, the wheelbarrow, the ramp and the well at home; the flag rope,
the seesaw and the book trolley at school; and the path from the house past the tree, the stream and the
market stall to the school door.  All eight passed flattened inspection with nothing rejected, the book grew to
73 pages with 60 of 60 Contents numbers agreeing, and `gates.py` closed the turn `ALL CLEAR`.  Coverage now
reads **7 of 32 subject files fully pictured**: six in Third Term plus the Second Term Basic Science sample.
`img_import --check` reports no shortfall in `3rd-term` at all, and the job left is counted, not guessed —
**97 plates in Second Term, 105 in First, and 57 riding on the seven Third Term subjects still to be written:
259 in all**, at eight to ten a turn.

One honest footnote about the turn itself: the paragraph that should have recorded this was written into a
`&&` chain behind `grep -c "3rd-term"`, which matched nothing, returned exit 1 as a *success* of the check and
silently skipped every edit after it.  Two of the three documents therefore lagged a call behind the book.
The lesson is small but real: a proof command that reports "no problems" by exiting non-zero must never be
chained into the thing that records the result.

## Prevocational Studies closed in one turn: the shape the loop was built to have

The seventh Third Term subject went from an empty file to `ALL CLEAR` inside a single turn, which is the
point of the loop contract — notes, paper, pictures and the record, with nothing asked of the owner.

The eight notes spread the term's one safety thread (farm tools, where they rest, what safety means, why it
matters, what a misused tool does, the kitchen, the rules we keep, the clothes that protect, storing and
first aid) so no two weeks repeat each other. `polish_audit` found exactly one thing to fix and it was a
register tell, not a content error: `as well as the` had crept into the week 6 bullet about swinging a tool,
so the line became *"the handle comes round too, and it can hit a person standing there."* After that,
`0 to fix · 3 to consider`.

The paper is 30/10/5 with `A=7 B=8 C=8 D=7`, no adjacent repeats, no ABAB, and `sheet_lint` quiet once
three traps in the ground-checking item were lengthened to sit within a few characters of the right option.

All eight plates were drawn from each note's own `**My own work**` line, flattened into one contact sheet at
threshold 160, read, and accepted — no regeneration was needed at all this time. The scene content came back
right every time: tools on a rack above a wheelbarrow, a path with nothing on it, three workers with room to
swing, a cracked hoe handle beside a stoned ring, a lid lifted with a cloth and cutlery high on a shelf, a
cutlass carried point-down with the hoe's blade behind the boy, four pegs of protective gear, and a rake hung
up beside a broken one being shown to a man with a hammer. The book now bills **56 plates over 56 notes**.

One mistake worth recording: the contact sheet script placed its tiles with `i // 2` for the column and
`i % 2` for the row, so half of them landed outside the canvas and the first read showed four pictures where
eight were expected. The fix was to swap the arithmetic and read again — but the lesson is that **a QC sheet
must be checked for its tile count before its contents are judged**, otherwise the pass is a pass over
whatever happened to fit. The rebuilt sheet printed `tiles: 8` and showed all eight.

`img_import --check` now reads **69 plate(s) · 8 of 33 subject files fully pictured**, no shortfall anywhere
in `3rd-term`, and the debt is 251: 49 notes still to be written in Third Term, 97 in Second, 105 in First.
Workspace 14 MB, 318 files, `assets/.scratch` empty.

Addendum to that entry, made in the same turn: the note's own voice was then swept to the book's word
**grown-up** (ten `adult` uses and the week 5 heading rewritten, three lines of the paper re-worded with the
traps lengthened so `sheet_lint` stayed quiet), because `polish_audit`'s register list was never about that
noun at all — what it caught was `as well as the`.  `adult` now appears nowhere in Prevocational Studies, and
`gates.py` closed `ALL CLEAR` on the re-worded book: 56 notes, 56 plates, 85 pages, 70 of 70 Contents
numbers, `audit : CLEAN`.

## Social and Citizenship Studies: eight notes and a paper, seven plates, and a flag said no twice

The eighth Third Term subject was authored whole — the place we live and the weather that changes, the animals
that live by themselves, the naira (coin, note, `N` with two strokes), spending wisely and saving, being a
citizen with rights and duties, the town and the village, the leaders of the community and the wide world —
8 notes at `0 to fix`, and a paper at 30/10/5 with `A=8 B=7 C=7 D=8`, no adjacency, no ABAB, `sheet_lint`
quiet on the first pass because the traps were written within a few letters of the right option.

Seven of its eight plates were drawn, read together on one contact sheet (`tiles: 8 of 8`, the arithmetic
fixed after last turn's mistake) and filed. The eighth is the honest exception, and it is recorded rather
than hidden: the first raw came back as **two identical scenes side by side** — a duplicated panel is not a
plate — so the prompt was reissued with `ONE single scene … no panels, no repeats`, which fixed the
duplication but drew the Nigerian flag with four horizontal bands where the note teaches *three tall strips*.
The turn's ten generations were spent by then, so the raw was left in `assets/.scratch` and the queue line
carries the debt into the next turn: `7 of 8 plates`, one more try at the flag.

The book grew to **64 notes, 63 plates, 97 pages, 80 of 80 Contents numbers**, `audit : CLEAN`,
`gates.py` closing `ALL CLEAR`. The debt was recounted from `img_import --check` line by line instead of
carried over from a note: 105 (First) + 97 (Second) + 1 (SCS week 5) = 203 owed on notes already written, plus
41 Third Term notes still to be written — **244**, at eight to ten a turn. Workspace 15 MB, two files in
scratch, nothing else derived left behind.

## Yoruba, Third Term: nine notes, a first-pass paper, and no pictures at all

The owner's word — *"Yoruba doesn't need images, move to the next subject"* — closed a whole category of work,
and it is written into `80-AUTOLOOP.md` §4 as a standing decision rather than a one-off: the subject is sound,
word and song, and `img_import --check` will keep printing 27 Yoruba shortfall lines (nine in each term) that
are **exempt, not owed**. The held Prevocational/Social-studies raw from the previous turn was deleted with the
turn instead of being carried, and that one owed plate moved into the backfill sweep where the rest of its
term-mates wait.

Nine notes were authored from the school's own rows, each carrying the three strands the master prints —
**Ẹ̀dẹ̀ · Àṣà · Lítíréṣọ̀**: the teacher's actions and the greetings at their hours; joining letters
(**à-kà-rá = àkàrà**) beside the fruits of the land and the two kinds of àlọ́; the talk between teacher and
pupil, washing at the two times, and the carrying song; numbers 21–40 with the seven days of the week;
the colours, good and bad character, and **Iṣẹ́ ni òògùn ìẹ́**; dictation and the duties of ẹ̀gbọ́n and
àbúrò; the cassava work from the ground to the pot and the akọ̀sọ̀rọ̀ at two speeds; the parts of the body and
the Òba aláde; and a Week 11 revision note, because the school prints that week as a teaching row.

Where the master names a song or a poem by its first line alone — *Orí ẹwẹ̀, má ṣe payà*, *Kí ni n ń fi ọ̀lẹ̀
ṣe?* — the note keeps that line and teaches the form, the answer and the meaning; it does not invent the rest.
That is written into the file's preamble so the next reader sees the choice was made, not missed.

The paper came out 30/10/5 on the first pass — `A=8 B=8 C=7 D=7`, no adjacency, no ABAB, `sheet_lint` quiet —
after the word *answer* was kept out of the stems, where the sheet checker reads it as a teacher-voice word.
The book is now **73 notes, 63 plates, 110 pages, 91 of 91 Contents numbers, `audit : CLEAN`, `ALL CLEAR`**.
The debt was recounted through the exemption: 212 shortfall lines printed, 27 exempt, **185 owed on notes
already written** plus the 32 Third Term notes still to come — **217**.

## General Knowledge: eight notes, one paper, and the second subject freed from pictures

*"GK does not need images too"* — the owner's second word on pictures, written straight into `80-AUTOLOOP.md`
§4, and with it two of the thirteen subjects are now **word-only in every term**: Yoruba and General Knowledge.
Every other subject still gets one plate per note; the 51 shortfall lines `img_import --check` prints for these
two are read as exempt and nothing more is generated for them.

The eight notes follow the school's stream line, *My Big World & My Country's Story*: our state and town
(Lagos at the south-west where the land meets the sea, Ikeja the big city, the Eyo masks, àmàlà with ẹ̀fọ́ and
fish from a boat); water and air, with the float-and-sink, the bubble and the window chime; the sky and the five
parts of the day; the tools of the house and the class, with the wheel, the ramp and the lever; one Nigeria of
many peoples, the river the country is named from, the flag's three tall strips; counting twenty as two lines of
ten and sorting by size, colour, shape and kind; the people who did great things — the farmer, Ìjà̀pá, **Queen
Amina of Zaria told in story form as the pack asks**, and the workers who keep a town moving; and the
end-of-year quiz, show-and-tell and the line *I am ready for Primary 1*.

Three draft slips were caught and cut before the audit — a half-written food list with a `?` in it, a
show-and-tell day item that implied Friday was the mosque day wrongly framed, and Yoruba fruit names in an
English sorting question. The book is **81 notes, 63 plates, 120 pages, 101 of 101 Contents numbers,
`audit : CLEAN`, `ALL CLEAR`**, with the key shape at `n=300 A=76 B=74 C=75 D=75`.

The debt after the second exemption: **193** — 169 plates owed on notes already written (88 First Term,
80 Second Term, and the one Social Studies week 5), plus the 24 notes of the three Mathematics & English
streams still to be written. Those three are the last subject files of the term, and every note in them is
still to be pictured.

## Numeracy: eight notes with real objects in them, and two plates refused for a stray limb

The first of the three Mathematics & English streams is finished — halves and quarters, length, weight, time,
the shapes you can hold, the flat shapes, patterns and symmetry, and the first gathering of class information —
each note carrying the pack's depth floor (the **½** and **¼**, the hand span and the centimetre, the gram and
the kilogram, the short hand and the long, faces·edges·corners on a cube, sides and corners on a triangle, the
line of symmetry, four strokes and a fifth across them) in lines a five-year-old can read out loud.

Its paper went out 30/10/5, first pass clean: `A=8 B=7 C=8 D=7 · exploitable-longest 0 · PASS — no adjacency,
no ABAB, balanced`, with the traps kept within a few letters of the right option and no teacher-voice word in any
stem. Every worksheet in the notes was then **re-ordered by hand** so the subject's answer letters run
`C A D B · A D B C · D B C A · B C A D …` — 8 of each letter across the 32 objective items, with no letter twice
at a seam — because the option order is what makes a key guessable, not the wording.

Six of the eight plates were accepted at the first reading. Two were refused for the same fault the house has
seen before: a **disembodied limb** — an arm lying on the far side of the desk with no child attached, and a
hand reaching in from nowhere to place the next shape. Both prompts were rewritten to name the one body and to
say `no extra arms, no second person, no floating hands` / `no people, no hands, no arms anywhere`, and both
came back right. The rejected raws were deleted in the same turn as their replacements were filed.

Two things the audit caught that are worth keeping in memory. A worksheet option line of four long options reads
as a 37-word line, so it was trimmed; and `polish_audit` counts **hard-wrapped lines** in a `p` block — the `---`
that closes a note counts with them — so a `My own work` of three source lines is already over the house ceiling.
That is now written in `80-AUTOLOOP.md` §4 rather than rediscovered next term.

The book is **89 notes, 71 plates, 133 pages, 111 of 111 Contents numbers, `audit : CLEAN`, `ALL CLEAR`**, and
the docx was counted rather than trusted: 71 inline shapes against 71 media parts. With two subjects exempt
from pictures, the remaining debt is **185**: 88 plates in First Term, 80 in Second, the one Social Studies
week 5, and the 16 notes of the last two streams.

## Literacy (letter work): the subject about words, pictured with no word in it

The twelfth subject file is done — sight words and the three things that make a sentence neat, five-letter
words and the blends and digraphs inside them, compound words, the hen story in three boxes, describing words,
action words, writing a story of your own, and the marks that end a line. The sentences a child has to read are
printed in the **note** ("The hen goes out. She sees a corn.") and the **plates carry no text at all** — a
subject about letters is the one where a garbled pseudo-word in the art would do the most harm.

That set the picture problem and the way round it: a blank caption strip under the morning washstand, five
empty boxes for the sounding-out, three plain boxes for the hen story with no numbers on them, two blank cards
standing on the table where the tall one says *the first letter is big*, and — for the full stop — not a drawn
symbol but **one small solid dot at the end of the first ruled line**. All eight came through the first read
with no grey fill, no stray limb and every figure head to shoes, so nothing had to be regenerated.

Its paper went out 30/10/5 clean on the first pass, `A=7 B=8 C=8 D=7`, no adjacency, no ABAB, `sheet_lint`
quiet; the notes' own worksheets again rotate their letters (8 of each, none twice at a seam). One item was
rewritten while drafting because "a big stone / a small stone" style ambiguity would have let two options be
right at once — e.g. "which word ends a sentence" became "a line that **tells** a thing ends with", so the
question mark and exclamation mark stay wrong answers rather than half-right ones.

The book is now **97 notes, 79 plates, 145 pages, 121 of 121 Contents numbers, key shape n=360
A=91 B=89 C=91 D=89, `audit : CLEAN`, `ALL CLEAR`** (docx counted: 79 inline shapes, 79 media parts). Workspace
15 MB, scratch empty. **One subject file stands between this term and completion**: the language domain —
8 notes, one paper, 8 plates — and after it the debt is 88 (First Term) + 80 (Second Term) + 1 (Social
Studies week 5) = **169** pictures in the backfill sweep, plus those 8.

## 2 Sep 2026 — the language domain, and the term closes (Nursery 2 · Third Term)

Item 13, the last Third Term subject file, came in as eight notes: the sound patterns we already know
(`shirt`, `clock`, `hair`), naming words in four kinds, doing words, a naming word and a doing word together,
longer sentences, reading a page of our own, a three-box story we write ourselves, and the whole term on one
page. `polish_audit` first asked for four changes — a `My own work` line that deputised a grown-up, a
"with teacher" phrasing, the register word *particular*, and a week 2 note pointing forward to week 8 — all
four reworded, then `0 to fix · 3 to consider (pre-existing)`. Its paper was clean on the first pass: 30/10/5,
`A=8 B=7 C=7 D=8`, no adjacency, no ABAB, `exploitable-longest: 0 (slight: 7)`, `sheet_lint` with
`lines to re-balance: 0`. Eight plates, one per note, all eight accepted on the first read and none
regenerated: the shirt and the twelve-mark clock with no numerals, four blank-topped boxes for the four kinds
of naming word, four children doing four things, a bird–fish–goat set, the putting-away scenes, the boat in
three boxes, three empty story boxes with a teddy and a drum waiting, and a girl reading a blank page to the
class. Every writing surface in them is blank, as a letter-work subject requires.

**The import nearly didn't happen, and the book nearly shipped a duplicate.** The eight `img_import` calls
first came back `status: shell_error` with nothing written — the shell's `cwd` field had been given a command
fragment instead of a directory path, so the block never started. Re-run as plain `cwd: /home/user`, all eight
lands. Then the build printed `121 notes · 28 parts` for 105 notes in 13 files: the third maths-and-English
file was being pasted **twice**. `build_term_doc` assigns a file to a part by `bare(title)` — the title with a
trailing bracket cut — and `Mathematics & English · Literacy (Language Domain)` and `… · Literacy (Letter
Work)` bare() to the same name, so each of those two parts held both files' 8 notes and two of the thirteen
papers were printed twice. The tool has always had the right shape for this (First and Second Term use it):
one title `# Mathematics & English — <Class> · <Term>` plus a `**Stream: …**` line per file, so one part
carries three sub-parts. Applied to all three Third Term files, the book came back **105 notes, 24 parts,
13/13 papers**, and the coverage audit now keys each stream properly. Yoruba lost four `the teacher says/asks`
lines to the same rule that polices plan voice in the pupil book.

**Third Term is closed.** `notes/Nursery 2 - Third Term.md` 392,164 B / `.docx` 1,263,942 B, **156 pages**,
**87 plates** billed, **129 of 129** Contents lines numbered, `key shape n=390 · A=99 B=96 C=98 D=97 ·
repeats 0 · ABAB 0`, `audit : CLEAN`, `img_import --check figures : CLEAN`, and `gates.py` ends **ALL CLEAR**
with no `[half]` on the build line for the first time this term. Workspace 15 MB, `assets/.scratch` empty.
The queue now turns to the backfill sweep, kept in **`76-BACKFILL.md`** and regenerated by
`tools/backfill_ledger.py` each turn. The sweep opened the same day: Second Term's basic digital literacy took its
first two plates — the room-sized computer with the abacus and the phone, and the parts-I-can-touch still life —
both accepted on the first read, so that book stands at **10 plates, 145 pages, 129 of 129 Contents numbers,
gates ALL CLEAR**, and **167 plates remain** (Second Term 78, First Term 88, one SCS plate in Third Term).
The teacher's copy for all three terms is still owed after the sweep.

## 2 Sep 2026 — the sweep opens: six plates for two Second Term subjects

Third Term being shut, the loop moved to the backfill. `tools/backfill_ledger.py` was written first so no count is
carried by hand again: it runs `img_import --check`, drops the exempt subjects, and rewrites **`76-BACKFILL.md`**
at the start and end of every sweep turn. Two turns of the sweep landed today — Second Term basic digital literacy
took the room-sized machine, the parts-I-can-touch still life, the hand on the mouse, the quiet microphone and the
printer with its blank sheet; Christian Religious Studies took the good things in the garden, the child under the
tree with the lamb, and the bowls set out for the younger children.

Ten generations, **six kept, four deleted in the same turn**: the scanner sheet came back with a solid black blob
down the right edge, and the monitor, the headphones and the bedtime scenes each came back as **the same child
drawn twice side by side** — a split panel where one scene was asked for. Both failure shapes are now written into
`80-AUTOLOOP.md` §2 step 1, with the wording that wards off the second (`the child appears once — no second copy,
no split panels, one scene only`), and those four plates are the head of tomorrow's run.

**Second Term now builds at 105 notes, 13 papers, 16 plates, 147 pages, 129 of 129 Contents numbers,
`audit : CLEAN`, `rule checks: all clear`, gates ALL CLEAR** (docx counted: 16 inline media parts). Third Term is
unchanged and green at 87 plates and 156 pages. The ledger reads **161 owed**: Second Term 72 (basic digital
literacy 3, Christian Religious Studies 5, then nine files at 8) and First Term 88, plus the one SCS week 5 in
Third Term. Workspace 15 MB, `assets/.scratch` empty.

## 2 Sep 2026 — sweep turn two: ten generations, eight kept

Second Term's four rejects from the first sweep turn were re-made with the one-scene wording, and the two subjects
were carried on: **basic digital literacy is whole at 8 plates** (the scanner with its lid up and the webcam on a
blank screen, the child sitting with the eyes level with the top of the monitor, the child with one hand at the
headphone ear cup, joining the machine-room row, the still life of parts, the mouse, the microphone and the
printer), and **Christian Religious Studies stands at 7 of 8** (the child kneeling by the bed under the moon
window, the tree watered and the compound swept with the goat drinking, the basket of five loaves and two fish by
the boat, and three children on a mat with a bowl of seeds and one bird). Cultural and creative arts opened with
the hand fan: zigzags, dots and stripes on its face, scissors and a folded card on the table.

Two of the ten went back out again the same turn: the church-and-sharing scene came with a **solid black speckled
band** down the right half — the third time that blob has appeared on a scene with a wall or a background plane —
and the splash-art sheet covered its table with **newspaper drawn as columns of fake print**, which is writing
however small it is. Both raws are deleted, neither plate is overwritten, and `80-AUTOLOOP.md` §2 step 1 now names
covering props (newspaper, cloth, poster) as the thing that invites surrogate text, with the wording to ask for
plain instead.

**Second Term: 105 notes, 13 papers, 24 plates, 149 pages, 129 of 129 Contents numbers, `rule checks: all clear`,
gates ALL CLEAR** (docx counted: 24 inline media parts). Third Term unchanged and still green at 87 plates,
156 pages. The ledger re-derived itself to **153 plates owed** over 21 files — Second Term 64 (CRS 1, then CCA 7
and eight files at 8) and First Term 88 plus the single SCS week 5 — and the workspace is at 16 MB with
`assets/.scratch` empty.

## 2 Sep 2026 — sweep turn three: ten generated, seven kept, and a rate measured

Christian Religious Studies closed: the church-and-sharing sheet came back clean once the wall was left out, and
**that file is whole at 8 of 8**. Second Term cultural and creative arts took four more — the brush flick over
blank splashes, the fork pressed into the hedgehog's back, the tree of torn paper with its leaf shapes left empty,
and the foam cut in layers so one piece stands proud — and the Mathematics & English language stream opened with
its two hardest plates to draw without writing: a blank ruled page with three blank cards for the capital letters,
and one ball, three children holding hands and a heap of marbles for `one`, `we` and `some`.

Three of the ten were deleted in the turn: the bead-threading, the sand and the cone-hat sheets all came back as
**the same child drawn twice side by side**, for the fourth, fifth and sixth time in three turns. Counting all thirty generations of the sweep turned the hunch into a number, now written in `80-AUTOLOOP.md` §2: the wording that begs for one copy of the child has held on **11 of 14** single-child sheets (and only 3 of 6 before it was lengthened), so it is worth saying and worth nothing on its own, while the five sheets asked for as **the work and the tools only** have never doubled at all.  Craft and device notes are therefore drawn as objects; a body enters only when the note is about the body.

**Second Term: 105 notes, 13 papers, 31 plates, 150 pages, 129 of 129 Contents numbers, `audit : CLEAN`,
`rule checks: all clear`, gates ALL CLEAR** (docx counted: 31 inline media parts). The ledger re-derived to
**146 owed** over 20 files — CCA 3, then Mathematics & English language 6, literacy 8, numeracy 8, and eight more
Second Term files at 8, before First Term's 88 and the single Social-and-citizenship week 5. Workspace 16 MB,
`assets/.scratch` empty.

## 2 Sep 2026 — sweep turn four: ten made, ten kept

The rule measured last turn was followed and it paid: every sheet this turn was asked for as **the work and the
tools only**, with `no people, no hands, no arms anywhere`, and **all ten came through the read with no second
copy, no black edge and no writing anywhere** — the first clean sweep of a full ten. Three cultural and creative
arts plates landed (the beads strung in an alternating pattern on the mat, the sand with its tipped cup and its
plate of spare, the cone hat with its ribbon and peg), six closed the Second Term language stream (three matched
pairs on a mat for double consonants; an egg, an ink bottle, a comb and a spoonful of beans for `egg · add · ink ·
comb`; rain, a train, a tree and a blank tea tag for `ai / ay / ee / ea`; a kite, an oil lamp, a cow and a
steaming pot for `igh / oi / ou`; a brush, two matches, a fan and a glass of water for `are / air / tch / ure`; and
one apple, one ball and a heap of stones for `a · an · some`), and one opened the literacy stream — a cat, a fan,
a log, an empty tin and a net for the CVC families, five three-letter words with nothing written on them at all.

**Second Term: 105 notes, 13 papers, 41 plates, 153 pages, 129 of 129 Contents numbers, `audit : CLEAN`,
`rule checks: all clear`, gates ALL CLEAR** (docx counted: 41 inline media parts). Two more files are whole:
cultural and creative arts 8 of 8 and the language stream 8 of 8. The ledger re-derived to **136 owed** over
18 files — Second Term literacy 7 and then six files at 8, First Term's eleven at 8, and the one
Social-and-citizenship week 5 — workspace 16 MB with `assets/.scratch` emptied.

## 2 Sep 2026 — the owner frees two more subjects, and the literacy stream closes

*"Nigerian History and Social and Citizenship Studies need no images."*  Four of the thirteen subjects are word-only
now — Yoruba, General Knowledge, Nigerian History, Social & Citizenship Studies — and the rule lives in one place,
the `EXEMPT` set in `tools/backfill_ledger.py`, so the ledger, the sweep queue and the debt count all moved together
the moment it was written there: **136 owed became 103** before a single plate was made this turn.  It also settles
the last loose end in Third Term: the social-and-citizenship week 5 plate, which had come back three times and been
cut for a wrongly striped flag, is **closed by the exemption rather than re-made**; the raw left waiting there is gone with the rest of the scratch, and the seven plates already drawn for
that subject stay in the book — the exemption says what is owed, not what to erase.

Ten plates were generated and **eight were kept**: the whole of Second Term's literacy stream closed — nest, band and
mint for the `-nd -nt -st` endings; lamp, trunk and parcel for `-mp -nk -ft`; a blank flag, a drum and a frog for the
blends; eight blank cards for the flash-card game; a nine-empty-square bingo card for `bingo`; three empty ruled
lines with **one small solid dot** at the end of the first for sentence work; and the cat, hat, bat, spoon and balloon
for rhyming.  Numeracy took its five bundles and empty tray.

**Two went back over their counts.**  Asked for eight bundles of sticks the model drew seven, and asked for one bundle
beside a tens board it drew two crossed like a letter — and on a counting note the number is the lesson, so a miscount
is not a small blemish but a wrong plate.  Both were deleted in the turn, and `80-AUTOLOOP.md` §2 now says the read
must count every group, or the prompt must leave the quantity out and let the text carry it.

**Second Term: 105 notes, 13 papers, 49 plates, 155 pages, 129 of 129 Contents numbers, `audit : CLEAN`,
`rule checks: all clear`, gates ALL CLEAR** (docx counted: 49 inline media parts).  The ledger re-derived to
**95 owed** over 12 files — Second Term 23 (numeracy 7, PHE 8, prevocational 8) and First Term 72 — and Third Term
now owes nothing at all.  Workspace 16 MB, `assets/.scratch` empty.

## 2 Sep 2026 — counting sheets, and the frame that isn't a frame

Ten generations for Second Term: **seven kept**.  Numeracy moved to 6 of 8 — five bundles with three loose ones for
the nineties, four bowls whose beads climb by one for ordering, the nest with three eggs and a basket for putting
together, four stones on a plate with three waiting between the plates for the missing addend, and four eggs left in
the basket with the two taken out for the subtraction gap.  Physical and health education opened on its two
people-shaped notes: the ring with one gap left open for the new player, and the pair at attention and marching.

Three were deleted in the turn, and all three for a shape not previously on the list: **the model framing the scene
itself**.  One money sheet and one football-bench sheet came back with a thick black band along the edge; a sticks
sheet came back as a **mock-up of an open book**, the drawing sitting on a curled page with grey shadow under it,
which is not a plate at all but a picture of a plate.  `80-AUTOLOOP.md` §2 now asks for a `flat drawing on a plain
white page, no book, no page curl, no shadow, no frame line`, and the read looks at the edges before it looks at
the objects.  The counting rule from the last turn was also tested: the bundles, the climbing bowls, the stones and
the eggs were **counted by eye at full size** before being accepted, and the one sheet whose loose sticks came back
as seven instead of six went out with the grey book mock-up rather than being argued about — with the count already
named in the note's own text, a plate that miscounts is a wrong plate.

**Second Term: 105 notes, 13 papers, 56 plates, 156 pages, 129 of 129 Contents numbers, `audit : CLEAN`,
`rule checks: all clear`, gates ALL CLEAR** (docx counted: 56 inline media parts).  The ledger re-derived to
**88 owed** over 12 files: Second Term numeracy 2, PHE 6, prevocational studies 8, and First Term's nine files at
8 apiece.  Workspace 16 MB, `assets/.scratch` empty.

## 2 Sep 2026 — the flat-page ward, and two subjects joined

Ten generations again: **eight kept**.  The new wording — `a flat drawing on a plain white page, no book, no page
curl, no shadow, no frame line` — went onto all ten prompts and the edge trouble fell from **3 sheets in 10 to 1 in
10**: improving, not gone.  What landed: numeracy week 9's market cloth (two folded notes standing on their edge,
three plain coins, a bowl of four and an empty basket, every coin blank); Physical and Health Education opened its
feelings work with the child on the bench and the arm stretched out in welcome, and added the jump and the bend, the
hand-and-foot-before-the-weight on the climbing frame, the two runners to the flag, and the indoor games laid out as
objects only — a cross-path board with four counters, six puzzle pieces half joined and two cards face down; and
prevocational studies opened on farm work drawn without a farmer in it, the hoe, sheathed cutlass, watering can,
knapsack sprayer and tipped seed basket, and the farm row of fence, goat, maize, yams, hens at a feeder and a
cutlass standing in a stump.

**Two went back.**  The bundle-of-sticks sheet carries a torn dashed line down its right edge — the frame artifact
again, one survival out of ten — and the posture sheet filled both pages with hatch marks that read as writing, so
the blank-surface rule was applied as written and it is being re-made.

**Second Term: 105 notes, 13 papers, 64 plates, 159 pages, 129 of 129 Contents numbers, `audit : CLEAN`,
`rule checks: all clear`, gates ALL CLEAR** (docx counted: 64 inline media parts).  Per-file counts read back off the
sources: numeracy 7, PHE 7, prevocational studies 2.  The ledger re-derived to **80 owed** over 12 files: numeracy 1,
PHE 1, prevocational 6, then First Term's nine files at 8 apiece.  Workspace 17 MB, `assets/.scratch` empty.

## 2 Sep 2026 — the owner counts the sticks, and three filed plates are pulled out of the book

*"What you must consider in the numeracy is the consistency of the picture with the lesson. 1 bundle of sticks
should count 10. Whereas, what I've been seeing so far is always counting more than ten per bundle."*  The word
**more** was even generous: counting the filed plates at zoom, the bundles held **seven and eight**, not twelve —
and the five rows meant to be five tens came back with ends packed too thick to count as ten.  The bowls plate I had accepted last
turn for the ordering lesson reads **2, 3, 5, 6**, not the 2, 3, 4, 5 the note teaches.  Every one of those was
drawn by me, read by me and filed by me, because I had been judging the counts from a 660-pixel contact-sheet tile
instead of looking at the sheet itself.

**Four plates came out of the book.**  `![…](…)` removed from the note, the PNG deleted, the row dropped from
`assets/img/MANIFEST.jsonl`, the book rebuilt — after which `img_import --check` put weeks 2, 3 and 4 back on the
ledger by itself, which is the proof that pulling is clean: Second Term numeracy went from a wrong 7 of 8 to an
honest **5 of 8**.  What replaced them is drawn so a child can point: **ten sticks in one row, tied at one end,
ten ends visible**, counted at full size before it was accepted (the bundle that went in for week 1 has ten tops and
ten bottoms and four loose sticks apart from it, and it stayed), and for week 5 an arithmetic sum the note can stand
on: **five eggs in the nest, three laid beside, eight in the basket** — 5 + 3 = 8, each group counted.  A ten-frame
is the fallback where a row of ten still will not come back right.

Six plates were added with the correction: the two numeracy ones above, PHE's posture sheet at last (one child
straight-backed with feet flat, one bent double with a leg tucked under, both pages blank — the hatched pages that
got the first attempt rejected are gone), and prevocational studies weeks 3 to 6 — the hoe and the sheathed cutlass,
the eight-toothed rake with the watering can and the levelled seedbed, the **flat square-topped spade against the
deep pointed shovel** so the two can actually be told apart, and the one-wheeled barrow with its basket.  **Second
Term's physical and health education is whole at 8 of 8.**

The same test was then run over the numeracy plates already shipped in Third Term, and most of them pass it hard:
the clock really does read **nine** with twelve marks and no numerals, the pattern is exactly `square circle square
circle square circle square` with square next, the house is triangle over square over a rectangle door, and the
three towers count **6, 4, 2** against the orange, banana and mango the note asks about.  Two do not, and both are
head of the queue: week 5's row of shapes you can hold ends in a **flat circle** where the lesson needs a ball, and
week 1's "halves" include a pair of rectangles whose half is three-fifths.  They are written into `80-AUTOLOOP.md`
§3 as **repairs owed**, taken before the next owed plate.

**Second Term: 105 notes, 13 papers, 67 plates, 160 pages, 129 of 129 Contents numbers, `audit : CLEAN`,
`rule checks: all clear`, gates ALL CLEAR.**  Ledger re-derived: **77 owed** over 11 files.  Workspace 17 MB,
`assets/.scratch` empty.

---

## 2 Sep 2026 — the four repairs are taken, and Second Term closes at eight of eight in every subject

The repairs were run first, before any new subject, and every one of them was judged by counting at full size rather
than by looking at a contact-sheet tile.

**Third Term · numeracy week 5** — the shelf of things you can hold was re-made with the ball drawn as a **sphere with
one curved seam**, standing between the cube, the cylinder, the cone and the matchbox, with a plain die and a carton
at the end of the shelf.  **Week 1** — re-made as three rows that are actually equal: a cake with one piece cut out, a
circle cut on a straight line through its centre into **two alike halves**, and a circle cut into **four alike
quarters**.  The rectangle "half" that was three-fifths is gone.  Both replaced through the full pull dance — note
line, PNG and manifest row (asserted on the way: lines 51 and 300, manifest 159 → 157 rows) — and the term came back
at **87 plates · 156 pages · `audit : CLEAN` · gates ALL CLEAR**, so the page billing never shifted.

**Second Term · numeracy weeks 2, 3 and 4** — rebuilt on the **ten-frame** the note itself names, and counted off a
1250 px print before import: week 2 is **five frames, every one of its two rows of five filled** (ten counters in
each, fifty in all); week 3 is **four filled frames, a fifth holding only the three left boxes of its top row, and
three loose counters below** — forty-three, which is the tens-and-ones the lesson teaches; week 4 is **four rows of
counters, two then three then four then five**, each row one longer than the row above, nothing else on the page.  All
three margins measured clean (0 dark pixels inside 14 px of an edge).

**Second Term · prevocational studies weeks 8 and 9** — the row of tools whose **working part** faces the reader (hoe
blade set square, eight-toothed rake, flat square-topped spade, curved scoop) and the two tools **at work**: a spade
sunk in a clean-cut hole against a shovel lifting a scoop of soil with crumbs falling, which is the one-sentence
difference the note asks for.  **Second Term's prevocational studies is whole at 8 of 8, and so is its numeracy — the
term now has no plate owed anywhere in it**, `img_import --check` prints not one Second Term file.

**First Term · basic digital literacy** began: week 2 is filed (desktop with separate screen, keyboard, mouse and box
· laptop opened like a book · one flat tablet, every screen blank).  Week 1 came back with the right five devices and
blank screens but **its table legs ran off the bottom edge** — 139 dark pixels inside the 14 px margin band, counted
by the margin test — so it was deleted in the turn it was judged and the week stays owed.  The margin test is now part
of the same-turn QC.

**Books as they stand**: Second Term 105 notes · **72 plates** · 160 pages · 129/129 Contents numbers · 13/13 papers
· `n=390 A=98 B=99 C=99 D=94` · rule checks all clear · gates ALL CLEAR.  Third Term 105 notes · 87 plates · 156
pages · gates ALL CLEAR.  **Ledger re-derived: 71 owed over 9 files — all nine are First Term.**  Workspace 17 MB,
`assets/.scratch` emptied of every raw and every crop.

## 2 Sep 2026 — First Term backfill sweep, turn one: seven plates in, three sent back

The sweep on the new ledger took the top of the queue: **First Term basic-digital-literacy** and the start of
**basic-science**. Ten raws generated, flattened at the print threshold into one contact sheet and read, with the
border margin counted by machine rather than by eye. Seven survived and were imported through `img_import.py`
(reference placed at the end of each note's *Let us talk*): BDL **weeks 1, 3, 4, 8, 9** (five devices on a table with
its legs inside the page · the four basic parts · shop/bank/hospital machines · abacus-to-laptop row · the geared
thinking machine) and basic-science **weeks 1, 2** (the girl whole, head to feet · brushing her teeth at the
washstand). Three were **deleted in the same turn**, all caught by the margin count rather than by eye: BDL **week 5**
(708 dark pixels inside the 14 px band — a floor line ran off both sides), BDL **week 6** (641 — the desk and a wall
line bled off the right edge) and basic-science **week 3** (168 — the table line crossed both margins). They stay on
the ledger to be re-made. First Term rebuilt at **8 plates · 127 pages · 129/129 Contents numbers · book and file
gates ok**; its one standing `sheet_check` flag remains the documented objective-pool behaviour, not a defect.
Ledger re-derived at **64 owed over 9 files**, scratch emptied, and the contact sheet died with the turn.

## 2 Sep 2026 — First Term sweep, turn two: BDL and basic-science both whole, eight-for-eight

The three turn-one rejects were re-made with the edge discipline written into the prompt (*no floor line, no wall
line, no table line, nothing touching the page edges*) and all eight passed the margin count at **0 dark pixels**
before a single import: BDL **weeks 5 and 6** (the boy carrying the tablet in two hands beside a charging phone and a
grown-up; the boy sitting straight at the lab desk) and basic-science **weeks 3–6, 8, 9** (the open first aid box with
its six things; the bandaged teddy; the knife, needle, broken cup and hot pot; the girl plastering her own knee; the
girl resting in bed with a cool cloth; the rock, the sorted stones and the plant in soil). With those, **First Term
basic-digital-literacy and basic-science are each 8 of 8 and leave the ledger**, the First Term book rebuilt at
**16 plates · 130 pages · 129/129 Contents numbers · book and file gates ok**, and the ledger re-derived at
**56 owed over 7 files** — all still First Term. The standing `sheet_check` flag on the term remains the documented
objective-pool behaviour. Scratch emptied of every raw and the contact sheet.

## 2 Sep 2026 — CRS freed from pictures; cultural-and-creative-arts swept whole

The owner freed a fifth subject: *"CRS does not need images."* It was added to `EXEMPT` in
`tools/backfill_ledger.py` (never in prose) and recorded as a closed decision in `80-AUTOLOOP.md`; the ledger
re-derived at **48 owed** with exempt notes rising to 92. The sweep then took **First Term
cultural-and-creative-arts**, eight plates, all craft and colouring drawn as objects with no people, and all eight
passed the margin count at 0 before import: the car, the print-art shapes (caterpillar, butterfly, fish, flower),
the friendly dinosaur, the pig, the straw-bead necklace and bracelet, the umbrella, the vegetable stamps with their
star/heart/ring prints, and the plasticine figure. **CCA is 8 of 8 and leaves the ledger**; the First Term book
rebuilt at **24 plates · 132 pages · 129/129 Contents numbers · book and file gates ok**, the ledger now
**40 owed over 5 files**, scratch emptied.

## 2 Sep 2026 — First Term mathematics-english-language swept whole, eight blank-card scenes

The language domain keeps every writing surface blank, so all eight First Term plates are object scenes with empty
cards, tiles and boards — the never-doubles shape — and every count was read against the lesson before import (five
vowel cards against a heap; four tiles; four sight-word cards; three cards and a car; three cards and a bell; three
cards on a shelf; telephone, fish and chair for ph/sh/ch sounds; a camera with a blank chart for photo/chart). All
eight passed the margin count at 0 and were imported; **mathematics-english-language is 8 of 8 and leaves the
ledger**, the First Term book rebuilt at **32 plates · 135 pages · 129/129 Contents numbers · book and file gates
ok**, the ledger now **32 owed over 4 files**, scratch emptied.

## 2 Sep 2026 — First Term mathematics-english-literacy swept whole, blank cards counted to the alphabet

Letter work keeps every surface blank, so the alphabet weeks are blank-card scenes whose counts were verified
against the letter runs before import — six cards for A–F, six in two rows for G–L, six folded for M–R, eight in a
row for S–Z — and the CVC weeks are object scenes (cat, hat, fan, van; hen, pin, dog; sun, mug, ladybird) plus an
open blank story book with three empty boxes for the storytelling week. All eight at 0 border-ink, all imported;
**mathematics-english-literacy is 8 of 8 and leaves the ledger**, the First Term book rebuilt at
**40 plates · 138 pages · 129/129 Contents numbers · book and file gates ok**, the ledger now **24 owed over
3 files** (numeracy, physical-and-health-education, prevocational-studies), scratch emptied.

## 2 Sep 2026 — First Term numeracy swept whole, every quantity counted at full size

The counting stream was drawn with exact-by-construction devices and each plate's quantities were counted at full
size before import: a blank number line; a full ten-frame plus three loose (13); two blank cards; a card with two
empty lines; 2+3 apples; 4+2 balls; five strawberries with two lifted into a basket (5−2); and a ten-frame holding
seven with three set apart (10−3). Every count read true, all at 0 border-ink; **mathematics-english-numeracy is
8 of 8 and leaves the ledger**, the First Term book rebuilt at **48 plates · 140 pages · 129/129 Contents numbers ·
book and file gates ok**, the ledger now **16 owed over 2 files** (physical-and-health-education,
prevocational-studies), scratch emptied.

## 2 Sep 2026 — First Term PHE swept whole, one consistent child in motion

Physical-and-health-education is all body, so all eight plates show the same girl (twin pigtails, T-shirt, shorts)
drawn whole and once: jogging on the spot, the egg-and-spoon walk, skipping over the rope, balancing on one leg,
marching to the tambourine, catching with two hands, the tucked forward roll on the mat, and kicking the ball. All at
0 border-ink, no duplicated panels, all imported; **PHE is 8 of 8 and leaves the ledger**, the First Term book
rebuilt at **56 plates · 143 pages · 129/129 Contents numbers · book and file gates ok**, the ledger now
**8 owed over 1 file** (prevocational-studies), scratch emptied.

## 2 Sep 2026 — Backfill sweep CLOSED: every owed plate in every term is now in the book

First Term prevocational-studies took the last eight: the basket of farm foods, farm-to-table, the four tools with
their working parts forward, yam/cocoa/orange, the three animals each with its young, timber-and-fruit trees with the
plank, the fishing boat with net and fish, and the crops of Nigeria. All at 0 border-ink, all imported;
**prevocational-studies is 8 of 8**, and `backfill_ledger.py` now prints **0 plate(s) owed · 0 subject file(s)**
(exempt notes 92). The sweep that began at 71 owed is closed. The three books, rebuilt and re-audited: First Term
**64 plates · 146 pages**, Second Term 72 · 160, Third Term 87 · 156, each **129/129 Contents numbers**; gates ALL
CLEAR on 2nd and 3rd, and on 1st the only flag is the standing documented objective-pool `sheet_check` behaviour.
The sole remaining owed work across the project is the **teacher's copy** for the three terms (60-ROADMAP §1).

## 2 Sep 2026 — Teacher's copy built for all three terms (`--edition teacher`), one honest gap

`build_term_doc.py --edition teacher` now emits `notes/<Class> - <Term> - TEACHER COPY.{md,docx}`: the pupil pages
plus each term paper's key as *letter and answer text* (the text read off the paper's own options, so the printed
answer is the option the child sees) and the Sections B & C marking points, a "**TEACHER COPY — not for pupils**"
front line, and a flipped `--strict` gate — pupil keeps "no answer printed", teacher demands "every paper has a
key". First/Second/Third build at exit 0 with 129/129 Contents and the page audit clean (158/172/169 pages); the
pupil edition is untouched. The weekly-worksheet answers are **not** printed: they were never stored as data (the
shuffle tool "does not need to know which option is right"), so printing them would be guessing — the gap is logged
in `70-OPEN-QUESTIONS.md` and the teacher copy gains worksheet keys only once they are authored as data.

## 2 Sep 2026 — Primary 1 begins: Basic Science First Term authored and green

The owner closed Nursery 2 and ordered *"Continue to primary one ASAP."* No new tools were needed — the pipeline is
class-agnostic. `notes/src/primary-1__1st-term/basic-science.md` (8 notes, weeks 1–6/8/9: road and safety, environment
and colours, shapes I and II, living things, non-living things, air and wind, soil) and its 30/10/5 paper were
authored to the house shape and validated: `spec_from_lines` 1 of 1, `sheet_check` all well formed, `make_exam
--strict` PASS (A=7 B=8 C=8 D=7, exploitable-longest 0), `polish_audit` 0 to fix. The note worksheets came out
correct-first (all-A), so `shuffle_worksheet_options.py` was run (24 items moved) and the inferred spread became
A=0 B=1 C=2 D=3, longest run 2. `gates.py --class "Primary 1" --term "1st Term"` is **ALL CLEAR** with the expected
`[half]` book line (1 of 11 subjects). Tracked in `PROJECT/77-PRIMARY-1.md`.

## 2 Sep 2026 — Primary 1 · basic-digital-literacy authored and green (2 of 11)

Eight notes (devices around us, the four basic parts, care and lab rules, abacus-to-today, Babbage and Lovelace,
hardware and software, keyboard and mouse, output devices and the microphone) plus a 30/10/5 paper
(A=8 B=8 C=7 D=7, exploitable-longest 0). One stem needed a trailing `?` to pass `sheet_check`
("Which of these is NOT a digital device?"); worksheets shuffled (48 items moved) to an inferred spread with longest
run 2. `gates.py --class "Primary 1" --term "1st Term"` ALL CLEAR with `[half]` book (2 of 11 subjects).

## 2 Sep 2026 — Primary 1 · CRS authored and green (3 of 11)

Eight Bible-story notes (calming the storm, walking on water, feeding the five thousand, healing the man with
leprosy, the paralyzed man and his friends, Jairus' daughter, Lazarus, cleansing the temple) plus a 30/10/5 paper.
Two sub-objectives first had a single answer (the gate needs two or more) and were re-cast as two-answer items;
`sheets` then read all well formed, `make_exam --strict` PASS (A=8 B=7 C=8 D=7), worksheets shuffled (72 items) to a
longest run of 2. `gates.py` ALL CLEAR with `[half]` (3 of 11 subjects).

## 2 Sep 2026 — Primary 1 · CCA authored and green (4 of 11)

Eight notes (lines, shapes and sizes, texture, art materials and tools, Nigerian culture, naming ceremonies, body
beautification, performing arts) plus a 30/10/5 paper; first pass was clean — `sheet_check` all well formed,
`make_exam --strict` PASS (A=7 B=8 C=7 D=8), worksheets shuffled (96 items) to longest run 2, `polish_audit` 0 to fix.
`gates.py` ALL CLEAR with `[half]` (4 of 11).

## 2 Sep 2026 — Primary 1 · General Knowledge authored and green (5 of 11)

Eight civics notes (myself, my family, my school, my classroom, my home and neighbourhood, community helpers, my
country Nigeria, being a good citizen) on the school-scheme provenance the Nursery 2 GK used, plus a 30/10/5 paper
(A=7 B=7 C=8 D=8). Two "My own work" lines first paired a grown-up with a writing verb (the deputise heuristic) and
were reworded so the child acts alone; `polish_audit` then 0 to fix, `gates.py` ALL CLEAR with `[half]` (5 of 11).

## 2 Sep 2026 — Primary 1 · Nigerian History authored and green (6 of 11)

Eight notes (what is history, sources of history, my own history, early people, migration and the Nok, major ethnic
groups, early kingdoms and empires, traditional occupations) plus a 30/10/5 paper; clean first pass — `sheet_check`
all well formed, `make_exam --strict` PASS (A=8 B=7 C=7 D=8), worksheets shuffled (144 items), `polish_audit` 0 to fix,
`gates.py` ALL CLEAR with `[half]` (6 of 11).

* **Primary 1 First Term — PHE authored (7 of 11).** Eight weeks: running/50m dash, shuttle run, local games (suwe/ten-ten/boju-boju), running posture, toilet hygiene + handwashing, personal hygiene, body care, keeping our surroundings clean. polish_audit caught 2 real fixes: 'environmental' is a banned grown-up register word (3 hits) and wk4 repeated wk1's 'posture' bullet — both reworded. sheet_check clean, make_exam --strict PASS (A=8 B=7 C=8 D=7, exploitable-longest 0), worksheets shuffled (168 items), polish 0-to-fix, gates ALL CLEAR.

* **Primary 1 First Term — Prevocational Studies authored (8 of 11).** Eight weeks: what pre-vocational studies is, simple farm tools, crops, animals we keep, simple food preparation, cleanliness at home, simple crafts, working safely. sheet_check clean, make_exam --strict PASS (A=8 B=7 C=7 D=8, exploitable-longest 0), worksheets shuffled (168 items), polish 0-to-fix, gates ALL CLEAR.

* **Primary 1 First Term — Social and Citizenship Studies authored (9 of 11).** Eight weeks: myself/identity, my family, my community, our culture, good values and manners, being a good citizen, our environment, living together in peace. Named to match the scheme (Social and Citizenship Studies) and the repo slug `social-and-citizenship-studies` — an initial `social-studies.md` was renamed before commit. sheet_check clean, make_exam --strict PASS (A=8 B=7 C=8 D=7, exploitable-longest 0), worksheets shuffled (168 items), polish 0-to-fix, gates ALL CLEAR.

* **Primary 1 First Term — Yoruba authored (10 of 11).** Eight weeks: kíki (greetings), ẹbí (family), ara (body), nọ́mbà (1-10), àwọ̀ (colours), ọjọ́ ọ̀sẹ̀ (days), ilé (home), ẹranko (animals). Two fixes: paper objective stems ending in 'means' got a '?' or blank (sheet_check), and wk6 'My own work' got a hands verb (draw a week chart). sheet_check clean, make_exam --strict PASS (A=8 B=8 C=7 D=7, exploitable-longest 0), worksheets shuffled (168 items), polish 0-to-fix, gates ALL CLEAR.

* **Primary 1 First Term — Mathematics & English authored (11 of 11) and the term book built.** The master (`data/curriculum_master.json`) defines this subject for Primary 1 as **two streams — MATHEMATICS and ENGLISH LANGUAGE** (not the three Nursery-style streams), so an initial numeracy/letter-work/language draft was replaced. MATHEMATICS weeks follow the master topics (whole numbers 1-100 and 101-9000, fractions, addition, subtraction); ENGLISH LANGUAGE follows phonemic awareness, spelling, comprehension, adjectives, phonics II, listening and speaking, tense, and word families. Three further fixes: Yoruba needed a ninth topic week (the master carries a wk11 topic) so WEEK 11 OÚNJẸ (food) was added; General Knowledge wk4 dropped the lesson-plan tell "teacher writes"; and one English paper objective was shortened so the right option is not the guessable long one (sheet_lint). Final state: sheet_check clean, both stream papers make_exam --strict PASS (exploitable-longest 0), sheet_lint 0 to re-balance, worksheets shuffled, polish 0-to-fix, **gates ALL CLEAR**. `build_term_doc` reports **0 problems** and "rule checks: all clear" — 97 lessons, 12 papers, key shape A=91 B=89 C=90 D=90. Book written to `notes/Primary 1 - First Term.{md,docx}` (figures: none yet — plates are the remaining backfill phase).

* **Primary 1 Second Term started — Basic Science authored (1 of 11).** Eight weeks extending First Term: plants, animals, sense organs, health and cleanliness, water, weather and seasons, light and sound, the sun/moon/stars. sheet_check clean, make_exam --strict PASS (A=8 B=8 C=7 D=7, exploitable-longest 0), sheet_lint 0, polish 0-to-fix, gates ALL CLEAR. New tracker `78-PRIMARY-1-2ND-TERM.md` records the master topics for the two Mathematics & English streams and Yoruba's ninth week (wk11).

* **Primary 1 Second Term — Basic Digital Literacy authored (2 of 11).** Eight weeks extending First Term: the desktop and icons, using the mouse, the keyboard, typing simple words, opening and closing a program, drawing with the computer, learning with the computer, safe habits. One fix (wk4 'My own work' needed a hands verb). sheet_check clean, make_exam --strict PASS (A=8 B=7 C=8 D=7, exploitable-longest 0), sheet_lint 0, polish 0-to-fix, gates ALL CLEAR.

* **Primary 1 Second Term — Christian Religious Studies authored (3 of 11).** Eight weeks extending First Term's miracles: the birth of Jesus, the shepherds and the wise men, Jesus as a boy, the baptism, the temptation, Jesus calls the first disciples, water into wine at Cana, Jesus loves the children. One fix (a paper answer shortened so it is not the guessable long one). sheet_check clean, make_exam --strict PASS (A=8 B=8 C=7 D=7, exploitable-longest 0), sheet_lint 0, polish 0-to-fix, gates ALL CLEAR.

* **Primary 1 Second Term — Cultural and Creative Arts authored (4 of 11).** Eight weeks extending First Term: colour (primary and secondary), drawing and colouring, modelling, craft work, music and songs, musical instruments, dance and movement, drama and role play. sheet_check clean, make_exam --strict PASS (A=8 B=7 C=7 D=8, exploitable-longest 0), sheet_lint 0, polish 0-to-fix, gates ALL CLEAR.

* **Primary 1 Second Term — General Knowledge authored (5 of 11).** Eight weeks extending First Term: my friends, days and months, time and the clock, weather and seasons, plants and animals around us, food and nutrition, safety at home and on the road, our festivals. sheet_check clean, make_exam --strict PASS (A=8 B=7 C=8 D=7, exploitable-longest 0), sheet_lint 0, polish 0-to-fix, gates ALL CLEAR.

* **Primary 1 Second Term — Nigerian History authored (6 of 11).** Eight weeks extending First Term: heroes and heroines, traditional rulers, festivals, crafts, music and dance, food and dress, our neighbours, national symbols. sheet_check clean, make_exam --strict PASS (A=8 B=7 C=8 D=7, exploitable-longest 0), sheet_lint 0, polish 0-to-fix, gates ALL CLEAR.

* **Primary 1 Second Term — Physical and Health Education authored (7 of 11).** Eight weeks extending First Term: jumping, throwing and catching, ball games, gymnastics and movement, rest and sleep, food and nutrition, safety in play, the value of exercise. One fix (wk8 repeated wk5's rest bullet). sheet_check clean, make_exam --strict PASS (A=7 B=8 C=7 D=8, exploitable-longest 0), sheet_lint 0, polish 0-to-fix, gates ALL CLEAR.

* **Primary 1 Second Term — Prevocational Studies authored (8 of 11).** Eight weeks extending First Term: planting a garden, caring for crops, animals and their young, preparing more foods, keeping the school clean, reusing waste, simple sewing, jobs in the community. sheet_check clean, make_exam --strict PASS (A=7 B=7 C=8 D=8, exploitable-longest 0), sheet_lint 0, polish 0-to-fix, gates ALL CLEAR.

* **Primary 1 Second Term — Social and Citizenship Studies authored (9 of 11).** Eight weeks extending First Term: friends and neighbours, the extended family, community leaders, our country Nigeria, rights and duties of a child, honesty, obedience and respect, caring for public property. Two fixes (a paper answer recast so it is not the guessable long one; wk5's 'obey' notebook word varied). sheet_check clean, make_exam --strict PASS (A=8 B=7 C=7 D=8, exploitable-longest 0), sheet_lint 0, polish 0-to-fix, gates ALL CLEAR.

* **Primary 1 Second Term — Yoruba authored (10 of 11).** Nine weeks (1-6, 8, 9, 11) extending First Term: numbers 11-20, clothes, school, market, town, actions, weather, fruits, things in the home. Fix: the 'You will learn to' bullet 'say the Yoruba word for each' repeated across weeks — varied per week. sheet_check clean, make_exam --strict PASS (A=7 B=7 C=8 D=8, exploitable-longest 0), sheet_lint 0, polish 0-to-fix, gates ALL CLEAR.

* **Primary 1 Second Term complete — Mathematics & English authored (11 of 11) and the term books built.** Two master streams: MATHEMATICS (multiplication, open sentences, money, length, time) and ENGLISH LANGUAGE (listening and telling stories, phonics practice, comprehension, plurals, fluency, songs and rhymes, adverbs, consonant digraphs). Two fixes (a repeated bullet in the maths stream; a subobjective that needed two real answers). sheet_check clean, both papers make_exam --strict PASS (exploitable-longest 0), sheet_lint 0, polish 0-to-fix, gates ALL CLEAR. `build_term_doc` 0 problems, "rule checks: all clear" — 97 lessons, 12 papers, key shape A=92 B=89 C=89 D=90. Pupil book and teacher copy written to `notes/Primary 1 - Second Term*`.

* **Primary 1 Third Term started — Basic Science authored (1 of 11).** Eight weeks: energy, push and pull, simple machines, growth and change, electricity and safety, magnets, waste and recycling, caring for our environment. One fix (wk9 repeated wk8's dustbin bullet once the bold markup was normalised). sheet_check clean, make_exam --strict PASS (A=8 B=7 C=7 D=8, exploitable-longest 0), sheet_lint 0, polish 0-to-fix, gates ALL CLEAR. New tracker `79-PRIMARY-1-3RD-TERM.md`.

* **Primary 1 Third Term — Basic Digital Literacy authored (2 of 11).** Eight weeks: storing our work, the internet, sending a message, learning software, computers in daily life, people who work with computers, being safe online, caring for our devices. Fixes: 'with a grown-up'/'ask a grown-up' phrasing tripped the deputise rule (reworded to 'a grown-up stays near'), and two wk8 bullets repeated wk2 once bold markup was normalised. sheet_check clean, make_exam --strict PASS (A=8 B=7 C=8 D=7, exploitable-longest 0), sheet_lint 0, polish 0-to-fix, gates ALL CLEAR.

* **Primary 1 Third Term — Christian Religious Studies authored (3 of 11).** Eight weeks: Jesus teaches us to love, the Good Samaritan, the lost sheep, the Lord's Prayer, Jesus is arrested, the death of Jesus, Jesus rises again, Jesus sends his disciples. sheet_check clean, make_exam --strict PASS (A=8 B=7 C=7 D=8, exploitable-longest 0), sheet_lint 0, polish 0-to-fix, gates ALL CLEAR.
