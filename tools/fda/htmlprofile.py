"""HTML profile (D47 D): checklist items drafted from FDA web pages, checked against the page's exact text.

  python3 tools/fda/htmlprofile.py prepare-draft SOURCE [UNIT ...]   # default: every unit of SOURCE
  python3 tools/fda/htmlprofile.py ingest-draft RUN                  # checks, coverage -> RUN/items.jsonl, report.json
  python3 tools/fda/htmlprofile.py prepare-verify RUN                # verifier A and B batches (unit text + items)
  python3 tools/fda/htmlprofile.py ingest-verify RUN                 # agreement + automatic route -> RUN/route.json
  python3 tools/fda/htmlprofile.py prepare-redraft RUN               # new run drafting only RUN's coverage gaps
  python3 tools/fda/htmlprofile.py recheck RUN                       # deterministic checks again, re-route

The page is read as text (no rendering, no vision): tools/parse/fdahtml.py gives the text blocks of the page's
<article> in order (paragraphs, list items, headings). Units and references:
  Q&A pages      one unit per question, "Q4"; the question is paragraph "Q4", its answer blocks "Q4.1", "Q4.2", ...;
                 the reference list and date under each answer, the question index and page chrome are left out
  other pages    paragraphs "¶1", "¶2", ... in page order (fdahtml's numbering); headings and short labels are
                 shown as context, not cited; units are runs of paragraphs of about UNIT_CHARS characters, named
                 "¶12-¶20". The clause of an item is its Q&A number, or its paragraph with the heading path above it
                 (several ORA guides print a heading after its text in the HTML: the paragraph number is the
                 locator, the heading path is context only)
Checks: as the XML profile (tools/fda/xmlprofile.py): clause (a paragraph of the unit), quote (exact text of that
paragraph, token for token, running on into the following blocks of the unit if at all), numbers both ways,
strength, conditions, lead-in (a list item takes the condition of the paragraph ending ":" above it), plants.
Guidance wording: "FDA expects / recommends" is recommended; an imperative addressed to the investigator
("Determine whether ...", "Check ...", "Review ...") is an inspection point and counts for coverage.
Automatic route (D47): no finding, quote confirmed, both blind verifiers say correct; everything else goes to the
review queue (tools/fda/review.py).
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
sys.path.insert(0, str(HERE))
import obligations  # noqa: E402
import quotes  # noqa: E402
import vision  # noqa: E402
import xmlprofile as X  # noqa: E402
from common import OFFICIAL  # noqa: E402

PROMPTS = HERE / "prompts"
UNIT_CHARS = 5000
DRAFT_SCHEMA = json.loads(json.dumps(X.DRAFT_SCHEMA).replace('"section"', '"unit"'))

REFS_LABEL = re.compile(r"^(?:References?|Resources?|Related (?:Information|Links?)|For more information|"
                        r"Contact for further information)\s*:?\s*$", re.I)
DATE = re.compile(r"^(?:Date|Posted|Last updated|Updated)\s*:", re.I)
# Q&A blocks that are no answer text: they keep their number (references stay stable) but are not citable
NOISE = re.compile(r"^(?:Back to Top|Date(?: Revised| Posted)?\s*:?\s*\d.*|CDER Key Officials)$", re.I)
EMAIL = re.compile(r"^\S+@\S+$")


def blocks(source):
    import fdahtml
    return fdahtml.blocks(OFFICIAL / source)


def paragraphs(source, cache={}):
    """[{ref, unit, text, li, heading, cite}] of the page in order; cite False for context (headings, labels)."""
    if source in cache:
        return cache[source]
    import fdahtml
    bl = blocks(source)
    found, index = fdahtml.questions(bl)
    out = []
    if found:
        q, k, skip_li = None, 0, False
        for i, b in enumerate(bl):
            t = b["text"]
            if i in found:
                q, k, skip_li = f"Q{found[i]}", 0, False
                out.append({"ref": q, "unit": q, "text": re.sub(r"^(?:Q\s?)?\d{1,3}\.\s+", "", t), "li": False,
                            "heading": "", "cite": True})
                continue
            if q is None or i in index or fdahtml.NAV.match(t) or EMAIL.match(t) or b["tag"] in ("h1", "h2"):
                if b["tag"] in ("h1", "h2"):
                    q = None                      # a new part of the page ends the answer
                continue
            if REFS_LABEL.match(t):
                skip_li = True                    # the reference list under an answer
                continue
            if DATE.match(t):
                skip_li = False
                continue
            if skip_li and b["tag"] == "li":
                continue
            skip_li = False
            k += 1
            out.append({"ref": f"{q}.{k}", "unit": q, "text": t, "li": b["tag"] == "li", "heading": "",
                        "cite": not NOISE.match(t)})
    else:
        heads, para = [], 0
        for b in bl:
            t = b["text"]
            if fdahtml.NAV.match(t):
                continue
            if b["tag"] in fdahtml.HEADINGS or (b["bold"] and len(t) < 120):
                level = int(b["tag"][1]) if b["tag"] in fdahtml.HEADINGS else 7
                heads = [h for h in heads if h[0] < level] + [(level, (b["marker"] + ". " if b["marker"] else "") + t)]
                out.append({"ref": "", "unit": "", "text": t, "li": False, "heading": "", "cite": False})
            elif len(t) < fdahtml.SHORT and not t.endswith((".", "?", ";", ":")):
                out.append({"ref": "", "unit": "", "text": t, "li": False, "heading": "", "cite": False})
            else:
                para += 1
                out.append({"ref": f"¶{para}", "unit": "", "text": t, "li": b["tag"] == "li",
                            "heading": " > ".join(h for _, h in heads), "cite": True})
        size, start = 0, None
        for p in out:                             # units: runs of about UNIT_CHARS characters
            if p["cite"] and (start is None or size + len(p["text"]) > UNIT_CHARS and size and not p["li"]):
                start, size = p["ref"], 0
            p["unit"] = start or "¶1"
            size += len(p["text"])
        names = {}
        for p in out:
            if p["cite"]:
                names.setdefault(p["unit"], []).append(p["ref"])
        for p in out:
            refs = names.get(p["unit"])
            if refs:
                p["unit"] = refs[0] if len(refs) == 1 else f"{refs[0]}-{refs[-1]}"
    cache[source] = out
    return out


def units(source):
    """{unit: [paragraph]} in page order (context blocks stay with the unit around them)."""
    out = {}
    for p in paragraphs(source):
        if p["unit"]:
            out.setdefault(p["unit"], []).append(p)
    return out


def cited(source):
    return {p["ref"]: p for p in paragraphs(source) if p["cite"]}


def clause_of(source, ref):
    """The item's clause for people: the Q&A number ("Q4"), or the paragraph with its heading path."""
    p = cited(source).get(ref)
    if not p:
        return ref
    if ref.startswith("Q"):
        return ref.split(".")[0]
    return f"{p['heading']} {ref}".strip() if p["heading"] else ref


