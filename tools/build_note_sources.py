#!/usr/bin/env python3
"""
build_note_sources.py — the depth layer for lesson-note generation.

For every teaching row of the school master corpus, resolve the NERDC 2025 material
that gives the note its minimum depth, and write one self-contained source block.

Matching rules (agreed 1 Sep 2026):
  * master class label is NOT used to pick the NERDC band — the school re-cut the
    scheme, shifting topics down a band (NERDC P2 -> master P1, P4 -> master P3 ...).
  * Basic Digital Literacy & Prevocational Studies: content was duplicated and
    redistributed into the lower classes, so their depth lives in the UPPER NERDC
    bands (P4/P5/P6) and is matched on CONTENT text, not on topic title.
  * Yoruba and General Knowledge are school-generated: no NERDC lookup at all.
  * Merged weeks: when the school folded NERDC's "I / II" (or consecutive weeks)
    into one week, the sibling week is pulled in so the note gets the full span.

Outputs
  data/note_sources.json   one record per teaching week, ready for the note writer
  reports/gaps.md            rows with thin / no resolved depth, for manual fill
"""
import json, re, sys, difflib, unicodedata, collections, argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MASTER = ROOT / "data/curriculum_master.json"
SCHEME = ROOT / "data/scheme.json"
OUT = ROOT / "data/note_sources.json"
GAPS = ROOT / "reports/gaps.md"

BAND = {"PRE-NURSERY": -1, "NURSERY 1": 0, "NURSERY 2": 1, "NURSERY 3": 2,
        "PRIMARY 1": 3, "PRIMARY 2": 4, "PRIMARY 3": 5, "PRIMARY 4": 6,
        "PRIMARY 5": 7, "PRIMARY 6": 8}
MASTER_BAND = {"Nursery 2": 1, "Primary 1": 3, "Primary 2": 4, "Primary 3": 5, "Primary 4": 6}

SCHOOL_GENERATED = {"Yoruba", "General Knowledge"}          # no NERDC depth source
UPPER_BAND_OK = {"Basic Digital Literacy", "Prevocational Studies (PVS)"}

SUBJ_MAP = {
    "Basic Science": ["BASIC SCIENCE", "BASIC SCIENCE AND TECHNOLOGY",
                      "BASIC SCIENCE & TECHNOLOGY", "PRE-SCIENCE"],
    "Cultural and Creative Arts (CCA)": ["CULTURAL AND CREATIVE ARTS", "CREATIVITY"],
    "Christian Religious Studies (CRS)": ["CHRISTIAN RELIGIOUS STUDIES"],
    "Basic Digital Literacy": ["BASIC DIGITAL LITERACY"],
    "Nigerian History": ["NIGERIAN HISTORY"],
    "Physical and Health Education (PHE)": ["PHYSICAL AND HEALTH EDUCATION",
                                            "PHYSICAL & HEALTH EDUCATION"],
    "Prevocational Studies (PVS)": ["PREVOCATIONAL STUDIES"],
    "Social and Citizenship Studies (SCS)": ["SOCIAL AND CITIZENSHIP STUDIES",
                                             "CIVIC EDUCATION", "SOCIAL HABITS"],
    "Mathematics & English": None,
}
STREAM_MAP = {
    "NUMERACY": ["MATHEMATICS", "NUMERACY"],
    "MATHEMATICS": ["MATHEMATICS", "NUMERACY"],
    "ENGLISH LANGUAGE": ["ENGLISH LANGUAGE", "LITERACY", "LITERACY (LANGUAGE DOMAIN)"],
    "LITERACY (LETTER WORK)": ["LITERACY (LETTER WORK)", "HANDWRITING"],
    "LITERACY (LANGUAGE DOMAIN)": ["LITERACY (LANGUAGE DOMAIN)", "ENGLISH LANGUAGE"],
}

STOP = set("""the a an of and or to in for on with by as is are be being been into from
that this these those i ii iii iv v vi vii viii ix x part introduction continued basic
nigeria nigerian our their his her its uses use type types what when which how""".split())


PARTISH = r"(?:parts?|section|lesson|week)s?\s*(?:&|and|\+)?\s*(?:\d+|[ivx]+)(?:\s*(?:&|and|\+)\s*(?:\d+|[ivx]+))?"


