# 80 — The loop: keep going without asking

**Owner's instruction, 2 Sep 2026:** *"I'm okay with the way things are going now. Can you just make it a
loop that doesn't require you to stop and ask me to check and telling you to continue before you continue?
Until the 3 terms are fully ready, I'm not ready for any review. Please keep the ball rolling."*

So: no review cycles, no approval questions, no "shall I carry on".  Work advances every turn and each turn
ends with a few lines of fact.  Anything that would once have been a question is decided here, once, or is
written into `70-OPEN-QUESTIONS.md` and worked around in the safest way.

---

## 1. Resume rule

Any message at all — `continue`, `ride on`, `?`, a single word, or a correction — means: **run the next item
of the queue in §3, then report**.  Do not re-read the whole project, do not re-ask a settled decision, and
do not re-plan.  `PROJECT/00-START-HERE.md` and the queue below are the whole briefing.

A turn that ends mid-subject is normal.  The queue line carries the state (`3 of 8 plates`), so the next
turn picks up without a summary being requested.

## 2. The turn recipe, in this order

1. **Pictures for the subject being finished** — the ceiling is ten generations a turn, so spend them first,
   not last: subjects get their plates whole, in one run, which is what keeps the child's face and wardrobe
   consistent.  Generate into `assets/.scratch/`, flatten at the print threshold into one contact sheet,
   **read it**, and reject by eye: no grey fill that would print as a blob, no writing anywhere, no figure cut
   off by the edge, every person drawn head to feet, the object actually being the object the note names.
   *Two failure shapes keep coming back and both are a same-turn delete, not a repair:* a **black or grey
   blob** at the edge of the page (a table leg or a wall bled solid when the bilevel threshold bit in), and a
   **duplicated panel** — the model draws the same child twice side by side, so a scene with one child at a desk
   and one prop asks for `the child appears once — no second copy, no split panels, one scene only`.  A third
   shape bites when a **covering prop** is asked for — newspaper on a table, a patterned cloth, a poster on a
   wall — the model fills it with columns of fake print, which is writing; so name such props plain
   (`a plain folded cloth, no marks`) and reject anything that reads as text at the size it will print.
   *Measured on 2 Sep over the thirty backfill generations:* a child in the scene is where the duplication lives.
   The early wording (`only this one child appears`) lost 3 of 6 single-child sheets to doubled panels; the longer
   ward (`the child appears once — no second copy, no split panels, one scene only`) lost 3 of 14 — it helps, it
   does not fix it.  A sheet asked for **the work and the tools only**, with `no people, no hands, no arms
   anywhere`, has never doubled in **15 goes** (the fourth sweep turn made ten of them, ten-for-ten clean).  So:
   craft and device notes are drawn as objects, and a body is brought
   in only when the note is about the body — sitting straight, one hand on the mouse, one hand at the ear cup.
   *A third shape, seen 3 times in 10 on 2 Sep:* the model frames the scene itself — a thick black band at a
   corner, or the whole drawing pasted into a **mock-up of an open book** with grey page shadow.  Ask for a
   `flat drawing on a plain white page, no book, no page curl, no shadow, no frame line` and reject any sheet
   whose edge carries ink.  **Measure the edge, do not eyeball it** — count the dark pixels inside 14 px of
   each border: a First Term plate on 2 Sep read as perfect in the contact sheet and still had 139 of them
   where the table legs ran off the page, so its raw was deleted and the week left on the ledger.
   **A number in a picture is a claim about the lesson — owner, 2 Sep 2026: *"in the numeracy, consider the
   consistency of the picture with the lesson: 1 bundle of sticks should count 10."***  So for any counting,
   place-value or shape note, before a plate is accepted: **count what it shows, at full size, and read it against
   what the note says**.  A row of ten tied sticks must have ten ends you can point at — the model cannot keep ten
   sticks inside a bundle (measured: filed bundles held 7, 8 and 12+, and a "2, 3, 4, 5" set of bowls came back
   2, 3, 5, 6).  Safer devices: a **ten-frame** (a 2×5 box, one counter per cell) or **one row of ten separate
   objects tied at one end**; ask for the exact counts and say `no others anywhere on the page`, then count again.
   *A plate that has already been filed and fails this test is pulled, not kept*: delete the `![…](…)` line from the
   note, delete the PNG, drop its row from `assets/img/MANIFEST.jsonl`, rebuild, and `img_import --check` puts the
   week back on the ledger on its own.  Three Second Term numeracy plates were pulled this way on 2 Sep — the
   method works and is not a favour to ask for later.
   *A counted plate is counted by eye in the read.*  Asked for eight bundles the model drew seven, and asked for one
   bundle it drew two crossed; on a numeracy note the number **is** the lesson, so both went back.  Either leave the
   quantity out of the prompt and let the text carry it, or count every group in the read before accepting.
   *For a letter-work, language or numbers stream the plate shows the **scene** and leaves every writing surface
   blank* (blank page, empty box, blank flag; a clock with twelve marks and no numerals; a full stop as *one small
   solid round dot") — a
   ruled sheet with no letters, empty boxes, a blank caption strip; ask for `no letters, no words, no marks of
   any kind anywhere`, and where a mark must be shown (the full stop at the end of a line) ask for `one small
   solid dot` rather than a drawn punctuation sign.
2. `python3 tools/img_import.py --note … --week N --slug … --src … --alt "one plain sentence"` (give `cwd` as a
plain directory path — a command fragment in that field aborts the whole block with `status: shell_error` and
nothing is imported) — it encodes,
   files, declares the pixels, deletes the raw and puts the reference at the end of the note's
   `**Let us talk**` block.  One command, no hand-placing.
3. **Authoring**, when the subject is new: 8 notes in the house shape (`20-STYLE.md`), worksheet of 7 with
   **no bolded option**, then the 30/10/5 sheet — blank in every objective stem on the first pass, traps
   within a few letters of the right option, correct option first.  *A Mathematics & English stream file takes the
   shared title `# Mathematics & English — <Class> · <Term>` and a `**Stream: …**` line, exactly as First and
   Second Term do: two files whose titles bare() to the same subject get pasted into **both** parts, which is how
   the Third Term book came to hold 121 notes for 105 written.*
4. `python3 tools/gates.py --class "Nursery 2" --term "3rd Term"` — ten gates in one command, ending
   `ALL CLEAR`.  `[half]` on the build line is the expected `--strict` refusal while notes are still missing;
   it is not a failure and is not to be hidden.
5. `PROJECT/75-THIRD-TERM.md` (the table) and `PROJECT/40-HISTORY.md` (one paragraph) updated, scratch
   emptied, `du -sh .` inside the turn.
6. **Commit the verified state and push to the session branch before the turn ends.** The GitHub remote is
   the only durable copy — a sandbox can fill up or stall ("AI is taking too long") and be abandoned, so the
   branch must always hold the latest green build. On a fresh machine, `git clone` + checkout the branch +
   `pip install python-docx Pillow` + `gates.py` re-establishes state; nothing lives only in a workspace.
   Never leave the uploaded workspace zip in the live tree: it is already unpacked and is pure weight.

## 3. The queue

**Third Term, Nursery 2** — 13 subjects, one file each in `notes/src/nursery-2__3rd-term/`, one paper in
`data/exams/src/`, one plate per note.

| # | subject | state |
| --- | --- | --- |
| 1 | basic-science | ✅ 8 notes · paper ✅ · 8 plates |
| 2 | cultural-and-creative-arts | ✅ 8 · ✅ · 8 |
| 3 | christian-religious-studies | ✅ 8 · ✅ · 8 |
| 4 | basic-digital-literacy | ✅ 8 · ✅ · 8 |
| 5 | nigerian-history | ✅ 8 · ✅ · 8 |
| 6 | physical-and-health-education | ✅ 8 · ✅ · 8 |
| 7 | prevocational-studies | ✅ **done** — 8 notes, 30/10/5 paper, 8 plates, `ALL CLEAR` |
| 8 | social-and-citizenship-studies | ✅ 8 notes · paper ✅ · **7 of 8 plates** — week 5's raw was deleted with the turn; the plate joins the backfill sweep |
| 9 | yoruba | ✅ **9 notes · paper ✅ · no plates** (owner: the subject needs no images) |
| 10 | general-knowledge | ✅ **8 notes · paper ✅ · no plates** (owner: GK needs no images either) |
| 11 | mathematics-english-numeracy | ✅ 8 notes · paper ✅ · 8 plates |
| 12 | mathematics-english-literacy (letter work) | ✅ 8 notes · paper ✅ · 8 plates |
| 13 | mathematics-english-language (language domain) | ✅ **done** — 8 notes, paper `A=8 B=7 C=7 D=8`, 8 plates · **the term is shut**: 105/105 notes, 13/13 papers, `gates.py` ALL CLEAR |

**Third Term is closed** (2 Sep 2026): 13 of 13 subject files, 105 notes, 13 papers at 30/10/5, 87 plates, 156
pages, `build_term_doc --strict` *rule checks: all clear*, `gates.py` ALL CLEAR. What the completion pass did *not*
include is the **teacher's copy** (keys, marking guidance, worksheet answers — a separate clearly-named file per
term, never inside the pupil book); it is still owed for all three terms and is not part of the sweep below.