def lead_in(ref, source):
    """The lead-in over a list item: the nearest paragraph above it in its unit that is not a list item, when its
    text ends in ":" (its last sentence, with earlier sentences that carry no obligation word of their own)."""
    paras = [p for p in units(source)[cited(source)[ref]["unit"]] if p["cite"]]
    pos = next(k for k, p in enumerate(paras) if p["ref"] == ref)
    if not paras[pos]["li"]:
        return ""
    for p in reversed(paras[:pos]):
        if not p["li"]:
            t = p["text"].rstrip()
            if not t.endswith(":"):
                return ""
            sents = obligations.sentences(t) or [t]
            return " ".join([x for x in sents[:-1] if not obligations.strength(x)] + [sents[-1]])
    return ""


def run_on(ref, source):
    """The paragraph's text and the cited blocks after it in its unit, up to the next heading or label:
    (own text, following texts)."""
    blocks = units(source)[cited(source)[ref]["unit"]]
    pos = next(k for k, p in enumerate(blocks) if p["ref"] == ref)
    after = []
    for p in blocks[pos + 1:]:
        if not p["cite"]:
            break
        after.append(p["text"])
    return blocks[pos]["text"], after


MIN_OWN = 3


def quote_found(q, ref, source):
    """The quote is a run of the exact tokens of ref's text, running on, if at all, into the blocks after it in
    the unit (not across a heading), and at least MIN_OWN of its tokens (or all of it) come from ref itself: a
    quote that only touches ref's last word and is really the next paragraph's cites the wrong paragraph."""
    own, after = run_on(ref, source)
    if not q or (len(q) < X.MIN_QUOTE_TOKENS and q != quotes.toks(own)):
        return False
    o = quotes.toks(own)
    whole = o + quotes.toks(" ".join(after))
    need = min(MIN_OWN, len(q))
    return any(whole[s:s + len(q)] == q and len(o) - s >= need for s in range(len(o)))


