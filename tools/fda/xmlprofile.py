"""XML profile (D47): checklist items drafted from eCFR XML sections, checked against the exact XML text.

  python3 tools/fda/xmlprofile.py prepare-draft SOURCE [SECTION ...]   # default: every section of SOURCE
  python3 tools/fda/xmlprofile.py ingest-draft RUN                     # checks, coverage -> RUN/items.jsonl, report.json
  python3 tools/fda/xmlprofile.py prepare-verify RUN                   # verifier A and B batches (section text + items)
  python3 tools/fda/xmlprofile.py ingest-verify RUN                    # agreement + automatic route -> RUN/route.json
  python3 tools/fda/xmlprofile.py prepare-redraft RUN                  # new run drafting only RUN's coverage gaps
  python3 tools/fda/xmlprofile.py reverify RUN                         # old verify/ kept as verify-superseded-N; new batches
  python3 tools/fda/xmlprofile.py recheck RUN                          # deterministic checks again (items unchanged), re-route

The XML is read as text (no rendering, no vision): tools/parse/ecfr.py gives every paragraph with its reference
from the structure (211.84(c)(1)) and its exact text. Drafting agents get whole sections (all paragraphs with their
references) and answer as in tools/pages (batch file -> answers file).

Checks (deterministic):
  clause     the item's clause_number is a paragraph reference of the section (from the XML)
  quote      the quote is in that paragraph's own text, token for token (quotes.toks / contains, not loose): one
             exact source, so there is no second reader; a quote that runs into a sub-paragraph may include the
             sub-paragraphs' text in order
  numbers    both ways (statement <-> quote); strength (an obligation word of the quote, else of the parent lead-in);
  conditions condition wording of the quote in the statement; lead-in: a parent paragraph ending in ":" (e.g.
             211.84(c) "... in accordance with the following procedures:") states a scoping condition the statement
             must carry (vision.lead_in_missing), or a qualifier "as are necessary to ..." (qualifier_missing)
  plants     a text limited to products not required to be sterile excludes INJ; one limited to sterile products
             lists only INJ (and API)
Coverage: every obligation sentence of every paragraph (vision.counts_for_coverage) is in an item quote citing that
paragraph or one of its sub-paragraphs (whole-token, 80 % of its words, its condition words; or the quotes printed
inside it together with 90 %, every number), or listed by the drafter as not applicable; a lead-in sentence ending
":" with one obligation word is covered by its sub-paragraphs' items when each has one and all carry the lead-in.
Automatic route (D47): no finding, quote confirmed, and both blind verifiers say correct; everything else goes to
the review queue (tools/fda/review.py).
"""
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
for sub in ("library", "parse", "pages", "ai"):
    sys.path.insert(0, str(ROOT / "tools" / sub))
import obligations  # noqa: E402
import quotes  # noqa: E402
import vision  # noqa: E402
from common import OFFICIAL  # noqa: E402

PROMPTS = HERE / "prompts"
SECTIONS_PER_BATCH = 5
DRAFT_SCHEMA = {
    "type": "object", "required": ["section", "items", "not_applicable"],
    "properties": {
        "section": {"type": "string"},
        "items": {"type": "array", "items": {
            "type": "object", "required": ["statement", "quote", "clause_number", "strength", "plant_types",
                                            "numbers", "condition", "topic"],
            "properties": {"statement": {"type": "string"}, "quote": {"type": "string"},
                           "clause_number": {"type": "string"}, "strength": {"enum": list(vision.STRENGTHS)},
                           "plant_types": {"type": "array", "items": {"enum": list(vision.PLANTS)}},
                           "numbers": {"type": "array", "items": {"type": "string"}},
                           "condition": {"type": "string"}, "topic": {"type": "string"}}}},
        "not_applicable": {"type": "array", "items": {
            "type": "object", "required": ["clause_number", "text", "reason"],
            "properties": {"clause_number": {"type": "string"}, "text": {"type": "string"},
                           "reason": {"type": "string"}}}}}}


def paragraphs(source, cache={}):
    """[(ref, text)] of the XML in document order, from tools/parse/ecfr.py."""
    if source not in cache:
        import ecfr
        cache[source] = [(c.ref, c.text) for c in ecfr.parse(OFFICIAL / source)[0]]
    return cache[source]


def section_of(ref):
    return ref.split("(")[0]


