"""Clause graph: how clauses relate to each other and to the library (no AI).

  python3 tools/library/graph.py report                 # writes library/graph-report.md (counts per source)
  python3 tools/library/graph.py context <file> <ref>   # what a drafter or verifier gets as context
  python3 tools/library/graph.py impact <file>          # requirements to re-verify when that source changes

Link kinds (one row each: kind, from source, from ref, to source, to ref, detail):
- refers_to     a cross-reference in the clause text ("see 5.21", "paragraph 4.3", "Annex 15", "Chapter 4",
                "§ 211.84", "21 CFR part 211"), resolved to a clause of the same source, or to a catalogued source
                of the same family (EU/EMA, PIC/S, FDA, WHO, ICH, INDIA); a document-level target has no to ref.
                A reference that cannot be resolved is kept with no to source and listed in the report.
- defines       a glossary or definition entry -> each clause of the same family that uses the term.
- same_text_as  two clauses of different sources whose word runs are near-identical (Jaccard >= SAME_TEXT), e.g.
                EU GMP and PIC/S PE 009, or WHO and Schedule M.
- maps_to       requirement -> clause, from the library mappings.
- stricter_than clause of a "stricter" mapping -> clause of a "same" mapping of the same requirement.
"""
import argparse
import csv
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent))
import model  # noqa: E402

SAME_TEXT = 0.9          # Jaccard similarity of 5-word runs for same_text_as
SHINGLE = 5
MIN_WORDS = 10           # shorter clauses are too generic to call the same text
COMMON_RUN = 40          # a run found in more clauses than this is boilerplate, not evidence
FAMILY = {"EU": "EU", "EMA": "EU", "PICS": "PICS", "FDA": "FDA", "WHO": "WHO", "ICH": "ICH", "INDIA": "INDIA",
          "JAPAN": "JAPAN", "BRAZIL": "BRAZIL"}
NUMBER = r"\d+(?:\.\d+)+(?:\s?\([a-z0-9]{1,4}\))*"          # 5.21, 211.84(b), 10.8.2
INTERNAL = re.compile(rf"(?i:\b(?:paragraphs?|sections?|points?|clauses?|items?|subsections?|see|cf\.?|under)\s+"
                      rf"|§§?\s*)({NUMBER})")
DOCUMENT = re.compile(r"(?i:\b(annex|chapter)(?:es|s)?\s+)(\d{1,2})\b|(?i:\bpart\s+)(I{1,3}|IV|[1-4])\b"
                      r"|(?i:\b21\s*CFR\s*(?:parts?\s*)?)(\d{3})(?:\.(\d+))?")
WORD = re.compile(r"[a-z0-9]+")


def family_of(row):
    return FAMILY.get(row["regulator"], row["regulator"])


def catalog():
    with open(model.ROOT / "sources" / "catalog.csv", encoding="utf-8") as f:
        return {r["file"]: r for r in csv.DictReader(f)}


def documents(sources):
    """{(family, "annex"|"chapter"|"part"|"cfr", number): file} from catalog titles; drafts and superseded
    versions are left out so a reference goes to the text in force."""
    out = {}
    for file, row in sorted(sources.items()):
        title, fam = row["title"], family_of(row)
        if re.search(r"draft|superseded", title, re.I):
            continue
        for kind, pattern in (("annex", r"^(?:EudraLex Vol 4 )?Annex (\d+)\b"), ("chapter", r"\bChapter (\d+)\b"),
                              ("part", r"^(?:EudraLex Vol 4 |PE 009-\d+ Guide to GMP - )?Part (I{1,3})\b(?! Chapter)"),
                              ("cfr", r"^21 CFR Part (\d+)\b")):
            m = re.search(pattern, title)
            if m and not (fam == "EU" and kind == "part" and m.group(1) == "III"):   # Part III is a collection
                out.setdefault((fam, kind, m.group(1)), file)
        if re.search(r"\bAnnexes\b", title):                # PIC/S: all annexes in one file, one section each
            out.setdefault((fam, "annexes"), file)
    for key, file in list(out.items()):                     # PIC/S: chapters are sections of Part I
        if key[1:] == ("part", "I"):
            out.setdefault((key[0], "chapters"), file)
    return out


