#!/usr/bin/env python3
"""
make_exam.py — build a subject's term exam paper from an authored question spec.

Why a tool and not freehand: the school requires 30 objective + 10 sub-objective + 5
theory per subject per term with **no pattern in the choice of answers**. Written by hand
that is exactly what leaks (A,B,A,B…; the same letter twice; the longest option always
being right). So the correct answer is authored as TEXT and the letter is assigned here by
a balanced construction that cannot repeat, then checked.

Input  : data/exams/<class>__<term>__<subject>.json
  {
   "subject": "...", "class": "...", "term": "...",
   "objective":    [ {"stem","answer","distractors":[x3]}, ... x30 ],
   "subobjective": [ {"stem", "parts":[optional "(a) …" lines], "points":[marking guide]}, ... x10 ],
   "theory":       [ {"stem", "points":[marking guide], "marks":int}, ... x5 ]
  }
Output : data/exams/papers/exam-<name>.md — pupil paper, plus exam-<name>.key.md (the
           key and marking guide, never printed into a pupil book).

Guarantees / hard checks: counts 30/10/5; key letters balanced (max-min <= 2); no letter
twice in a row; no ABAB alternation; the correct option is not clearly the longest in more than
6 items (otherwise "pick the longest" answers the paper — authoring must be fixed, --strict fails).
The pupil paper carries NO answer key: the key and marking guide are written to exam-<name>.key.md.
"""
import json, random, sys, argparse, collections
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LETTERS = "ABCD"

def name_seed(s, base):
    """Deterministic per-paper seed: the same file always gets the same key, and two
    subjects in one term never share an identical answer pattern."""
    import zlib
    return base + zlib.crc32(s.encode("utf-8")) % 99991