def sections(source):
    """{section: [(ref, text)]} in document order."""
    out = {}
    for ref, text in paragraphs(source):
        out.setdefault(section_of(ref), []).append((ref, text))
    return out


def parent(ref):
    """211.84(c)(1) -> 211.84(c); 211.84(c) -> 211.84; 211.84 -> ''."""
    m = re.match(r"(.*)\([^()]+\)$", ref)
    return m.group(1) if m else ""


def own_text(ref, text):
    """A paragraph's text without its leading designation ("(c) ") or, for a section, without "§ 211.84" and its
    heading ("Testing and approval or rejection of components, ..."): the parser joins the heading to the
    section's own text (211.142 "§ 211.142 Warehousing procedures. Written procedures ...")."""
    if re.match(r"^§\s*[\d.]+", text):
        return re.sub(r"^§\s*[\d.]+\s*[^.?]*[.?]\s*", "", text).strip()    # headings end in "." or "?" (Part 207)
    return re.sub(r"^(?:\([^()]{1,6}\)\s*)+", "", text).strip()


MAX_BATCH_CHARS = 20000
MAX_BATCH_SECTIONS = 10


def pack(keys, secs):
    """Sections in order, packed into batches of at most MAX_BATCH_SECTIONS sections and about MAX_BATCH_CHARS
    characters of text (a longer section is a batch alone)."""
    out, cur, size = [], [], 0
    for k in keys:
        n = sum(len(t) for _, t in secs[k])
        if cur and (size + n > MAX_BATCH_CHARS or len(cur) >= MAX_BATCH_SECTIONS):
            out.append(cur)
            cur, size = [], 0
        cur.append(k)
        size += n
    return out + ([cur] if cur else [])


MAX_VERIFY_ITEMS = 20


def cap(chunks, groups, limit=MAX_VERIFY_ITEMS):
    """D50: verify batches of at most `limit` items. Each chunk (sections or units packed by text size) is split
    in item order; a part lists the sections its items come from (a section with more items than the limit
    appears in several parts, each with the section's whole text)."""
    out = []
    for chunk in chunks:
        part = []
        for s in chunk:
            for it in groups[s]:
                if len(part) >= limit:
                    out.append(part)
                    part = []
                part.append(it)
        if part:
            out.append(part)
    return [(list(dict.fromkeys(it["section"] for it in part)), part) for part in out]


def supersede_verify(run):
    """Moves RUN/verify to RUN/verify-superseded-N (the old batches and answers stay, unused), so prepare-verify can
    write new batches (D50 re-verification). route.json stays until the new answers are ingested."""
    run = Path(run)
    vdir = run / "verify"
    if not vdir.exists():
        raise SystemExit(f"{vdir} does not exist")
    n = 1
    while (run / f"verify-superseded-{n}").exists():
        n += 1
    vdir.rename(run / f"verify-superseded-{n}")
    if (run / "verify-report.json").exists():
        (run / "verify-report.json").rename(run / f"verify-report-superseded-{n}.json")
    return run / f"verify-superseded-{n}"


def prepare_draft(source, wanted=None):
    run = vision.new_run("xml-draft")
    secs = sections(source)
    keys = [s for s in secs if not wanted or s in wanted]
    instructions = (PROMPTS / "draft_xml.md").read_text()
    batches = pack(keys, secs)
    for n, group in enumerate(batches, start=1):
        units = [{"id": f"{source}:{s}", "source": source, "section": s, "plant_scope": vision.scope(source),
                  "paragraphs": [{"ref": r, "text": t} for r, t in secs[s]]} for s in group]
        (run / "batches" / f"batch_{n:03d}.json").write_text(json.dumps(
            {"instructions": instructions, "topics": vision.topics(), "schema": DRAFT_SCHEMA, "sections": units},
            indent=1, ensure_ascii=False))
    (run / "source.json").write_text(json.dumps({"source": source, "sha256": vision.sha256(OFFICIAL / source),
                                                 "sections": keys}, indent=1))
    print(run, len(batches), "batches")
    return run


def ancestors_text(ref, paras):
    """The sentences of a paragraph's ancestors that introduce their sub-paragraphs ("... the following ...",
    or ending ":"), without references: where a statement may rightly take a number from (314.81(b)(1) "... of
    the following kinds ... within 3 working days of receipt" governs (b)(1)(i) and (ii)); other duties of the
    parent paragraph lend no numbers."""
    out, r = [], parent(ref)
    while r:
        for sent in obligations.sentences(own_text(r, paras.get(r, ""))):
            if sent.rstrip().endswith(":") or re.search(r"\bthe following\b", sent, re.I):
                out.append(without_refs(sent))       # only the sentence that governs the sub-paragraphs
        r = parent(r)
    return out


