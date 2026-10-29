"""Independent cross-check that no obligation text was lost by the parser.

The PDF is read a second time with a different extraction mode (`pdftotext -raw`, reading order instead of
layout). Every obligation sentence found that way must also appear, word for word after normalisation, somewhere
in the parsed clauses. A miss means the parser dropped or mangled requirement text; it is reported, never ignored.
"""
import re
import subprocess

from obligations import sentences, strength

WORD = re.compile(r"[a-z0-9]+")


def norm_words(text):
    """Lower-case words without bare numbers (raw mode injects page and line numbers mid-sentence)."""
    return [w for w in WORD.findall(text.lower()) if not w.isdigit()]


def raw_text(path):
    return subprocess.run(["pdftotext", "-raw", str(path), "-"], capture_output=True, text=True, check=True).stdout


def missed_obligations(path, clauses, window=6):
    """Obligation sentences from the raw extraction that the parsed clauses do not contain.

    A sentence is cut into overlapping 6-word windows (step 2); it counts as found when at least half of its windows occur
    in the clause text. That tolerates running headers that raw mode inserts mid-sentence, but not lost text.
    """
    if not str(path).endswith(".pdf"):
        return []
    joined = " ".join(" ".join(norm_words(c.text)) for c in clauses)
    haystack, squeezed = " " + joined + " ", joined.replace(" ", "")   # squeezed: raw mode sometimes drops spaces
    missed = []
    for s in sentences(re.sub(r"\s+", " ", raw_text(path))):
        if not strength(s):
            continue
        words = norm_words(s)
        wins = [words[i:i + window] for i in range(0, len(words) - window + 1, 2)]
        if not wins:
            continue
        found = sum(1 for w in wins if " " + " ".join(w) + " " in haystack or "".join(w) in squeezed)
        if found < len(wins) / 2:
            missed.append(s[:200])
    return missed
