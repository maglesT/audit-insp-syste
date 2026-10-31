# FDA HTML profile: trial on 20 units (31 Oct 2026, D47 D / D49)

Profile: `tools/fda/htmlprofile.py` (the page text is read directly from `sources/official/*.html` by
`tools/parse/fdahtml.py`; no rendering, no vision). Prompts: `tools/fda/prompts/draft_html.md`,
`verify_html_a.md`, `verify_html_b.md`. Tests: `tests/test_fda_html.py`.

## Units and references
- Q&A pages: one unit per question ("Q4"); the question is paragraph "Q4", its answer blocks "Q4.1", "Q4.2", ...
  The question index, each answer's reference list and date, and the page chrome are left out.
- Other pages (Guides to Inspections, ITGs, CPG, alert): paragraphs "¶n" in page order; units are runs of about
  5,000 characters ("¶9-¶17"). The clause shown is the Q&A number, or the paragraph with its heading path. Several
  ORA guides print a heading after its text in the HTML (cleaning validation: "I INTRODUCTION ... IV" sit as a list
  after section III's text), so the paragraph number is the locator and the heading path is context only.
- A list item takes the condition of the paragraph ending ":" above it (lead-in check, D46/D48).

## Trial set (20 units, 5 documents)
| Run | Document | Units | Items | Quotes exact | Findings | Gaps | Auto | Review |
|---|---|---|---|---|---|---|---|---|
| `20261031T115746.029428Z-html-draft` | CGMP Q&A: Equipment (whole page) | 13 | 54 | 54 | 1 | 3 | 49 | 5 |
| `20261031T115746.134947Z-html-draft` | Guide: Validation of Cleaning Processes ¶9-¶26 | 2 | 33 | 33 | 0 | 0 | 31 | 2 |
| `20261031T115746.225475Z-html-draft` | CPG 490.200 parametric release ¶12-¶34 | 2 | 33 | 33 | 3 | 1 | 29 | 4 |
| `20261031T115746.327942Z-html-draft` | ITG: Water for Pharmaceutical Use (whole page) | 2 | 24 | 24 | 4 | 1 | 18 | 6 |
| `20261031T115746.450821Z-html-draft` | Benzene alert ¶8-¶18 | 1 | 16 | 16 | 1 | 0 | 13 | 3 |
| **Total** | | **20** | **160** | **160 (100 %)** | 9 | 5 | **140 (87.5 %)** | **20** |

Verifiers (blind, A starts from the item, B from the text): both correct 140 of 160; both incorrect 3; disagree 12
(A incorrect 7, B incorrect 5). Usage (agent totals): drafting about 365 k tokens, verifying about 437 k; about
5 k tokens per item.

## Tuning done on the trial (checks only; prompts unchanged after drafting)
- "may not be adequate", "may be more difficult": a possibility, not a prohibition or permission (2 strength
  findings gone).
- "may be made only by": a restriction, read as mandatory.
- "determine if ...", "check if ...": an indirect question, not a condition (1 conditions finding gone).
- "provided the ..." counts as the condition word "provided that" in a statement.
- Regulation references as chains ("21 CFR 211.186 and 211.188", "(21 CFR 211.113(b))") are not numbers.
- "+/-0.5°C" read as "± 0.5°C" (the number check missed it).
- Plant scope: "probability of a non-sterile unit" and "(other than water intended to be sterile)" do not limit
  the text to non-sterile or sterile products.

## What the verifiers caught (examples)
- Q11#1 (both): the statement adds a second instruction the quote does not state.
- Q13#1, #3 (A): WFI piping text applied to OSD/LIQ/SEMI plants.
- Benzene ¶17 (B, and the numbers check): "this level" replaced by a vague "acceptable level"; the statement also
  carries 2 ppm / 10 g / 20 from the paragraph before, which the numbers check flags.
- ITG water ¶1-¶16#15 (both): "generally not acceptable" turned into an absolute prohibition.
- CPG ¶12-¶21#3 (both): "in-process" added.

## Residual and next steps
- 5 coverage gaps: sentences split over two items or with a non-obligation lead clause ("The purpose of cleaning
  validation is ...; the sampling ... should be ..."); a redraft run handles them (`prepare-redraft`).
- Review queue: 20 items, through `tools/fda/review.py` (now reads HTML items: source text, corrected quotes).
- Full build: document by document in work-list order (9 CGMP Q&A pages, Guides to Inspections, ITGs, CPG
  490.200, benzene alert). Whole-document runs from the trial (Q&A Equipment, ITG Water) count as builds after the
  redraft of their gaps.

## Review fixes (independent review of PR #42)
- Coverage: an item covers only its own paragraph, the paragraphs its quote really runs into, and (for a list
  item) its lead-in; before, any item citing an earlier paragraph in the unit counted (18 sentences hidden in a
  probe).
- Units never start at a list item, so a list stays with its lead-in (CPG ¶21/¶22, ITG lyophilization ¶9/¶10, ...).
- A quote must take at least 3 of its tokens (or all) from its cited paragraph and does not run across a heading.
- "may not be removed" stays a prohibition (only "may not be adequate / sufficient / ..." is a possibility);
  "may be only a milligram" is no restriction; references no longer swallow a following number ("211.166, 30 days").
- Q&A "Back to Top", "Date Revised 6/18/2015", "CDER Key Officials" are not citable (they keep their number, so
  references stay stable). The review queue shows the unit's text for an item citing an unknown paragraph.
- Effect on the documents already built (Q&A Equipment, Buildings and Facilities, General Provisions): none (same
  gaps, same route); the trial's guide runs (cleaning validation, CPG, ITG water, benzene) are trial-only, their
  documents are built whole in new runs.