EXPECTS = re.compile(r"\b(?:FDA|the agency|we)\s+(?:would\s+|will\s+|does\s+|also\s+|further\s+|generally\s+)*(?:expects?|recommends?|"
                     r"encourages?|advises?)\b|\bit is (?:important|essential|critical) (?:to|that)\b", re.I)
# Inspection points in ORA guides and ITGs: a sentence that starts with an instruction to the investigator.
IMPERATIVE = re.compile(r"^(?:Also,?\s+|Always\s+|In addition,?\s+|Then\s+)?(?:Determine|Check|Examine|Review|"
                        r"Evaluate|Verify|Confirm|Assure|Ensure|Inspect|Observe|Look|Find out|Establish|Compare|"
                        r"Obtain|Audit|Document|Assess|Identify|Note|Ask|Question)\b(?!\s+(?:of|that|is|was|were|are)\b)")


# "may not be adequate" states a possibility, not a prohibition (Guide to Inspections: "equipment sterilization
# processes may not be adequate to achieve significant inactivation ... of pyrogens")
NOT_POSSIBLE = re.compile(r"\b(?:may|might|can|could)\s+not\s+(?:always\s+|necessarily\s+)?be\s+(?:adequate|"
                          r"sufficient|suitable|appropriate|possible|necessary|effective|accurate|representative|"
                          r"feasible|practical|uniform|soluble|reliable)\b"
                          r"|\b(?:may|might|can|could)\s+(?:also\s+)?be\s+(?:more|less|very|particularly|difficult|"
                          r"hard|easier|harder)\b"
                          r"|\b(?:can|may|could)\s+be\s+(?:summarized|described|found|seen|viewed|accessed|in|present)\b"
                          r"|\b(?:may|might|can|could)\s+(?:contaminate|harbor|enter|grow|survive|persist|need|be needed|constitute)\b",
                          re.I)
# "These regulations require ...", "§ 211.84 requires ...": a legal requirement stated in guidance
REG_REQUIRES = re.compile(r"\b(?:regulations?|CGMPs?|CFR\s+[\d.()a-z]+|§\s*[\d.()a-z]+|section\s+\d[\d.()a-z]*|statute|Act)"
                          r"\s+(?:also\s+|explicitly\s+|specifically\s+|clearly\s+)?"
                          r"(?:require|requires|mandate|mandates|prohibit|prohibits)\b", re.I)
# "determine if ...", "check if ...": an indirect question, not a condition
ASK_IF = re.compile(r"\b(determin(?:e|es|ed|ing)|check(?:s|ed|ing)?|see|verify(?:ing)?|establish(?:ing)?|ascertain|"
                    r"evaluat(?:e|ing)|assess(?:ing)?|confirm(?:ing)?|question|ask|know|find out)\s+if\b", re.I)


