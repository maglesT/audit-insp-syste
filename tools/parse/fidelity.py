"""Source fidelity (owner priority 0a, D39): every parsed clause of every PDF, checked against a second engine.

  python3 tools/parse/fidelity.py run [FILE ...]    # re-extract, compare, write library/fidelity-report.{json,md}
  python3 tools/parse/fidelity.py check             # every flag in the committed report is explained (CI)

The parser reads PDFs with poppler (`pdftotext -layout`). This check reads them again with pdfminer.six (through
pdfplumber's page text), which is a separate code base, and compares each clause with the second engine's words on
the clause's pages (one page of margin either side, since a clause's page numbers come from the first engine).
Both texts are normalised the same way first: Unicode NFKC (ligatures, full-width letters), soft hyphens dropped,
a word broken at a line end joined ("manufac- turing" -> "manufacturing"; letters on both sides, any hyphen), letters case-folded, punctuation and
spacing ignored, and the letters of ligatures (fi, fl, ff, ffi, ffl) left out, since pdfminer drops some ligature
glyphs. A clause word of three or more characters that the second engine split ("PD50" as "PD 50") counts as
found when it is not a whole word on the pages but appears in their words run together. A clause's match share is the share of its words found, in order, in the second engine's words
(difflib longest matching blocks). Table rows (kind table_row) are compared as a bag of words, since the two
engines may read table cells in different orders.

Flags: a clause under CLAUSE_MIN, and a source whose clauses' median is under SOURCE_MIN. Each flagged clause is
classified by its missing words (classify): minor tokens, reading order, elsewhere in the document, or read by a
third reading (poppler's raw order). A flag whose missing words all fall under those rules is explained by rule;
an "unconfirmed" word, which no reading of the PDF has, must be fixed in the parser or explained in
library/fidelity-explanations.csv (source, ref or "*", reason), and so must a source median under SOURCE_MIN.
`check` fails on anything unexplained, so CI holds the committed report to that rule without re-reading the PDFs. Contents
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
    text = re.sub(r"([^\W\d_])[-\u2010\u2011]\s+([^\W\d_])", r"\1\2", text)   # letters only: "3,5,8- pyrene" stays
    return [LIGATURES.sub("", w) or w for w in re.findall(r"\w+", text.casefold())]


def matched(clause_words, page_words, bag=False):
    """(share, missing words): the share of the clause's words found in the page words, in order or as a bag of
    words, and the words not found. A clause word of three or more characters that the second engine split ("PD50"
    read as "PD 50", subscripts and superscripts) counts as found when it is not a whole word there but appears in
    the page's words run together (a word that is there but out of order still counts as missing)."""
    if not clause_words:
        return 1.0, []
    if bag:
        have = Counter(page_words)
        missing = [w for w, n in Counter(clause_words).items() for _ in range(max(n - have[w], 0))]
    else:
        sm = SequenceMatcher(None, clause_words, page_words, autojunk=False)
        got = set()
        for b in sm.get_matching_blocks():
            got.update(range(b.a, b.a + b.size))
        missing = [w for n, w in enumerate(clause_words) if n not in got]
    whole, joined = set(page_words), "".join(page_words)
    missing = [w for w in missing if not (len(w) > 2 and w not in whole and w in joined)]
    return (len(clause_words) - len(missing)) / len(clause_words), missing


def share(clause_words, page_words, bag=False):
    return matched(clause_words, page_words, bag)[0]


def classify(missing, page_words, doc_words, raw_words):
    """Why a flagged clause's missing words are missing, or which are not explained by rule:
    (category, unconfirmed words). Categories, checked in this order for every missing word:
      minor      one or two letters (superscripts such as "th", units, list letters); never a number: a number
                 must be on the clause's own pages in the second reading, so a changed limit ("25" stored,
                 "52" printed) is flagged even when "25" appears elsewhere in the document
      order      on the clause's pages, in another order (columns, table cells, headers read differently)
      elsewhere  elsewhere in the second engine's text of the document (a table row repeating a spanned cell's
                 label, a clause whose page numbers are off)
      engine     not in the second engine's text but in poppler's raw-order text (a pdfminer gap)
    A word in none of these is unconfirmed: no independent reading of the PDF has it, so the stored text may be
    wrong and the flag needs a fix or an explanation in library/fidelity-explanations.csv."""
    page, doc = set(page_words), set(doc_words)
    doc_joined, raw, raw_joined = "".join(doc_words), set(raw_words), "".join(raw_words)
    seen, unconfirmed = set(), []
    for w in missing:
        if len(w) <= 2 and not w.isdigit():
            seen.add("minor")
        elif w.isdigit() and w not in page:
            unconfirmed.append(w)                   # a number counts only where the clause is printed
        elif w in page:
            seen.add("order")
        elif w in doc or w in doc_joined:
            seen.add("elsewhere")
        elif w in raw or w in raw_joined:
            seen.add("engine")
        else:
            unconfirmed.append(w)
    order = ("unconfirmed", "engine", "elsewhere", "order", "minor")
    category = next(c for c in order if c in seen or (c == "unconfirmed" and unconfirmed))
    return category, unconfirmed


