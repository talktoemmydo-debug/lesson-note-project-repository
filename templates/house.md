# House lesson-note template

Every note, in this order:

    ### WEEK n — <topic exactly as the master corpus prints it>
    **Reference:** <NERDC subject · class · term · week (page)  |  or: school-generated>
    **Objectives:** 3–5 observable verbs (name, point, count, write, compare, recite…)
    **Previous knowledge:** what the class already did, from the corpus (never invented)
    **Materials:** real objects first, then chart/picture, then board
    **Presentation:** Step 1 … Step 4, one short paragraph each; teacher says → pupils do
    **Board summary:** 2–4 lines the pupils copy (Nursery: teacher writes, pupils trace/say)
    **Evaluation:** 4–6 oral/practical items, answerable in class
    **Assignment:** take-home work the PUPIL does alone. Never address parents/guardians and
      never ask an adult to supervise, sign, help or provide materials. Tasks must be doable
      unaided: count, point, name, colour, circle, copy, recite.
    **Worksheet:** exam-style, 6 items (4 objective A–D, 1 fill-in, 1 short written/oral),
      drawn only from what this lesson taught — the pattern of an exam question on this topic.
    **Teacher's key:** answers for the worksheet only.

Depth rule: every "MUST COVER" line in `data/note_sources.json` for that week must appear in
the note; nothing beyond the matched NERDC week is required.

Subject exam at the end of each subject block: 30 objective + 10 sub-objective + 5 theory,
built from `data/exams/*.json` by `tools/make_exam.py`, which assigns the objective key so no
answer pattern can exist.
