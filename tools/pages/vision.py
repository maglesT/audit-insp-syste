"""Page-based drafting with vision (D45): checklist items drafted from PDF pages, checked on page text.

  python3 tools/pages/vision.py prepare-draft [SOURCE:PAGE ...]   # default: the trial pages (TRIAL)
  python3 tools/pages/vision.py ingest-draft RUN                  # checks + measures -> RUN/items.jsonl, report.json
  python3 tools/pages/vision.py prepare-verify RUN [SOURCE ...]   # verifier A and B batches, one per document
  python3 tools/pages/vision.py ingest-verify RUN                 # verifier agreement -> RUN/verify-report.json

Each page is rendered to PNG at DPI with pypdfium2 (pinned in requirements.txt; image sha256 recorded) and its text
layer taken with `pdftotext -layout`. A drafting agent gets, per page, the image path, the text layer, and the next
page's text when a sentence runs over the break; it writes the items it sees (batch file -> answers file, as in
tools/ai/sessions.py). Nothing here depends on the parsed clause store (frozen, D45).

Checks on each item (deterministic, no AI):
  quote      found word for word (quotes.letters / quotes.contains) on its page, or page + next when the item says
             it runs over (with or without the page's running lines, body()), in BOTH readings; a table row
             (cells joined with " | ") cell by cell, also in pdfminer's ruled-table cell texts (cell_texts): pdftotext -layout and pdfminer (pdfplumber). A quote found in one
             reading only, or in neither, goes to the "text layer differs" list (the image-true reading is kept for
             the verifiers and the spot check; never accepted silently).
  clause     every part of a clause number given by the item ("4.22 i") is printed on the page or the page before
  numbers    every number in the item's statement is in its quote (layer1.number_found)
  strength   the item's strength matches its quote's wording where the quote has one (layer1.strength_of)
  conditions condition wording in the quote has a counterpart in the statement (layer1.conditions_missing)
Coverage per page: every obligation sentence of the page's text layer (tools/parse/obligations.py) has at least
COVERED_SHARE of its words inside one item quote of that page or the page before (carry-over), or is listed by the
drafter as not applicable with a reason.
"""
import hashlib
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "tools" / "library"))
sys.path.insert(0, str(ROOT / "tools" / "parse"))
sys.path.insert(0, str(ROOT / "tools" / "ai"))
import obligations  # noqa: E402
import quotes  # noqa: E402
from common import OFFICIAL  # noqa: E402

DPI = 150
RUNS = ROOT / "library" / "ai-runs"
IMAGES = ROOT / "work" / "vision-pages"            # rendered pages (not in git; sha256 in the run's pages.json)
PROMPTS = HERE / "prompts"
COVERED_SHARE = 0.8
PAGES_PER_BATCH = 5
STRENGTHS = ("mandatory", "recommended", "optional")
PLANTS = ("OSD", "LIQ", "SEMI", "INJ", "API")

# The D45 trial: 5 pages from each of the 10 hardest documents. Known hard pages (tables, landscape pages,
# superscripts, pages of former parser defects) plus ordinary body pages of the same document.
TRIAL = {
    "eu-20220825_gmp-an1_en_0.pdf": [12, 13, 14, 22, 45],
    "pics-pe009-18-annexes.pdf": [18, 19, 20, 21, 22],
    "who-trs1044-a2-sterile.pdf": [17, 18, 19, 20, 52],
    "who-trs1010-a8-hvac-nonsterile.pdf": [8, 9, 15, 16, 17],
    "ich-q3c-r9.pdf": [8, 11, 12, 13, 17],
    "india-cdsco-circ-2024-03-risk-based-inspection.pdf": [16, 17, 45, 48, 116],
    "fda-cp-7356-002-drug-manufacturing-inspections.pdf": [10, 11, 20, 21, 41],
    "fda-guidance-nitrosamine-control-2024.pdf": [10, 11, 12, 20, 41],
    "india-schedule-m-2023-GSR922E.pdf": [155, 156, 157, 163, 271],    # English half starts at p149
    "pics-pi011-3-computerised-systems.pdf": [8, 9, 10, 20, 21],
}

