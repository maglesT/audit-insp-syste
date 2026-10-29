"""Parser for fda.gov HTML pages: CGMP Q&A pages, inspection guides, compliance policy guides (deterministic).

Only the page's <article> is read; page chrome after "Content current as of" is left out. Block elements (p, li,
headings, table cells, ...) become text blocks in page order. Ordered lists keep their visible markers ("IV", "B").

- Q&A pages (title "Questions and Answers ..."): the page lists its questions first and then repeats each one above
  its answer. A block that repeats an earlier index entry, or that carries the next question number, starts clause
  "Q<n>"; the answer, references and date that follow belong to it. The index entries become kind "toc".
- Other pages: one clause per paragraph or list item, "¶<n>" in page order, with the last heading as its `section`.
  Paragraph numbers rather than sections, because several ORA guides put text before the heading it belongs to in
  the HTML; headings are kept as unnumbered segments so no text is lost.
"""
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import Clause  # noqa: E402

BLOCK = {"p", "li", "h1", "h2", "h3", "h4", "h5", "h6", "dt", "dd", "td", "th", "blockquote", "pre", "div", "tr",
         "caption"}
SKIP = {"script", "style", "nav", "noscript", "button", "form", "svg"}
ROMAN = "I II III IV V VI VII VIII IX X XI XII XIII XIV XV XVI XVII XVIII XIX XX".split()
QUESTION = re.compile(r"^(?:Q\s?)?(\d{1,3})\.\s+(.+)$")
CHROME = re.compile(r"^(Content current as of|Regulated Product|Topic\(s\)|Submit Comments)")
HEADINGS = ("h1", "h2", "h3", "h4", "h5", "h6")


def list_marker(kind, n):
    if kind in ("I", "i"):
        label = ROMAN[n - 1] if n <= len(ROMAN) else str(n)
        return label if kind == "I" else label.lower()
    if kind in ("A", "a") and n <= 26:
        return chr((64 if kind == "A" else 96) + n)
    return str(n)


class Blocks(HTMLParser):
    """Text blocks inside <article>: {"tag", "text", "marker", "bold"} in page order."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.article = self.skip = 0
        self.blocks, self.buf, self.strong, self.lists = [], [], [], []
        self.tag, self.marker, self.in_strong = "p", "", False

    def flush(self):
        text = re.sub(r"\s+", " ", "".join(self.buf)).strip()
        if text:
            strong = re.sub(r"\s+", " ", "".join(self.strong)).strip()
            self.blocks.append({"tag": self.tag, "text": text, "marker": self.marker, "bold": strong == text})
        self.buf, self.strong, self.marker = [], [], ""

    def handle_starttag(self, tag, attrs):
        if tag == "article":
            self.article += 1
        if not self.article:
            return
        if tag in SKIP:
            self.skip += 1
        elif tag in ("ol", "ul"):
            self.flush()
            a = dict(attrs)
            self.lists.append([(a.get("type") or "1") if tag == "ol" else "*", int(a.get("start") or 1) - 1])
        if tag in BLOCK or tag == "br":
            self.flush()
            if tag != "br":
                self.tag = tag
        if tag == "li" and self.lists:
            self.lists[-1][1] += 1
            kind, n = self.lists[-1]
            self.marker = "" if kind == "*" else list_marker(kind, n)
        if tag in ("strong", "b"):
            self.in_strong = True

    def handle_endtag(self, tag):
        if not self.article:
            return
        if tag == "article":
            self.flush()
            self.article -= 1
        elif tag in SKIP:
            self.skip = max(0, self.skip - 1)
        elif tag in BLOCK:
            self.flush()
        elif tag in ("ol", "ul") and self.lists:
            self.flush()
            self.lists.pop()
        if tag in ("strong", "b"):
            self.in_strong = False

    def handle_data(self, data):
        if self.article and not self.skip:
            self.buf.append(data)
            if self.in_strong:
                self.strong.append(data)


def blocks(path):
    parser = Blocks()
    parser.feed(Path(path).read_text(encoding="utf-8", errors="replace"))
    parser.flush()
    out = parser.blocks
    for i, b in enumerate(out):
        if CHROME.match(b["text"]):
            return out[:i]
    return out


def _key(text):
    """First six words, lower case, letters and digits only: the index and the answers section word a question
    slightly differently ("auto-calibration" / "auto calibration")."""
    return " ".join(re.findall(r"[a-z0-9]+", re.sub(r"^\d{1,3}\.\s+", "", text).lower().replace("-", ""))[:6])


def questions(bl):
    """{block index: question number} and the set of index-entry blocks, for a Q&A page.

    Numbered pages: the answers section repeats the questions in order, after the index, so walking back from the
    highest number and taking the last block with each number finds the questions and never an index entry or a
    list item (list numbers are not part of the block text). Pages without numbers: a block that repeats an earlier
    one (from the index above the first question) starts a question.
    """
    if not any(b["tag"] == "h1" and "Questions and Answers" in b["text"] for b in bl):
        return {}, set()
    numbered = [(i, int(m.group(1))) for i, b in enumerate(bl)
                if (m := QUESTION.match(b["text"])) and len(m.group(2)) >= 15]
    found = {}
    if len({n for _, n in numbered}) >= 3:
        pos = len(bl)
        for k in range(max(n for _, n in numbered), 0, -1):
            before = [i for i, n in numbered if n == k and i < pos]
            if before:
                found[before[-1]] = k
                pos = before[-1]
    else:
        first_seen, used = {}, set()
        for i, b in enumerate(bl):
            key = _key(b["text"])
            if len(key.split()) < 4:
                continue
            if key in first_seen and first_seen[key] not in used:
                used.add(first_seen[key])
                found[i] = len(found) + 1
            elif not found:
                first_seen.setdefault(key, i)
    start = min(found, default=len(bl))
    keys = {_key(bl[i]["text"]) for i in found}
    index = {i for i in range(start) if _key(bl[i]["text"]) in keys}
    return found, index


def parse(path):
    """Clauses of an fda.gov page: (clauses, body_chars, dropped_chars)."""
    bl = blocks(path)
    found, index = questions(bl)
    rows, heading, para, in_q, unnumbered = [], "", 0, False, 0
    for i, b in enumerate(bl):
        text = (b["marker"] + ". " if b["marker"] else "") + b["text"]
        if i in index:
            rows.append(["toc", f"_toc:{len(rows) + 1}", "", [text]])
        elif i in found:
            in_q = True
            rows.append(["clause", f"Q{found[i]}", "", [text]])
        elif in_q and b["tag"] not in ("h1", "h2"):
            rows[-1][3].append(text)                  # answer, references and date stay with their question
        elif b["tag"] in HEADINGS or (b["bold"] and len(b["text"]) < 120):
            in_q, heading = False, text
            unnumbered += 1
            rows.append(["unnumbered", f"_unnumbered:{unnumbered}", heading, [text]])
        else:
            in_q = False
            para += 1
            rows.append(["clause", f"¶{para}", heading, [text]])
    name = Path(path).name
    clauses = [Clause(source=name, ref=ref, section=sec[:160], number=ref if kind == "clause" else "",
                      heading=parts[0][:160], text=" ".join(parts), page_start=0, page_end=0, kind=kind)
               for kind, ref, sec, parts in rows]
    body = sum(len(c.text.replace(" ", "")) for c in clauses)
    return clauses, body, 0
