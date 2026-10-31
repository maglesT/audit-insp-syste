"""Source fidelity (owner priority 0a, D39): every parsed clause of every PDF, checked against a second engine.

  python3 tools/parse/fidelity.py run [FILE ...]    # re-read, compare, write library/fidelity-report.{json,md}
  python3 tools/parse/fidelity.py check             # the committed report is current and fully explained (CI)

The parser reads PDFs with poppler (`pdftotext -layout`). This check reads them again with pdfminer.six (through
pdfplumber's words), a separate code base, and compares each stored clause with the second reading of its pages,
in both directions: the clause's tokens are aligned to the page text (one page of margin either side), the
stretch of page text from the first to the last matching token is taken as the clause's place in the PDF, and
every difference in that stretch is a discrepancy, whether the stored clause has a token the PDF lacks there or
the PDF has a token the stored clause lacks (dropped text, a dropped "not"). There is no share threshold: one
wrong token in a long clause is flagged.

Tokens: words, numbers with their decimal point ("0.5"), and the signs < > ≤ ≥ ± % − (a minus sign before a
number); case is folded and Unicode normalised (NFKC, soft hyphens). Before comparing, the second reading drops
what the parser drops too: running headers and footers (lines repeated at page edges), page numbers at page
edges, margin line numbers of line-numbered documents (read first or last on the line), Devanagari text of bilingual gazettes, and "(cid:n)" glyphs. A difference is tolerated
only in these narrow cases, each of which leaves the words of the regulation unchanged:
  - ligature letters dropped by pdfminer ("qualication" for "qualification"), or a word split or joined
    differently ("cross- contamination" / "crosscontamination", "multi- 73 disciplinary" with a margin line
    number inside the split word): the same letters in the same order;
  - footnote marks: small-font tokens in the PDF that do not follow a number (a following small number may be an
    exponent and is not tolerated), or a one- to three-digit number in the clause that the page prints small
    (a number starting a line is not enough: it may be a list number);
  - text set vertically, read one character at a time (runs of three or more single characters), and headings in
    small capitals read as split words ("s cope of g uideline") at a clause's start or end;
  - a line of five or more words printed on a third of the pages (a running title in the margin, or a reference
    such as "PIC/S GMP Guide Part I" repeated in an aide-memoire): kept in the reading, but a clause may lack it;
  - a footnote number or sign that only moved within the clause.
Table rows (kinds table_row, table_header) are compared as a bag of tokens against the row's own stretch of the
page (the tokens printed within the row's band of heights), since the two engines read cells in different orders;
running header lines are kept for them, as a table's header row repeated at the top of each page is one. Coverage, the other direction at document level:
every run of three or more tokens of the second reading that no clause accounts for (text missing from every
stored clause: a dropped paragraph, a clause end cut off) is flagged as "uncovered" with its page.

A flagged clause is fixed in the parser or explained in library/fidelity-explanations.csv: source, ref (or "*"),
discrepancy (the exact discrepancy text, or with ref "*" a regular expression every listed discrepancy must match
in full, for one systematic layout effect of a source), reason. An explanation lapses when the discrepancy
changes. The report records the sha256 of this file, of each PDF and of each clause file; `check` fails when the
code changed since the report was built, a PDF differs from sources/inventory.csv, a pilot must/should PDF is
missing from the report, or a discrepancy is unexplained, so CI holds the committed report to these rules without
re-reading the PDFs. HTML and XML sources are not PDF and are not covered; a clause boundary error is found only
when it changes a clause's text (structure checks cover the rest).
"""
import argparse
import csv
import hashlib
import json
import re
import sys
import unicodedata
from collections import Counter
from difflib import SequenceMatcher
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import common  # noqa: E402
from common import CLAUSES, OFFICIAL  # noqa: E402

ROOT = HERE.parents[1]
REPORT = ROOT / "library" / "fidelity-report.json"
REPORT_MD = ROOT / "library" / "fidelity-report.md"
EXPLANATIONS = ROOT / "library" / "fidelity-explanations.csv"
MARGIN = 1
TOKEN = re.compile(r"\d+(?:[.,]\d+)*|[^\W\d_]+|[<>≤≥±%−]")
LIGATURES = re.compile(r"ffi|ffl|ff|fi|fl")
INDIC = re.compile(r"[ऀ-෿]")
PAGE_NUMBER = re.compile(r"\s*(page\s*)?(\d{1,4}|[ivxl]{1,6})(\s*(of|/)\s*\d{1,4})?\s*", re.I)
TABLE_KINDS = ("table_row", "table_header")


