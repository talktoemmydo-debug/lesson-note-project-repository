# Pictures — the house style, the measured budget, and the discipline that keeps the workspace alive

The owner's warning, in spirit verbatim: *the workspace may soon be overloaded as soon as you begin to
create and add pictures.* The previous workspace was abandoned because it hit the size budget, so the
budget here is a hard constraint, not advice.

## Settled by the owner, 2 Sep 2026

* **Style: colouring-book line art.** Chosen from four samples of one identical concept (the table below
  is the comparison that was made). Bold black outlines, no shading, no fill — the child colours it in.
* **Where they go: embedded in the book.** Not a separate picture pack, not merely cues. Which means the
  page model has to learn about images **first** (rule 7) or every Contents number breaks.
* **Children are drawn fully — faces and hands included** — but with a real QC step, in the owner's
  words: *"double check for errors and correct. Discard the ones that are not useful immediately to keep
  the workspace clean."* That is a standing instruction, so it is written into the workflow (rule 6), not
  left to taste.

## The house line — USE THESE WORDS

Append the block below to every prompt verbatim, changing only the scene sentence and the bracketed child
line. It is not decoration: it is what keeps 105 pictures looking like one book, and it was proven on a
second concept (`assets/samples/05-probe-scanner_LINE.png`) before being written down here.

```
STYLE (the house line, do not vary): a colouring-book page for five-year-olds. Bold, even black outlines
on pure white. No shading, no grey tones, no hatching, no colour fill of any kind, no background wash,
no shadow on the floor. Every shape closed, so a child can colour inside it. Thick friendly line, rounded
corners, no fine detail smaller than a fingernail, no cross-contour lines, no photorealism, no texture,
no clutter. Objects drawn true to life and identifiable from their silhouette alone, and exactly the
objects the note names. The child is five years old — [THE CHILD LINE: one per subject, kept identical
for every image in that subject, e.g. "a girl with short twin pigtails tied with ribbons, in a collared
shirt and a pinafore"] — with correct hands, five separated digits, and a calm, friendly, symmetrical
face. Nothing in the picture is writing: no letters, no numbers, no words, no labels, no captions, no
poster text, no chalkboard, no logo, no print on any screen or sheet of paper. No watermark, no frame, no
page border, no speech bubbles. Single scene, centred, landscape 4:3, generous white space around it.
Every figure is drawn entirely, head to feet, standing well inside the page with white space below the
feet — a body cut off by the edge of the picture is a reject, not a style. Say so in the prompt for any
scene of standing grown-ups, because the model crops them first and often.
```

**The drift to watch, measured:** twice out of two line-art generations, a prompt saying *girl in a
pinafore* came back as a **boy in a shirt**. Naming the hair and the collar is the fix; the QC gate checks
the figure every time. This is the likeliest way the book becomes inconsistent.

**The container for this style is a 1-bit PNG, not JPEG** — worth more than the whole style table. At
1200 px the same picture encodes to JPEG q84 **121 kB**, PNG-8/64 **111 kB**, thresholded bilevel **17 kB**
— with no line lost (ink kept ≥ 100 % under every container, so nothing broke). Pipeline:
`convert("L")` → `point(lambda v: 0 if v < 160 else 255, mode="1")` → `save(PNG, optimize=True)`. No
dithering: it costs size and puts grey speckle where a child expects white to colour inside.

**Size ceiling, measured:** the generator gives about 1200 × 896 px and does not enlarge. At one column
(12.3 cm) that is ~248 dpi and prints crisply; at full page width (26.5 cm) it is ~115 dpi and soft.
**Pictures therefore go column-width or smaller.** A full-width figure has to be composed at that ratio,
never stretched.

## The four options compared (kept for the record, with what each cost)

The concept was deliberately hard — *a child at a desk holding a land snail in one open palm and a yam in
the other, rice and half an egg on the desk, a mango tree and a hen behind* — face, hands, animal, plant,
food and depth at once. Tiles: `assets/samples/style-comparison.html`.

| option | style | cost of 105 images, as JPEG | chosen? | what the QC pass found |
| --- | --- | --- | --- | --- |
| 1 | colouring-book line art | 17.5 MB → **~1.8 MB as bilevel PNG** | ✅ **taken** | best print behaviour and the child colours it in; but a boy where the prompt said girl, a "window" that came out as a framed picture, one jagged bench leg |
| 2 | flat colour, limited palette | 9.7 MB | | most legible at column size; finger count slips, a stray curve on the lap, mangoes read as tomatoes |
| 3 | cut-paper collage | 16.4 MB | | nicest texture; snail sat on the forearm not the palm, brown dress on brown chair lost figure from ground |
| 4 | hand-drawn pencil and crayon | 30.2 MB | | the best *drawing*, and the only one that generated **fake writing** (poster captions, chalk marks) — forbidden by rule 4 |

## Budget math (measured, not guessed)

Snapshot caps: **≈128 MB and ≈10,000 files**. Baseline before pictures: **9.7 MB / 180 files**
(2 Sep 2026) — the fat being `data/note_sources.json` 1.9 MB, `data/scheme.json` 1.8 MB,
`uploads/NERDC-…html` 1.6 MB, `data/curriculum_master.json` 1.4 MB, the four book files 1.1 MB.