**Backfill, now the queue**: one plate for every note on First and Second Term that still has none, plus the
single social-and-citizenship week 5 plate in Third Term.  The list, in order, lives in **`76-BACKFILL.md`** and is
regenerated by `python3 tools/backfill_ledger.py` at the start and the end of every sweep turn — that command reads
`img_import --check`, subtracts the two exempt subjects and writes the table, so **no number is carried in this file**:
open `76-BACKFILL.md` (or run the tool and read its one summary line) for what is owed right now.
Nothing is authored in a sweep turn, so those turns run §2 steps 1, 2, 4 and 5 only, at **ten plates a turn**, and
the subject is finished before the next one starts.


**Repairs owed (found by counting on 2 Sep):** ~~all four taken the same day, see 40-HISTORY~~ — closed.  What the
counting pass left behind:
* **Second Term is whole** — every non-exempt note in the term now carries a plate (`img_import --check` prints no
  Second Term file at all).  Its book rebuilt at **72 plates · 160 pages · 129/129 Contents numbers · rule checks all
  clear**, and `gates.py` says ALL CLEAR for both terms.
* **Third Term · mathematics-english-numeracy weeks 1 and 5** — replaced in place: week 5 now shows a ball drawn as a
  sphere with a curved seam in the row of things to hold, and week 1 shows two equal halves and four equal quarters,
  with no "half" that is three-fifths.  Counted at full size before import; the term is still 87 plates and 156 pages.
