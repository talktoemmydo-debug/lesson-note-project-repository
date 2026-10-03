#!/usr/bin/env python3
"""Run every gate this house owns, in one command, and say one word at the end.

    python3 tools/gates.py --class "Nursery 2" --term "3rd Term"

It exists so that a turn of work can be closed by reading four lines instead of remembering which of the
ten scripts prove what.  The order is the order of cheapness: the note audit and the picture manifest first,
because they cost nothing and catch almost everything; then the sheets; then the papers, which re-letter
themselves; then the book, which re-plans every page; then the file, which counts what the plan promised.

Nothing here edits anything.  `--strict` is tried on the build and, when the term is still being written,
the build's own refusal to call an unfinished term a book is reported as the expected thing it is — not as a
failure, and not hidden by silently dropping the flag.
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TERM_PRETTY = {"1st Term": "First Term", "2nd Term": "Second Term", "3rd Term": "Third Term"}
EXPECTED = "term still in progress"


def run(cmd: list[str]) -> tuple[int, str]:
    p = subprocess.run([sys.executable, *cmd], cwd=ROOT, capture_output=True, text=True)
    return p.returncode, (p.stdout + p.stderr).strip()


def keep(out: str, *pats: str) -> list[str]:
    want = re.compile("|".join(pats), re.I)
    return [ln.strip() for ln in out.splitlines() if want.search(ln)]


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--class", dest="cls", default="Nursery 2")
    ap.add_argument("--term", required=True)
    ap.add_argument("--verbose", action="store_true")
    a = ap.parse_args()
    cls, term = a.cls, a.term
    slug = cls.lower().replace(" ", "-")
    fails: list[str] = []
    notes: list[str] = []

    def gate(title: str, cmd: list[str], ok_when, report: list[str]) -> None:
        code, out = run(cmd)
        bad = ok_when(code, out)
        if bad == EXPECTED:                      # --strict refusing an unfinished term is the flag working
            print(f"  [half ] {title}  ← {bad}")
            return
        tag = "ok  " if not bad else "FAIL"
        print(f"  [{tag}] {title}" + (f"  ← {bad}" if isinstance(bad, str) and bad else ""))
        if bad:
            fails.append(title if not isinstance(bad, str) else f"{title}: {bad}")
        for ln in report:
            for l in keep(out, ln):
                notes.append(l)
        if a.verbose and out:
            print("        " + out.replace("\n", "\n        ")[:1400])

    print(f"gates   : {cls} · {TERM_PRETTY.get(term, term)}")
    gate("pictures  — every reference has a file, every file a manifest row",
         ["tools/img_import.py", "--check"],
         lambda c, o: "" if c == 0 else o.splitlines()[-1], ["manifest", "FAIL"])
    gate("notes     — the house shape, the register, nothing that prints an answer",
         ["tools/polish_audit.py", "--class", cls, "--term", term, "--list", "0"],
         # NOT `"0 to fix" in o`: that substring also sits inside "20 to fix", "30 to fix", "100 to fix",
         # so any count ending in zero passed the gate while the notes were still dirty.  Found 3 Sep 2026
         # on Nursery 2 First Term, which read ALL CLEAR at 20 to fix.  Anchor the zero to a word start.
         lambda c, o: "" if re.search(r"(?<![\d])0 to fix", o) else keep(o, r"\d+ to fix"), ["notes   :"])
    srcdir = ROOT / "data/exams/src"
    if srcdir.exists():
        srcs = sorted(srcdir.glob(f"{slug}__{term.lower().replace(chr(32), chr(45))}__*.txt"))
        gate(f"sheets    — {len(srcs)} written, sections and item shape",
             ["tools/spec_from_lines.py", "--all", "--class", cls, "--term", term],
             lambda c, o: "" if c == 0 else keep(o, r"PROBLEM|!!"), ["sheets expanded"])
        gate("sheets    — every objective keeps a blank or a question, no double blank",
             ["tools/sheet_check.py", "--class", cls, "--term", term],
             lambda c, o: "" if c == 0 else keep(o, r"PROBLEM|needs|!!"), ["all sheets"])
        gate("sheets    — no right option is the long one a child could guess",
             ["tools/sheet_lint.py"], lambda c, o: "" if re.search(r"re-balance: (?![1-9])0", o) else "lines to re-balance", [])
        for f in sorted((ROOT / "data/exams").glob(f"{slug}__{term.lower().replace(chr(32), chr(45))}__*.json")):
            gate(f"papers    — {f.stem.split('__')[-1]} balanced and re-lettered",
                 ["tools/make_exam.py", str(f.relative_to(ROOT)), "--seed", "0", "--strict"],
                 lambda c, o: "" if c == 0 else "make_exam refused", [])
        gate("worksheets— the notes' own 7-item sheets and the term's letter spread",
             ["tools/check_worksheets.py", "--class", cls, "--term", term],
             lambda c, o: "" if c == 0 else "worksheet check", ["term total:"])
    gate("book      — assembled, planned and stamped",
         ["tools/build_term_doc.py", "--class", cls, "--term", term, "--strict"],
         lambda c, o: ("" if c == 0 else
                       (EXPECTED if "no note for" in o else keep(o, r"PROBLEM|!!"))),
         ["^book", "^notes", "^figures", "^contents", "^papers", "^key shape", "^rule checks"])
    gate("file      — page breaks and Contents numbers agree with the .docx",
         ["tools/book_pages.py", "--class", cls, "--term", term, "--audit"],
         lambda c, o: "" if "CLEAN" in o else keep(o, r"MISMATCH|FAIL"), ["audit"])
    for n in notes:
        print("          ·", n[:150])
    print("gates   :", "ALL CLEAR" if not fails else f"{len(fails)} FAILURE(S) — " + " | ".join(fails[:4]))
    raise SystemExit(1 if fails else 0)
