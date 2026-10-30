"""Layer 1: deterministic checks of every mapping, every run, no AI (plan section 2.4).

  python3 tools/library/layer1.py [library dir]       # prints findings; exit 1 if a check fails on a verified
                                                      # item, or on structure, coverage, twins or fingerprints

Checks, per mapping:
  1 quote      the quote appears word for word in the cited clause (whitespace-normalised)
  2 clause     the clause reference exists in the parsed clause tree, and its text hash matches clause_sha256
               (a changed source text means "re-verify")
  3 numbers    every number in the item text and the parameters appears in the quote
  4 strength   the mapping's strength matches the quote's words (shall/must -> mandatory, should ->
               recommended, may -> optional; a list item without such words takes its lead-in's), and the
               item's strength is its mapping's
  5 scope      the mapping's plant types are within the source's applies_to (catalog), and the item's plant
               types are its mapping's
Per library:
  6 coverage   for every source with a coverage file, every citable clause is mapped or marked not applicable
               (reported as a share; missing clauses are listed). A coverage entry must point at live requirements
               that really map that clause, and at clauses that exist; "must"/"should" sources without a coverage
               file are counted (not a failure until the library is meant to be complete)
  7 fingerprint every source file matches its sha256 in sources/inventory.csv; mappings to a changed source are
               flagged for re-verification
  8 twins      two mapped clauses of different sources with the same text (EU GMP and PIC/S) give identical
               items (D34, D37)
  9 conditions condition and limit wording in a quote ("where applicable", "before", "at least", "within 30
               days", "unless", "only") has a counterpart in the item text (D35)

The rules are strict on purpose: a false alarm costs a look, a missed error reaches a customer (D28).
"""
import csv
import hashlib
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "parse"))
import model  # noqa: E402
import obligations  # noqa: E402
from common import CITABLE, CLAUSES, OFFICIAL, normalise, twin_key  # noqa: E402

RANK = {"optional": 0, "recommended": 1, "mandatory": 2}
# condition and limit wording, by meaning (check 9, D35): a quote that says one of these must have an item that
# says it too, in any of the group's words. Only the condition uses count: "where applicable", not "areas where";
# "within 30 days", not "within the facility"; "after", not "the following".
_NUM = (r"(?:\d+|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen"
        r"|seventeen|eighteen|nineteen|twenty|thirty|forty|forty-eight|seventy-two|ninety|a|an|the\s+same)")
_TIME = (rf"{_NUM}(?:\s*\(\d+\))?\s*(?:-\s*)?(?:hours?|hrs?|h\b|days?|weeks?|months?|years?|minutes?|mins?"
         r"|working|business|calendar|shifts?)")