def lead_in_text(ref, paras):
    """The lead-ins over a paragraph: every ancestor paragraph whose own text ends in ":", nearest first
    (211.42(c)(10)(i) takes (c)(10) "Aseptic processing, which includes as appropriate:" and (c)'s "... as are
    necessary to prevent contamination or mixups during the course of the following procedures:")."""
    return " ".join(lead_ins(ref, paras))


def lead_ins(ref, paras):
    """The lead-in sentences over a paragraph, nearest first (see lead_in_text)."""
    out, r = [], parent(ref)
    while r:
        t = own_text(r, paras.get(r, ""))
        if not t.rstrip().endswith(":"):
            break
        sents = obligations.sentences(t) or [t]
        # the sentence that introduces the list (D46), plus earlier sentences without an obligation word of their
        # own ("For products labeled for adults only.", 201.326); not the paragraph's other duties (11.10)
        out.append(" ".join([x for x in sents[:-1] if not obligations.strength(x)] + [sents[-1]]))
        r = parent(r)
    return out


def strength_words(text):
    """layer1.strength_of without the may/can/could that state a possibility ("changes that may affect sterility
    assurance", vision.DESCRIPTIVE, the coverage rule of PR #36): those are not permissions."""
    import layer1
    return layer1.strength_of(POSSIBILITY.sub(" ", text)) if text else None


# Only verbs that state a possibility; "may include / contain / appear / be considered" stay permissions (Part 201
# "The declaration may contain common or decimal fractions"), unlike vision.DESCRIPTIVE used for coverage.
POSSIBILITY = re.compile(r"\b(?:may|can|could)\s+(?:also\s+|even\s+|well\s+)?(?:affect|cause|result|occur|increase|"
                         r"decrease|vary|differ|arise|lead|indicate|exist|be\s+(?:present|found|formed|due|caused|"
                         r"generated|introduced|seen|observed))\b", re.I)


MIN_QUOTE_TOKENS = 3
DESIGNATION = re.compile(r"\((?:\d{1,2}|[ivx]{1,5}|[a-z])\)")


_SEP = r"(?:\s*,\s*(?:and\s+|or\s+)?|\s+and\s+|\s+or\s+|\s+through\s+)"
_REF = r"(?:§\s*)?\d+(?:\.\d+)*(?:\([^()\s]{1,5}\))*"
CROSS_REF = re.compile(rf"§§?\s*{_REF}(?:{_SEP}(?:{_REF}|\([^()\s]{{1,5}}\)))*"
                       rf"|\bparts?\s+\d+(?:{_SEP}\d+)*", re.I)


def without_refs(text):
    """Text without cross-references ("§ 211.192", "§§ 211.68 and 211.188(b)(11)", "parts 600 through 680") and
    paragraph designations ("(1)"): these are not numbers, limits or periods the statement has to repeat (and the
    statement, shown to customers, carries no references)."""
    return DESIGNATION.sub(" ", CROSS_REF.sub(" ", text))


def quote_found(q, ref, source):
    """The quote's tokens are in the exact text of ref, starting in ref's own text and running on, if at all, into
    its sub-paragraphs in order (designations "(1)" left out, as the prompt asks): whole tokens, and not a quote
    found in the sub-paragraphs alone (that one cites the wrong paragraph)."""
    rows = [(r, own_text(r, t)) for r, t in paragraphs(source) if r == ref or r.startswith(ref + "(")]
    if not q or (len(q) < MIN_QUOTE_TOKENS and q != quotes.toks(rows[0][1])):   # short only as the whole paragraph
        return False
    whole = quotes.toks(" ".join(t for _, t in rows))
    kids = quotes.toks(" ".join(t for r, t in rows if r != ref))
    return quotes.contains(q, whole) and not (kids and quotes.contains(q, kids))


def item_hash(item):
    """Fingerprint of what a verifier or reviewer judged: statement, quote, clause, strength, plant types, condition."""
    import hashlib
    key = json.dumps([item.get(k) for k in ("statement", "quote", "clause_number", "strength", "plant_types",
                                            "condition")],
                     ensure_ascii=False)
    return hashlib.sha256(key.encode()).hexdigest()[:16]


