notes/ — deliverables
=====================

Nursery 2 - First Term.docx   THE PRINTED BOOK. A4 landscape, two columns, one document per
                               class-term holding every subject offered to that class.
Nursery 2 - First Term.md      the same content as markdown — the working copy the .docx is built
                               from, kept for diffing and for grepping the rules.

Both are GENERATED. Do not edit them; edit the sources and rebuild:

    python3 tools/build_term_doc.py --class "Nursery 2" --term "1st Term" --strict

src/<Class>__<term>/<section>.md
                        One authored section per subject (Mathematics & English is three files, one
                        per stream). This is where the notes live. Format of every note:

                            ### WEEK n — TOPIC
                            *Depth: NERDC … Wn (pp …).*
                            **Main content**            the content — depth runs on the class ladder
                                                        (Nursery 2 8–12, P1 10–14, P2 14–22, P3 16–24,
                                                        P4 18–26 bullets; a revision note says
                                                        "What to revise").  The old **You will learn to**
                                                        objective block was deleted on 3 Sep 2026.
                            **Words for my notebook**  1–3 lines to copy
                            **Let us talk**             3–5 oral items
                            **Worksheet**               4 objective (A–D), 5 fill-in, 6 short answer, 7 theory
                            **My own work**             the assignment, done by the pupil alone

                        It is the pupil's own book: no teaching steps, no word "teacher" as an
                        instructor, no answer key anywhere, and no request to a parent or guardian.

The term papers
    data/exams/src/<class>__<term>__<section>.txt   hand-written question sheets, one line per item:
                                                    stem || correct option || trap || trap || trap
    python3 tools/spec_from_lines.py --all --class … --term …      sheet -> data/exams/*.json
    python3 tools/sheet_lint.py                                  right option must not be the long one
    python3 tools/make_exam.py data/exams/<name>.json --seed 0 --strict
                                                    -> data/exams/papers/exam-<name>.md (the pupil paper, no key)
                                                       data/exams/papers/exam-<name>.key.md (key + marking guide, never
                                                       printed in the book)
    Every subject: 30 objective + 10 sub-objective + 5 theory, theory at 2 marks, so 50 marks; the
    answer letters are assigned by make_exam so that they balance, never repeat, and never ABAB.

Weekly worksheets are re-lettered for the same reason:
    python3 tools/shuffle_worksheet_options.py --class … --term …   deterministic, needs no key
    python3 tools/check_worksheets.py --class … --term …            reports the letter spread

Status — First Term AND Second Term are complete. Next class: see PROJECT/60-ROADMAP.md §3.
The earlier state was: First Term is complete: 105 notes (all teaching weeks; weeks 7/10/11/12 carry no
note except the school's own Yoruba "Exam Preparation" row) and 13 papers (11 subjects, M&E in three
streams). Next class: Primary 1, same contract.

_teacher-edition/       superseded teacher-voiced drafts, kept only because two subjects (General
                        Knowledge, Nigerian History) were re-voiced from them.
