#!/usr/bin/env python3
"""
book_layout.py — one classifier from markdown to the paragraph stream, and a page model over it.

Shared so the three tools cannot disagree about what sits on a page: `tools/docx_out.py` writes these
paragraphs, `tools/build_term_doc.py` writes the Contents list that points at them, and
`tools/book_pages.py` measures them against the written .docx. The numbers are stamped by this plan,
not by a word processor: `docx_out` is obliged to break the book where `plan()` says.

The stream is a list of tuples, one per Word paragraph:
    ("rule",)                                   a thin rule
    ("h1"|"h2"|"h3"|"h4", text)                  a heading
    ("toc", level, text[, page])                a Contents entry, with its page once stamped
    ("num", text) ("bullet", text) ("opt", text) numbered line, bullet, packed A)-D) option run
    ("label", text) ("para", text)              a bold label line, plain prose
"""
import json
import math
import re
from pathlib import Path

# body metrics — tools/docx_out.py reads its numbers from here
BODY = 10.5                     # pt
CHARS = 74                      # characters a column line is assumed to hold (real ~84)
OPTION_WIDTH = 88               # A)-D) options are packed onto a line up to this many characters
LINE = 13.45                    # pt, one body line: 10.5 pt Calibri x 1.22 x 1.05 line spacing
SPACE_AFTER = 2.0               # pt after every paragraph
STICKY_EXTRA = 3.0              # pt: a label hugs its list, so its room is the list's first line
COLUMN = 521.6                  # pt of usable height in a column (21.0 cm less 2 x 1.3 cm margins)
FILL = 0.90                     # never plan a page beyond 90 % of what it can hold
PAGE_PT = round(COLUMN * 2 * FILL, 1)      # the budget one page may take

# a figure is one of the house's own line-art plates; its width in the book is fixed so its height in
# points can be charged to the page before Word ever sees it (see image_pt)
IMAGE = re.compile(r"^!\[(?P<alt>[^\]]*)\]\((?P<path>[^)\s]+)(?:\s+\"[^\"]*\")?\)$")
IMAGE_WIDTH_CM = 12.5                 # a column is 13.1 cm here; 12.5 leaves the air a figure needs
PT_PER_CM = 28.3465
_ASSET_ROOT = Path(__file__).resolve().parent.parent

BULLET = re.compile(r"^\s*(?:[•·]\s+|-\s+)")
NUMBERED = re.compile(r"^\s*(\d{1,2})([.)])\s+(.*)$")
OPTION = re.compile(r"^\s*([A-D])\)\s+(.*)$")
TOC_LINE = re.compile(r"^( *)([-*])\s+(\*\*)?\[(?P<text>[^\]]+)\]\(#[^)]*\)(\*\*)?"
                      r"(?:\s*·\s*(?P<page>\d+))?\s*$")


def join_wrapped(lines):
    """markdown folds a sentence across source lines; a Word paragraph must not start where the
    author's editor happened to wrap, so a plain line is glued onto the plain line before it"""
    out = []
    for ln in lines:
        s = ln.strip()
        plain_prev = (out and out[-1].strip() and not re.match(
            r"^\s*(#|\*\*|[•·*-]\s|\(?[A-D]\)|\d+[.)]\s|\|)", out[-1])
            and not out[-1].strip().startswith("---"))
        plain_now = (s and not re.match(r"^\s*(#|\*\*|[•·*-]\s|\(?[A-D]\)|\d+[.)]\s|\||---)", s))
        if out and plain_prev and plain_now:
            out[-1] = out[-1].rstrip() + " " + s
        else:
            out.append(ln)
    return out


def pack_options(lines, i, width=OPTION_WIDTH):
    """consecutive A) B) C) D) lines are packed into as few lines as a column allows — four stacked
    options turn a two-page practice paper into a six-page one"""
    bits = []
    while i < len(lines) and OPTION.match(lines[i].strip()):
        m = OPTION.match(lines[i].strip())
        bits.append(f"{m.group(1)}) {m.group(2)}")
        i += 1
    packed, cur = [], ""
    for piece in bits:
        if cur and len(cur) + 3 + len(piece) > width:
            packed.append(cur)
            cur = piece
        else:
            cur = (cur + "   " + piece).strip()
    if cur:
        packed.append(cur)
    return packed, i


def nlines(text, width=CHARS, indent=0.0):
    """lines this paragraph takes once Word wraps it (pessimistic)"""
    if not text:
        return 0
    w = max(24, width - int(indent * 8))
    return sum(max(1, math.ceil(len(seg) / w)) for seg in text.split("\n"))