def prepare_redraft(run):
    """A new run that drafts only the coverage gaps of RUN: each section with gaps, whole, plus the gap sentences;
    the drafter writes items (or not-applicable entries) for those sentences only; coverage is then judged on them."""
    run = Path(run)
    src = json.loads((run / "source.json").read_text())["source"]
    rep = json.loads((run / "report.json").read_text())
    if rep.get("failed"):
        raise SystemExit(f"sections without a usable answer: {rep['failed']}; draft them again in a new run first")
    gaps = rep["coverage_gaps"]
    if not gaps:
        raise SystemExit("no coverage gaps")
    new = vision.new_run("xml-redraft")
    secs = sections(src)
    keys = list(dict.fromkeys(g["section"] for g in gaps))
    instructions = (PROMPTS / "draft_xml.md").read_text() + (
        "\n\nREDRAFT: earlier items already cover this section except the sentences in \"gaps\". Write items, or "
        "not_applicable entries, for those sentences only; do not repeat other obligations.\n")
    units = [{"id": f"{src}:{k}", "source": src, "section": k, "plant_scope": vision.scope(src),
              "paragraphs": [{"ref": r, "text": t} for r, t in secs[k]],
              "gaps": [{"clause": g["clause"], "sentence": g["sentence"]} for g in gaps if g["section"] == k]}
             for k in keys]
    (new / "batches" / "batch_001.json").write_text(json.dumps(
        {"instructions": instructions, "topics": vision.topics(), "schema": DRAFT_SCHEMA, "sections": units},
        indent=1, ensure_ascii=False))
    (new / "source.json").write_text(json.dumps({"source": src, "sha256": vision.sha256(OFFICIAL / src),
                                                 "sections": keys, "redraft_of": run.name, "gaps": gaps}, indent=1))
    print(new)
    return new


def check_item(item, source, section=None):
    """(findings, quote confirmed); section: the section the drafter answered for (its items must cite it)."""
    import layer1
    paras = dict(paragraphs(source))
    ref = item["clause_number"].strip()
    out = []
    if ref not in paras:
        return [("clause", f"{ref!r} is not a paragraph of {source}")], False
    if section and section_of(ref) != section:
        out.append(("clause", f"{ref!r} is not in section {section}"))
    q = quotes.toks(item["quote"])
    found = quote_found(q, ref, source)
    if not found:
        out.append(("quote", f"quote not in the text of {ref} (exact XML text, starting in {ref} itself, "
                             f"at least {MIN_QUOTE_TOKENS} tokens)"))
    lead = lead_in_text(ref, paras)
    for n in re.findall(r"\d+(?:[.,]\d+)?", item["statement"]):
        if not layer1.number_found(n, [item["quote"]] + ancestors_text(ref, paras)):
            out.append(("numbers", f"{n} in the statement, not in the quote or its parent paragraphs"))
    for n in re.findall(r"(?<![\w.^§])\d+(?:[.,]\d+)?", without_refs(item["quote"])):
        if not layer1.number_found(n, [item["statement"]]):
            out.append(("numbers", f"{n} in the quote, not in the statement"))
    words = strength_words(item["quote"]) or next(
        (w for w in map(strength_words, lead_ins(ref, paras)) if w), None)     # the nearest lead-in decides
    if words and words != item["strength"]:
        out.append(("strength", f"quote says {words}, item {item['strength']}"))
    missing = layer1.conditions_missing(item["quote"], layer1.conditions_in(item["statement"]))
    if missing:
        out.append(("conditions", "quote has " + ", ".join(missing) + " wording the statement lacks"))
    lm = vision.lead_in_missing(lead, item["statement"]) + qualifier_missing(lead, item["statement"])
    if lm:
        out.append(("lead-in", f"the statement lacks the lead-in's condition: {'; '.join(lm)[:160]}"))
    pf = plants_finding(item["quote"] + " " + lead, item["plant_types"])
    if pf:
        out.append(("plants", pf))
    return out, found


# A lead-in qualifier that limits what every sub-paragraph asks for: "such other control systems ... as are
# necessary to prevent contamination or mixups during the course of the following procedures:" (211.42(c)).
QUALIFIER = re.compile(r"\bas (?:(?:is|are|may be) )?(necessary|needed|required|appropriate)\b(?:\s+(?:to|for)\s+([^:;.]*))?",
                       re.I)
