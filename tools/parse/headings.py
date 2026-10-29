"""Heading-based parser for FDA guidance PDFs and compliance programs (deterministic, no AI).

FDA texts are not numbered paragraph by paragraph: they have an outline of headings ("IV. RECOMMENDATIONS",
"B. Stage 1 - Process Design", "2. Strategy", "PART III-INSPECTIONAL") and numbered lists inside the body that use the
same markers ("1. A clear statement of the reason ..."). A clause is therefore a section: the text from one heading
to the next.

- The document's own table of contents is the outline when it has one (a block of lines with dot leaders). Each
  contents entry gets its reference from its place in the outline ("IV.B.2"; "Part II 2.A" in compliance programs),
  and a body line is a heading only when it carries the marker and the first two title words of the next expected
  entry (up to LOOKAHEAD entries ahead, so one unmatched entry does not block the rest; unmatched entries are noted).
  Body lists can never be mistaken for headings this way.
- Without a contents block, a marked line that looks like a heading (short, no closing full stop) is accepted when
  its marker is the next one in the outline: the next sibling (skipping at most one), or the first child.
- Old FDA documents print line numbers in the margin ("16   I. INTRODUCTION"); when most lines carry one they are
  removed. Running headers and footers are removed as in the numbered parser.
"""
import re
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import Clause, edge_lines, english_line, line_key, normalise, pdf_pages, repeated_lines  # noqa: E402

ROMAN = {v: i for i, v in enumerate("I II III IV V VI VII VIII IX X XI XII XIII XIV XV XVI XVII XVIII XIX XX".split(),
                                    start=1)}
MARK = re.compile(r"^(PART\s+[IVX]+|[IVX]{1,5}\.|[A-Z]\.|\d{1,2}(?:\.\d{1,2}){1,2}\.?|\d{1,2}\.|[a-z]\.|\(\d{1,2}\)"
                  r"|\([a-z]\))(?:\s+|\s*[—–]\s*)(\S.*)$")
LEADER = re.compile(r"(?:\.\s?){4,}\s*\d*\s*$|\s{3,}\d{1,3}\s*$")
LINE_NO = re.compile(r"^\d{1,4}\s{2,}(?=\S)")
LOOKAHEAD = 4
TOC_GAP = 6            # lines without a leader allowed inside the contents block (wrapped entries)


def readings(mark):
    """Possible (type, value) readings of a marker: "I." is a Roman one or the letter I, "C." a letter."""
    m = mark.rstrip(".")
    if m.startswith("PART"):
        return [("part", ROMAN.get(m.split()[1], 0))]
    out = []
    if m in ROMAN:
        out.append(("roman", ROMAN[m]))
    if re.fullmatch(r"[A-Z]", m):
        out.append(("upper", ord(m) - 64))
    if re.fullmatch(r"\d{1,2}", m):
        out.append(("digit", int(m)))
    if re.fullmatch(r"\d{1,2}(\.\d{1,2}){1,2}", m):
        out.append(("decimal", tuple(int(x) for x in m.split("."))))
    if re.fullmatch(r"[a-z]", m):
        out.append(("lower", ord(m) - 96))
    if re.fullmatch(r"\(\d{1,2}\)", m):
        out.append(("pdigit", int(m[1:-1])))
    if re.fullmatch(r"\([a-z]\)", m):
        out.append(("plower", ord(m[1]) - 96))
    return out


def _next(kind, prev, value):
    """Is value the next number after prev (skipping at most one)? Decimals: sibling, child or back up a level."""
    if kind != "decimal":
        return 1 <= value - prev <= 2
    p, v = prev, value
    return ((len(v) == len(p) and v[:-1] == p[:-1] and 1 <= v[-1] - p[-1] <= 2)
            or (len(v) < len(p) and v[:-1] == p[:len(v) - 1] and 1 <= v[-1] - p[len(v) - 1] <= 2)
            or (len(v) == len(p) + 1 and v[:-1] == p and v[-1] == 1))


def _first(kind, value):
    return value == 1 or (kind == "decimal" and (value[-1] == 1 or len(value) == 2))


class Outline:
    """The heading stack: [(type, value, label)], e.g. roman IV > upper B > digit 2."""

    def __init__(self):
        self.stack = []

    def accept(self, mark):
        label = mark.rstrip(".")
        for kind, value in readings(mark):
            kinds = [s[0] for s in self.stack]
            if kind == "part":
                self.stack = [(kind, value, label.replace("PART", "Part"))]
                return True
            if kind in kinds:
                d = kinds.index(kind)
                if _next(kind, self.stack[d][1], value):
                    self.stack = self.stack[:d] + [(kind, value, label)]
                    return True
            elif _first(kind, value):
                self.stack.append((kind, value, label))
                return True
        return False

    def ref(self):
        """"IV.B.2"; a part prefixes the rest: "Part II 2.A"."""
        labels = [s[2] for s in self.stack]
        if self.stack and self.stack[0][0] == "part":
            return f"{labels[0]} {'.'.join(labels[1:])}".strip()
        return ".".join(labels)


