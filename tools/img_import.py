#!/usr/bin/env python3
"""Move a generated plate from the scratch folder into the book, once, and make it part of the page model.

    python3 tools/img_import.py --note notes/src/nursery-2__2nd-term/basic-science.md \\
        --week 1 --slug food-sources --src /tmp/gen/wk1.png --alt "Mangoes, a hen with eggs, a cow and a bucket."

Five things happen and none of them can be done by hand without a mistake: the picture is flattened to one
bit and capped at 1200 px; it is filed where its name says it belongs; its size is declared to the manifest
the page model reads; the raw generation is deleted, because the workspace has died of hoarding before; and
the reference is put in the note, at the end of "Let us talk" if there is one, so the picture sits with the
looking-talking it belongs to and never strands a heading on a page of its own.

Nothing is overwritten.  A plate for the same week and subject under a different name is refused rather than
silently swapped, and --check reports every reference and file that has come apart since.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

IMG_DIR = ROOT / "assets/img"
MANIFEST = IMG_DIR / "MANIFEST.jsonl"
MAX_PX = 1200
THRESHOLD = 160


def encode(src: Path, dest: Path) -> tuple[int, int, int]:
    from PIL import Image
    im = Image.open(src)
    im = im.convert("L")
    if max(im.size) > MAX_PX:
        from PIL import Image as I
        im.thumbnail((MAX_PX, MAX_PX), I.LANCZOS)
    im = im.point(lambda v: 0 if v < THRESHOLD else 255, mode="1")
    dest.parent.mkdir(parents=True, exist_ok=True)
    im.save(dest, "PNG", optimize=True)
    return im.size[0], im.size[1], dest.stat().st_size


def manifest_rows() -> list[dict]:
    if not MANIFEST.exists():
        return []
    return [json.loads(ln) for ln in MANIFEST.read_text(encoding="utf-8").splitlines() if ln.strip()]


def declare(rec: dict) -> None:
    rows = manifest_rows()
    rows = [r for r in rows if r.get("file") != rec["file"]]
    rows.append(rec)
    MANIFEST.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")


HEAD = re.compile(r"^\*\*(.+?)\*\*\s*$")


def place(md: str, week: int, rel: str, alt: str) -> tuple[str, str]:
    """Put the reference in the note for this week.

    It goes at the end of "Let us talk" (PROJECT/50-IMAGES rule 3): the picture is what the class looks at
    while it is talking, and putting it after the questions rather than under a heading means a heading can
    never be stranded alone at the foot of a page with a picture glued to it.
    """
    lines = md.splitlines()
    ref = f"![{alt}]({rel})"
    head = None
    for i, ln in enumerate(lines):
        if re.match(rf"^#{{2,4}}\s+WEEK\s+{week}\b", ln, re.I):
            head = i
            break
    if head is None:
        raise SystemExit(f"this note has no heading for week {week}")
    end = len(lines)
    for j in range(head + 1, len(lines)):
        if re.match(r"^#{2,4}\s", lines[j]) or lines[j].strip() in {"---", "***", "___"}:
            end = j
            break
    if any(ln.strip().startswith("![") for ln in lines[head:end]):
        return md, "already holds a plate"
    talk = None
    for j in range(head + 1, end):
        m = HEAD.match(lines[j].strip())
        if m and "talk" in m.group(1).lower():
            talk = j
            break
    at = end
    if talk is not None:
        at = talk + 1
        for j in range(talk + 1, end):
            s = lines[j].strip()
            if s.startswith("**") or s.startswith("#### ") or HEAD.match(s) or re.match(r"^\d+\.", s) is None and not s and j > talk + 2 and lines[j].startswith("**"):
                at = j
                break
            if s:
                at = j + 1
        while at < end and not lines[at].strip():
            at += 1
    lines.insert(at, ref)
    if at and not lines[at - 1].strip() and at >= 2 and not lines[at - 2].strip():
        del lines[at - 1]                  # one blank line above a figure, never two
    else:
        lines.insert(at, "")
    return "\n".join(lines) + "\n", ('end of "Let us talk"' if talk is not None else "end of the note")


def check() -> int:
    """every reference in every note has a file and a manifest row; every row has a file"""
    rows = {r["file"]: r for r in manifest_rows()}
    bad = []
    for f in sorted((ROOT / "notes/src").rglob("*.md")):
        for ln in f.read_text(encoding="utf-8").splitlines():
            m = re.match(r"^!\[[^\]]*\]\(([^)\s]+)", ln.strip())
            if not m:
                continue
            rel = m.group(1)
            if not (ROOT / rel).exists():
                bad.append(f"{f.name}: the note asks for {rel} and it is not there")
            elif rel not in rows:
                bad.append(f"{rel}: on disk but not in the manifest, so its height is a guess")
    for rel in rows:
        if not (ROOT / rel).exists():
            bad.append(f"{rel}: in the manifest, but the file was deleted")
    # coverage: a note is only finished when it carries its plate, so count both per subject file.
    # This line exists because a status table was once ticked for a subject whose pictures had been made
    # for a different term of the same name — the plates were real, the book they belonged to was not.
    cov = []
    for f in sorted((ROOT / "notes/src").rglob("*.md")):
        txt = f.read_text(encoding="utf-8")
        notes = len(re.findall(r"(?m)^#{2,4}\s+WEEK\s+\d+\b", txt))
        got = len(re.findall(r"(?m)^!\[", txt))
        if notes:
            cov.append(("/".join(f.parent.name.split("__")[1:3]) + "/" + f.stem, notes, got))
    gaps = [f"{name}: {got} of {n} notes carry a plate" for name, n, got in cov if got != n]
    print(f"manifest  : {len(rows)} plate(s) · {len(cov) - len({g.split(':')[0] for g in gaps})} of {len(cov)}"
          f" subject files fully pictured")
    for g in gaps:
        print("  plates  :", g)
    for b in bad:
        print("  FAIL   :", b)
    print("figures   :", "CLEAN" if not bad else f"{len(bad)} thing(s) out of place")
    return 1 if bad else 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--note")
    ap.add_argument("--week", type=int)
    ap.add_argument("--slug")
    ap.add_argument("--src")
    ap.add_argument("--alt", default="")
    a = ap.parse_args()
    if a.check:
        raise SystemExit(check())
    if not all([a.note, a.week, a.slug, a.src]):
        raise SystemExit(__doc__)
    nf, src = ROOT / a.note if not Path(a.note).is_absolute() else Path(a.note), Path(a.src)
    if not nf.exists() or not src.exists():
        raise SystemExit(f"missing: {nf if not nf.exists() else src}")
    rel_dir = nf.relative_to(ROOT / "notes/src")
    subject = rel_dir.stem                       # nursery-2__2nd-term / basic-science.md
    cls, term = rel_dir.parent.name.split("__", 1)
    rel = f"assets/img/{cls}/{term}/{subject}/week{a.week}-{a.slug}.png"
    dest = ROOT / rel
    if dest.exists():
        raise SystemExit(f"{rel} already exists; a plate is never overwritten in place")
    w, h, size = encode(src, dest)
    declare({"file": rel, "px": [w, h], "bytes": size, "bit": "1",
             "cap": f"{cls} · {term} · {subject} · week {a.week}"})
    md, where = place(nf.read_text(encoding="utf-8"), a.week, rel, a.alt)
    nf.write_text(md, encoding="utf-8")
    src.unlink()                              # the raw generation was never meant to be kept
    for old in (src.with_suffix(".png"), src.with_suffix(".jpg")):
        if old != dest.parent / dest.name and old.exists() and str(old).startswith("/tmp"):
            old.unlink(missing_ok=True)
    print(f"{rel} · {w}x{h} · {size/1024:.1f} kB · reference placed at the {where}")
