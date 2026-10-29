"""Shared clause model and helpers for the source parsers (deterministic, no AI).

A clause is the smallest citable unit of a source. Every body line of a source ends up in exactly one clause:
numbered clauses get their own reference ("9.3", "211.68(b)"), and text the parser cannot attach to a number
goes into "_unnumbered:<n>" segments, so nothing is silently dropped.
"""
import hashlib
import json
import re
import subprocess
from dataclasses import asdict, dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OFFICIAL = ROOT / "sources" / "official"
CLAUSES = ROOT / "library" / "clauses"

DEVANAGARI = re.compile(r"[ऀ-ॿ]")


@dataclass
class Clause:
    source: str            # file name in sources/official
    ref: str               # e.g. "Part I 10.5", "211.68(b)", "Principle", "_unnumbered:3"
    section: str           # section prefix that resets numbering ("Annex 1", "Part II"); "" if none
    number: str            # the bare number ("10.5"); "" for headings and unnumbered segments
    heading: str           # first line, trimmed (for humans and drafting context)
    text: str              # whitespace-normalised text of the whole clause
    page_start: int
    page_end: int
    kind: str = "clause"   # clause | principle | unnumbered | toc
    notes: list = field(default_factory=list)

    def to_json(self):
        d = asdict(self)
        d["sha256"] = hashlib.sha256(self.text.encode("utf-8")).hexdigest()
        return d


def normalise(text):
    return re.sub(r"\s+", " ", text).strip()


def pdf_pages(path):
    """Layout-preserving text, one string per page."""
    out = subprocess.run(["pdftotext", "-layout", str(path), "-"], capture_output=True, text=True, check=True).stdout
    pages = out.split("\f")
    if pages and not pages[-1].strip():
        pages = pages[:-1]
    return pages


def english_page(page):
    letters = [c for c in page if c.isalpha()]
    if not letters:
        return True
    return sum(1 for c in letters if DEVANAGARI.match(c)) / len(letters) < 0.05


def repeated_lines(pages, min_share=0.3, min_pages=3):
    """Lines that recur on many pages (running headers and footers), compared with digits masked."""
    counts = {}
    for page in pages:
        seen = set()
        for line in page.splitlines():
            key = re.sub(r"\d+", "#", line.strip())
            if key and key not in seen:
                seen.add(key)
                counts[key] = counts.get(key, 0) + 1
    limit = max(min_pages, int(len(pages) * min_share))
    return {k for k, n in counts.items() if n >= limit}


def write_clauses(source, clauses):
    CLAUSES.mkdir(parents=True, exist_ok=True)
    path = CLAUSES / (Path(source).stem + ".jsonl")
    with open(path, "w", encoding="utf-8") as f:
        for c in clauses:
            f.write(json.dumps(c.to_json(), ensure_ascii=False) + "\n")
    return path


def report(source, clauses, body_chars):
    """Completeness figures for one source."""
    assigned = sum(len(c.text.replace(" ", "")) for c in clauses)
    numbered = sum(len(c.text.replace(" ", "")) for c in clauses if c.kind in ("clause", "principle"))
    refs = [c.ref for c in clauses if c.kind in ("clause", "principle")]
    dups = sorted({r for r in refs if refs.count(r) > 1})
    return {
        "source": source,
        "clauses": len(refs),
        "unnumbered_segments": sum(1 for c in clauses if c.kind == "unnumbered"),
        "toc_segments": sum(1 for c in clauses if c.kind == "toc"),
        "body_chars": body_chars,
        "assigned_share": round(assigned / body_chars, 4) if body_chars else 1.0,
        "numbered_share": round(numbered / body_chars, 4) if body_chars else 1.0,
        "duplicate_refs": dups,
        "gaps": [n for c in clauses for n in c.notes if n.startswith("gap")],
    }