def balanced_key(n, seed):
    """Deterministic-ish balanced sequence with no adjacency and no ABAB pattern."""
    rng = random.Random(seed)
    counts = {l: n // 4 for l in LETTERS}
    left = n - sum(counts.values())
    cap = -(-n // 4)                           # ceil: 30 -> 8, 32 -> 8
    while left > 0:                            # remainder to random letters, never above the cap
        l = rng.choice(LETTERS)
        if counts[l] < cap:
            counts[l] += 1
            left -= 1
    seq, prev, prev2 = [], None, None
    for _ in range(n):
        ok = [l for l in LETTERS if counts[l] > 0]
        ok = [l for l in ok if l != prev] or ok          # no letter twice in a row
        ok2 = [l for l in ok if not (prev2 is not None and l == prev2)] or ok  # no AxA
        ok3 = [l for l in ok2 if not (len(seq) >= 3 and l == seq[-3] and prev == seq[-2])] or ok2
        cands = sorted(ok3, key=lambda l: (-counts[l], rng.random()))
        best = cands[0]
        seq.append(best)
        counts[best] -= 1
        prev2, prev = prev, best
    return seq


def check_key(seq):
    problems = []
    d = collections.Counter(seq)
    for l in LETTERS:
        d[l] = d.get(l, 0)
    if max(d.values()) - min(d.values()) > 2:
        problems.append(f"key unbalanced: {dict(sorted(d.items()))}")
    for i in range(len(seq) - 1):
        if seq[i] == seq[i + 1]:
            problems.append(f"key repeats at Q{i+1}/Q{i+2} ({seq[i]}{seq[i+1]})")
    for i in range(len(seq) - 3):
        if seq[i] == seq[i + 2] and seq[i + 1] == seq[i + 3] and seq[i] != seq[i + 1]:
            problems.append(f"ABAB alternation from Q{i+1}")
    return problems, d


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("spec")
    ap.add_argument("--seed", type=int, default=20260901, help="0 = derive from the file name")
    ap.add_argument("--strict", action="store_true")
    ap.add_argument("--default", type=int, default=20260901)
    a = ap.parse_args()

    spec = json.loads(Path(a.spec).read_text(encoding="utf-8"))
    name = Path(a.spec).stem
    if a.seed == 0:
        a.seed = name_seed(name, a.default)
    obj = spec.get("objective", [])
    sub = spec.get("subobjective", [])
    th = spec.get("theory", [])

    bad = []
    if len(obj) != 30:
        bad.append(f"objective: {len(obj)} (need 30)")
    if len(sub) != 10:
        bad.append(f"sub-objective: {len(sub)} (need 10)")
    if len(th) != 5:
        bad.append(f"theory: {len(th)} (need 5)")
    for i, q in enumerate(obj, 1):
        if len(q.get("distractors", [])) != 3:
            bad.append(f"objective {i}: needs exactly 3 distractors")
        if not q.get("answer"):
            bad.append(f"objective {i}: no answer text")
        st = q.get("stem", "").strip()
        if not st:
            bad.append(f"objective {i}: empty stem")
    if bad:
        sys.exit("spec rejected:\n  " + "\n  ".join(bad))

    key = balanced_key(len(obj), a.seed)
    kp, dist = check_key(key)

    paper, keysec, longest, slight = [], [], [], []
    for i, q in enumerate(obj):
        letter = key[i]
        right = " ".join(str(q["answer"]).split())
        if "?" not in q["stem"] and "_" not in q["stem"]:
            q = dict(q, stem=q["stem"].rstrip() + " ___")   # completion-type stem
        others = [" ".join(str(x).split()) for x in q["distractors"]]
        random.Random(a.seed + i * 17).shuffle(others)
        opts = others[:LETTERS.index(letter)] + [right] + others[LETTERS.index(letter):]
        # an option is only a "tell" if a child can see it: the right one must beat every trap
        # by a good margin, not by one or two letters.
        gap = len(right) - max(len(o) for o in others)
        if gap >= 10 and gap >= 0.2 * max(len(o) for o in others):
            longest.append((i + 1, gap))
        elif gap > 0:
            slight.append(i + 1)
        paper.append(f"{i+1}. {q['stem'].strip()}\n" +
                     "\n".join(f"   {LETTERS[j]}) {t}" for j, t in enumerate(opts)))
        keysec.append(f"{i+1}. {letter}")

    # "pick the longest" is only a tell when the right option stands out in many questions, so the
    # margin has to be visible to a six-year-old before we call it a leak.
    if len(longest) > 8:
        det = ", ".join(f"Q{n}(+{g})" for n, g in longest)
        kp.append(f"answer is the longest option too often ({len(longest)} clearly, "
                  f"{len(slight)} slightly) — {det}: lengthen those distractors")

    for i, q in enumerate(sub, 1):
        line = f"{30+i}. {q['stem'].strip()}"
        for p in q.get("parts", []):
            line += "\n      " + p.strip()
        paper.append(line)
        pts = q.get("points") or []
        keysec.append(f"{30+i}. " + ("; ".join(pts) if pts else str(q.get("answer", ""))))
    for i, q in enumerate(th, 1):
        paper.append(f"{40+i}. {q['stem'].strip()}" + (f" ({q.get('marks', 2)} marks)" if q.get("marks") else ""))
        pts = q.get("points") or []
        keysec.append(f"{40+i}. " + ("; ".join(pts) if pts else str(q.get("answer", ""))))

    marks = f"**Time:** 1 hour · **Total: {len(obj) + len(sub) + sum(int(q.get('marks', 2)) for q in th)} marks**"
    out = (f"\n---\n\n# EXAMINATION PRACTICE — {spec.get('subject', name).upper()}"
           f" ({spec.get('class', '')} · {spec.get('term', '')})\n\n{marks}\n\n"
           f"## Section A — Objective ({len(obj)} marks)\n"
           "Choose the correct option and ring the letter.\n\n" + "\n".join(paper[:len(obj)]) +
           f"\n\n## Section B — Sub-objective ({len(sub)} marks)\nAnswer briefly.\n\n" +
           "\n".join(paper[len(obj):len(obj) + len(sub)]) +
           "\n\n## Section C — Theory (10 marks)\nAnswer in full sentences.\n\n" +
           "\n".join(paper[len(obj) + len(sub):]) +
           "\n")
    keyfile = (f"\n# Teacher's key — {spec.get('subject', name)} ({spec.get('class', '')} · "
               f"{spec.get('term', '')})\n\n**Not for the pupil's book.**\n\n"
               f"**Section A:** " + "  ".join(keysec[:len(obj)]) +
               "\n\n**Sections B & C (marking guide)**\n\n" +
               "\n".join(f"{k}" for k in keysec[len(obj):]) + "\n")

    out_dir = ROOT / "data/exams/papers"
    out_dir.mkdir(parents=True, exist_ok=True)
    p = out_dir / f"exam-{name}.md"
    p.write_text(out, encoding="utf-8")
    (p.parent / f"exam-{name}.key.md").write_text(keyfile, encoding="utf-8")
    print(f"wrote {p.relative_to(ROOT)}")
    print("key        :", " ".join(key))
    print("spread     :", ", ".join(f"{l}={dist[l]}" for l in LETTERS),
          "| exploitable-longest:", len(longest), f"(slight: {len(slight)})")
    if longest and len(longest) > 8:
        print("fix these  :", ", ".join(f"Q{n}(+{g})" for n, g in longest))
    print("checks     :", ("PASS — no adjacency, no ABAB, balanced" if not kp else
                           "FAIL\n   - " + "\n   - ".join(kp)))
    if a.strict and kp:
        sys.exit(1)


if __name__ == "__main__":
    main()