DRAFT_SCHEMA = {
    "type": "object", "required": ["page", "items", "not_applicable"],
    "properties": {
        "page": {"type": "string"},
        "items": {"type": "array", "items": {
            "type": "object",
            "required": ["statement", "quote", "clause_number", "strength", "plant_types", "numbers", "condition",
                         "topic", "runs_over", "text_layer_differs"],
            "properties": {
                "statement": {"type": "string"}, "quote": {"type": "string"},
                "clause_number": {"type": "string"},
                "strength": {"enum": list(STRENGTHS)},
                "plant_types": {"type": "array", "items": {"enum": list(PLANTS)}},
                "numbers": {"type": "array", "items": {"type": "string"}},
                "condition": {"type": "string"}, "topic": {"type": "string"},
                "runs_over": {"type": "boolean"}, "text_layer_differs": {"type": "string"}}}},
        "not_applicable": {"type": "array", "items": {
            "type": "object", "required": ["text", "reason"],
            "properties": {"text": {"type": "string"}, "reason": {"type": "string"}}}}}}

VERIFY_SCHEMA = {
    "type": "object", "required": ["id", "verdict", "quote_as_printed", "reason"],
    "properties": {"id": {"type": "string"}, "verdict": {"enum": ["correct", "incorrect"]},
                   "quote_as_printed": {"type": "boolean"}, "reason": {"type": "string"}}}


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def render(source, pno):
    """The page as PNG at DPI (path, sha256); rendered once into IMAGES."""
    import pypdfium2 as pdfium
    out = IMAGES / f"{Path(source).stem}-p{pno:03d}.png"
    if not out.exists():
        out.parent.mkdir(parents=True, exist_ok=True)
        doc = pdfium.PdfDocument(str(OFFICIAL / source))
        try:
            doc[pno - 1].render(scale=DPI / 72).to_pil().convert("RGB").save(out, optimize=True)
        finally:
            doc.close()
    return out, sha256(out)


def layer_text(source, pno):
    """pdftotext -layout of one page ("" past the last page)."""
    r = subprocess.run(["pdftotext", "-layout", "-f", str(pno), "-l", str(pno), str(OFFICIAL / source), "-"],
                       capture_output=True, text=True)
    return r.stdout.replace("\f", "") if r.returncode == 0 else ""


def pdfminer_text(source, pno, cache={}):
    """pdfminer's text of one page (pdfplumber), the independent second reading."""
    key = (source, pno)
    if key not in cache:
        import pdfplumber
        with pdfplumber.open(str(OFFICIAL / source)) as pdf:
            cache[key] = (pdf.pages[pno - 1].extract_text() or "") if pno <= len(pdf.pages) else ""
    return cache[key]


def page_count(source):
    import pypdfium2 as pdfium
    doc = pdfium.PdfDocument(str(OFFICIAL / source))
    try:
        return len(doc)
    finally:
        doc.close()


def topics():
    t = json.loads((ROOT / "library" / "topics.json").read_text())["topics"]
    return [s for x in t for s in x["sub"]]


def scope(source):
    import csv
    with open(ROOT / "sources" / "catalog.csv", encoding="utf-8") as f:
        row = next(r for r in csv.DictReader(f) if r["file"] == source)
    return list(PLANTS) if row["applies_to"].strip() == "ALL" else row["applies_to"].split(";")


def new_run(stage):
    run = RUNS / f"{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')}-{stage}"
    (run / "batches").mkdir(parents=True)
    (run / "answers").mkdir()
    return run


