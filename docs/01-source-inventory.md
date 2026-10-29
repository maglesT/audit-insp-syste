# Deliverable (a): Source inventory, pilot

Status: draft for owner review, 29 October 2026.
Machine-readable record: `sources/catalog.csv` (what each file is) + `sources/urls.tsv` (where it came from)
→ `sources/inventory.csv` (sha256, bytes, pages, extractable characters), produced by `tools/inventory.py write`.
`tools/inventory.py check` runs in CI and fails if any official file changes, goes missing or is uncatalogued.

All files were downloaded on 29 October 2026 directly from the regulators' own sites (no third-party copies).
The eBMR extracts were not reused: every text will be re-extracted from these PDFs with `pdftotext -layout`.
The Schedule M gazette PDF is byte-identical to the eBMR copy (sha256 `918704…d271`).

## What we have (237 files, 29 October 2026)

Scope rule (owner, D9): every in-scope GMP guideline of each pilot body. That means binding rules, final guidances,
supplementary annexes, and the inspectors' own aides. Priority `must` = binding or what inspectors work from;
`should` = final guidance that tightens a topic; `reference` = drafts and development-only guidelines, tracked but
not turned into items until final.

| Body | Files | must / should / reference | Highlights |
|---|---|---|---|
| US FDA | 100 | 38 / 29 / 33 | 21 CFR 210, 211, 11, 4, 7, 200, 201, 207, 314.70, 314.81 (eCFR XML); all final CGMP guidances in scope; 12 ORA Guides to Inspections, 9 Inspection Technical Guides, Compliance Programs 7356.002 / 002A / 002F; CGMP Q&A pages (32 files are fda.gov web pages, which have no PDF) |
| EU (Commission) | 24 | 15 / 5 / 4 | EudraLex Vol 4 Part I, Part II, Annexes 1, 8, 9, 11, 15, 16, 17, 21, Part III; draft revisions marked reference |
| EMA | 11 | 7 / 2 / 2 | HBEL guideline and Q&A, sterilisation guideline, water quality guideline, process validation (finished products), GMP/GDP Q&A, Q&A on microbial contamination of non-sterile products (July 2026) |
| PIC/S | 29 | 14 / 9 / 6 | PE 009-18 (Sept 2026); PI 041 data integrity; inspection aide-memoires; PI 006-4 validation (Oct 2026); PI 058-1 interpretation of Annex 1 (Oct 2026); PI 045/047 (same texts as the EU excipients/GDP-API guidelines) |
| WHO | 33 | 15 / 15 / 3 | TRS main, sterile and API GMP; water, HVAC, data integrity, chromatography, QC labs (TRS 1052 A4), microbiology labs, hazardous substances, HBEL, QRM, technology transfer, storage/distribution, sampling, excipients (TRS 1060 A3); currency checked against TRS 1067 A1 |
| ICH | 25 | 7 / 11 / 7 | Q7 + Q&A, Q9(R1), Q10; Q1A-E, Q2(R2), Q14, Q3A-D, M7, Q6A, Q8(R2), Q11 (+Q&A), Q12, Q13 |
| India | 9 | 4 / 2 / 3 | Revised Schedule M (G.S.R. 922(E)) + corrigendum G.S.R. 666(E); Drugs Rules 1945 as compiled by CDSCO (to 1 Jul 2024: Schedule L-1, conditions of licence); timeline notices |
| Japan (phase 2) | 6 | 3 / 3 / 0 | PMDA's own English translations (D7): GMP Ordinance 179, PIC/S adoption notice + Q&A, computerized systems guideline + Q&A, aseptic processing guidance |

All PDFs have an extractable text layer (`tools/inventory.py check` enforces this).

## Still needed: `sources/missing.tsv` (29 rows)

**From the owner** (these sites block automated downloads; we do not get around that):
1. **EUR-Lex**: Directive (EU) 2017/1572 and Regulation (EU) 1252/2014 (both `must`, the EU's binding GMP law);
   excipient risk-assessment and API-GDP guidelines (we hold the identical PIC/S texts).
2. **EC health site**: Annex 19 + its 2026 revision act, Glossary, written-confirmation template.
3. **EMA**: nitrosamines Q&A for MAHs.
4. **Anvisa** (phase 2): RDC 658/2022, RDC 654/2022, and the IN annexes in English.

**We handle these ourselves:**
- Four Indian circulars are scanned images with no text, so they need OCR, which is not installed yet. The
  Schedule L-1 text they relate to is already in the compiled Drugs Rules.
- Not published yet: the ICH consolidated Q1 (still a draft; Q1A-E are held).
- Addresses not found: ICH M7(R2) Q&A and the FDA Burkholderia advisory, to retry. The CDSCO Schedule M FAQ
  does not appear to exist.

## Notes and risks found while collecting

- **Copyright:** PIC/S PDFs say "Reproduction prohibited for commercial purposes". WHO and ICH texts are also
  copyrighted. So quotes stay in the private library, and the customer app shows only our own plain-language
  items (as decided). EU and US texts are public documents.
- **Versions:** PIC/S PE 009-18 was published in September 2026, so it is newer than several EU chapters.
  Where PIC/S and EU wording differ, both are mapped and the difference is flagged; they are never assumed
  identical. The EU Annex 19 revision (item 1 above) is an example of exactly this.
- **Schedule M:** the gazette mixes Hindi and English pages. The extractor keeps only the English parts and
  checks every clause label against `pdftotext -layout` output (the eBMR's non-layout extract scrambled
  clause numbers).
- **Three short EU PDFs** (Chapter 9, Annexes 8 and 9) carry no date. Their version is taken from the EudraLex
  page listing.