def code_sha256():
    return hashlib.sha256(Path(__file__).read_bytes()).hexdigest()


def tokens(text):
    """The comparable tokens of a text (see the module docstring)."""
    text = unicodedata.normalize("NFKC", text).replace("­", "")
    text = re.sub(r"\(cid:\d+\)", " ", text)
    text = re.sub(r"(?:(?<=\s)|^)[-−](?=\d)", "−", text)
    return [t for t in TOKEN.findall(text.casefold()) if not INDIC.search(t)]


def unlig(text):
    return LIGATURES.sub("", text)


def same(a, b):
    """Two tokens are the same, or one is the other with its ligature letters dropped."""
    return a == b or bool(LIGATURES.search(a) and unlig(a) == b) or bool(LIGATURES.search(b) and unlig(b) == a)


def page_lines(page):
    """[[(word, small font, height on the page)]] per line of a pdfplumber page, words in reading order, lines by baseline (landscape
    pages, whose text is set turned by 90 degrees, are read along their own lines)."""
    turned = [c for c in page.chars if not c["upright"]]
    if len(turned) > len(page.chars) / 2:                  # a landscape page: lines run up (or down) the page
        up = sum(c["matrix"][1] > 0 for c in turned) > len(turned) / 2
        words = page.extract_words(keep_blank_chars=False, line_dir_rotated="ltr" if up else "rtl",
                                   char_dir_rotated="btt" if up else "ttb")
        for w in words:                                     # turned glyphs report odd sizes: use the line height
            w["size"] = w["x1"] - w["x0"] if not w["upright"] else w["bottom"] - w["top"]
        start, end = "x0", "x1"
    else:
        words = page.extract_words(extra_attrs=["size"], keep_blank_chars=False, use_text_flow=True)
        start, end = "top", "bottom"
    if not words:
        return []
    sizes = sorted(w["size"] for w in words)
    body = sizes[len(sizes) // 2]
    lines, line = [], []
    for w in words:
        if line and abs(w[start] - line[-1][start]) > 2.5 and abs(w[end] - line[-1][end]) > 2.5:
            lines.append(line)
            line = []
        line.append(w)
    lines.append(line)
    return [[(cid_text(w["text"]), w["size"] < 0.8 * body, round((w[start] + w[end]) / 2, 1)) for w in ln]
            for ln in lines]


CID = re.compile(r"\(cid:(\d+)\)")
CID_EXTRA = {1: " ", 109: "fi", 116: "•", 245: "ff"}


def cid_text(text):
    """A word in a font without a Unicode map, which pdfminer reads as "(cid:n)" glyph numbers, read in the
    standard glyph order of Adobe's Pro fonts (glyph n = character n + 31; 1 is the space, 109 "fi", 116 a
    bullet, 245 "ff"), only when the word holds the space glyph 1 next to other glyphs (WHO TRS 981 Annex 2's QRM
    tables). Any other "(cid:n)" is dropped later, as before."""
    glyphs = [int(n) for n in CID.findall(text)]
    if 1 not in glyphs or len(set(glyphs)) < 2 or not all(n in CID_EXTRA or 2 <= n <= 95 for n in glyphs):
        return text
    return CID.sub(lambda m: CID_EXTRA.get(int(m.group(1))) or chr(int(m.group(1)) + 31), text)


def latin_line(line):
    """A line without Devanagari text; empty when only a gazette header's remnant would be left."""
    indic = any(INDIC.search(w[0]) for w in line)
    kept = [(INDIC.sub("", t).replace("‍", ""), *rest) for t, *rest in line if "cid:" not in t]
    kept = [w for w in kept if w[0].strip()]
    if indic and not any(re.search(r"[^\W\d_]{3}", w[0]) for w in kept):
        return []
    return kept


def read_pages(lines_per_page):
    """[(tokens, small-font token indexes, numbers that start a line, each token's height)] per page, and whether the document has
    numbered lines, from page_lines() of every page (see the module docstring for what is dropped)."""
    pages = [[ln for ln in (latin_line(ln) for ln in pl) if ln] for pl in lines_per_page]
    texts = ["\n".join(" ".join(w[0] for w in ln) for ln in pl) for pl in pages]
    placed = ["\n".join(" ".join(w[0] for w in ln) for ln in sorted(pl, key=lambda ln: ln[0][2] or 0)) for pl in pages]
    running = common.repeated_lines(texts) | common.repeated_lines(placed)   # page edges by reading order or place
    anywhere = Counter(k for t in texts for k in {common.line_key(ln) for ln in t.splitlines()} if len(k.split()) >= 5)
    anywhere = {k for k, n in anywhere.items() if n >= max(3, int(len(texts) * 0.3))} - running
    exact = common.repeated_lines(["\n".join(re.sub(r"\d", "@", ln) for ln in t.splitlines()) for t in texts])

    def header(line):
        key = common.line_key(line)
        if not re.search(r"[^\W\d_]", key):
            return False                                    # no letters: page numbers are taken at the edges
        if len(re.findall(r"[^\W\d_]{2,}", key)) < 2 and common.line_key(re.sub(r"\d", "@", line)) not in exact:
            return False                                    # "Article #": headings differ by number, not repeated
        return bool(key in running or common.SIDE_HEADER.match(key)
                    or common.SIDE_HEADER.match(common.line_key(line[::-1])))
    all_lines = [" ".join(w[0] for w in ln) for pl in pages for ln in pl]
    numbered = None
    for side, pattern in ((0, r"^(\d{1,4})\s+\S"), (-1, r"\S\s+(\d{1,4})$")):   # margin numbers read first or last
        found = [int(m.group(1)) for ln in all_lines for m in [re.search(pattern, ln)] if m]
        if (len(found) > 0.4 * max(len(all_lines), 1)
                and sum(b == a + 1 for a, b in zip(found, found[1:])) > 0.6 * len(found)):
            numbered = side
    out = []
    for pl in pages:
        toks, small, starts, height, soft, head = [], set(), set(), [], set(), set()
        ys = sorted({ln[0][2] for ln in pl if ln and ln[0][2] is not None})
        edges = set(ys[:2] + ys[-2:])
        for n, ln in enumerate(pl):
            line = " ".join(w[0] for w in ln)
            optional = common.line_key(line) in anywhere
            if len(ln) > 1 and all(re.fullmatch(r"[^\W\d_]", w[0]) for w in ln):
                continue
            running_line = header(line)
            if (n < 2 or n >= len(pl) - 2 or ln[0][2] in edges) and PAGE_NUMBER.fullmatch(line):
                continue                                    # a page number: at a page edge by reading order or place
            words = list(ln)
            if numbered is not None and words and re.fullmatch(r"\d{1,4}", words[numbered][0]):
                words.pop(numbered)
            if words and re.fullmatch(r"\d{1,3}", words[0][0]) and (
                    words[0][2] is None or not ys or words[0][2] >= ys[0] + 0.6 * (ys[-1] - ys[0])):
                starts.add(words[0][0])                     # a footnote's number: low on the page
            for t, is_small, y in words:
                for tok in tokens(t):
                    if is_small:
                        small.add(len(toks))
                    if optional:
                        soft.add(len(toks))
                    if running_line:
                        head.add(len(toks))
                    toks.append(tok)
                    height.append(y)
        out.append((toks, small, starts, height, soft, head))
    return out, numbered is not None


def second_reading(path):
    import pdfplumber
    with pdfplumber.open(path) as pdf:
        return read_pages([page_lines(p) for p in pdf.pages])


def char_runs(words):
    """Vertical text read one character at a time: runs of single-character tokens, joined both ways."""
    runs, cur = [], []
    for t in list(words) + [""]:
        if len(t) == 1:
            cur.append(t)
            continue
        if len(cur) >= 3:
            runs += ["".join(cur), "".join(reversed(cur))]
        cur = []
    return runs


def joins(words):
    """Every token and run of two or three adjacent tokens, joined, with and without ligature letters."""
    out = {"".join(words[k:k + n]) for n in (1, 2, 3) for k in range(len(words) - n + 1)}
    return out | {unlig(x) for x in out}


CHAIN_SLACK = 20


def chain(blocks, free=None):
    """The clause's place on the page: the run of consecutive matching blocks with the best score (tokens matched
    minus half the page tokens skipped beyond the clause's own gap and CHAIN_SLACK), so that a few tokens matched far away (a
    number, a common word) do not stretch the clause over unrelated text; clause tokens outside the run are then
    compared as missing. free (a list of window flags) marks tokens that do not count as skipped: optional
    lines, footnote marks, vertical text."""
    blocks = [b for b in blocks if b.size]
    skipped = [0]
    for f in free or []:
        skipped.append(skipped[-1] + (not f))
    best, best_score, start, score = (0, 0), -1.0, 0, 0.0
    for k, b in enumerate(blocks):
        go_on = -1.0
        if k:
            p = blocks[k - 1]
            gap = skipped[b.b] - skipped[p.b + p.size] if free else b.b - p.b - p.size
            go_on = score + b.size - 0.5 * max(0, gap - (b.a - p.a - p.size) - CHAIN_SLACK)
        if go_on < b.size:                                  # starting afresh here scores better
            start, score = k, float(b.size)
        else:
            score = go_on
        if score > best_score:
            best, best_score = (start, k + 1), score
    return blocks[best[0]:best[1]]


ROW_BAND = 4


def compare_table(clause, window, covered=None, place=None, row_span=None):
    """Discrepancies of a table row: its tokens missing from its own stretch of the page, as a bag. The stretch is
    the aligned run of the page text plus, when place gives each window token's (page, height), every token
    printed within the band of heights the aligned tokens span (a row's cells, whatever order the engine read
    them in); without place, the run widened by the row's length either side. covered (a set) receives the
    window positions of tokens the row accounts for."""
    blocks = chain(SequenceMatcher(None, clause, window, autojunk=False).get_matching_blocks())
    lo, hi = (blocks[0].b, blocks[-1].b + blocks[-1].size) if blocks else (0, len(window))
    if blocks and place and place[lo][1] is not None:
        band = {}
        for b in blocks:
            for k in range(b.b, b.b + b.size):
                pg, y = place[k]
                low, high = band.get(pg, (y, y))
                band[pg] = (min(low, y), max(high, y))
        span = sorted(set(range(lo, hi)) | {k for k, (pg, y) in enumerate(place) if pg in band
                                            and band[pg][0] - ROW_BAND <= y <= band[pg][1] + ROW_BAND})
    else:
        span = list(range(max(lo - len(clause), 0), min(hi + len(clause), len(window))))
    if covered is not None and blocks:
        wanted = Counter(clause)
        for b in blocks:                                    # the aligned tokens first, then the nearest others
            for k in range(b.b, b.b + b.size):
                wanted[window[k]] -= 1
                covered.add(k)
        order = sorted(span, key=lambda k: 0 if lo <= k < hi else min(abs(k - lo), abs(k - hi)))
        for k in order:
            if k not in covered and wanted[window[k]] > 0:
                wanted[window[k]] -= 1
                covered.add(k)
    if row_span is not None and blocks:
        row_span.extend(span)                                   # the row's stretch, for row-level coverage
    stretch = [window[k] for k in span]
    have, missing = Counter(stretch), []
    for t in clause:
        if have[t] > 0:
            have[t] -= 1
        else:
            missing.append(t)
    near, runs = joins(stretch), char_runs(stretch)
    missing = [t for t in missing if not any(same(t, x) for x in stretch) and unlig(t) not in near
               and not any(t in r for r in runs)]
    return [("missing", missing, [])] if missing else []


ELSEWHERE = 5


def grams(toks, n=ELSEWHERE):
    return {tuple(toks[k:k + n]) for k in range(len(toks) - n + 1)}


def stored_elsewhere(run, elsewhere, tables=()):
    """A run of ELSEWHERE or more page tokens that other clauses of these pages hold word for word (every token
    lies in a run of ELSEWHERE tokens found in one of them: grams()), or that one table of these pages holds as a
    bag (tables: a Counter of each table's row tokens; the engines read cells in different orders)."""
    if re.fullmatch(r"\d{1,3}", run[0]) and len(run) > ELSEWHERE:
        run = run[1:]                                       # a footnote's number, then its text held elsewhere
    if len(run) < ELSEWHERE:
        return False
    if any(not Counter(run) - t for t in tables):
        return True
    hit = set()
    for k in range(len(run) - ELSEWHERE + 1):
        if tuple(run[k:k + ELSEWHERE]) in elsewhere:
            hit.update(range(k, k + ELSEWHERE))
    return len(hit) == len(run)


def letters(toks):
    return unlig("".join(t for t in toks if not t.isdigit()))


def spaced(clause_part, window, at, before=True):
    """Clause tokens at the start or end of the clause that the page prints near that place with the same letters
    split differently: headings in small capitals, which pdfminer reads as "s cope of g uideline"."""
    want = letters(clause_part)
    k = 3 * len(clause_part) + 4
    region = window[max(at - k, 0):at] if before else window[at:at + k]   # outside the clause's stretch
    if any(region[i:i + len(clause_part)] == list(clause_part) for i in range(len(region))):
        return False                                    # the same tokens verbatim: not split capitals
    return len(want) >= 4 and want in letters(region) and any(len(t) == 1 and t.isalpha() for t in region)


def compare_text(clause, window, small=frozenset(), starts=frozenset(), covered=None, elsewhere=frozenset(),
                 soft=frozenset(), tables=()):
    """Discrepancies of running text: (op, clause tokens, page tokens) for every difference in the clause's
    stretch of the page that no rule of the module docstring tolerates. covered (a set) receives the window
    positions of the stretch, for the coverage check."""
    free = [k in soft or k in small or len(t) == 1 for k, t in enumerate(window)]
    blocks = chain(SequenceMatcher(None, clause, window, autojunk=False).get_matching_blocks(), free)
    if not blocks:
        return [("missing", clause, [])]
    lo, hi = blocks[0].b, blocks[-1].b + blocks[-1].size
    if covered is not None:
        covered.update(range(lo, hi))
    stretch = window[lo:hi]
    small = {k - lo for k in small if lo <= k < hi}
    found, pos = [], []
    for op, i1, i2, j1, j2 in SequenceMatcher(None, clause, stretch, autojunk=False).get_opcodes():
        if op == "equal":
            continue
        a, b = clause[i1:i2], stretch[j1:j2]
        letters = [x for x in b if not (x.isdigit() and len(x) <= 4)]
        if op == "replace" and (
                (len(a) == len(b) and all(x == y or unlig(x) == y for x, y in zip(a, b)))
                or unlig("".join(a)) == "".join(b) or "".join(a) == "".join(b)
                or (2 <= len(letters) < len(b) and all(x.isalpha() for x in letters)
                    and unlig("".join(a)) == unlig("".join(letters)))):
            continue                                        # ligatures, split or joined words, margin numbers
        if op == "insert" and len(b) >= 3 and all(len(x) == 1 for x in b):
            continue                                        # vertical text read character by character
        if op == "insert" and any(k + lo in soft for k in range(j1, j2)) and all(
                k + lo in soft or len(stretch[k]) == 1 for k in range(j1, j2)):
            continue                                        # a line repeated on many pages (running title, reference),
                                                            # with vertical text beside it
        if op == "insert" and stored_elsewhere(b, elsewhere, tables):
            continue                                        # another clause holds it (a table row, a footnote)
        if op == "insert" and all(k in small for k in range(j1, j2)) \
                and not (j1 > 0 and re.search(r"\d", stretch[j1 - 1])):
            continue                                        # footnote marks (not an exponent after a number)
        if op == "delete" and (i1 == 0 or i2 == len(clause)) and spaced(a, window, lo if i1 == 0 else hi, i1 == 0):
            continue                                        # a heading at the clause's edge set in spaced capitals
        if op == "delete" and len(a) <= 2 and all(
                t.isdigit() and len(t) <= 3 and any(stretch[k] == t for k in small) for t in a):
            continue                                        # footnote marks the PDF prints small or as a line start
        found.append((op, a, b))
        pos.append(lo + j1)
    def near_at(j):                                     # only the page tokens around the difference
        e = window[max(j - 4, 0):j + 4]
        e2 = [x for x in e if not (x.isdigit() and len(x) <= 3)]
        return (joins(e) | joins(e2)) - set(e) - set(e2)   # a join of page tokens, not one whole page token
    def marks(ts):
        return all((t.isdigit() and len(t) <= 3) or t in "<>≤≥±%−" for t in ts)
    inserted = {"".join(b) for op, _, b in found if op == "insert" and marks(b)}   # only marks move (footnote numbers, signs)
    deleted = {"".join(a) for op, a, _ in found if op == "delete" and marks(a)}
    found = [f for f, j in zip(found, pos)
             if not (f[0] == "delete" and (unlig("".join(f[1])) in near_at(j) or "".join(f[1]) in inserted))
             and not (f[0] == "insert" and "".join(f[2]) in deleted)]
    moved = Counter(t for op, _, b in found if op == "insert" for t in b) & \
        Counter(t for op, a, _ in found if op == "delete" for t in a)

    def mark(t):
        return (t.isdigit() and len(t) <= 3) or t in "<>≤≥±%−"
    return [(op, a, b) for op, a, b in found
            if not (op in ("insert", "delete") and len(a or b) == 1 and mark((a or b)[0]) and moved[(a or b)[0]])]


def describe(discrepancies):
    """One line per clause: "-x y" for clause tokens the page lacks, "+x y" for page tokens the clause lacks."""
    parts = []
    for _, a, b in discrepancies:
        if a:
            parts.append("-" + " ".join(a))
        if b:
            parts.append("+" + " ".join(b))
    return " | ".join(parts)


UNCOVERED_MIN = 3


def spelled(run):
    """Vertical text read a character or two at a time ("d o c u m e n a n d r ec o r"): seven in ten tokens
    of one or two letters (table header cells set upright; the clause comparison tolerates them too)."""
    return sum(len(t) == 1 or (len(t) == 2 and t.isalpha()) for t in run) >= 0.7 * len(run)


def held_nearby(run, page, clauses):
    """A run the alignment left uncovered that a clause of the page or the pages next to it holds word for word
    (every token in a run of min(len, ELSEWHERE) tokens found there): repeated table rows ("N/A | No Q&A drafted")
    align to their first copy, and a clause read in another order leaves its text elsewhere on the page."""
    n = min(len(run), ELSEWHERE)
    near, text = set(), []
    for c in clauses:
        if c["page_start"] - 1 <= page <= c["page_end"] + 1:
            near |= grams(tokens(c["text"]), n)
            text.append(letters(tokens(c["text"])))
    if len(letters(run)) >= 8 and any(letters(run) in t for t in text):
        return True                                         # the same letters split differently (small capitals)
    hit = set()
    for k in range(len(run) - n + 1):
        if tuple(run[k:k + n]) in near:
            hit.update(range(k, k + n))
    return len(hit) == len(run)


def page_parts(page):
    """(tokens, small, starts, heights, optional, running) of a read_pages() page; heights None and no optional or
    running tokens for a page given as (tokens, small, starts)."""
    if len(page) == 3:
        return (*page, [None] * len(page[0]), set(), set())
    return page


def compare(clauses, reading):
    """([(ref, kind, tokens, discrepancy text)] for every clause but contents entries ("" when it matches),
    [(page, uncovered text)]): runs of UNCOVERED_MIN or more tokens of the second reading that no clause's
    stretch accounts for (text the stored clauses lack: a dropped paragraph, a cut-off clause end). Contents
    entries count toward coverage but are not compared."""
    pages, _ = reading
    covered = [set() for _ in pages]
    out = []
    held = [(c, grams(tokens(c["text"]))) for c in clauses]
    inrow, claim, ends = set(), {}, []
    for c in clauses:
        toks = tokens(c["text"])
        if not toks:
            continue
        first, last = max(c["page_start"] - 1 - MARGIN, 0), min(c["page_end"] + MARGIN, len(pages))
        window, small, starts, where, place, soft, head = [], set(), set(), [], [], set(), set()
        for p in range(first, last):
            page_tokens, page_small, page_starts, page_height, page_soft, page_head = page_parts(pages[p])
            place += [(p, y) for y in page_height]
            small |= {len(window) + k for k in page_small}
            soft |= {len(window) + k for k in page_soft}
            head |= {len(window) + k for k in page_head}
            where += [(p, k) for k in range(len(page_tokens))]
            window += page_tokens
            starts |= page_starts
        hit = set()
        if c["kind"] in TABLE_KINDS:
            found = compare_table(toks, window, place=place)
            taken = {k for k, (p, i) in enumerate(where) if i in covered[p]}
            row_span = []
            compare_table(toks, ["\0" if k in taken else t for k, t in enumerate(window)], hit, place, row_span)
            for k in row_span:                              # the row's whole band, for row-level coverage
                inrow.add(where[k])
        else:                                               # running text: without the running headers
            keep = [k for k in range(len(window)) if k not in head]
            at = {k: n for n, k in enumerate(keep)}
            elsewhere = set().union(*[g for o, g in held if o is not c and o["page_start"] - 1 <= c["page_end"]
                                      and o["page_end"] + 1 >= c["page_start"]])
            tables = {}
            for o in clauses:
                if o["kind"] in TABLE_KINDS and o["page_start"] <= c["page_end"] and o["page_end"] >= c["page_start"]:
                    tables[o["ref"].split()[1]] = tables.get(o["ref"].split()[1], Counter()) + Counter(tokens(o["text"]))
            text_hit = set()
            found = compare_text(toks, [window[k] for k in keep], {at[k] for k in small if k in at}, starts,
                                 text_hit, elsewhere, {at[k] for k in soft if k in at}, list(tables.values()))
            hit = {keep[n] for n in text_hit}
            if hit and c["kind"] != "toc":
                for k in hit:
                    claim.setdefault(where[k], []).append(c["ref"])
                ends.append((c["ref"], where[min(hit)], where[max(hit)]))
        for k in hit:
            covered[where[k][0]].add(where[k][1])
        if c["kind"] != "toc":
            out.append((c["ref"], c["kind"], len(toks), describe(found)))
    uncovered = []
    for p, page in enumerate(pages):
        page_tokens, page_small, _, _, page_soft, page_head = page_parts(page)
        run = []
        for k, t in enumerate(page_tokens + [None]):
            if t is not None and k not in covered[p] and k not in page_small | page_soft | page_head:
                run.append(t)
                continue
            if len(run) >= UNCOVERED_MIN and not held_nearby(run, p + 1, clauses) and not spelled(run):
                uncovered.append((p + 1, " ".join(run)))
            elif run and all((p, j) in inrow for j in range(k - len(run), k)) and not spelled(run):
                uncovered.append((p + 1, "in table row: " + " ".join(run)))
            run = []
    for ref, (p0, i0), (p1, i1) in ends:                    # a clause's first or last words left on the page
        for p, side in ((p0, range(i0 - 1, i0 - 1 - UNCOVERED_MIN, -1)), (p1, range(i1 + 1, i1 + 1 + UNCOVERED_MIN))):
            page_tokens, page_small, _, _, page_soft, page_head = page_parts(pages[p])
            run = []
            for j in side:
                if not 0 <= j < len(page_tokens) or j in covered[p] or j in page_small | page_soft | page_head:
                    break
                run.append(page_tokens[j])
            if run and len(run) < UNCOVERED_MIN and any((len(t) > 1 and t.isalpha()) or re.fullmatch(r"\d+[.,]\d+|\d{4,}", t) for t in run) \
                    and not spelled(run):
                uncovered.append((p + 1, f"next to {ref}: " + " ".join(run)))
    twice = sorted(k for k, v in claim.items() if len(v) > 1)  # page text claimed by two text clauses
    run, prev = [], None
    for k in twice + [None]:
        if k is not None and prev is not None and k[0] == prev[0] and k[1] == prev[1] + 1:
            run.append(k)
        else:
            if len(run) >= UNCOVERED_MIN:
                uncovered.append((run[0][0] + 1, "in two clauses " + " and ".join(sorted(set(claim[run[0]])))
                                  + ": " + " ".join(page_parts(pages[run[0][0]])[0][i] for _, i in run)))
            run = [k] if k is not None else []
        prev = k
    return out, uncovered


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def pdf_sources():
    """The PDF sources with parsed clauses."""
    return sorted(p.stem + ".pdf" for p in CLAUSES.glob("*.jsonl") if (OFFICIAL / (p.stem + ".pdf")).exists())


def check_source(f):
    """The report entry of one PDF source."""
    path = CLAUSES / (Path(f).stem + ".jsonl")
    clauses = [json.loads(ln) for ln in path.read_text(encoding="utf-8").splitlines() if ln.strip()]
    rows, uncovered = compare(clauses, second_reading(OFFICIAL / f))
    return {"pdf_sha256": sha256(OFFICIAL / f), "clauses_sha256": sha256(path), "clauses": len(rows),
            "tokens": sum(n for _, _, n, _ in rows),
            "flagged": [{"ref": r, "kind": k, "tokens": n, "discrepancy": d} for r, k, n, d in rows if d]
            + [{"ref": f"page {p}", "kind": "uncovered", "tokens": len(t.split()), "discrepancy": "+" + t}
               for p, t in uncovered]}


def run(files=None, jobs=1):
    files = files or pdf_sources()
    old = json.loads(REPORT.read_text(encoding="utf-8")) if REPORT.exists() else {}
    report = old.get("sources", {}) if old.get("code_sha256") == code_sha256() else {}
    if jobs > 1:
        from concurrent.futures import ProcessPoolExecutor
        with ProcessPoolExecutor(jobs) as pool:
            results = pool.map(check_source, files)
            for f, entry in zip(files, results):
                report[f] = entry
                print(f"{f}: {entry['clauses']} clauses, {len(entry['flagged'])} flagged", flush=True)
    else:
        for f in files:
            report[f] = check_source(f)
            print(f"{f}: {report[f]['clauses']} clauses, {len(report[f]['flagged'])} flagged", flush=True)
    doc = {"engine": "pdfminer.six via pdfplumber", "code_sha256": code_sha256(),
           "sources": dict(sorted(report.items()))}
    REPORT.write_text(json.dumps(doc, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    REPORT_MD.write_text(markdown(doc), encoding="utf-8")
    return doc


def explanations(path=EXPLANATIONS):
    """[(source, ref, discrepancy, reason)]."""
    if not Path(path).exists():
        return []
    with open(path, encoding="utf-8") as f:
        return [(r["source"], r["ref"], r["discrepancy"], r["reason"]) for r in csv.DictReader(f)]


def explanation(source, flag, why):
    """The reason that covers a flagged clause, or None: an entry for its ref with the same discrepancy text, or a
    source-wide pattern ("*") that the discrepancy matches in full."""
    for s, ref, disc, reason in why:
        if s != source:
            continue
        if ref == flag["ref"] and disc == flag["discrepancy"]:
            return reason
        if ref == "*" and re.fullmatch(disc, flag["discrepancy"]):
            return reason
    return None


def problems(doc, why, inventory=None, pilot=()):
    """Everything `check` fails on: [(source, ref or "", detail)]."""
    out = []
    if doc.get("code_sha256") != code_sha256():
        out.append(("", "", "the report was built by another version of fidelity.py: run it again"))
    for f, s in doc["sources"].items():
        if inventory is not None and inventory.get(f) != s["pdf_sha256"]:
            out.append((f, "", "the PDF differs from sources/inventory.csv: run the check again"))
        for flag in s["flagged"]:
            if explanation(f, flag, why) is None:
                out.append((f, flag["ref"], f"{flag['kind']}: {flag['discrepancy']}"))
    out += [(f, "", "pilot must/should PDF source missing from the report") for f in sorted(set(pilot) - set(doc["sources"]))]
    return out


def pilot_pdfs():
    with open(ROOT / "sources" / "catalog.csv", encoding="utf-8") as f:
        return [r["file"] for r in csv.DictReader(f) if r["file"].endswith(".pdf") and r["phase"] == "pilot"
                and r["priority"] in ("must", "should")]


def inventory_hashes():
    with open(ROOT / "sources" / "inventory.csv", encoding="utf-8") as f:
        return {r["file"]: r["sha256"] for r in csv.DictReader(f)}


def markdown(doc):
    srcs = doc["sources"]
    why = explanations()
    flags = [(f, c) for f, s in srcs.items() for c in s["flagged"]]
    lines = ["# Source fidelity report", "",
             f"Built by `python3 tools/parse/fidelity.py run` (D39): every parsed clause of every PDF source compared "
             f"in both directions with a second reading ({doc['engine']}); the rules are in the module docstring. "
             "Every flagged clause is fixed or explained in `library/fidelity-explanations.csv`.", "",
             f"Sources: {len(srcs)}; clauses: {sum(s['clauses'] for s in srcs.values())}; tokens: "
             f"{sum(s['tokens'] for s in srcs.values())}; flagged clauses: {len(flags)}; unexplained: "
             f"{sum(explanation(f, c, why) is None for f, c in flags)}.", "",
             "| Source | Clauses | Flagged |", "|---|---|---|"]
    lines += [f"| {f} | {s['clauses']} | {len(s['flagged'])} |" for f, s in srcs.items()]
    lines += ["", "## Flagged clauses", ""]
    for f, c in flags:
        lines.append(f"- {f} {c['ref']} ({c['kind']}): `{c['discrepancy'][:300]}` - "
                     f"{explanation(f, c, why) or 'NOT EXPLAINED'}")
    return "\n".join(lines) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("command", choices=["run", "check"])
    ap.add_argument("files", nargs="*", help="run: PDF file names in sources/official (default: all parsed PDFs)")
    ap.add_argument("--jobs", type=int, default=1, help="run: processes")
    a = ap.parse_args()
    if a.command == "run":
        run([Path(f).name for f in a.files] or None, a.jobs)
        return
    doc = json.loads(REPORT.read_text(encoding="utf-8"))
    found = problems(doc, explanations(), inventory_hashes(), pilot_pdfs())
    for f, ref, detail in found:
        print(f"fidelity: {f} {ref}: {detail}")
    print(f"fidelity: {sum(s['clauses'] for s in doc['sources'].values())} clauses in {len(doc['sources'])} "
          f"sources, {len(found)} problems")
    sys.exit(1 if found else 0)


if __name__ == "__main__":
    main()
