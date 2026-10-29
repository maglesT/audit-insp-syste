"""Parser for the EMA "GMP and GDP: Questions and answers" web page (deterministic, no AI).

The page groups numbered questions under topic headings (h2: "EU GMP guide part I: Basic requirements for medicinal
products: Chapter 1: Pharmaceutical quality system"). Each question sits in an accordion button (h3) above its
answer; numbering restarts under every topic. A clause is one question with its answer, referenced by the topic and
the number: "EU GMP guide part I: Chapter 1: Pharmaceutical quality system Q1". The wordy middle part of a topic
title ("Basic requirements for medicinal products", "Supplementary requirements") is left out of the reference;
the full title stays in `section`. Text under a topic that is not part of a question is an unnumbered segment.
"""
import re
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import Clause  # noqa: E402
from fdahtml import QUESTION, SKIP, blocks  # noqa: E402

END = re.compile(r"^(Page update history|Topics|Share this page)$")
FILLER = re.compile(r"^(Basic requirements|Supplementary requirements|GMP requirements for)", re.I)
LABEL_MAX = 90


def topic_label(title):
    """The topic title without its wordy middle part, cut to LABEL_MAX characters."""
    parts = [p.strip() for p in title.split(": ")]
    label = ": ".join([parts[0]] + [p for p in parts[1:] if not FILLER.match(p)])
    return label if len(label) <= LABEL_MAX else label[:LABEL_MAX].rsplit(" ", 1)[0] + "…"


def parse(path):
    """Questions with their answers as clauses: (clauses, body_chars, dropped_chars)."""
    bl = blocks(path, SKIP - {"button"})          # the questions are the accordion buttons
    rows, topic, label, expected, unnumbered, used = [], "", "", 1, 0, {}
    current = None
    for b in bl:
        text = b["text"]
        if b["tag"] == "h2":
            if END.match(text):
                break
            topic, label, expected, current = text, topic_label(text), 1, None
            unnumbered += 1
            rows.append(["unnumbered", f"_unnumbered:{unnumbered}", topic, [text]])
            continue
        m = QUESTION.match(text)
        if topic and b["tag"] == "h3" and m and int(m.group(1)) == expected:
            expected += 1
            ref = f"{label} Q{m.group(1)}"
            used[ref] = used.get(ref, 0) + 1
            ref = ref if used[ref] == 1 else f"{ref} #{used[ref]}"
            current = ["clause", ref, topic, [text]]
            rows.append(current)
            continue
        if current is not None and b["tag"] not in ("h2", "h3"):
            current[3].append(text)
            continue
        current = None
        unnumbered += 1
        rows.append(["unnumbered", f"_unnumbered:{unnumbered}", topic, [text]])
    name = Path(path).name
    clauses = [Clause(source=name, ref=ref, section=sec[:160], number=ref if kind == "clause" else "",
                      heading=parts[0][:160], text=" ".join(parts), page_start=0, page_end=0, kind=kind)
               for kind, ref, sec, parts in rows]
    body = sum(len(c.text.replace(" ", "").replace("|", "")) for c in clauses)
    return clauses, body, 0
