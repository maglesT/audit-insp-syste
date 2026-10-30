"""Layer 1: deterministic checks of every mapping, every run, no AI (plan section 2.4).

  python3 tools/library/layer1.py [library dir]       # prints findings; exit 1 if any check fails

Checks, per mapping:
  1 quote      the quote appears word for word in the cited clause (whitespace-normalised)
  2 clause     the clause reference exists in the parsed clause tree, and its text hash matches clause_sha256
               (a changed source text means "re-verify")
  3 numbers    every number in the item text, the addendum and the parameters appears in one of the quotes
  4 strength   the mapping's strength matches the quote's words (shall/must -> mandatory, should ->
               recommended, may -> optional), and the requirement's strength is the strictest of its mappings
  5 scope      the mapping's plant types are within the source's applies_to (catalog), and the requirement's
               plant types are covered by its mappings
Per library:
  6 coverage   for every source with a coverage file, every citable clause is mapped or marked not applicable
               (reported as a share; missing clauses are listed)
  7 fingerprint every source file matches its sha256 in sources/inventory.csv
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
from common import CITABLE, CLAUSES, OFFICIAL, normalise  # noqa: E402

RANK = {"optional": 0, "recommended": 1, "mandatory": 2}
NUMBER = re.compile(r"(?<![\w.])\d+(?:[.,]\d+)?(?![\w.]*\d)")
WORDS = {1: "one", 2: "two", 3: "three", 4: "four", 5: "five", 6: "six", 7: "seven", 8: "eight", 9: "nine",
         10: "ten", 12: "twelve"}
UNIT_EQUIVALENTS = {("frequency_max_months", 12): ("once a year", "once in a year", "annually", "yearly",
                                                  "every year", "12 months")}


def read_csv(path):
    with open(path, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def catalog():
    return {r["file"]: r for r in read_csv(model.ROOT / "sources" / "catalog.csv")}


def clauses_of(source, cache={}):
    """{ref: clause dict} of a source, from library/clauses (rebuilt by tools/parse/run.py), or parsed on demand."""
    if source not in cache:
        path = CLAUSES / (Path(source).stem + ".jsonl")
        if path.exists():
            rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
        else:
            import run
            row = catalog()[source]
            rows = [c.to_json() for c in run.parser_for(row)(OFFICIAL / source)[0]]
        cache[source] = {c["ref"]: c for c in rows if c["kind"] in CITABLE}
    return cache[source]


def plant_scope(applies_to):
    return set(model.PLANT_TYPES) if applies_to.strip() == "ALL" else set(applies_to.split(";"))


def numbers_in(text):
    return {n.replace(",", ".") for n in NUMBER.findall(text)}


def number_found(n, quotes):
    """A number is found when it, or its word form, appears in one of the quotes."""
    joined = " ".join(quotes).lower()
    if n in numbers_in(joined):
        return True
    try:
        word = WORDS.get(int(float(n)))
    except ValueError:
        word = None
    return bool(word) and re.search(rf"\b{word}\b", joined) is not None


def strength_of(quote):
    """The strictest obligation wording in the quote: mandatory / recommended / optional, or None."""
    found = [obligations.strength(s) for s in obligations.sentences(quote)]
    mapping = {"mandatory": "mandatory", "recommended": "recommended", "permissive": "optional"}
    ranked = [mapping[f] for f in found if f]
    return max(ranked, key=RANK.get) if ranked else None


def check_requirement(req, sources):
    """Findings for one requirement: (requirement id, mapping number or 0, check, message)."""
    out = []
    quotes = []
    for n, m in enumerate(req["mappings"], start=1):
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
        words = strength_of(m["quote"])
        if words is None:
            out.append((req["id"], n, "strength", "quote has no obligation wording (shall/should/may)"))
        elif words != m["strength"]:
            out.append((req["id"], n, "strength", f"quote reads {words}, mapping says {m['strength']}"))
        scope = plant_scope(sources[m["source"]]["applies_to"])
        if not set(m["plant_types"]) <= scope:
            out.append((req["id"], n, "scope", f"plant types {sorted(set(m['plant_types']) - scope)} are outside "
                                               f"the scope of {m['source']} ({sources[m['source']]['applies_to']})"))
    texts = [req["item_text"]] + [m["addendum"] for m in req["mappings"]]
    wanted = set().union(*(numbers_in(t) for t in texts))
    for key, value in req["parameters"].items():
        if isinstance(value, (int, float)):
            equivalents = UNIT_EQUIVALENTS.get((key, value), ())
            if not (number_found(str(value), quotes) or any(e in " ".join(quotes).lower() for e in equivalents)):
                out.append((req["id"], 0, "numbers", f"parameter {key}={value} is not in any quote"))
    for n in sorted(wanted):
        if not number_found(n, quotes):
            out.append((req["id"], 0, "numbers", f"number {n} in the item or an addendum is not in any quote"))
    strengths = [m["strength"] for m in req["mappings"]]
    if strengths and req["strength"] != max(strengths, key=RANK.get):
        out.append((req["id"], 0, "strength", f"requirement says {req['strength']}, strictest mapping is "
                                              f"{max(strengths, key=RANK.get)}"))
    covered = set().union(*(set(m["plant_types"]) for m in req["mappings"])) if req["mappings"] else set()
    if not set(req["plant_types"]) <= covered:
        out.append((req["id"], 0, "scope", f"plant types {sorted(set(req['plant_types']) - covered)} have no mapping"))
    return out


def check_coverage(root):
    """{source stem: (share covered, missing refs)} for every source with a coverage file."""
    stems = {Path(f).stem: f for f in catalog()}
    out = {}
    for stem, entries in model.coverage(root).items():
        tree = clauses_of(stems[stem]) if stem in stems else {}
        refs = [r for r, c in tree.items() if c["kind"] in ("clause", "principle", "section", "table_row")]
        missing = [r for r in refs if r not in entries]
        out[stem] = ((len(refs) - len(missing)) / len(refs) if refs else 1.0, missing)
    return out


def check_fingerprints():
    rows = read_csv(model.ROOT / "sources" / "inventory.csv")
    key = next(k for k in rows[0] if "sha" in k.lower())
    bad = []
    for r in rows:
        path = OFFICIAL / r["file"]
        if not path.exists() or hashlib.sha256(path.read_bytes()).hexdigest() != r[key]:
            bad.append(r["file"])
    return bad


def run(root=model.LIBRARY):
    errors = model.validate(root)
    if errors:
        return [("library", 0, "structure", e) for e in errors], {}, []
    sources = catalog()
    findings = [f for req in model.requirements(root) if req["status"] != "retired"
                for f in check_requirement(req, sources)]
    return findings, check_coverage(root), check_fingerprints()


def main():
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else model.LIBRARY
    findings, coverage, fingerprints = run(root)
    for f in findings:
        print(f"{f[0]} mapping {f[1]} [{f[2]}] {f[3]}" if f[1] else f"{f[0]} [{f[2]}] {f[3]}")
    for stem, (share, missing) in coverage.items():
        print(f"coverage {stem}: {share:.1%}" + (f", missing {', '.join(missing[:10])}" if missing else ""))
    for f in fingerprints:
        print(f"fingerprint mismatch: {f}")
    print(f"{len(findings)} findings, {len(fingerprints)} fingerprint mismatches")
    sys.exit(1 if findings or fingerprints else 0)


if __name__ == "__main__":
    main()