LIST_TAIL = re.compile(r"\b(?:during the course of |in |for |of )?(?:each of )?the following\b.*$", re.I)
NEED_WORDS = {"necessary": {"necessary", "needed", "need", "needs", "required", "require", "requires"},
              "needed": {"necessary", "needed", "need", "needs", "required", "require", "requires"},
              "required": {"necessary", "needed", "need", "needs", "required", "require", "requires"},
              "appropriate": {"appropriate", "appropriately", "suitable", "suitably"}}


def qualifier_missing(lead, statement):
    """The "as are necessary to ..." qualifiers of a lead-in that the statement lacks: the statement needs a word
    of the qualifier's kind (necessary / needed / required, or appropriate / suitable) and 80 % of the content
    words (4+ letters, compared by stem) of its purpose ("prevent contamination or mixups"); the list tail ("during the course of
    the following procedures") is not part of the purpose."""
    if not lead:
        return []
    said = set(re.findall(r"[a-z]{4,}", statement.lower()))
    out = []
    for m in QUALIFIER.finditer(lead):
        kind, purpose = m.group(1).lower(), LIST_TAIL.sub("", m.group(2) or "").strip()
        content = vision.stems(purpose) - {"such"}                 # by stem, as vision.lead_in_missing
        if not (said & NEED_WORDS[kind]) or (content and len(content & vision.stems(statement)) / len(content) < 0.8):
            out.append(f"as ... {kind}" + (f" to {purpose}" if purpose else ""))
    return out


# Plant types the text itself rules in or out (the brief: INJ is sterile injectables).
NONSTERILE = re.compile(r"\bnot (?:required|intended|represented|purporting) to be sterile\b|\bnon-?sterile\b", re.I)
STERILE = re.compile(r"\b(?:purporting|required|represented|intended) to be sterile\b|\bsterile drug products?\b", re.I)


def plants_finding(text, plants):
    """'' or why the item's plant types do not fit the text: a paragraph only for products not required to be
    sterile cannot list INJ (211.113(a)); one only for sterile products lists only INJ (and API)."""
    if NONSTERILE.search(text):
        return "the text is limited to non-sterile products, the item lists INJ" if "INJ" in plants else ""
    if STERILE.search(text) and set(plants) - {"INJ", "API"}:
        return "the text is limited to sterile products, the item lists " + ", ".join(sorted(set(plants) - {"INJ", "API"}))
    return ""


def lead_in_covered(ref, sentence, items, source):
    """A lead-in sentence (ending ":") with a single obligation word is covered when every sub-paragraph under it
    has an item and none of those items lacks the lead-in's condition or qualifier; a lead-in that also states
    its own duty ("The written program shall be followed and shall include:") needs its own item."""
    import layer1
    if not sentence.rstrip().endswith(":"):
        return False
    if len(re.findall(r"\b(?:shall|must|should|may|is required|are required)\b", sentence, re.I)) != 1:
        return False
    kids = [r for r, _ in sections(source)[section_of(ref)] if parent(r) == ref]
    if not kids:
        return False
    for k in kids:
        mine = [i for i in items if i["clause_number"].strip() == k or i["clause_number"].strip().startswith(k + "(")]
        if not mine:
            return False
        for i in mine:
            if vision.lead_in_missing(sentence, i["statement"]) or qualifier_missing(sentence, i["statement"]):
                return False
    return True


def coverage(source, section, items, na):
    """Obligation sentences of the section's paragraphs not covered (module docstring)."""
    import layer1
    gaps = []
    # the sentence's first 8+ words copied exactly (prompt), or the whole sentence when it is shorter
    na_raw = [(x["clause_number"].strip(), quotes.toks(own_text("", x["text"]))) for x in na]
    for ref, text in sections(source)[section]:
        cl = [(i["clause_number"].strip(), i["quote"]) for i in items]
        mine = [q for c, q in cl if c == ref or ref.startswith(c + "(") or c.startswith(ref + "(")]
        for s in obligations.sentences(own_text(ref, text)):
            if not vision.counts_for_coverage(s):
                continue
            ws, conds, st = vision._words(s), layer1.conditions_in(s), quotes.toks(s)
            if not ws:
                continue
            if any(sum(w in set(vision._words(q)) for w in ws) / len(ws) >= vision.COVERED_SHARE
                   and not (conds - layer1.conditions_in(q)) for q in mine):
                continue
            parts = [q for q in mine if quotes.contains(quotes.toks(q), st)]
            if parts:
                union = set().union(*(set(vision._words(q)) for q in parts))
                nums = set(re.findall(r"\d+(?:[.,]\d+)?", s)) - set(re.findall(r"\d+(?:[.,]\d+)?", " ".join(parts)))
                if (sum(w in union for w in ws) / len(ws) >= vision.UNION_SHARE and not nums
                        and not (conds - layer1.conditions_in(" ".join(parts)))):
                    continue
            if any(c == ref and (quotes.contains(k[:8], st) if len(st) >= 8 else k == st) for c, k in na_raw):
                continue
            if lead_in_covered(ref, s, items, source):
                continue
            gaps.append({"clause": ref, "sentence": s[:300]})
    return gaps


