# Handover: read this first in every new session

Last updated: 29 October 2026 (session 1).

## Where we are
- Brief: `docs/00-brief.md` (the owner's decisions). Small decisions: `docs/decisions.md`.
- **Deliverable (a), source inventory: done as a draft.** It is in `docs/01-source-inventory.md` and waits for
  owner review.
  - 37 official English files are in `sources/official/`, fingerprinted in `sources/inventory.csv`.
  - CI runs `python3 tools/inventory.py check` and the unit tests.
- **Next:** deliverables (b) library data model + verification pipeline with release thresholds, (c) customer app
  scope + minimum compliance rules, (d) slices with a token/time estimate per regulator. Show all three to the
  owner together for approval, then build the pilot.

## Open with the owner
1. The repo name. Until the owner gives it, work stays local in `/home/user/gmp-audit`; once known, attach it
   with `add_repo` (push) and push `main`.
2. Optional: three EU PDFs behind a bot check (Annex 19 old and 2026 act, Glossary). See section "Still needed"
   in `docs/01-source-inventory.md`.

## Facts a new session needs
- The owner's email is triplerascals03@gmail.com. Updates go in the Gmail thread whose subject starts with
  "Audit:".
- eBMR repo (read-only context): `maglesT/ebmr`. It is not this product. Do not copy its controls blindly.
- Downloads: EC, FDA, eCFR (send `Accept-Encoding`, i.e. `curl --compressed`), ICH, PIC/S (`/docview/<id>`) and
  the WHO CDN all work through the proxy. Three EC files return a bot check; leave those to the owner.
- Commands: `python3 tools/inventory.py write|check`, `python3 -m unittest discover -s tests`.
- Commit trailer: `Co-Authored-By: Claude <noreply@anthropic.com>` plus the session's Claude-Session line. No
  model names.