def second_engine_pages(path):
    """Words per page from pdfminer.six (via pdfplumber)."""
    import pdfplumber
    with pdfplumber.open(path) as pdf:
        return [words(page.extract_text() or "") for page in pdf.pages]


def compare(clauses, pages, raw_words=()):
    """[(ref, kind, share, words, category, unconfirmed)] for every clause but contents entries; category and
    unconfirmed (classify) are filled in for flagged clauses only."""
    doc_words = [w for p in pages for w in p]
    out = []
    for c in clauses:
        if c["kind"] == "toc":
            continue
        cw = words(c["text"])
        if not cw:
            continue
        first, last = max(c["page_start"] - 1 - MARGIN, 0), min(c["page_end"] + MARGIN, len(pages))
        pw = [w for p in pages[first:last] for w in p]
        sh, missing = matched(cw, pw, bag=c["kind"] == "table_row")
        cat, unconfirmed = classify(missing, pw, doc_words, raw_words) if sh < CLAUSE_MIN else ("", [])
        out.append((c["ref"], c["kind"], round(sh, 4), len(cw), cat, unconfirmed))
    return out


def source_summary(rows):
    shares = [r[2] for r in rows]
    return {"clauses": len(rows), "median": round(statistics.median(shares), 4) if shares else 1.0,
            "min": min(shares) if shares else 1.0,
            "flagged": [{"ref": r, "kind": k, "share": s, "words": n, "category": cat, "unconfirmed": u}
                        for r, k, s, n, cat, u in rows if s < CLAUSE_MIN]}


def raw_words(path):
    """Words of poppler's raw-order text (`pdftotext -raw`), the third reading used by classify."""
    import subprocess
    return words(subprocess.run(["pdftotext", "-raw", str(path), "-"], capture_output=True, text=True,
                                check=True).stdout)


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
        report[f] = source_summary(compare(clauses, second_engine_pages(OFFICIAL / f), raw_words(OFFICIAL / f)))
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
    """Flags that neither a rule (classify: every missing word is minor, out of order, elsewhere in the document
    or read by poppler) nor an explanation covers: (source, ref or "*", detail). A source median under the
    threshold always needs an explanation."""
    out = []
    for f, s in doc["sources"].items():
        if s["median"] < doc["source_min"] and (f, "*") not in why:
            out.append((f, "*", f"median {s['median']:.4f} under {doc['source_min']}"))
        for c in s["flagged"]:
            if c.get("category", "unconfirmed") != "unconfirmed" or (f, c["ref"]) in why or (f, "*") in why:
                continue
            out.append((f, c["ref"], f"{c['kind']} share {c['share']:.4f} ({c['words']} words); no reading has: "
                                     f"{' '.join(c.get('unconfirmed', []))}"))
    return out


def markdown(doc):
    srcs = doc["sources"]
    total = sum(s["clauses"] for s in srcs.values())
    flags = [(f, c) for f, s in srcs.items() for c in s["flagged"]]
    cats = Counter(c.get("category", "") for _, c in flags)
    why = explanations()
    lines = ["# Source fidelity report", "",
             f"Built by `python3 tools/parse/fidelity.py run` (D39): every parsed clause of every PDF source compared "
             f"word by word with a second engine ({doc['engine']}). Flags: a clause under {doc['clause_min']:.0%} "
             f"of its words matched, a source median under {doc['source_min']:.1%}.", "",
             f"Sources: {len(srcs)}; clauses: {total}; flagged clauses: {len(flags)} "
             f"({', '.join(f'{k} {v}' for k, v in sorted(cats.items()))}); sources under the median threshold: "
             f"{sum(s['median'] < doc['source_min'] for s in srcs.values())}.", "",
             "Categories (`classify`): minor = only numbers or one- or two-character tokens differ (footnote marks, "
             "superscripts); order = the words are on the clause's pages in another order; elsewhere = the words are "
             "elsewhere in the document (a table row repeating a spanned cell's label); engine = pdfminer misses them "
             "but poppler's raw reading has them; unconfirmed = no reading of the PDF has a word, so the flag is "
             "fixed or explained in `library/fidelity-explanations.csv`.", "",
             "## Unconfirmed words and low medians", ""]
    for f, s in srcs.items():
        if s["median"] < doc["source_min"]:
            lines.append(f"- {f}: median {s['median']:.4f}. {why.get((f, '*'), 'NOT EXPLAINED')}")
    for f, c in flags:
        if c.get("category") == "unconfirmed":
            lines.append(f"- {f} {c['ref']} ({c['kind']}, {c['share']:.4f}): {' '.join(c['unconfirmed'])}. "
                         f"{why.get((f, c['ref']), why.get((f, '*'), 'NOT EXPLAINED'))}")
    lines += ["", "| Source | Clauses | Median | Lowest | Flagged |", "|---|---|---|---|---|"]
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
