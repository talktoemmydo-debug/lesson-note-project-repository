#!/usr/bin/env python3
"""
book_pages.py — audit the page numbers a book prints, and cross-check them if Word/LibreOffice exist.

The numbers in a Contents are produced by a plan (tools/book_layout.py) that the renderer is forced to
obey: every page boundary in the plan is a page break written into the .docx. That makes the numbers
arithmetic rather than a forecast — but only if the file really contains those breaks. So:

  --audit   read the built .docx, count the page breaks, and check that every Contents line names the
            page its heading actually sits on. Exits non-zero on any disagreement. Also reports how
            full the fullest page was, because the whole scheme rests on no page overflowing.
  --render  if a word processor is available (LibreOffice/Word), lay the book out for real, read each
            heading off the PDF pages and compare with the printed numbers. Agreement here means the
            pessimistic page model still had room; if it does not agree, lower FILL in
            tools/book_layout.py (or shorten the block named) and rebuild.

    python3 tools/book_pages.py --audit  --class "Nursery 2" --term "2nd Term"
    python3 tools/book_pages.py --render --class "Nursery 2" --term "2nd Term" [--soffice NAME]
"""
import argparse
import re
import shutil
import statistics
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
from book_layout import COLUMN, FILL, PAGE_PT, flow_of, height, page_key, plan   # noqa: E402

OUT = ROOT / "notes"
TERM_PRETTY = {"1st Term": "First Term", "2nd Term": "Second Term", "3rd Term": "Third Term"}
BREAK = re.compile(r'<w:br w:type="page"/>')


def book_paths(cls, term):
    pretty = TERM_PRETTY.get(term, term)
    return OUT / f"{cls} - {pretty}.md", OUT / f"{cls} - {pretty}.docx"


def para_text(xml_para):
    """the words of a paragraph, with a tab kept (the page number of a Contents line sits after one)"""
    s = ""
    for r in re.findall(r"<w:r\b.*?</w:r>", xml_para, re.S):
        if "<w:tab/>" in r:
            s += "\t"
        s += "".join(re.findall(r"<w:t[^>]*>([^<]*)</w:t>", r))
    return s


def docx_pages(docx):
    """walk the document once: which page each heading sits on, and what each Contents line claims"""
    with zipfile.ZipFile(docx) as z:
        xml = z.read("word/document.xml").decode("utf-8")
    page, claims, heads = 1, {}, {}
    for p in re.findall(r"<w:p\b.*?</w:p>", xml, re.S):
        if BREAK.search(p):
            page += 1
        raw = para_text(p)
        t = " ".join(raw.split())
        if not t:
            continue
        m = re.match(r"(.*)\t(\d+)$", raw.strip())
        if m and 'w:val="Heading' not in p:
            claims[page_key(m.group(1))] = int(m.group(2))
        if 'w:val="Heading' in p:
            heads.setdefault(page_key(t), page)
    return page, claims, heads


def audit_problems(cls, term):
    """the same check as --audit, as strings, so tools/build_term_doc.py can fail on it"""
    md_path, docx_path = book_paths(cls, term)
    if not docx_path.exists():
        return [f"{docx_path.name} was not written, so nothing was audited"]
    flow = flow_of(md_path.read_text(encoding="utf-8"))
    _pages, _brk, problems, info = plan(flow)
    real, claims, heads = docx_pages(docx_path)
    out = list(problems)
    for k, (says, sits) in {k: (v, heads.get(k)) for k, v in claims.items()
                            if heads.get(k) != v}.items():
        out.append(f"Contents says page {says}, the file puts it on page {sits}: {k[:40]}")
    if not claims:
        out.append("the Contents printed no page numbers")
    if real != info["pages"]:
        out.append(f"the plan counts {info['pages']} pages, the file has {real}")
    return out


def audit(cls, term):
    md_path, docx_path = book_paths(cls, term)
    if not docx_path.exists():
        raise SystemExit(f"{docx_path.relative_to(ROOT)} is not built — run tools/build_term_doc.py")
    flow = flow_of(md_path.read_text(encoding="utf-8"))
    pages, brk, problems, info = plan(flow)
    real, claims, heads = docx_pages(docx_path)
    bad = {k: (v, heads.get(k)) for k, v in claims.items() if heads.get(k) != v}
    tallest = 0.0
    slot = 0.0
    for i, it in enumerate(flow):
        if i in brk:
            tallest = max(tallest, slot)
            slot = 0.0
        slot += height(it)
    tallest = max(tallest, slot)
    print(f"audit     : {real} pages in the file · {info['breaks']} breaks the plan asked for · "
          f"{len(claims)} Contents lines numbered")
    print(f"            numbers agree with the file on {len(claims) - len(bad)} of {len(claims)} lines · "
          f"planned tallest page {tallest:.0f} pt of {PAGE_PT:.0f} pt "
          f"(a real page holds {COLUMN * 2:.0f} pt, planned to {FILL:.0%})")
    for k, (says, sits) in list(bad.items())[:6]:
        print(f"   MISMATCH  p.{says} claimed, p.{sits} in the file: {k[:44]}")
    for x in problems[:4]:
        print("   MODEL    ", x[:100])
    n_bad = len(bad) + len(problems) + (0 if real == info["pages"] else 1)
    if real != info["pages"]:
        print(f"   the plan counts {info['pages']} pages, the file has {real}")
    print("audit     :", "CLEAN" if not n_bad else f"{n_bad} problem(s)")
    return n_bad