def flow_of(md):
    """classify the markdown into the stream of things the renderer writes"""
    lines = join_wrapped(md.splitlines())
    flow, n = [], 0
    while n < len(lines):
        ln = lines[n].rstrip()
        n += 1
        s = ln.strip()
        if not s:
            continue
        if s in {"---", "***", "___"}:
            flow.append(("rule",))
            continue
        m = IMAGE.match(s)
        if m:
            flow.append(("image", m.group("path"), m.group("alt")))
            continue
        if s.startswith("##") and s.lstrip("# ").strip().lower() == "contents":
            flow.append(("h2", "Contents"))
            started = False
            while n < len(lines):
                raw = lines[n].rstrip()
                s2 = raw.strip()
                m = TOC_LINE.match(raw)
                if not m:
                    if not s2:
                        n += 1
                        continue
                    # the italic lead-in above the list is prose, and it belongs to the page
                    if not started and not s2.startswith("#") and s2 not in {"---", "***", "___"}:
                        flow.append(("para", s2))
                        n += 1
                        continue
                    break
                started = True
                lvl = 1 if m.group(3) else 2
                item = ("toc", lvl, " ".join(m.group("text").split()))
                if m.group("page"):
                    item += (int(m.group("page")),)
                flow.append(item)
                n += 1
            continue
        if s.startswith("####"):
            flow.append(("h4", s.lstrip("# ").strip()))
            continue
        if s.startswith("###"):
            flow.append(("h3", s.lstrip("# ").strip()))
            continue
        if s.startswith("##"):
            flow.append(("h2", s.lstrip("# ").strip()))
            continue
        if s.startswith("#"):
            flow.append(("h1", s.lstrip("# ").strip()))
            continue
        if OPTION.match(s):
            n -= 1
            opts, n = pack_options(lines, n)
            flow.extend(("opt", o) for o in opts)
            continue
        m = NUMBERED.match(s)
        if m and not OPTION.search(s):
            flow.append(("num", f"{m.group(1)}{m.group(2)} {m.group(3)}"))
            continue
        if re.match(r"^\d+[.)]\s", s) and len(re.findall(r"\(?[A-D]\)", s)) >= 2:
            flow.append(("num", s))
            continue
        if BULLET.match(s):
            flow.append(("bullet", "• " + BULLET.sub("", s)))
            continue
        if re.fullmatch(r"\*\*[^*]+\*\*[.:]?", s):
            flow.append(("label", s))
            continue
        if s.startswith("|"):
            flow.append(("para", s.replace("|", "  ")))
            continue
        flow.append(("para", s))
    return flow


# what Word charges for each heading, per size it is drawn at (docx_out: BODY+6/+3/+2/+0.5)
HEAD_PT = {"h1": 29.0, "h2": 32.0, "h3": 29.0, "h4": 23.0}


_MANIFEST = None


def manifest():
    """`assets/img/MANIFEST.jsonl`, once.  The manifest declares a picture's size so the page model never
    has to trust a file that may not be where the build runs."""
    global _MANIFEST
    if _MANIFEST is None:
        _MANIFEST = {}
        f = _ASSET_ROOT / "assets/img/MANIFEST.jsonl"
        if f.exists():
            for ln in f.read_text(encoding="utf-8").splitlines():
                ln = ln.strip()
                if not ln:
                    continue
                try:
                    r = json.loads(ln)
                except json.JSONDecodeError:
                    continue
                if r.get("file"):
                    _MANIFEST[r["file"]] = r
    return _MANIFEST


def asset_path(rel):
    """Where a figure named in a note actually lives.  The page model and the Word renderer both ask this
    one function, so a book cannot bill a page for one file and print another."""
    q = Path(rel)
    return q if q.is_absolute() else _ASSET_ROOT / q


def image_px(rel):
    rec = manifest().get(rel)
    if rec and rec.get("px"):
        return int(rec["px"][0]), int(rec["px"][1])
    f = _ASSET_ROOT / rel
    if f.exists():                                     # declared first, measured second
        try:
            from PIL import Image
            with Image.open(f) as im:
                return im.size
        except Exception:
            pass
    return 1200, 896                                   # the house ratio, so a stray reference still fits


def image_pt(rel, width_cm=IMAGE_WIDTH_CM):
    w, h = image_px(rel)
    return round(width_cm * h / max(w, 1) * PT_PER_CM, 1)


def height(item):
    """points of a two-column page this paragraph takes — wrapping *and* the 2 pt after every
    paragraph, which is what makes the budget honest rather than hopeful. We assume 74 characters to
    a line where Calibri fits about 84, so a real page ends up emptier than planned: an empty corner
    is harmless, a line that spills is what would move a page number."""
    k = item[0]
    if k == "image":
        # a plate cannot be split across a page, so it is one unsplittable block the packer must place
        return image_pt(item[1]) + 8.0
    if k == "rule":
        return 4.0 + SPACE_AFTER
    if k in HEAD_PT:
        return HEAD_PT[k]
    if k == "toc":
        return LINE - 1.5
    if k == "label":
        return LINE + STICKY_EXTRA
    if k == "opt":
        return nlines(item[1], width=OPTION_WIDTH, indent=1.15) * LINE + SPACE_AFTER
    if k in ("num", "bullet"):
        return nlines(item[1], indent=0.62) * LINE + SPACE_AFTER
    return nlines(item[1]) * LINE + SPACE_AFTER