def ingest_draft(run):
    run = Path(run)
    if (run / "verify").exists() or (run / "route.json").exists():
        raise SystemExit(f"{run} is already verified: a redraft is a new run (its ids would carry old verdicts)")
    source = json.loads((run / "source.json").read_text())["source"]
    items, rep = [], {"sections": 0, "items": 0, "quote_confirmed": 0, "findings": {}, "coverage_gaps": [],
                      "not_applicable": 0, "failed": []}
    for bf in sorted((run / "batches").glob("batch_*.json")):
        batch = json.loads(bf.read_text())
        af = run / "answers" / bf.name
        answers, dup = {}, set()
        for a in (json.loads(af.read_text())["answers"] if af.exists() else []):
            key = a["section"].rsplit(":", 1)[-1]               # "src.xml:211.84" and "211.84" are one section
            if key in answers:
                dup.add(key)
            answers[key] = a
        for u in batch["sections"]:
            a = answers.get(u["section"])
            if a is None or u["section"] in dup:               # missing, or answered twice: redraft
                rep["failed"].append(u["id"])
                continue
            rep["sections"] += 1
            rep["not_applicable"] += len(a["not_applicable"])
            for k, it in enumerate(a["items"], start=1):
                found, ok = check_item(it, source, u["section"])
                rep["quote_confirmed"] += ok
                for c, _ in found:
                    rep["findings"][c] = rep["findings"].get(c, 0) + 1
                items.append({"id": f"{u['id']}#{k}", "source": source, "section": u["section"], **it,
                              "findings": found, "quote_confirmed": ok, "hash": item_hash(it)})
            found_gaps = coverage(source, u["section"], a["items"], a["not_applicable"])
            if "gaps" in u:                     # a redraft is judged on the sentences it was asked to cover
                asked = {(g["clause"], g["sentence"]) for g in u["gaps"]}
                found_gaps = [g for g in found_gaps if (g["clause"], g["sentence"]) in asked]
            rep["coverage_gaps"] += [{"section": u["section"], **g} for g in found_gaps]
    rep["items"] = len(items)
    with open(run / "items.jsonl", "w", encoding="utf-8") as f:
        for i in items:
            f.write(json.dumps(i, ensure_ascii=False) + "\n")
    (run / "report.json").write_text(json.dumps(rep, indent=1, ensure_ascii=False))
    print(json.dumps({k: (len(v) if isinstance(v, list) else v) for k, v in rep.items()}, indent=1))
    return rep


def prepare_verify(run):
    """Verifier A and B batches, one per draft batch: each item with its section's paragraphs (blind)."""
    run = Path(run)
    items = [json.loads(ln) for ln in (run / "items.jsonl").read_text().splitlines() if ln.strip()]
    source = json.loads((run / "source.json").read_text())["source"]
    secs = sections(source)
    vdir = run / "verify"
    if vdir.exists() and any(vdir.rglob("*.json")):
        raise SystemExit(f"{vdir} already holds verify batches or answers: verify a redraft in a new run")
    (vdir / "batches").mkdir(parents=True, exist_ok=True)
    (vdir / "answers").mkdir(exist_ok=True)
    groups = {}
    for it in items:
        groups.setdefault(it["section"], []).append(it)
    keys = list(groups)
    parts = cap(pack(keys, secs), groups)
    n = 0
    for role in ("a", "b"):
        instructions = (PROMPTS / f"verify_xml_{role}.md").read_text()
        for chunk, part in parts:
            n += 1
            payload = {"role": role, "instructions": instructions, "schema": vision.VERIFY_SCHEMA,
                       "sections": [{"section": s, "paragraphs": [{"ref": r, "text": t} for r, t in secs[s]]}
                                    for s in chunk],
                       "items": [{"id": it["id"], "section": it["section"], "hash": it["hash"],
                                  "item": {k: it[k] for k in ("statement", "quote", "clause_number", "strength",
                                                              "plant_types", "condition")},
                                  "plant_scope": vision.scope(source)} for it in part]}
            (vdir / "batches" / f"batch_{n:03d}_{role}.json").write_text(json.dumps(payload, indent=1,
                                                                                    ensure_ascii=False))
    print(vdir, n, "batches")