def prepare_draft(targets):
    run = new_run("vision-draft")
    pages, batch, n = [], [], 0
    instructions = (PROMPTS / "draft.md").read_text()
    for source, pno in targets:
        image, digest = render(source, pno)
        entry = {"id": f"{source}:{pno}", "source": source, "page": pno, "image": str(image.relative_to(ROOT)),
                 "image_sha256": digest, "dpi": DPI, "pdf_sha256": sha256(OFFICIAL / source),
                 "text_layer": layer_text(source, pno), "next_page_text": layer_text(source, pno + 1)[:3000],
                 "plant_scope": scope(source)}
        pages.append({k: v for k, v in entry.items() if k not in ("text_layer", "next_page_text")})
        batch.append(entry)
        last = (source, pno) == targets[-1]
        if len(batch) == PAGES_PER_BATCH or last or targets[targets.index((source, pno)) + 1][0] != source:
            n += 1
            (run / "batches" / f"batch_{n:03d}.json").write_text(json.dumps(
                {"instructions": instructions, "topics": topics(), "schema": DRAFT_SCHEMA, "pages": batch},
                indent=1, ensure_ascii=False))
            batch = []
    import pypdfium2
    (run / "pages.json").write_text(json.dumps({"renderer": f"pypdfium2 {pypdfium2.version.PYPDFIUM_INFO}", "dpi": DPI,
                                                "pages": pages}, indent=1))
    print(run, n, "batches")
    return run


def _words(text):
    return re.findall(r"\w+", text.lower())


def _key(line):
    return re.sub(r"\d+", "#", re.sub(r"\s+", " ", line).strip().lower())


def body(reader, source, pno):
    """A page's text without its running lines: lines (digits masked) that also stand on the page before or after
    (headers, footers, side titles, page numbers), which a reader may put inside a sentence."""
    near = {_key(ln) for p in (pno - 1, pno + 1) if p >= 1 for ln in reader(source, p).splitlines()}
    return "\n".join(ln for ln in reader(source, pno).splitlines() if not (_key(ln) and _key(ln) in near))


def readings(reader, source, span):
    """The text of the pages in span as one reader gives it: whole, and without running lines."""
    return [" ".join(reader(source, p) for p in span), " ".join(body(reader, source, p) for p in span)]


def cell_texts(source, pno, cache={}):
    """pdfminer's text of every cell of the ruled tables pdfplumber finds on a page (a cell's lines kept together,
    which page-order readings interleave with the neighbouring columns)."""
    key = (source, pno)
    if key not in cache:
        import pdfplumber
        with pdfplumber.open(str(OFFICIAL / source)) as pdf:
            page = pdf.pages[pno - 1] if pno <= len(pdf.pages) else None
            cache[key] = [c for t in (page.extract_tables() if page else []) for r in t for c in r if c]
    return cache[key]


def quote_in(quote, texts):
    """The quote is in one of the texts (letters()); a table-row quote (cells joined with " | ") piece by piece, each
    cell in one of the texts."""
    pieces = [quotes.letters(x) for x in quote.split(" | ")] if " | " in quote else [quotes.letters(quote)]
    return all(any(quotes.contains(q, t) for t in texts) for q in pieces if q)


def check_item(item, source, pno):
    """Findings of one item (list of (check, message)) and whether its quote is in each reading."""
    import layer1
    span = [pno, pno + 1] if item["runs_over"] else [pno]
    in_layer = quote_in(item["quote"], [quotes.letters(t) for t in readings(layer_text, source, span)])
    in_miner = quote_in(item["quote"], [quotes.letters(t) for t in readings(pdfminer_text, source, span)]
                        + [quotes.letters(c) for p in span for c in cell_texts(source, p)])
    out = []
    if not (in_layer and in_miner):
        out.append(("quote", f"quote not found in {'pdftotext' if not in_layer else ''}"
                             f"{' and ' if not in_layer and not in_miner else ''}{'pdfminer' if not in_miner else ''}"))
    num = item["clause_number"].strip()
    printed = {t.strip(".:;,()[]").lower() for p in [pno - 1] + span if p >= 1 for t in layer_text(source, p).split()}
    parts = [t.strip(".:;,()[]").lower() for t in num.split()]
    if num and not all(t in printed for t in parts if t):     # "4.22 i", "Table 1", "Part I 10.4": every part, on
        #                                                       this page or the one before (a clause running over)
        out.append(("clause", f"clause number {num!r} not printed on page {pno}"))
    for n in re.findall(r"\d+(?:[.,]\d+)?", item["statement"]):
        if not layer1.number_found(n, [item["quote"]]):
            out.append(("numbers", f"{n} not in the quote"))
    words = layer1.strength_of(item["quote"])
    if words and words != item["strength"]:
        out.append(("strength", f"quote says {words}, item {item['strength']}"))
    said = layer1.conditions_in(item["statement"])
    missing = layer1.conditions_missing(item["quote"], said)
    if missing:
        out.append(("conditions", "quote has " + ", ".join(missing) + " wording the statement lacks"))
    return out, in_layer, in_miner


