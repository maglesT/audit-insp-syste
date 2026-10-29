"""Independent cross-check that no obligation text was lost by the parser.

The PDF is read a second time with a different extraction mode (`pdftotext -raw`, reading order instead of
layout). Every obligation sentence found that way must also appear, word for word after normalisation, somewhere
in the parsed clauses. A miss means the parser dropped or mangled requirement text; it is reported, never ignored.

Tables: raw mode reads a table line by line across its columns, so a sentence from one cell comes out mixed with
words from the cells beside it. On a page that the parser read as a table (it has table_row clauses), a sentence
therefore also counts as found when every one of its words, with repeats, is in one table row on that page (or the
page before or after, for rows that run over a page break). That proves the text is in that row; the reading order
inside a table cannot be checked this way.
"""
import re
import subprocess
from collections import Counter

from common import edge_lines, line_key, repeated_lines
from obligations import sentences, strength

WORD = re.compile(r"[a-z0-9]+")
RAW_EDGE = 10


def norm_words(text):
    """Lower-case words without bare numbers (raw mode injects page and line numbers mid-sentence)."""
    return [w for w in WORD.findall(text.lower()) if not w.isdigit()]


def raw_pages(path):
    out = subprocess.run(["pdftotext", "-raw", str(path), "-"], capture_output=True, text=True, check=True).stdout
    return out.split("\f")


def without_running_lines(pages):
    """Raw pages without running headers and footers: the parser's rule (lines repeated at the page edges), but
    looking 10 lines deep, because raw mode prints a rotated side header one word per line ("WHO / Technical /
    Report / Series")."""
    noise = repeated_lines(pages, n=RAW_EDGE)
    out = []
    for page in pages:
        edges = {ln.strip() for ln in edge_lines(page, RAW_EDGE)}
        out.append("\n".join(ln for ln in page.splitlines()
                             if not (ln.strip() in edges and line_key(ln) in noise)))
    return out


def located_sentences(pages):
    """(page number, sentence) for the whole document, split across page breaks as one text."""
    text, starts = "", []
    for pno, page in enumerate(without_running_lines(pages), start=1):
        page = re.sub(r"\s+", " ", page).strip()
        if page:
            starts.append((len(text) + (1 if text else 0), pno))
            text = f"{text} {page}" if text else page
    out, pos = [], 0
    for s in sentences(text):
        at = text.find(s[:40], pos)
        pos = at if at >= 0 else pos
        pno = max((p for st, p in starts if st <= pos), default=1)
        out.append((pno, s))
    return out


def missed_obligations(path, clauses, window=6):
    """Obligation sentences from the raw extraction that the parsed clauses do not contain.

    A sentence is cut into overlapping 6-word windows (step 2); it counts as found when at least half of its windows occur
    in the clause text. That tolerates running headers that raw mode inserts mid-sentence, but not lost text.
    """
    if not str(path).endswith(".pdf"):
        return []
    joined = " ".join(" ".join(norm_words(c.text)) for c in clauses)
    haystack, squeezed = " " + joined + " ", joined.replace(" ", "")   # squeezed: raw mode sometimes drops spaces
    rows = [(c.page_start, c.page_end, Counter(norm_words(c.text))) for c in clauses if c.kind == "table_row"]
    table_pages = {p for a, b, _ in rows for p in range(a, b + 1)}

    def in_one_row(pno, bag):
        return any(a - 1 <= pno <= b + 1 and not bag - row for a, b, row in rows)

    missed = []
    for pno, s in located_sentences(raw_pages(path)):
        if not strength(s):
            continue
        words = norm_words(s)
        wins = [words[i:i + window] for i in range(0, len(words) - window + 1, 2)]
        if not wins:
            continue
        found = sum(1 for w in wins if " " + " ".join(w) + " " in haystack or "".join(w) in squeezed)
        if found >= len(wins) / 2:
            continue
        if pno in table_pages and in_one_row(pno, Counter(words)):
            continue
        missed.append(s[:200])
    return missed
