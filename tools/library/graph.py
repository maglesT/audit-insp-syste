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
- maps_to       item -> its source clause, from the library mappings (D37: one per item; no stricter_than).
"""
import argparse
import csv
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "parse"))      # common.pdf_pages
import model  # noqa: E402

SAME_TEXT = 0.9          # Jaccard similarity of 5-word runs for same_text_as
SHINGLE = 5
MIN_WORDS = 10           # shorter clauses are too generic to call the same text
COMMON_RUN = 40          # a run found in more clauses than this proposes no candidates (similarity stays exact)
FAMILY = {"EU": "EU", "EMA": "EU", "PICS": "PICS", "FDA": "FDA", "WHO": "WHO", "ICH": "ICH", "INDIA": "INDIA",
          "JAPAN": "JAPAN", "BRAZIL": "BRAZIL"}
ROMAN = r"X{0,1}(?:IX|IV|V?I{1,3}|V|X)"
NUMBER = r"\d+(?:\.\d+)+(?!\.?[A-Za-z]\b)(?:\s?\([a-z0-9]{1,4}\))*"     # 5.21, 211.84(b); not CTD 3.2.P.3.5
JOIN = r"\s*(?:,|and|or|to|through|-|–)\s*(?:§\s*)?"
INTERNAL = re.compile(rf"(?i:\b(?:paragraphs?|sections?|subsections?|points?|clauses?|items?|see|cf\.?|under)\s+"
                      rf"|(§§?)\s*)({NUMBER}(?:{JOIN}{NUMBER})*)")
DOCUMENT = re.compile(rf"(?i:\b(annex|chapter)(?:es|s)?\s+)(\d{{1,2}}[AB]?(?:{JOIN}\d{{1,2}}[AB]?)*)\b"
                      rf"|(?i:\bpart\s+)({ROMAN}|[1-9])\b(?!\.\d)"
                      rf"|(?i:\b21\s*CFR\s*(?:parts?\s*)?)(\d{{1,3}})(?:\.(\d+))?"
                      rf"|(?i:\bparts?\s+)(\d{{1,3}}(?:{JOIN}\d{{1,3}})*)\s+of\s+this\s+chapter")
THIS_SECTION = re.compile(r"(?i:\bparagraphs?\s+)((?:\([a-z0-9]{1,4}\))+)\s+of\s+this\s+section")
EXTERNAL_AFTER = re.compile(r"^[^.;]{0,40}?\b(?:of|in)\s+(?:ISO|EN|IEC|USP|Ph\.?\s?Eur|the\s+(?:Directive|Regulation|"
                            r"EU\s+GDP|GDP)|Directive|Regulation|EU\s+GDP|GDP)\b", re.I)
SCOPE_BEFORE = re.compile(rf"(?i:\b(annex)\s+(\d{{1,2}}[AB]?)|\bpart\s+({ROMAN})\b|\b(chapter)\s+(\d{{1,2}})|"
                          rf"\b(CTD)\b|\b(ISO|GDP)\b)[^.;]{{0,40}}$")
WORD = re.compile(r"[a-z0-9]+")
LEADING = re.compile(r"^\s*(?:\(?[0-9]{1,3}[a-z]?\)|\(?[a-z]{1,4}\)|\d+(?:\.\d+)*\.?)\s+", re.I)
ROMAN_NUMBERS = {"I": "I", "II": "II", "III": "III", "IV": "IV", "1": "I", "2": "II", "3": "III", "4": "IV"}


def family_of(row):
    return FAMILY.get(row["regulator"], row["regulator"])


def catalog():
    with open(model.ROOT / "sources" / "catalog.csv", encoding="utf-8") as f:
        return {r["file"]: r for r in csv.DictReader(f)}


def documents(sources):
    """{(family, kind, number): file} from catalog titles, kinds "annex", "chapter", "part", "cfr" (a CFR part),
    "cfrsec" (a single CFR section file), and "annexes"/"chapters" for combined files. Drafts and superseded
    versions are left out so a reference goes to the text in force."""
    out = {}
    for file, row in sorted(sources.items()):
        title, fam = row["title"], family_of(row)
        if re.search(r"draft|superseded", title + " " + file, re.I):
            continue
        for kind, pattern in (("annex", r"^(?:EudraLex Vol 4 )?Annex (\d+)\b"), ("chapter", r"\bChapter (\d+)\b"),
                              ("part", r"^(?:EudraLex Vol 4 |PE 009-\d+ Guide to GMP - )?Part (I{1,3})\b(?! Chapter)"),
                              ("cfr", r"^21 CFR Part (\d+)\b"), ("cfrsec", r"^21 CFR (\d+\.\d+)\b")):
            m = re.search(pattern, title)
            if m and not (fam == "EU" and kind == "part" and m.group(1) == "III"):   # Part III is a collection
                out.setdefault((fam, kind, m.group(1)), file)
        if re.search(r"\bAnnexes\b", title):                # PIC/S: all annexes in one file, one section each
            out.setdefault((fam, "annexes"), file)
    for key, file in list(out.items()):                     # PIC/S: chapters are sections of Part I
        if key[1:] == ("part", "I"):
            out.setdefault((key[0], "chapters"), file)
    return out


def guide_files(docs):
    """The files of the GMP guides themselves (chapters, parts, annexes): only these resolve a bare number into
    another chapter of the same guide."""
    return {f for k, f in docs.items() if k[1] in ("chapter", "part", "annex", "annexes", "chapters")}


def find_ref(tree, number, prefix=""):
    """The clause ref in one source that a number names. With a prefix (the citing clause's own annex or appendix,
    "Annex 19"), a ref under that prefix wins. Then the same ref, a ref ending in " <number>", an eCFR section's
    first paragraph ("211.84" -> "211.84(a)"), and finally the number without its paragraph letters."""
    number = re.sub(r"\s+", "", number)
    if prefix and f"{prefix} {number}" in tree:
        return f"{prefix} {number}"
    if number in tree:
        return number
    tail = sorted((r for r in tree if r.endswith(" " + number)), key=len)
    if tail:
        return tail[0]
    sub = sorted(r for r in tree if r.startswith(number + "(") or r.startswith(number + " ("))
    if sub:
        return sub[0]
    base = re.sub(r"\(.*$", "", number)
    return find_ref(tree, base, prefix) if base != number else None


def own_prefix(ref):
    """The section a clause sits in, when its ref names one: "Annex 19 2.2" -> "Annex 19", "Appendix 3 3.43" ->
    "Appendix 3", "Part I 1.9" -> "Part I"."""
    m = re.match(r"^((?:Annex|Appendix|Part|Chapter)\s+[0-9IVXA-B]+)\b", ref)
    return m.group(1) if m else ""


def header_lines(source, cache={}):
    """Lines that repeat on 3 or more pages of a PDF (running headers and footers), longest first."""
    if source not in cache:
        path = model.ROOT / "sources" / "official" / source
        lines = []
        if path.suffix.lower() == ".pdf" and path.exists():
            import common
            pages = common.pdf_pages(path)
            seen = Counter(" ".join(l.split()) for p in pages for l in set(p.splitlines()) if l.strip())
            lines = sorted((l for l, n in seen.items() if n >= 3 and len(l) >= 8), key=len, reverse=True)
        cache[source] = lines
    return cache[source]


def looks_like_contents(text):
    return bool(re.search(r"\.{4,}", text)) or len(re.findall(r"\b(?:annex|chapter)\s+\d+", text, re.I)) >= 6


def _numbers(group):
    return [n for n in re.split(JOIN, group) if n.strip()]


def references(source, segments, sources, docs, clause_trees):
    """refers_to links of one source: [(from ref, to source or None, to ref or None, detail)]."""
    fam = family_of(sources[source])
    own = {k for k, f in docs.items() if f == source}
    guides = guide_files(docs)
    tree = clause_trees(source)
    headers = header_lines(source)
    out = []
    for seg in segments:
        if seg["kind"] == "toc" or looks_like_contents(seg["text"]):
            continue
        text = seg["text"]
        for h in headers:                                   # running headers are not references
            text = text.replace(h, " ")
        here = own_prefix(seg["ref"])
        seen = set()

        def add(target, to_ref, detail):
            if (target, to_ref) == (source, seg["ref"]) or (target == source and to_ref is None):
                return
            if target == source and to_ref and here and own_prefix(to_ref) == here and to_ref == here:
                return                                      # the section naming itself
            if (target, to_ref) not in seen:
                seen.add((target, to_ref))
                out.append((seg["ref"], target, to_ref, detail))

        for m in DOCUMENT.finditer(text):
            detail = m.group(0).strip()
            if m.start() < 3 or (m.group(1) and m.group(0).isupper()):
                continue                                    # a heading ("CHAPTER 5 PRODUCTION"), not a reference
            if m.group(1):
                kind = m.group(1).lower()
                for number in _numbers(m.group(2)):
                    key = (fam, kind, number)
                    if key in own:
                        continue
                    if kind == "chapter" and source not in guides and not re.search(
                            r"\b(?:GMP|EudraLex|Part\s+I)\b", text[max(0, m.start() - 60):m.end() + 60]):
                        add(None, None, detail)             # some other document's chapter
                        continue
                    target, to_ref = docs.get(key), None
                    if not target:                          # a section of a combined file (PIC/S)
                        combined = docs.get((fam, kind + ("es" if kind == "annex" else "s")))
                        if combined:
                            prefix = f"Annex {number}" if kind == "annex" else f"Part I {number}"
                            tree_c = clause_trees(combined)
                            hit = prefix if prefix in tree_c else next(
                                (r for r in sorted(tree_c) if r.startswith(prefix + " ")), None)
                            if hit and not (combined == source and own_prefix(hit) == here):
                                target, to_ref = combined, hit
                            elif hit:
                                continue                    # this file naming its own section
                    add(target, to_ref, detail)
            elif m.group(3):
                key = (fam, "part", ROMAN_NUMBERS.get(m.group(3).upper(), m.group(3).upper()))
                if key in own or key == ("EU", "part", "I"):
                    continue                                # the document itself; EU Part I is the guide
                inside = f"Part {m.group(3).upper()}"           # Schedule M: parts are sections of one file
                hit = next((r for r in sorted(tree) if r == inside or r.startswith(inside + " ")), None)
                if hit and docs.get(key) is None:
                    if own_prefix(hit) != here:
                        add(source, hit, detail)
                    continue
                add(docs.get(key), None, detail)
            elif m.group(4):
                part, section = m.group(4), m.group(5)
                target = docs.get(("FDA", "cfrsec", f"{part}.{section}")) if section else None
                target = target or docs.get(("FDA", "cfr", part))
                to_ref = find_ref(clause_trees(target), f"{part}.{section}") if target and section else None
                if target or not section:
                    add(target, to_ref, detail)
            else:
                for part in _numbers(m.group(6)):
                    if ("FDA", "cfr", part) not in own:
                        add(docs.get(("FDA", "cfr", part)), None, detail)
        for m in INTERNAL.finditer(text):
            if EXTERNAL_AFTER.match(text[m.end():]):
                add(None, None, m.group(0).strip())        # "clause 7.3 of ISO 13485"
                continue
            scope = SCOPE_BEFORE.search(text[max(0, m.start() - 60):m.start()])
            for number in _numbers(m.group(2)):
                detail = m.group(0).strip() if len(_numbers(m.group(2))) == 1 else f"{m.group(0).split()[0]} {number}"
                if scope and (scope.group(6) or scope.group(7)):
                    add(None, None, detail)                 # a CTD, ISO or GDP section
                    continue
                if scope and scope.group(1):               # "Annex 17 section 4.9"
                    key = (fam, "annex", scope.group(2))
                    target = docs.get(key)
                    if target:
                        add(target, find_ref(clause_trees(target), number), detail)
                        continue
                    combined = docs.get((fam, "annexes"))
                    hit = find_ref(clause_trees(combined), number, f"Annex {scope.group(2)}") if combined else None
                    if hit and hit.startswith(f"Annex {scope.group(2)} "):
                        add(combined, hit, detail)
                    else:
                        add(None, None, detail)
                    continue
                if scope and scope.group(3):               # "Part II paragraph 2.14"
                    target = docs.get((fam, "part", ROMAN_NUMBERS.get(scope.group(3), scope.group(3))))
                    if target and target != source:
                        add(target, find_ref(clause_trees(target), number), detail)
                        continue
                if m.group(1) and fam == "FDA" and not find_ref(tree, number, here):
                    part = number.split(".")[0]             # "§ 210.3" from part 211
                    target = docs.get(("FDA", "cfrsec", re.sub(r"\(.*$", "", number))) or docs.get(("FDA", "cfr", part))
                    add(target, find_ref(clause_trees(target), number) if target else None, detail)
                    continue
                hit = find_ref(tree, number, here)
                combined_file = source in (docs.get((fam, "annexes")), docs.get((fam, "chapters")))
                if hit and combined_file and here and own_prefix(hit) not in ("", here):
                    hit = None                              # another annex's clause: not what "3.6" means here
                if hit:
                    if hit != seg["ref"]:
                        add(source, hit, detail)
                    continue
                if source in guides and fam in ("EU", "PICS") and not scope:   # a chapter of the guide's Part I
                    other = docs.get((fam, "chapter", number.split(".")[0]))
                    prefix = ""
                    if not other and docs.get((fam, "chapters")) not in (None, source):
                        other, prefix = docs.get((fam, "chapters")), "Part I"
                    hit = find_ref(clause_trees(other), number, prefix) if other and other != source else None
                    if hit and (not prefix or hit.startswith(prefix + " ")):
                        add(other, hit, detail)
                        continue
                add(None, None, detail)
        for m in THIS_SECTION.finditer(text):               # eCFR "paragraph (d) of this section"
            base = re.sub(r"\(.*$", "", seg["ref"])
            hit = find_ref(tree, base + m.group(1)) if base else None
            if hit and hit != seg["ref"]:
                add(source, hit, m.group(0).strip())
    return out


GLOSSARY = re.compile(r"glossary|definitions?\b|terminology", re.I)
HEADING = re.compile(r"^\s*(?:\d{1,2}\.?\s+)?(?:common\s+)?(?:glossary|definitions|terminology)"
                     r"(?:\s+(?:of\s+terms|to\s+annex.*))?\s*$", re.I)
NEXT_PART = re.compile(r"^\s*(?:\d{1,2}\.?\s+[A-Z]{3,}|\d{1,2}\.\s+[A-Z]|ANNEX\b|APPENDIX\b|ATTACHMENT\b|REFERENCES\b|"
                       r"Annex \d|Table \d|Figure \d)")
INLINE = re.compile(r"^\s{2,}([A-Za-z][\w ()/,'-]{2,70}?)\.\s+([A-Z].*)$")   # WHO: "   batch. A defined ..."
TOO_COMMON = 300            # a term used in more clauses than this is everyday GMP wording, not worth a link
TOO_COMMON_WORD = 60        # the same for single-word terms, which match more loosely
NOT_TERMS = {"reference", "references", "introduction", "scope", "background", "abbreviations", "purpose",
             "objective", "objectives", "general", "principle", "summary", "annex", "appendix", "notes", "reduce",
             "reporting", "return", "material", "materials", "critical", "intermediate", "container", "product",
             "production", "quality", "manufacture", "manufacturing", "verification", "validation", "process",
             "system", "record", "records", "procedure", "procedures", "specification", "packaging", "batch"}


def _indent(line):
    return len(line) - len(line.lstrip())


def _is_term(line, after):
    """A glossary term line: short, starts with a capital, no full stop at the end, and followed by a longer line."""
    text = line.strip()
    return (0 < len(text) <= 80 and len(text.split()) <= 10 and text[0].isupper()
            and not text.endswith((".", ",", ";", ":")) and not re.search(r"\.{4,}|\s\d+$|[:=]", text)
            and len(after.strip()) > len(text) * 0.6)


def _sections(lines, title):
    """(start, stop) line ranges of the glossary sections; a glossary document is one section."""
    if GLOSSARY.search(title):
        return [(-1, len(lines))]
    out = []
    for start in (i for i, l in enumerate(lines) if HEADING.match(l)):
        stop = next((j for j in range(start + 2, len(lines)) if NEXT_PART.match(lines[j])
                     and not HEADING.match(lines[j])), len(lines))
        out.append((start, stop))
    return out


def _entries(lines, start, stop):
    def prev_ends_sentence(i):
        before = next((lines[j] for j in range(i - 1, start, -1) if lines[j].strip()), ".")
        return before.rstrip().endswith((".", ":")) or HEADING.match(before)

    inline = [(i, m) for i in range(start + 1, stop) if (m := INLINE.match(lines[i]))
              and len(m.group(1).split()) <= 6 and prev_ends_sentence(i)]
    if len(inline) >= 3:                                    # "term. Definition" entries on one line
        out = []
        for n, (i, m) in enumerate(inline):
            end = inline[n + 1][0] if n + 1 < len(inline) else stop
            body = [m.group(2)] + [lines[j].strip() for j in range(i + 1, end) if lines[j].strip()]
            out.append((i, m.group(1).strip(), " ".join(body)))
        return out

    def starts_entry(j):
        """A term line: after a blank line, or an unindented capitals line right after an indented body line."""
        if j + 1 >= stop or not lines[j].strip():
            return False
        nxt = next((k for k in range(j + 1, stop) if lines[k].strip()), None)
        if nxt is None or not _is_term(lines[j], lines[nxt]):
            return False
        prev = lines[j - 1] if j > 0 else ""
        return not prev.strip() or (lines[j].strip().isupper() and _indent(lines[j]) < _indent(prev))

    out, i = [], start + 1
    while i < stop:
        if starts_entry(i):
            j = i + 1
            body = []
            while j < stop and not starts_entry(j):
                if re.match(r"^\s*\d{1,2}\s+[A-Z]", lines[j]) and _indent(lines[j]) == 0 and len(lines[j]) < 120 \
                        and j > i + 1 and not lines[j - 1].strip():
                    break                                   # a footnote at the page foot
                body.append(lines[j].strip())
                j += 1
            definition = " ".join(b for b in body if b)
            if definition:
                out.append((i, re.sub(r"\s+", " ", lines[i].strip()), definition))
            i = j
        else:
            i += 1
    return out


def glossary_entries(source, title=""):
    """[(section number, term, definition)] of a PDF source's glossary or definitions sections, read from the
    layout text: the term on its own line (EU, ICH, PIC/S) or "term. Definition" on one line (WHO). Running headers
    and footers are blanked first. A glossary document is read whole."""
    path = model.ROOT / "sources" / "official" / source
    if path.suffix.lower() != ".pdf" or not path.exists():
        return []
    import common
    pages = common.pdf_pages(path)
    lines = "\n".join(pages).splitlines()
    repeated = Counter(" ".join(l.split()) for p in pages for l in set(p.splitlines()) if l.strip())
    lines = ["" if repeated[" ".join(l.split())] >= 3 else l for l in lines]
    out = []
    for n, (start, stop) in enumerate(_sections(lines, title)):
        out += [(n, term, definition) for _, term, definition in _entries(lines, start, stop)]
    return out


def glossary_terms(source, segments, title="", entries_of=None):
    """[(ref, term, definition)] of a source's definition entries; ref is the glossary segment that holds the
    entry (the n-th glossary segment for the n-th glossary section). entries_of(source, title) reads the entries
    (default: glossary_entries, from the PDF layout text)."""
    refs = [s["ref"] for s in segments if s["kind"] != "toc" and GLOSSARY.search(
        " ".join([s["ref"], s.get("section", ""), s.get("heading", "")])) and not re.match(r"^\d+(?:\.\d+)*$", s["ref"])]
    if not refs and GLOSSARY.search(title):
        refs = [next((s["ref"] for s in segments if s["kind"] != "toc"), "")]
    if not refs:
        refs = [s["ref"] for s in segments if s["kind"] != "toc" and GLOSSARY.search(
            " ".join([s.get("section", ""), s.get("heading", ""), s["text"][:60]]))][:1]
    if not refs:
        return []
    texts = {s["ref"]: s["text"] for s in segments}
    out = []
    for entry in (entries_of or glossary_entries)(source, title):
        n, term, definition = entry if len(entry) == 3 else (0, *entry)
        name = re.sub(r"\s*\(.*?\)", "", term).strip(" -")        # "Batch (or Lot)" -> "Batch"
        if GLOSSARY.search(name) and len(name.split()) <= 2 or ". " in name or name.lower() in NOT_TERMS or \
                re.search(r"[:=]", name) or re.match(r"(?:Appendix|Annex|Part|Chapter|Section|Table|Figure)\b", name):
            continue                                        # headings, not terms
        if not (2 <= len(name.split()) <= 6 or (len(name.split()) == 1 and len(name) >= 6)):
            continue
        holder = next((r for r in refs if name.lower() in texts.get(r, "").lower()), refs[min(n, len(refs) - 1)])
        out.append((holder, name, definition))
    return out


def definitions(families, segments_of, sources, entries_of=None):
    """defines links: (glossary source, entry ref, using source, using ref, term) for every clause of the same
    family whose text uses the term as whole words. One glossary per term and family (a glossary document first),
    and in each clause the longest matching term wins over terms inside it ("packaging materials" over
    "packaging")."""
    out = []
    for fam, files in families.items():
        terms = {}
        ordered = sorted(files, key=lambda f: (not GLOSSARY.search(sources.get(f, {}).get("title", "")), f))
        for f in ordered:
            for ref, term, _ in glossary_terms(f, segments_of(f), sources.get(f, {}).get("title", ""), entries_of):
                terms.setdefault(term.casefold(), (f, ref, term))
        if not terms:
            continue
        patterns = sorted(((f, ref, term, re.compile(rf"(?<![\w-]){re.escape(term)}(?![\w-])", re.I))
                           for f, ref, term in terms.values()), key=lambda x: -len(x[2]))
        found = defaultdict(list)
        for f in files:
            for seg in segments_of(f):
                if seg["kind"] == "toc":
                    continue
                taken = []
                for gf, gref, term, pattern in patterns:
                    if (gf, gref) == (f, seg["ref"]):
                        continue
                    spans = [m.span() for m in pattern.finditer(seg["text"])]
                    free = [sp for sp in spans if not any(a <= sp[0] and sp[1] <= b for a, b in taken)]
                    if free:
                        taken += spans
                        found[(gf, gref, term)].append((f, seg["ref"]))
        for (gf, gref, term), uses in found.items():
            if len(uses) <= (TOO_COMMON_WORD if len(term.split()) == 1 else TOO_COMMON):
                out += [(gf, gref, f, ref, term) for f, ref in uses]
    return out


def _runs(text):
    w = WORD.findall(LEADING.sub("", text).lower())
    return {hash(tuple(w[i:i + SHINGLE])) for i in range(len(w) - SHINGLE + 1)} if len(w) >= MIN_WORDS else set()


def same_text(clauses, threshold=SAME_TEXT):
    """same_text_as pairs across different sources: [((source, ref), (source, ref), similarity)]. Leading clause
    numbers are left out, so renumbered twins pair; runs found in many clauses only stop proposing candidates,
    the similarity itself is exact."""
    runs = {key: _runs(text) for key, text in clauses}
    index = defaultdict(list)
    for key, r in runs.items():
        for h in r:
            index[h].append(key)
    out = []
    for key, r in runs.items():
        if not r:
            continue
        candidates = Counter()
        for h in r:
            holders = index[h]
            if len(holders) <= COMMON_RUN:
                candidates.update(k for k in holders if k[0] != key[0] and k > key)
        for other, n in candidates.items():
            if n < len(r) * threshold * 0.5:
                continue                                    # cannot reach the threshold
            sim = len(r & runs[other]) / len(r | runs[other])
            if sim >= threshold:
                out.append((key, other, round(sim, 3)))
    return sorted(out)


def library_links(reqs):
    """maps_to rows from the library mappings: item -> its source clause."""
    return [("maps_to", "", req["id"], m["source"], m["clause_ref"], "") for req in reqs for m in req["mappings"]]


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
        if kind == "defines" and (ts, tr) == (source, ref) and (fs, fr, detail) not in seen:
            seen.add((fs, fr, detail))
            out.append((f"definition of {detail!r}", fs, fr, definition(fs, fr, detail)))
    return out


def context_block(items, limit=6000, piece=1500):
    """The context as text for a model input, clearly marked as not to be drafted from. Each item is cut to
    `piece` characters and the block to `limit`."""
    if not items:
        return ""
    parts, size = [], 0
    for why, s, r, text in items:
        text = text if len(text) <= piece else text[:piece].rsplit(" ", 1)[0] + " [...]"
        line = f"- {why} ({s} {r}): {text}"
        if size + len(line) > limit:
            parts.append("- (further context left out)")
            break
        parts.append(line)
        size += len(line)
    return ("CONTEXT (for understanding only; do not draft obligations from it, and do not judge the item "
            "against it):\n" + "\n".join(parts))


def impact(source, rows, reqs):
    """Requirements to re-verify when a source changes: those mapped to it, and those mapped to a clause whose
    context (refers_to or defines) points into it. {requirement id: reason}."""
    leaning = {(fs, fr) for kind, fs, fr, ts, tr, _ in rows if kind == "refers_to" and ts == source}
    leaning |= {(ts, tr) for kind, fs, fr, ts, tr, _ in rows if kind == "defines" and fs == source}
    out = {}
    for req in reqs:
        if req.get("status") == "retired":
            continue
        for m in req["mappings"]:
            if m["source"] == source:
                out.setdefault(req["id"], f"maps to {m['clause_ref']}")
            elif (m["source"], m["clause_ref"]) in leaning:
                out.setdefault(req["id"], f"{m['source']} {m['clause_ref']} relies on this source")
    return out


def consistency(rows, reqs):
    """same_text_as pairs whose clauses are both mapped but whose items differ (Layer 1 finding; D37: identical
    texts must produce identical items): (from source, ref, to source, ref, from item ids, to item ids)."""
    from common import normalise
    texts, ids = defaultdict(set), defaultdict(set)
    for req in reqs:
        for m in req["mappings"]:
            texts[(m["source"], m["clause_ref"])].add((normalise(req["item_text"]), m["strength"]))
            ids[(m["source"], m["clause_ref"])].add(req["id"])
    out = []
    for kind, fs, fr, ts, tr, _ in rows:
        if kind == "same_text_as" and texts.get((fs, fr)) and texts.get((ts, tr)) \
                and texts[(fs, fr)] != texts[(ts, tr)]:
            out.append((fs, fr, ts, tr, sorted(ids[(fs, fr)]), sorted(ids[(ts, tr)])))
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
        elif kind == "maps_to":
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
