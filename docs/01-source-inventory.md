# Deliverable (a): Source inventory, pilot

Status: draft for owner review, 29 October 2026.
Machine-readable record: `sources/catalog.csv` (what each file is) + `sources/urls.tsv` (where it came from)
→ `sources/inventory.csv` (sha256, bytes, pages, extractable characters), produced by `tools/inventory.py write`.
`tools/inventory.py check` runs in CI and fails if any official file changes, goes missing or is uncatalogued.

All files were downloaded on 29 October 2026 directly from the regulators' own sites (no third-party copies).
The eBMR extracts were not reused: every text will be re-extracted from these PDFs with `pdftotext -layout`.
The Schedule M gazette PDF is byte-identical to the eBMR copy (sha256 `918704…d271`).

## What we have (37 files, all English, all with an extractable text layer)

| Regulator | Files | Pages | Content |
|---|---|---|---|
| US FDA | 6 | 119 + eCFR XML | 21 CFR 210 and 211 as structured eCFR XML (up to date as of 27 Oct 2026; the XML carries section and paragraph structure, better than a PDF); guidances: aseptic processing (2004), process validation (2011), OOS investigations (Rev 1, 2022), data integrity Q&A (2018) |
| EU GMP (EudraLex Vol 4) | 18 | 214 | Introduction; Part I chapters 1–9; Part II (active substances); Annexes 1 (sterile, 2022), 8, 9, 11, 15, 16, 17 |
| PIC/S | 4 | 400 | PE 009-18 of 24 September 2026: Introduction, Part I, Part II, Annexes 1–20 (includes Annex 19 and the glossary) |
| WHO | 4 | 288 | TRS 986 Annex 2 (main principles, 2014); TRS 1044 Annex 2 (sterile, 2022); TRS 957 Annex 2 (APIs, 2010); TRS 1019 Annex 3 (validation, 2019) |
| India | 1 | 272 | Revised Schedule M, G.S.R. 922(E) of 28 Dec 2023, the official bilingual gazette. English parts: I (main principles), II (sterile), VIII (OSD), IX (oral liquids), X (topicals: creams, ointments, gels), XII (APIs), XIII (plant and equipment) and others not in scope (biologicals, radiopharmaceuticals, phytopharmaceuticals, IMPs, MDIs, hazardous) |
| ICH | 4 | 120 | Q7 (2000) + Q7 Q&A (2015); Q9(R1) (2023); Q10 (2008) |

How the sources map to the five plant types:

| Plant type | FDA | EU / PIC/S | WHO | Schedule M | ICH |
|---|---|---|---|---|---|
| OSD | 211 | Part I + Annexes 8, 11, 15 | TRS 986 A2 | I, VIII | Q9, Q10 |
| Oral liquids | 211 | Part I + Annex 9 | TRS 986 A2 | I, IX | Q9, Q10 |
| Gels / semisolids | 211 | Part I + Annex 9 | TRS 986 A2 | I, X | Q9, Q10 |
| Injectables (sterile) | 211 + aseptic guidance | Part I + Annex 1 | TRS 986 A2 + TRS 1044 A2 | I, II | Q9, Q10 |
| APIs | (none: FDA applies ICH Q7 as its guidance) | Part II (= ICH Q7) | TRS 957 A2 | XII | Q7, Q9, Q10 |

## Still needed

Nothing blocks the pilot. Three files and one set of WHO supplementary texts are still missing:

1. **EU: three files behind a bot check** (the EC site served a JavaScript challenge instead of the PDF. I did
   not try to get around it.) Optional, because PIC/S PE 009-18 carries an equivalent Annex 19 and a glossary.
   If you want EU's own wording, please download them from
   https://health.ec.europa.eu/medicinal-products/eudralex/eudralex-volume-4_en and attach them:
   - Annex 19 Reference and Retention Samples (`2005_12_14_annex19_en.pdf`)
   - The newer Annex 19 act listed on the same page (`c2026-4135_en_act_en.pdf`; it looks like a 2026
     revision, and we need it to know which version is in force)
   - Glossary (`glos4en200408_en.pdf`)
2. **WHO supplementary guidelines** (water for pharmaceutical use TRS 1033 Annex 3; HVAC for non-sterile
   products TRS 1019 Annex 2; data integrity TRS 1033 Annex 4). TRS 986 refers to these, and inspectors use
   them. Their WHO pages did not resolve at the addresses I tried. I will look for them myself before asking you.

Not needed for the pilot: 21 CFR Part 11 (it governs only our app's own records, and eCFR has it), and Phase 2/3
regulators.

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