def coverage(source, pno, items_here, items_before, na):
    """Obligation sentences of the page's text layer not covered (see the module docstring)."""
    text = re.sub(r"\s+", " ", layer_text(source, pno))
    bags = [set(_words(i["quote"])) for i in items_here + items_before]
    na_keys = [quotes.letters(x["text"])[:40] for x in na]
    gaps = []
    for s in obligations.sentences(text):
        if not obligations.strength(s):
            continue
        ws = _words(s)
        if not ws:
            continue
        if any(sum(w in b for w in ws) / len(ws) >= COVERED_SHARE for b in bags):
            continue
        if any(k and k in quotes.letters(s) for k in na_keys):
            continue
        gaps.append(s[:300])
    return gaps


def ingest_draft(run):
    run = Path(run)
    items, failed, report = [], [], {"pages": 0, "items": 0, "quote_both": 0, "quote_layer_only": 0,
                                     "quote_pdfminer_only": 0, "quote_neither": 0, "text_layer_differs": [],
                                     "findings": {}, "coverage_gaps": [], "not_applicable": 0}
    for bf in sorted((run / "batches").glob("batch_*.json")):
        batch = json.loads(bf.read_text())
        af = run / "answers" / bf.name
        answers = {a["page"]: a for a in json.loads(af.read_text())["answers"]} if af.exists() else {}
        by_page = {}
        for p in batch["pages"]:
            a = answers.get(p["id"])
            if a is None:
                failed.append({"page": p["id"], "reason": "no answer"})
                continue
            by_page[p["page"]] = a
        for p in batch["pages"]:
            a = by_page.get(p["page"])
            if a is None:
                continue
            report["pages"] += 1
            report["not_applicable"] += len(a["not_applicable"])
            for k, it in enumerate(a["items"], start=1):
                found, in_layer, in_miner = check_item(it, p["source"], p["page"])
                key = ("quote_both" if in_layer and in_miner else "quote_layer_only" if in_layer
                       else "quote_pdfminer_only" if in_miner else "quote_neither")
                report[key] += 1
                rec = {"id": f"{p['id']}#{k}", "source": p["source"], "page": p["page"], **it,
                       "image_sha256": p["image_sha256"], "findings": found, "in_pdftotext": in_layer,
                       "in_pdfminer": in_miner}
                items.append(rec)
                if not (in_layer and in_miner) or it["text_layer_differs"]:
                    report["text_layer_differs"].append({"id": rec["id"], "quote": it["quote"][:200],
                                                         "drafter_note": it["text_layer_differs"],
                                                         "in_pdftotext": in_layer, "in_pdfminer": in_miner})
                for check, _ in found:
                    report["findings"][check] = report["findings"].get(check, 0) + 1
            before = by_page.get(p["page"] - 1, {"items": []})["items"]
            before = [i for i in before if i["runs_over"]]
            for g in coverage(p["source"], p["page"], a["items"], before, a["not_applicable"]):
                report["coverage_gaps"].append({"page": p["id"], "sentence": g})
    report["items"] = len(items)
    report["failed"] = failed
    with open(run / "items.jsonl", "w", encoding="utf-8") as f:
        for i in items:
            f.write(json.dumps(i, ensure_ascii=False) + "\n")
    (run / "report.json").write_text(json.dumps(report, indent=1, ensure_ascii=False))
    print(json.dumps({k: (len(v) if isinstance(v, list) else v) for k, v in report.items()}, indent=1))
    return report