# ----------------------------------------------------------------- optional real-render cross-check
def find_tool(*names):
    for n in names:
        if not n:
            continue
        if Path(str(n)).exists():
            return Path(n)
        w = shutil.which(str(n))
        if w:
            return Path(w)
    return None


def render_check(cls, term, soffice, pdftotext):
    _md, docx_path = book_paths(cls, term)
    pages = None
    with tempfile.TemporaryDirectory() as td:
        r = subprocess.run([str(soffice), "--headless", "--norestore",
                            f"-env:UserInstallation=file://{Path(td) / 'profile'}",
                            "--convert-to", "pdf", "--outdir", td, str(docx_path)],
                           capture_output=True, text=True, timeout=1800)
        pdf = Path(td) / (docx_path.stem + ".pdf")
        if not pdf.exists():
            raise SystemExit("the layout engine produced no PDF:\n" + (r.stdout + r.stderr)[-600:])
        txt = subprocess.run([str(pdftotext), "-layout", str(pdf), "-"],
                             capture_output=True, text=True, check=True).stdout
        pages, page = {}, 1
        for chunk in txt.split("\f"):
            for ln in chunk.splitlines():
                pages.setdefault(page_key(ln), page)
            page += 1
    _real, claims, heads = docx_pages(docx_path)
    agree = sum(1 for k, v in claims.items() if pages.get(k) == v)
    drift = {k: (v, pages.get(k)) for k, v in heads.items() if pages.get(k) and pages[k] != v}
    print(f"render    : {page - 1} pages from the layout engine · printed numbers match for "
          f"{agree} of {len(claims)} Contents lines")
    for k, (says, sits) in list(drift.items())[:6]:
        print(f"   DRIFT     printed p.{says}, engine put it on p.{sits}: {k[:40]}")
    if drift:
        print("            → the page model was too generous; lower FILL in tools/book_layout.py "
              "and rebuild (the plan is only exact while nothing overflows a page)")
    return len(drift)


def model(cls, term):
    md_path, _ = book_paths(cls, term)
    flow = flow_of(md_path.read_text(encoding="utf-8"))
    _p, brk, problems, info = plan(flow)
    heights, slot = [], 0.0
    for i, it in enumerate(flow):
        if i in brk:
            heights.append(slot)
            slot = 0.0
        slot += height(it)
    heights.append(slot)
    h = [x for x in heights if x > 0]
    print(f"model     : {len(h)} pages · median {statistics.median(h):.0f} pt · "
          f"p95 {sorted(h)[int(len(h) * .95)]:.0f} pt · max {max(h):.0f} pt · budget {PAGE_PT:.0f} pt · "
          f"{len(problems)} over budget")
    for x in problems[:4]:
        print("   ", x[:100])
    return len(problems)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--class", dest="cls", required=True)
    ap.add_argument("--term", required=True)
    ap.add_argument("--audit", action="store_true", help="check the .docx against the plan (default)")
    ap.add_argument("--render", action="store_true", help="also cross-check with a real engine")
    ap.add_argument("--model", action="store_true", help="report the page model only")
    ap.add_argument("--soffice", default=None)
    ap.add_argument("--pdftotext", default=None)
    a = ap.parse_args()
    if a.model:
        sys.exit(1 if model(a.cls, a.term) else 0)
    n = audit(a.cls, a.term)
    if a.render:
        lo = find_tool(a.soffice, "soffice", "libreoffice", "/usr/bin/soffice",
                       "/Applications/LibreOffice.app/Contents/MacOS/soffice")
        pt = find_tool(a.pdftotext, "pdftotext")
        if not lo or not pt:
            print("render    : skipped — no LibreOffice and pdftotext here (the audit above needs "
                  "neither; it reads the .docx itself)")
        else:
            n += render_check(a.cls, a.term, lo, pt)
    sys.exit(1 if n else 0)


if __name__ == "__main__":
    main()
