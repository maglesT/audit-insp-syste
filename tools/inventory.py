"""Source inventory and fingerprint check (verification layer 1, no AI).

Usage:
  python3 tools/inventory.py write   # (re)compute sources/inventory.csv
  python3 tools/inventory.py check   # fail if any file is uncatalogued, missing,
                                     # unextractable, or its sha256 changed

A changed sha256 means the official text changed: every item citing that source
must be re-verified before release.
"""
import csv
import hashlib
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OFFICIAL = ROOT / "sources" / "official"
CATALOG = ROOT / "sources" / "catalog.csv"
URLS = ROOT / "sources" / "urls.tsv"
INVENTORY = ROOT / "sources" / "inventory.csv"
FIELDS = ["file", "regulator", "title", "version", "applies_to", "pilot_role", "source_class",
          "url", "sha256", "bytes", "pages", "text_chars"]
MIN_CHARS_PER_PAGE = 200  # below this the PDF is probably scanned and needs OCR


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def pdf_pages(path):
    out = subprocess.run(["pdfinfo", str(path)], capture_output=True, text=True, check=True).stdout
    for line in out.splitlines():
        if line.startswith("Pages:"):
            return int(line.split()[1])
    raise ValueError(f"no page count for {path.name}")


def text_chars(path):
    if path.suffix == ".pdf":
        text = subprocess.run(["pdftotext", "-layout", str(path), "-"],
                              capture_output=True, text=True, check=True).stdout
    else:
        text = path.read_text(encoding="utf-8")
    return len("".join(text.split()))


def load_catalog():
    with open(CATALOG, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def load_urls():
    urls = {}
    for line in URLS.read_text(encoding="utf-8").splitlines():
        if line.strip():
            name, url = line.split("\t", 1)
            urls[name] = url
    return urls


def build_rows(official=OFFICIAL):
    urls = load_urls()
    rows = []
    for entry in load_catalog():
        path = official / entry["file"]
        pages = pdf_pages(path) if path.suffix == ".pdf" else ""
        rows.append({**entry, "url": urls.get(entry["file"], ""), "sha256": sha256(path),
                     "bytes": path.stat().st_size, "pages": pages, "text_chars": text_chars(path)})
    return rows


def problems(official=OFFICIAL, inventory=INVENTORY):
    """Return a list of human-readable problems; empty means the sources are intact."""
    found = []
    catalog = {e["file"]: e for e in load_catalog()}
    on_disk = {p.name for p in official.iterdir() if p.is_file()}
    urls = load_urls()
    for name in sorted(on_disk - catalog.keys()):
        found.append(f"uncatalogued file: {name}")
    for name in sorted(catalog.keys() - on_disk):
        found.append(f"catalogued file missing: {name}")
    for name in sorted(catalog.keys() & on_disk):
        if name not in urls:
            found.append(f"no official URL recorded: {name}")
    recorded = {}
    if inventory.exists():
        with open(inventory, newline="", encoding="utf-8") as f:
            recorded = {r["file"]: r for r in csv.DictReader(f)}
    for name in sorted(catalog.keys() & on_disk):
        path = official / name
        if name not in recorded:
            found.append(f"not in inventory (run write): {name}")
        elif recorded[name]["sha256"] != sha256(path):
            found.append(f"sha256 changed, re-verify all items citing: {name}")
        if path.suffix == ".pdf":
            pages = pdf_pages(path)
            if text_chars(path) < MIN_CHARS_PER_PAGE * pages:
                found.append(f"too little extractable text (scanned?): {name}")
    return found


def main(argv):
    if argv[1:] == ["write"]:
        rows = build_rows()
        with open(INVENTORY, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=FIELDS)
            w.writeheader()
            w.writerows(rows)
        print(f"wrote {len(rows)} sources to {INVENTORY.relative_to(ROOT)}")
        return 0
    if argv[1:] == ["check"]:
        found = problems()
        for p in found:
            print(p)
        print("sources OK" if not found else f"{len(found)} problem(s)")
        return 1 if found else 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