* **One re-roll owed, on the First Term list:** `basic-digital-literacy` **week 1** (the five devices).  The raw came
  back correct — desktop, tablet, phone, watch, camera, all screens blank — but the **table legs ran off the bottom
  edge** (139 dark pixels inside 14 px of the border, measured), so it was deleted in the turn it was judged and the
  week stayed on the ledger.  Re-make with `the whole table inside the page, its legs ending above the bottom edge`.

## 4. Decisions that are closed. Do not re-ask, do not re-propose

* Layout: A4 **landscape, two columns**, as-is — no one-lesson-per-page rule, no never-split rule, no portrait
  or phone edition.
* Papers live **inside the book**; no per-subject exam pack; the Contents is a pupil feature in every book,
  with real numbers (`book_pages.py` proves them against the file).
* Style of images: **colouring-book line art**, bilevel PNG, ≤1200 px, placed at **12.5 cm** in a 13.1 cm
  column and billed to the page model from the manifest — `book_layout.IMAGE_WIDTH_CM` is the only width.
* **Every generation is QC'd and a reject is deleted in the turn that made it.**  A plate is never overwritten.
* Pupil text: never addresses a grown-up, never prints a key, never mentions calendar weeks.  `--strict`
  enforces all three; if it refuses, the note is wrong, not the gate.
