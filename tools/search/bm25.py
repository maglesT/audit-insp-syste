"""BM25 (Okapi) over clause texts: the lexical half of candidate search (D21). Pure Python, deterministic.

Tokens are lower-case letter/digit runs with English stop words removed and a light suffix stem, so "inspections",
"inspected" and "inspection" meet. No AI.
"""
import math
import re
from collections import Counter

K1, B = 1.5, 0.75
WORD = re.compile(r"[a-z0-9]+")
STOP = set("""a an and are as at be been being but by can could do does for from had has have if in into is it its
may might must no not of on or other our shall should so such than that the their them then there these they this
those to under up upon was were what when where whether which while who whom will with within without would""".split())
# (suffix, shortest stem left): "-ation" and "-ate" need 5 letters left, so deviation/deviate -> "deviat" and
# operate/operation/operating -> "operat", while validate/validation -> "valid"
SUFFIXES = (("ations", 5), ("ation", 5), ("ions", 4), ("ion", 4), ("ating", 5), ("ated", 5), ("ates", 5),
            ("ate", 5), ("ings", 4), ("ing", 4), ("ies", 3), ("ied", 3), ("ed", 4), ("es", 4), ("s", 4))
KEEP = ("ss", "us", "is")                           # "process", "status", "analysis" are not plurals


def stem(word):
    """A light stem that joins a word with its common inflections: procedure/procedures, manufacture/
    manufactured/manufacturing, control/controlled, validate/validated/validation, process/processes."""
    if word.endswith(KEEP):
        return word
    stripped = False
    for suffix, rest in SUFFIXES:
        if word.endswith(suffix) and len(word) - len(suffix) >= rest:
            word = word[:-len(suffix)] + ("y" if suffix in ("ies", "ied") else "")
            stripped = True
            break
    if stripped and len(word) > 4 and word[-1] == word[-2] and word[-1] not in "aeiouys":
        word = word[:-1]                            # controll -> control, submitt -> submit
    if word.endswith("e") and len(word) > 4:
        word = word[:-1]                            # procedure -> procedur, like procedures -> procedur
    return word


def tokens(text):
    return [stem(w) for w in WORD.findall(text.lower()) if w not in STOP and len(w) > 1]


class BM25:
    def __init__(self, texts, k1=K1, b=B):
        self.k1, self.b = k1, b
        self.docs = [Counter(tokens(t)) for t in texts]
        self.lengths = [sum(d.values()) for d in self.docs]
        self.avg = sum(self.lengths) / len(self.docs) if self.docs else 0.0
        df = Counter(term for d in self.docs for term in d)
        n = len(self.docs)
        self.idf = {t: math.log(1 + (n - f + 0.5) / (f + 0.5)) for t, f in df.items()}

    def scores(self, query):
        """One score per document, in document order."""
        terms = set(tokens(query))
        out = []
        for doc, length in zip(self.docs, self.lengths):
            s = 0.0
            for t in terms:
                f = doc.get(t)
                if f:
                    s += self.idf[t] * f * (self.k1 + 1) / (f + self.k1 * (1 - self.b + self.b * length / self.avg))
            out.append(s)
        return out