def norm(t):
    """compare-grade normalisation: case/punctuation insensitive, and the school and
    NERDC both slice topics into '(Part 1)' / '- Part 2' / 'I' / 'II & III', which
    must not defeat a match."""
    if not t:
        return ""
    t = unicodedata.normalize("NFKD", str(t))
    t = t.replace("\u2013", "-").replace("\u2014", "-").replace("\u2019", "'")
    t = t.lower()
    t = re.sub(r"\(([^)]*)\)", r" \1 ", t)                 # unbrace, then strip
    t = re.sub(PARTISH, " ", t)
    t = re.sub(r"\b(?:i|ii|iii|iv|v|vi|vii|viii|ix|x)\b\.?$", " ", t.strip())
    t = re.sub(r"\b(?:continued|cont)\b", " ", t)
    t = re.sub(r"[^a-z0-9' ]+", " ", t)
    return re.sub(r"\s+", " ", t).strip()


ROMAN = {"i":1,"ii":2,"iii":3,"iv":4,"v":5,"vi":6,"vii":7,"viii":8,"ix":9,"x":10}


def part_marks(t):
    """Which NERDC sub-parts a topic line refers to.

    The school prints 'God the Creator (Part 1)' as its own week and NERDC prints
    'God the Creator (Part 1)' / '(Part 2)' / '(Part 3)' across three weeks; a
    single marker must pin ONE part, a range marker ('Part 1 & 2', '1-3') must
    pull that range, and no marker at all means the school merged the whole span.
    Returns (set_of_part_numbers, mode) with mode in {'single','range','none'}.
    """
    if not t:
        return set(), "none"
    x = unicodedata.normalize("NFKD", str(t)).lower()
    x = x.replace("\u2013", "-").replace("\u2014", "-")

    def val(g):
        g = g.strip()
        return int(g) if g.isdigit() else ROMAN.get(g, 0) or None

    m = re.search(r"parts?\s*(\d+|[ivx]+)\s*(?:&|and|\+|-|to)\s*(?:part\s*)?(\d+|[ivx]+)", x)
    if m:
        a, b = val(m.group(1)), val(m.group(2))
        if a and b and b >= a:
            return set(range(a, b + 1)), "range"
    m = re.search(r"(?:parts?|lessons?)\s*\(?\s*(\d+|[ivx]+)\s*\)?(?![\s-]*(?:&|and|\+|-|to))", x)
    if m:
        v = val(m.group(1))
        if v:
            return {v}, "single"
    m = re.search(r"[\s-](i|ii|iii|iv|v|vi|vii|viii|ix|x)$", x.strip())
    if m:
        return {ROMAN[m.group(1)]}, "single"
    return set(), "none"


def split_cells(cells):
    """(topic, pointer, [(column, text)…]) by header name, not position."""
    topic, explicit, extra = "", "", []
    for cname, val in (cells or {}).items():
        if not val:
            continue
        lc = cname.lower()
        if lc == "topic" and not topic:
            topic = val
        elif "source" in lc or "nerdc" in lc:
            explicit = val
        else:
            extra.append({"column": cname, "text": val})
    if not topic and cells:
        topic = next(iter(cells.values()), "")
    return topic, explicit, extra


def squash(t):
    """space-free key, so word-splitting differences cannot defeat an exact hit."""
    return re.sub(r"[^a-z0-9]", "", norm(t))


def stem(w):
    """token-form only, so 'component/components', 'hero/heroines' style noise settles"""
    for suf in ("ies", "es", "s"):
        if w.endswith(suf) and len(w) - len(suf) >= 4:
            return w[:-len(suf)] + ("y" if suf == "ies" else "")
    return w


def toks(t):
    return [stem(w) for w in norm(t).split() if w not in STOP and len(w) > 3]