PLUSMINUS = re.compile(r"\+\s*/\s*-\s*")
# wording that names sterility without limiting the text to sterile or non-sterile products: "a probability of a
# non-sterile unit", "(other than water intended to be sterile)"
NOT_SCOPE = re.compile(r"\bprobability of (?:a )?non-?sterile units?\b|\((?:other than|except|excluding)[^()]*\)", re.I)
# "may be made only by distillation": a restriction, not a permission
MAY_ONLY = re.compile(r"\bmay\s+(?:be\s+\w+\s+)?only\b(?!\s+(?:a|an|one|be|rarely|occasionally)\b)", re.I)


def strength_of(text):
    """xmlprofile.strength_words, with "FDA expects / recommends" as recommended; "may not be adequate" is no
    prohibition; "may ... only" is a restriction (mandatory)."""
    text = NOT_POSSIBLE.sub(" ", text or "")
    text = MAY_ONLY.sub("must only", text)
    if re.match(r"\s*Only\b", text) and re.search(r"\bmay\b", text):      # "Only validated methods may be used"
        return "mandatory"
    if REG_REQUIRES.search(text):
        return "mandatory"
    return X.strength_words(text) or ("recommended" if EXPECTS.search(text) else None)


def counts(sentence):
    """An obligation sentence the unit's items must cover."""
    return vision.counts_for_coverage(sentence) or bool(EXPECTS.search(sentence)) or bool(IMPERATIVE.match(sentence))


def check_item(item, source, unit=None):
    """(findings, quote confirmed); unit: the unit the drafter answered for (its items must cite it)."""
    import layer1
    paras = cited(source)
    ref = item["clause_number"].strip()
    if ref not in paras:
        return [("clause", f"{ref!r} is not a paragraph of {source}")], False
    out = []
    if unit and paras[ref]["unit"] != unit:
        out.append(("clause", f"{ref!r} is not in unit {unit}"))
    found = quote_found(quotes.toks(item["quote"]), ref, source)
    if not found:
        out.append(("quote", f"quote not in the text of {ref} (exact page text, starting in {ref} itself, "
                             f"at least {X.MIN_QUOTE_TOKENS} tokens)"))
    lead = lead_in(ref, source)
    item = dict(item, statement=PLUSMINUS.sub("± ", item["statement"]), quote=PLUSMINUS.sub("± ", item["quote"]))
    for n in re.findall(r"\d+(?:[.,]\d+)?", CFR_REF.sub(" ", item["statement"])):
        if not layer1.number_found(n, [item["quote"], lead]):
            out.append(("numbers", f"{n} in the statement, not in the quote or its lead-in"))
    for n in re.findall(r"(?<![\w.^§])\d+(?:[.,]\d+)?", X.without_refs(CFR_REF.sub(" ", item["quote"]))):
        if not layer1.number_found(n, [item["statement"]]):
            out.append(("numbers", f"{n} in the quote, not in the statement"))
    words = strength_of(item["quote"]) or strength_of(lead)
    if words and words != item["strength"]:
        out.append(("strength", f"quote says {words}, item {item['strength']}"))
    missing = layer1.conditions_missing(ASK_IF.sub(r"\1 whether", item["quote"]),
                                        layer1.conditions_in(re.sub(r"\bprovided\b(?!\s+(?:that|it)\b)",
                                                                    "provided that", item["statement"])))
    if missing:
        out.append(("conditions", "quote has " + ", ".join(missing) + " wording the statement lacks"))
    lm = vision.lead_in_missing(lead, item["statement"]) + X.qualifier_missing(lead, item["statement"])
    if lm:
        out.append(("lead-in", f"the statement lacks the lead-in's condition: {'; '.join(lm)[:160]}"))
    pf = X.plants_finding(NOT_SCOPE.sub(" ", item["quote"] + " " + lead), item["plant_types"])
    if pf:
        out.append(("plants", pf))
    return out, found


