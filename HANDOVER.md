# Handover: read this first in every new session

Last updated: 30 October 2026 (session 3, pilot run).

## Pilot results (30 Oct 2026, D29)
Run folders: `library/ai-runs/20261030T074231.724549Z-pilot-draft/` and `.../20261030T074433.157454Z-pilot-verify/`
(the report is `pilot-report.json` in the verify folder). Prompts and budget unchanged (`--budget 15`). Both batches
finished in about 4 minutes in total.
- **Cost:** US$0.73 in total (drafting US$0.14, verification US$0.59), **US$0.0125 per mapping** (drafting plus both
  verifiers). Output tokens dominate: 38,305 output tokens against 157,659 input tokens (cached and uncached).
- **Counts:** 24 clauses -> **58 mappings**; **0 rejected quotes**; **0 failed calls** (24 + 116 requests, all
  `end_turn`); 0 mappings left unverified for budget.
- **Verifiers:** both correct **43**; both incorrect **5**; disagree **10** (A incorrect / B correct 9, the reverse 1).
  The 5 both-incorrect are all items that keep one half of a clause and drop the half that the clause treats as one
  requirement (WHO 8.5 and Schedule M 10.5: report on completion vs report contents; WHO 8.9 and Schedule M 10.8.2:
  supplier evaluation without its criteria; Schedule M 10.4: annual minimum without "stated in the procedure").
- **Pattern in the disagreements:** nearly all are the same split question. When the drafter splits a clause into
  several items, verifier A judges each item against the whole clause and calls it "looser". Verifier B accepts it
  because the other parts are "separate obligations" for other items. This is a granularity rule the prompts leave
  open, not a factual error. It belongs to adjudication or a prompt decision for the owner. Examples:
  1. *EU Ch 9 9.3*, item "Keep a record of every self inspection performed." A: incorrect, it leaves out what the
     record should contain (observations, corrective proposals, follow-up), so it is looser. B: correct, it reflects
     the first sentence, and report content and follow-up are separate obligations for their own items.
  2. *Schedule M Part I 10.4*, item "The self-inspection procedure must state how often self-inspections are carried
     out." A: incorrect, it drops the at-least-once-a-year minimum, so the stated frequency could be less than annual.
     B: correct, the clause's "stated in the procedure" is captured exactly, and the annual minimum is a distinct
     obligation for another item.
  3. *WHO TRS 986 8.5* (the one reverse case), item "The self-inspection report should include the results ... and
     the recommended corrective actions." A: correct, it matches the three report contents, strength and plant types.
     B: incorrect, it presupposes a report and drops the duty to make one at the completion of each self-inspection.
     Note that verifier A treated the same split in Schedule M 10.5 as incorrect, so A is not fully consistent either.
- **For pricing the full run:** at about 2.4 mappings per clause and US$0.0125 per mapping, that is about US$0.03 per
  clause, before adjudication of disagreements (17 % here).
- **Model names in the run folders:** `requests.jsonl`, `batch.json` and `summary.json` record the model ID that was
  sent to the API. They were committed unchanged, because the audit trail must hold the exact requests (D29).
  Owner to confirm this is acceptable under the "no model name in the repo" rule (that rule was written for
  attribution).

## Where we are
- **Latest (30 Oct 2026), read first:**
  - S1 done (PRs #11-#15). S2 part 1 merged (PR #16): library format (`tools/library/model.py`,
    `library/topics.json`), SQLite build, and the Layer 1 checker (`tools/library/layer1.py`, in CI; D28).
  - **AI checking now runs through the Claude API (D29, replaces D14).** `tools/ai/runner.py` (Batch API, cached
    instructions, JSON-schema answers, audit trail in `library/ai-runs/`) and `tools/ai/pilot.py` (paid pilot,
    24 self-inspection clauses, hard budget US$15). The key is the environment variable `AUDIT_ANTHROPIC_KEY`, set in the
    cloud environment's settings (Claude Code strips `ANTHROPIC_API_KEY` from sessions), never in the repo or the chat. The paid pilot has run (see "Pilot results"
    below); next: report the cost per mapping to the owner and price the full run.
  - Still to do in S2: mutation harness, customer export with the option-A test, candidate search (BM25 +
    embeddings, D21).
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
  - Current result: 120 sources, about 15,900 clauses, **94 flagged** for review. 60 FDA guidance and web files
    are pending.
  - **NLP safety net (owner request, D19), so a requirement cannot go missing even when the structure is misread:**
    - `tools/parse/obligations.py` lists every obligation sentence (shall/must/should/may, plus the numbers in
      it): about 27,400 across 120 sources.
    - `tools/parse/crosscheck.py` re-reads each PDF independently (`pdftotext -raw`) and reports obligation
      sentences missing from the parsed clauses. Today there are 211 possible misses (0.8 %). Most are tables
      (PIC/S PI 058 interpretation table, Q&A tables, aide-memoires, CDSCO checklists), where layout and raw
      extraction order the columns differently. Next step: table-aware extraction for those documents, e.g. one
      clause per table row with pdfplumber or pdftotext -bbox.
    - S2/S3 rule: every obligation sentence must end up covered by a mapping or marked not applicable. This is
      the completeness check that does not rely on the numbering.
  - One review pass is done (5 defects, all fixed with tests): contents detection, decimal rule, leading zeros,
    header/footer removal (now page edges only, with dropped text counted), and eCFR inline paragraphs plus
    roman-vs-letter (i).
