"""Build library.sqlite from the JSON library, for queries and internal tools (plan section 1).

  python3 tools/library/build.py [library dir] [output file]     # default: library/ -> library/library.sqlite

The database is derived data (like the parsed clauses, D20) and is not committed. It is rebuilt from the JSON files
and refuses to build an invalid library.
"""
import sqlite3
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent))
import model  # noqa: E402

SCHEMA = """
CREATE TABLE topic (id TEXT PRIMARY KEY, name TEXT NOT NULL);
CREATE TABLE requirement (id TEXT PRIMARY KEY, topic TEXT NOT NULL REFERENCES topic(id), item_text TEXT NOT NULL,
    strength TEXT NOT NULL, status TEXT NOT NULL, parameters TEXT NOT NULL, general INTEGER NOT NULL);
CREATE TABLE requirement_plant (requirement TEXT NOT NULL REFERENCES requirement(id), plant_type TEXT NOT NULL,
    PRIMARY KEY (requirement, plant_type));
CREATE TABLE mapping (requirement TEXT NOT NULL REFERENCES requirement(id), n INTEGER NOT NULL, source TEXT NOT NULL,
    clause_ref TEXT NOT NULL, clause_sha256 TEXT NOT NULL, quote TEXT NOT NULL, strength TEXT NOT NULL,
    relation TEXT NOT NULL, plant_types TEXT NOT NULL, addendum TEXT NOT NULL, PRIMARY KEY (requirement, n));
CREATE TABLE coverage (source TEXT NOT NULL, clause_ref TEXT NOT NULL, requirement TEXT, na_reason TEXT);
"""


def build(root=model.LIBRARY, out=None):
    errors = model.validate(root)
    if errors:
        raise ValueError("invalid library:\n" + "\n".join(errors[:20]))
    out = Path(out or Path(root) / "library.sqlite")
    out.unlink(missing_ok=True)
    db = sqlite3.connect(out)
    db.executescript(SCHEMA)
    db.executemany("INSERT INTO topic VALUES (?, ?)", model.topics(root).items())
    import json
    for r in model.requirements(root):
        db.execute("INSERT INTO requirement VALUES (?, ?, ?, ?, ?, ?, ?)",
                   (r["id"], r["topic"], r["item_text"], r["strength"], r["status"], json.dumps(r["parameters"]),
                    int(r["general"])))
        db.executemany("INSERT INTO requirement_plant VALUES (?, ?)", [(r["id"], p) for p in r["plant_types"]])
        for n, m in enumerate(r["mappings"], start=1):
            db.execute("INSERT INTO mapping VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                       (r["id"], n, m["source"], m["clause_ref"], m["clause_sha256"], m["quote"], m["strength"],
                        m["relation"], ",".join(m["plant_types"]), m["addendum"]))
    for stem, clauses in model.coverage(root).items():
        for ref, entry in clauses.items():
            if "na" in entry:
                db.execute("INSERT INTO coverage VALUES (?, ?, NULL, ?)", (stem, ref, entry["na"]))
            for req in entry.get("requirements", []):
                db.execute("INSERT INTO coverage VALUES (?, ?, ?, NULL)", (stem, ref, req))
    db.commit()
    db.close()
    return out


if __name__ == "__main__":
    args = sys.argv[1:]
    print(build(*(Path(a) for a in args)))