# "21 CFR 211.42(d)", "section 501(a)(2)(B)", "Part 11": references, not numbers a statement must repeat
_R = r"\d+\.\d+(?:\([^()\s]{1,5}\))*"
_S = r"(?:\s*,\s*(?:and\s+|or\s+)?|\s+and\s+|\s+or\s+|\s*[-–]\s*|\s+through\s+)"
CFR_REF = re.compile(rf"\b(?:\d+\s+)?CFR\s+(?:parts?\s+\d{{2,}}(?:{_S}\d{{2,}}\b)*|{_R}(?:{_S}{_R})*)"
                     rf"|§§?\s*{_R}(?:{_S}{_R})*"
                     rf"|\bsections?\s+\d+(?:\.\d+)?[A-Za-z]?(?:\([^()\s]{{1,5}}\))*|\bparts?\s+\d{{2,}}(?:{_S}\d{{3,}}\b)*", re.I)


def coverage(source, unit, items, na):
    """Obligation sentences of the unit's paragraphs not covered: as xmlprofile.coverage, where an item covers its
    own paragraph, the paragraphs its quote runs into, and its lead-in."""
    import layer1
    gaps = []
    na_raw = [(x["clause_number"].strip(), quotes.toks(x["text"])) for x in na]
    paras = [p for p in units(source)[unit] if p["cite"]]
    order = [p["ref"] for p in paras]
    for p in paras:
        ref, pos = p["ref"], order.index(p["ref"])
        mine = [i["quote"] for i in items if covers(i, ref, source)]
        for s in obligations.sentences(p["text"]):
            if not counts(s):
                continue
            s0, s = s, bare(s)                    # measured without its regulation references
            ws, conds, st = vision._words(s), layer1.conditions_in(s), quotes.toks(s)
            if not ws:
                continue
            if any(sum(w in set(vision._words(q)) for w in ws) / len(ws) >= vision.COVERED_SHARE
                   and not (conds - layer1.conditions_in(q)) for q in mine):
                continue
            parts = [q for q in mine if quotes.contains(quotes.toks(bare(q)), st)]
            if parts:
                union = set().union(*(set(vision._words(q)) for q in parts))
                nums = set(re.findall(r"\d+(?:[.,]\d+)?", s)) - set(re.findall(r"\d+(?:[.,]\d+)?", " ".join(parts)))
                if (sum(w in union for w in ws) / len(ws) >= vision.UNION_SHARE and not nums
                        and not (conds - layer1.conditions_in(" ".join(parts)))):
                    continue
            st0 = quotes.toks(s0)
            if any(c == ref and (quotes.contains(k[:8], st0) if len(st0) >= 8 else k == st0) for c, k in na_raw):
                continue
            if lead_in_covered(ref, s0, items, source):
                continue
            gaps.append({"clause": ref, "sentence": s0[:300]})
    return gaps


SEE = re.compile(r"\(\s*(?:see|cf\.?|refer to)?\s*\)|\bunder\s*,", re.I)


def bare(sentence):
    """A sentence without its regulation references ("(see 21 CFR 211.150(b))", "Under 21 CFR 211.180(e), ..."):
    a quote that leaves them out still covers it."""
    t = SEE.sub(" ", CFR_REF.sub(" ", sentence))
    return re.sub(r"\s+", " ", re.sub(r"^\s*,\s*", "", t)).strip()


def lead_in_ref(ref, source):
    """The reference of the paragraph whose ":" introduces the list item ref ("" if none; see lead_in)."""
    paras = [p for p in units(source)[cited(source)[ref]["unit"]] if p["cite"]]
    pos = next(k for k, p in enumerate(paras) if p["ref"] == ref)
    if not paras[pos]["li"]:
        return ""
    for p in reversed(paras[:pos]):
        if not p["li"]:
            return p["ref"] if p["text"].rstrip().endswith(":") else ""
    return ""


