"""XML profile (D47): checklist items drafted from eCFR XML sections, checked against the exact XML text.

  python3 tools/fda/xmlprofile.py prepare-draft SOURCE [SECTION ...]   # default: every section of SOURCE
  python3 tools/fda/xmlprofile.py ingest-draft RUN                     # checks, coverage -> RUN/items.jsonl, report.json
  python3 tools/fda/xmlprofile.py prepare-verify RUN                   # verifier A and B batches (section text + items)
  python3 tools/fda/xmlprofile.py ingest-verify RUN                    # agreement + automatic route -> RUN/route.json

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
    """A paragraph's text without its leading designation ("(c) ", "§ 211.84 ")."""
    return re.sub(r"^(?:§\s*[\d.]+\s*|\([^()]{1,6}\)\s*)+", "", text).strip()


def prepare_draft(source, wanted=None):
    run = vision.new_run("xml-draft")
    secs = sections(source)
    keys = [s for s in secs if not wanted or s in wanted]
    instructions = (PROMPTS / "draft_xml.md").read_text()
    batches = [keys[i:i + SECTIONS_PER_BATCH] for i in range(0, len(keys), SECTIONS_PER_BATCH)]
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


def lead_in_text(ref, paras):
    """The lead-ins over a paragraph: every ancestor paragraph whose own text ends in ":", nearest first
    (211.42(c)(10)(i) takes (c)(10) "Aseptic processing, which includes as appropriate:" and (c)'s "... as are
    necessary to prevent contamination or mixups during the course of the following procedures:")."""
    out, r = [], parent(ref)
    while r:
        t = own_text(r, paras.get(r, ""))
        if not t.rstrip().endswith(":"):
            break
        out.append(t)
        r = parent(r)
    return " ".join(out)