# "maximum"/"minimum" are limits only as "a minimum of 3", "minimum 3", "maximum permitted"; not "minimum and peak
# demand"; "longest permitted" says the same
_LIMIT = r"(?:permissible|permitted|allowed|allowable|acceptable)"
CONDITIONS = {
    "condition": r"(?:^|[.!?•:;,(]\s*|\b(?:and|or|but)\s+)(?:where|whenever)\b"
                 r"|(?<!\beven\s)(?<!\bas\s)\bif\b|\bwhen\b(?!\s+in\s+(?:operation|use)\b)"
                 r"|\bas\s+(?:\w+\s+){1,2}(?:requires?|dictates?)\b"
                 r"|\bas\s+(?:applicable|appropriate|necessary|needed|required)\b"
                 r"|\b(?:where|when|if)\s+(?:applicable|appropriate|necessary|needed|required|relevant|possible"
                 r"|justified|practicable|feasible)\b"
                 r"|\bin\s+(?:the\s+)?event\s+(?:of|that)\b|\bin\s+case\s+(?:of|that)\b|\bin\s+the\s+case\s+that\b"
                 r"|\bprovided\s+(?:that|it)\b|\bas\s+long\s+as\b|\beach\s+time\b|\bevery\s+time\b"
                 r"|\bon\s+each\s+occasion\b|\bin\s+the\s+absence\s+of\b",
    "before": r"\bbefore\b|\bprior\s+to\b|\bin\s+advance\b|\bbeforehand\b|\bprecede[sd]?\b|\bpreceding\b",
    "after": r"(?<!located\s)(?<!positioned\s)(?<!placed\s)(?<!installed\s)(?<!fitted\s)\bafter(?:wards)?\b"
             r"|\bfollowing\s+(?:any|each|every|completion|release|use|cleaning|approval|maintenance|repair)\b"
             r"|\bsubsequent(?:ly)?\b|(?<!\bno\s)\blater\b(?!\s+than)|\bonce\b(?!\s+(?:a|every|per|in)\b)|\bon\s+completion\b",
    "unless": r"\bunless\b|\bexcept\b|\bapart\s+from\b|\bexempt|\bexcluding\b",
    "at_least": rf"\bat\s+least\b|\bnot\s+less\s+than\b|\bno\s+less\s+than\b|\bat\s+a\s+minimum\b"
                rf"|\bminimum\s+(?:of\s+)?(?=\d|{_NUM}\b)|\b(?:minimum|lowest|shortest|least)\s+{_LIMIT}\b"
                r"|\bor\s+(?:more|longer)\b",
    "at_most": rf"\bnot\s+more\s+than\b|\bno\s+more\s+than\b|\bat\s+(?:the\s+)?most\b|\bnot\s+(?:to\s+)?exceed"
               rf"|\bmaximum\s+(?:of\s+)?(?=\d|{_NUM}\b)|\b(?:maximum|highest|longest|greatest)\s+{_LIMIT}\b"
               r"|\bup\s+to\b(?![\s-]+date)|\bor\s+(?:less|fewer|shorter)\b",
    "deadline": rf"\bwithin\s+{_TIME}|\bno\s+later\s+than\b|\bwithin\s+(?:a\s+)?(?:reasonable|defined|specified|agreed"
                r"|appropriate|predetermined|set)\s+(?:time|period|timeframe|timescale)|\bpromptly\b"
                r"|\bwithout\s+(?:undue\s+)?delay\b|\bimmediately\b|\bas\s+soon\s+as\s+(?:possible|practicable)\b",
    "until": r"\buntil\b|\btill\b|\bpending\b",
    "only": r"(?<!\bnot\s)\bonly\b(?!\s+the\s+minimum)|\bsolely\b|\bexclusively\b",
}
CONDITION_PATTERNS = {k: re.compile(v, re.I) for k, v in CONDITIONS.items()}
# "do not release until tested" says the same as "test before release" or "release only after testing"
SATISFIED_BY = {"until": {"before", "after"}}


# examples are not conditions: "e.g. in the case of product recalls ... or when an inspection is announced". The
# example runs to a closing bracket or the end of its sentence, but stops before a limit: "such as milling, to at
# least the standards"
EXAMPLE = re.compile(r"(?:\be\.\s?g\.,?|\bfor\s+example,?|\bfor\s+instance,?|\bsuch\s+as)"
                     r"(?:(?!\bat\s+least\b|\bunless\b|\bonly\b|\bwithin\b|\bbefore\b|\bafter\b)[^.;)])*", re.I)


def conditions_in(text):
    """The condition groups a text uses (check 9)."""
    text = EXAMPLE.sub("e.g.", text)
    return {k for k, pattern in CONDITION_PATTERNS.items() if pattern.search(text)}


def conditions_missing(quote, said):
    """The condition groups of a quote that none of the groups in `said` states."""
    return sorted(k for k in conditions_in(quote) if k not in said and not SATISFIED_BY.get(k, set()) & said)
SUPERSCRIPT = "⁰¹²³⁴⁵⁶⁷⁸⁹⁻"
# a number keeps its sign and its exponent: "−20", "10³", "10^6", "10⁻⁶"; "2-8" is 2 and 8
NUMBER = re.compile(rf"(?<![\w.])[-−]?\d+(?:[.,]\d+)?(?:\^-?\d+|[{SUPERSCRIPT}]+)?(?![\w.]*\d)")
WORDS = {1: "one", 2: "two", 3: "three", 4: "four", 5: "five", 6: "six", 7: "seven", 8: "eight", 9: "nine",
         10: "ten", 11: "eleven", 12: "twelve"}