* The word for a carer in pupil text is **grown-up**, not `adult` — it is the word six of the seven Third Term
  files already use.  `polish_audit` does **not** police that noun: its `ADULT` list catches adult *register
  phrases* (`as well as the`, `however`, `in order to`) and `DEPUTISE` only fires when the grown-up is made to
  *do the child's own work* ("help", "check", "read", "mark" within the sentence).  Naming an adult who does the
  dangerous job is safety content and is allowed.  So sweep the noun for consistency yourself at authoring
  time; do not wait for the audit and do not assume a `grown-up` line is a defect.
* **Yoruba carries no plates, in any term** — owner's instruction, 2 Sep 2026: *"Yoruba doesn't need images."*
  The subject is sound, word and song; nothing is drawn for it and `img_import --check` will still print its
  `0 of 9` shortfall lines, which are **exempt, not owed**. Do not generate Yoruba art, do not re-ask.
  The debt count therefore subtracts 9 in each of First Term, Second Term and Third Term.
* **General Knowledge carries no plates either, in any term** — owner, 2 Sep 2026: *"GK does not need images too."*
  So two of the thirteen subjects are word-only (Yoruba, General Knowledge) and `img_import --check` will print
  16 more `0 of 8` lines for them across First and Second Term. Those are **exempt, not owed**. Every other
  subject still gets one plate per note.
* **Nigerian History and Social & Citizenship Studies carry no plates either, in any term** — owner, 2 Sep 2026:
  *"Nigerian History and Social and Citizenship Studies need no images"*.  Four of the thirteen subjects are now
  word-only (Yoruba, General Knowledge, Nigerian History, Social & Citizenship Studies); `img_import --check` still
  prints their shortfall lines and `tools/backfill_ledger.py` subtracts them, which is how **the social-and-
  citizenship week 5 gap closed without a plate being made**.  The seven SCS plates already drawn for Third Term stay
  in that book — nothing is stripped out of a finished page; the exemption is about what is owed, not about erasing
  what exists.  `tools/backfill_ledger.py` holds the list in `EXEMPT`; add a subject there and re-run, never in prose.
* `polish_audit` counts **hard-wrapped lines**, not sentences, in a `p` block — and the `---` that closes a
  note is counted too. So a `**My own work**` or `**Words for my notebook**` block of **two** source lines is the
  safe house shape; three can tip it over the 1–3 ceiling on the last block of a note.
* Workspace: keep `PROJECT/` authoritative, `du -sh .` each turn, **nothing derived left behind** — raws and
  contact sheets die with the turn.  Past ~60 MB, prune first and say so.

## 5. When something genuinely cannot be decided here

Write it to `70-OPEN-QUESTIONS.md` with the two or three readings and the one taken, **take the reading that
keeps the book correct for a child** (never the one that saves time), continue, and put one line about it in
the turn's report.  A blocked question is a reason to choose conservatively, not a reason to stop.

## 6. Done means

* **subject**: 8 (or 9) notes at `0 to fix`, one 30/10/5 paper at `exploitable-longest: 0` with `sheet_lint`
  0, and **one plate on every note**, all four verified by `gates.py`.
* **term**: `build_term_doc --strict` passes with `rule checks: all clear`, `book_pages --audit` CLEAN with
  every Contents number agreeing, `img_import --check` CLEAN, 13/13 papers rendered — and then the teacher's
  copy for that term.
* **all three terms**: the two finished books rebuilt with their full picture sets, plus First and Second
  Term rebuilt once more after backfill so their page numbers are true for the books that carry the plates.

## 7. The report, at the end of each turn

Four to eight lines: what closed, the gate numbers that prove it, what the queue's next item is.  No question
at the end.  If a plate was rejected, say which and why; if a gate was gamed by a checker bug, say that the
checker was fixed and never the notes.
