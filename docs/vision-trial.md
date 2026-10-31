# Vision drafting trial (D45), 31 October 2026

Run folder: `library/ai-runs/20261031T075617.244703Z-vision-draft/` (`pages.json`, `batches/`, `answers/`,
`items.jsonl`, `report.json`, `verify/`, `verify-report.json`). Tool: `tools/pages/vision.py`; prompts in
`tools/pages/prompts/`. Page images: 150 dpi, pypdfium2 5.13.0, sha256 per page in `pages.json` (images in
`work/vision-pages/`, not in git; re-rendered bit for bit by `vision.render`).

**Set-up.** 10 documents x 5 pages = 50 pages: known hard pages (grade tables, the landscape HVAC table, Q3C
solvent tables, CDSCO checklist pages, superscripts, former parser-defect pages) plus ordinary body pages of the
same documents. 10 drafting agents (one per document, at most 3 at a time), each seeing only its batch: page image,
text layer, next page's text. Verification on a sample of 5 documents (EU Annex 1, WHO TRS 1044 A2, ICH Q3C, CDSCO
circular, FDA CP 7356.002; 236 items), blind verifiers A and B per document (10 agents), each with page images and
text, no drafter notes or check results.

## Results

| Measure | Result |
|---|---|
| Items drafted | 481 from 50 pages (9.6 per page); 236 not-applicable sentences with reasons |
| Quote in BOTH readings (pdftotext and pdfminer), whole tokens in order | **424 of 481 (88 %)**; 5 pdftotext only, 8 pdfminer only, 44 neither (37 of the 57 are table rows) |
| "Text layer differs" list | 70 items: 57 failing one or both readings, 13 more noted by the drafter although both readings match |
| Coverage gaps (obligation sentences not in a quote with their condition words, nor marked n/a) | 28 sentences on 50 pages, to inspect (FDA nitrosamine guidance and PI 011 hold most) |
| Verifier agreement (236 items) | **both correct 223 (94.5 %)**, both incorrect 5, disagree 8 |
| Usage, drafting | about 840 k agent tokens: **about 17 k per page, 1.75 k per item** (text-only drafting in S3: 0.5 k per item) |
| Usage, two verifiers | about 740 k tokens for 236 items: **about 3.1 k per item** (text-only S3: 4.5 k per item) |
| All passes per item | about 4.9 k tokens (text-only S3: about 6-7 k with the reverse test) |

**Per document, quotes failing a reading:** CDSCO 22, WHO 1044 A2 13, PI 011 9, ICH Q3C 6, CP 7356.002 3, Schedule M 2,
EU Annex 1 1, WHO 1010 A8 1, PE 009 Annex 1 0, nitrosamine 2024 0.

**Correction (independent review, 31 Oct):** the first version of the checks matched concatenated letters and table
cells anywhere on the page; the review showed wrong text passing ("15" for "1.5", "≤" for "≥", row C's values
under grade B). The checks now match whole tokens in order and table rows cell by cell within one ruled-table row;
the first report said 92 % (443) pass, the corrected figure is 88 % (424). The drafts and verdicts are unchanged.

## What the misses are
- **Both verifiers incorrect (5): a real drafting error.** ICH Q3C Table 1 rows (Class 1 solvents) drafted as
  plain limits ("Where benzene is used, limit it to 2 ppm") without the page's condition: the limits apply only
  where Class 1 use is unavoidable for a significant therapeutic advance, unless otherwise justified. The
  deterministic condition check cannot see it (the condition is in the lead-in sentence, not the row quote);
  both verifiers did.
- **Disagreements (8):** 6 are verifier B rejecting Q3C Table 2 rows whose quotes leave out a superscript footnote
  marker ("Cumene¹"): a strictness question on footnote marks, not a content error. 2 are EU Annex 1 wording
  points ("all glove surfaces" added; "continuous" added for grade B), each caught by one verifier: genuine
  small over-statements.
- **Quotes failing a reading (57):** table rows whose cells a reading does not keep together (CDSCO landscape
  checklist; grade D rows split over three lines; unruled Q3C rows with a superscript footnote mark), the WHO turned
  side title that pdftotext prints inside body lines (WHO 1044 A2), and footnote marks moved by the text layer
  (PI 011, CP 7356.002). 45 of the 57 are in the verified sample: for 39 both verifiers answered that the quote is
  printed as quoted; for 6 (Q3C rows without their footnote mark) verifier B said not as printed. These are the
  "text layer differs" cases D45 routes to both verifiers and the spot check; the 12 outside the sample are
  unverified.
- **Deterministic findings worth fixing before scaling:** the number check (now both ways) gives 205 findings: table-row
  statements that name a column-header value (0.5 µm) the row quote lacks, and quote numbers the statement drops or
  words differently; table quotes should carry their header
  ("header cells || row cells") or the check should read the table header; strength for checklist rows without a modal verb ("Specify ...",
  "Whether ...") needs a rule (the CDSCO agent chose mandatory for Sch-M rows, recommended for WHO rows).

## Assessment
Vision drafting reads the hard pages correctly where the text layer fails (landscape HVAC table, grade tables,
superscripts, CDSCO checklist); 88 % of quotes pass the strict two-reader check as they are; of the rest, the 45
in the verified sample were confirmed as printed by both verifiers for 39; and the verifiers agree on 94.5 % with one real error class found (a lead-in condition
dropped from table rows). It costs about 3.5 x the drafting tokens of text-only drafting but less per item in
verification, about 4.9 k tokens per item in all.

**Before scaling (proposed):** (1) table-row quotes include the column headers, and the drafter prompt states that a
lead-in condition belongs to every row or list item under it; (2) footnote markers: quote as printed with the
marker in "^" form ("Cumene^1"), so verifiers and checks agree; (3) coverage measure without running headers;
(4) a strength rule for checklist rows without a modal verb (owner question: CDSCO "Specify/Whether" rows);
(5) clause_number only as printed (the drafters composed references such as "Table 2 Note 1": 26 clause findings).