def covers(item, ref, source):
    """Can the item's quote cover sentences of paragraph ref? When it cites ref; when it cites an earlier paragraph
    and its quote runs on into ref (its last tokens are in ref's text, not in the cited paragraph alone); when it
    cites a list item whose lead-in is ref."""
    c = item["clause_number"].strip()
    if c not in cited(source):
        return False
    if c == ref:
        return True
    if lead_in_ref(c, source) == ref:
        return True
    own, after = run_on(c, source)
    if ref not in [p["ref"] for p in units(source)[cited(source)[c]["unit"]]]:
        return False
    q = quotes.toks(item["quote"])
    if not q or quotes.contains(q, quotes.toks(own)):
        return False
    texts = [p for p in units(source)[cited(source)[c]["unit"]] if p["cite"]]
    k = next(i for i, p in enumerate(texts) if p["ref"] == c)
    if ref not in [p["ref"] for p in texts[k + 1:k + 1 + len(after)]]:
        return False
    return bool(set(q[-4:]) & set(quotes.toks(cited(source)[ref]["text"]))) or quotes.contains(
        quotes.toks(cited(source)[ref]["text"])[:4], q)


def lead_in_covered(ref, sentence, items, source):
    """A lead-in sentence (ending ":") with at most one obligation word is covered when every list item under it
    has an item and none of those items lacks its condition (xmlprofile.lead_in_covered)."""
    if not sentence.rstrip().endswith(":"):
        return False
    if len(re.findall(r"\b(?:shall|must|should|may|is required|are required)\b", sentence, re.I)) > 1:
        return False
    paras = [p for p in units(source)[cited(source)[ref]["unit"]] if p["cite"]]
    pos = next(k for k, p in enumerate(paras) if p["ref"] == ref)
    kids = []
    for p in paras[pos + 1:]:
        if not p["li"]:
            break
        kids.append(p["ref"])
    if not kids:
        return False
    for k in kids:
        mine = [i for i in items if i["clause_number"].strip() == k]
        if not mine:
            return False
        if any(vision.lead_in_missing(sentence, i["statement"]) or X.qualifier_missing(sentence, i["statement"])
               for i in mine):
            return False
    return True


def unit_payload(source, unit):
    return [{"ref": p["ref"], "text": p["text"], **({"list_item": True} if p["li"] else {}),
             **({"heading_path": p["heading"]} if p["heading"] else {})} if p["cite"]
            else {"context": p["text"]} for p in units(source)[unit]]


def pack(keys, source):
    secs = {k: [(p["ref"], p["text"]) for p in v] for k, v in units(source).items()}
    return X.pack(keys, secs)


def page_kind(source):
    if any(p["ref"].startswith("Q") for p in paragraphs(source)):
        return "Q&A page (questions and answers on CGMP; nonbinding FDA guidance)"
    return "FDA web page (inspection guide, inspection technical guide, compliance policy guide or alert)"


def prepare_draft(source, wanted=None):
    run = vision.new_run("html-draft")
    us = units(source)
    keys = [u for u in us if not wanted or u in wanted]
    if wanted and set(wanted) - set(keys):
        raise SystemExit(f"not units of {source}: {sorted(set(wanted) - set(keys))}")
    instructions = (PROMPTS / "draft_html.md").read_text()
    batches = pack(keys, source)
    for n, group in enumerate(batches, start=1):
        payload = [{"id": f"{source}:{u}", "source": source, "unit": u, "page_kind": page_kind(source),
                    "plant_scope": vision.scope(source), "paragraphs": unit_payload(source, u)} for u in group]
        (run / "batches" / f"batch_{n:03d}.json").write_text(json.dumps(
            {"instructions": instructions, "topics": vision.topics(), "schema": DRAFT_SCHEMA, "units": payload},
            indent=1, ensure_ascii=False))
    (run / "source.json").write_text(json.dumps({"source": source, "sha256": vision.sha256(OFFICIAL / source),
                                                 "profile": "html", "units": keys}, indent=1))
    print(run, len(batches), "batches")
    return run


