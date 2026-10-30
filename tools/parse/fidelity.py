"""Source fidelity (owner priority 0a, D38): every parsed clause of every PDF, checked against a second engine.

  python3 tools/parse/fidelity.py run [FILE ...]    # re-extract, compare, write library/fidelity-report.{json,md}
  python3 tools/parse/fidelity.py check             # every flag in the committed report is explained (CI)

The parser reads PDFs with poppler (`pdftotext -layout`). This check reads them again with pdfminer.six (through
pdfplumber's page text), which is a separate code base, and compares each clause with the second engine's words on
the clause's pages (one page of margin either side, since a clause's page numbers come from the first engine).
Both texts are normalised the same way first: Unicode NFKC (ligatures, full-width letters), soft hyphens dropped,
a word broken at a line end joined ("manufac- turing" -> "manufacturing"), letters case-folded, punctuation and
spacing ignored, and the letters of ligatures (fi, fl, ff, ffi, ffl) left out, since pdfminer drops some ligature
glyphs. A clause word of three or more characters that the second engine split ("PD50" as "PD 50") counts as
found when it is not a whole word on the pages but appears in their words run together. A clause's match share is the share of its words found, in order, in the second engine's words
(difflib longest matching blocks). Table rows (kind table_row) are compared as a bag of words, since the two
engines may read table cells in different orders.

Flags: a clause under CLAUSE_MIN, and a source whose clauses' median is under SOURCE_MIN. Every flag is either
fixed in the parser or explained in library/fidelity-explanations.csv (source, ref or "*", reason); `check` fails
on a flag with no explanation, so CI holds the committed report to that rule without re-reading 140 PDFs. Contents
entries (kind toc) are left out. HTML and XML sources are parsed from structured text, not PDF, and are not covered.
"""
import argparse
import csv
import json
import re
import statistics
import sys
import unicodedata
from collections import Counter
from difflib import SequenceMatcher
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from common import CLAUSES, OFFICIAL  # noqa: E402

ROOT = HERE.parents[1]
REPORT = ROOT / "library" / "fidelity-report.json"
REPORT_MD = ROOT / "library" / "fidelity-report.md"
EXPLANATIONS = ROOT / "library" / "fidelity-explanations.csv"
CLAUSE_MIN = 0.99
SOURCE_MIN = 0.995
MARGIN = 1


# pdfminer drops some ligature glyphs ("qualiﬁcation" -> "qualication"): the letters a ligature stands for are
# left out of every word on both sides before comparing
LIGATURES = re.compile(r"ffi|ffl|ff|fi|fl")


def words(text):
    """The comparable words of a text (see the module docstring)."""
    text = unicodedata.normalize("NFKC", text).replace("\u00ad", "")
    text = re.sub(r"(\w)-\s+(\w)", r"\1\2", text)
    return [LIGATURES.sub("", w) or w for w in re.findall(r"\w+", text.casefold())]


def share(clause_words, page_words, bag=False):
    """Share of the clause's words found in the page words: in order, or as a bag of words. A clause word of three
    or more characters that the second engine split ("PD50" read as "PD 50", subscripts and superscripts) counts as
    found when it is not a whole word there but appears in the page's words run together (a word that is there
    but out of order still counts as missing)."""
    if not clause_words:
        return 1.0
    if bag:
        have = Counter(page_words)
        found = sum(min(n, have[w]) for w, n in Counter(clause_words).items())
        missing = [w for w, n in Counter(clause_words).items() for _ in range(max(n - have[w], 0))]
    else:
        sm = SequenceMatcher(None, clause_words, page_words, autojunk=False)
        got = set()
        for b in sm.get_matching_blocks():
            got.update(range(b.a, b.a + b.size))
        found = len(got)
        missing = [w for n, w in enumerate(clause_words) if n not in got]
    whole, joined = set(page_words), "".join(page_words)
    found += sum(1 for w in missing if len(w) > 2 and w not in whole and w in joined)
    return found / len(clause_words)


def second_engine_pages(path):
    """Words per page from pdfminer.six (via pdfplumber)."""
    import pdfplumber
    with pdfplumber.open(path) as pdf:
        return [words(page.extract_text() or "") for page in pdf.pages]


