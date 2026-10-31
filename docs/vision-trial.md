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
| Quote in BOTH readings (pdftotext and pdfminer) | **443 of 481 (92 %)**; 5 pdftotext only, 17 pdfminer only, 16 neither |
| "Text layer differs" list | 63 items: 38 failing one or both readings, 25 more noted by the drafter although both readings match |
| Coverage gaps (obligation sentences not in a quote nor marked n/a) | 30 sentences on 50 pages; most are measurement artefacts (running headers glued to the sentence push it under the 80 % rule); a few real (FDA nitrosamine guidance 10, PI 011 7: to inspect) |
| Verifier agreement (236 items) | **both correct 223 (94.5 %)**, both incorrect 5, disagree 8 |
| Usage, drafting | about 840 k agent tokens: **about 17 k per page, 1.75 k per item** (text-only drafting in S3: 0.5 k per item) |
| Usage, two verifiers | about 740 k tokens for 236 items: **about 3.1 k per item** (text-only S3: 4.5 k per item) |
| All passes per item | about 4.9 k tokens (text-only S3: about 6-7 k with the reverse test) |

**Per document, quotes in both readings:** EU Annex 1 74/76, PE 009 Annex 1 74/75, WHO 1044 A2 59/64, WHO 1010 A8
(landscape) 21/22, ICH Q3C 46/46, CDSCO 12/32, CP 7356.002 15/18, nitrosamine 2024 11/11, Schedule M 91/93,
PI 011 40/44.

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
- **Quotes failing a reading (38):** table rows whose cells a reading interleaves with the neighbouring column
  (CDSCO landscape checklist: 20 of 32; the cell texts of ruled tables fix part of it), superscript footnote
  markers flattened into the word ("Cumene1"), and grade D rows split over three lines. In each case the image
  shows the true text; these are exactly the "text layer differs" cases D45 routes to both verifiers and the spot
  check. 30 of the 38 are in the verified sample, and for all 30 both verifiers answered that the quote is
  printed on the page as quoted (verifier B's 6 footnote-mark rejections are verdicts, with quote_as_printed true).
- **Deterministic findings worth fixing before scaling:** the number check flags table-row items whose statement
  names a column-header value (0.5 µm) that the row quote lacks (124): table quotes should carry their header
  ("header cells || row cells") or the check should read the table header; the coverage measure should drop
  running headers before the 80 % rule; strength for checklist rows without a modal verb ("Specify ...",
  "Whether ...") needs a rule (the CDSCO agent chose mandatory for Sch-M rows, recommended for WHO rows).

## Assessment
Vision drafting reads the hard pages correctly where the text layer fails (landscape HVAC table, grade tables,
superscripts, CDSCO checklist), 92 % of quotes pass the two-reader check as they are, the rest are explained
image-true readings, and the verifiers agree on 94.5 % with one real error class found (a lead-in condition
dropped from table rows). It costs about 3.5 x the drafting tokens of text-only drafting but less per item in
verification, about 4.9 k tokens per item in all.

**Before scaling (proposed):** (1) table-row quotes include the column headers, and the drafter prompt states that a
lead-in condition belongs to every row or list item under it; (2) footnote markers: quote as printed with the
marker in "^" form ("Cumene^1"), so verifiers and checks agree; (3) coverage measure without running headers;
(4) a strength rule for checklist rows without a modal verb (owner question: CDSCO "Specify/Whether" rows).