def prepare_redraft(run):
    run = Path(run)
    src = json.loads((run / "source.json").read_text())["source"]
    rep = json.loads((run / "report.json").read_text())
    if rep.get("failed"):
        raise SystemExit(f"units without a usable answer: {rep['failed']}; draft them again in a new run first")
    gaps = rep["coverage_gaps"]
    if not gaps:
        raise SystemExit("no coverage gaps")
    new = vision.new_run("html-redraft")
    keys = list(dict.fromkeys(g["unit"] for g in gaps))
    instructions = (PROMPTS / "draft_html.md").read_text() + (
        "\n\nREDRAFT: earlier items already cover this unit except the sentences in \"gaps\". Write items, or "
        "not_applicable entries, for those sentences only; do not repeat other obligations.\n")
    payload = [{"id": f"{src}:{k}", "source": src, "unit": k, "page_kind": page_kind(src),
                "plant_scope": vision.scope(src), "paragraphs": unit_payload(src, k),
                "gaps": [{"clause": g["clause"], "sentence": g["sentence"]} for g in gaps if g["unit"] == k]}
               for k in keys]
    (new / "batches" / "batch_001.json").write_text(json.dumps(
        {"instructions": instructions, "topics": vision.topics(), "schema": DRAFT_SCHEMA, "units": payload},
        indent=1, ensure_ascii=False))
    (new / "source.json").write_text(json.dumps({"source": src, "sha256": vision.sha256(OFFICIAL / src),
                                                 "profile": "html", "units": keys, "redraft_of": run.name,
                                                 "gaps": gaps}, indent=1))
    print(new)
    return new


def ingest_draft(run):
    run = Path(run)
    if (run / "verify").exists() or (run / "route.json").exists():
        raise SystemExit(f"{run} is already verified: a redraft is a new run (its ids would carry old verdicts)")
    source = json.loads((run / "source.json").read_text())["source"]
    items, rep = [], {"units": 0, "items": 0, "quote_confirmed": 0, "findings": {}, "coverage_gaps": [],
                      "not_applicable": 0, "failed": []}
    for bf in sorted((run / "batches").glob("batch_*.json")):
        batch = json.loads(bf.read_text())
        af = run / "answers" / bf.name
        answers, dup = {}, set()
        for a in (json.loads(af.read_text())["answers"] if af.exists() else []):
            key = a.get("unit", "").rsplit(":", 1)[-1]
            if key in answers:
                dup.add(key)
            answers[key] = a
        for u in batch["units"]:
            a = answers.get(u["unit"])
            if a is None or u["unit"] in dup:
                rep["failed"].append(u["id"])
                continue
            rep["units"] += 1
            rep["not_applicable"] += len(a["not_applicable"])
            for k, it in enumerate(a["items"], start=1):
                found, ok = check_item(it, source, u["unit"])
                rep["quote_confirmed"] += ok
                for c, _ in found:
                    rep["findings"][c] = rep["findings"].get(c, 0) + 1
                items.append({"id": f"{u['id']}#{k}", "source": source, "section": u["unit"], **it,
                              "clause": clause_of(source, it["clause_number"].strip()),
                              "findings": found, "quote_confirmed": ok, "hash": X.item_hash(it)})
            found_gaps = coverage(source, u["unit"], a["items"], a["not_applicable"])
            if "gaps" in u:
                asked = {(g["clause"], g["sentence"]) for g in u["gaps"]}
                found_gaps = [g for g in found_gaps if (g["clause"], g["sentence"]) in asked]
            rep["coverage_gaps"] += [{"unit": u["unit"], **g} for g in found_gaps]
    rep["items"] = len(items)
    with open(run / "items.jsonl", "w", encoding="utf-8") as f:
        for i in items:
            f.write(json.dumps(i, ensure_ascii=False) + "\n")
    (run / "report.json").write_text(json.dumps(rep, indent=1, ensure_ascii=False))
    print(json.dumps({k: (len(v) if isinstance(v, list) else v) for k, v in rep.items()}, indent=1))
    return rep