def compare(clauses, pages):
    """[(ref, kind, share, words)] for every clause but contents entries."""
    out = []
    for c in clauses:
        if c["kind"] == "toc":
            continue
        cw = words(c["text"])
        if not cw:
            continue
        first, last = max(c["page_start"] - 1 - MARGIN, 0), min(c["page_end"] + MARGIN, len(pages))
        pw = [w for p in pages[first:last] for w in p]
        out.append((c["ref"], c["kind"], round(share(cw, pw, bag=c["kind"] == "table_row"), 4), len(cw)))
    return out


def source_summary(rows):
    shares = [s for _, _, s, _ in rows]
    return {"clauses": len(rows), "median": round(statistics.median(shares), 4) if shares else 1.0,
            "min": min(shares) if shares else 1.0,
            "flagged": [{"ref": r, "kind": k, "share": s, "words": n} for r, k, s, n in rows if s < CLAUSE_MIN]}


def pdf_sources():
    """The PDF sources that have parsed clauses."""
    return sorted(p.stem + ".pdf" for p in CLAUSES.glob("*.jsonl") if (OFFICIAL / (p.stem + ".pdf")).exists())


def run(files=None):
    files = files or pdf_sources()
    report = json.loads(REPORT.read_text(encoding="utf-8")) if REPORT.exists() and files != pdf_sources() else {}
    report = report.get("sources", {})
    for f in files:
        clauses = [json.loads(l) for l in (CLAUSES / (Path(f).stem + ".jsonl")).read_text(encoding="utf-8")
                   .splitlines() if l.strip()]
        report[f] = source_summary(compare(clauses, second_engine_pages(OFFICIAL / f)))
        print(f"{f}: median {report[f]['median']:.4f}, {len(report[f]['flagged'])} flagged", flush=True)
    doc = {"engine": "pdfminer.six via pdfplumber", "clause_min": CLAUSE_MIN, "source_min": SOURCE_MIN,
           "sources": dict(sorted(report.items()))}
    REPORT.write_text(json.dumps(doc, indent=1) + "\n", encoding="utf-8")
    REPORT_MD.write_text(markdown(doc), encoding="utf-8")
    return doc


def explanations(path=EXPLANATIONS):
    if not Path(path).exists():
        return {}
    with open(path, encoding="utf-8") as f:
        return {(r["source"], r["ref"]): r["reason"] for r in csv.DictReader(f)}


def unexplained(doc, why):
    """Flags with no explanation: (source, ref or "*", detail)."""
    out = []
    for f, s in doc["sources"].items():
        if s["median"] < doc["source_min"] and (f, "*") not in why:
            out.append((f, "*", f"median {s['median']:.4f} under {doc['source_min']}"))
        for c in s["flagged"]:
            if (f, c["ref"]) not in why and (f, "*") not in why:
                out.append((f, c["ref"], f"{c['kind']} share {c['share']:.4f} ({c['words']} words)"))
    return out


def markdown(doc):
    srcs = doc["sources"]
    total = sum(s["clauses"] for s in srcs.values())
    flagged = sum(len(s["flagged"]) for s in srcs.values())
    lines = ["# Source fidelity report", "",
             f"Built by `python3 tools/parse/fidelity.py run` (D38): every parsed clause of every PDF source compared "
             f"word by word with a second engine ({doc['engine']}). Flags: a clause under {doc['clause_min']:.0%} "
             f"of its words matched, a source median under {doc['source_min']:.1%}. Explanations: "
             "`library/fidelity-explanations.csv`.", "",
             f"Sources: {len(srcs)}; clauses: {total}; flagged clauses: {flagged}; sources under the median "
             f"threshold: {sum(s['median'] < doc['source_min'] for s in srcs.values())}.", "",
             "| Source | Clauses | Median | Lowest | Flagged |", "|---|---|---|---|---|"]
    for f, s in srcs.items():
        lines.append(f"| {f} | {s['clauses']} | {s['median']:.4f} | {s['min']:.4f} | {len(s['flagged'])} |")
    return "\n".join(lines) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("command", choices=["run", "check"])
    ap.add_argument("files", nargs="*")
    a = ap.parse_args()
    if a.command == "run":
        run(a.files or None)
        return
    doc = json.loads(REPORT.read_text(encoding="utf-8"))
    missing = unexplained(doc, explanations())
    for f, ref, detail in missing:
        print(f"unexplained: {f} {ref}: {detail}")
    print(f"fidelity: {sum(s['clauses'] for s in doc['sources'].values())} clauses in {len(doc['sources'])} sources, "
          f"{len(missing)} unexplained flags")
    sys.exit(1 if missing else 0)


if __name__ == "__main__":
    main()