def body_lines(pages):
    """(page, line) of the body: English lines without running headers, footers and margin line numbers."""
    noise = repeated_lines(pages)
    every = [ln.strip() for pg in pages for ln in pg.splitlines() if ln.strip()]
    margin_numbers = sum(1 for ln in every if LINE_NO.match(ln)) > 0.3 * max(1, len(every))
    out, dropped = [], 0
    for pno, page in enumerate(pages, start=1):
        edges = {ln.strip() for ln in edge_lines(page)}
        for raw in page.splitlines():
            line = raw.strip()
            if margin_numbers:
                line = LINE_NO.sub("", line)
            if not line or not english_line(line):
                continue
            running = line_key(raw) in noise or re.fullmatch(r"[-–—\s\d]+|Page \d+( of \d+)?", line)
            if raw.strip() in edges and not line.startswith("[[TABLE ") and running:
                dropped += len(line.replace(" ", ""))
                continue
            out.append((pno, line))
    return out, dropped


def contents_block(lines):
    """(first, last) line index of the table of contents: marked lines with dot leaders close together."""
    idx = [i for i, (_, ln) in enumerate(lines) if LEADER.search(ln) and MARK.match(ln)]
    if len(idx) < 3:
        return None
    first = last = idx[0]
    for i in idx[1:]:
        if i - last > TOC_GAP:
            break
        last = i
    return first, last


def _words(text, n):
    return [re.sub(r"\d+$", "", w) for w in re.findall(r"[a-z0-9]+", text.lower())[:n]]


def heading_like(rest):
    rest = rest.strip()
    return bool(rest) and (rest.isupper() or (len(rest) < 110 and not rest.endswith((".", ";", ",", ":"))))


def parse(path, pages=None):
    """Sections of an FDA PDF as clauses: (clauses, body_chars, dropped_chars)."""
    pages = pdf_pages(path) if pages is None else pages
    lines, dropped = body_lines(pages)
    toc = contents_block(lines)
    entries = []                       # (marker, first title words, ref)
    if toc:
        outline = Outline()
        for _, ln in lines[toc[0]:toc[1] + 1]:
            m = MARK.match(ln)
            if m and outline.accept(m.group(1)):
                entries.append((m.group(1).rstrip("."), _words(LEADER.sub("", m.group(2)), 2), outline.ref()))
    clauses, cur, outline, nxt, unnumbered, body = [], None, Outline(), 0, 0, 0

    def start(kind, ref, line, pno):
        nonlocal cur
        cur = {"kind": kind, "ref": ref, "lines": [line], "page_start": pno, "page_end": pno, "notes": []}
        clauses.append(cur)

    for i, (pno, line) in enumerate(lines):
        body += len(line.replace(" ", ""))
        if toc and toc[0] <= i <= toc[1]:
            if cur and cur["kind"] == "toc":
                cur["lines"].append(line)
            else:
                start("toc", "_toc", line, pno)
            continue
        m = MARK.match(line)
        ref = None
        if m and entries:
            for j in range(nxt, min(nxt + LOOKAHEAD, len(entries))):
                if m.group(1).rstrip(".") == entries[j][0] and _words(m.group(2), 2) == entries[j][1]:
                    skipped = [e[2] for e in entries[nxt:j]]
                    ref, nxt = entries[j][2], j + 1
                    break
        elif m and heading_like(m.group(2)) and outline.accept(m.group(1)):
            ref, skipped = outline.ref(), []
        if ref:
            start("clause", ref, line, pno)
            cur["notes"] += [f"gap: contents entry {s} not found in the body" for s in skipped]
            continue
        if cur is None or cur["kind"] == "toc":
            unnumbered += 1
            start("unnumbered", f"_unnumbered:{unnumbered}", line, pno)
        else:
            cur["lines"].append(line)
            cur["page_end"] = pno
    notes = [f"gap: contents entry {e[2]} not found in the body" for e in entries[nxt:]]
    out = []
    for k, c in enumerate(clauses):
        out.append(Clause(source=Path(path).name, ref=c["ref"] if c["kind"] != "toc" else f"_toc:{k + 1}",
                          section="", number=c["ref"] if c["kind"] == "clause" else "", heading=c["lines"][0][:160],
                          text=normalise(" ".join(c["lines"])), page_start=c["page_start"], page_end=c["page_end"],
                          kind=c["kind"], notes=c["notes"]))
    if out and notes:
        out[-1].notes += notes
    return out, body, dropped
