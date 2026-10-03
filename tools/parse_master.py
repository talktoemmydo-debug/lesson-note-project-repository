#!/usr/bin/env python3
"""
parse_master.py — rebuild a machine-readable curriculum master corpus from the
readable HTML edition (Curriculum-Master-Compilation HTML).

RECOVERY parser: the original data/curriculum_master.json was not re-uploaded,
but the compilation HTML is its readable rendering, so every topic / calendar /
blank cell can be re-derived. Cells are kept verbatim.

Writes: data/curriculum_master.json

Row object: {"week": int|None, "kind": "topic"|"calendar"|"blank",
             "cells": {col: text}, "cell_kinds": {col: kind}}
Layouts:
  week-x-3-terms : NC subjects (Basic Science, CCA, CRS, Digital Literacy,
                   Nigerian History, PHE, PVS, SCS, Yoruba)
  stream-term    : Mathematics & English (class -> stream -> term -> week)
  gk-term        : General Knowledge (class -> term-block -> week w/ breakdown)
"""
import json, re, html, unicodedata
from pathlib import Path

SRC = Path(__file__).resolve().parent.parent / "uploads/Curriculum-Master-Compilation (1).html"
OUT = Path(__file__).resolve().parent.parent / "data/curriculum_master.json"

CLASSES = ["Nursery 2", "Primary 1", "Primary 2", "Primary 3", "Primary 4"]
CAL_WORDS = {"MID-TERM BREAK", "MID TERM BREAK", "MIDTERM BREAK", "MID-TERM",
             "REVISION", "EXAMINATION", "EXAMINATIONS", "CLOSING / AWARDS",
             "CLOSING/AWARDS", "CLOSING", "AWARDS", "OPENING", "BREAK"}


def unesc(s: str) -> str:
    s = re.sub(r"<br\s*/?>", " / ", s, flags=re.I)
    s = re.sub(r"<[^>]+>", " ", s)
    s = html.unescape(s).replace("\u00a0", " ")
    return re.sub(r"\s+", " ", s).strip()


def norm(s: str) -> str:
    """Fold to A-Z words for classification: punctuation/hyphens become spaces."""
    t = unicodedata.normalize("NFKD", s)
    t = t.replace("\u2013", "-").replace("\u2014", " ").replace("\u2019", "'")
    t = re.sub(r"[^A-Za-z]", " ", t).upper()
    return re.sub(r"\s+", " ", t).strip()


def kind_of(text: str) -> str:
    if not text:
        return "blank"
    t = norm(text)
    if t in {"", "BLANK", "BLANK IN SOURCE", "DASH"}:
        return "blank"
    if t in {"MID TERM BREAK", "MIDTERM BREAK", "MID TERM", "REVISION", "EXAMINATION",
             "EXAMINATIONS", "CLOSING AWARDS", "CLOSING", "AWARDS", "OPENING", "BREAK",
             "MID TERM REVISION", "MID TERM AND REVISION"}:
        return "calendar"
    return "topic"