def split_phrases(text):
    # the school concatenates merged weeks with " AND " (e.g. "... TYPES AND SYMPTOMS
    # CAUSES AND CARE"), so that is a phrase boundary too, not prose.
    parts = re.split(r"[;|]|\n|\s+AND\s+(?=[A-Z])", text)
    out = []
    for p in parts:
        p = p.strip(" -•")
        # the school also concatenates merged weeks with a comma:
        # "NEURO MUSCULAR SKILLS: DANCING, SOMERSAULTING" is two NERDC weeks.
        if len(norm(p)) > 18 and ", " in p:
            for q in p.split(", "):
                if len(norm(q)) > 6:
                    out.append(q.strip(" -•"))
        if len(norm(p)) > 6:
            out.append(p)
    seen, keep = set(), []
    for q in out:
        k = squash(q)
        if k not in seen:
            seen.add(k)
            keep.append(q)
    return keep


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--min-line", type=float, default=0.70, help="min similarity for a content line hit")
    ap.add_argument("--max-weeks", type=int, default=5)
    ap.add_argument("--max-content-weeks", type=int, default=2,
                    help="cap when only content (not the title) matched")
    ap.add_argument("--gap", type=float, default=0.10,
                    help="accept content hits within this score of the best hit")
    a = ap.parse_args()

    master = json.loads(MASTER.read_text(encoding="utf-8"))
    scheme = json.loads(SCHEME.read_text(encoding="utf-8"))

    # ---- NERDC week inventory + line corpus -------------------------------
    weeks = []            # (idx, sec, week dict)
    lines = []            # (week_idx, text, norm, tokset)
    sec_cols = {}
    CAL = {"REVISION", "EXAMINATION", "EXAMINATIONS", "MIDTERM", "MID", "TERM", "BREAK",
           "CLOSING", "VACATION", "HOLIDAY", "OPENING", "TEST", "MOCK", "ASSESSMENT",
           "CONTINUOUS", "PROJECT", "REVIEW"}
    CAL_PAT = re.compile(r"(?i)\b(revision|examination|exam|mock|mid[- ]?term|midterm|"
                         r"closing|vacation|holiday|continuous assessment|end of (the )?term|"
                         r"end of (the )?year|assessment)\b")
    for si, sec in enumerate(scheme["sections"]):
        det = [c for c in sec["columns"]
               if norm(c) not in ("week", "topic", "w e k", "col 1") and norm(c)]
        sec_cols[si] = det
        for w in sec["weeks"]:
            wt = norm(w.get("topic", ""))
            # A revision / exam / mock week is not depth for a topic, whatever else
            # it mentions — it is the single worst source of nonsense in a generated note.
            if wt and (CAL_PAT.search(w.get("topic", "")) or all(x in CAL for x in wt.split())):
                continue
            wi = len(weeks)
            weeks.append({"si": si, "class": sec["class"], "subject": sec["subject"],
                          "term": sec["term"], "week": str(w.get("week", "")),
                          "topic": w.get("topic", ""), "pages": f"{sec['start_page']}-{sec['end_page']}"})
            body = " \n ".join(str(w["cells"].get(c, "")).strip() for c in det if w["cells"].get(c))
            for ln in re.split(r"\n|(?<=\.)\s+(?=[A-Z-])|•", body):
                ln = re.sub(r"^[\s\-–•\d.]+", "", ln).strip()
                if len(norm(ln)) > 8:
                    lines.append([wi, ln, norm(ln), set(toks(ln))])

    by_topic = collections.defaultdict(list)
    by_topic_sq = collections.defaultdict(list)
    for wi, w in enumerate(weeks):
        if norm(w["topic"]):
            by_topic[norm(w["topic"])].append(wi)
            by_topic_sq[squash(w["topic"])].append(wi)

    inv = collections.defaultdict(list)
    for li, (wi, txt, nt, ts) in enumerate(lines):
        for t in ts:
            inv[t].append(li)

    def line_candidates(qtoks):
        """candidate lines sharing >=2 query tokens, ranked by rarest-token posting list."""
        if not qtoks:
            return []
        freq = sorted(((len(inv.get(t, [])), t) for t in qtoks), key=lambda x: x[0])
        pool = None
        for _, t in freq:                        # intersect the rarest tokens first
            cur = set(inv.get(t, ()))
            pool = cur if pool is None else (pool & cur if pool & cur else pool)
            if pool and len(pool) < 400:
                break
        if not pool:
            pool = set()
            for _, t in freq[:2]:
                pool |= set(inv.get(t, ()))
        cnt = collections.Counter()
        for li in pool:
            cnt[li] = len(lines[li][3] & set(qtoks))
        return [li for li, c in cnt.most_common(400) if c >= 1]

    def match_weeks(topic, phrases, allowed_subs, want_band, force_upper, printed_band=None):
        hits = {}     # wi -> {"score":, "why":, "lines": set()}
        nt = norm(topic)
        for wi in by_topic.get(nt, []):
            if weeks[wi]["subject"] in allowed_subs:
                hits[wi] = {"score": 1.0, "why": "topic-exact", "lines": set()}
        for wi in by_topic.get(re.sub(r"\s+ii$", "", nt), []):
            if weeks[wi]["subject"] in allowed_subs:
                hits.setdefault(wi, {"score": 0.98, "why": "topic-exact", "lines": set()})
        for key, sc in ((squash(topic), 0.97), (squash(re.sub(r"\s+ii$", "", nt)), 0.96)):
            for wi in by_topic_sq.get(key, []):
                if weeks[wi]["subject"] in allowed_subs:
                    hits.setdefault(wi, {"score": sc, "why": "topic-exact(squashed)", "lines": set()})

        for ph in phrases + [topic]:
            k = squash(ph)
            if not k:
                continue
            for wi in by_topic_sq.get(k, ()):            # phrase == a NERDC topic
                if weeks[wi]["subject"] in allowed_subs:
                    hits.setdefault(wi, {"score": 0.93, "why": "phrase=topic", "lines": set()})
            if len(k) >= 10:      # phrase is one half of a merged NERDC title
                for wi, w in enumerate(weeks):
                    if w["subject"] not in allowed_subs or not w["topic"]:
                        continue
                    wt = squash(w["topic"])
                    if k != wt and (k in wt or wt in k) and wi not in hits:
                        hits[wi] = {"score": 0.92, "why": "phrase in topic", "lines": set()}
        cand_lines = collections.defaultdict(set)
        for ph in phrases + [topic]:
            qt = toks(ph)
            for li in line_candidates(qt):
                if weeks[lines[li][0]]["subject"] not in allowed_subs:
                    continue
                lt = lines[li][3]
                if not lt.issuperset(set(qt)) and len(set(qt) & lt) < max(2, len(set(qt)) - 1):
                    continue
                sm = difflib.SequenceMatcher(None, norm(ph), lines[li][2]).ratio()
                jac = len(set(qt) & lt) / max(1, len(set(qt) | lt))
                cov = len(set(qt) & lt) / max(1, len(set(qt)))   # query fully covered?
                sc = max(0.55 * sm + 0.45 * jac, 0.80 + 0.20 * cov)
                if sc >= a.min_line:
                    cand_lines[lines[li][0]].add(li)
        for wi, ls in cand_lines.items():
            best = max(difflib.SequenceMatcher(None, nt, lines[l][2]).ratio() for l in ls)
            agg = min(1.0, 0.45 + 0.06 * len(ls) + 0.4 * best)
            if wi not in hits or agg > hits[wi]["score"]:
                hits[wi] = {"score": round(agg, 3), "why": "content", "lines": ls}

        # ---- stage 2b: the school printed a NERDC class for this row, so look inside
        # that band specifically — a verbatim title match two bands below must not beat
        # the pointer the school itself wrote (this is what fixes M&E P4 "Fractions").
        if printed_band:
            for wi, w in enumerate(weeks):
                if w["subject"] not in allowed_subs or w["class"] != printed_band or not w["topic"]:
                    continue
                sm = difflib.SequenceMatcher(None, nt, norm(w["topic"])).ratio()
                if sm >= 0.72 and (wi not in hits or 1.20 > hits[wi]["score"]):
                    hits[wi] = {"score": 1.20 if sm >= 0.95 else round(1.05 + 0.15 * sm, 3),
                                "why": "printed-band", "lines": set()}

        # ---- stage 3: fuzzy topic similarity. Runs unless a strong title hit already
        # landed: content-only evidence must never outrank the printed topic title.
        strong_title = any(h["why"].startswith(("topic-exact", "printed-band", "phrase=topic"))
                           and h["score"] >= 0.95 for h in hits.values())
        if not strong_title:
            for wi, w in enumerate(weeks):
                if w["subject"] not in allowed_subs or not w["topic"]:
                    continue
                sm = difflib.SequenceMatcher(None, nt, norm(w["topic"])).ratio()
                if sm >= 0.76:
                    if wi not in hits or sm > hits[wi]["score"]:
                        hits[wi] = {"score": round(0.55 + 0.45 * sm, 3),
                                    "why": f"topic-fuzzy({sm:.2f})", "lines": set()}

        # ---- stage 4: rare-keyword fallback (content-heavy rows whose wording is
        # not a topic title, e.g. "Microphone, Proper use, care and functions.") ----
        if not hits:
            qwords = collections.Counter(t for t in toks(" ".join(phrases)) if len(t) > 4)
            shared = collections.defaultdict(set)
            for t, n in qwords.items():
                if len(inv.get(t, ())) > 900:          # skip common words
                    continue
                for li in inv.get(t, ()):
                    wi = lines[li][0]
                    if weeks[wi]["subject"] in allowed_subs:
                        shared[wi].add(t)
            ranked = sorted(shared.items(), key=lambda kv: (-len(kv[1]), kv[0]))
            for wi, ts in ranked[:8]:
                if len(ts) < 2:
                    continue
                sc = min(0.95, 0.55 + 0.12 * len(ts))
                if wi not in hits or sc > hits[wi]["score"]:
                    hits[wi] = {"score": sc, "why": "keyword:" + ",".join(sorted(ts)), "lines": set()}

        out = []
        for wi, h in hits.items():
            w = weeks[wi]
            b = BAND.get(w["class"], 4)
            off = b - want_band
            pref = 0
            if printed_band and w["class"] == printed_band:
                pref += 4                          # the school's own printed pointer wins
            if force_upper:
                if off < 0:
                    continue                       # redistribution: upper bands only
                pref = 2 if 0 <= off <= 3 else 1
            elif abs(off) > 3:
                continue                           # ignore far-away bands
            else:
                pref = 2 if abs(off) <= 1 else 1
            out.append((round(h["score"], 3) + 0.08 * pref, wi, h, off))
        TITLE = ("topic-exact", "printed-band", "phrase=topic", "topic-fuzzy")
        out.sort(key=lambda x: (0 if any(x[2]["why"].startswith(k) for k in TITLE) else 1, -x[0]))
        exact = [o for o in out if o[2]["why"].startswith("topic-exact")
                 or o[2]["why"] == "printed-band"]
        if exact:
            # the school's own title matched: keep those parts, plus at most one
            # clearly-strong neighbour. Do not sweep the whole band in.
            extra = [o for o in out if o not in exact and o[0] >= 1.18]
            out = (exact + extra[:1])
        else:
            # content-only evidence: accept only the top hits, and only those close
            # to the best score — a vague row like "What are crops;" otherwise drags
            # nine weeks of depth into one lesson.
            best = out[0][0] if out else 0
            gap = a.gap
            keep = [o for o in out if o[0] >= best - gap]
            out = keep[:a.max_content_weeks]
        out = out[:a.max_weeks]

        # marker pinning: a 'single' marker must select that NERDC part only
        mparts, mmode = part_marks(topic)
        if mmode == "single" and len(out) > 1:
            pinned = [o for o in out
                      if part_marks(weeks[o[1]]["topic"])[0] in (mparts, set()) and
                      part_marks(weeks[o[1]]["topic"])[1] != "none"
                      and part_marks(weeks[o[1]]["topic"])[0] == mparts]
            if pinned:
                out = pinned
                mmode = "pinned"

        # ---- merged continuation: when the school's row names extra parts that the
        # primary hit does not cover, pull the ADJACENT NERDC week whose title carries
        # them (e.g. master "SICKNESS: DEFINITION, TYPES AND SYMPTOMS CAUSES AND CARE"
        # = NERDC wk9 "…DEFINITION, TYPES AND SYMPTOMS" + wk10 "…CAUSES AND CARE…").
        primary = [o for o in out if o[2]["why"].startswith(("topic-exact", "topic-fuzzy",
                                                             "printed-band", "phrase"))]
        if primary:
            covered = norm(" ".join(weeks[o[1]]["topic"] for o in primary))
            for sc, wi, h, off in list(primary):
                w = weeks[wi]
                for j in (wi - 1, wi + 1, wi + 2):
                    if j < 0 or j >= len(weeks):
                        continue
                    w2 = weeks[j]
                    if j == wi or w2["si"] != w["si"] or w2["subject"] not in allowed_subs:
                        continue
                    if norm(w2["topic"]) and norm(w2["topic"]) not in covered:
                        # words the primary title did NOT cover, e.g. {causes, care}
                        resid = set(toks(topic)) - set(toks(covered))
                        phr = sorted(resid & set(toks(w2["topic"])))
                        if len(phr) >= 2:
                            covered += " " + norm(w2["topic"])
                            out.append((0.95, j, {"score": 0.95,
                                                 "why": "merged-continuation", "lines": set()}, off))

        # pull in the sibling week for merged I / II (or n / n+1) pairs
        #   only when the school did NOT already split the parts across its own weeks
        have = {wi for _, wi, _, _ in out}
        extra = []
        if mmode != "pinned":
          for sc, wi, h, off in out:
            w = weeks[wi]
            base = re.sub(r"\s+(?:i|ii)$", "", norm(w["topic"]))
            for j, w2 in enumerate(weeks):
                if j in have or w2["si"] != w["si"] or w2["term"] != w["term"]:
                    continue
                if re.sub(r"\s+(?:i|ii)$", "", norm(w2["topic"])) == base and base:
                    extra.append((sc - 0.05, j,
                                  {"score": sc - 0.05, "why": "merged-sibling", "lines": set()}, off))
                    have.add(j)
        return (out + extra)[:a.max_weeks + 4]

    recs, gap_rows = [], []
    stat = collections.Counter()
    for subj in master["subjects"]:
        name = subj["name"]
        school_gen = name in SCHOOL_GENERATED
        for cn in subj["classes"]:
            cls = cn["class"]
            wb = MASTER_BAND.get(cls, 4)
            rows = []
            if cn.get("by_term"):
                for term, rr in cn["by_term"].items():
                    for r in rr:
                        rows.append((term, None, r["week"], r["topic"], r["kind"], "", []))
            else:
                # keyed by HEADER NAME, never by position: for Mathematics & English the
                # 2nd column is a NERDC pointer, for General Knowledge it is the school's
                # own "Breakdown (Subtopics)" column — which is itself depth, not a pointer.
                def emit(cells, term, stream):
                    topic, explicit, school_depth = "", "", []
                    for cname, val in (cells or {}).items():
                        if not val:
                            continue
                        lc = cname.lower()
                        if lc == "topic" and not topic:
                            topic = val
                        elif "source" in lc or "nerdc" in lc:
                            explicit = val
                        else:
                            school_depth.append({"column": cname, "text": val})
                    if not topic and cells:
                        topic = next(iter(cells.values()), "")
                    return term, stream, week_of(cells), topic, school_depth, explicit

                def week_of(_cells):
                    return None

                for sname, st in (cn.get("streams") or {}).items():
                    for t in st["terms"]:
                        for r in t["rows"]:
                            topic, explicit, school_depth = split_cells(r["cells"])
                            rows.append((t["term"], sname, r["week"], topic, r["kind"],
                                         explicit, school_depth))
                for b in cn.get("blocks") or []:
                    for r in b["rows"]:
                        topic, explicit, school_depth = split_cells(r["cells"])
                        rows.append((b["heading"], None, r["week"], topic, r["kind"],
                                     explicit, school_depth))

            for item in rows:
                term, stream, week, topic, kind = item[:5]
                explicit = item[5] if len(item) > 5 else ""
                school_depth = item[6] if len(item) > 6 else []
                if kind != "topic" or not topic:
                    continue
                rec = {"subject": name, "class": cls, "stream": stream, "term": term,
                       "week": week, "topic": topic,
                       "explicit_source_note": explicit if explicit not in ("—", "-", "") else None,
                       "school_depth": school_depth,
                       "mode": None, "nerdc_weeks": [], "depth_text": [],
                       "method_text": [], "confidence": 0.0}
                if school_gen:
                    rec["mode"] = "school-generated"
                    rec["confidence"] = 1.0
                    if rec["school_depth"]:
                        rec["depth_text"] = [{"column": d["column"],
                                              "from": "school master corpus (own breakdown)",
                                              "text": d["text"]} for d in rec["school_depth"]]
                        stat["school-gen with own breakdown"] += 1
                    stat["school-generated"] += 1
                    recs.append(rec)
                    continue
                subs = SUBJ_MAP.get(name) if name != "Mathematics & English" \
                    else STREAM_MAP.get((stream or "").upper())
                force_upper = name in UPPER_BAND_OK
                if not subs:
                    rec["mode"] = "no-source-mapped"
                    gap_rows.append(rec)
                    stat["no-source-mapped"] += 1
                    recs.append(rec)
                    continue
                # if the master itself prints a NERDC class label, honour it as a strong prior
                pb = (explicit or "").strip().upper()
                pb = pb if re.fullmatch(r"(?:PRE-?NURSERY|NURSERY [1-3]|PRIMARY [1-6])", pb) else None
                ms = match_weeks(topic, split_phrases(topic), set(subs), wb, force_upper, pb)
                for sc, wi, h, off in ms:
                    w = weeks[wi]
                    rec["nerdc_weeks"].append({
                        "section_index": w["si"], "class": w["class"], "subject": w["subject"],
                        "term": w["term"], "week": w["week"], "topic": w["topic"],
                        "pages": w["pages"], "via": h["why"], "score": sc,
                        "band_offset": off})
                    for c in sec_cols[w["si"]]:
                        wk = next((x for x in scheme["sections"][w["si"]]["weeks"]
                                   if str(x.get("week")) == w["week"]), None)
                        v = (wk or {}).get("cells", {}).get(c)
                        if not v:
                            continue
                        entry = {"column": c,
                                 "from": f"{w['subject']} {w['class']} {w['term']} wk{w['week']}",
                                 "text": str(v).strip()}
                        # 'what to teach' vs 'how to run the lesson' — the note needs both,
                        # but only the former is the depth floor the audit enforces.
                        kindd = ("method" if re.search(r"(?i)activit|material|resource|instruction|"
                                                       r"assessment|evaluation|strategy|method", c)
                                 else "content")
                        (rec["method_text"] if kindd == "method" else rec["depth_text"]).append(entry)
                if rec["nerdc_weeks"]:
                    top = rec["nerdc_weeks"][0]
                    rec["mode"] = ("upper-band-redistribution" if force_upper else "nerdc-depth")
                    rec["confidence"] = top["score"]
                    stat["matched"] += 1
                    stat[f"offset {top['band_offset']:+d}"] += 1
                    if top["via"] == "content":
                        stat["via content"] += 1
                    elif top["via"] == "topic-exact":
                        stat["via topic-exact"] += 1
                else:
                    rec["mode"] = "no-hit"
                    stat["no-hit"] += 1
                    gap_rows.append(rec)
                recs.append(rec)

    OUT.write_text(json.dumps({
        "generated_by": "tools/build_note_sources.py",
        "rules": {"school_generated": sorted(SCHOOL_GENERATED),
                  "upper_band_only": sorted(UPPER_BAND_OK),
                  "band_offset_meaning": "positive = depth found in a HIGHER NERDC band than the master class",
                  "min_line": a.min_line, "max_weeks": a.max_weeks},
        "counts": dict(stat), "records": recs}, ensure_ascii=False, indent=1), encoding="utf-8")

    # ---- gap report ----
    L = ["# Depth-resolution gap report", "",
         f"Rows whose NERDC depth came back empty or thin (`min-line {a.min_line}`).",
         "Yoruba / General Knowledge are excluded by design (school-generated).", ""]
    thin = [r for r in gap_rows] + [r for r in recs if r["nerdc_weeks"] and r["confidence"] < 0.6]
    L.append(f"**{len(thin)}** of {len(recs)} teaching rows need manual depth.")
    per = collections.Counter((r["subject"], r["class"]) for r in thin)
    L += ["", "## Where the gaps are", "", "| subject | class | rows |", "|---|---|---|"]
    for (s, c), n in sorted(per.items()):
        L.append(f"| {s} | {c} | {n} |")
    L += ["", "## Row list", "", "| subject | class | term | wk | topic | status |", "|---|---|---|---|---|---|"]
    for r in thin[:400]:
        st = "no hit" if not r["nerdc_weeks"] else f"thin {r['confidence']:.2f}"
        L.append(f"| {r['subject'][:26]} | {r['class']} | {str(r['term'])[:12]} | {r['week']} | "
                 f"{r['topic'][:70].replace('|', '/')} | {st} |")
    GAPS.parent.mkdir(exist_ok=True)
    GAPS.write_text("\n".join(L) + "\n", encoding="utf-8")

    print("records:", len(recs))
    for k, v in sorted(stat.items(), key=lambda x: -x[1]):
        print(f"  {k:28s} {v}")
    print(f"\nwrote {OUT} ({OUT.stat().st_size:,} bytes)")
    print(f"wrote {GAPS} ({GAPS.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
