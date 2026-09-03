#!/usr/bin/env python3
"""
shuffle_worksheet_options.py — re-order the A)-D) options of every worksheet item in the notes.

Why this is needed: the pupil's book carries no answer key, so a week after week that puts the right
option in A or B still leaks the answer to a child who has noticed. The fix does not need to know which
option is right — a deterministic shuffle of the four makes the position of the right answer uniform by
construction, and the same file always shuffles the same way, so re-running never disturbs a finished
document.

Rules:
  * only items numbered 1 to 4 in a **Worksheet** block, and only when four options sit on one line;
  * an item is left alone when an option says "all of these", "none of", "both A", "A and B", or when
    the stem asks for an order (sorting those genuinely breaks the question);
  * markdown/blank lines are preserved byte-for-byte otherwise — this only rewrites that one line.

    python3 tools/shuffle_worksheet_options.py --class "Nursery 2" --term "1st Term" [--check]
"""
import re, random, argparse, collections
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "notes/src"
LET = "ABCD"
KEEP = re.compile(r"(?i)all of (?:these|the above)|none of|both [A-D]|[A-D] and [B-D]|"
                  r"in order|first,|arrange|sequence")
ORDER = re.compile(r"(?i)(in this order|arrange|put .* in order|from first to last|sequence of)")


def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def opts_of(line):
    """[(letter, text)] if the line is a four-option item, else None"""
    body = line.strip()
    if len(re.findall(r"\(?[A-D]\)", body)) != 4:
        return None
    parts = re.split(r"\s*\(?([A-D])\)\s*", body)
    if len(parts) < 8:
        return None
    lead = parts[0].strip()
    pairs = [(parts[i], parts[i + 1]) for i in range(1, 8, 2)]
    if [p[0] for p in pairs] != list(LET):
        return None
    return lead, [p[1].strip() for p in pairs]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--class", dest="cls", required=True)
    ap.add_argument("--term", required=True)
    ap.add_argument("--check", action="store_true", help="report only, change nothing")
    a = ap.parse_args()
    d = SRC / f"{slug(a.cls)}__{slug(a.term)}"
    moved = kept = 0
    dist = collections.Counter()
    for p in sorted(x for x in d.glob("*.md") if not x.name.startswith("_")):
        text = p.read_text(encoding="utf-8")
        out = []
        wk = 0
        for ln in text.splitlines():
            m = re.match(r"^###\s+WEEK\s+(\d+)", ln)
            if m:
                wk = int(m.group(1))
            o = opts_of(ln)
            if o and re.match(r"^\s*[1-4]\.\s", ln):
                lead, opts = o
                if KEEP.search(" ".join(opts)) or ORDER.search(lead):
                    kept += 1
                    out.append(ln)
                    continue
                rng = random.Random(f"{p.name}|{wk}|{lead}")
                order = list(range(4))
                rng.shuffle(order)
                if order == [0, 1, 2, 3]:
                    order = order[1:] + [0]          # never a no-op shuffle
                new = [opts[i] for i in order]
                dist[new.index(opts[0])] += 1        # where the old first option landed
                moved += 1
                pre = re.sub(r"\s*\(?[A-D]\)\s*.*$", "", lead)
                out.append(pre + " " + " ".join(f"{LET[i]}) {t}" for i, t in enumerate(new)))
                continue
            out.append(ln)
        if not a.check:
            p.write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"{'would move' if a.check else 'moved'}: {moved} items · left alone (order/all-of options): {kept}")


if __name__ == "__main__":
    main()
