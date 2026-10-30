# Handover: read this first in every new session

Last updated: 30 October 2026 (session 2, S1 tail branch).

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