def find_ref(tree, number):
    """The clause ref in one source that a number names: the same ref, a ref ending in " <number>", or for an
    eCFR section the section itself ("211.84" -> "211.84" or its first paragraph)."""
    number = re.sub(r"\s+", "", number)
    if number in tree:
        return number
    tail = [r for r in tree if r.endswith(" " + number)]
    if tail:
        return sorted(tail, key=len)[0]
    sub = sorted(r for r in tree if r.startswith(number + "(") or r.startswith(number + " ("))
    return sub[0] if sub else None


def references(source, segments, sources, docs, clause_trees):
    """refers_to links of one source: [(from ref, to source or None, to ref or None, detail)]."""
    row = sources[source]
    fam = family_of(row)
    own = {k for k, f in docs.items() if f == source}
    tree = clause_trees(source)
    out = []
    for seg in segments:
        if seg["kind"] == "toc":
            continue
        text, seen = seg["text"], set()
        for m in DOCUMENT.finditer(text):
            if m.group(1):
                key = (fam, m.group(1).lower(), m.group(2))
            elif m.group(3):
                key = (fam, "part", {"1": "I", "2": "II", "3": "III", "4": "IV"}.get(m.group(3), m.group(3)))
            else:
                key = ("FDA", "cfr", m.group(4))
            if key in own or key == ("EU", "part", "I"):
                continue                                    # the document naming itself; EU Part I is the guide
            target = docs.get(key)
            to_ref = None
            if target and m.group(5):                       # 21 CFR 211.84
                to_ref = find_ref(clause_trees(target), f"{m.group(4)}.{m.group(5)}")
            if not target and key[1] in ("annex", "chapter"):    # a section of a combined file (PIC/S)
                combined = docs.get((fam, key[1] + ("es" if key[1] == "annex" else "s")))
                if combined:
                    prefix = f"Annex {key[2]}" if key[1] == "annex" else f"Part I {key[2]}"
                    tree_c = clause_trees(combined)
                    hit = prefix if prefix in tree_c else next(
                        (r for r in tree_c if r.startswith(prefix + " ") or r.startswith(prefix + "A ")), None)
                    if hit:
                        target, to_ref = combined, hit
            if target == source and to_ref is None:
                continue                                    # the combined file naming its own section
            link = (seg["ref"], target, to_ref, m.group(0).strip())
            if link[1:3] not in seen:
                seen.add(link[1:3])
                out.append(link)
        for m in INTERNAL.finditer(text):
            number = m.group(1)
            hit = find_ref(tree, number)
            target = source if hit else None
            if not hit:                                     # another chapter of the guide, another CFR part
                key = (fam, "chapter", number.split(".")[0]) if fam in ("EU", "PICS") else \
                    ("FDA", "cfr", number.split(".")[0]) if fam == "FDA" else None
                other = docs.get(key) if key else None
                if other and other != source:
                    hit = find_ref(clause_trees(other), number)
                    target = other if hit else None
            if hit == seg["ref"]:
                continue
            link = (seg["ref"], target, hit, m.group(0).strip())
            if link[1:3] not in seen:
                seen.add(link[1:3])
                out.append(link)
    return out


GLOSSARY = re.compile(r"glossary|definitions?\b|terminology", re.I)
HEADING = re.compile(r"^\s*(?:\d{1,2}\.?\s+)?(?:glossary|definitions|terminology)\s*$", re.I)
NEXT_PART = re.compile(r"^\s*(?:\d{1,2}\.\s+[A-Z]|ANNEX\b|APPENDIX\b|REFERENCES\b|Annex \d)")
INLINE = re.compile(r"^\s{2,}([A-Za-z][\w ()/,'-]{2,70}?)\.\s+([A-Z].*)$")   # WHO: "   batch. A defined ..."
TOO_COMMON = 300            # a term used in more clauses than this is everyday GMP wording, not worth a link
NOT_TERMS = {"reference", "references", "introduction", "scope", "background", "abbreviations", "purpose",
             "objective", "objectives", "general", "principle", "summary", "annex", "appendix", "notes"}


def _is_term(line, after):
    """A glossary term line: short, starts with a capital, no full stop at the end, and followed by a longer line."""
    text = line.strip()
    return (0 < len(text) <= 80 and len(text.split()) <= 10 and text[0].isupper() and not text.endswith((".", ",", ";", ":"))
            and not re.search(r"\.{4,}|\s\d+$", text) and len(after.strip()) > len(text) * 0.6)