def sticky(item):
    """something that must not sit alone at the foot of a page: a heading keeps its first line, a
    label keeps its list. Word is told the same thing with keep_with_next, so the two must agree."""
    return item[0] in ("h1", "h2", "h3", "h4", "label")


def is_week(text):
    return bool(re.match(r"WEEK\s+\d", str(text).strip(), re.I))


def page_key(text):
    """how a Contents line and a heading decide they are talking about the same thing"""
    return re.sub(r"[^a-z0-9]", "", re.sub(r"\s+", " ", str(text)).strip().lower())


def plan(flow):
    """Pack the stream into pages and say which page every heading lands on.

    This is not a prediction of what Word will do — it is the instruction the renderer obeys: every
    index in `breaks` becomes one forced page break in the .docx, so Word is left no page of its own
    to choose and a page number is arithmetic. Two consequences are enforced here: a page is opened
    exactly once per index (the renderer cannot open it twice), and a heading or a bold label never
    sits alone at the foot of a page (Word's keep_with_next would push it down and move the number).

    Returns (pages, breaks, problems, info)."""
    breaks, pages, problems = set(), {}, []
    slot, used, page = [], 0.0, 1        # page 1 already holds the title block

    def break_before(i):
        """start a new page at flow index i — once, however many rules ask for it"""
        nonlocal slot, used, page
        if i in breaks:
            return
        breaks.add(i)
        page += 1
        slot, used = [], 0.0

    i, n = 0, len(flow)
    while i < n:
        item = flow[i]
        k = item[0]
        if k == "h1" and i:
            break_before(i)                      # a part (subject, practice paper) opens a page
        h = height(item)
        if h > PAGE_PT and k not in ("h1", "h2", "h3", "h4"):
            problems.append(f"a single paragraph is taller than a page ({h:.0f} pt against "
                            f"{PAGE_PT:.0f}): “{' '.join(str(x)[:44] for x in item[1:])}”")
        if slot and used + h > PAGE_PT:
            break_before(i)                      # the page is full
            h = height(item)
        if sticky(item) and i + 1 < n:            # and it must not be left standing alone
            nxt = next((flow[j] for j in range(i + 1, n) if flow[j][0] != "rule"), None)
            if nxt is not None and used + h + height(nxt) > PAGE_PT:
                before = page
                break_before(i)
                if page == before:
                    problems.append(f"“{str(item[1])[:44]}” and the line after it do not fit one page")
                h = height(item)
        slot.append(i)
        used += h
        if k == "h1" or (k == "h3" and is_week(item[1])):
            pages.setdefault(page_key(item[1]), page)
        i += 1
    info = {"items": n, "pages": page, "breaks": len(breaks),
            "toc_lines": sum(1 for it in flow if it[0] == "toc"),
            "page_pt": PAGE_PT, "fill": FILL, "capacity_pt": round(COLUMN * 2, 1)}
    return pages, breaks, problems, info


def stamp_contents(md, pages):
    """append the page number to every Contents line of the markdown twin"""
    out, changed = [], 0
    for ln in md.splitlines():
        m = TOC_LINE.match(ln.rstrip())
        if m and not m.group("page"):
            pg = pages.get(page_key(m.group("text")))
            if pg:
                ln = re.sub(r"\s*$", f" · {pg}", ln)
                changed += 1
        out.append(ln)
    return "\n".join(out) + "\n", changed


def numbered_flow(flow, pages):
    """return a copy of the Contents entries carrying their page number, so the .md and the .docx
    write the same thing and the plan can be checked against what it just produced"""
    out, stamped = [], 0
    for item in flow:
        if item[0] == "toc" and len(item) == 3:
            pg = pages.get(page_key(item[2]))
            if pg:
                item = (item[0], item[1], item[2], pg)
                stamped += 1
        out.append(item)
    return out, stamped


if __name__ == "__main__":
    import sys
    md = open(sys.argv[1], encoding="utf-8").read()
    flow = flow_of(md)
    pages, brk, problems, info = plan(flow)
    print(f"paragraphs {info['items']} · pages {info['pages']} · forced breaks {info['breaks']} · "
          f"contents lines {info['toc_lines']} · problems {len(problems)} · "
          f"headings placed {len(pages)}")
    for x in problems[:5]:
        print("   ", x)
