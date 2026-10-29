"""NLP safety net: find every obligation sentence in a source, independent of clause numbering (D19).

Even if the numbering parser misreads a document's structure, a requirement cannot go missing: every sentence that
carries obligation wording (shall, must, should, is required, ...) is listed here with the clause it landed in, and
the pipeline must later show that each of these sentences is covered by a mapping or marked not applicable.
Classic NLP only (sentence splitting + modal-verb patterns); no AI, fully reproducible.
"""
import re

ABBREV = r"(?:e\.g|i\.e|etc|No|Nos|Fig|Ref|para|Sect|Art|cf|vs|approx|incl|min|max|Dr|Mr|Ms|St)\."
SPLIT = re.compile(r"(?<=[.;!?])\s+(?=[A-Z(\"'“‘0-9•–-])")
MANDATORY = re.compile(r"\b(shall|must|is required to|are required to|is required|are required|has to|have to|"
                       r"is mandatory|are mandatory|is not permitted|are not permitted|is prohibited|are prohibited|"
                       r"should not under any circumstances)\b", re.I)
RECOMMENDED = re.compile(r"\b(should|is expected to|are expected to|is expected|are expected|it is recommended|"
                         r"is recommended|are recommended|ought to|it is advisable)\b", re.I)
PERMISSIVE = re.compile(r"\b(may|can be|could be|is acceptable|are acceptable)\b", re.I)
NUMBER = re.compile(r"(?<![\w.])(?:\d+(?:[.,]\d+)?)(?:\s?(?:%|°C|ºC|°|µm|μm|mm|cm|m|mL|ml|L|mg|g|kg|ppm|ppb|EU|CFU|cfu|"
                    r"h|hr|hours?|min(?:utes)?|days?|weeks?|months?|years?|times))?(?![\w.])")


def sentences(text):
    """Split clause text into sentences, protecting common abbreviations."""
    protected = re.sub(ABBREV, lambda m: m.group(0).replace(".", "․"), text)
    return [s.replace("․", ".").strip() for s in SPLIT.split(protected) if s.strip()]


def strength(sentence):
    if MANDATORY.search(sentence):
        return "mandatory"
    if RECOMMENDED.search(sentence):
        return "recommended"
    if PERMISSIVE.search(sentence):
        return "permissive"
    return None


def numbers(sentence):
    return [m.group(0).strip() for m in NUMBER.finditer(sentence)]


def extract(clauses):
    """Obligation sentences of a parsed source: one dict per sentence with obligation wording."""
    out = []
    for c in clauses:
        if c.kind == "toc":
            continue
        for i, s in enumerate(sentences(c.text)):
            st = strength(s)
            if st:
                out.append({"source": c.source, "ref": c.ref, "sentence_index": i, "strength": st,
                            "numbers": numbers(s), "text": s})
    return out