def glossary_entries(source, title=""):
    """[(term, definition)] of a PDF source's glossary or definitions section, read from the layout text, where
    each entry starts after a blank line with the term on its own line. A glossary document is read whole."""
    path = model.ROOT / "sources" / "official" / source
    if path.suffix.lower() != ".pdf" or not path.exists():
        return []
    import common
    lines = "\n".join(common.pdf_pages(path)).splitlines()
    if GLOSSARY.search(title):
        start, stop = 0, len(lines)
    else:
        starts = [i for i, l in enumerate(lines) if HEADING.match(l)]
        if not starts:
            return []
        start = starts[-1]                                  # the last one: the first is usually the contents
        stop = next((j for j in range(start + 2, len(lines)) if NEXT_PART.match(lines[j])
                     and not HEADING.match(lines[j])), len(lines))
    repeated = Counter(l.strip() for l in lines if l.strip())
    lines = ["" if repeated[l.strip()] >= 3 else l for l in lines]     # page headers and footers

    def prev_ends_sentence(i):
        before = next((lines[j] for j in range(i - 1, start - 1, -1) if lines[j].strip()), ".")
        return before.rstrip().endswith((".", ":")) or HEADING.match(before)

    inline = [(i, m) for i in range(start + 1, stop) if (m := INLINE.match(lines[i]))
              and len(m.group(1).split()) <= 6 and prev_ends_sentence(i)]
    if len(inline) >= 3:                                    # "term. Definition" entries on one line
        out = []
        for n, (i, m) in enumerate(inline):
            end = inline[n + 1][0] if n + 1 < len(inline) else stop
            body = [m.group(2)] + [lines[j].strip() for j in range(i + 1, end) if lines[j].strip()]
            out.append((m.group(1).strip(), " ".join(body)))
        return out
    out, i = [], start + 1
    while i < stop:
        nxt = next((j for j in range(i + 1, stop) if lines[j].strip()), None)
        if (i == 0 or not lines[i - 1].strip()) and nxt is not None and _is_term(lines[i], lines[nxt]):
            body, j = [], nxt
            while j < stop and not (not lines[j - 1].strip() and j + 1 < stop
                                    and _is_term(lines[j], lines[j + 1] if lines[j + 1].strip() else "")):
                body.append(lines[j].strip())
                j += 1
            definition = " ".join(b for b in body if b)
            if definition:
                out.append((re.sub(r"\s+", " ", lines[i].strip()), definition))
            i = j
        else:
            i += 1
    return out


def glossary_terms(source, segments, title="", entries_of=None):
    """[(ref, term, definition)] of a source's definition entries; ref is the glossary segment they belong to.
    entries_of(source, title) reads the entries (default: glossary_entries, from the PDF layout text)."""
    refs = [s["ref"] for s in segments if s["kind"] != "toc" and GLOSSARY.search(
        " ".join([s["ref"], s.get("section", ""), s.get("heading", "")]))]
    if not refs and GLOSSARY.search(title):
        refs = [next((s["ref"] for s in segments if s["kind"] != "toc"), "")]
    if not refs:
        return []
    out = []
    for term, definition in (entries_of or glossary_entries)(source, title):
        name = re.sub(r"\s*\(.*?\)", "", term).strip(" -")        # "Batch (or Lot)" -> "Batch"
        if GLOSSARY.search(name) and len(name.split()) <= 2 or ". " in name or name.lower() in NOT_TERMS or \
                re.match(r"(?:Appendix|Annex|Part|Chapter|Section|Table|Figure)\b", name):
            continue                                        # headings, not terms
        if 2 <= len(name.split()) <= 8 or (len(name.split()) == 1 and len(name) >= 6):
            out.append((refs[0], name, definition))
    return out


def definitions(families, segments_of, sources, entries_of=None):
    """defines links: (glossary source, entry ref, using source, using ref, term) for every clause of the same
    family whose text uses the term as whole words."""
    out = []
    for fam, files in families.items():
        terms = [(f, ref, term) for f in files
                 for ref, term, _ in glossary_terms(f, segments_of(f), sources.get(f, {}).get("title", ""),
                                                    entries_of)]
        if not terms:
            continue
        patterns = [(f, ref, term, re.compile(rf"(?<![\w-]){re.escape(term)}(?![\w-])", re.I))
                    for f, ref, term in terms]
        found = defaultdict(list)
        for f in files:
            for seg in segments_of(f):
                if seg["kind"] == "toc":
                    continue
                for gf, gref, term, pattern in patterns:
                    if (gf, gref) != (f, seg["ref"]) and pattern.search(seg["text"]):
                        found[(gf, gref, term)].append((f, seg["ref"]))
        for (gf, gref, term), uses in found.items():
            if len(uses) <= TOO_COMMON:
                out += [(gf, gref, f, ref, term) for f, ref in uses]
    return out