def parse_table(tag_html: str):
    th = [unesc(x) for x in re.findall(r"<th[^>]*>(.*?)</th>", tag_html, re.S)]
    rows = []
    for tr in re.finditer(r"<tr([^>]*)>(.*?)</tr>", tag_html, re.S):
        attrs, inner = tr.group(1), tr.group(2)
        if "<th" in inner:
            continue
        cells = [unesc(c) for c in re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", inner, re.S)]
        if not cells:
            continue
        wk_raw = cells[0]
        week = int(wk_raw) if re.fullmatch(r"\d+", wk_raw) else None
        vals = cells[1:]
        cols = (th[1:] + [f"col{i+1}" for i in range(len(vals))])[:len(vals)]
        kinds = [kind_of(v) for v in vals]
        # row kind: blank if every cell blank; otherwise driven by the TOPIC column
        # (first content column), so a calendar week in a 2-column layout is not
        # masked by a non-empty breakdown cell.
        if all(k == "blank" for k in kinds):
            rk = "blank"
        else:
            primary = kinds[0] if kinds else "topic"
            if 'class="cal"' in attrs and primary != "topic":
                rk = "calendar"
            elif primary == "calendar":
                rk = "calendar"
            elif 'class="cal"' in attrs:
                rk = "calendar"
            else:
                rk = "topic"
        row = {"week": week,
               "week_label": wk_raw if week is None else str(week),
               "kind": rk,
               "cells": {c: v for c, v in zip(cols, vals)},
               "cell_kinds": dict(zip(cols, kinds))}
        rows.append(row)
    return rows


TABLE_RE = re.compile(r"<table[^>]*>.*?</table>", re.S)
H3_RE = re.compile(r'<h3 class="sub"[^>]*>(.*?)</h3>', re.S)
SUM_RE = re.compile(r"<summary[^>]*>(.*?)</summary>", re.S)
DETAILS_RE = re.compile(r"<details[^>]*>(.*?)</details>", re.S)


def top_level_h3(seg: str):
    """h3 matches that are NOT nested inside a <details> block."""
    opens = [m.start() for m in re.finditer(r"<details[^>]*>", seg)]
    closes = [m.end() for m in re.finditer(r"</details>", seg)]
    hits = []
    for m in H3_RE.finditer(seg):
        inside = sum(1 for o in opens if o < m.start()) > sum(1 for c in closes if c <= m.start())
        if not inside:
            hits.append(m)
    return hits


def split_by_h3(seg: str):
    hits = top_level_h3(seg)
    out = []
    for i, m in enumerate(hits):
        end = hits[i + 1].start() if i + 1 < len(hits) else len(seg)
        out.append((unesc(m.group(1)), seg[m.end():end]))
    return out


def tables_with_heading(seg: str, strip_details=True):
    """Return [{heading, rows}] for each table in seg, labelled by nearest h3/summary."""
    body = seg
    res = []
    # walk linearly over markers and tables
    marks = [(m.start(), "h3", unesc(m.group(1))) for m in H3_RE.finditer(body)]
    marks += [(m.start(), "sum", unesc(m.group(1))) for m in SUM_RE.finditer(body)]
    marks.sort()
    ti = [m for m in TABLE_RE.finditer(body)]
    for t in ti:
        heading = None
        for pos, kind_, txt in marks:
            if pos < t.start():
                heading = txt
        res.append({"heading": heading or "", "rows": parse_table(t.group(0))})
    return res


def parse_subject_section(slug: str, seg: str):
    hm = re.search(r'<h2 class="sec">(.*?)</h2>', seg, re.S)
    title = unesc(hm.group(1)) if hm else slug
    srcm = re.search(r'Source:([^<]*)', seg)
    subj = {"name": title, "slug": slug,
            "source_note": unesc(srcm.group(1)) if srcm else "",
            "classes": [], "extra_blocks": [], "preambles": []}

    pre = seg[:hm.end()] if hm else ""
    lead = re.search(r"<p class=\"small\">(.*?)</p>", seg, re.S)
    if lead and lead.start() < (hm.end() if hm else 0) + 400:
        subj["source_note"] = unesc(lead.group(1))

    for label, body in split_by_h3(seg):
        if label in CLASSES:
            node = {"class": label, "layout": None, "terms": {}, "streams": {}, "blocks": []}
            tables = tables_with_heading(body)
            # decide layout
            heads = {t["heading"] for t in tables}
            if any(re.match(r"(?i)^(first|second|third) term\b", h) for h in heads if h):
                # stream/term layout — use details summary as stream if present
                det = list(DETAILS_RE.finditer(body))
                if det:
                    node["layout"] = "stream-term"
                    for d in det:
                        sname = unesc(SUM_RE.search(d.group(1)).group(1)) if SUM_RE.search(d.group(1)) else ""
                        terms = [{"term": t["heading"] or f"table{i+1}",
                                  "rows": t["rows"]}
                                 for i, t in enumerate(tables_with_heading(d.group(1)))]
                        node["streams"][sname] = {"terms": terms}
                else:
                    node["layout"] = "term-block"
                    for i, t in enumerate(tables):
                        node["blocks"].append({"heading": t["heading"], "rows": t["rows"]})
            elif len(tables) == 1 and set(tables[0]["rows"] and
                                          list(tables[0]["rows"][0]["cells"].keys()) or []) <= \
                    {"1st Term", "2nd Term", "3rd Term"}:
                node["layout"] = "week-x-3-terms"
                for r in tables[0]["rows"]:
                    for term in ("1st Term", "2nd Term", "3rd Term"):
                        node["terms"].setdefault(term, []).append(r)
                node["table_rows"] = tables[0]["rows"]
            else:
                node["layout"] = "term-block"
                for t in tables:
                    node["blocks"].append({"heading": t["heading"], "rows": t["rows"]})
            if node["layout"] == "week-x-3-terms":
                # explode into per-term rows
                node["by_term"] = {}
                for term in ("1st Term", "2nd Term", "3rd Term"):
                    rr = []
                    for r in node["table_rows"]:
                        v = r["cells"].get(term, "")
                        rr.append({"week": r["week"], "week_label": r["week_label"],
                                   "kind": kind_of(v), "topic": v})
                    node["by_term"][term] = rr
            subj["classes"].append(node)
        else:
            subj["extra_blocks"].append({"heading": label,
                                         "tables": [{"rows": t["rows"]}
                                                    for t in tables_with_heading(body)]})
    return subj


def main():
    h = SRC.read_text(encoding="utf-8")
    secs = [(m.group(1), m.group(2)) for m in re.finditer(
        r'<section id="([^"]+)" class="card">(.*?)(?=<section id=|</main>|$)', h, re.S)]
    data = {"meta": {"rebuilt_from": SRC.name, "rebuilt_by": "tools/parse_master.py",
                     "classes": CLASSES,
                     "caveat": ("Recovered from the readable HTML edition. Topic/calendar/blank "
                                "cells verbatim. The old JSON's per-row 'teaching content' and the "
                                "Maths & English source_nerdc deep pointers were NOT rendered into "
                                "the HTML, so they are absent and must be re-derived from "
                                "data/scheme.json.")},
            "subjects": [], "appendices": {}}

    for slug, seg in secs:
        if slug == "matrix":
            t = TABLE_RE.search(seg)
            rows = parse_table(t.group(0)) if t else []
            data["matrix"] = rows
            continue
        if slug in ("ca", "p5", "sources"):
            key = {"ca": "current_affairs_snapshot", "p5": "primary5_bridge",
                   "sources": "source_map"}[slug]
            data["appendices"][key] = {
                "title": unesc((re.search(r'<h2 class="sec">(.*?)</h2>', seg, re.S) or
                               re.search(r"<h2[^>]*>(.*?)</h2>", seg, re.S)).group(1)),
                "blocks": tables_with_heading(seg)}
            continue
        data["subjects"].append(parse_subject_section(slug, seg))

    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")

    # ---- report ----
    print(f"{'subject':38s}{'layout':16s}{'classes':>8s}{'teach rows':>11s}{'cal':>6s}{'blank':>6s}")
    tot = cal = bl = 0
    for s in data["subjects"]:
        n = c = b = 0
        lays = set()
        for cn in s["classes"]:
            lays.add(cn["layout"])
            for blk in list(cn["by_term"].values()) if cn.get("by_term") else \
                       [t["rows"] for st in cn["streams"].values() for t in st["terms"]] + \
                       [x["rows"] for x in cn["blocks"]]:
                for r in blk:
                    if cn.get("by_term"):
                        n += 1
                        k = r["kind"]
                    else:
                        k = r["kind"]
                        n += 1
                    c += k == "calendar"
                    b += k == "blank"
        tot += n
        cal += c
        bl += b
        print(f"{s['name'][:38]:38s}{'+'.join(sorted(x or '-' for x in lays))[:15]:16s}"
              f"{len(s['classes']):8d}{n:11d}{c:6d}{b:6d}")
    print(f"{'TOTAL':38s}{'':16s}{'':8}{tot:11d}{cal:6d}{bl:6d}")
    print("\nwrote", OUT, OUT.stat().st_size, "bytes")


if __name__ == "__main__":
    main()
