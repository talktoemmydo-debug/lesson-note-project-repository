#!/usr/bin/env python3
"""
extract_scheme.py — recover data/scheme.json from the NERDC interactive HTML.

The old workspace's `data/scheme.json` was never re-uploaded, but
`NERDC-2025-Scheme-Interactive.html` embeds its entire dataset as a JS object
(`window.SCHEME_DATA = {...}`), so the extract is recovered verbatim — sections,
week rows, frontmatter, and the 28-page sample lesson note.

Usage: python3 tools/extract_scheme.py [--check]
"""
import json, re, sys, argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "uploads/NERDC-2025-Scheme-Interactive.html"
OUT = ROOT / "data/scheme.json"
MARKER = "window.SCHEME_DATA = "


def extract(html_text: str) -> dict:
    i = html_text.find(MARKER)
    if i < 0:
        raise SystemExit(f"marker {MARKER!r} not found in {SRC}")
    blob = html_text[i + len(MARKER):]
    end = blob.find("\n</script>")
    if end < 0:
        raise SystemExit("could not find the end of the SCHEME_DATA block")
    blob = blob[:end].rstrip().rstrip(";")
    data = json.loads(blob)          # raises if the block is truncated
    if "sections" not in data:
        raise SystemExit("parsed payload has no 'sections' key — extraction is wrong")
    return data


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="print counts, do not write")
    a = ap.parse_args()

    data = extract(SRC.read_text(encoding="utf-8"))
    weeks = sum(len(s["weeks"]) for s in data["sections"])
    subjects = {s["subject"] for s in data["sections"]}
    with_detail = 0
    for s in data["sections"]:
        det = [c for c in s["columns"]
               if re.sub(r"[^a-z]", "", c.lower()) not in ("week", "topic", "col1")]
        for w in s["weeks"]:
            if any(str(w["cells"].get(c, "")).strip() for c in det):
                with_detail += 1

    print(f"{SRC.name}")
    print(f"  schema_version : {data.get('schema_version')}")
    print(f"  source         : {data.get('source')}")
    print(f"  classes        : {len(data['class_order'])} ({', '.join(data['class_order'])})")
    print(f"  subjects       : {len(subjects)}")
    print(f"  sections       : {len(data['sections'])}  (class x subject x term)")
    print(f"  week rows      : {weeks}   (of which {with_detail} carry a detail column)")
    print(f"  frontmatter    : {len(data['frontmatter'])} pages")
    print(f"  sample notes   : {len(data['sample_notes'])} pages "
          f"(pp {data['sample_notes'][0]['page']}-{data['sample_notes'][-1]['page']})")

    if a.check:
        return
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\nwrote {OUT} ({OUT.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