def _runs(text):
    w = WORD.findall(text.lower())
    return {hash(tuple(w[i:i + SHINGLE])) for i in range(len(w) - SHINGLE + 1)} if len(w) >= MIN_WORDS else set()


def same_text(clauses, threshold=SAME_TEXT):
    """same_text_as pairs across different sources: [((source, ref), (source, ref), similarity)]."""
    runs = {key: _runs(text) for key, text in clauses}
    index = defaultdict(list)
    for key, r in runs.items():
        for h in r:
            index[h].append(key)
    out = []
    for key, r in runs.items():
        if not r:
            continue
        overlap = Counter()
        for h in r:
            holders = index[h]
            if len(holders) <= COMMON_RUN:
                overlap.update(k for k in holders if k[0] != key[0] and k > key)
        for other, n in overlap.items():
            sim = n / len(r | runs[other])
            if sim >= threshold:
                out.append((key, other, round(sim, 3)))
    return sorted(out)


def library_links(reqs):
    """maps_to and stricter_than rows from the library mappings."""
    out = []
    for req in reqs:
        same = [m for m in req["mappings"] if m["relation"] == "same"]
        for m in req["mappings"]:
            out.append(("maps_to", "", req["id"], m["source"], m["clause_ref"], m["relation"]))
            if m["relation"] == "stricter":
                out += [("stricter_than", m["source"], m["clause_ref"], s["source"], s["clause_ref"], req["id"])
                        for s in same]
    return out


def links(sources=None, segments_of=None, clauses_of=None, reqs=None, files=None, entries_of=None):
    """Every link row: (kind, from source, from ref, to source, to ref, detail)."""
    import layer1
    sources = sources or catalog()
    segments_of = segments_of or layer1.segments_of
    clauses_of = clauses_of or layer1.clauses_of
    files = sorted(files or (f for f in sources if (model.ROOT / "library" / "clauses" / (Path(f).stem + ".jsonl"))
                             .exists() or GLOSSARY.search(sources[f]["title"])))   # glossaries: parsed on demand
    docs = documents({f: sources[f] for f in sources})
    out = []
    for f in files:
        out += [("refers_to", f, a, b or "", c or "", d) for a, b, c, d in
                references(f, segments_of(f), sources, docs, clauses_of)]
    families = defaultdict(list)
    for f in files:
        families[family_of(sources[f])].append(f)
    out += [("defines", a, b, c, d, e) for a, b, c, d, e in definitions(families, segments_of, sources, entries_of)]
    clauses = [((f, ref), c["text"]) for f in files for ref, c in clauses_of(f).items()]
    out += [("same_text_as", a[0], a[1], b[0], b[1], str(s)) for a, b, s in same_text(clauses)]
    out += library_links(model.requirements() if reqs is None else reqs)
    return out


def context(source, ref, rows, segments_of, sources=None, entries_of=None):
    """What a drafter or verifier may read beside a clause, marked as context only: the clauses it refers to and
    the definitions of the terms it uses (the definition itself, not the whole glossary). [(why, source, ref,
    text)]."""
    texts, defs = {}, {}

    def definition(s, r, term):
        if s not in defs:
            title = (sources or {}).get(s, {}).get("title", "")
            defs[s] = {(gr, t): d for gr, t, d in glossary_terms(s, segments_of(s), title, entries_of)}
        return defs[s].get((r, term)) or text_of(s, r)[:500]

    def text_of(s, r):
        if s not in texts:
            texts[s] = {seg["ref"]: seg["text"] for seg in segments_of(s)}
        return texts[s].get(r, "")

    out, seen = [], set()
    for kind, fs, fr, ts, tr, detail in rows:
        if kind == "refers_to" and (fs, fr) == (source, ref) and ts and tr and (ts, tr) not in seen:
            seen.add((ts, tr))
            out.append((f"referred to as {detail!r}", ts, tr, text_of(ts, tr)))
        if kind == "defines" and (ts, tr) == (source, ref) and (fs, fr) not in seen:
            seen.add((fs, fr))
            out.append((f"definition of {detail!r}", fs, fr, definition(fs, fr, detail)))
    return out