* **The raw generation is the killer, not the finished picture.** The four samples arrived at 0.79, 1.27,
  2.28 and 2.96 MB — 7.3 MB for four images, i.e. **~190 MB for one term**, straight through the ceiling.
  Same four, optimised: 308 kB. So the import step is not housekeeping, it is the only reason pictures are
  possible here at all. (Line art raw is cheaper — 0.28 MB — and finishes at 17 kB.)
* The .docx grows by roughly the images' size again, since it stores each file once inside the zip.
* File **count** is the binding limit for this style: ~105 images a term against 10,000 — comfortable,
  but never keep a second copy of an image "just in case".

## Rules

1. **One home: `assets/img/<class>/<term>/<subject>/week<n>-<slug>.png`.** Never scatter copies, never a
   "final/final2" pair, never images inside `notes/` or `data/`.
2. **One manifest, not one sidecar per image**: `assets/img/MANIFEST.jsonl`, one line per image —
   `{"file","px","kb","style","used_by":[…],"prompt","qc"}`. It is what a fresh session reads to know what
   exists. **An image not in the manifest does not exist** — it is scratch, and it is deleted at the end of
   the turn that made it. (Exists as of 2 Sep 2026 with 5 lines: four decision samples + the style probe.)
3. **Encode for print, at the size the book uses:** 1200 px long edge maximum (`tools/img_import.py` does
   the resize, and refuses a name already in use), bilevel PNG for line art
   (rule above); JPEG q84 only if a picture ever arrives with colour in it.
4. **Nothing in the picture may be writing.** Generated text is never legible and never correct, and in a
   book for five-year-olds it is a teaching error: no captions, no labels, no poster scribble, no
   chalkboard, no print on a screen, no numbers on a plate. If the scene wants a label, the *note*
   supplies the words and the picture stays mute. (Style 4 broke this on its first attempt.)
5. **Generate once, then re-encode — never "improve" by re-running the model.** Each call is a new
   drawing: re-running fills the workspace with near-duplicates and drifts the style across the book. Fix
   a bad picture by editing the file, or by one deliberate re-roll recorded in the manifest.
6. **Discard-immediately, the owner's instruction.** Every generation lands in `assets/.scratch/`, is
   inspected in the same turn, and either passes → encoded into `assets/img/`, manifest line added, scratch
   deleted; or fails → deleted in that same turn. **No rejected image survives a turn.**
7. **The page model pays for the picture before the picture ships** — *built, 2 Sep 2026.*
   `book_layout.flow_of` emits `("image", path, alt)`; `image_pt()` takes the **declared height in points**
   from `MANIFEST.jsonl` (the file itself is opened only when the manifest is silent) and `height()` bills
   it plus 8 pt of air, so `plan()` treats a figure as unsplittable — exactly as a sticky heading is
   treated.  A figure at `IMAGE_WIDTH_CM = 12.5` in a 13.1 cm column costs 193 pt, a fifth of a page:
   eight plates moved the Second Term book from 143 to 145 pages and every Contents number with it, which
   is why the billing came before the pictures.  **An unbilled image silently moves every page number the
   Contents promises**, so this rule stays before any of the others in force.
8. **`--no-images` always works** — *built, 2 Sep 2026.*  `build_term_doc.py --no-images` strips the
   references before the plan runs, so the text-only book prints page numbers true for *that* book; nothing
   is cached.  Verified by building the picture-free Second Term book and diffing it against the audited
   one: byte-identical.  A copier out of toner still gets a book.
9. **Nothing large and derived stays in the workspace.** No caches, no PDF renders beside sources, no raw
   generations. `build/`, `dist/`, `out/`, `node_modules/`, `.cache/`, `__pycache__/` are excluded from
   snapshots anyway — never put a source of truth in one.
10. **Prune before you add.** Any session ending over ~60 MB or ~3,000 files deletes scratch first and
    says so in its report; over ~90 MB, ship a finished class-term's images out to a folder the owner
    keeps locally and leave the manifest plus the sources here, so the book can always be rebuilt.

## The QC gate — what "double check for errors" means in practice

Each flag below is something a real image in this workspace did, not a hypothetical. An image that fails
any of them is deleted (rule 6), not shipped with a note.

* **The figure matches the subject's child line** — same age, same hair, same uniform, every image.
* **No limb ends without a hand** (the scanner probe's left arm did, hidden behind the lid).
* **Every cord connects to something** (the probe's mouse cable ran off the bottom edge and joined nothing).
* **The objects are the ones the note names** — e.g. Basic Digital Literacy asks the child to label
  "keyboard, mouse, screen and CPU" (`notes/src/nursery-2__2nd-term/basic-digital-literacy.md:115`), so a
  picture of a computer with no CPU box teaches the wrong set.
* **No writing anywhere in it** (rule 4).
* **Fingers counted** — five, separated, on each hand that is shown.
* **Shapes closed**, so colouring stays inside; nothing smaller than a fingernail that will fill with
  pencil and blob at print size.
* **The thing is the thing** — a snail has a spiral shell and two long eyestalks; a yam is long, thick and
  knobbly; a hen is not a chicken from a catalogue photo.

## What "safe" looks like, per term

One class-term of 105 line-art images: **~1.8 MB** in `assets/img` plus ~the same inside that term's .docx
plus 105 files and 105 manifest lines. At 11 MB / 191 files today, the whole of Nursery 2 — both terms,
210 pictures — costs under 8 MB. The style the owner chose is the cheap one, so the danger here is not
the budget, it is sloppiness: raw generations left lying around and un-inspected pictures reaching a book.