# D50: words a reason may use without saying anything about the item (they fit any item of any batch).
GENERIC = {
    # the verifier's own vocabulary
    "quote", "quoted", "quotes", "statement", "statements", "obligation", "obligations", "strength", "condition",
    "conditions", "item", "items", "paragraph", "paragraphs", "text", "texts", "correct", "correctly", "exact",
    "exactly", "verbatim", "printed", "match", "matches", "matched", "matching", "mandatory", "recommended",
    "optional", "required", "requires", "require", "requirement", "requirements", "shall", "should", "must", "may",
    "plant", "plants", "type", "types", "applies", "apply", "applicable", "cited", "cites", "section", "sections",
    "regulation", "regulations", "whole", "faithful", "faithfully", "accurately", "accurate", "adds", "added",
    "nothing", "omits", "omitted", "omission", "omissions", "scope", "scoped", "states", "stated", "state",
    "captures", "captured", "reflects", "reflected", "restates", "lead", "leadin", "inj", "osd", "api", "liq",
    "ste", "all", "every", "listed", "list", "number", "numbers", "qualifier", "qualifiers", "unit", "page",
    "guide", "fda", "firm", "investigator", "expects", "expected", "expectation", "verdict", "issue", "issues",
    "problem", "fully", "full", "same", "also", "both", "sub", "parent",
    # function words
    "and", "the", "for", "with", "without", "that", "this", "its", "not", "are", "was", "were", "has", "have",
    "into", "from", "under", "over", "any", "each", "one", "two", "only", "here", "there", "than", "then", "which",
    "what", "who", "whom", "does", "did", "but", "nor", "yet", "can", "could", "would", "will", "being", "been",
    "such", "these", "those", "their", "them", "they", "you", "your", "our", "out", "per", "via", "within",
    "between", "about", "above", "below", "where", "when", "while", "because", "since", "true", "false"}
_WORD = re.compile(r"[a-z]+|\d+(?:\.\d+)*")


def _content(text):
    """Content words (as light stems) and numbers of a text: GENERIC words and words under 3 letters left out."""
    out = set()
    for w in _WORD.findall(text.lower()):
        if w[0].isdigit():
            out.add(w)
        elif len(w) >= 3 and w not in GENERIC:
            out.add(vision.stem(w))
    return out


def norm_reason(reason):
    """A reason's text for the duplicate test: lower case, every run of other characters one space."""
    return " ".join(re.findall(r"[a-z0-9]+", (reason or "").lower()))


def specific(reason, item):
    """D50: the reason names at least one content word or number of the item's own statement or quote."""
    return bool(_content(reason or "") & _content(f"{item.get('statement') or ''} {item.get('quote') or ''}"))