def context_block(items, limit=6000):
    """The context as text for a model input, clearly marked as not to be drafted from."""
    if not items:
        return ""
    parts, size = [], 0
    for why, s, r, text in items:
        piece = f"- {why} ({s} {r}): {text}"
        if size + len(piece) > limit:
            parts.append("- (further context left out)")
            break
        parts.append(piece)
        size += len(piece)
    return ("CONTEXT (for understanding only; do not draft obligations from it, and do not judge the item "
            "against it):\n" + "\n".join(parts))


def impact(source, rows, reqs):
    """Requirements to re-verify when a source changes: those mapped to it, and those mapped to a clause whose
    context (refers_to or defines) points into it. {requirement id: reason}."""
    leaning = {(fs, fr) for kind, fs, fr, ts, tr, _ in rows if kind == "refers_to" and ts == source}
    leaning |= {(ts, tr) for kind, fs, fr, ts, tr, _ in rows if kind == "defines" and fs == source}
    out = {}
    for req in reqs:
        for m in req["mappings"]:
            if m["source"] == source:
                out.setdefault(req["id"], f"maps to {m['clause_ref']}")
            elif (m["source"], m["clause_ref"]) in leaning:
                out.setdefault(req["id"], f"{m['source']} {m['clause_ref']} relies on this source")
    return out


def consistency(rows, reqs):
    """same_text_as pairs whose clauses are both mapped but to different requirements (Layer 1 finding)."""
    mapped = defaultdict(set)
    for req in reqs:
        for m in req["mappings"]:
            mapped[(m["source"], m["clause_ref"])].add(req["id"])
    out = []
    for kind, fs, fr, ts, tr, _ in rows:
        if kind == "same_text_as" and mapped.get((fs, fr)) and mapped.get((ts, tr)) \
                and mapped[(fs, fr)] != mapped[(ts, tr)]:
            out.append((fs, fr, ts, tr, sorted(mapped[(fs, fr)]), sorted(mapped[(ts, tr)])))
    return out


def report(rows):
    """Markdown counts per source, and the unresolved references."""
    per = defaultdict(Counter)
    unresolved = defaultdict(Counter)
    for kind, fs, fr, ts, tr, detail in rows:
        if kind == "refers_to":
            per[fs]["refers_to" if ts else "unresolved"] += 1
            if not ts:
                unresolved[fs][re.sub(r"\s+", " ", detail)] += 1
        elif kind == "defines":
            per[fs]["defines"] += 1
        elif kind == "same_text_as":
            per[fs]["same_text_as"] += 1
            per[ts]["same_text_as"] += 1
        elif kind in ("maps_to", "stricter_than"):
            per[ts][kind] += 1
    totals = Counter(r[0] for r in rows)
    lines = ["# Clause graph report", "", "Built by `python3 tools/library/graph.py report` from the parsed clauses "
             "(D34). Counts per source; `unresolved` are references with no catalogued target (mostly laws and "
             "documents outside the catalogue).", "",
             "Totals: " + ", ".join(f"{k} {v}" for k, v in sorted(totals.items())) +
             f", unresolved {sum(c['unresolved'] for c in per.values())}", "",
             "| Source | refers_to | unresolved | defines (entries used) | same_text_as | maps_to |",
             "|---|---|---|---|---|---|"]
    for f in sorted(per):
        c = per[f]
        lines.append(f"| {f} | {c['refers_to']} | {c['unresolved']} | {c['defines']} | {c['same_text_as']} | "
                     f"{c['maps_to']} |")
    lines += ["", "## Unresolved references (most frequent per source)", ""]
    for f in sorted(unresolved):
        top = ", ".join(f"{d} ({n})" if n > 1 else d for d, n in unresolved[f].most_common(8))
        lines.append(f"- {f}: {top}")
    return "\n".join(lines) + "\n"


def main():
    import layer1
    ap = argparse.ArgumentParser()
    ap.add_argument("command", choices=["report", "context", "impact"])
    ap.add_argument("args", nargs="*")
    a = ap.parse_args()
    rows = links()
    if a.command == "report":
        (model.ROOT / "library" / "graph-report.md").write_text(report(rows), encoding="utf-8")
        print(report(rows).split("\n\n")[2])
    elif a.command == "context":
        if len(a.args) != 2:
            ap.error("context <file> <ref>")
        print(context_block(context(a.args[0], a.args[1], rows, layer1.segments_of, catalog())) or "(no context)")
    else:
        if len(a.args) != 1:
            ap.error("impact <file>")
        for rid, why in sorted(impact(a.args[0], rows, model.requirements()).items()):
            print(rid, why)


if __name__ == "__main__":
    main()
