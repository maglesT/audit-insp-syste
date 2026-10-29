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
- **Plan (b)-(d): APPROVED** (`docs/02-plan.md`; owner decisions D13-D18). There is no API key: AI checking runs as
  Claude Code agents, with Opus for every role (D14, D15). No print or export at all (D16); the R6 compliance gap
  is recorded. NLP is used for deterministic checks and candidate search (D19).
- **S1 (parsers + clause store): in progress.** Branch work merged so far:
  - `tools/parse/numbered.py` handles EudraLex, PIC/S, WHO, ICH and Schedule M: successor-number rule, contents
    detection, section resets, English-page filter.
  - `tools/parse/ecfr.py` handles 21 CFR XML, with paragraph nesting like 211.42(c)(10)(vi).
  - `tools/parse/run.py` writes `library/clauses/*.jsonl` (not committed, D20) and `library/parse-report.md`.
  - `tests/test_parse.py` pins clauses the plan cites.
  - Current result: 120 sources, about 15,100 clauses, **99 flagged** for review. 60 FDA guidance and web files
    are pending.
- **S1 remaining (next session, in this order):**
  1. A heading-based parser for FDA guidance PDFs and fda.gov HTML pages (the 60 pending files).
  2. An article parser for EU legal acts (Directive 2017/1572, Regulation 1252/2014: "Article N").
  3. A Q&A parser for EMA/PIC/S Q&A documents (some parse to 0 clauses today).
  4. Work through the flags in `library/parse-report.md`. Many come from too-strict thresholds: the numbered-share
     limit of 0.80 also catches documents with long intros. Investigate the duplicate refs in Annex 1 (EU and PIC/S
     copies) and the large clauses. Add `sources/parse-overrides` only where a rule cannot be fixed generally.
     Exit: every pilot source is unflagged or has a written explanation in the report.
  5. Then S2: library schema, Layer 1 checker with the NLP pieces (D19), mutation harness, customer export and
     the option-A test.

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
