# Handover: read this first in every new session

Last updated: 29 October 2026 (session 1).

## Where we are
- Brief: `docs/00-brief.md` (the owner's decisions). Small decisions: `docs/decisions.md`.
- **Deliverable (a), source inventory: done as a draft.** It is in `docs/01-source-inventory.md` and waits for
  owner review.
  - 247 English files are in `sources/official/` (about 87 MB), fingerprinted in `sources/inventory.csv`. What
    could not be fetched is in `sources/missing.tsv`.
  - Collected by three agents (FDA, EU/PIC/S, WHO/ICH/India). Their staging folders were in `work/` (not
    committed).
  - CI runs `python3 tools/inventory.py check` and the unit tests.
- **Deliverables (b)-(d): `docs/02-plan.md`, a draft waiting for owner approval.** Owner questions Q1-Q5 are
  in its section 0: API key and budget, verifier vendors, thresholds, the report-print exception, pilot plant
  types.
- **Next, once approved:** slice S1 (parsers and clause store), then S2. S3 needs the API key (Q1).

## Open with the owner
1. Anvisa RDC 654/2022 (APIs) and the English IN annexes are still wanted (phase 2; captcha, so the owner
   downloads them). The owner uploads files on a branch; we catalogue them and delete the upload branch (D11).

## Facts a new session needs
- Repo: `maglesT/audit-insp-syste` (private). Owner decision D7: regulator-published English translations are allowed.
- The owner's email is triplerascals03@gmail.com. Updates go in Gmail thread id 1a1888c48a563240 (reply with replyThreadId), whose subject starts with
  "Audit:".
- eBMR repo (read-only context): `maglesT/ebmr`. It is not this product. Do not copy its controls blindly.
- Downloads: EC, FDA, eCFR (send `Accept-Encoding`, i.e. `curl --compressed`), ICH, PIC/S (`/docview/<id>`) and
  the WHO CDN all work through the proxy. Three EC files return a bot check; leave those to the owner.
- Commands: `python3 tools/inventory.py write|check`, `python3 -m unittest discover -s tests`.
- Commit trailer: `Co-Authored-By: Claude <noreply@anthropic.com>` plus the session's Claude-Session line. No
  model names.