TIMES = {1: "once", 2: "twice", 3: "thrice"}
# number words taken from item text ("one" and "once" are too common to mean a count)
WORD_NUMBERS = {w: n for n, w in WORDS.items() if n > 1} | {"twice": 2, "thrice": 3}
UNIT_EQUIVALENTS = {("frequency_max_months", 12): ("once a year", "once in a year", "annually", "yearly",
                                                  "every year", "12 months")}
# wording that is not the main obligation of a sentence: conditions, relative clauses, the month May
NOT_MAIN = [re.compile(p, re.I) for p in (
    r"^(?:where|if|when|whenever|unless|in case|in cases where|as long as)\b[^,]*,",
    r"\b(?:as|if|where|when|unless)\s+(?:otherwise\s+)?(?:is\s+|are\s+)?required\b",
    r"\b(?:that|which|who)\s+(?:is|are)\s+required\b",
    r"\b(?:that|which|who)\s+(?:has|have)\s+to\b",
)]
MONTH_MAY = re.compile(r"\bMay\s+\d{4}\b|\b\d{1,2}\s+May\b")
PROHIBITION = re.compile(r"\b(?:may|can)\s+not\b|\bcannot\b", re.I)


def read_csv(path):
    with open(path, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def catalog():
    return {r["file"]: r for r in read_csv(model.ROOT / "sources" / "catalog.csv")}


def segments_of(source, cache={}):
    """Every parsed segment of a source in document order (all kinds, including unnumbered text and contents
    entries), from library/clauses (rebuilt by tools/parse/run.py), or parsed on demand."""
    if source not in cache:
        path = CLAUSES / (Path(source).stem + ".jsonl")
        if path.exists():
            rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
        else:
            import run
            row = catalog()[source]
            rows = [c.to_json() for c in run.parser_for(row)(OFFICIAL / source)[0]]
        cache[source] = rows
    return cache[source]


def clauses_of(source, cache={}):
    """{ref: clause dict} of the citable clauses of a source."""
    if source not in cache:
        cache[source] = {c["ref"]: c for c in segments_of(source) if c["kind"] in CITABLE}
    return cache[source]


def plant_scope(applies_to):
    return set(model.PLANT_TYPES) if applies_to.strip() == "ALL" else set(applies_to.split(";"))


def numbers_in(text, words=False):
    """Numbers in a text, normalised ("−20" -> "-20", "0,5" -> "0.5"); words=True adds number words ("twice")."""
    out = {n.replace("−", "-").replace(",", ".") for n in NUMBER.findall(text)}
    if words:
        out |= {str(WORD_NUMBERS[w]) for w in re.findall(r"[a-z]+", text.lower()) if w in WORD_NUMBERS}
    return out


def number_found(n, quotes):
    """A number is found when it, or (for a whole number) its word form, appears in one of the quotes."""
    joined = " ".join(quotes).lower()
    if n in numbers_in(joined):
        return True
    try:
        value = float(n)
    except ValueError:
        return False
    if not value.is_integer():
        return False
    forms = [f for f in (WORDS.get(int(value)), TIMES.get(int(value))) if f]
    return any(re.search(rf"\b{f}\b", joined) for f in forms)


def equivalent_found(phrases, quotes):
    """A listed phrase as whole words, not part of "semi-annually" or "biannually"."""
    joined = " ".join(quotes).lower()
    return any(re.search(rf"(?<![\w-]){re.escape(e)}\b", joined) for e in phrases)


def strength_of(quote):
    """The strictest obligation wording of the quote's main clauses: mandatory / recommended / optional, or None.
    "may not" is a prohibition (mandatory); conditions ("where ... is required,"), relative clauses ("which has
    to ...") and the month May are not obligations."""
    found = []
    for sentence in obligations.sentences(quote):
        if PROHIBITION.search(sentence):
            found.append("mandatory")
            continue
        main = MONTH_MAY.sub(" ", sentence)
        for pattern in NOT_MAIN:
            main = pattern.sub(" ", main)
        word = obligations.strength(main)
        if word:
            found.append({"permissive": "optional"}.get(word, word))
    return max(found, key=RANK.get) if found else None


# a sentence ends at ". " before a capital, but not after a list number or a single letter ("1.", "a.")
SENTENCE_END = re.compile(r"(?<![\d(])(?<!\b[a-zA-Z])[.!?]\s+(?=[A-Z(])")


# a list opens at ":" or a dash right after a word ("shall ensure that—"), but not at a dash between numbers
# ("15–25 °C") or a dash used as a bullet ("; –– staff are trained")
LIST_OPEN = re.compile(r":|(?<=\w)[—–](?![—–]|\s?\d)")
# a list item starts with "(a)", "1.", "ii)", "■" or "•"
_MARKER = r"(?:\(?(?:[a-zA-Z]|[ivxIVX]{1,4}|\d{1,3})[.)]|[■•▪\uf0b7]+|––?)"


def lead_in_strength(quote, text):
    """The strength of the list lead-in a quote sits under, for a list item that has no obligation word of its own:
    "The quality unit should ...: 6. making sure that deviations are investigated" reads recommended. The lead-in is
    the sentence ending at the last list opening (":" or a dash, not a dash between numbers) before the quote, and
    the quote must start a list item: right after the opening, after ";" or ",", or after a list marker ("(a)",
    "11.", "(xi)", "■"); a quote that follows running text ("... review them. The results ...") is not in the list.
    Each occurrence of the quote is tried in turn. None when no lead-in fits or it has no obligation word."""
    text, quote = normalise(text), normalise(quote)
    at = text.find(quote)
    while at >= 0:
        before = text[:at]
        opens = [m.start() for m in LIST_OPEN.finditer(before)]
        if opens:
            tail = before[opens[-1] + 1:]
            starts_item = (not tail.strip() or tail.rstrip()[-1:] in ";,"
                           or re.search(rf"(?:^|\s){_MARKER}\s*$", tail))
            if starts_item:
                lead = before[:opens[-1]]
                ends = [m.end() for m in SENTENCE_END.finditer(lead)]
                return strength_of(lead[ends[-1]:] if ends else lead)
        at = text.find(quote, at + 1)
    return None


def check_requirement(req, sources, changed=()):
    """Findings for one requirement: (requirement id, mapping number or 0, check, message).
    changed: source files whose fingerprint no longer matches the inventory."""
    out = []
    quotes = []
    for n, m in enumerate(req["mappings"], start=1):
        if m["source"] in changed:
            out.append((req["id"], n, "fingerprint", f"{m['source']} changed: re-verify"))
        tree = clauses_of(m["source"])
        clause = tree.get(m["clause_ref"])
        if clause is None:
            out.append((req["id"], n, "clause", f"{m['source']} has no clause {m['clause_ref']!r}"))
            continue
        if hashlib.sha256(clause["text"].encode("utf-8")).hexdigest() != m["clause_sha256"]:
            out.append((req["id"], n, "clause", f"text of {m['clause_ref']} changed since mapping: re-verify"))
        if normalise(m["quote"]) not in normalise(clause["text"]):
            out.append((req["id"], n, "quote", f"quote not found word for word in {m['clause_ref']}"))
        else:
            quotes.append(m["quote"])
        words = strength_of(m["quote"]) or lead_in_strength(m["quote"], clause["text"])
        if words is None:
            out.append((req["id"], n, "strength", "quote has no obligation wording (shall/should/may)"))
        elif words != m["strength"]:
            out.append((req["id"], n, "strength", f"quote reads {words}, mapping says {m['strength']}"))
        scope = plant_scope(sources[m["source"]]["applies_to"])
        if not set(m["plant_types"]) <= scope and not req["general"]:
            out.append((req["id"], n, "scope", f"plant types {sorted(set(m['plant_types']) - scope)} are outside "
                                               f"the scope of {m['source']} ({sources[m['source']]['applies_to']}) "
                                               f"and the requirement is not marked general"))
    for key, value in req["parameters"].items():
        if isinstance(value, bool):
            continue
        if isinstance(value, (int, float)):
            if not (number_found(numbers_key(value), quotes)
                    or equivalent_found(UNIT_EQUIVALENTS.get((key, value), ()), quotes)):
                out.append((req["id"], 0, "numbers", f"parameter {key}={value} is not in any quote"))
        else:
            for n in sorted(numbers_in(str(value), words=True)):
                if not number_found(n, quotes):
                    out.append((req["id"], 0, "numbers", f"parameter {key}: number {n} is not in any quote"))
    texts = [req["item_text"]]
    for n in sorted(set().union(*(numbers_in(t, words=True) for t in texts))):
        if not number_found(n, quotes):
            out.append((req["id"], 0, "numbers", f"number {n} in the item is not in the quote"))
    # a quote not found is already reported
    said = set().union(*(conditions_in(t) for t in texts))
    for n, m in enumerate(req["mappings"], start=1):
        if m["quote"] not in quotes:
            continue
        missing = conditions_missing(m["quote"], said)
        if missing:
            out.append((req["id"], n, "conditions", f"the quote has {', '.join(missing)} wording that the item "
                                                    f"does not state"))
    strengths = [m["strength"] for m in req["mappings"]]
    if strengths and req["strength"] != max(strengths, key=RANK.get):
        out.append((req["id"], 0, "strength", f"item says {req['strength']}, its mapping is "
                                              f"{max(strengths, key=RANK.get)}"))
    covered = set().union(*(set(m["plant_types"]) for m in req["mappings"])) if req["mappings"] else set()
    if not set(req["plant_types"]) <= covered:
        out.append((req["id"], 0, "scope", f"plant types {sorted(set(req['plant_types']) - covered)} have no mapping"))
    return out


def numbers_key(value):
    """12 -> "12", 0.5 -> "0.5", 12.0 -> "12": the form numbers_in gives."""
    return str(int(value)) if float(value).is_integer() else str(value)


def check_coverage(root, reqs):
    """({source stem: (share covered, missing refs)}, findings) for every source with a coverage file.
    An entry must name a clause that exists and live requirements that map that clause."""
    stems = {Path(f).stem: f for f in catalog()}
    by_id = {r["id"]: r for r in reqs}
    shares, findings = {}, []
    for stem, entries in model.coverage(root).items():
        if stem not in stems:
            findings.append((f"coverage {stem}", 0, "coverage", "no such source in sources/catalog.csv"))
            continue
        tree = clauses_of(stems[stem])
        for ref, entry in entries.items():
            where = f"coverage {stem} {ref}"
            if ref not in tree:
                findings.append((where, 0, "coverage", "no such clause"))
            for rid in entry.get("requirements", []):
                req = by_id.get(rid)
                if req is None:
                    continue                                    # reported by model.validate
                if req["status"] == "retired":
                    findings.append((where, 0, "coverage", f"{rid} is retired"))
                elif not any(m["source"] == stems[stem] and m["clause_ref"] == ref for m in req["mappings"]):
                    findings.append((where, 0, "coverage", f"{rid} has no mapping to this clause"))
        refs = [r for r, c in tree.items() if c["kind"] in ("clause", "principle", "section", "table_row")]
        missing = [r for r in refs if r not in entries]
        shares[stem] = ((len(refs) - len(missing)) / len(refs) if refs else 1.0, missing)
    return shares, findings


def uncovered_sources(root):
    """"must" and "should" sources that have no coverage file yet."""
    have = set(model.coverage(root))
    return sorted(f for f, r in catalog().items() if r["priority"] in ("must", "should") and Path(f).stem not in have)


def check_fingerprints():
    rows = read_csv(model.ROOT / "sources" / "inventory.csv")
    bad = []
    for r in rows:
        path = OFFICIAL / r["file"]
        if not path.exists() or hashlib.sha256(path.read_bytes()).hexdigest() != r["sha256"]:
            bad.append(r["file"])
    return bad


def run(root=model.LIBRARY):
    """(findings, coverage shares, fingerprint mismatches)."""
    errors = model.validate(root)
    if errors:
        return [("library", 0, "structure", e) for e in errors], {}, []
    sources = catalog()
    changed = check_fingerprints()
    reqs = model.requirements(root)
    findings = [f for req in reqs if req["status"] != "retired" for f in check_requirement(req, sources, changed)]
    shares, coverage_findings = check_coverage(root, reqs)
    return findings + coverage_findings + check_twins(reqs), shares, changed




def twin_differences(reqs, clauses_of=None):
    """Check 8 (D34, D37): two mapped clauses of different sources with the same words (common.twin_key: leading
    number and punctuation left out; e.g. EU GMP and PIC/S) must give identical items: the same item texts and
    strengths. Near twins that differ in a word ("should" in ICH Q7, "shall" in Schedule M) may differ. Returns
    (from source, ref, to source, ref, from item ids, to item ids) per differing pair."""
    import graph
    clauses_of = clauses_of or globals()["clauses_of"]
    mapped = sorted({(m["source"], m["clause_ref"]) for r in reqs if r["status"] != "retired" for m in r["mappings"]})
    groups = {}
    for s, ref in mapped:
        if ref in (clauses_of(s) or {}):
            groups.setdefault(twin_key(clauses_of(s)[ref]["text"]), []).append((s, ref))
    rows = [("same_text_as", a[0], a[1], b[0], b[1], "1.0") for members in groups.values()
            for i, a in enumerate(members) for b in members[i + 1:] if a[0] != b[0]]
    return graph.consistency(rows, [r for r in reqs if r["status"] != "retired"])


def check_twins(reqs, clauses_of=None):
    """Check 8 findings, one per differing twin pair, named by the lowest item id of the pair."""
    return [(min(ra + rb, key=id_order), 0, "twins", f"{fs} {fr} and {ts} {tr} have the same text but give "
                                                     f"different items {ra} and {rb}")
            for fs, fr, ts, tr, ra, rb in twin_differences(reqs, clauses_of)]


def id_order(rid):
    """"SI-002" < "SI-010" < "SI-1000": by prefix, then number."""
    prefix, _, number = rid.partition("-")
    return (prefix, int(number) if number.isdigit() else 0)


def failing(findings, reqs):
    """The findings that fail the run: all but those on draft or unverified items (twin pairs included when the
    item they are named by is open), which the repair round fixes before Layer 2 may verify them (D37); structure
    and coverage findings always fail. An open item cannot be verified while it has a finding (verify.blocked)."""
    open_items = {r["id"] for r in reqs if r["status"] in ("draft", "unverified")}
    return [f for f in findings if not (f[2] not in ("coverage", "structure") and f[0] in open_items)]


def main():
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else model.LIBRARY
    findings, coverage, fingerprints = run(root)
    for f in findings:
        print(f"{f[0]} mapping {f[1]} [{f[2]}] {f[3]}" if f[1] else f"{f[0]} [{f[2]}] {f[3]}")
    for stem, (share, missing) in coverage.items():
        print(f"coverage {stem}: {share:.1%}" + (f", missing {', '.join(missing[:10])}" if missing else ""))
    for f in fingerprints:
        print(f"fingerprint mismatch: {f}")
    print(f"{len(uncovered_sources(root))} must/should sources have no coverage file yet")
    blocking = failing(findings, model.requirements(root))
    print(f"{len(findings)} findings ({len(findings) - len(blocking)} on draft items, to fix before verification), "
          f"{len(fingerprints)} fingerprint mismatches")
    sys.exit(1 if blocking or fingerprints else 0)


if __name__ == "__main__":
    main()