def check_item(item, source):
    """(findings, quote confirmed)."""
    import layer1
    paras = dict(paragraphs(source))
    ref = item["clause_number"].strip()
    out = []
    if ref not in paras:
        return [("clause", f"{ref!r} is not a paragraph of {source}")], False
    kids = [t for r, t in paragraphs(source) if r == ref or r.startswith(ref + "(")]
    q = quotes.toks(item["quote"])
    found = quotes.contains(q, quotes.toks(" ".join(kids)))
    if not found:
        out.append(("quote", f"quote not in the text of {ref} (exact XML text)"))
    for n in re.findall(r"\d+(?:[.,]\d+)?", item["statement"]):
        if not layer1.number_found(n, [item["quote"]]):
            out.append(("numbers", f"{n} in the statement, not in the quote"))
    for n in re.findall(r"(?<![\w.^§])\d+(?:[.,]\d+)?", item["quote"]):
        if not layer1.number_found(n, [item["statement"]]):
            out.append(("numbers", f"{n} in the quote, not in the statement"))
    lead = lead_in_text(ref, paras)
    words = layer1.strength_of(item["quote"]) or (layer1.strength_of(lead) if lead else None)
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
    words (4+ letters) of its purpose ("prevent contamination or mixups"); the list tail ("during the course of
    the following procedures") is not part of the purpose."""
    if not lead:
        return []
    said = set(re.findall(r"[a-z]{4,}", statement.lower()))
    out = []
    for m in QUALIFIER.finditer(lead):
        kind, purpose = m.group(1).lower(), LIST_TAIL.sub("", m.group(2) or "").strip()
        content = set(re.findall(r"[a-z]{4,}", purpose.lower())) - {"their", "there", "this", "that", "these",
                                                                    "with", "from", "such"}
        if not (said & NEED_WORDS[kind]) or (content and len(content & said) / len(content) < 0.8):
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
        mine = [i for i in items if i["clause_number"] == k or i["clause_number"].startswith(k + "(")]
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
    na_keys = [(x["clause_number"], " ".join(quotes.toks(x["text"])[:8])) for x in na]
    for ref, text in sections(source)[section]:
        mine = [i["quote"] for i in items if i["clause_number"] == ref or ref.startswith(i["clause_number"] + "(")
                or i["clause_number"].startswith(ref + "(")]
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
            if any(c in (ref, "") and k and k in " ".join(st) for c, k in na_keys):
                continue
            if lead_in_covered(ref, s, items, source):
                continue
            gaps.append({"clause": ref, "sentence": s[:300]})
    return gaps


def ingest_draft(run):
    run = Path(run)
    source = json.loads((run / "source.json").read_text())["source"]
    items, rep = [], {"sections": 0, "items": 0, "quote_confirmed": 0, "findings": {}, "coverage_gaps": [],
                      "not_applicable": 0, "failed": []}
    for bf in sorted((run / "batches").glob("batch_*.json")):
        batch = json.loads(bf.read_text())
        af = run / "answers" / bf.name
        answers = {a["section"]: a for a in json.loads(af.read_text())["answers"]} if af.exists() else {}
        for u in batch["sections"]:
            a = answers.get(u["id"]) or answers.get(u["section"])
            if a is None:
                rep["failed"].append(u["id"])
                continue
            rep["sections"] += 1
            rep["not_applicable"] += len(a["not_applicable"])
            for k, it in enumerate(a["items"], start=1):
                found, ok = check_item(it, source)
                rep["quote_confirmed"] += ok
                for c, _ in found:
                    rep["findings"][c] = rep["findings"].get(c, 0) + 1
                items.append({"id": f"{u['id']}#{k}", "source": source, "section": u["section"], **it,
                              "findings": found, "quote_confirmed": ok})
            rep["coverage_gaps"] += [{"section": u["section"], **g}
                                     for g in coverage(source, u["section"], a["items"], a["not_applicable"])]
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
    (vdir / "batches").mkdir(parents=True, exist_ok=True)
    (vdir / "answers").mkdir(exist_ok=True)
    groups = {}
    for it in items:
        groups.setdefault(it["section"], []).append(it)
    keys = list(groups)
    chunks = [keys[i:i + SECTIONS_PER_BATCH] for i in range(0, len(keys), SECTIONS_PER_BATCH)]
    n = 0
    for role in ("a", "b"):
        instructions = (PROMPTS / f"verify_xml_{role}.md").read_text()
        for chunk in chunks:
            n += 1
            payload = {"role": role, "instructions": instructions, "schema": vision.VERIFY_SCHEMA,
                       "sections": [{"section": s, "paragraphs": [{"ref": r, "text": t} for r, t in secs[s]]}
                                    for s in chunk],
                       "items": [{"id": it["id"], "section": it["section"],
                                  "item": {k: it[k] for k in ("statement", "quote", "clause_number", "strength",
                                                              "plant_types", "condition")},
                                  "plant_scope": vision.scope(source)} for s in chunk for it in groups[s]]}
            (vdir / "batches" / f"batch_{n:03d}_{role}.json").write_text(json.dumps(payload, indent=1,
                                                                                    ensure_ascii=False))
    print(vdir, n, "batches")


def ingest_verify(run):
    """Verifier agreement (vision.ingest_verify) and the automatic route per item -> route.json."""
    run = Path(run)
    rep = vision.ingest_verify(run)
    verdicts = {}
    for af in sorted((run / "verify" / "answers").glob("batch_*.json")):
        for a in json.loads(af.read_text())["answers"]:
            verdicts.setdefault(a["id"], []).append(a["verdict"])
    items = [json.loads(ln) for ln in (run / "items.jsonl").read_text().splitlines() if ln.strip()]
    route = {i["id"]: ("auto" if not i["findings"] and i["quote_confirmed"] and verdicts.get(i["id"]) == ["correct", "correct"]
                       else "review") for i in items}
    out = {"items": len(items), "auto": sum(v == "auto" for v in route.values()),
           "review": sum(v == "review" for v in route.values()), "route": route,
           "decided": datetime.now(timezone.utc).isoformat(timespec="seconds"), "verify": {k: v for k, v in rep.items()
                                                                                         if k != "cases"}}
    (run / "route.json").write_text(json.dumps(out, indent=1))
    print({k: out[k] for k in ("items", "auto", "review")})
    return out


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
    else:
        raise SystemExit(__doc__)


if __name__ == "__main__":
    main()