- **Session 2, done: table-aware extraction (D22, D23).** `tools/parse/tables.py` (pdfplumber cell boxes + poppler
  words) gives one clause per table row (`Table <k> <label>`, kind `table_row`, `parent` = enclosing clause) for every
  non-FDA PDF; text around tables is still `pdftotext -layout`. Cross-check fallback: on table pages a sentence counts
  as found when all its words are in one row. Also fixed: WHO side header and India gazette header inside clause text;
  mixed Hindi/English gazette pages. Result: 19,465 clauses, possible misses **211 -> 19** (remaining: figure and
  flowchart text in PE 009 annexes, Q1E, Q9, WHO TRS 957/1044; Drugs Rules footnotes; one PI 030 row without a bottom
  rule; PI 041 8.8 and PI 038 3.3, to look at in the flags step). Full run takes about 9 minutes.
- **Session 2, done: FDA parsers (D24).** `tools/parse/headings.py` parses FDA guidance and compliance-program PDFs by
  section, guided by each document's own contents list ("IV.B.2", "Part III 3.A"); `tools/parse/fdahtml.py` parses
  fda.gov pages (Q&A pages -> "Q7"; other pages -> "¶12"). All 59 FDA files parse; 179 sources in the report, only
  `ema-gmp-gdp-qa.html` pending (Q&A parser).
- **Session 2, done: article, Q&A and EMA-page parsers (D25).** `articles.py` (EU Directive 2017/1572, Regulation
  1252/2014: "Recital (7)", "Article 4(2)(a)"; OJ footnotes and the annex kept out), `qa.py` ("Q7" per question),
  `emahtml.py` (EMA GMP/GDP Q&A page: "<topic> Q<n>", 129 questions). `run.text_parser` picks the numbered parser
  unless Q&A/articles fit clearly better (usable share: unique refs, clauses <= 4,000 characters); today it switches
  exactly 6 documents (EMA HBEL Q&A, EMA microbial Q&A, PIC/S PI 053, EMA nitrosamines Q&A, the two EU acts).
  No source is pending any more.
- **Session 2, done: parse-report flags (D26). S1 exit criterion met:** every flagged source has a written explanation
  in `library/parse-explanations.csv` (`run.py --report` re-renders the report without parsing). 180 sources, 22,831
  clauses, 59 flagged, 0 unexplained, 20 possible misses (figure text). Fixed in general: unique references
  (`common.resolve_duplicates`: contents copies -> toc, real restarts "#2" + note), contents lines no longer open
  appendix sections, stray numbers (footnotes, list items, running headers, wrapped lines) are taken back when the old
  numbering resumes, title-case chapters after subsections, glossaries and annex/appendix intro text are citable
  sections, cover dates, eCFR deep levels and italic definitions, FDA appendices/attachments.
- **Session 2, done: S1 tail (D27).** Known parser limitations 22 -> 10: chapters without sub-numbers (WHO HVAC,
  QRM, EU MAH paper, EU Annex 11), unnumbered trailing annexes and back matter, prefixed numbering ("B 1.1", "I.1",
  "A.1"), margin line numbers (EU Annex 17), wrapped lower-case lines, a heading that replaces a list item with its
  number (Q1B), table rows sharing one ruled cell (PI 038), an FDA level below the contents list (III.B.1) and appendix
  sections. 180 sources, 22,783 clauses (reference-list entries are no longer clauses), 51 flagged (all explained).
- **Remaining limitations (10, text kept, reference coarse):** WFI Q&A Part II list, PI 011 sections 27-29, PI 041
  numbered table rows, PI 030 open table row, PE 009 Annex 2A B 3.3 tail and Annex 3 typo "14..", Drugs Rules form
  items, WHO AMR quoted clauses, CP 7356.002a Attachment A in the page header, WHO TTSP bibliography. They can be
  fixed alongside S2 if mapping needs them.
- **Then S2:** library schema, Layer 1 checker with the NLP pieces (D19), BM25 plus a pinned embedding model for
  candidate search (D21), mutation harness, customer export and the option-A test.

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