def prepare_verify(run):
    """Verifier A and B batches, one per group of units: each item with its unit's paragraphs (blind)."""
    run = Path(run)
    items = [json.loads(ln) for ln in (run / "items.jsonl").read_text().splitlines() if ln.strip()]
    source = json.loads((run / "source.json").read_text())["source"]
    vdir = run / "verify"
    if vdir.exists() and any(vdir.rglob("*.json")):
        raise SystemExit(f"{vdir} already holds verify batches or answers: verify a redraft in a new run")
    (vdir / "batches").mkdir(parents=True, exist_ok=True)
    (vdir / "answers").mkdir(exist_ok=True)
    groups = {}
    for it in items:
        groups.setdefault(it["section"], []).append(it)
    chunks = pack(list(groups), source)
    n = 0
    for role in ("a", "b"):
        instructions = (PROMPTS / f"verify_html_{role}.md").read_text()
        for chunk in chunks:
            n += 1
            payload = {"role": role, "instructions": instructions, "schema": vision.VERIFY_SCHEMA,
                       "page_kind": page_kind(source),
                       "units": [{"unit": u, "paragraphs": unit_payload(source, u)} for u in chunk],
                       "items": [{"id": it["id"], "unit": it["section"], "hash": it["hash"],
                                  "item": {k: it[k] for k in ("statement", "quote", "clause_number", "strength",
                                                              "plant_types", "condition")},
                                  "plant_scope": vision.scope(source)} for u in chunk for it in groups[u]]}
            (vdir / "batches" / f"batch_{n:03d}_{role}.json").write_text(json.dumps(payload, indent=1,
                                                                                    ensure_ascii=False))
    print(vdir, n, "batches")


def ingest_verify(run):
    return X.ingest_verify(run)


def recheck(run):
    """The deterministic checks again on a run's items as they are (same ids and hashes), then routes again."""
    run = Path(run)
    meta = json.loads((run / "source.json").read_text())
    source = meta["source"]
    if vision.sha256(OFFICIAL / source) != meta["sha256"]:
        raise SystemExit(f"{source} changed since {run.name} was drafted: draft and verify a new run")
    items = [json.loads(ln) for ln in (run / "items.jsonl").read_text().splitlines() if ln.strip()]
    for i in items:
        before = X.item_hash(i)
        i["findings"], i["quote_confirmed"] = check_item(i, source, i["section"])
        i["clause"] = clause_of(source, i["clause_number"].strip())
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
    rep["coverage_gaps"] = coverage_of(run, source)
    rep["rechecked"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    (run / "report.json").write_text(json.dumps(rep, indent=1, ensure_ascii=False))
    if (run / "verify" / "answers").exists():
        return ingest_verify(run)


def coverage_of(run, source):
    """The coverage gaps of a run's answers, computed again (a redraft is judged on the sentences it was given)."""
    gaps = []
    for af in sorted((run / "answers").glob("batch_*.json")):
        batch = {u["unit"]: u for u in json.loads((run / "batches" / af.name).read_text())["units"]}
        for a in json.loads(af.read_text())["answers"]:
            u = batch.get(a.get("unit", "").rsplit(":", 1)[-1])
            if not u:
                continue
            found = coverage(source, u["unit"], a["items"], a["not_applicable"])
            if "gaps" in u:
                asked = {(g["clause"], g["sentence"]) for g in u["gaps"]}
                found = [g for g in found if (g["clause"], g["sentence"]) in asked]
            gaps += [{"unit": u["unit"], **g} for g in found]
    return gaps


def main():
    if len(sys.argv) < 3:
        raise SystemExit(__doc__)
    cmd, args = sys.argv[1], sys.argv[2:]
    fn = {"prepare-draft": lambda: prepare_draft(args[0], set(args[1:]) or None),
          "ingest-draft": lambda: ingest_draft(args[0]), "prepare-verify": lambda: prepare_verify(args[0]),
          "ingest-verify": lambda: ingest_verify(args[0]), "prepare-redraft": lambda: prepare_redraft(args[0]),
          "recheck": lambda: recheck(args[0])}.get(cmd)
    if not fn:
        raise SystemExit(__doc__)
    fn()


if __name__ == "__main__":
    main()