def proven_by_both(run, items, report=None):
    """Ids that exactly one verifier A and exactly one verifier B answer "correct", each answer read with the
    batch file of the same name (the role and the item hash that batch showed): the hash must equal the item's
    hash as it is now (recomputed). A duplicate answer, a missing role, an answer to an item its batch did not
    show, or a batch without hashes does not count.

    D50: a "correct" counts only if its reason is item-specific (specific(): it names a content word or number of
    the item's statement or quote, as its batch showed the item) and its normalised text repeats no other reason
    of the same answers file; any other "correct" counts as unanswered. With report (a dict), the numbers of
    generic and duplicate-reason "correct" answers are added to it."""
    run = Path(run)
    seen, bad = {}, set()
    generic = duplicate = 0
    for af in sorted((run / "verify" / "answers").glob("batch_*.json")):
        bf = run / "verify" / "batches" / af.name
        if not bf.exists():
            continue
        batch = json.loads(bf.read_text())
        role = batch.get("role")
        shown = {e["id"]: e for e in batch["items"]}
        answers = json.loads(af.read_text())["answers"]
        times = {}
        for a in answers:
            r = norm_reason(a.get("reason"))
            times[r] = times.get(r, 0) + 1
        for a in answers:
            key = (role, a["id"])
            if key in seen:
                bad.add(a["id"])
            e = shown.get(a["id"]) or {}
            verdict = a.get("verdict")
            if verdict == "correct":
                if times[norm_reason(a.get("reason"))] > 1:
                    verdict, duplicate = "unanswered (duplicate reason, D50)", duplicate + 1
                elif not specific(a.get("reason"), e.get("item") or {}):
                    verdict, generic = "unanswered (generic reason, D50)", generic + 1
            seen[key] = (verdict, e.get("hash"))
    if report is not None:
        report.update({"generic_correct": generic, "duplicate_reason_correct": duplicate})
    out = set()
    for i in items:
        h = item_hash(i)
        if i["id"] not in bad and all(seen.get((r, i["id"])) == ("correct", h) for r in ("a", "b")):
            out.add(i["id"])
    return out


def ingest_verify(run):
    """Verifier agreement (vision.ingest_verify) and the automatic route per item -> route.json."""
    run = Path(run)
    rep = vision.ingest_verify(run)
    items = [json.loads(ln) for ln in (run / "items.jsonl").read_text().splitlines() if ln.strip()]
    d50 = {}
    ok = proven_by_both(run, items, d50)
    route = {i["id"]: ("auto" if not i["findings"] and i["quote_confirmed"] and i["id"] in ok else "review")
             for i in items}
    hashes = {i["id"]: item_hash(i) for i in items}
    out = {"items": len(items), "auto": sum(v == "auto" for v in route.values()),
           "review": sum(v == "review" for v in route.values()), "route": route, "hashes": hashes,
           "decided": datetime.now(timezone.utc).isoformat(timespec="seconds"), "d50": d50, "verify": {k: v for k, v in rep.items()
                                                                                         if k != "cases"}}
    (run / "route.json").write_text(json.dumps(out, indent=1))
    print({k: out[k] for k in ("items", "auto", "review")})
    return out


def recheck(run):
    """Re-runs the deterministic checks on a run's items as they are (no item changes: same ids and hashes), then
    routes again with the verifiers' existing answers: for a check that was corrected after verification."""
    run = Path(run)
    meta = json.loads((run / "source.json").read_text())
    source = meta["source"]
    if vision.sha256(OFFICIAL / source) != meta["sha256"]:
        raise SystemExit(f"{source} changed since {run.name} was drafted: draft and verify a new run")
    items = [json.loads(ln) for ln in (run / "items.jsonl").read_text().splitlines() if ln.strip()]
    for i in items:
        before = item_hash(i)
        i["findings"], i["quote_confirmed"] = check_item(i, source, i["section"])
        if item_hash(i) != before:
            raise SystemExit(f"{i['id']} changed during recheck")
        i["hash"] = before
    with open(run / "items.jsonl", "w", encoding="utf-8") as f:
        for i in items:
            f.write(json.dumps(i, ensure_ascii=False) + "\n")
    rep = json.loads((run / "report.json").read_text())
    rep["findings"] = {}
    for i in items:
        for c, _ in i["findings"]:
            rep["findings"][c] = rep["findings"].get(c, 0) + 1
    rep["quote_confirmed"] = sum(i["quote_confirmed"] for i in items)
    rep["rechecked"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    (run / "report.json").write_text(json.dumps(rep, indent=1, ensure_ascii=False))
    if (run / "verify" / "answers").exists():
        return ingest_verify(run)


def main():
    cmd, args = sys.argv[1], sys.argv[2:]
    if cmd == "prepare-draft":
        prepare_draft(args[0], set(args[1:]) or None)
    elif cmd == "ingest-draft":
        ingest_draft(args[0])
    elif cmd == "prepare-verify":
        prepare_verify(args[0])
    elif cmd == "ingest-verify":
        ingest_verify(args[0])
    elif cmd == "prepare-redraft":
        prepare_redraft(args[0])
    elif cmd == "recheck":
        recheck(args[0])
    elif cmd == "reverify":
        supersede_verify(args[0])
        prepare_verify(args[0])
    else:
        raise SystemExit(__doc__)


if __name__ == "__main__":
    main()
