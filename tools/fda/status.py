"""FDA build status (D47): library/fda-status.json and the document's row in docs/fda-worklist.md.

  python3 tools/fda/status.py set FILE STATUS [--items N --auto N --review N --usage K --run RUN --note TEXT]
  python3 tools/fda/status.py show

docs/fda-worklist.md is the coordinating session's file: only the Status / Items / Auto / Review cells of the row
whose File cell is FILE are changed; its format is kept. Usage (k tokens), run folders and notes live in the JSON.
"""
import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STATUS = ROOT / "library" / "fda-status.json"
WORKLIST = ROOT / "docs" / "fda-worklist.md"
STATES = ("not started", "drafted", "verified", "in review", "done")


def load(path=STATUS):
    return json.loads(path.read_text()) if path.exists() else {"documents": {}}


def update_row(md, file, status, items="", auto="", review=""):
    """md with the row of FILE given new Status / Items / Auto / Review cells (the last four columns)."""
    out, hit = [], False
    for line in md.splitlines():
        cells = line.split("|")
        if line.startswith("|") and len(cells) >= 6 and f"`{file}`" in line:
            cells[-5:-1] = [f" {status} ", f" {items} ", f" {auto} ", f" {review} "]
            line, hit = "|".join(cells), True
        out.append(line)
    if not hit:
        raise SystemExit(f"{file} is not in the work list")
    return "\n".join(out) + ("\n" if md.endswith("\n") else "")


def set_status(file, status, items=None, auto=None, review=None, usage=None, run=None, note=None,
               path=STATUS, worklist=WORKLIST):
    if status not in STATES and not status.startswith(STATES):
        raise SystemExit(f"status must start with one of {STATES}")
    doc = load(path)
    rec = doc["documents"].setdefault(file, {})
    rec.update({k: v for k, v in {"status": status, "items": items, "auto": auto, "review": review,
                                  "usage_k_tokens": usage, "note": note}.items() if v is not None})
    if run:
        rec.setdefault("runs", [])
        if run not in rec["runs"]:
            rec["runs"].append(run)
    rec["updated"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    path.write_text(json.dumps(doc, indent=1, ensure_ascii=False) + "\n")
    worklist.write_text(update_row(worklist.read_text(), file, status, *("" if rec.get(k) is None else rec[k]
                                                                         for k in ("items", "auto", "review"))))
    return rec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["set", "show"])
    ap.add_argument("file", nargs="?")
    ap.add_argument("status", nargs="?")
    for k in ("items", "auto", "review", "usage"):
        ap.add_argument(f"--{k}", type=int)
    ap.add_argument("--run")
    ap.add_argument("--note")
    a = ap.parse_args()
    if a.cmd == "show":
        print(json.dumps(load(), indent=1, ensure_ascii=False))
    else:
        print(set_status(a.file, a.status, a.items, a.auto, a.review, a.usage, a.run, a.note))


if __name__ == "__main__":
    main()