def prepare_verify(run, sources=None):
    """Verifier A and B batches, one per document (so a verifier opens at most that document's page images): each
    item with its page image path and text layer (blind: no drafter notes, no check results). A and B never share
    a batch. sources: only these documents (a sample)."""
    run = Path(run)
    items = [json.loads(ln) for ln in (run / "items.jsonl").read_text().splitlines() if ln.strip()]
    items = [i for i in items if not sources or i["source"] in sources]
    pages = {p["id"]: p for p in json.loads((run / "pages.json").read_text())["pages"]}
    vdir = run / "verify"
    (vdir / "batches").mkdir(parents=True, exist_ok=True)
    (vdir / "answers").mkdir(exist_ok=True)
    n = 0
    for role in ("a", "b"):
        instructions = (PROMPTS / f"verify_{role}.md").read_text()
        for source in sorted({i["source"] for i in items}):
            group = [i for i in items if i["source"] == source]
            n += 1
            chunk = [{"id": it["id"], "image": pages[f"{it['source']}:{it['page']}"]["image"],
                      "text_layer": layer_text(it["source"], it["page"]),
                      "next_page_text": layer_text(it["source"], it["page"] + 1)[:3000] if it["runs_over"] else "",
                      "item": {k: it[k] for k in ("statement", "quote", "clause_number", "strength", "plant_types",
                                                  "condition", "runs_over")},
                      "plant_scope": pages[f"{it['source']}:{it['page']}"]["plant_scope"]}
                     for it in group]
            (vdir / "batches" / f"batch_{n:03d}_{role}.json").write_text(json.dumps(
                {"role": role, "instructions": instructions, "schema": VERIFY_SCHEMA, "items": chunk},
                indent=1, ensure_ascii=False))
    print(vdir, n, "batches")


def ingest_verify(run):
    run = Path(run)
    verdicts = {"a": {}, "b": {}}
    for af in sorted((run / "verify" / "answers").glob("batch_*.json")):
        role = af.stem.rsplit("_", 1)[1]
        for a in json.loads(af.read_text())["answers"]:
            verdicts[role][a["id"]] = a
    items = [json.loads(ln) for ln in (run / "items.jsonl").read_text().splitlines() if ln.strip()]
    rep = {"items": len(items), "both_correct": 0, "both_incorrect": 0, "disagree": 0, "unanswered": 0,
           "cases": []}
    for it in items:
        a, b = verdicts["a"].get(it["id"]), verdicts["b"].get(it["id"])
        if not a or not b:
            rep["unanswered"] += 1
            continue
        if a["verdict"] == b["verdict"] == "correct":
            rep["both_correct"] += 1
        else:
            rep["both_incorrect" if a["verdict"] == b["verdict"] else "disagree"] += 1
            rep["cases"].append({"id": it["id"], "a": a["verdict"], "a_reason": a["reason"], "b": b["verdict"],
                                 "b_reason": b["reason"]})
    (run / "verify-report.json").write_text(json.dumps(rep, indent=1, ensure_ascii=False))
    print(json.dumps({k: v for k, v in rep.items() if k != "cases"}, indent=1))
    return rep


def main():
    cmd, args = sys.argv[1], sys.argv[2:]
    if cmd == "prepare-draft":
        targets = [(a.rsplit(":", 1)[0], int(a.rsplit(":", 1)[1])) for a in args] or \
                  [(s, p) for s, ps in TRIAL.items() for p in ps]
        prepare_draft(targets)
    elif cmd == "ingest-draft":
        ingest_draft(args[0])
    elif cmd == "prepare-verify":
        prepare_verify(args[0], args[1:] or None)
    elif cmd == "ingest-verify":
        ingest_verify(args[0])
    else:
        raise SystemExit(__doc__)


if __name__ == "__main__":
    main()
