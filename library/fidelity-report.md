# Source fidelity report

Built by `python3 tools/parse/fidelity.py run` (D39): every parsed clause of every PDF source compared in both directions with a second reading (pdfminer.six via pdfplumber); the rules are in the module docstring. Every flagged clause is fixed or explained in `library/fidelity-explanations.csv`.

Sources: 146; clauses: 20562; tokens: 1593633; flagged clauses: 1336; unexplained: 879.

| Source | Clauses | Flagged |
|---|---|---|
| ema-hbel-guideline.pdf | 26 | 2 |
| ema-hbel-qa-cross-contamination.pdf | 14 | 1 |
| ema-manufacture-finished-dosage-form.pdf | 32 | 1 |
| ema-nitrosamines-qa-mah-rev23-2025.pdf | 61 | 18 |
| ema-process-validation-finished-products.pdf | 30 | 1 |
| ema-qa-microbial-contamination-nonsterile.pdf | 3 | 2 |
| ema-qa-wfi-non-distillation.pdf | 21 | 1 |
| ema-sterilisation-guideline.pdf | 58 | 7 |
| ema-water-quality-guideline.pdf | 66 | 10 |
| eu-2014-03_chapter_2.pdf | 25 | 1 |
| eu-2014-08_gmp_chap8.pdf | 33 | 0 |
| eu-2014-08_gmp_part1.pdf | 439 | 0 |
| eu-2014-11_vol4_chapter_6.pdf | 43 | 1 |
| eu-2015-10_annex15.pdf | 118 | 1 |
| eu-2015-c95-01-gdp-active-substances.pdf | 62 | 1 |
| eu-2015-c95-02-excipients-risk-assessment.pdf | 19 | 4 |
| eu-2018_annex17_en.pdf | 37 | 4 |
| eu-20220825_gmp-an1_en_0.pdf | 335 | 6 |
| eu-annex11_01-2011_en.pdf | 40 | 0 |
| eu-annex19-2026-c2026-4135.pdf | 51 | 2 |
| eu-annex21-importation.pdf | 30 | 1 |
| eu-anx08_en.pdf | 7 | 1 |
| eu-anx09_en.pdf | 11 | 0 |
| eu-cap9_en.pdf | 5 | 0 |
| eu-chapter4_01-2011_en.pdf | 35 | 0 |
| eu-chapter_3.pdf | 46 | 4 |
| eu-chapter_5.pdf | 74 | 3 |
| eu-directive-2017-1572-gmp.pdf | 67 | 1 |
| eu-p3-gmp-mah-reflection-paper.pdf | 16 | 3 |
| eu-p3-site-master-file.pdf | 39 | 0 |
| eu-regulation-1252-2014-gmp-active-substances.pdf | 99 | 1 |
| eu-v4_an16_201510_en.pdf | 74 | 1 |
| eu-vol4-chap1_2013-01_en.pdf | 15 | 0 |
| eu-vol4-chap7_2012-06_en.pdf | 19 | 1 |
| eu-written-confirmation-template-2013.pdf | 13 | 3 |
| fda-aseptic-2004.pdf | 80 | 3 |
| fda-cp-7346-832-preapproval-inspections.pdf | 75 | 116 |
| fda-cp-7356-002-drug-manufacturing-inspections.pdf | 60 | 7 |
| fda-cp-7356-002a-sterile-drug-process.pdf | 54 | 4 |
| fda-cp-7356-002f-api.pdf | 35 | 5 |
| fda-cp-7356-021-dqrs-field-alerts.pdf | 26 | 3 |
| fda-cp-7356-843-postapproval-inspections.pdf | 44 | 3 |
| fda-data-integrity-2018.pdf | 29 | 1 |
| fda-guidance-analytical-procedures-validation-2015.pdf | 32 | 34 |
| fda-guidance-anda-stability-2013.pdf | 5 | 2 |
| fda-guidance-benzene-carbomers-2023.pdf | 10 | 1 |
| fda-guidance-cci-in-lieu-of-sterility-2008.pdf | 9 | 1 |
| fda-guidance-changes-approved-nda-anda-2004.pdf | 74 | 2 |
| fda-guidance-container-closure-systems-1999.pdf | 86 | 40 |
| fda-guidance-deg-eg-high-risk-components-2023.pdf | 6 | 1 |
| fda-guidance-delaying-denying-inspection-2024.pdf | 15 | 3 |
| fda-guidance-dissolution-mechanical-calibration-2010.pdf | 5 | 3 |
| fda-guidance-elemental-impurities-2018.pdf | 15 | 3 |
| fda-guidance-field-alert-report-qa-2021.pdf | 16 | 2 |
| fda-guidance-melamine-components-2009.pdf | 6 | 2 |
| fda-guidance-methanol-testing-alcohol-2023.pdf | 7 | 2 |
| fda-guidance-nitrosamine-control-2024.pdf | 58 | 9 |
| fda-guidance-nitrosamine-ndsri-ai-limits-2023.pdf | 52 | 4 |
| fda-guidance-npbl-cross-contamination-2013.pdf | 9 | 3 |
| fda-guidance-part11-scope-application-2003.pdf | 16 | 18 |
| fda-guidance-product-recalls-2020.pdf | 6 | 1 |
| fda-guidance-pyrogen-endotoxins-qa-2026.pdf | 19 | 2 |
| fda-guidance-quality-agreements-2016.pdf | 21 | 2 |
| fda-guidance-quality-systems-approach-2006.pdf | 67 | 20 |
| fda-guidance-remote-regulatory-assessments-2025.pdf | 20 | 6 |
| fda-guidance-sterilization-validation-submission-1994.pdf | 91 | 5 |
| fda-guidance-voluntary-recalls-initiation-2022.pdf | 10 | 5 |
| fda-oos-2022.pdf | 24 | 2 |
| fda-process-validation-2011.pdf | 23 | 1 |
| ich-m7-r2.pdf | 109 | 5 |
| ich-q10.pdf | 58 | 2 |
| ich-q11-qa-pmda.pdf | 68 | 3 |
| ich-q12.pdf | 137 | 12 |
| ich-q1a-r2.pdf | 73 | 4 |
| ich-q1b.pdf | 11 | 1 |
| ich-q1d.pdf | 46 | 4 |
| ich-q1e.pdf | 68 | 4 |
| ich-q2-r2.pdf | 202 | 6 |
| ich-q3a-r2.pdf | 33 | 4 |
| ich-q3b-r2.pdf | 26 | 3 |
| ich-q3c-r9.pdf | 68 | 23 |
| ich-q3d-r2.pdf | 381 | 56 |
| ich-q6a.pdf | 35 | 2 |
| ich-q7-qa.pdf | 206 | 9 |
| ich-q7.pdf | 446 | 3 |
| ich-q8-q9-q10-qa-r4.pdf | 89 | 11 |
| ich-q9r1.pdf | 45 | 2 |
| india-cdsco-circ-2024-03-risk-based-inspection.pdf | 1314 | 120 |
| india-cdsco-gdp-guidelines-2024.pdf | 217 | 4 |
| india-drugs-rules-1945-consolidated-2024-07.pdf | 2981 | 128 |
| india-gsr127e-2025-schm-timeline.pdf | 14 | 4 |
| india-gsr666e-2024-schm-corrigendum.pdf | 1 | 3 |
| india-schedule-m-2023-GSR922E.pdf | 1593 | 20 |
| pics-pe008-4-site-master-file.pdf | 47 | 1 |
| pics-pe009-18-annexes.pdf | 1303 | 25 |
| pics-pe009-18-part1.pdf | 286 | 10 |
| pics-pe009-18-part2.pdf | 449 | 9 |
| pics-pi006-4-qualification-validation.pdf | 282 | 0 |
| pics-pi007-6-aseptic-validation.pdf | 172 | 1 |
| pics-pi009-4-am-utilities.pdf | 56 | 12 |
| pics-pi011-3-computerised-systems.pdf | 260 | 13 |
| pics-pi012-3-sterility-testing.pdf | 125 | 2 |
| pics-pi014-3-isolators.pdf | 113 | 4 |
| pics-pi023-2-am-qc-labs.pdf | 97 | 14 |
| pics-pi028-2-am-packaging.pdf | 29 | 12 |
| pics-pi030-1-am-api.pdf | 114 | 33 |
| pics-pi038-2-am-qrm.pdf | 94 | 6 |
| pics-pi040-1-deficiency-classification.pdf | 55 | 3 |
| pics-pi041-1-data-integrity.pdf | 401 | 8 |
| pics-pi043-1-am-cross-contamination.pdf | 154 | 5 |
| pics-pi045-1-excipient-risk-assessment.pdf | 26 | 2 |
| pics-pi047-1-gdp-active-substances.pdf | 70 | 2 |
| pics-pi052-1-am-hbel.pdf | 39 | 7 |
| pics-pi053-1-qa-cross-contamination.pdf | 18 | 1 |
| pics-pi054-1-pqs-effectiveness.pdf | 125 | 7 |
| pics-pi058-1-annex1-interpretation.pdf | 109 | 5 |
| who-trs1010-a10-stability.pdf | 82 | 10 |
| who-trs1010-a8-hvac-nonsterile.pdf | 121 | 40 |
| who-trs1019-a2-hvac-nonsterile-part2.pdf | 24 | 4 |
| who-trs1019-a3-validation.pdf | 407 | 14 |
| who-trs1025-a3-wfi-non-distillation.pdf | 39 | 7 |
| who-trs1025-a4-chromatography.pdf | 100 | 0 |
| who-trs1025-a6-amr-environment.pdf | 14 | 0 |
| who-trs1025-a7-storage-distribution.pdf | 215 | 2 |
| who-trs1033-a2-hbel-cleaning.pdf | 51 | 2 |
| who-trs1033-a3-water.pdf | 121 | 0 |
| who-trs1033-a4-data-integrity.pdf | 88 | 2 |
| who-trs1044-a2-sterile.pdf | 315 | 10 |
| who-trs1044-a4-tech-transfer.pdf | 136 | 2 |
| who-trs1052-a4-qc-labs.pdf | 382 | 6 |
| who-trs1060-a2-nitrosamines.pdf | 130 | 1 |
| who-trs1060-a3-excipients.pdf | 272 | 13 |
| who-trs902-a9-packaging.pdf | 110 | 3 |
| who-trs929-a4-sampling.pdf | 83 | 24 |
| who-trs943-a3-reference-substances.pdf | 42 | 2 |
| who-trs953-a2-app1-stability-conditions.pdf | 208 | 1 |
| who-trs957-a2-api.pdf | 559 | 59 |
| who-trs957-a3-hazardous.pdf | 94 | 13 |
| who-trs961-a14-site-master-file.pdf | 32 | 2 |
| who-trs961-a2-micro-labs.pdf | 206 | 30 |
| who-trs961-a9-storage-transport-ttsp.pdf | 142 | 11 |
| who-trs981-a2-qrm.pdf | 46 | 9 |
| who-trs986-a2-gmp-main.pdf | 322 | 0 |
| who-trs992-a4-hold-time.pdf | 6 | 1 |
| who-trs992-a5-ttsp-supplements.pdf | 318 | 37 |
| who-trs996-a4-app1-model-inspection-report.pdf | 84 | 18 |

## Flagged clauses

- ema-hbel-guideline.pdf _unnumbered:1 (unnumbered): `-churchill place canary wharf london e 14 5 eu united kingdom telephone 44 0 | +june 2013 adoption by cvmp 11 september 2014 adopted by safety working party october 2014 adoption by chmp | -3660 6000 facsimile 44 0 20 3660 5555 send a question via our website www ema europa eu contact an agency of t` - Front matter (cover page, document history, contents): the two engines read the cover's text boxes, address blocks and history table in different orders; not regulation text.
- ema-hbel-guideline.pdf 5.1 (clause): `+−` - Exponent minus (verified: every minus sign on the clause's pages follows a number or a unit, as in '10⁻⁶' or 'mg⁻¹'): the stored text has poppler's rendering of the superscript without the sign ('10-6' or '106'). Known superscript limitation (0b: keep superscripts as '10^-6').
- ema-hbel-qa-cross-contamination.pdf Q2 (clause): `-30 churchill place canary wharf london e 14 5 eu united kingdom telephone 44 0 20 3660 6000 facsimile 44 0 20 3660 5555 send a question via our website www ema europa eu contact an agency of the european union european medicines agency 2018 reproduction is authorised provided the source is acknowle` - NOT EXPLAINED
- ema-manufacture-finished-dosage-form.pdf _unnumbered:1 (unnumbered): `-4 july 2017 ema chmp qwp 245074 2015 committee for human medicinal products chmp guideline on manufacture of the finished dosage form this guideline replaces the note for guidance on manufacture of the finished dosage form cpmp qwp 486 95 | -an agency of the european union | -table of contents exec` - Front matter (cover page, document history, contents): the two engines read the cover's text boxes, address blocks and history table in different orders; not regulation text.
- ema-nitrosamines-qa-mah-rev23-2025.pdf _unnumbered:1 (unnumbered): `-official address domenico scarlattilaan 6 1083 hs amsterdam the netherlands address for visits and deliveries refer to www ema europa eu how to find us send us a question go to www ema europa eu contact telephone 31 0 88 781 6000 an agency of the european union european medicines agency 2025 reprod` - Front matter (cover page, document history, contents): the two engines read the cover's text boxes, address blocks and history table in different orders; not regulation text.
- ema-nitrosamines-qa-mah-rev23-2025.pdf _unnumbered:2 (unnumbered): `-revision history questions and answers for marketing authorisation holders applicants on the chmp questions and answers for marketing authorisation holders applicants on the chmp | -questions and answers for marketing authorisation holders applicants on the chmp` - Front matter (cover page, document history, contents): the two engines read the cover's text boxes, address blocks and history table in different orders; not regulation text.
- ema-nitrosamines-qa-mah-rev23-2025.pdf Q1 (clause): `-questions and answers for marketing authorisation holders applicants on the chmp` - Order or place only (verified mechanically): every stored word run of this discrepancy is printed on the clause's pages, and every page run it lacks is stored word for word (in this clause or another), so no word is lost or added; the engines read table cells, columns or figure labels in different orders.
- ema-nitrosamines-qa-mah-rev23-2025.pdf Q2 (clause): `-questions | +3 for the call for review for chemically synthesised | -answers for marketing authorisation holders applicants on the chmp` - Parser defect (0b): the running page header 'Questions and answers for marketing authorisation holders/applicants on the CHMP Opinion...' is stored inside the answer at each page break (and the footer 'EMA/409815/2020 Page n/27' the second engine keeps); answer text intact.
- ema-nitrosamines-qa-mah-rev23-2025.pdf Q3 (clause): `-questions and answers for marketing authorisation holders applicants on the chmp | -questions and answers for marketing authorisation holders applicants on the chmp` - Order or place only (verified mechanically): every stored word run of this discrepancy is printed on the clause's pages, and every page run it lacks is stored word for word (in this clause or another), so no word is lost or added; the engines read table cells, columns or figure labels in different orders.
- ema-nitrosamines-qa-mah-rev23-2025.pdf Q4 (clause): `-questions and answers for marketing authorisation holders applicants on the chmp | -questions and answers for marketing authorisation holders applicants on the chmp` - Order or place only (verified mechanically): every stored word run of this discrepancy is printed on the clause's pages, and every page run it lacks is stored word for word (in this clause or another), so no word is lost or added; the engines read table cells, columns or figure labels in different orders.
- ema-nitrosamines-qa-mah-rev23-2025.pdf Q5 (clause): `-questions and answers for marketing authorisation holders applicants on the chmp` - Order or place only (verified mechanically): every stored word run of this discrepancy is printed on the clause's pages, and every page run it lacks is stored word for word (in this clause or another), so no word is lost or added; the engines read table cells, columns or figure labels in different orders.
- ema-nitrosamines-qa-mah-rev23-2025.pdf Q7 (clause): `-questions and answers for marketing authorisation holders applicants on the chmp` - Order or place only (verified mechanically): every stored word run of this discrepancy is printed on the clause's pages, and every page run it lacks is stored word for word (in this clause or another), so no word is lost or added; the engines read table cells, columns or figure labels in different orders.
- ema-nitrosamines-qa-mah-rev23-2025.pdf Q8 (clause): `-questions and answers for marketing authorisation holders applicants on the chmp | -questions | +9 what are the requirements of the analytical method s the analytical methods need to be sufficiently sensitive in order to adequately detect | -answers for marketing authorisation holders applicants on` - Parser defect (0b): the running page header 'Questions and answers for marketing authorisation holders/applicants on the CHMP Opinion...' is stored inside the answer at each page break (and the footer 'EMA/409815/2020 Page n/27' the second engine keeps); answer text intact.
- ema-nitrosamines-qa-mah-rev23-2025.pdf Q10 (clause): `-questions and answers for marketing authorisation holders applicants on the chmp | -questions and answers for marketing authorisation holders applicants on the chmp | +xi aii | -xi | +i 2 | -aii i 2 questions and answers for marketing authorisation holders applicants on the chmp | -320 ppb 88 ppb |` - Parser defect (0b): the running page header 'Questions and answers for marketing authorisation holders/applicants on the CHMP Opinion...' is stored inside the answer at each page break (and the footer 'EMA/409815/2020 Page n/27' the second engine keeps); answer text intact.
- ema-nitrosamines-qa-mah-rev23-2025.pdf Q12 (clause): `-questions and answers for marketing authorisation holders applicants on the chmp` - Order or place only (verified mechanically): every stored word run of this discrepancy is printed on the clause's pages, and every page run it lacks is stored word for word (in this clause or another), so no word is lost or added; the engines read table cells, columns or figure labels in different orders.
- ema-nitrosamines-qa-mah-rev23-2025.pdf Q14 (clause): `-questions and answers for marketing authorisation holders applicants on the chmp | -questions and answers for marketing authorisation holders applicants on the chmp` - Order or place only (verified mechanically): every stored word run of this discrepancy is printed on the clause's pages, and every page run it lacks is stored word for word (in this clause or another), so no word is lost or added; the engines read table cells, columns or figure labels in different orders.
- ema-nitrosamines-qa-mah-rev23-2025.pdf Q16 (clause): `-questions and answers for marketing authorisation holders applicants on the chmp` - Order or place only (verified mechanically): every stored word run of this discrepancy is printed on the clause's pages, and every page run it lacks is stored word for word (in this clause or another), so no word is lost or added; the engines read table cells, columns or figure labels in different orders.
- ema-nitrosamines-qa-mah-rev23-2025.pdf Q20 (clause): `-questions and answers for marketing authorisation holders applicants on the chmp` - Order or place only (verified mechanically): every stored word run of this discrepancy is printed on the clause's pages, and every page run it lacks is stored word for word (in this clause or another), so no word is lost or added; the engines read table cells, columns or figure labels in different orders.
- ema-nitrosamines-qa-mah-rev23-2025.pdf Q22 (clause): `-questions and answers for marketing authorisation holders applicants on the chmp | -questions and answers for marketing authorisation holders applicants on the chmp | -questions and answers for marketing authorisation holders applicants on the chmp` - Order or place only (verified mechanically): every stored word run of this discrepancy is printed on the clause's pages, and every page run it lacks is stored word for word (in this clause or another), so no word is lost or added; the engines read table cells, columns or figure labels in different orders.
- ema-nitrosamines-qa-mah-rev23-2025.pdf Table 4 row 1 (table_row): `-limit results limit results limit results` - Order or place only (verified mechanically): every stored word run of this discrepancy is printed on the clause's pages, and every page run it lacks is stored word for word (in this clause or another), so no word is lost or added; the engines read table cells, columns or figure labels in different orders.
- ema-nitrosamines-qa-mah-rev23-2025.pdf page 7 (uncovered): `+in two clauses Q2 and Q3: 3 for the call for review for chemically synthesised and` - NOT EXPLAINED
- ema-nitrosamines-qa-mah-rev23-2025.pdf page 15 (uncovered): `+in two clauses Q8 and Q9: 9 what are the requirements of the analytical method s the analytical methods need to be sufficiently sensitive in order to adequately detect and` - NOT EXPLAINED
- ema-process-validation-finished-products.pdf _unnumbered:1 (unnumbered): `-30 churchill place canary wharf london e 14 | +draft agreed by chmp cvmp quality working party 2 february 2012 adoption by cvmp for release for consultation 8 march 2012 adoption by chmp for release for consultation 15 march 2012 end of consultation deadline for comments 31 october 2012 agreed by q` - Front matter (cover page, document history, contents): the two engines read the cover's text boxes, address blocks and history table in different orders; not regulation text.
- ema-qa-microbial-contamination-nonsterile.pdf _unnumbered:1 (unnumbered): `-official address domenico scarlattilaan 6 1083 hs amsterdam the netherlands address for visits and deliveries refer to www ema europa eu how to find us an agency of the european union send us a question go to www ema europa eu contact telephone 31 0 88 781 6000 european medicines agency 2026 reprod` - Front matter (cover page, document history, contents): the two engines read the cover's text boxes, address blocks and history table in different orders; not regulation text.
- ema-qa-microbial-contamination-nonsterile.pdf Q2 (clause): `-what are technical and organisational measures that should be taken into consideration to prevent microbial contamination of non sterile medicinal products ema ins gmp 161750 2026 page 3 3` - Order or place only (verified mechanically): every stored word run of this discrepancy is printed on the clause's pages, and every page run it lacks is stored word for word (in this clause or another), so no word is lost or added; the engines read table cells, columns or figure labels in different orders.
- ema-qa-wfi-non-distillation.pdf _unnumbered:1 (unnumbered): `-30 churchill place canary wharf london e 14 5 eu united kingdom telephone 44 0 20 3660 6000 facsimile 44 0 20 3660 5555 send a question via our website www ema europa eu contact an agency of the european union european medicines agency 2017 reproduction is authorised provided the source is acknowle` - Front matter (cover page, document history, contents): the two engines read the cover's text boxes, address blocks and history table in different orders; not regulation text.
- ema-sterilisation-guideline.pdf _unnumbered:1 (unnumbered): `-official address domenico scarlattilaan 6 1083 hs amsterdam the netherlands address for visits and deliveries refer to www ema europa eu how to find us send us a question go to www ema europa eu contact telephone 31 0 88 781 6000 an agency of the european union european medicines agency 2019 reprod` - Order or place only (verified mechanically): every stored word run of this discrepancy is printed on the clause's pages, and every page run it lacks is stored word for word (in this clause or another), so no word is lost or added; the engines read table cells, columns or figure labels in different orders.
- ema-sterilisation-guideline.pdf 4.1.1 (clause): `+−` - Exponent minus (verified: every minus sign on the clause's pages follows a number or a unit, as in '10⁻⁶' or 'mg⁻¹'): the stored text has poppler's rendering of the superscript without the sign ('10-6' or '106'). Known superscript limitation (0b: keep superscripts as '10^-6').
- ema-sterilisation-guideline.pdf 4.1.2 (clause): `+− | +−` - Exponent minus (verified: every minus sign on the clause's pages follows a number or a unit, as in '10⁻⁶' or 'mg⁻¹'): the stored text has poppler's rendering of the superscript without the sign ('10-6' or '106'). Known superscript limitation (0b: keep superscripts as '10^-6').
- ema-sterilisation-guideline.pdf 4.1.4.1 (clause): `+−` - Exponent minus (verified: every minus sign on the clause's pages follows a number or a unit, as in '10⁻⁶' or 'mg⁻¹'): the stored text has poppler's rendering of the superscript without the sign ('10-6' or '106'). Known superscript limitation (0b: keep superscripts as '10^-6').
- ema-sterilisation-guideline.pdf 4.1.5 (clause): `-4.1.5 sterile filtration the filter data to be provided in the quality dossier is summarised in table 3 table 3 filter data to be provided in the quality dossier for filters in contact with the drug product or components of the drug product` - NOT EXPLAINED
- ema-sterilisation-guideline.pdf 4.1.6 (clause): `+−` - Exponent minus (verified: every minus sign on the clause's pages follows a number or a unit, as in '10⁻⁶' or 'mg⁻¹'): the stored text has poppler's rendering of the superscript without the sign ('10-6' or '106'). Known superscript limitation (0b: keep superscripts as '10^-6').
- ema-sterilisation-guideline.pdf Definitions (section): `+− | +−` - Exponent minus (verified: every minus sign on the clause's pages follows a number or a unit, as in '10⁻⁶' or 'mg⁻¹'): the stored text has poppler's rendering of the superscript without the sign ('10-6' or '106'). Known superscript limitation (0b: keep superscripts as '10^-6').
- ema-water-quality-guideline.pdf _unnumbered:1 (unnumbered): `-guideline on the | +draft agreed by | -water | +public consultation 15 november 2018 end of consultation deadline | -pharmaceutical use | +comments 15 may 2019 agreed by gmdp iwg 5 march 2020 agreed by bwp 18 march 2020 agreed by qwp 6 may 2020 adopted by chmp for publication 28 may 2020 adopted by` - Front matter (cover page, document history, contents): the two engines read the cover's text boxes, address blocks and history table in different orders; not regulation text.
- ema-water-quality-guideline.pdf 5.2 (clause): `-5.2 water used during manufacture of active substances and medicinal products excluding water present as an excipient in the final formulation the grade of water will depend on the stage at which it is to be used during manufacture the subsequent processing steps and the nature of the final product` - Order or place only (verified mechanically): every stored word run of this discrepancy is printed on the clause's pages, and every page run it lacks is stored word for word (in this clause or another), so no word is lost or added; the engines read table cells, columns or figure labels in different orders.
- ema-water-quality-guideline.pdf Table 5 AS is in solution, not sterile, and… (table_row): `-wfi` - NOT EXPLAINED
- ema-water-quality-guideline.pdf page 7 (uncovered): `+in table row: during manufacture of active substances and medicinal products excluding` - NOT EXPLAINED
- ema-water-quality-guideline.pdf page 7 (uncovered): `+in table row: present as an excipient` - NOT EXPLAINED
- ema-water-quality-guideline.pdf page 7 (uncovered): `+in table row: the final` - NOT EXPLAINED
- ema-water-quality-guideline.pdf page 7 (uncovered): `+in table row: the grade of` - NOT EXPLAINED
- ema-water-quality-guideline.pdf page 7 (uncovered): `+in table row: will depend on the stage at which it is` - NOT EXPLAINED
- ema-water-quality-guideline.pdf page 7 (uncovered): `+in table row: during manufacture the subsequent processing steps and the nature of the final product according` - NOT EXPLAINED
- ema-water-quality-guideline.pdf page 7 (uncovered): `+in table row: final isolation and purification` - NOT EXPLAINED
- eu-2014-03_chapter_2.pdf _unnumbered:1 (unnumbered): `-ref ares 2014 968076 28 03 2014` - Order or place only (verified mechanically): every stored word run of this discrepancy is printed on the clause's pages, and every page run it lacks is stored word for word (in this clause or another), so no word is lost or added; the engines read table cells, columns or figure labels in different orders.
- eu-2014-11_vol4_chapter_6.pdf _unnumbered:1 (unnumbered): `-ref ares 2014 968036 28 03 2014 | +ref ares 2014 968036 28 03 2014` - NOT EXPLAINED
- eu-2015-10_annex15.pdf _unnumbered:1 (unnumbered): `-ref ares 2015 1380025 30 03 2015 | -commission européenne europese commissie 1049 bruxelles brussel belgique belgië tel 32 22991111` - Order or place only (verified mechanically): every stored word run of this discrepancy is printed on the clause's pages, and every page run it lacks is stored word for word (in this clause or another), so no word is lost or added; the engines read table cells, columns or figure labels in different orders.
- eu-2015-c95-01-gdp-active-substances.pdf _unnumbered:1 (unnumbered): `-ii` - NOT EXPLAINED
- eu-2015-c95-02-excipients-risk-assessment.pdf _unnumbered:1 (unnumbered): `-c 95 10 en official journal of the european union 21.3.2015` - Order or place only (verified mechanically): every stored word run of this discrepancy is printed on the clause's pages, and every page run it lacks is stored word for word (in this clause or another), so no word is lost or added; the engines read table cells, columns or figure labels in different orders.
- eu-2015-c95-02-excipients-risk-assessment.pdf Chapter 2 2.3 (clause): `-21.3.2015 | +c 95 10 | -c 95 11 | +21.3.2015` - NOT EXPLAINED
- eu-2015-c95-02-excipients-risk-assessment.pdf Chapter 2 2.6 (clause): `-c 95 12 | +21.3.2015 | -21.3.2015 | +c 95 11` - NOT EXPLAINED
- eu-2015-c95-02-excipients-risk-assessment.pdf Chapter 4 4.1 (clause): `-21.3.2015 | +c 95 12 | -c 95 13 | +21.3.2015` - NOT EXPLAINED
- eu-2018_annex17_en.pdf _unnumbered:1 (unnumbered): `-4 | -1` - NOT EXPLAINED
- eu-2018_annex17_en.pdf page 3 (uncovered): `+next to 1.1: principle 1` - NOT EXPLAINED
- eu-2018_annex17_en.pdf page 3 (uncovered): `+next to 1.1: 2 scope` - NOT EXPLAINED
- eu-2018_annex17_en.pdf page 3 (uncovered): `+next to 2.1: scope 2` - NOT EXPLAINED
- eu-20220825_gmp-an1_en_0.pdf _unnumbered:1 (unnumbered): `-european commission brussels 22.8.2022 | -2022 5938 final guidelines | +u d o n p r o il na un 2 2 a a n e d i c i 0 n p m 8 2 8 f i u r o o r 2 3 ef s e l s 2 2 2 5 9 n t h e a c t i c e u s e u s 2 0 s i p b r c t r e unn l i n p r o d t u r i e t e r i no n g u i d d i c i n a m a n u f n a n d ` - Front matter (cover page, document history, contents): the two engines read the cover's text boxes, address blocks and history table in different orders; not regulation text.
- eu-20220825_gmp-an1_en_0.pdf Annex 1 8.6 (clause): `-aseptic preparation and processing` - Order or place only (verified mechanically): every stored word run of this discrepancy is printed on the clause's pages, and every page run it lacks is stored word for word (in this clause or another), so no word is lost or added; the engines read table cells, columns or figure labels in different orders.
- eu-20220825_gmp-an1_en_0.pdf Annex 1 Glossary (section): `+− | +−` - Exponent minus (verified: every minus sign on the clause's pages follows a number or a unit, as in '10⁻⁶' or 'mg⁻¹'): the stored text has poppler's rendering of the superscript without the sign ('10-6' or '106'). Known superscript limitation (0b: keep superscripts as '10^-6').
- eu-20220825_gmp-an1_en_0.pdf page 4 (uncovered): `+next to Annex 1 1: 2 principle` - NOT EXPLAINED
- eu-20220825_gmp-an1_en_0.pdf page 4 (uncovered): `+next to Annex 1 2.1: principle 2` - NOT EXPLAINED
- eu-20220825_gmp-an1_en_0.pdf page 2 (uncovered): `+in two clauses Annex 1 and _unnumbered:1: annex 1 manufacture of sterile medicinal products legal context for publishing the detailed guidelines article 47 of directive 2001 83 ec on the community code relating to medicinal products for human use and regulation 2019 6 on the community code relating` - NOT EXPLAINED
- eu-annex19-2026-c2026-4135.pdf _unnumbered:1 (unnumbered): `-european commission brussels 23.6.2026 | +o mm i ss i o n b r u ss e l s 23 6 | -4135 final guidelines | +c 20 26 413 5 f i n a l g u i d el i n e s t h e r u l e s g ov er n i n g m e d i c i n a l p r o d u c t s i n t h e e u r o p e a n u n i o n v o l u m e 4 e u g u i d e li n e s f o r g oo ` - NOT EXPLAINED
- eu-annex19-2026-c2026-4135.pdf page 2 (uncovered): `+in two clauses Annex 19 and _unnumbered:1: annex 19 reference and retention samples legal basis for publishing the detailed guidelines article 47 of directive 2001 83 ec on the community code relating to medicinal products` - NOT EXPLAINED
- eu-annex21-importation.pdf _unnumbered:1 (unnumbered): `-en en` - NOT EXPLAINED
- eu-anx08_en.pdf Annex 8 3 (clause): `+n` - NOT EXPLAINED
- eu-chapter_3.pdf _unnumbered:1 (unnumbered): `-ref ares 2015 283695 23 01 2015 | -commission européenne b 1049 bruxelles europese commissie b 1049 brussel belgium telephone 32 2 299 11 11 | +ref ares 2015 283695 23 01 2015` - Order or place only (verified mechanically): every stored word run of this discrepancy is printed on the clause's pages, and every page run it lacks is stored word for word (in this clause or another), so no word is lost or added; the engines read table cells, columns or figure labels in different orders.
- eu-chapter_3.pdf 3 Principle (principle): `+p remises general 3.1` - NOT EXPLAINED
- eu-chapter_3.pdf 3.33 (clause): `+e quipment 3.34 manufacturing` - NOT EXPLAINED
- eu-chapter_3.pdf page 5 (uncovered): `+in two clauses 3.33 and 3.34: 3.34 manufacturing equipment` - NOT EXPLAINED
- eu-chapter_5.pdf Chapter 5 (section): `-commission européenne b 1049 bruxelles europese commissie b 1049 brussel belgium telephone 32 2 299 11 11 | +ref ares 2015 283689 23 01 2015` - Order or place only (verified mechanically): every stored word run of this discrepancy is printed on the clause's pages, and every page run it lacks is stored word for word (in this clause or another), so no word is lost or added; the engines read table cells, columns or figure labels in different orders.
- eu-chapter_5.pdf Chapter 5 5.71 (clause): `+4` - A footnote reference number (verified: it starts a line or is printed small on the clause's pages) that the parser drops with the footnote mark; no regulation word changes.
- eu-chapter_5.pdf page 1 (uncovered): `+in two clauses Chapter 5 and _unnumbered:1: ref ares 2015 283689 23 01 2015` - NOT EXPLAINED
- eu-directive-2017-1572-gmp.pdf _unnumbered:4 (unnumbered): `+directive 2003 94 ec this directive | -directive 2003 94 ec this directive` - NOT EXPLAINED
- eu-p3-gmp-mah-reflection-paper.pdf _unnumbered:1 (unnumbered): `-10 january 2022 ema 419571 2021 human medicines pharmacovigilance and committees division version 2 reflection paper on good manufacturing practice and marketing authorisation holders | -an agency of the european union | +10 january 2022 ema 419571 2021 human medicines pharmacovigilance and committ` - NOT EXPLAINED
- eu-p3-gmp-mah-reflection-paper.pdf 5.2 (clause): `+manufac the document titled guidance for the template for the qualified person s declaration concerning gmp compliance of active substance manufacture also addresses the responsibility of the mah to ensure that a written confirmation of compliance of the` - NOT EXPLAINED
- eu-p3-gmp-mah-reflection-paper.pdf 5.3 (clause): `-the document titled guidance for the template for the qualified person s declaration concerning gmp compliance of active substance manufacture also addresses the responsibility of the mah to ensure that a written confirmation of compliance of the manufac` - Order or place only (verified mechanically): every stored word run of this discrepancy is printed on the clause's pages, and every page run it lacks is stored word for word (in this clause or another), so no word is lost or added; the engines read table cells, columns or figure labels in different orders.
- eu-regulation-1252-2014-gmp-active-substances.pdf _unnumbered:1 (unnumbered): `-ii` - Front matter (cover page, document history, contents): the two engines read the cover's text boxes, address blocks and history table in different orders; not regulation text.
- eu-v4_an16_201510_en.pdf _unnumbered:1 (unnumbered): `-ref ares 2015 4234460 12 10 2015 | +ref ares 2015 4234460 12 10 2015` - NOT EXPLAINED
- eu-vol4-chap7_2012-06_en.pdf _unnumbered:1 (unnumbered): `-ref ares 2012 778531 28 06 2012 | +ref ares 2012 778531 28 06 2012` - NOT EXPLAINED
- eu-written-confirmation-template-2013.pdf _unnumbered:1 (unnumbered): `-ref ares 2013 101580 28 01 2013` - Order or place only (verified mechanically): every stored word run of this discrepancy is printed on the clause's pages, and every page run it lacks is stored word for word (in this clause or another), so no word is lost or added; the engines read table cells, columns or figure labels in different orders.
- eu-written-confirmation-template-2013.pdf 2 (clause): `-2 the template for this written confirmation is set out in annex 1 http ec europa eu health documents pharmaceutical committee index en htm commission 2 writteneuropéenne europese confirmations basedcommissie 1049 bruxelles brussel on the previous belgique belgië version of the template tel 32 2299` - Parser defect (0b): the page footer (the Commission's address in French and Dutch) is interleaved with footnote 2 and stored glued onto the clause; the clause's own sentence is intact.
- eu-written-confirmation-template-2013.pdf page 1 (uncovered): `+written confirmations based on the previous version of the template remain valid` - Parser defect (0b): the page footer (the Commission's address in French and Dutch) is interleaved with footnote 2 and stored glued onto the clause; the clause's own sentence is intact.
- fda-aseptic-2004.pdf IV (clause): `-classificationsa | +classifications a clean area classification 0.5 um particles ft 3 iso designation b > 0.5 μm particles m 3 microbiological active air action levels c cfu m 3 microbiological settling plates action levels c d diam 90 mm cfu 4 hours 100 5 3,520 1 e 1 e 1000 6 35,200 7 3 10,000 7 3` - NOT EXPLAINED
- fda-aseptic-2004.pdf IX.C.1 (clause): `+−` - Exponent minus (verified: every minus sign on the clause's pages follows a number or a unit, as in '10⁻⁶' or 'mg⁻¹'): the stored text has poppler's rendering of the superscript without the sign ('10-6' or '106'). Known superscript limitation (0b: keep superscripts as '10^-6').
- fda-aseptic-2004.pdf _unnumbered:4 (unnumbered): `+−` - Exponent minus (verified: every minus sign on the clause's pages follows a number or a unit, as in '10⁻⁶' or 'mg⁻¹'): the stored text has poppler's rendering of the superscript without the sign ('10-6' or '106'). Known superscript limitation (0b: keep superscripts as '10^-6').
- fda-cp-7346-832-preapproval-inspections.pdf _unnumbered:1 (unnumbered): `-food and drug administration compliance program program 7346.832 chapter 46 new drug evaluation` - Front matter (cover page, document history, contents): the two engines read the cover's text boxes, address blocks and history table in different orders; not regulation text.
- fda-cp-7346-832-preapproval-inspections.pdf Part II 2.A (clause): `-yes risk assessment supports determination pai not needed of pai objectives no no risk assessment supports potential use of alternative tools ats in lieu of inspection yes | -no yes | -pai needed | +pai needed risk assessment supports determination of pai objectives yes yes no no no risk assessment` - NOT EXPLAINED
- fda-cp-7346-832-preapproval-inspections.pdf Part III 1.B (clause): `+29` - A footnote reference number (verified: it starts a line or is printed small on the clause's pages) that the parser drops with the footnote mark; no regulation word changes.
- fda-cp-7346-832-preapproval-inspections.pdf Part V B (clause): `+45` - A footnote reference number (verified: it starts a line or is printed small on the clause's pages) that the parser drops with the footnote mark; no regulation word changes.
- fda-cp-7346-832-preapproval-inspections.pdf Part VI D (clause): `+46` - A footnote reference number (verified: it starts a line or is printed small on the clause's pages) that the parser drops with the footnote mark; no regulation word changes.
- fda-cp-7346-832-preapproval-inspections.pdf _unnumbered:6 (unnumbered): `-dmf drug master file | -ec established condition | -eir establishment inspection report | -far field alert report | +action cder center for drug evaluation and research cgmp current good manufacturing practice cmc chemistry manufacturing and controls cms compliance management system conops concept ` - NOT EXPLAINED
- fda-cp-7346-832-preapproval-inspections.pdf Attachment A (clause): `+in addition to its inspectional authority fda may conduct remote regulatory assessments rras under certain circumstances to support oversight of fda regulated products and establishments 1` - NOT EXPLAINED
- fda-cp-7346-832-preapproval-inspections.pdf Attachment B (clause): `-cont next page cont next page cont next page cont next page cont next page cont next page manufacturing and control the iqa team assesses the the inspection team inspection team lead or pam of finished product sterility control and assurance evaluates the facility provides the iqa team with informa` - NOT EXPLAINED
- fda-cp-7346-832-preapproval-inspections.pdf Table 4 Novel excipient manufacturing (e.g.… (table_row): `-recommends a pai better communicates finds released lots do meet manufacturer observations form fda 483 communicates requests assessment before pai pai assessment after pai` - NOT EXPLAINED
- fda-cp-7346-832-preapproval-inspections.pdf Table 4 Manufacturing and control of finished… #2 (table_row): `-manufacturing control finished product finished product assesses finished drug product in evaluates integrity in reports questionable assesses whether method has been verified operate under specified conditions use lead or pam provides initial facility recommendation assesses make recommendation by` - NOT EXPLAINED
- fda-cp-7346-832-preapproval-inspections.pdf Table 4 Manufacturing and control of finished… #4 (table_row): `-terminally sterilized overall including included cycle acceptance criteria will allow act surrogates preventative maintenance equipment system investigations batch include issues will` - NOT EXPLAINED
- fda-cp-7346-832-preapproval-inspections.pdf Table 5 Manufacturing and control of finished… (table_row): `-finds deficient includes observations on form 483 works with understand impact on communicates quality with requests they update reflect a higher e g consistent with recommendations guidance communicates quality with inspected example identifies blender revolutions as proposes a lower e g annual re` - NOT EXPLAINED
- fda-cp-7346-832-preapproval-inspections.pdf page 47 (uncovered): `+in table row: evaluates` - NOT EXPLAINED
- fda-cp-7346-832-preapproval-inspections.pdf page 47 (uncovered): `+in table row: conformance with` - NOT EXPLAINED
- fda-cp-7346-832-preapproval-inspections.pdf page 47 (uncovered): `+in table row: evaluates` - NOT EXPLAINED
- fda-cp-7346-832-preapproval-inspections.pdf page 47 (uncovered): `+in table row: on site mitigation strategy` - NOT EXPLAINED
- fda-cp-7346-832-preapproval-inspections.pdf page 47 (uncovered): `+in table row: controls for the` - NOT EXPLAINED
- fda-cp-7346-832-preapproval-inspections.pdf page 47 (uncovered): `+in table row: and` - NOT EXPLAINED
- fda-cp-7346-832-preapproval-inspections.pdf page 47 (uncovered): `+in table row: identified by the` - NOT EXPLAINED
- fda-cp-7346-832-preapproval-inspections.pdf page 47 (uncovered): `+in table row: inspection` - NOT EXPLAINED
- fda-cp-7346-832-preapproval-inspections.pdf page 47 (uncovered): `+in table row: lead or pam provides the` - NOT EXPLAINED
- fda-cp-7346-832-preapproval-inspections.pdf page 47 (uncovered): `+in table row: team with its initial` - NOT EXPLAINED
- fda-cp-7346-832-preapproval-inspections.pdf page 47 (uncovered): `+in table row: recommendation the iqa team assesses the inspection findings` - NOT EXPLAINED
- fda-cp-7346-832-preapproval-inspections.pdf page 47 (uncovered): `+in table row: and their impact on application approval cder on behalf of the iqa team may communicate with the` - NOT EXPLAINED
- fda-cp-7346-832-preapproval-inspections.pdf page 47 (uncovered): `+in table row: dmf holder or inspected facility` - NOT EXPLAINED
- fda-cp-7346-832-preapproval-inspections.pdf page 47 (uncovered): `+in table row: the facility` - NOT EXPLAINED
- fda-cp-7346-832-preapproval-inspections.pdf page 47 (uncovered): `+in table row: the applicant as appropriate` - NOT EXPLAINED
- fda-cp-7346-832-preapproval-inspections.pdf page 47 (uncovered): `+resolve outstanding quality issues for` - NOT EXPLAINED
- fda-cp-7346-832-preapproval-inspections.pdf page 47 (uncovered): `+in table row: the iqa team` - NOT EXPLAINED
- fda-cp-7346-832-preapproval-inspections.pdf page 47 (uncovered): `+in table row: facility and` - NOT EXPLAINED
- fda-cp-7346-832-preapproval-inspections.pdf page 47 (uncovered): `+in table row: the` - NOT EXPLAINED
- fda-cp-7346-832-preapproval-inspections.pdf page 47 (uncovered): `+in table row: risks and concerns to the inspection team` - NOT EXPLAINED
- fda-cp-7346-832-preapproval-inspections.pdf page 47 (uncovered): `+in table row: cont next page` - NOT EXPLAINED
- fda-cp-7346-832-preapproval-inspections.pdf page 48 (uncovered): `+in table row: addressing quality related topics via` - NOT EXPLAINED
- fda-cp-7346-832-preapproval-inspections.pdf page 48 (uncovered): `+integrated approach quality topic integrated approach` - NOT EXPLAINED
- fda-cp-7346-832-preapproval-inspections.pdf page 48 (uncovered): `+in table row: iqa team` - NOT EXPLAINED
- fda-cp-7346-832-preapproval-inspections.pdf page 48 (uncovered): `+in table row: adequacy` - NOT EXPLAINED
- fda-cp-7346-832-preapproval-inspections.pdf page 48 (uncovered): `+in table row: supplier s qualifications ongoing qc testing` - NOT EXPLAINED
- fda-cp-7346-832-preapproval-inspections.pdf page 48 (uncovered): `+in table row: storage handling` - NOT EXPLAINED
- fda-cp-7346-832-preapproval-inspections.pdf page 48 (uncovered): `+in table row: procedures` - NOT EXPLAINED
- fda-cp-7346-832-preapproval-inspections.pdf page 48 (uncovered): `+in table row: cont next page` - NOT EXPLAINED
- fda-cp-7346-832-preapproval-inspections.pdf page 49 (uncovered): `+addressing quality related topics via an integrated approach quality topic integrated approach` - NOT EXPLAINED
- fda-cp-7346-832-preapproval-inspections.pdf page 49 (uncovered): `+in table row: cont next page` - NOT EXPLAINED
- fda-cp-7346-832-preapproval-inspections.pdf page 50 (uncovered): `+in table row: addressing` - NOT EXPLAINED
- fda-cp-7346-832-preapproval-inspections.pdf page 50 (uncovered): `+related topics via an integrated approach quality topic integrated approach` - NOT EXPLAINED
- fda-cp-7346-832-preapproval-inspections.pdf page 50 (uncovered): `+in table row: cont next page` - NOT EXPLAINED
- fda-cp-7346-832-preapproval-inspections.pdf page 51 (uncovered): `+in table row: addressing` - NOT EXPLAINED
- fda-cp-7346-832-preapproval-inspections.pdf page 51 (uncovered): `+related topics via an integrated approach quality topic integrated approach` - NOT EXPLAINED
- fda-cp-7346-832-preapproval-inspections.pdf page 51 (uncovered): `+in table row: evaluates` - NOT EXPLAINED
- fda-cp-7346-832-preapproval-inspections.pdf page 51 (uncovered): `+in table row: facility for conformance` - NOT EXPLAINED
- fda-cp-7346-832-preapproval-inspections.pdf page 51 (uncovered): `+in table row: cgmp` - NOT EXPLAINED
- fda-cp-7346-832-preapproval-inspections.pdf page 51 (uncovered): `+in table row: objectives of this compliance program` - NOT EXPLAINED
- fda-cp-7346-832-preapproval-inspections.pdf page 51 (uncovered): `+in table row: risks` - NOT EXPLAINED
- fda-cp-7346-832-preapproval-inspections.pdf page 51 (uncovered): `+in table row: concerns identified by` - NOT EXPLAINED
- fda-cp-7346-832-preapproval-inspections.pdf page 51 (uncovered): `+in table row: inspection` - NOT EXPLAINED
- fda-cp-7346-832-preapproval-inspections.pdf page 51 (uncovered): `+in table row: with the` - NOT EXPLAINED
- fda-cp-7346-832-preapproval-inspections.pdf page 51 (uncovered): `+in table row: inspection team lead or pam provides the` - NOT EXPLAINED
- fda-cp-7346-832-preapproval-inspections.pdf page 51 (uncovered): `+in table row: team with its initial facility recommendation the iqa team assesses the inspection findings and their` - NOT EXPLAINED
- fda-cp-7346-832-preapproval-inspections.pdf page 51 (uncovered): `+in table row: on the` - NOT EXPLAINED
- fda-cp-7346-832-preapproval-inspections.pdf page 51 (uncovered): `+in table row: control strategy` - NOT EXPLAINED
- fda-cp-7346-832-preapproval-inspections.pdf page 51 (uncovered): `+in table row: make the quality recommendation if the inspection findings` - NOT EXPLAINED
- fda-cp-7346-832-preapproval-inspections.pdf page 51 (uncovered): `+in table row: and` - NOT EXPLAINED
- fda-cp-7346-832-preapproval-inspections.pdf page 51 (uncovered): `+in table row: impact` - NOT EXPLAINED
- fda-cp-7346-832-preapproval-inspections.pdf page 51 (uncovered): `+in table row: quality cder on behalf of the iqa team` - NOT EXPLAINED
- fda-cp-7346-832-preapproval-inspections.pdf page 51 (uncovered): `+in table row: communicate with the` - NOT EXPLAINED
- fda-cp-7346-832-preapproval-inspections.pdf page 51 (uncovered): `+in table row: or inspected facility as appropriate the iqa team may` - NOT EXPLAINED
- fda-cp-7346-832-preapproval-inspections.pdf page 51 (uncovered): `+in table row: the applicant` - NOT EXPLAINED
- fda-cp-7346-832-preapproval-inspections.pdf page 51 (uncovered): `+in table row: the` - NOT EXPLAINED
- fda-cp-7346-832-preapproval-inspections.pdf page 51 (uncovered): `+in table row: and the` - NOT EXPLAINED
- fda-cp-7346-832-preapproval-inspections.pdf page 51 (uncovered): `+in table row: control strategy` - NOT EXPLAINED
- fda-cp-7346-832-preapproval-inspections.pdf page 51 (uncovered): `+in table row: the` - NOT EXPLAINED
- fda-cp-7346-832-preapproval-inspections.pdf page 51 (uncovered): `+in table row: cont next page` - NOT EXPLAINED
- fda-cp-7346-832-preapproval-inspections.pdf page 52 (uncovered): `+addressing quality related topics via an integrated approach quality topic integrated approach` - NOT EXPLAINED
- fda-cp-7346-832-preapproval-inspections.pdf page 52 (uncovered): `+in table row: iqa team` - NOT EXPLAINED
- fda-cp-7346-832-preapproval-inspections.pdf page 52 (uncovered): `+in table row: manufacturing and control of finished product parametric release for terminally sterilized drug products the iqa team assesses the overall drug product control strategy including parametric release included in the application e g proposed terminal sterilization cycle critical process ` - NOT EXPLAINED
- fda-cp-7346-832-preapproval-inspections.pdf page 52 (uncovered): `+in table row: e g preventative maintenance program facility equipment quality system investigations and batch release` - NOT EXPLAINED
- fda-cp-7346-832-preapproval-inspections.pdf page 52 (uncovered): `+in table row: and compliance program 7356.002 a` - NOT EXPLAINED
- fda-cp-7346-832-preapproval-inspections.pdf page 52 (uncovered): `+in table row: regarding` - NOT EXPLAINED
- fda-cp-7346-832-preapproval-inspections.pdf page 52 (uncovered): `+in table row: parametric release` - NOT EXPLAINED
- fda-cp-7346-832-preapproval-inspections.pdf page 52 (uncovered): `+in table row: parametric release` - NOT EXPLAINED
- fda-cp-7346-832-preapproval-inspections.pdf page 52 (uncovered): `+in table row: include` - NOT EXPLAINED
- fda-cp-7346-832-preapproval-inspections.pdf page 52 (uncovered): `+in table row: issues related to validation data` - NOT EXPLAINED
- fda-cp-7346-832-preapproval-inspections.pdf page 53 (uncovered): `+in table row: addressing` - NOT EXPLAINED
- fda-cp-7346-832-preapproval-inspections.pdf page 53 (uncovered): `+in table row: topics via an integrated approach` - NOT EXPLAINED
- fda-cp-7346-832-preapproval-inspections.pdf page 53 (uncovered): `+in table row: topic integrated approach` - NOT EXPLAINED
- fda-cp-7346-832-preapproval-inspections.pdf page 53 (uncovered): `+in table row: cont next page` - NOT EXPLAINED
- fda-cp-7346-832-preapproval-inspections.pdf page 53 (uncovered): `+in table row: assurance` - NOT EXPLAINED
- fda-cp-7346-832-preapproval-inspections.pdf page 53 (uncovered): `+in table row: sterile` - NOT EXPLAINED
- fda-cp-7346-832-preapproval-inspections.pdf page 53 (uncovered): `+in table row: sterility` - NOT EXPLAINED
- fda-cp-7346-832-preapproval-inspections.pdf page 53 (uncovered): `+and assurance information provided` - NOT EXPLAINED
- fda-cp-7346-832-preapproval-inspections.pdf page 53 (uncovered): `+in table row: suitability of` - NOT EXPLAINED
- fda-cp-7346-832-preapproval-inspections.pdf page 53 (uncovered): `+in table row: selected methods of` - NOT EXPLAINED
- fda-cp-7346-832-preapproval-inspections.pdf page 53 (uncovered): `+in table row: adequacy of` - NOT EXPLAINED
- fda-cp-7346-832-preapproval-inspections.pdf page 53 (uncovered): `+test method selection specifications` - NOT EXPLAINED
- fda-cp-7346-832-preapproval-inspections.pdf page 53 (uncovered): `+in table row: sterility assurance` - NOT EXPLAINED
- fda-cp-7346-832-preapproval-inspections.pdf page 53 (uncovered): `+in table row: example` - NOT EXPLAINED
- fda-cp-7346-832-preapproval-inspections.pdf page 53 (uncovered): `+inspection team evaluates the state of` - NOT EXPLAINED
- fda-cp-7346-832-preapproval-inspections.pdf page 53 (uncovered): `+in table row: of the` - NOT EXPLAINED
- fda-cp-7346-832-preapproval-inspections.pdf page 53 (uncovered): `+in table row: well` - NOT EXPLAINED
- fda-cp-7346-832-preapproval-inspections.pdf page 53 (uncovered): `+the manufacturing procedures practices` - NOT EXPLAINED
- fda-cp-7346-832-preapproval-inspections.pdf page 53 (uncovered): `+in table row: employed` - NOT EXPLAINED
- fda-cp-7346-832-preapproval-inspections.pdf page 53 (uncovered): `+in table row: ensure` - NOT EXPLAINED
- fda-cp-7346-832-preapproval-inspections.pdf page 53 (uncovered): `+sterility the inspection team also evaluates` - NOT EXPLAINED
- fda-cp-7346-832-preapproval-inspections.pdf page 53 (uncovered): `+in table row: sterility assurance` - NOT EXPLAINED
- fda-cp-7346-832-preapproval-inspections.pdf page 53 (uncovered): `+are about the aseptic` - NOT EXPLAINED
- fda-cp-7346-832-preapproval-inspections.pdf page 53 (uncovered): `+in table row: sterility assurance` - NOT EXPLAINED
- fda-cp-7346-832-preapproval-inspections.pdf page 53 (uncovered): `+example the iqa team identifies risks and concerns regarding the sterilization process and controls for sterility assurance` - NOT EXPLAINED
- fda-cp-7346-832-preapproval-inspections.pdf page 53 (uncovered): `+environmental monitoring program media fill process` - NOT EXPLAINED
- fda-cp-7346-832-preapproval-inspections.pdf page 53 (uncovered): `+in table row: and communicates them` - NOT EXPLAINED
- fda-cp-7346-832-preapproval-inspections.pdf page 53 (uncovered): `+in table row: inspection team the inspection team finds` - NOT EXPLAINED
- fda-cp-7346-832-preapproval-inspections.pdf page 53 (uncovered): `+the aseptic processing area is deficient regarding the environmental monitoring program and includes its observations on form fda 483 the iqa team uses the inspection findings to request` - NOT EXPLAINED
- fda-cp-7346-832-preapproval-inspections.pdf page 53 (uncovered): `+in table row: the` - NOT EXPLAINED
- fda-cp-7346-832-preapproval-inspections.pdf page 53 (uncovered): `+update its environmental monitoring program to address the risks to sterility assurance of the product cont next page` - NOT EXPLAINED
- fda-cp-7346-832-preapproval-inspections.pdf page 37 (uncovered): `+next to Part VI: references` - NOT EXPLAINED
- fda-cp-7346-832-preapproval-inspections.pdf page 37 (uncovered): `+next to Part VI A: references` - NOT EXPLAINED
- fda-cp-7346-832-preapproval-inspections.pdf page 43 (uncovered): `+in two clauses Part VII and _unnumbered:6: part vii center and oii responsibilities cder and oii redefined their roles and responsibilities regarding application assessments and inspections of` - NOT EXPLAINED
- fda-cp-7356-002-drug-manufacturing-inspections.pdf _unnumbered:1 (unnumbered): `-food and drug administration compliance program program 7356.002 chapter 56 drug quality assurance 1 we update guidances periodically for the most recent version of a guidance check the fda guidance web page at https www fda gov regulatory information search fda guidance documents` - Front matter (cover page, document history, contents): the two engines read the cover's text boxes, address blocks and history table in different orders; not regulation text.
- fda-cp-7356-002-drug-manufacturing-inspections.pdf Part IV 2 (clause): `+23` - A footnote reference number (verified: it starts a line or is printed small on the clause's pages) that the parser drops with the footnote mark; no regulation word changes.
- fda-cp-7356-002-drug-manufacturing-inspections.pdf Part VI 3.B (clause): `-cms compliance management | -system | -dqrs drug quality reporting system | -ec established condition | -eir establishment inspection report | +research cgmp current good manufacturing practice cms compliance management system dqrs drug quality reporting system ec established condition eir establis` - NOT EXPLAINED
- fda-cp-7356-002-drug-manufacturing-inspections.pdf Attachment A (clause): `-attachment a remote regulatory assessments` - Order or place only (verified mechanically): every stored word run of this discrepancy is printed on the clause's pages, and every page run it lacks is stored word for word (in this clause or another), so no word is lost or added; the engines read table cells, columns or figure labels in different orders.
- fda-cp-7356-002-drug-manufacturing-inspections.pdf page 38 (uncovered): `+opq office of pharmaceutical quality oqs office of quality surveillance ora office of regulatory affairs ors office of regulatory science pac product assignment code pam preapproval program manager pet positron emission tomography plcm product lifecycle management poai potential official action ind` - NOT EXPLAINED
- fda-cp-7356-002-drug-manufacturing-inspections.pdf page 41 (uncovered): `+its inspectional authority` - NOT EXPLAINED
- fda-cp-7356-002-drug-manufacturing-inspections.pdf page 41 (uncovered): `+an rra is an examination of an fda regulated establishment and or its` - Text read outside any clause's stretch that is stored word for word in another clause of the document (verified mechanically): a running title, table caption or text read in another order.
- fda-cp-7356-002a-sterile-drug-process.pdf _unnumbered:1 (unnumbered): `-food and drug administration program 7356.002 a compliance program guidance manual chapter 56 drug quality assurance` - Order or place only (verified mechanically): every stored word run of this discrepancy is printed on the clause's pages, and every page run it lacks is stored word for word (in this clause or another), so no word is lost or added; the engines read table cells, columns or figure labels in different orders.
- fda-cp-7356-002a-sterile-drug-process.pdf Part II 2.2.C (clause): `-end part ii` - NOT EXPLAINED
- fda-cp-7356-002a-sterile-drug-process.pdf Part VII B (clause): `-moist heat sterilization | +moist heat sterilization | -sterilization depyrogenation dry heat | +dry heat sterilization depyrogenation | -aseptic filling | +aseptic filling | -lyophilization freeze drying | +lyophilization freeze drying | -isolator barrier technology | +isolator barrier technology ` - NOT EXPLAINED
- fda-cp-7356-002a-sterile-drug-process.pdf page 6 (uncovered): `+in two clauses Part II 2.2.A and Part III: part iii inspectional` - NOT EXPLAINED
- fda-cp-7356-002f-api.pdf _unnumbered:1 (unnumbered): `-food and drug administration compliance program program 7356.002 f chapter 56 drug quality assurance` - Front matter (cover page, document history, contents): the two engines read the cover's text boxes, address blocks and history table in different orders; not regulation text.
- fda-cp-7356-002f-api.pdf Part I 2 (clause): `+7 | +10` - A footnote reference number (verified: it starts a line or is printed small on the clause's pages) that the parser drops with the footnote mark; no regulation word changes.
- fda-cp-7356-002f-api.pdf Part III 1.B (clause): `+28 | +35` - A footnote reference number (verified: it starts a line or is printed small on the clause's pages) that the parser drops with the footnote mark; no regulation word changes.
- fda-cp-7356-002f-api.pdf Part III 1.C (clause): `+38` - A footnote reference number (verified: it starts a line or is printed small on the clause's pages) that the parser drops with the footnote mark; no regulation word changes.
- fda-cp-7356-002f-api.pdf Part VI 1 (clause): `+41` - A footnote reference number (verified: it starts a line or is printed small on the clause's pages) that the parser drops with the footnote mark; no regulation word changes.
- fda-cp-7356-021-dqrs-field-alerts.pdf _unnumbered:1 (unnumbered): `-food and drug administration compliance program guidance manual 7356.021 chapter 56 drug quality assurance` - Front matter (cover page, document history, contents): the two engines read the cover's text boxes, address blocks and history table in different orders; not regulation text.
- fda-cp-7356-021-dqrs-field-alerts.pdf page 1 (uncovered): `+food and drug administration chapter 56 drug quality assurance` - NOT EXPLAINED
- fda-cp-7356-021-dqrs-field-alerts.pdf page 1 (uncovered): `+7356.021 compliance program guidance manual` - NOT EXPLAINED
- fda-cp-7356-843-postapproval-inspections.pdf _unnumbered:1 (unnumbered): `-food and drug administration compliance program program 7356.843 chapter 56 drug quality assurance` - Front matter (cover page, document history, contents): the two engines read the cover's text boxes, address blocks and history table in different orders; not regulation text.
- fda-cp-7356-843-postapproval-inspections.pdf Part II 4.A (clause): `+27` - A footnote reference number (verified: it starts a line or is printed small on the clause's pages) that the parser drops with the footnote mark; no regulation word changes.
- fda-cp-7356-843-postapproval-inspections.pdf Part VI 4 (clause): `-cder center for drug evaluation and | -research | +anda abbreviated new drug application api active pharmaceutical ingredient capa corrective action and preventive action cbe changes being effected cder center for drug evaluation and research | -anda abbreviated new drug application | -api active p` - NOT EXPLAINED
- fda-data-integrity-2018.pdf III.1.f (clause): `+8` - A footnote reference number (verified: it starts a line or is printed small on the clause's pages) that the parser drops with the footnote mark; no regulation word changes.
- fda-guidance-analytical-procedures-validation-2015.pdf _unnumbered:1 (unnumbered): `-2015 | -3128 | -2015` - Front matter (cover page, document history, contents): the two engines read the cover's text boxes, address blocks and history table in different orders; not regulation text.
- fda-guidance-analytical-procedures-validation-2015.pdf _unnumbered:2 (unnumbered): `-1 4 5 | -11 12 13` - Front matter (cover page, document history, contents): the two engines read the cover's text boxes, address blocks and history table in different orders; not regulation text.
- fda-guidance-analytical-procedures-validation-2015.pdf I (clause): `-27 | -31 | -46 | -52 | -55 | -61 | -65 | -71 72` - Parser defect (0b): margin line numbers of this line-numbered FDA guidance are left in the stored text where a line starts a paragraph or follows a footnote (e.g. 'II. BACKGROUND 74 Each NDA'); the guidance words are intact, the numbers are not part of it.
- fda-guidance-analytical-procedures-validation-2015.pdf II (clause): `-74 | -10 82 | -11 86 | -94 95` - Parser defect (0b): margin line numbers of this line-numbered FDA guidance are left in the stored text where a line starts a paragraph or follows a footnote (e.g. 'II. BACKGROUND 74 Each NDA'); the guidance words are intact, the numbers are not part of it.
- fda-guidance-analytical-procedures-validation-2015.pdf III (clause): `-97 | -104 | -112 | -121 122 | +11` - NOT EXPLAINED
- fda-guidance-analytical-procedures-validation-2015.pdf IV (clause): `-133` - Parser defect (0b): margin line numbers of this line-numbered FDA guidance are left in the stored text where a line starts a paragraph or follows a footnote (e.g. 'II. BACKGROUND 74 Each NDA'); the guidance words are intact, the numbers are not part of it.
- fda-guidance-analytical-procedures-validation-2015.pdf IV.A (clause): `-135 | -139` - Parser defect (0b): margin line numbers of this line-numbered FDA guidance are left in the stored text where a line starts a paragraph or follows a footnote (e.g. 'II. BACKGROUND 74 Each NDA'); the guidance words are intact, the numbers are not part of it.
- fda-guidance-analytical-procedures-validation-2015.pdf IV.B (clause): `-141 | -144` - Parser defect (0b): margin line numbers of this line-numbered FDA guidance are left in the stored text where a line starts a paragraph or follows a footnote (e.g. 'II. BACKGROUND 74 Each NDA'); the guidance words are intact, the numbers are not part of it.
- fda-guidance-analytical-procedures-validation-2015.pdf IV.C (clause): `-146 | -151` - Parser defect (0b): margin line numbers of this line-numbered FDA guidance are left in the stored text where a line starts a paragraph or follows a footnote (e.g. 'II. BACKGROUND 74 Each NDA'); the guidance words are intact, the numbers are not part of it.
- fda-guidance-analytical-procedures-validation-2015.pdf IV.D (clause): `-153 | -155 | -170` - Parser defect (0b): margin line numbers of this line-numbered FDA guidance are left in the stored text where a line starts a paragraph or follows a footnote (e.g. 'II. BACKGROUND 74 Each NDA'); the guidance words are intact, the numbers are not part of it.
- fda-guidance-analytical-procedures-validation-2015.pdf IV.E (clause): `-172 | -178` - Parser defect (0b): margin line numbers of this line-numbered FDA guidance are left in the stored text where a line starts a paragraph or follows a footnote (e.g. 'II. BACKGROUND 74 Each NDA'); the guidance words are intact, the numbers are not part of it.
- fda-guidance-analytical-procedures-validation-2015.pdf IV.F (clause): `-180 | -184` - Parser defect (0b): margin line numbers of this line-numbered FDA guidance are left in the stored text where a line starts a paragraph or follows a footnote (e.g. 'II. BACKGROUND 74 Each NDA'); the guidance words are intact, the numbers are not part of it.
- fda-guidance-analytical-procedures-validation-2015.pdf IV.G (clause): `-186 | -191` - Parser defect (0b): margin line numbers of this line-numbered FDA guidance are left in the stored text where a line starts a paragraph or follows a footnote (e.g. 'II. BACKGROUND 74 Each NDA'); the guidance words are intact, the numbers are not part of it.
- fda-guidance-analytical-procedures-validation-2015.pdf IV.H (clause): `-193 | -201` - Parser defect (0b): margin line numbers of this line-numbered FDA guidance are left in the stored text where a line starts a paragraph or follows a footnote (e.g. 'II. BACKGROUND 74 Each NDA'); the guidance words are intact, the numbers are not part of it.
- fda-guidance-analytical-procedures-validation-2015.pdf IV.I (clause): `-203` - Parser defect (0b): margin line numbers of this line-numbered FDA guidance are left in the stored text where a line starts a paragraph or follows a footnote (e.g. 'II. BACKGROUND 74 Each NDA'); the guidance words are intact, the numbers are not part of it.
- fda-guidance-analytical-procedures-validation-2015.pdf IV.J (clause): `-220 221` - Parser defect (0b): margin line numbers of this line-numbered FDA guidance are left in the stored text where a line starts a paragraph or follows a footnote (e.g. 'II. BACKGROUND 74 Each NDA'); the guidance words are intact, the numbers are not part of it.
- fda-guidance-analytical-procedures-validation-2015.pdf V (clause): `-223 | -236 | -248 | -255 256` - Parser defect (0b): margin line numbers of this line-numbered FDA guidance are left in the stored text where a line starts a paragraph or follows a footnote (e.g. 'II. BACKGROUND 74 Each NDA'); the guidance words are intact, the numbers are not part of it.
- fda-guidance-analytical-procedures-validation-2015.pdf VI (clause): `-258` - Parser defect (0b): margin line numbers of this line-numbered FDA guidance are left in the stored text where a line starts a paragraph or follows a footnote (e.g. 'II. BACKGROUND 74 Each NDA'); the guidance words are intact, the numbers are not part of it.
- fda-guidance-analytical-procedures-validation-2015.pdf VI.A (clause): `-260 | -271` - Parser defect (0b): margin line numbers of this line-numbered FDA guidance are left in the stored text where a line starts a paragraph or follows a footnote (e.g. 'II. BACKGROUND 74 Each NDA'); the guidance words are intact, the numbers are not part of it.
- fda-guidance-analytical-procedures-validation-2015.pdf VI.B (clause): `-273 | -276 | -284 | -288 | -296 | -15 302 | -16 306` - Parser defect (0b): margin line numbers of this line-numbered FDA guidance are left in the stored text where a line starts a paragraph or follows a footnote (e.g. 'II. BACKGROUND 74 Each NDA'); the guidance words are intact, the numbers are not part of it.
- fda-guidance-analytical-procedures-validation-2015.pdf VI.C (clause): `-308 | -314 | -327 328` - Parser defect (0b): margin line numbers of this line-numbered FDA guidance are left in the stored text where a line starts a paragraph or follows a footnote (e.g. 'II. BACKGROUND 74 Each NDA'); the guidance words are intact, the numbers are not part of it.
- fda-guidance-analytical-procedures-validation-2015.pdf VII (clause): `-330` - Parser defect (0b): margin line numbers of this line-numbered FDA guidance are left in the stored text where a line starts a paragraph or follows a footnote (e.g. 'II. BACKGROUND 74 Each NDA'); the guidance words are intact, the numbers are not part of it.
- fda-guidance-analytical-procedures-validation-2015.pdf VII.A (clause): `-332 | +17 | -349` - Parser defect (0b): margin line numbers of this line-numbered FDA guidance are left in the stored text where a line starts a paragraph or follows a footnote (e.g. 'II. BACKGROUND 74 Each NDA'); the guidance words are intact, the numbers are not part of it.
- fda-guidance-analytical-procedures-validation-2015.pdf VII.B (clause): `-351 | -356 357` - Parser defect (0b): margin line numbers of this line-numbered FDA guidance are left in the stored text where a line starts a paragraph or follows a footnote (e.g. 'II. BACKGROUND 74 Each NDA'); the guidance words are intact, the numbers are not part of it.
- fda-guidance-analytical-procedures-validation-2015.pdf VIII (clause): `-359 | -368 | -375 | -382 | -389` - Parser defect (0b): margin line numbers of this line-numbered FDA guidance are left in the stored text where a line starts a paragraph or follows a footnote (e.g. 'II. BACKGROUND 74 Each NDA'); the guidance words are intact, the numbers are not part of it.
- fda-guidance-analytical-procedures-validation-2015.pdf VIII.A (clause): `-391 | -399 | -403` - Parser defect (0b): margin line numbers of this line-numbered FDA guidance are left in the stored text where a line starts a paragraph or follows a footnote (e.g. 'II. BACKGROUND 74 Each NDA'); the guidance words are intact, the numbers are not part of it.
- fda-guidance-analytical-procedures-validation-2015.pdf VIII.B (clause): `-405 | -411` - Parser defect (0b): margin line numbers of this line-numbered FDA guidance are left in the stored text where a line starts a paragraph or follows a footnote (e.g. 'II. BACKGROUND 74 Each NDA'); the guidance words are intact, the numbers are not part of it.
- fda-guidance-analytical-procedures-validation-2015.pdf VIII.B.1 (clause): `-413 | -21 422 | -22 432 | -437 | -440 | -443 | -449 | -451 | -464` - Parser defect (0b): margin line numbers of this line-numbered FDA guidance are left in the stored text where a line starts a paragraph or follows a footnote (e.g. 'II. BACKGROUND 74 Each NDA'); the guidance words are intact, the numbers are not part of it.
- fda-guidance-analytical-procedures-validation-2015.pdf VIII.B.2 (clause): `-466 | -478` - Parser defect (0b): margin line numbers of this line-numbered FDA guidance are left in the stored text where a line starts a paragraph or follows a footnote (e.g. 'II. BACKGROUND 74 Each NDA'); the guidance words are intact, the numbers are not part of it.
- fda-guidance-analytical-procedures-validation-2015.pdf VIII.C (clause): `-480 | -489 490` - Parser defect (0b): margin line numbers of this line-numbered FDA guidance are left in the stored text where a line starts a paragraph or follows a footnote (e.g. 'II. BACKGROUND 74 Each NDA'); the guidance words are intact, the numbers are not part of it.
- fda-guidance-analytical-procedures-validation-2015.pdf IX (clause): `-492 | -500 | -507` - Parser defect (0b): margin line numbers of this line-numbered FDA guidance are left in the stored text where a line starts a paragraph or follows a footnote (e.g. 'II. BACKGROUND 74 Each NDA'); the guidance words are intact, the numbers are not part of it.
- fda-guidance-analytical-procedures-validation-2015.pdf X (clause): `-513 | -515 | -517 | -520 | -523 | -527 | -530 | -533 | -536 | -538 | -540 | -543 | -547 | -550 | -552 | -554 | -556 | -558 | -560 | -562 | -565 | -568 | -571 | -574 | -576 | -578 | -580 | -582 | -584 | -586 | -592 | -594 | -598 | -601 | -604 | -607 | -610 | -613 614 615` - Parser defect (0b): margin line numbers of this line-numbered FDA guidance are left in the stored text where a line starts a paragraph or follows a footnote (e.g. 'II. BACKGROUND 74 Each NDA'); the guidance words are intact, the numbers are not part of it.
- fda-guidance-analytical-procedures-validation-2015.pdf page 4 (uncovered): `+next to _unnumbered:2: i introduction` - NOT EXPLAINED
- fda-guidance-analytical-procedures-validation-2015.pdf page 4 (uncovered): `+next to I: introduction i` - NOT EXPLAINED
- fda-guidance-anda-stability-2013.pdf _unnumbered:1 (unnumbered): `-guidance for industry | -guidance for industry` - Order or place only (verified mechanically): every stored word run of this discrepancy is printed on the clause's pages, and every page run it lacks is stored word for word (in this clause or another), so no word is lost or added; the engines read table cells, columns or figure labels in different orders.
- fda-guidance-anda-stability-2013.pdf _unnumbered:2 (unnumbered): `-guidance for industry` - Order or place only (verified mechanically): every stored word run of this discrepancy is printed on the clause's pages, and every page run it lacks is stored word for word (in this clause or another), so no word is lost or added; the engines read table cells, columns or figure labels in different orders.
- fda-guidance-benzene-carbomers-2023.pdf III (clause): `+11 | -cbe 30 changes being effected in 30 days pas prior approval supplement` - NOT EXPLAINED
- fda-guidance-cci-in-lieu-of-sterility-2008.pdf V (clause): `+4` - A footnote reference number (verified: it starts a line or is printed small on the clause's pages) that the parser drops with the footnote mark; no regulation word changes.
- fda-guidance-changes-approved-nda-anda-2004.pdf _unnumbered:1 (unnumbered): `+15 20` - Front matter (cover page, document history, contents): the two engines read the cover's text boxes, address blocks and history table in different orders; not regulation text.
- fda-guidance-changes-approved-nda-anda-2004.pdf VII.B (clause): `+16 for the purposes of this guidance natural product refers to materials e g drug substance excipients that are derived from plants animals or microorganisms and that are subject to approval under section 505 of the act the specific recommendations for natural products are not applicable to inorgan` - NOT EXPLAINED
- fda-guidance-container-closure-systems-1999.pdf _unnumbered:2 (unnumbered): `-guidance for industry 1 container closure systems for packaging human drugs and biologics chemistry manufacturing and controls documentation` - Order or place only (verified mechanically): every stored word run of this discrepancy is printed on the clause's pages, and every page run it lacks is stored word for word (in this clause or another), so no word is lost or added; the engines read table cells, columns or figure labels in different orders.
- fda-guidance-container-closure-systems-1999.pdf I (clause): `-i introduction this document is intended to provide guidance on general principles 2 for submitting information on | +that concern | -materials used for human drugs and biologics 3 this guidance supersedes the fda guideline for submitting documentation for packaging for human drugs and biologics is` - NOT EXPLAINED
- fda-guidance-container-closure-systems-1999.pdf II.A (clause): `-5 these definitions are intended to clarify | -use | +materials | -certain terms in this guidance only and are not intended to supersede the definitions of container and package as provided for in 21 cfr 600.3 6 this term is | +construction | +the labeling are | -general sense for | +concern from a` - NOT EXPLAINED
- fda-guidance-container-closure-systems-1999.pdf II.B (clause): `-7 the materials of construction used in the labeling are a concern from a packaging perspective if they affect the protection and or safety of the drug product` - NOT EXPLAINED
- fda-guidance-container-closure-systems-1999.pdf II.C.2 (clause): `+this discussion does not apply to the repackaging of drug products for dispensing under the practice of pharmacy 8 fda compliance policy guides expiration dating of unit repackaged drugs 480.200 february 1 1984 rev 9 march 1995 cpg 7132 b 11 fda compliance policy guides regulatory action regarding ` - NOT EXPLAINED
- fda-guidance-container-closure-systems-1999.pdf III.A (clause): `-8 this discussion does not apply to the repackaging of drug products for dispensing under the practice of pharmacy 9 fda compliance policy guides expiration dating of unit repackaged drugs 480.200 february 1 1984 rev march 1995 cpg 7132 b 11 10 fda compliance policy guides regulatory action regardi` - NOT EXPLAINED
- fda-guidance-container-closure-systems-1999.pdf III.B.1 (clause): `+for further information regarding photostability studies see the fda guideline for the photostability testing of new 11 drug substances and products may 1997 | -11 for further information regarding photostability studies see the fda guideline for the photostability testing of new drug substances an` - NOT EXPLAINED
- fda-guidance-container-closure-systems-1999.pdf III.B.2 (clause): `+these are substances not previously determined to be safe by extraction toxicological evaluation studies e g the usp 14 biological reactivity tests or another appropriate method conducted on the packaging component as part of the qualifying process | -these are substances not previously determined ` - NOT EXPLAINED
- fda-guidance-container-closure-systems-1999.pdf III.C.2 (clause): `-2 information about suitability 15 | +c information that should be submitted in support of an original application for any drug product 15 additional discussion and information regarding the cmc information to be provided in an application nda anda or bla can be found in the guidances and guideline` - NOT EXPLAINED
- fda-guidance-container-closure-systems-1999.pdf III.C.3 (clause): `+statistical process control is defined as t he application of statistical techniques for measuring and analyzing the 18 variation in processes juran j m ed 1988 quality control handbook 4 th ed mcgraw hill p 24.2` - NOT EXPLAINED
- fda-guidance-container-closure-systems-1999.pdf III.C.4 (clause): `-4 stability data packaging concerns stability testing of the drug product should be conducted using the container 18 statistical process control is defined as t he application of statistical techniques for measuring and analyzing the variation in processes juran j m ed 1988 quality control handbook` - NOT EXPLAINED
- fda-guidance-container-closure-systems-1999.pdf III.E.1 (clause): `-19 the terms svp and lvp as used in this guidance correspond to the definitions of small volume injection and large volume injection respectively in usp 23 page 1650` - NOT EXPLAINED
- fda-guidance-container-closure-systems-1999.pdf III.E.2 (clause): `-a including any additives used in the manufacture of a packaging component b testing for plastics should be performed on the packaging component not on the unformed resin c note that applicant s acceptance tests may include among others test parameters indicated under the description suitability an` - NOT EXPLAINED
- fda-guidance-container-closure-systems-1999.pdf III.F (clause): `+see attachment a for a listing of the fda regulations for indirect food additives 20` - NOT EXPLAINED
- fda-guidance-container-closure-systems-1999.pdf III.F.1 (clause): `-a | +c | -listing | +discussion | -the fda regulations for indirect food additives | +extraction studies 21` - NOT EXPLAINED
- fda-guidance-container-closure-systems-1999.pdf III.F.2 (clause): `-see attachment c for a discussion of extraction studies` - Order or place only (verified mechanically): every stored word run of this discrepancy is printed on the clause's pages, and every page run it lacks is stored word for word (in this clause or another), so no word is lost or added; the engines read table cells, columns or figure labels in different orders.
- fda-guidance-container-closure-systems-1999.pdf III.F.3 (clause): `-a including any additives used in the manufacture of a packaging component b the materials of construction should be acceptable for contact with foods that have extraction characteristics similar to those of the drug product e g aqueous acidic alcoholic or fatty c plastics testing should be perform` - NOT EXPLAINED
- fda-guidance-container-closure-systems-1999.pdf III.G (clause): `+hartauer k j et al the effects of rayon coiler on the dissolution stability of hard shelled gelatin capsules 22 pharmaceutical technology 17 76 83 1993 | -22 hartauer k j et al the effects of rayon coiler on the dissolution stability of hard shelled gelatin capsules pharmaceutical technology 17 76 ` - NOT EXPLAINED
- fda-guidance-container-closure-systems-1999.pdf VI.A (clause): `+the 1987 stability guidance will be superseded by the fda guidance for industry stability testing of drug 23 substances and drug products issued in draft for comment in june 1998 once it is issued in final form` - NOT EXPLAINED
- fda-guidance-container-closure-systems-1999.pdf VI.B (clause): `-23 the 1987 stability guidance will be superseded by the | -guidance for industry stability testing of drug substances | +compliance policy guides regulatory action regarding approved new drugs | +antibiotic | -issued in draft for comment in june 1998 once it is issued in final form | +24 subjected` - NOT EXPLAINED
- fda-guidance-container-closure-systems-1999.pdf Attachment A (clause): `-applicants should check the appropriate sources directly for the most up to date information | -1 | +2 | +federal register volume 49 march 5 1984 page 8008 49 fr 8008 prescribed drugs distributed to prescribing 26 practitioners withdrawal of proposed statement of policy and interpretation | -2 | +3` - NOT EXPLAINED
- fda-guidance-container-closure-systems-1999.pdf Attachment B (clause): `-1 | +2 | -b 2` - NOT EXPLAINED
- fda-guidance-container-closure-systems-1999.pdf Attachment C (clause): `-c | +d` - NOT EXPLAINED
- fda-guidance-container-closure-systems-1999.pdf _unnumbered:4 (unnumbered): `-d 1` - NOT EXPLAINED
- fda-guidance-container-closure-systems-1999.pdf Attachment E (clause): `-27 a list of cder and cber guidances and guidelines is provided on the internet at www fda gov cder guidances index htm and www fda gov cber guidelines htm respectively | -1 | +2 | -e 2` - NOT EXPLAINED
- fda-guidance-container-closure-systems-1999.pdf Table 1 Highest (table_row): `-suspensions a` - NOT EXPLAINED
- fda-guidance-container-closure-systems-1999.pdf Table 2 Route of Administration/ Dosage Form (table_row): `-delivery` - NOT EXPLAINED
- fda-guidance-container-closure-systems-1999.pdf Table 2 Oral Tablets and Oral (Hard and Soft… (table_row): `-capsules` - NOT EXPLAINED
- fda-guidance-container-closure-systems-1999.pdf page 4 (uncovered): `+guidance for industry 1 container closure systems for packaging human drugs and biologics chemistry manufacturing and controls documentation i introduction this document is intended to provide guidance on general principles for submitting information` - NOT EXPLAINED
- fda-guidance-container-closure-systems-1999.pdf page 26 (uncovered): `+in table row: terms svp` - NOT EXPLAINED
- fda-guidance-container-closure-systems-1999.pdf page 26 (uncovered): `+in table row: lvp` - NOT EXPLAINED
- fda-guidance-container-closure-systems-1999.pdf page 26 (uncovered): `+in table row: used` - NOT EXPLAINED
- fda-guidance-container-closure-systems-1999.pdf page 26 (uncovered): `+in table row: this guidance correspond` - NOT EXPLAINED
- fda-guidance-container-closure-systems-1999.pdf page 26 (uncovered): `+in table row: definitions` - NOT EXPLAINED
- fda-guidance-container-closure-systems-1999.pdf page 26 (uncovered): `+in table row: small volume injection` - NOT EXPLAINED
- fda-guidance-container-closure-systems-1999.pdf page 26 (uncovered): `+in table row: large` - NOT EXPLAINED
- fda-guidance-container-closure-systems-1999.pdf page 26 (uncovered): `+in table row: volume injection respectively` - NOT EXPLAINED
- fda-guidance-container-closure-systems-1999.pdf page 3 (uncovered): `+in two clauses I and _unnumbered:2: that concern packaging b 1 attachment c c 1 extraction studies c 1 attachment d d 1 abbreviations d 1 attachment e e 1 references e 1` - NOT EXPLAINED
- fda-guidance-container-closure-systems-1999.pdf page 20 (uncovered): `+in two clauses III.C and III.C.2: c information that should be submitted in support of an original application for any drug product 15 additional discussion and information regarding the cmc information to be provided in an application nda anda or bla can be found in the guidances and guidelines li` - NOT EXPLAINED
- fda-guidance-container-closure-systems-1999.pdf page 45 (uncovered): `+in two clauses Attachment A and VI.B: attachment a 25 regulatory` - NOT EXPLAINED
- fda-guidance-deg-eg-high-risk-components-2023.pdf I (clause): `+1` - A footnote reference number (verified: it starts a line or is printed small on the clause's pages) that the parser drops with the footnote mark; no regulation word changes.
- fda-guidance-delaying-denying-inspection-2024.pdf _unnumbered:2 (unnumbered): `-circumstances that constitute delaying denying limiting or refusing a drug or device inspection` - Order or place only (verified mechanically): every stored word run of this discrepancy is printed on the clause's pages, and every page run it lacks is stored word for word (in this clause or another), so no word is lost or added; the engines read table cells, columns or figure labels in different orders.
- fda-guidance-delaying-denying-inspection-2024.pdf II (clause): `+6` - A footnote reference number (verified: it starts a line or is printed small on the clause's pages) that the parser drops with the footnote mark; no regulation word changes.
- fda-guidance-delaying-denying-inspection-2024.pdf page 4 (uncovered): `+in two clauses I and _unnumbered:2: this guidance represents the current thinking of the food and drug administration fda or agency on this topic it does not establish any rights for any person and is not binding on fda or the public you can use an alternative approach if it satisfies the requireme` - NOT EXPLAINED
- fda-guidance-dissolution-mechanical-calibration-2010.pdf _unnumbered:1 (unnumbered): `-guidance for industry | -guidance for industry | +the use of mechanical calibration` - Front matter (cover page, document history, contents): the two engines read the cover's text boxes, address blocks and history table in different orders; not regulation text.
- fda-guidance-dissolution-mechanical-calibration-2010.pdf _unnumbered:2 (unnumbered): `-guidance for industry | +ii background 2 iii recommendations 3 the use of mechanical calibration` - Front matter (cover page, document history, contents): the two engines read the cover's text boxes, address blocks and history table in different orders; not regulation text.
- fda-guidance-dissolution-mechanical-calibration-2010.pdf II (clause): `-2005,3 | +2005 3` - NOT EXPLAINED
- fda-guidance-elemental-impurities-2018.pdf _unnumbered:1 (unnumbered): `-9073135 fnl 8 1 2018` - Order or place only (verified mechanically): every stored word run of this discrepancy is printed on the clause's pages, and every page run it lacks is stored word for word (in this clause or another), so no word is lost or added; the engines read table cells, columns or figure labels in different orders.
- fda-guidance-elemental-impurities-2018.pdf _unnumbered:2 (unnumbered): `-i` - NOT EXPLAINED
- fda-guidance-elemental-impurities-2018.pdf I (clause): `+1 | +6` - A footnote reference number (verified: it starts a line or is printed small on the clause's pages) that the parser drops with the footnote mark; no regulation word changes.
- fda-guidance-field-alert-report-qa-2021.pdf _unnumbered:2 (unnumbered): `-i` - NOT EXPLAINED
- fda-guidance-field-alert-report-qa-2021.pdf III.1.b (clause): `+13` - A footnote reference number (verified: it starts a line or is printed small on the clause's pages) that the parser drops with the footnote mark; no regulation word changes.
- fda-guidance-melamine-components-2009.pdf _unnumbered:1 (unnumbered): `+pharmaceutical components | +pharmaceutical components` - Front matter (cover page, document history, contents): the two engines read the cover's text boxes, address blocks and history table in different orders; not regulation text.
- fda-guidance-melamine-components-2009.pdf _unnumbered:2 (unnumbered): `-1 | +pharmaceutical components` - Front matter (cover page, document history, contents): the two engines read the cover's text boxes, address blocks and history table in different orders; not regulation text.
- fda-guidance-methanol-testing-alcohol-2023.pdf II (clause): `+19` - A footnote reference number (verified: it starts a line or is printed small on the clause's pages) that the parser drops with the footnote mark; no regulation word changes.
- fda-guidance-methanol-testing-alcohol-2023.pdf III.A (clause): `+34` - A footnote reference number (verified: it starts a line or is printed small on the clause's pages) that the parser drops with the footnote mark; no regulation word changes.
- fda-guidance-nitrosamine-control-2024.pdf _unnumbered:2 (unnumbered): `-ii` - Front matter (cover page, document history, contents): the two engines read the cover's text boxes, address blocks and history table in different orders; not regulation text.
- fda-guidance-nitrosamine-control-2024.pdf III.A (clause): `-1 hno | -h | -n n o x n n o n o r 2 r 2` - NOT EXPLAINED
- fda-guidance-nitrosamine-control-2024.pdf III.A.2 (clause): `+api | -n h api n n o n o` - NOT EXPLAINED
- fda-guidance-nitrosamine-control-2024.pdf III.B.2 (clause): `-n n | -sodium nitrite` - NOT EXPLAINED
- fda-guidance-nitrosamine-control-2024.pdf V.A (clause): `+68` - A footnote reference number (verified: it starts a line or is printed small on the clause's pages) that the parser drops with the footnote mark; no regulation word changes.
- fda-guidance-nitrosamine-control-2024.pdf V.C.2 (clause): `+82` - A footnote reference number (verified: it starts a line or is printed small on the clause's pages) that the parser drops with the footnote mark; no regulation word changes.
- fda-guidance-nitrosamine-control-2024.pdf _unnumbered:3 (unnumbered): `-ity | +voluntarily recall ranitidine and nizatidine products with ndma levels above those fda calculated using the methods in the international council for harmonisation of technical requirements for pharmaceuticals for human use guidance for industry m 7 r 2 assessment and control of dna reactive ` - NOT EXPLAINED
- fda-guidance-nitrosamine-control-2024.pdf Table 2 𝑛𝑛𝑖𝑖=2 𝑋𝑋𝑋𝑋 (table_row): `-nnii xxxx` - NOT EXPLAINED
- fda-guidance-nitrosamine-control-2024.pdf Table 2 ∑ 𝐴𝐴𝐴𝐴𝐴𝐴 ∗ 100% ≤ 100% (table_row): `-aaaaaa` - NOT EXPLAINED
- fda-guidance-nitrosamine-ndsri-ai-limits-2023.pdf III.A (clause): `+20` - A footnote reference number (verified: it starts a line or is printed small on the clause's pages) that the parser drops with the footnote mark; no regulation word changes.
- fda-guidance-nitrosamine-ndsri-ai-limits-2023.pdf IV.A (clause): `+23` - A footnote reference number (verified: it starts a line or is printed small on the clause's pages) that the parser drops with the footnote mark; no regulation word changes.
- fda-guidance-nitrosamine-ndsri-ai-limits-2023.pdf IV.B (clause): `-b specific application of the predicted carcinogenic potency categorization approach fda recommends the following ai limits based on the predicted carcinogenic potency categorization approach for ndsris table 1 shows the predicted carcinogenic potency categories and associated recommended ai limits` - Order or place only (verified mechanically): every stored word run of this discrepancy is printed on the clause's pages, and every page run it lacks is stored word for word (in this clause or another), so no word is lost or added; the engines read table cells, columns or figure labels in different orders.
- fda-guidance-nitrosamine-ndsri-ai-limits-2023.pdf Appendix A (clause): `-potency score α hydrogen score deactivating feature score sum all scores for features present in ndsri activating feature score sum all scores for features present in ndsri | +count of hydrogen atoms on each α carbon lowest first example α hydrogen score 0,2 3 0,3 2 1,2 3 1,3 3 2,2 1 potency score ` - NOT EXPLAINED
- fda-guidance-npbl-cross-contamination-2013.pdf _unnumbered:1 (unnumbered): `-guidance for industry | -guidance for industry` - Order or place only (verified mechanically): every stored word run of this discrepancy is printed on the clause's pages, and every page run it lacks is stored word for word (in this clause or another), so no word is lost or added; the engines read table cells, columns or figure labels in different orders.
- fda-guidance-npbl-cross-contamination-2013.pdf _unnumbered:2 (unnumbered): `-guidance for industry | +introduction` - Front matter (cover page, document history, contents): the two engines read the cover's text boxes, address blocks and history table in different orders; not regulation text.
- fda-guidance-npbl-cross-contamination-2013.pdf II.A (clause): `+4` - A footnote reference number (verified: it starts a line or is printed small on the clause's pages) that the parser drops with the footnote mark; no regulation word changes.
- fda-guidance-part11-scope-application-2003.pdf _unnumbered:1 (unnumbered): `-guidance for industry | -2003 | -guidance for industry | -2003` - Front matter (cover page, document history, contents): the two engines read the cover's text boxes, address blocks and history table in different orders; not regulation text.
- fda-guidance-part11-scope-application-2003.pdf _unnumbered:2 (unnumbered): `-guidance for industry 1 | -4 5 6 | -13 14 15` - Front matter (cover page, document history, contents): the two engines read the cover's text boxes, address blocks and history table in different orders; not regulation text.
- fda-guidance-part11-scope-application-2003.pdf I (clause): `-21 | -32 | +1 | -43 | -48 | -51 | -57 58` - NOT EXPLAINED
- fda-guidance-part11-scope-application-2003.pdf II (clause): `-60 | -67 | -83 | -91 | -104 | -110 111` - Parser defect (0b): margin line numbers of this line-numbered FDA guidance are left in the stored text where a line starts a paragraph or follows a footnote (e.g. 'II. BACKGROUND 74 Each NDA'); the guidance words are intact, the numbers are not part of it.
- fda-guidance-part11-scope-application-2003.pdf III (clause): `-113` - NOT EXPLAINED
- fda-guidance-part11-scope-application-2003.pdf III.A (clause): `-115 | -118 | -134 | -148 | -153` - NOT EXPLAINED
- fda-guidance-part11-scope-application-2003.pdf III.B (clause): `-155` - NOT EXPLAINED
- fda-guidance-part11-scope-application-2003.pdf III.B.1 (clause): `-157 | -163 | -172` - NOT EXPLAINED
- fda-guidance-part11-scope-application-2003.pdf III.B.2 (clause): `-174 | -177 | -184 | -211` - NOT EXPLAINED
- fda-guidance-part11-scope-application-2003.pdf III.C (clause): `-213` - NOT EXPLAINED
- fda-guidance-part11-scope-application-2003.pdf III.C.1 (clause): `-215 | -221 | -228 | -233 | -237` - NOT EXPLAINED
- fda-guidance-part11-scope-application-2003.pdf III.C.2 (clause): `-239 | -246 | -256` - NOT EXPLAINED
- fda-guidance-part11-scope-application-2003.pdf III.C.3 (clause): `-258 | -262 | -265 | -271 | -275` - NOT EXPLAINED
- fda-guidance-part11-scope-application-2003.pdf III.C.4 (clause): `-277 | -283 | -285 | -297` - NOT EXPLAINED
- fda-guidance-part11-scope-application-2003.pdf III.C.5 (clause): `-299 | -305 | -309 | -319 | +8` - NOT EXPLAINED
- fda-guidance-part11-scope-application-2003.pdf IV (clause): `-321 | -323 | -327 | -331 | -335 | -339 340 | -342 | -345 | -348` - Parser defect (0b): margin line numbers of this line-numbered FDA guidance are left in the stored text where a line starts a paragraph or follows a footnote (e.g. 'II. BACKGROUND 74 Each NDA'); the guidance words are intact, the numbers are not part of it.
- fda-guidance-part11-scope-application-2003.pdf page 4 (uncovered): `+next to _unnumbered:2: i introduction` - NOT EXPLAINED
- fda-guidance-part11-scope-application-2003.pdf page 4 (uncovered): `+next to I: introduction i` - NOT EXPLAINED
- fda-guidance-product-recalls-2020.pdf II (clause): `-o | -o | -o | -o | -o | -o | -o | -o | -o | -o | -o | -o | -o | -o | -o | -o | -o | -o | -o | -o | -o | -o o | -o | -o | -o | -o | -o | -o | -o | -o | -o | -o | -o | -o | -o | -o | -o | -o | -o | -o | -o | -o | -o | -o | -o | -o | -o | -o | -o | -o | -o | -o | -o | -o | -o | -o | -o | -o | -o | -o ` - NOT EXPLAINED
- fda-guidance-pyrogen-endotoxins-qa-2026.pdf _unnumbered:2 (unnumbered): `-i` - Front matter (cover page, document history, contents): the two engines read the cover's text boxes, address blocks and history table in different orders; not regulation text.
- fda-guidance-pyrogen-endotoxins-qa-2026.pdf III.6 (clause): `+25` - A footnote reference number (verified: it starts a line or is printed small on the clause's pages) that the parser drops with the footnote mark; no regulation word changes.
- fda-guidance-quality-agreements-2016.pdf _unnumbered:2 (unnumbered): `-i` - NOT EXPLAINED
- fda-guidance-quality-agreements-2016.pdf II (clause): `+2` - A footnote reference number (verified: it starts a line or is printed small on the clause's pages) that the parser drops with the footnote mark; no regulation word changes.
- fda-guidance-quality-systems-approach-2006.pdf II.B (clause): `+3` - A footnote reference number (verified: it starts a line or is printed small on the clause's pages) that the parser drops with the footnote mark; no regulation word changes.
- fda-guidance-quality-systems-approach-2006.pdf III.G (clause): `+8` - A footnote reference number (verified: it starts a line or is printed small on the clause's pages) that the parser drops with the footnote mark; no regulation word changes.
- fda-guidance-quality-systems-approach-2006.pdf IV.A.3 (clause): `+quality standard that will be followed the | -the quality standard that will be followed` - Order or place only (verified mechanically): every stored word run of this discrepancy is printed on the clause's pages, and every page run it lacks is stored word for word (in this clause or another), so no word is lost or added; the engines read table cells, columns or figure labels in different orders.
- fda-guidance-quality-systems-approach-2006.pdf IV.B.3 (clause): `+21 cfr cgmp regulations related to resources quality system element regulatory citation quality system element regulatory citation quality system element regulatory citation quality system element regulatory citation 1 general arrangements qualifications 211.25 a 2 develop personnel staff training ` - NOT EXPLAINED
- fda-guidance-quality-systems-approach-2006.pdf IV.B.4 (clause): `-see reference 4` - Order or place only (verified mechanically): every stored word run of this discrepancy is printed on the clause's pages, and every page run it lacks is stored word for word (in this clause or another), so no word is lost or added; the engines read table cells, columns or figure labels in different orders.
- fda-guidance-quality-systems-approach-2006.pdf IV.C.1 (clause): `+resources and facilities used` - Order or place only (verified mechanically): every stored word run of this discrepancy is printed on the clause's pages, and every page run it lacks is stored word for word (in this clause or another), so no word is lost or added; the engines read table cells, columns or figure labels in different orders.
- fda-guidance-quality-systems-approach-2006.pdf IV.C.3 (clause): `+17` - A footnote reference number (verified: it starts a line or is printed small on the clause's pages) that the parser drops with the footnote mark; no regulation word changes.
- fda-guidance-quality-systems-approach-2006.pdf Table 1 row 1 (table_row): `-system element` - NOT EXPLAINED
- fda-guidance-quality-systems-approach-2006.pdf Table 2 3. Facilities and Equipment (table_row): `-3 and buildings and 211.28 c` - NOT EXPLAINED
- fda-guidance-quality-systems-approach-2006.pdf Table 4 Quality System Element (table_row): `-element regulatory citation` - Order or place only (verified mechanically): every stored word run of this discrepancy is printed on the clause's pages, and every page run it lacks is stored word for word (in this clause or another), so no word is lost or added; the engines read table cells, columns or figure labels in different orders.
- fda-guidance-quality-systems-approach-2006.pdf Table 4 1. Design and Develop Product and… (table_row): `-develop` - NOT EXPLAINED
- fda-guidance-quality-systems-approach-2006.pdf Table 4 2. Examine Inputs (table_row): `-211.122 211.125` - NOT EXPLAINED
- fda-guidance-quality-systems-approach-2006.pdf Table 5 1. Analyze Data for Trends (table_row): `-data for trends` - Order or place only (verified mechanically): every stored word run of this discrepancy is printed on the clause's pages, and every page run it lacks is stored word for word (in this clause or another), so no word is lost or added; the engines read table cells, columns or figure labels in different orders.
- fda-guidance-quality-systems-approach-2006.pdf Table 5 3. Risk Assessment (table_row): `-3` - NOT EXPLAINED
- fda-guidance-quality-systems-approach-2006.pdf page 16 (uncovered): `+in table row: systemelement` - NOT EXPLAINED
- fda-guidance-quality-systems-approach-2006.pdf page 18 (uncovered): `+in table row: andequipment` - NOT EXPLAINED
- fda-guidance-quality-systems-approach-2006.pdf page 25 (uncovered): `+in table row: systemelement` - NOT EXPLAINED
- fda-guidance-quality-systems-approach-2006.pdf page 25 (uncovered): `+in table row: anddevelop` - NOT EXPLAINED
- fda-guidance-quality-systems-approach-2006.pdf page 25 (uncovered): `+in table row: 211.122,211.125` - NOT EXPLAINED
- fda-guidance-quality-systems-approach-2006.pdf page 28 (uncovered): `+in table row: datafortrends` - NOT EXPLAINED
- fda-guidance-remote-regulatory-assessments-2025.pdf _unnumbered:2 (unnumbered): `-conducting remote regulatory assessments questions and answers guidance for industry 1` - Order or place only (verified mechanically): every stored word run of this discrepancy is printed on the clause's pages, and every page run it lacks is stored word for word (in this clause or another), so no word is lost or added; the engines read table cells, columns or figure labels in different orders.
- fda-guidance-remote-regulatory-assessments-2025.pdf III.A.7 (clause): `+19` - A footnote reference number (verified: it starts a line or is printed small on the clause's pages) that the parser drops with the footnote mark; no regulation word changes.
- fda-guidance-remote-regulatory-assessments-2025.pdf III.C (clause): `-33 | +34` - NOT EXPLAINED
- fda-guidance-remote-regulatory-assessments-2025.pdf Appendix 1 (clause): `-appendix 1` - NOT EXPLAINED
- fda-guidance-remote-regulatory-assessments-2025.pdf page 18 (uncovered): `+next to III.D: appendix 1` - NOT EXPLAINED
- fda-guidance-remote-regulatory-assessments-2025.pdf page 4 (uncovered): `+in two clauses I and _unnumbered:2: this guidance represents the current thinking of the food and drug administration fda or agency on this topic it does not establish any rights for any person and is not binding on fda or the public you can use an alternative approach if it satisfies the requireme` - NOT EXPLAINED
- fda-guidance-sterilization-validation-submission-1994.pdf I.A (clause): `-1 this guidance has been prepared by the sterility technical committee of the chemistry manufacturing controls coordinating committee of the center for drug evaluation and research cder and the center for veterinary medicine cvm at the food and drug administration although this guidance does not cr` - NOT EXPLAINED
- fda-guidance-sterilization-validation-submission-1994.pdf II.A.3 (clause): `-fo | +f` - NOT EXPLAINED
- fda-guidance-sterilization-validation-submission-1994.pdf II.C (clause): `+or −` - NOT EXPLAINED
- fda-guidance-sterilization-validation-submission-1994.pdf page 4 (uncovered): `+2 the packaging of the product 10 3 multiple dose mapping studies 10 4 microbiological methods and controls 11 5 monitoring stability 11 iv information for aseptic fill manufacturing processes which should be included in drug applications 11 a buildings and facilities 11 1 floor plan 11 2 location ` - Text read outside any clause's stretch that is stored word for word in another clause of the document (verified mechanically): a running title, table caption or text read in another order.
- fda-guidance-sterilization-validation-submission-1994.pdf page 5 (uncovered): `+g container closure and package integrity 15 h sterility testing methods and release criteria 16 i bacterial endotoxins test and method 16 j evidence of formal written procedures 16 v maintenance of microbiological control and quality stability considerations 16 a container closure integrity 16 b p` - Text read outside any clause's stretch that is stored word for word in another clause of the document (verified mechanically): a running title, table caption or text read in another order.
- fda-guidance-voluntary-recalls-initiation-2022.pdf _unnumbered:2 (unnumbered): `-guidance for industry and fda staff 1` - Order or place only (verified mechanically): every stored word run of this discrepancy is printed on the clause's pages, and every page run it lacks is stored word for word (in this clause or another), so no word is lost or added; the engines read table cells, columns or figure labels in different orders.
- fda-guidance-voluntary-recalls-initiation-2022.pdf I (clause): `+1` - A footnote reference number (verified: it starts a line or is printed small on the clause's pages) that the parser drops with the footnote mark; no regulation word changes.
- fda-guidance-voluntary-recalls-initiation-2022.pdf III.A.1 (clause): `+23` - A footnote reference number (verified: it starts a line or is printed small on the clause's pages) that the parser drops with the footnote mark; no regulation word changes.
- fda-guidance-voluntary-recalls-initiation-2022.pdf III.B (clause): `+28 | +29` - A footnote reference number (verified: it starts a line or is printed small on the clause's pages) that the parser drops with the footnote mark; no regulation word changes.
- fda-guidance-voluntary-recalls-initiation-2022.pdf page 4 (uncovered): `+in two clauses I and _unnumbered:2: this guidance represents the current thinking of the u s food and drug administration fda we or agency on this topic it does not establish any rights for any person and is not binding on fda or the public you can use an alternative approach if it satisfies the re` - NOT EXPLAINED
- fda-oos-2022.pdf _unnumbered:2 (unnumbered): `-i` - NOT EXPLAINED
- fda-oos-2022.pdf V.C (clause): `+20` - A footnote reference number (verified: it starts a line or is printed small on the clause's pages) that the parser drops with the footnote mark; no regulation word changes.
- fda-process-validation-2011.pdf _unnumbered:2 (unnumbered): `-i guidance for industry 1` - Front matter (cover page, document history, contents): the two engines read the cover's text boxes, address blocks and history table in different orders; not regulation text.
- ich-m7-r2.pdf 3 (clause): `+−` - Exponent minus (verified: every minus sign on the clause's pages follows a number or a unit, as in '10⁻⁶' or 'mg⁻¹'): the stored text has poppler's rendering of the superscript without the sign ('10-6' or '106'). Known superscript limitation (0b: keep superscripts as '10^-6').
- ich-m7-r2.pdf 7.3.1 (clause): `+− | +−` - Exponent minus (verified: every minus sign on the clause's pages follows a number or a unit, as in '10⁻⁶' or 'mg⁻¹'): the stored text has poppler's rendering of the superscript without the sign ('10-6' or '106'). Known superscript limitation (0b: keep superscripts as '10^-6').
- ich-m7-r2.pdf 9.2 (clause): `+− | +− | +− | +−` - Exponent minus (verified: every minus sign on the clause's pages follows a number or a unit, as in '10⁻⁶' or 'mg⁻¹'): the stored text has poppler's rendering of the superscript without the sign ('10-6' or '106'). Known superscript limitation (0b: keep superscripts as '10^-6').
- ich-m7-r2.pdf Appendix 3 (section): `-route specific limit` - Order or place only (verified mechanically): every stored word run of this discrepancy is printed on the clause's pages, and every page run it lacks is stored word for word (in this clause or another), so no word is lost or added; the engines read table cells, columns or figure labels in different orders.
- ich-m7-r2.pdf page 5 (uncovered): `+a ssessment and c ontrol of dna r eactive m utagenic i mpurities in p harmaceuticals to l imit p otential c arcinogenic r isk m 7 r 2 1 i` - NOT EXPLAINED
- ich-q10.pdf _unnumbered:1 (unnumbered): `-pharmaceutical quality system | +q 10 approval by the steering committee under step 4 and recommendation for adoption to the three ich regulatory bodies 4 june p harmaceutical q uality s ystem` - Front matter (cover page, document history, contents): the two engines read the cover's text boxes, address blocks and history table in different orders; not regulation text.
- ich-q10.pdf Table 2 Q10 (table_row): `-2008` - NOT EXPLAINED
- ich-q11-qa-pmda.pdf _unnumbered:1 (unnumbered): `-implementation working group ich q 11 guideline development and manufacture of drug substances chemical entities and biotechnological biological entities questions and answers version 23 august 2017 | +implementation working group ich q 11 guideline development and manufacture of drug substances ch` - NOT EXPLAINED
- ich-q11-qa-pmda.pdf _unnumbered:2 (unnumbered): `-ii` - NOT EXPLAINED
- ich-q11-qa-pmda.pdf 12 (clause): `-iii` - NOT EXPLAINED
- ich-q12.pdf 3 (clause): `-3` - NOT EXPLAINED
- ich-q12.pdf 4 (clause): `-4 | -change management protocol pacmp` - NOT EXPLAINED
- ich-q12.pdf 6 (clause): `-6 pharmaceutical quality system pqs` - Order or place only (verified mechanically): every stored word run of this discrepancy is printed on the clause's pages, and every page run it lacks is stored word for word (in this clause or another), so no word is lost or added; the engines read table cells, columns or figure labels in different orders.
- ich-q12.pdf Appendix 1 (section): `+q as from training sessions q 8 q 9 q 10 points to consider a ppendix` - NOT EXPLAINED
- ich-q12.pdf Table 4 row 1 (table_row): `-ctd section section title established conditions general list with notes` - Order or place only (verified mechanically): every stored word run of this discrepancy is printed on the clause's pages, and every page run it lacks is stored word for word (in this clause or another), so no word is lost or added; the engines read table cells, columns or figure labels in different orders.
- ich-q12.pdf Table 4 3.2.P.3 (table_row): `-3.2 p 3 manufacture` - Order or place only (verified mechanically): every stored word run of this discrepancy is printed on the clause's pages, and every page run it lacks is stored word for word (in this clause or another), so no word is lost or added; the engines read table cells, columns or figure labels in different orders.
- ich-q12.pdf page 26 (uncovered): `+in table row: supportive information` - NOT EXPLAINED
- ich-q12.pdf page 26 (uncovered): `+in table row: drug product` - NOT EXPLAINED
- ich-q12.pdf page 15 (uncovered): `+next to 4.1: pacmp` - NOT EXPLAINED
- ich-q12.pdf page 10 (uncovered): `+in two clauses 3 and 3.1: established conditions for manufacturing and control referred to as ecs` - NOT EXPLAINED
- ich-q12.pdf page 19 (uncovered): `+in two clauses 6 and 6.1: and change management` - NOT EXPLAINED
- ich-q12.pdf page 23 (uncovered): `+in two clauses 11 and Appendix 1: appendix q as from training sessions q 8 q 9 q 10 points to consider` - NOT EXPLAINED
- ich-q1a-r2.pdf _unnumbered:1 (unnumbered): `-cover note | +q 1 a r 2 approval by the steering committee of the second revision directly under step 4 without further public consultation to include consequences of the adoption of q 1 f stability data package | -revision | +registration applications in climatic zones iii and iv and recommendatio` - Front matter (cover page, document history, contents): the two engines read the cover's text boxes, address blocks and history table in different orders; not regulation text.
- ich-q1a-r2.pdf 2.1.7.1 (clause): `-2.1.7.1 general case` - Order or place only (verified mechanically): every stored word run of this discrepancy is printed on the clause's pages, and every page run it lacks is stored word for word (in this clause or another), so no word is lost or added; the engines read table cells, columns or figure labels in different orders.
- ich-q1a-r2.pdf 2.2.7.1 (clause): `-2.2.7.1 general case` - Order or place only (verified mechanically): every stored word run of this discrepancy is printed on the clause's pages, and every page run it lacks is stored word for word (in this clause or another), so no word is lost or added; the engines read table cells, columns or figure labels in different orders.
- ich-q1a-r2.pdf Table 2 Q1A(R2) (table_row): `-2003` - NOT EXPLAINED
- ich-q1b.pdf _unnumbered:1 (unnumbered): `-stability testing photostability testing | +q 1 b approval by the steering committee under step 4 and recommendation for adoption to the three ich regulatory bodies 6 november 1996 q 1 b s tability t esting p hotostability t esting` - Front matter (cover page, document history, contents): the two engines read the cover's text boxes, address blocks and history table in different orders; not regulation text.
- ich-q1d.pdf _unnumbered:1 (unnumbered): `-bracketing | +q 1 d approval by the steering committee under step 4 | -matrixing designs | +recommendation | -stability testing | +adoption to the three ich regulatory bodies 7 february 2002 q 1 d b racketing and m atrixing d esigns for s tability t esting` - Front matter (cover page, document history, contents): the two engines read the cover's text boxes, address blocks and history table in different orders; not regulation text.
- ich-q1d.pdf Table 3 Container size (table_row): `-15` - NOT EXPLAINED
- ich-q1d.pdf Table 4 row 3 (table_row): `-s batch batch batch batch batch` - NOT EXPLAINED
- ich-q1d.pdf Table 5 row 3 (table_row): `-batch batch batch batch batch` - NOT EXPLAINED
- ich-q1e.pdf _unnumbered:1 (unnumbered): `-ii evaluation | +q 1 e approval by the steering committee under step 4 and recommendation | -stability data | +adoption to the three ich regulatory bodies 6 february 2003 q 1 e e valuation for s tability d ata` - Front matter (cover page, document history, contents): the two engines read the cover's text boxes, address blocks and history table in different orders; not regulation text.
- ich-q1e.pdf Appendix A (section): `-i evaluation of stability data` - NOT EXPLAINED
- ich-q1e.pdf Appendix A #2 (section): `+significant change at accelerated condition within 3 months yes no | -tabulate and or plot | -stability data on all | -attributes at all storage yes | -conditions and evaluate | +show variability tabulate and or plot stability data on all attributes at all storage conditions and evaluate | -show va` - NOT EXPLAINED
- ich-q1e.pdf Appendix B 8 (clause): `+80 85 90 95 100 105 110 115 | -115 assay % of label claim 110 105 raw data 100 upper confidence limit 95 lower confidence limit regression line 90 upper acceptance 85 criterion 105 lower acceptance 80 criterion 95 | +a s s a y % o f l a b e l c l a i m raw data upper confidence limit lower confiden` - NOT EXPLAINED
- ich-q2-r2.pdf _unnumbered:1 (unnumbered): `-international council for harmonisation of technical requirements for pharmaceuticals for human use ich harmonised guideline validation of analytical procedures q 2 r 2 final version adopted on 1 november 2023 this guideline has been developed by the appropriate ich expert working group and has bee` - Order or place only (verified mechanically): every stored word run of this discrepancy is printed on the clause's pages, and every page run it lacks is stored word for word (in this clause or another), so no word is lost or added; the engines read table cells, columns or figure labels in different orders.
- ich-q2-r2.pdf 3.2.3.3 (clause): `+dl | +ql` - NOT EXPLAINED
- ich-q2-r2.pdf 5 (clause): `-2 | +1` - NOT EXPLAINED
- ich-q2-r2.pdf 7 (clause): `-table 4 example for elemental impurities by icp oes or icp ms table 5 example for dissolution with hplc as product performance test for an immediate release dosage form table 6 example for quantitative 1 h nmr for the assay of a drug substance table 7 example for biological assays table 8 example f` - NOT EXPLAINED
- ich-q2-r2.pdf Table 10 development as (table_row): `-before measurement` - NOT EXPLAINED
- ich-q2-r2.pdf page 34 (uncovered): `+in table row: procedure` - NOT EXPLAINED
- ich-q3a-r2.pdf _unnumbered:1 (unnumbered): `-impurities in new drug substances | +q 3 a r 2 approval by the steering committee of the revision of the attachment 2 directly under step 4 without further public consultation 25 october q 3 a r 2 i mpurities i n n ew d rug s ubstances` - Front matter (cover page, document history, contents): the two engines read the cover's text boxes, address blocks and history table in different orders; not regulation text.
- ich-q3a-r2.pdf 3 #2 (clause): `+no yes structure identified | -any | +no greater than qualification threshold c | -known human yes reduce to structure relevant risksd identified safe level no no | -yes | +≤ qualification threshold c | -≤ identification | -thresholdc yes no | +≤ identification threshold c | -greater than | +reduce` - NOT EXPLAINED
- ich-q3a-r2.pdf Table 2 Q3A(R2) (table_row): `-2006` - NOT EXPLAINED
- ich-q3a-r2.pdf Table 5 “Raw” Result (%) (table_row): `-1.0` - NOT EXPLAINED
- ich-q3b-r2.pdf _unnumbered:1 (unnumbered): `-impurities | +q 3 b r 2 approval by the steering committee of the revision of the attachment 2 directly under step 4 without further public consultation 2 june q 3 b r 2 i mpurities` - Front matter (cover page, document history, contents): the two engines read the cover's text boxes, address blocks and history table in different orders; not regulation text.
- ich-q3b-r2.pdf Glossary (section): `-0 0 r ep o rtin g id en tific atio n percentage of drug substance q u alificatio n 0 8 0 0 6 0 0 4 0 0 2 0 0 0 0 | +0.00 0.20 0.40 0.60 0.80 1.00 | -m ax im u m d aily d o se | +maximum daily dose expressed in mg of drug substance p | -x p ressed in m | +r c e n t a | +reporting identification qual` - NOT EXPLAINED
- ich-q3b-r2.pdf Table 2 Q3B(R2) (table_row): `-2006` - NOT EXPLAINED
- ich-q3c-r9.pdf _unnumbered:1 (unnumbered): `-international council for harmonisation of technical requirements for pharmaceuticals for human use ich harmonised guideline impurities guideline for residual solvents q 3 c r 9 current step 4 version dated 24 january 2024 this guideline has been developed by the appropriate ich expert working grou` - Front matter (cover page, document history, contents): the two engines read the cover's text boxes, address blocks and history table in different orders; not regulation text.
- ich-q3c-r9.pdf Part I 3.3 (clause): `+c on ce n t r a ti on pp m | -pde concentration ppm | +p d e do s e` - NOT EXPLAINED
- ich-q3c-r9.pdf Part I 4.1 (clause): `+ppm` - NOT EXPLAINED
- ich-q3c-r9.pdf Part I 4.2 (clause): `+methylisobutylketone` - NOT EXPLAINED
- ich-q3c-r9.pdf Part I Appendix 1 (section): `+propan 2 one | -propan 2 one | +butan 1 ol | -butan 1 ol | +butan 2 ol | -butan 2 ol | +propane | -propane | +tert butanol | -tert butanol | -cl | +1 methyl ethylbenzene | -1 methyl ethylbenzene` - NOT EXPLAINED
- ich-q3c-r9.pdf Part I Appendix 1 2 (clause): `+ether 3 | -ether 3 | +ethylene dichloride ethylene chloride | -ethylene dichloride ethylene chloride | +vinylidene chloride | -vinylidene chloride | +acetylene dichloride | -acetylene dichloride | +monoglyme dimethyl cellosolve | -monoglyme dimethyl cellosolve | +dimethylformamide | -dimethylformam` - NOT EXPLAINED
- ich-q3c-r9.pdf Part I Appendix 1 3 (clause): `+ethoxyethane 1,1 oxybisethane | -ethoxyethane 1,1 oxybisethane | +isopentyl alcohol 3 methylbutan 1 ol | -isopentyl alcohol 3 methylbutan 1 ol | +hexan 2 one | -hexan 2 one | +mek butan 2 one | -mek butan 2 one | +4 methyl 2 pentanone mibk | -4 methyl 2 pentanone mibk | +2 methylpropan 1 ol | -2 me` - NOT EXPLAINED
- ich-q3c-r9.pdf Part I Appendix 1 5 (clause): `+xylol ch 3 | -ch 3 xylol` - NOT EXPLAINED
- ich-q3c-r9.pdf Part I Appendix 3 (section): `+pde | -pde 1 | +pde | -− 1 | -− 1 | -pde 4.22 mg day − 1 | +1 4.22 mg day − 1 − 1 − | +pregnant or not | -pregnant or not | +v | -− 6 atm | +a t m | -mg mol − 1 46.15 mg − 1 − 1 1.89 mg | +m g m o | -v rt 0.082 | -24.45 | +46 15 m g 24 45 | +1 89 m g l 6 1 1 1 0082` - NOT EXPLAINED
- ich-q3c-r9.pdf Part II (section): `-200 x 72.10 200 ppm 589.8 mg | +pp | -3 0.59 mg l 24.45 0.59 x 6 x 5 for continuous dosing 0.105 mg l 24 | +720 m g d ay 7 2 10 1000 | -0.105 x 290 daily dose 71.65 mg kg 0.425 71.65 x 50 pde 7.165 mg day 7.2 mg day 5 | +2 l i m it m g d a y 7 165 1 | +5 50 x 71 65 m g kg 65` - NOT EXPLAINED
- ich-q3c-r9.pdf Part II 7.2 (clause): `-7.2 x 1000 limit 720 ppm 10` - NOT EXPLAINED
- ich-q3c-r9.pdf Part III (section): `-150 | +pp m 530 m g d ay 5 3 10 1000 | -99.13 150 ppm 608.16 mg | +5 3 l i | -3 0.608 mg l 24.45 0.608 | +it 5 | -6 for continuous dosing 0.152 mg l 24 0.152 | +5 | -290 daily dose 133.58 mg kg 0.33 133.58 x 50 pde 5.3 mg day 5 | +1 | -1 x 5 x 5` - NOT EXPLAINED
- ich-q3c-r9.pdf Part III 5.3 (clause): `-5.3 x 1000 limit 530 ppm 10` - NOT EXPLAINED
- ich-q3c-r9.pdf Part IV #2 (section): `+part iv i mpurities r esidual s olvents m aintenance pde for c umene | -250 x 120.19 250 ppm 1229 mg | +m g l 23 1 m g | -1.23 mg | +1229 24 45 120 19 x 250 pp m 250 m g | -24.45 1.23 | +0 22 7 x 24 5 | -5 for continuous dosing 0.22 mg | +1 23 do s i ng c on ti nuou s f o r m g kg d a y 150 kg 0 42` - NOT EXPLAINED
- ich-q3c-r9.pdf Part V (section): `+methylisobutylketone part v i mpurities r esidual s olvents m aintenance pde for t riethylamine and | -247 x 101.19 247 ppm 1022.2 mg | +m g l 022 1 m g | -1.022 | +1022 2 24 45 101 19 x 247 pp m 247 | -24.45 1.022 | +0.183 7 x 24 5 | -5 | +1.022 dosing continuous | -continuous dosing 0.183 mg | +m` - NOT EXPLAINED
- ich-q3c-r9.pdf _unnumbered:3 (unnumbered): `-450 x 100.16 450 ppm 1843 mg | +m g l 843 1 m g | -1.843 mg | +1843 24 45 100 16 x 450 pp m 450 m g | -24.45 1.843 | +0 329 7 x 24 5 | -5 for continuous dosing 0.329 mg l 24 x 7 0.329 mg l | -x 290 l day − 1 daily dose 225 | +843 do s i ng c on ti nuou s f o r | +225 kg | -kg | +day l 290 x l mg 0.` - NOT EXPLAINED
- ich-q3c-r9.pdf Part VI (section): `+part vi i mpurities r esidual s olvents m aintenance pde for 2 m ethyltetrahydrofuran c yclopentyl m ethyl e ther and t ertiary b utyl a lcohol | -250 x 50 pde 50 | +50 1 x 1 x | -1 x 1 | +250 pde` - NOT EXPLAINED
- ich-q3c-r9.pdf Part VI 6 (clause): `-150 x 50 pde 15 mg day 5 x 10 x 10 x 1 x 1` - NOT EXPLAINED
- ich-q3c-r9.pdf _unnumbered:6 (unnumbered): `+mg day 15 1 x 1 x 10 x 10 x 5 50 x 150 pde | -175 x 50 pde 35 mg day 5 x 10 x 1 x 1 x 5 | +mg day 35 5 x 1 x 1 x 10 x 5 50 x 175 pde | -510 x 50 pde 42.5 mg day 12 x 10 x 1 x 1 x 5 | +mg day 42.5 5 x 1 x 1 x 10 x 12 50 x 510 pde` - NOT EXPLAINED
- ich-q3c-r9.pdf page 29 (uncovered): `+5 50 x 133 58 m g kg 133 58 0 33 290 x 0 152 do s e d a il y m g l 0 152 24 6 x 0 608 do s i ng c on ti nuou s f o r m g l 608 0 m g m 608 16 24 45 99 13 x 150 pp m 150` - NOT EXPLAINED
- ich-q3c-r9.pdf page 30 (uncovered): `+in two clauses Part III 5.3 and Part IV #2: pde for cumene` - NOT EXPLAINED
- ich-q3c-r9.pdf page 34 (uncovered): `+in two clauses Part V and _unnumbered:2: pde for triethylamine and methylisobutylketone` - NOT EXPLAINED
- ich-q3c-r9.pdf page 41 (uncovered): `+in two clauses Part VI and _unnumbered:4: pde for 2 methyltetrahydrofuran cyclopentyl methyl ether and tertiary butyl alcohol` - NOT EXPLAINED
- ich-q3d-r2.pdf _unnumbered:1 (unnumbered): `-international council for harmonisation of technical requirements for pharmaceuticals for human use ich harmonised guideline guideline for elemental impurities q 3 d r 2 final version adopted on 26 april 2022 this guideline has been developed by the appropriate ich expert working group and has been` - Front matter (cover page, document history, contents): the two engines read the cover's text boxes, address blocks and history table in different orders; not regulation text.
- ich-q3d-r2.pdf Appendix 5 5.2 (clause): `-manufacturing drug equipment substance elemental impurities in drug product water container excipients closure system` - NOT EXPLAINED
- ich-q3d-r2.pdf Appendix 5 5.3 (clause): `+elemental impurities in drug product container closure system drug substance excipients manufacturing equipment water` - NOT EXPLAINED
- ich-q3d-r2.pdf Appendix 5 7 (clause): `+day g product drug of amount daily day g | -day | +g ion | -ion g g | -daily amount of drug product g day | -pde g day c | +1 k k | -k | +c day g pde | -k 1` - NOT EXPLAINED
- ich-q3d-r2.pdf Appendix 5 Glossary (section): `+−` - Exponent minus (verified: every minus sign on the clause's pages follows a number or a unit, as in '10⁻⁶' or 'mg⁻¹'): the stored text has poppler's rendering of the superscript without the sign ('10-6' or '106'). Known superscript limitation (0b: keep superscripts as '10^-6').
- ich-q3d-r2.pdf _unnumbered:14 (unnumbered): `+− | +−` - Exponent minus (verified: every minus sign on the clause's pages follows a number or a unit, as in '10⁻⁶' or 'mg⁻¹'): the stored text has poppler's rendering of the superscript without the sign ('10-6' or '106'). Known superscript limitation (0b: keep superscripts as '10^-6').
- ich-q3d-r2.pdf Table 1 Q3D #3 (table_row): `-2013` - NOT EXPLAINED
- ich-q3d-r2.pdf Table 28 header (table_header): `-component` - NOT EXPLAINED
- ich-q3d-r2.pdf Table 29 header (table_header): `-component` - NOT EXPLAINED
- ich-q3d-r2.pdf Table 30 Component (table_row): `-component concentration μg` - NOT EXPLAINED
- ich-q3d-r2.pdf Table 31 Component (table_row): `-component potential concentration μg` - NOT EXPLAINED
- ich-q3d-r2.pdf Table 37 3 Pd (table_row): `-3` - NOT EXPLAINED
- ich-q3d-r2.pdf page 5 (uncovered): `+2 s cope` - NOT EXPLAINED
- ich-q3d-r2.pdf page 4 (uncovered): `+next to _unnumbered:1: c ontents` - NOT EXPLAINED
- ich-q3d-r2.pdf page 4 (uncovered): `+next to 1: ontents c` - NOT EXPLAINED
- ich-q3d-r2.pdf page 18 (uncovered): `+next to Appendix 5 Glossary: lossary g` - NOT EXPLAINED
- ich-q3d-r2.pdf page 29 (uncovered): `+next to Appendix 3: r eferences` - NOT EXPLAINED
- ich-q3d-r2.pdf page 29 (uncovered): `+next to _unnumbered:4: eferences r` - NOT EXPLAINED
- ich-q3d-r2.pdf page 31 (uncovered): `+next to _unnumbered:4: r eferences` - NOT EXPLAINED
- ich-q3d-r2.pdf page 31 (uncovered): `+next to _unnumbered:5: eferences r` - NOT EXPLAINED
- ich-q3d-r2.pdf page 34 (uncovered): `+next to Appendix 3 7.3: r eferences` - NOT EXPLAINED
- ich-q3d-r2.pdf page 34 (uncovered): `+next to _unnumbered:6: eferences r` - NOT EXPLAINED
- ich-q3d-r2.pdf page 36 (uncovered): `+next to _unnumbered:6: r eferences` - NOT EXPLAINED
- ich-q3d-r2.pdf page 36 (uncovered): `+next to _unnumbered:7: eferences r` - NOT EXPLAINED
- ich-q3d-r2.pdf page 39 (uncovered): `+next to _unnumbered:7: r eferences` - NOT EXPLAINED
- ich-q3d-r2.pdf page 39 (uncovered): `+next to _unnumbered:8: eferences r` - NOT EXPLAINED
- ich-q3d-r2.pdf page 41 (uncovered): `+next to _unnumbered:8: r eferences` - NOT EXPLAINED
- ich-q3d-r2.pdf page 41 (uncovered): `+next to _unnumbered:9: eferences r` - NOT EXPLAINED
- ich-q3d-r2.pdf page 42 (uncovered): `+next to _unnumbered:9: r eferences` - NOT EXPLAINED
- ich-q3d-r2.pdf page 42 (uncovered): `+next to _unnumbered:10: eferences r` - NOT EXPLAINED
- ich-q3d-r2.pdf page 45 (uncovered): `+next to _unnumbered:10: r eferences` - NOT EXPLAINED
- ich-q3d-r2.pdf page 45 (uncovered): `+next to _unnumbered:11: eferences r` - NOT EXPLAINED
- ich-q3d-r2.pdf page 46 (uncovered): `+next to _unnumbered:11: r eferences` - NOT EXPLAINED
- ich-q3d-r2.pdf page 46 (uncovered): `+next to _unnumbered:12: eferences r` - NOT EXPLAINED
- ich-q3d-r2.pdf page 48 (uncovered): `+next to _unnumbered:12: r eferences` - NOT EXPLAINED
- ich-q3d-r2.pdf page 48 (uncovered): `+next to _unnumbered:13: eferences r` - NOT EXPLAINED
- ich-q3d-r2.pdf page 50 (uncovered): `+next to _unnumbered:13: r eferences` - NOT EXPLAINED
- ich-q3d-r2.pdf page 50 (uncovered): `+next to _unnumbered:14: eferences r` - NOT EXPLAINED
- ich-q3d-r2.pdf page 52 (uncovered): `+next to _unnumbered:14: r eferences` - NOT EXPLAINED
- ich-q3d-r2.pdf page 52 (uncovered): `+next to _unnumbered:15: eferences r` - NOT EXPLAINED
- ich-q3d-r2.pdf page 54 (uncovered): `+next to _unnumbered:15: r eferences` - NOT EXPLAINED
- ich-q3d-r2.pdf page 54 (uncovered): `+next to _unnumbered:16: eferences r` - NOT EXPLAINED
- ich-q3d-r2.pdf page 57 (uncovered): `+next to _unnumbered:16: r eferences` - NOT EXPLAINED
- ich-q3d-r2.pdf page 57 (uncovered): `+next to _unnumbered:17: eferences r` - NOT EXPLAINED
- ich-q3d-r2.pdf page 59 (uncovered): `+next to _unnumbered:17: r eferences` - NOT EXPLAINED
- ich-q3d-r2.pdf page 59 (uncovered): `+next to _unnumbered:18: eferences r` - NOT EXPLAINED
- ich-q3d-r2.pdf page 62 (uncovered): `+next to _unnumbered:18: r eferences` - NOT EXPLAINED
- ich-q3d-r2.pdf page 62 (uncovered): `+next to _unnumbered:19: eferences r` - NOT EXPLAINED
- ich-q3d-r2.pdf page 64 (uncovered): `+next to _unnumbered:19: r eferences` - NOT EXPLAINED
- ich-q3d-r2.pdf page 64 (uncovered): `+next to _unnumbered:20: eferences r` - NOT EXPLAINED
- ich-q3d-r2.pdf page 66 (uncovered): `+next to _unnumbered:20: r eferences` - NOT EXPLAINED
- ich-q3d-r2.pdf page 66 (uncovered): `+next to _unnumbered:21: eferences r` - NOT EXPLAINED
- ich-q3d-r2.pdf page 68 (uncovered): `+next to _unnumbered:22: eferences r` - NOT EXPLAINED
- ich-q3d-r2.pdf page 69 (uncovered): `+next to _unnumbered:22: r eferences` - NOT EXPLAINED
- ich-q3d-r2.pdf page 72 (uncovered): `+next to _unnumbered:24: eferences r` - NOT EXPLAINED
- ich-q3d-r2.pdf page 4 (uncovered): `+in two clauses 3 and Appendix 5 3: 3 safety assessment of potential elemental impurities` - NOT EXPLAINED
- ich-q6a.pdf _unnumbered:1 (unnumbered): `-specifications test procedures | +q 6 a approval by the steering committee under step 4 | -acceptance criteria | +recommendation | -new drug substances | +adoption to the three ich regulatory bodies 6 october q 6 a s pecifications t est p rocedures | -new drug products chemical substances | +a ccep` - Front matter (cover page, document history, contents): the two engines read the cover's text boxes, address blocks and history table in different orders; not regulation text.
- ich-q6a.pdf Table 2 Q6A (table_row): `-1999` - NOT EXPLAINED
- ich-q7-qa.pdf _unnumbered:1 (unnumbered): `-q 7 implementation working group ich q 7 guideline good manufacturing practice guide for active pharmaceutical ingredients questions and answers current version dated 10 june 2015 | +q 7 implementation working group ich q 7 guideline good manufacturing practice guide for active pharmaceutical ingre` - NOT EXPLAINED
- ich-q7-qa.pdf _unnumbered:2 (unnumbered): `-i | -ii` - NOT EXPLAINED
- ich-q7-qa.pdf Glossary (section): `-20 glossary` - NOT EXPLAINED
- ich-q7-qa.pdf Table 18 header (table_header): `-questions answers` - NOT EXPLAINED
- ich-q7-qa.pdf Table 19 header (table_header): `-questions answers` - NOT EXPLAINED
- ich-q7-qa.pdf Table 30 row 1 (table_row): `-introduction quality personnel buildings facilities process equipment documentation records 7 8 production process packaging identification labelling intermediates storage distribution manufacturers other ich guidelines` - NOT EXPLAINED
- ich-q7-qa.pdf Table 31 row 1 (table_row): `-introduction quality personnel buildings facilities process equipment documentation records 7 8 production process packaging identification labelling intermediates storage distribution manufacturers other ich guidelines` - NOT EXPLAINED
- ich-q7-qa.pdf page 21 (uncovered): `+in table row: 11.6` - NOT EXPLAINED
- ich-q7-qa.pdf page 21 (uncovered): `+in table row: 11.72` - NOT EXPLAINED
- ich-q7.pdf _unnumbered:1 (unnumbered): `-good manufacturing practice guide | +q 7 a approval by the steering committee under step 4 and recommendation | -active pharmaceutical ingredients | +adoption to the three ich regulatory bodies 10 november q 7 g ood m anufacturing p ractice g uide for a ctive p harmaceutical i ngredients` - Front matter (cover page, document history, contents): the two engines read the cover's text boxes, address blocks and history table in different orders; not regulation text.
- ich-q7.pdf 1.3 (clause): `-increasing gmp requirements` - Order or place only (verified mechanically): every stored word run of this discrepancy is printed on the clause's pages, and every page run it lacks is stored word for word (in this clause or another), so no word is lost or added; the engines read table cells, columns or figure labels in different orders.
- ich-q7.pdf Table 2 Q7A (table_row): `-2000` - NOT EXPLAINED
- ich-q8-q9-q10-qa-r4.pdf _unnumbered:1 (unnumbered): `-quality implementation working group on q 8 q 9 and q 10 questions answers r 4 current version dated november 11 2010 | +quality implementation working group on q 8 q 9 and q 10 questions answers r 4 current version dated november 11 2010 | -table of contents 1 introduction 1` - NOT EXPLAINED
- ich-q8-q9-q10-qa-r4.pdf _unnumbered:2 (unnumbered): `-approved aug 2009 | -approved nov 10 2005 | -approved nov 13 2008 | +approved aug 2009 approved nov 10 2005 approved nov 13 2008 | -approved nov 09 2005 | +approved nov 09 2005 | -approved jun 04 2008` - NOT EXPLAINED
- ich-q8-q9-q10-qa-r4.pdf page 7 (uncovered): `+approval questions answers` - NOT EXPLAINED
- ich-q8-q9-q10-qa-r4.pdf page 9 (uncovered): `+approval questions answers` - NOT EXPLAINED
- ich-q8-q9-q10-qa-r4.pdf page 11 (uncovered): `+approval questions answers` - NOT EXPLAINED
- ich-q8-q9-q10-qa-r4.pdf page 12 (uncovered): `+approval questions answers` - NOT EXPLAINED
- ich-q8-q9-q10-qa-r4.pdf page 12 (uncovered): `+approval questions answers` - NOT EXPLAINED
- ich-q8-q9-q10-qa-r4.pdf page 13 (uncovered): `+approval questions answers` - NOT EXPLAINED
- ich-q8-q9-q10-qa-r4.pdf page 15 (uncovered): `+approval questions answers` - NOT EXPLAINED
- ich-q8-q9-q10-qa-r4.pdf page 16 (uncovered): `+approval questions answers` - NOT EXPLAINED
- ich-q8-q9-q10-qa-r4.pdf page 18 (uncovered): `+approval questions answers` - NOT EXPLAINED
- ich-q9r1.pdf 4 (clause): `-initiate quality risk management process risk assessment hazard identification risk analysis risk evaluation unacceptable risk management tools risk control risk communication risk reduction risk acceptance output result of the quality risk management process risk review review events` - NOT EXPLAINED
- ich-q9r1.pdf page 3 (uncovered): `+next to _unnumbered:1: c ontents` - NOT EXPLAINED
- india-cdsco-circ-2024-03-risk-based-inspection.pdf 12 (clause): `-s` - Table cell layout of the CDSCO risk-based inspection checklist (0b review): cells read in a different order or a heading cell merged into a neighbouring row; checked against the page, no requirement word changed.
- india-cdsco-circ-2024-03-risk-based-inspection.pdf 3 #2 (clause): `-observations should be descriptive without ambiguity and answer like yes or no should be avoided list of observations deficiencies 1 critical 1.1 1.2 2 major 2.1 2.2 3 others 3.1 3.2 3.3 concluding remarks name and signatures of the inspecting officials established hold time system remarks recommen` - Table cell layout of the CDSCO risk-based inspection checklist (0b review): cells read in a different order or a heading cell merged into a neighbouring row; checked against the page, no requirement word changed.
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 10 17.3 #2 (table_row): `-18 air handling system central air conditioning` - Order or place only (verified mechanically): every stored word run of this discrepancy is printed on the clause's pages, and every page run it lacks is stored word for word (in this clause or another), so no word is lost or added; the engines read table cells, columns or figure labels in different orders.
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 11 18.13 (table_row): `-19 environmental monitoring annexe 06` - Parser defect (0b): the table extractor merges the section-heading row printed below this row (e.g. '26 Sterilization', no ruled line between them) into this row, or the row continues across a page; the words are all in the PDF, in the next row.
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 13 20.2 (table_row): `-21 sanitation` - Parser defect (0b): the table extractor merges the section-heading row printed below this row (e.g. '26 Sterilization', no ruled line between them) into this row, or the row continues across a page; the words are all in the PDF, in the next row.
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 13 21.1 #4 (table_row): `-22 equipment` - Parser defect (0b): the table extractor merges the section-heading row printed below this row (e.g. '26 Sterilization', no ruled line between them) into this row, or the row continues across a page; the words are all in the PDF, in the next row.
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 13 22.6 (table_row): `-who trs 961` - Table cell layout of the CDSCO risk-based inspection checklist (0b review): cells read in a different order or a heading cell merged into a neighbouring row; checked against the page, no requirement word changed.
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 13 22.2 #3 (table_row): `-23 manufacturing process` - Order or place only (verified mechanically): every stored word run of this discrepancy is printed on the clause's pages, and every page run it lacks is stored word for word (in this clause or another), so no word is lost or added; the engines read table cells, columns or figure labels in different orders.
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 13 23.10 (table_row): `-24 aseptic processing and sterilization by filtration annexe 06` - Parser defect (0b): the table extractor merges the section-heading row printed below this row (e.g. '26 Sterilization', no ruled line between them) into this row, or the row continues across a page; the words are all in the PDF, in the next row.
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 13 24.6 (table_row): `-25 product containers closures` - Order or place only (verified mechanically): every stored word run of this discrepancy is printed on the clause's pages, and every page run it lacks is stored word for word (in this clause or another), so no word is lost or added; the engines read table cells, columns or figure labels in different orders.
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 13 25.6 (table_row): `-26 sterilization` - Parser defect (0b): the table extractor merges the section-heading row printed below this row (e.g. '26 Sterilization', no ruled line between them) into this row, or the row continues across a page; the words are all in the PDF, in the next row.
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 14 26.10 (table_row): `-27 by dry heat` - Parser defect (0b): the table extractor merges the section-heading row printed below this row (e.g. '26 Sterilization', no ruled line between them) into this row, or the row continues across a page; the words are all in the PDF, in the next row.
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 15 27.1 (table_row): `-28 by moist` - Parser defect (0b): the table extractor merges the section-heading row printed below this row (e.g. '26 Sterilization', no ruled line between them) into this row, or the row continues across a page; the words are all in the PDF, in the next row.
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 15 28.1 #2 (table_row): `-29 others` - Parser defect (0b): the table extractor merges the section-heading row printed below this row (e.g. '26 Sterilization', no ruled line between them) into this row, or the row continues across a page; the words are all in the PDF, in the next row.
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 15 29.3 (table_row): `-30 documentation and records` - Order or place only (verified mechanically): every stored word run of this discrepancy is printed on the clause's pages, and every page run it lacks is stored word for word (in this clause or another), so no word is lost or added; the engines read table cells, columns or figure labels in different orders.
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 17 row 1 (table_row): `-31 labels other printed materials` - Parser defect (0b): the table extractor merges the section-heading row printed below this row (e.g. '26 Sterilization', no ruled line between them) into this row, or the row continues across a page; the words are all in the PDF, in the next row.
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 17 31.4 (table_row): `-32 master formula records` - Order or place only (verified mechanically): every stored word run of this discrepancy is printed on the clause's pages, and every page run it lacks is stored word for word (in this clause or another), so no word is lost or added; the engines read table cells, columns or figure labels in different orders.
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 17 32.4 (table_row): `-33 batch processing manufacturing records` - Order or place only (verified mechanically): every stored word run of this discrepancy is printed on the clause's pages, and every page run it lacks is stored word for word (in this clause or another), so no word is lost or added; the engines read table cells, columns or figure labels in different orders.
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 17 33.4 (table_row): `-34 packaging records` - Parser defect (0b): the table extractor merges the section-heading row printed below this row (e.g. '26 Sterilization', no ruled line between them) into this row, or the row continues across a page; the words are all in the PDF, in the next row.
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 18 34.16 (table_row): `-35 standard operating procedure and records` - Order or place only (verified mechanically): every stored word run of this discrepancy is printed on the clause's pages, and every page run it lacks is stored word for word (in this clause or another), so no word is lost or added; the engines read table cells, columns or figure labels in different orders.
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 18 36.3 (table_row): `-37 finished product` - Order or place only (verified mechanically): every stored word run of this discrepancy is printed on the clause's pages, and every page run it lacks is stored word for word (in this clause or another), so no word is lost or added; the engines read table cells, columns or figure labels in different orders.
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 18 37.2 (table_row): `-38 quality control area` - Order or place only (verified mechanically): every stored word run of this discrepancy is printed on the clause's pages, and every page run it lacks is stored word for word (in this clause or another), so no word is lost or added; the engines read table cells, columns or figure labels in different orders.
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 18 38.8 (table_row): `-39 microbiology lab` - Order or place only (verified mechanically): every stored word run of this discrepancy is printed on the clause's pages, and every page run it lacks is stored word for word (in this clause or another), so no word is lost or added; the engines read table cells, columns or figure labels in different orders.
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 19 39.3 #6 (table_row): `-40 quality control system` - Order or place only (verified mechanically): every stored word run of this discrepancy is printed on the clause's pages, and every page run it lacks is stored word for word (in this clause or another), so no word is lost or added; the engines read table cells, columns or figure labels in different orders.
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 21 40.2 #7 (table_row): `-41 analytical method validation amv` - Order or place only (verified mechanically): every stored word run of this discrepancy is printed on the clause's pages, and every page run it lacks is stored word for word (in this clause or another), so no word is lost or added; the engines read table cells, columns or figure labels in different orders.
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 22 41.1 (table_row): `-42 hplc calibration` - Order or place only (verified mechanically): every stored word run of this discrepancy is printed on the clause's pages, and every page run it lacks is stored word for word (in this clause or another), so no word is lost or added; the engines read table cells, columns or figure labels in different orders.
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 22 42.1 (table_row): `-43 dissolution apparatus` - Order or place only (verified mechanically): every stored word run of this discrepancy is printed on the clause's pages, and every page run it lacks is stored word for word (in this clause or another), so no word is lost or added; the engines read table cells, columns or figure labels in different orders.
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 22 43.1 (table_row): `-44 uv vis` - Parser defect (0b): the table extractor merges the section-heading row printed below this row (e.g. '26 Sterilization', no ruled line between them) into this row, or the row continues across a page; the words are all in the PDF, in the next row.
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 22 44.1 (table_row): `-46 ftir` - Parser defect (0b): the table extractor merges the section-heading row printed below this row (e.g. '26 Sterilization', no ruled line between them) into this row, or the row continues across a page; the words are all in the PDF, in the next row.
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 22 46.1 (table_row): `-47 toc analyser following verify records calibration` - Parser defect (0b): the table extractor merges the section-heading row printed below this row (e.g. '26 Sterilization', no ruled line between them) into this row, or the row continues across a page; the words are all in the PDF, in the next row.
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 23 row 1 (table_row): `-48 stability studies` - Order or place only (verified mechanically): every stored word run of this discrepancy is printed on the clause's pages, and every page run it lacks is stored word for word (in this clause or another), so no word is lost or added; the engines read table cells, columns or figure labels in different orders.
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 23 48.1 #2 (table_row): `-49 quality assurance` - Order or place only (verified mechanically): every stored word run of this discrepancy is printed on the clause's pages, and every page run it lacks is stored word for word (in this clause or another), so no word is lost or added; the engines read table cells, columns or figure labels in different orders.
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 24 49.1 (table_row): `-50 annual quality review apqr` - Parser defect (0b): the table extractor merges the section-heading row printed below this row (e.g. '26 Sterilization', no ruled line between them) into this row, or the row continues across a page; the words are all in the PDF, in the next row.
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 24 51.4 (table_row): `-52 complaints and adverse reactions` - Order or place only (verified mechanically): every stored word run of this discrepancy is printed on the clause's pages, and every page run it lacks is stored word for word (in this clause or another), so no word is lost or added; the engines read table cells, columns or figure labels in different orders.
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 25 52.8 (table_row): `-53 site master file` - Order or place only (verified mechanically): every stored word run of this discrepancy is printed on the clause's pages, and every page run it lacks is stored word for word (in this clause or another), so no word is lost or added; the engines read table cells, columns or figure labels in different orders.
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 25 53.4 (table_row): `-54 validation` - Parser defect (0b): the table extractor merges the section-heading row printed below this row (e.g. '26 Sterilization', no ruled line between them) into this row, or the row continues across a page; the words are all in the PDF, in the next row.
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 25 54.2 #4 (table_row): `-55 internal quality gmp audit programme` - Order or place only (verified mechanically): every stored word run of this discrepancy is printed on the clause's pages, and every page run it lacks is stored word for word (in this clause or another), so no word is lost or added; the engines read table cells, columns or figure labels in different orders.
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 26 55.4 (table_row): `-56 pharmaceutical development` - Order or place only (verified mechanically): every stored word run of this discrepancy is printed on the clause's pages, and every page run it lacks is stored word for word (in this clause or another), so no word is lost or added; the engines read table cells, columns or figure labels in different orders.
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 26 56.4 (table_row): `-57 risk assessment system` - Parser defect (0b): the table extractor merges the section-heading row printed below this row (e.g. '26 Sterilization', no ruled line between them) into this row, or the row continues across a page; the words are all in the PDF, in the next row.
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 26 57.5 (table_row): `-58 data integrity` - Order or place only (verified mechanically): every stored word run of this discrepancy is printed on the clause's pages, and every page run it lacks is stored word for word (in this clause or another), so no word is lost or added; the engines read table cells, columns or figure labels in different orders.
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 27 58.9 (table_row): `-59 pharmaceutical quality management system pqs` - Order or place only (verified mechanically): every stored word run of this discrepancy is printed on the clause's pages, and every page run it lacks is stored word for word (in this clause or another), so no word is lost or added; the engines read table cells, columns or figure labels in different orders.
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 29 1.4 (table_row): `-quality rating` - Parser defect (0b): the rotated header cell 'Quality Rating' of the risk-rating table (Table 29) is glued into the row's last cell; row text intact.
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 29 3.2 (table_row): `-quality rating` - Parser defect (0b): the rotated header cell 'Quality Rating' of the risk-rating table (Table 29) is glued into the row's last cell; row text intact.
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 29 4.4 (table_row): `-quality rating` - Parser defect (0b): the rotated header cell 'Quality Rating' of the risk-rating table (Table 29) is glued into the row's last cell; row text intact.
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 29 4.10 (table_row): `-quality rating` - Parser defect (0b): the rotated header cell 'Quality Rating' of the risk-rating table (Table 29) is glued into the row's last cell; row text intact.
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 29 4.17.1 (table_row): `-loop system quality rating` - Parser defect (0b): the rotated header cell 'Quality Rating' of the risk-rating table (Table 29) is glued into the row's last cell; row text intact.
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 29 4.19 (table_row): `-circulation rate` - Table cell layout of the CDSCO risk-based inspection checklist (0b review): cells read in a different order or a heading cell merged into a neighbouring row; checked against the page, no requirement word changed.
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 29 4.30 (table_row): `-quality rating` - Parser defect (0b): the rotated header cell 'Quality Rating' of the risk-rating table (Table 29) is glued into the row's last cell; row text intact.
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 29 6.6 (table_row): `-quality rating` - Parser defect (0b): the rotated header cell 'Quality Rating' of the risk-rating table (Table 29) is glued into the row's last cell; row text intact.
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 29 8.2 (table_row): `-quality rating` - Parser defect (0b): the rotated header cell 'Quality Rating' of the risk-rating table (Table 29) is glued into the row's last cell; row text intact.
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 29 8.11 (table_row): `-quality rating` - Parser defect (0b): the rotated header cell 'Quality Rating' of the risk-rating table (Table 29) is glued into the row's last cell; row text intact.
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 29 8.21 (table_row): `-quality rating` - Parser defect (0b): the rotated header cell 'Quality Rating' of the risk-rating table (Table 29) is glued into the row's last cell; row text intact.
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 29 8.32 (table_row): `-quality rating` - Parser defect (0b): the rotated header cell 'Quality Rating' of the risk-rating table (Table 29) is glued into the row's last cell; row text intact.
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 29 9.9 (table_row): `-quality rating` - Parser defect (0b): the rotated header cell 'Quality Rating' of the risk-rating table (Table 29) is glued into the row's last cell; row text intact.
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 29 10.6 (table_row): `-quality rating` - Parser defect (0b): the rotated header cell 'Quality Rating' of the risk-rating table (Table 29) is glued into the row's last cell; row text intact.
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 29 11.2 (table_row): `-quality rating` - Parser defect (0b): the rotated header cell 'Quality Rating' of the risk-rating table (Table 29) is glued into the row's last cell; row text intact.
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 29 11.4 (table_row): `-area` - Table cell layout of the CDSCO risk-based inspection checklist (0b review): cells read in a different order or a heading cell merged into a neighbouring row; checked against the page, no requirement word changed.
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 29 11.5 (table_row): `-3 pressure gradients` - Order or place only (verified mechanically): every stored word run of this discrepancy is printed on the clause's pages, and every page run it lacks is stored word for word (in this clause or another), so no word is lost or added; the engines read table cells, columns or figure labels in different orders.
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 29 11.8 (table_row): `-quality rating` - Parser defect (0b): the rotated header cell 'Quality Rating' of the risk-rating table (Table 29) is glued into the row's last cell; row text intact.
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 29 12.9 (table_row): `-quality rating` - Parser defect (0b): the rotated header cell 'Quality Rating' of the risk-rating table (Table 29) is glued into the row's last cell; row text intact.
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 29 13.7 (table_row): `-quality rating` - Parser defect (0b): the rotated header cell 'Quality Rating' of the risk-rating table (Table 29) is glued into the row's last cell; row text intact.
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 29 14.5 (table_row): `-quality rating` - Parser defect (0b): the rotated header cell 'Quality Rating' of the risk-rating table (Table 29) is glued into the row's last cell; row text intact.
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 29 14.14 (table_row): `-quality rating` - Parser defect (0b): the rotated header cell 'Quality Rating' of the risk-rating table (Table 29) is glued into the row's last cell; row text intact.
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 29 16.12 (table_row): `-quality rating` - Parser defect (0b): the rotated header cell 'Quality Rating' of the risk-rating table (Table 29) is glued into the row's last cell; row text intact.
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 29 17.6 (table_row): `-quality rating` - Parser defect (0b): the rotated header cell 'Quality Rating' of the risk-rating table (Table 29) is glued into the row's last cell; row text intact.
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 29 17.21 (table_row): `-quality rating` - Parser defect (0b): the rotated header cell 'Quality Rating' of the risk-rating table (Table 29) is glued into the row's last cell; row text intact.
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 29 18.2 (table_row): `-quality rating` - Parser defect (0b): the rotated header cell 'Quality Rating' of the risk-rating table (Table 29) is glued into the row's last cell; row text intact.
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 29 18.11 (table_row): `-quality rating` - Parser defect (0b): the rotated header cell 'Quality Rating' of the risk-rating table (Table 29) is glued into the row's last cell; row text intact.
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 29 19.2 (table_row): `-quality rating` - Parser defect (0b): the rotated header cell 'Quality Rating' of the risk-rating table (Table 29) is glued into the row's last cell; row text intact.
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 29 20.5 (table_row): `-condition` - Table cell layout of the CDSCO risk-based inspection checklist (0b review): cells read in a different order or a heading cell merged into a neighbouring row; checked against the page, no requirement word changed.
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 29 20.14 (table_row): `-quality rating` - Parser defect (0b): the rotated header cell 'Quality Rating' of the risk-rating table (Table 29) is glued into the row's last cell; row text intact.
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 29 21.6 (table_row): `-quality rating` - Parser defect (0b): the rotated header cell 'Quality Rating' of the risk-rating table (Table 29) is glued into the row's last cell; row text intact.
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 29 21.13 (table_row): `-quality rating` - Parser defect (0b): the rotated header cell 'Quality Rating' of the risk-rating table (Table 29) is glued into the row's last cell; row text intact.
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 29 22.3 (table_row): `-quality rating` - Parser defect (0b): the rotated header cell 'Quality Rating' of the risk-rating table (Table 29) is glued into the row's last cell; row text intact.
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 29 22.8 (table_row): `-quality rating` - Parser defect (0b): the rotated header cell 'Quality Rating' of the risk-rating table (Table 29) is glued into the row's last cell; row text intact.
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 29 22.15 (table_row): `-quality rating` - Parser defect (0b): the rotated header cell 'Quality Rating' of the risk-rating table (Table 29) is glued into the row's last cell; row text intact.
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 29 23.5 (table_row): `-by suitable pipes` - Order or place only (verified mechanically): every stored word run of this discrepancy is printed on the clause's pages, and every page run it lacks is stored word for word (in this clause or another), so no word is lost or added; the engines read table cells, columns or figure labels in different orders.
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 29 23.6 (table_row): `-quality rating` - Parser defect (0b): the rotated header cell 'Quality Rating' of the risk-rating table (Table 29) is glued into the row's last cell; row text intact.
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 29 24.3 (table_row): `-quality rating` - Parser defect (0b): the rotated header cell 'Quality Rating' of the risk-rating table (Table 29) is glued into the row's last cell; row text intact.
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 29 25.4 (table_row): `-quality rating` - Parser defect (0b): the rotated header cell 'Quality Rating' of the risk-rating table (Table 29) is glued into the row's last cell; row text intact.
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 29 26.6 (table_row): `-quality rating` - Parser defect (0b): the rotated header cell 'Quality Rating' of the risk-rating table (Table 29) is glued into the row's last cell; row text intact.
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 29 27.1 (table_row): `-quality rating` - Parser defect (0b): the rotated header cell 'Quality Rating' of the risk-rating table (Table 29) is glued into the row's last cell; row text intact.
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 29 27.8 (table_row): `-quality rating` - Parser defect (0b): the rotated header cell 'Quality Rating' of the risk-rating table (Table 29) is glued into the row's last cell; row text intact.
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 29 28.4 (table_row): `-quality rating` - Parser defect (0b): the rotated header cell 'Quality Rating' of the risk-rating table (Table 29) is glued into the row's last cell; row text intact.
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 29 28.10 (table_row): `-quality rating` - Parser defect (0b): the rotated header cell 'Quality Rating' of the risk-rating table (Table 29) is glued into the row's last cell; row text intact.
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 29 29. Others sterilization is tested… (table_row): `-29 others` - Parser defect (0b): the table extractor merges the section-heading row printed below this row (e.g. '26 Sterilization', no ruled line between them) into this row, or the row continues across a page; the words are all in the PDF, in the next row.
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 29 30.5 (table_row): `-quality rating` - Parser defect (0b): the rotated header cell 'Quality Rating' of the risk-rating table (Table 29) is glued into the row's last cell; row text intact.
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 29 30.9 (table_row): `-30.9 specify retaining documents after respective who is responsible its maintenance 1 year after qa is responsible its maintenance no could be produced this regard` - Parser defect (0b): the table extractor merges the section-heading row printed below this row (e.g. '26 Sterilization', no ruled line between them) into this row, or the row continues across a page; the words are all in the PDF, in the next row.
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 29 31.2 (table_row): `-quality rating` - Parser defect (0b): the rotated header cell 'Quality Rating' of the risk-rating table (Table 29) is glued into the row's last cell; row text intact.
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 29 34.1 (table_row): `-quality rating` - Parser defect (0b): the rotated header cell 'Quality Rating' of the risk-rating table (Table 29) is glued into the row's last cell; row text intact.
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 29 34.11 (table_row): `-quality rating` - Parser defect (0b): the rotated header cell 'Quality Rating' of the risk-rating table (Table 29) is glued into the row's last cell; row text intact.
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 29 39.3 (table_row): `-quality rating` - Parser defect (0b): the rotated header cell 'Quality Rating' of the risk-rating table (Table 29) is glued into the row's last cell; row text intact.
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 29 39.14 (table_row): `-quality rating` - Parser defect (0b): the rotated header cell 'Quality Rating' of the risk-rating table (Table 29) is glued into the row's last cell; row text intact.
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 29 39.24 (table_row): `-quality rating` - Parser defect (0b): the rotated header cell 'Quality Rating' of the risk-rating table (Table 29) is glued into the row's last cell; row text intact.
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 29 40.3 (table_row): `-quality rating` - Parser defect (0b): the rotated header cell 'Quality Rating' of the risk-rating table (Table 29) is glued into the row's last cell; row text intact.
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 29 40.12 (table_row): `-quality rating` - Parser defect (0b): the rotated header cell 'Quality Rating' of the risk-rating table (Table 29) is glued into the row's last cell; row text intact.
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 29 40.24 (table_row): `-quality rating` - Parser defect (0b): the rotated header cell 'Quality Rating' of the risk-rating table (Table 29) is glued into the row's last cell; row text intact.
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 29 48.3 (table_row): `-quality rating` - Parser defect (0b): the rotated header cell 'Quality Rating' of the risk-rating table (Table 29) is glued into the row's last cell; row text intact.
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 29 49.4 (table_row): `-quality rating` - Parser defect (0b): the rotated header cell 'Quality Rating' of the risk-rating table (Table 29) is glued into the row's last cell; row text intact.
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 29 49.11 (table_row): `-quality rating` - Parser defect (0b): the rotated header cell 'Quality Rating' of the risk-rating table (Table 29) is glued into the row's last cell; row text intact.
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 29 50.3 (table_row): `-relevant equipment utilities` - Table cell layout of the CDSCO risk-based inspection checklist (0b review): cells read in a different order or a heading cell merged into a neighbouring row; checked against the page, no requirement word changed.
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 29 51.1 (table_row): `-quality rating` - Parser defect (0b): the rotated header cell 'Quality Rating' of the risk-rating table (Table 29) is glued into the row's last cell; row text intact.
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 29 52.7 (table_row): `-quality rating` - Parser defect (0b): the rotated header cell 'Quality Rating' of the risk-rating table (Table 29) is glued into the row's last cell; row text intact.
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 29 54.9 (table_row): `-988 quality rating` - Parser defect (0b): the rotated header cell 'Quality Rating' of the risk-rating table (Table 29) is glued into the row's last cell; row text intact.
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 29 55.4 (table_row): `-rating` - Parser defect (0b): the rotated header cell 'Quality Rating' of the risk-rating table (Table 29) is glued into the row's last cell; row text intact.
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 29 1 and premises: - 56 Building… (table_row): `-56 pharmaceutical development` - Order or place only (verified mechanically): every stored word run of this discrepancy is printed on the clause's pages, and every page run it lacks is stored word for word (in this clause or another), so no word is lost or added; the engines read table cells, columns or figure labels in different orders.
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 29 59.2 (table_row): `-rating` - Parser defect (0b): the rotated header cell 'Quality Rating' of the risk-rating table (Table 29) is glued into the row's last cell; row text intact.
- india-cdsco-circ-2024-03-risk-based-inspection.pdf page 46 (uncovered): `+annexe 06 19 environmental monitoring` - Table cell layout of the CDSCO risk-based inspection checklist (0b review): cells read in a different order or a heading cell merged into a neighbouring row; checked against the page, no requirement word changed.
- india-cdsco-circ-2024-03-risk-based-inspection.pdf page 51 (uncovered): `+annexe 06 24 aseptic processing and sterilization by filtration` - Table cell layout of the CDSCO risk-based inspection checklist (0b review): cells read in a different order or a heading cell merged into a neighbouring row; checked against the page, no requirement word changed.
- india-cdsco-circ-2024-03-risk-based-inspection.pdf page 81 (uncovered): `+in table row: loop system` - NOT EXPLAINED
- india-cdsco-circ-2024-03-risk-based-inspection.pdf page 82 (uncovered): `+in table row: circulation rate` - NOT EXPLAINED
- india-cdsco-circ-2024-03-risk-based-inspection.pdf page 91 (uncovered): `+in table row: area` - NOT EXPLAINED
- india-cdsco-circ-2024-03-risk-based-inspection.pdf page 91 (uncovered): `+in table row: 3 pressure gradients` - NOT EXPLAINED
- india-cdsco-circ-2024-03-risk-based-inspection.pdf page 105 (uncovered): `+in table row: condition` - NOT EXPLAINED
- india-cdsco-circ-2024-03-risk-based-inspection.pdf page 111 (uncovered): `+in table row: by suitable pipes` - NOT EXPLAINED
- india-cdsco-circ-2024-03-risk-based-inspection.pdf page 111 (uncovered): `+in table row: established hold time` - NOT EXPLAINED
- india-cdsco-circ-2024-03-risk-based-inspection.pdf page 116 (uncovered): `+the sterilizers are not studied for heat distribution penetration effectiveness of sterilization process not established by using microbial spore indicators` - Table cell layout of the CDSCO risk-based inspection checklist (0b review): cells read in a different order or a heading cell merged into a neighbouring row; checked against the page, no requirement word changed.
- india-cdsco-circ-2024-03-risk-based-inspection.pdf page 117 (uncovered): `+in table row: system` - NOT EXPLAINED
- india-cdsco-circ-2024-03-risk-based-inspection.pdf page 120 (uncovered): `+sch m specify the duration of retaining the documents after the expiry of the respective product and who is responsible for its maintenance na 1 year after expiry of the product and qa is responsible for its maintenance no records could be produced in this regard na` - Table cell layout of the CDSCO risk-based inspection checklist (0b review): cells read in a different order or a heading cell merged into a neighbouring row; checked against the page, no requirement word changed.
- india-cdsco-circ-2024-03-risk-based-inspection.pdf page 136 (uncovered): `+in table row: relevant equipment and utilities` - NOT EXPLAINED
- india-cdsco-gdp-guidelines-2024.pdf page 11 (uncovered): `+next to 11.15: pressurized gases` - NOT EXPLAINED
- india-cdsco-gdp-guidelines-2024.pdf page 11 (uncovered): `+next to 11.16: gases pressurized` - NOT EXPLAINED
- india-cdsco-gdp-guidelines-2024.pdf page 19 (uncovered): `+next to 16.17: the records` - NOT EXPLAINED
- india-cdsco-gdp-guidelines-2024.pdf page 19 (uncovered): `+next to 16.18: records the` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf Part II (section): `-1 sera 2 solution of serum proteins intended for injection 3 vaccines 4 toxins 5 antigens 6 anti toxins 7 sterilized surgical ligature and sterilized surgical suture 8 bacteriophages | +1 sera 2 solution of serum proteins intended for injection 3 vaccines 4 toxins 5 antigens 6 anti toxins 7 sterili` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf Part VII (section): `-73.297 | +73 297` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf Part VII 9 (clause): `-1977,370 | +1977 370 | +436` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf Part XI (section): `-4 lakes the aluminium or calcium salts lakes of any of the water soluble colours listed above 663 provided that in case of disinfectants in addition to the above said colours the colours referred in is 4707 part i as amended by bureau of indian standards from time to time or any of the colours list` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf Part XV (section): `+677 679` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf Part XV 30 (clause): `+xviii | -xviii | +bhasma | +si no dosage form shelf life or date of expiry with effect from the date of manufacture 1 2 3 i curanam kutinir curanam adai curanam kanchi curanam utkali curanam pittu curanam podithimirthal curanam podi 2 years pattru curanam pottanam or kizhi curanam ottratam curanam ` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf Part XV 8 (clause): `+dated` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf Part XV 5 #3 (clause): `+restricted` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf Part XV 4 #5 (clause): `+805` - A footnote reference number (verified: it starts a line or is printed small on the clause's pages) that the parser drops with the footnote mark; no regulation word changes.
- india-drugs-rules-1945-consolidated-2024-07.pdf Part XV 2 #12 (clause): `+restricted` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf Part XV 4 #11 (clause): `+loan | +a` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf Part XV 5 #8 (clause): `+1 this licence and` - Order or place only (verified mechanically): every stored word run of this discrepancy is printed on the clause's pages, and every page run it lacks is stored word for word (in this clause or another), so no word is lost or added; the engines read table cells, columns or figure labels in different orders.
- india-drugs-rules-1945-consolidated-2024-07.pdf Part XV 5 #9 (clause): `-1.896 | +1 896` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf Part XV 5 #10 (clause): `+899` - A footnote reference number (verified: it starts a line or is printed small on the clause's pages) that the parser drops with the footnote mark; no regulation word changes.
- india-drugs-rules-1945-consolidated-2024-07.pdf Part XV 4 #20 (clause): `-4 the licensee shall inform the licensing authority in writing in the event of any change in the constitution of the firm operating under the licence where any change in the constitution of the firm takes place the current licence shall be deemed to be valid for a maximum period of three months fro` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf Part XV 5 #18 (clause): `+986` - A footnote reference number (verified: it starts a line or is printed small on the clause's pages) that the parser drops with the footnote mark; no regulation word changes.
- india-drugs-rules-1945-consolidated-2024-07.pdf Part XV 9 (clause): `+d | +c` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf Part XV 6 #6 (clause): `-5 raughan 6 ghrita ney 6 zimad` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf Part XV 24 (clause): `-24 jauhar` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf Part XV 25 (clause): `-25 natool` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf Part XV 26 (clause): `-26 nashooq naswar` - Order or place only (verified mechanically): every stored word run of this discrepancy is printed on the clause's pages, and every page run it lacks is stored word for word (in this clause or another), so no word is lost or added; the engines read table cells, columns or figure labels in different orders.
- india-drugs-rules-1945-consolidated-2024-07.pdf Part XV 27 (clause): `-27 shamoom` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf Part XV 28 (clause): `-28 tablet mattirai` - Order or place only (verified mechanically): every stored word run of this discrepancy is printed on the clause's pages, and every page run it lacks is stored word for word (in this clause or another), so no word is lost or added; the engines read table cells, columns or figure labels in different orders.
- india-drugs-rules-1945-consolidated-2024-07.pdf Part XV 29 (clause): `-29 capsule` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf Part XV 30 #2 (clause): `-lashooq` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf Part XV 31 (clause): `-gulqand` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf Part XV 32 (clause): `-fateela` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf Part XV 33 (clause): `-ghaza ubtan sabhgh` - Order or place only (verified mechanically): every stored word run of this discrepancy is printed on the clause's pages, and every page run it lacks is stored word for word (in this clause or another), so no word is lost or added; the engines read table cells, columns or figure labels in different orders.
- india-drugs-rules-1945-consolidated-2024-07.pdf Part XV 35 (clause): `-35 capsule` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf Part XV 36 (clause): `-36 huqna` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf Part XV 37 (clause): `-37 naurah` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf Part XV 38 (clause): `-38 latookh` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf Part XV 39 (clause): `-39 vajoor throat pain | +24 jauhar 25 natool 26 nashooq naswar 27 shamoom 28 saoot nasal drops 29 mazoogh 30 tila 31 lashooq 32 gulqand 33 fateela 34 ghaza ubtan sabhgh 35 capsule 36 huqna 37 naurah 38 latookh 39 vajoor throat pain` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf Part XV 3 #28 (clause): `-note sample testing charges shall be determined or revised by the director pharmacopoeia commission for indian medicine and homoeopathy or government analyst of its central laboratory as the case may be in consultation with the ministry of ayurveda yoga and naturopathy unani siddha and homoeopathy ` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf Part XV 3 #30 (clause): `+equipment performance frequency frequency of calibration 1 temperature recorder compare against thermometer daily as often as necessary 2 refrigerated centrifuge observe speed and temperature each day of use as often as necessary 3 hematocrit centrifuge standardize before initial use after repair o` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf Part I 4 #2 (clause): `+− | +−` - Exponent minus (verified: every minus sign on the clause's pages follows a number or a unit, as in '10⁻⁶' or 'mg⁻¹'): the stored text has poppler's rendering of the superscript without the sign ('10-6' or '106'). Known superscript limitation (0b: keep superscripts as '10^-6').
- india-drugs-rules-1945-consolidated-2024-07.pdf Part I 3 #18 (clause): `+− | +−` - Exponent minus (verified: every minus sign on the clause's pages follows a number or a unit, as in '10⁻⁶' or 'mg⁻¹'): the stored text has poppler's rendering of the superscript without the sign ('10-6' or '106'). Known superscript limitation (0b: keep superscripts as '10^-6').
- india-drugs-rules-1945-consolidated-2024-07.pdf Part IV 2 (clause): `-chlorthalidone and other derivatives of | -chlorobenzene compound 1105 | -cis platin | -cyclophosphamide its salts 1105 | -cytarabine | -daunorubicin | +2 4 benzothiadiazine chlorpropamide its salts chlorthalidone and other derivatives of chlorobenzene compound 1105 cis platin cyclophosphamide its ` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf Part IV 1 #2 (clause): `+2 abciximab 3 acamprosate calcium 4 acebutol hydrochloride` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf Part IV 2 #2 (clause): `+3 acamprosate calcium 4 acebutol hydrochloride 5 aclarubicin` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf Part IV 3 (clause): `+4 acebutol hydrochloride 5 aclarubicin 6 albendazole` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf Part IV 4 (clause): `-4 acebutol hydrochloride 8 actilyse 9 acyclovir | -10 adenosine | -11 adrenocorticotrophic hormone | -acth | -12 alendronate sodium | -13 aliopurinol | -14 alphachymotrypsin | -1109 15 | -16 alprostadil | -17 amantadine hydrochloride | -18 amifostine | -19 amikacin sulphate | -hydrochloride 20 amil` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf Part IV 5 (clause): `-21 cycloserine 37 pentazocine` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf Part IV 6 (clause): `-22 diazepam 38 prulifloxacin` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf Part IV 7 (clause): `-23 diphenoxylate 39 pyrazinamide` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf Part IV 8 (clause): `-24 doripenem 40 rifabutin` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf Part IV 9 #2 (clause): `-25 ertapenem 41 rifampicin` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf Part IV 10 (clause): `-10 cefoperazone | -42 sodiumpara aminosalicylate` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf Part IV 11 (clause): `-27 ethionamide 43 sparfloxacin` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf Part IV 12 (clause): `-28 feropenem 44 tniacetazone` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf Part IV 13 (clause): `-29 gemifloxacin 45 tramadol` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf Part IV 14 (clause): `-14 ceftazidime 30 imipenem` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf Part IV 15 (clause): `-15 ceftibuten 31 lsoniazid` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf Part IV 16 (clause): `-16 ceftizoxime 32 levofloxacin` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf Part IV 99 (clause): `-99 gabapin nt 400 10 mg tablet 15 100 galvus 50 mg tablet 15 101 galvus met 50 1000 mg tablet 15 102 galvus met 50 500 mg tablet 15 103 geftinat 250 mg tablet 30 104 gelusil mps 250 50 250 mg liquid 200 ml 105 gemcal 500 mg 0.25 mcg 7.5 mg capsule 15 106 gemer 2 500 mg tablet 10 107 gibtulio 25 mg ` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf Part III 9.1 (clause): `-dop injection filterintegrity test de contamination by pass duct shut offdamper e s shut vfd offdampe r exhaustai secondaryfi m m m lter vfd velocitysensor v v variable frequencydrive m m m hepafil ter m filter pressuredifferensialgua ge hepabag in bag outunits` - Parser defect (0b): the labels of the HVAC schematic figure ('Shut- off Damper', 'VFD', 'EXHAUSTAI') are stored in the clause in layout order and glued; figure text, not regulatory prose.
- india-drugs-rules-1945-consolidated-2024-07.pdf Part XIII 4 #2 (clause): `-4 general provisions a pharmacy shall be conducted under the continuous personal supervision of a registered pharmacist whose name shall be displayed conspicuously in the premises the pharmacist shall always put on clean white overalls the premises and fittings of the pharmacy shall be properly kep` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf Part XIII 15 (clause): `+batch size 35001 to 1.5 lakhs single sampling plan sample size 200 aql 0.25 ac 1 r 2 batch size 150001 to 5 lakhs single sampling plan sample size 315 aql 0.25 ac 2 r 3 batch size over 5 lakhs single sampling plan sample size 500 aql 0.25 ac 3 r 4 | -aql 0.25 | +aql 0.25 | +batch size 150001 to 5 l` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf Part II #3 (section): `-b list of machinery equipment and minimum manufacturing premises required for the manufacturer of various categories of unani system of medicines one machine indicated for one category of medicine could be used for the manufacturing of other category of medicine also similarly some of the manufactu` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf Part II 8 #4 (clause): `-8 area specifications requirement for an applicant companies only to have gmp of rasaushadhies or rasamarunthukal and kushtajat herbo mineral metallic compounds of ayurveda siddha and unani medicines` - Order or place only (verified mechanically): every stored word run of this discrepancy is printed on the clause's pages, and every page run it lacks is stored word for word (in this clause or another), so no word is lost or added; the engines read table cells, columns or figure labels in different orders.
- india-drugs-rules-1945-consolidated-2024-07.pdf Part II 1 #7 (clause): `+common name as in afi api plant s botanical name quantity used per annum in kgs sources of supply part used traders manufacturers forest collectors cultivators imported total whole plants root leaf others | +name of extracts quantity used per annum in kgs sources of supply common name as in afi api` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf Part II 29 (clause): `-note 1 patent or proprietary medicines containing vitamins intended for prophylactic therapeutic or paediatric use shall bear on the label the words for prophylactic use for therapeutic use or for paediatric use as the case may be in the cases of paediatric preparations the age of the infant or the` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf Part II 6 #7 (clause): `-phencyclidine dexamphetamine | -barbital methylphenidate | -methamphetamine secobarbital | +hydrochloride amphetamine meprobamate phencyclidine barbital methamphetamine | +cyclobarbital 1288 1289 dexamphetamine methylphenidate secobarbital | -hydrochloride cyclobarbital | -1288 amphetamine 1289 mep` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf Part II Appendix I (section): `-1303` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf Part II Appendix III 1.8 (clause): `-1.8 animal toxicity requirements for clinical trials and marketing of a new drug systemic toxicity studies` - Order or place only (verified mechanically): every stored word run of this discrepancy is printed on the clause's pages, and every page run it lacks is stored word for word (in this clause or another), so no word is lost or added; the engines read table cells, columns or figure labels in different orders.
- india-drugs-rules-1945-consolidated-2024-07.pdf Part II Appendix III 1.9 (clause): `-1.9 number of animals required for repeated dose toxicity studies | -cerebrum cerebellum midbrain` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf _unnumbered:2 (unnumbered): `+3 | +32 | +43 | +1001 | -1001 | +1003 | -1003 | +1004 | -1004 | +1006 | -1006 | +1015 | -1015 | +1016 | -1016 | +1018 | -1018 | +1023 | -1023 | +1028 | -1028 | +1037 | -1037 | +1038 | -1038 | +1051 | -1051 | +1053 | -1053 | +1065 | -1065 | +1068 | -1068 | +1069 | -1069 | +1073 | -1073 | +1109 | -11` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf Table 2 3. (table_row): `-sulfophenylazo pyrazole` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf Table 2 17. (table_row): `-concentrated pyrene trisulfonic acid` - Order or place only (verified mechanically): every stored word run of this discrepancy is printed on the clause's pages, and every page run it lacks is stored word for word (in this clause or another), so no word is lost or added; the engines read table cells, columns or figure labels in different orders.
- india-drugs-rules-1945-consolidated-2024-07.pdf Table 2 37. (table_row): `-acid` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf Table 9 (1) (2) (3) (I) Rasayoga Containing… (table_row): `-1` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf Table 11 (1) (table_row): `-1 3` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf Table 11 (xi) (table_row): `-xi` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf Table 11 (xiii) (table_row): `-xiii` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf Table 11 (xiv) (table_row): `-xiv` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf Table 29 D (table_row): `-3` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf Table 32 row 1 (table_row): `-glove print` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf Table 33 API derived from animal sources (table_row): `-material into process` - Order or place only (verified mechanically): every stored word run of this discrepancy is printed on the clause's pages, and every page run it lacks is stored word for word (in this clause or another), so no word is lost or added; the engines read table cells, columns or figure labels in different orders.
- india-drugs-rules-1945-consolidated-2024-07.pdf Table 35 43. (table_row): `-24` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf Table 35 4. #5 (table_row): `-4 hydroxide` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf Table 46 12. (table_row): `-12 office total 1500` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf Table 56 Group (table_row): `-m f m f m f m f` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf page 158 (uncovered): `+in table row: serial number common name of colour colour index number chemical name of colour 1 2 3 4` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf page 159 (uncovered): `+serial number common name of colour colour index number chemical name of colour 1 2 3 4 concentrated pyrene trisulfonic acid` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf page 160 (uncovered): `+serial number common name of colour colour index number chemical name of colour 1 2 3 4 acid` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf page 161 (uncovered): `+serial number common name of colour colour index number chemical name of colour 1 2 3 4` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf page 315 (uncovered): `+14 vartti 15 netrabindu aschyotan` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf page 315 (uncovered): `+5 raughan 6 zimad 7 habb pill 8 shiyaf 9 qutoor drops` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf page 315 (uncovered): `+11 satt usara 12 kushta 13 joshanda single drugs` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf page 315 (uncovered): `+16 qurs tablet 17 marham qairooti 18 humool furzaja 19 bakhoor` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf page 315 (uncovered): `+21 maadni advia 22 ajsad advia 23 haiwani advia` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf page 316 (uncovered): `+28 tablet mattirai 29 capsule` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf page 325 (uncovered): `+in table row: revised by the director pharmacopoeia commission` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf page 325 (uncovered): `+in table row: indian medicine and homoeopathy or government analyst` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf page 325 (uncovered): `+in table row: its central laboratory` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf page 325 (uncovered): `+in table row: the case may be in consultation with the ministry of ayurveda yoga` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf page 326 (uncovered): `+in table row: serum proteins intended` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf page 328 (uncovered): `+in table row: class of drugs extent and conditions of exemption` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf page 329 (uncovered): `+class of drugs extent and conditions of exemption` - Text read outside any clause's stretch that is stored word for word in another clause of the document (verified mechanically): a running title, table caption or text read in another order.
- india-drugs-rules-1945-consolidated-2024-07.pdf page 343 (uncovered): `+5 danti 6 dhattura` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf page 343 (uncovered): `+8 jaipala seed 9 karaveera 10 langali` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf page 344 (uncovered): `+17 mancevikkalli exempted for external use euphorbia species` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf page 503 (uncovered): `+9 acyclovir 10 adenosine 11 adrenocorticotrophic hormone acth 12 alendronate sodium 13 aliopurinol 14 alphachymotrypsin 15` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf page 503 (uncovered): `+16 alprostadil 17 amantadine hydrochloride 18 amifostine 19 amikacin sulphate 20 amiloride hydrochloride 21 aminepline 22 aminoglu tethimide 23 aminosalicylic acid 24 amiodarone hydrochloride 25 amitriptyline 26 amlodipine besylate 27 amoscanate 28 amoxopine 29 amrinone lactate 30 analgin 31 androg` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf page 510 (uncovered): `+37 pentazocine 38 prulifloxacin 39 pyrazinamide 40 rifabutin 41 rifampicin 42 sodiumpara aminosalicylate 43 sparfloxacin 44 tniacetazone 45 tramadol` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf page 518 (uncovered): `+schedule j see rule 106 diseases and ailments by whatever name described which a drug may not purport to prevent or cure or make claims to prevent or cure 1 aids 2 angina pectoris 3 appendicitis` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf page 518 (uncovered): `+arteriosclerosis 5 baldness 6 blindness 7 bronchial asthma 8 cancer and benign tumour 9 cataract 10 change in colour of the hair and growth of new hair 11 change of foetal sex by drugs 12 congenital malformations 13 deafness 14 diabetes 15 diseases and disorders of uterus 16 epilepticfits and psych` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf page 526 (uncovered): `+in table row: the` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf page 795 (uncovered): `+in table row: phosphate` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf page 821 (uncovered): `+in table row: mixer` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf page 822 (uncovered): `+in table row: s no category of medicine minimum manufacturing space required machinery equipment recommended 1 2 3 4` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf page 826 (uncovered): `+s no category of medicine minimum manufacturing space required machinery equipment recommended 1 2 3 4` - Text read outside any clause's stretch that is stored word for word in another clause of the document (verified mechanically): a running title, table caption or text read in another order.
- india-drugs-rules-1945-consolidated-2024-07.pdf page 897 (uncovered): `+in table row: rodent rat` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf page 326 (uncovered): `+next to Part XV 4 #25: injections parenteral` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf page 502 (uncovered): `+next to Part IV 3: 8 actilyse` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf page 215 (uncovered): `+in two clauses Part XV 2 #2 and Part XV 2 #3: 2 each batch of drug imported into india shall be accompanied with a detailed batch test report and a batch release certificate duly signed and authenticated by the manufacturer with date of testing date of release and date of forwarding such reports th` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf page 218 (uncovered): `+in two clauses Part XV 1 #4 and Part XV 1 #5: 1 the licence shall be displayed in the office of the medical superintendent of government hospital head of institution of autonomous medical institution` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf page 240 (uncovered): `+in two clauses Part XV 1 #10 and Part XV 1 #11: 1 this licence shall be displayed in a prominent place in a part of the premises open to the public` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf page 258 (uncovered): `+in two clauses Part XV 1 #16 and Part XV 5 #8: 1 this licence and 889` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf page 316 (uncovered): `+in two clauses Part XV 28 and Part XV 39: 28 saoot nasal drops 29 mazoogh 30 tila` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf page 411 (uncovered): `+in two clauses Part I 5 #4 and Part I 6 #3: 5 labelling and storage should comply with the requirements for labelling and storage as laid down in the general monograph on bacterial vaccine` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf page 502 (uncovered): `+in two clauses Part IV 1 #2 and Part IV 2 #2: 2 abciximab 3 acamprosate calcium 4 acebutol hydrochloride 5 aclarubicin 6 albendazole` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf page 510 (uncovered): `+in two clauses Part IV 4 and Part IV 5: 5 cerdinir 6 cefditoren 7 cefepime 8 cefetamet 9 cefixime` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf page 510 (uncovered): `+in two clauses Part IV 11 and Part IV 4: 11 cefotaxime 12 cefpirome 13 cefpodoxime` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf page 510 (uncovered): `+in two clauses Part IV 10 and Part IV 4: 26 ethambutol hydrochloride` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf page 829 (uncovered): `+in two clauses Part II 1 #5 and Part II 3 #4: 1 si no 2 batch no` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf page 829 (uncovered): `+in two clauses Part II 4 #5 and Part II 7 #4: 4 name of the material and quantity` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf page 835 (uncovered): `+in two clauses Part II 1 #7 and Part II 2 #7: 2 shortage of raw material s inputs during the preceding year yes no if yes please indicate name` - NOT EXPLAINED
- india-gsr127e-2025-schm-timeline.pdf 4 (clause): `-4 the gazette of india extraordinary part ii sec 3 i form a application for seeking extension of compliance with revised good manufacturing practices gmp under schedule m of the drugs rules 1945 | -sarvesh kumar digitally signed by sarvesh kumar srivastava srivastava date 2025.02.11 22 35 41 05 30` - NOT EXPLAINED
- india-gsr127e-2025-schm-timeline.pdf page 1 (uncovered): `+1031 gi 2025 1` - NOT EXPLAINED
- india-gsr127e-2025-schm-timeline.pdf page 1 (uncovered): `+extraordinary part ii section 3 sub section i published by authority no 94 new delhi tuesday february 11 2025 magha 22 1946 cg dl e 11022025 260908` - NOT EXPLAINED
- india-gsr127e-2025-schm-timeline.pdf page 2 (uncovered): `+3 i iii vii viii` - NOT EXPLAINED
- india-gsr666e-2024-schm-corrigendum.pdf _unnumbered:1 (unnumbered): `-digitally signed by amit kumar amit kumar jaiswal jaiswal date 2024.10.29 19 30 05 05 30` - Front matter (cover page, document history, contents): the two engines read the cover's text boxes, address blocks and history table in different orders; not regulation text.
- india-gsr666e-2024-schm-corrigendum.pdf page 1 (uncovered): `+6992 gi 2024 1` - NOT EXPLAINED
- india-gsr666e-2024-schm-corrigendum.pdf page 1 (uncovered): `+extraordinary part ii section 3 sub section i published by authority no 608 new delhi monday october 28 2024 kartika 6 1946 cg dl e 29102024 258309` - NOT EXPLAINED
- india-schedule-m-2023-GSR922E.pdf Part I 1.2 (clause): `-7986 gi 2023 148` - Order or place only (verified mechanically): every stored word run of this discrepancy is printed on the clause's pages, and every page run it lacks is stored word for word (in this clause or another), so no word is lost or added; the engines read table cells, columns or figure labels in different orders.
- india-schedule-m-2023-GSR922E.pdf Part III 9.1 (clause): `-dop injection filterintegrity test de contamination by pass duct shut offdamper e s shut vfd offdampe r exhaustai secondaryfi m m m lter vfd velocitysensor v v variable frequencydrive m m m hepafil ter m filter pressuredifferensialgua ge hepabag in bag outunits` - Parser defect (0b): the labels of the HVAC schematic figure ('Shut- off Damper', 'VFD', 'EXHAUSTAI') are stored in the clause in layout order and glued; figure text, not regulatory prose.
- india-schedule-m-2023-GSR922E.pdf Part XIII 7 #2 (clause): `-manoj kumar digitally signed by manoj kumar verma date 2024.01.05 21 05 12 verma 05 30` - Parser defect (0b): the digital-signature stamp of the gazette signatory is stored inside the clause; clause text intact.
- india-schedule-m-2023-GSR922E.pdf page 1 (uncovered): `+gi 2023 1` - NOT EXPLAINED
- india-schedule-m-2023-GSR922E.pdf page 1 (uncovered): `+extraordinary part ii section 3 sub section i published by authority no 738 new delhi thursday december 28 2023 pausha 7 1945 cg dl e 05012024 251166 cg dl e 05012024 251166` - NOT EXPLAINED
- india-schedule-m-2023-GSR922E.pdf page 42 (uncovered): `+0.5 5.0 0.5 5.0` - NOT EXPLAINED
- india-schedule-m-2023-GSR922E.pdf page 60 (uncovered): `+vii viii xii` - NOT EXPLAINED
- india-schedule-m-2023-GSR922E.pdf page 81 (uncovered): `+iii vii viii` - NOT EXPLAINED
- india-schedule-m-2023-GSR922E.pdf page 94 (uncovered): `+iii vii viii xii xiii xiv iii` - NOT EXPLAINED
- india-schedule-m-2023-GSR922E.pdf page 95 (uncovered): `+vii viii iii vii` - NOT EXPLAINED
- india-schedule-m-2023-GSR922E.pdf page 96 (uncovered): `+iii vii viii` - NOT EXPLAINED
- india-schedule-m-2023-GSR922E.pdf page 99 (uncovered): `+iii vii viii` - NOT EXPLAINED
- india-schedule-m-2023-GSR922E.pdf page 102 (uncovered): `+iii vii iii vii` - NOT EXPLAINED
- india-schedule-m-2023-GSR922E.pdf page 103 (uncovered): `+viii xii iii vii viii iii` - NOT EXPLAINED
- india-schedule-m-2023-GSR922E.pdf page 117 (uncovered): `+iii iii vii viii` - NOT EXPLAINED
- india-schedule-m-2023-GSR922E.pdf page 119 (uncovered): `+iii vii 5 2` - NOT EXPLAINED
- india-schedule-m-2023-GSR922E.pdf page 123 (uncovered): `+i ii iii iii` - NOT EXPLAINED
- india-schedule-m-2023-GSR922E.pdf page 127 (uncovered): `+10.1 ii iii` - NOT EXPLAINED
- india-schedule-m-2023-GSR922E.pdf page 184 (uncovered): `+in table row: terminally sterilised products` - NOT EXPLAINED
- india-schedule-m-2023-GSR922E.pdf page 184 (uncovered): `+in table row: risk` - NOT EXPLAINED
- pics-pe008-4-site-master-file.pdf _unnumbered:1 (unnumbered): `-p 008 4 1 of 8 1 december 2010` - Order or place only (verified mechanically): every stored word run of this discrepancy is printed on the clause's pages, and every page run it lacks is stored word for word (in this clause or another), so no word is lost or added; the engines read table cells, columns or figure labels in different orders.
- pics-pe009-18-annexes.pdf _unnumbered:1 (unnumbered): `+pe 009 18 annexes 24 september 2026 | +table of contents | +i | -table of contents` - NOT EXPLAINED
- pics-pe009-18-annexes.pdf Annex 2A (section): `+table of contents | -i | +ii | -table of contents` - NOT EXPLAINED
- pics-pe009-18-annexes.pdf Annex 4 (section): `+table of contents | -ii | +iii | -table of contents` - NOT EXPLAINED
- pics-pe009-18-annexes.pdf Annex 10 (section): `+table of contents | -iii | +iv | -table of contents` - NOT EXPLAINED
- pics-pe009-18-annexes.pdf Annex 14 (section): `+table of contents | -iv | +v | -table of contents | +table of contents | -v | +vi | -table of contents | -pe 009 18 annexes vi 24 september 2026` - NOT EXPLAINED
- pics-pe009-18-annexes.pdf Annex 1 8.6 (clause): `-aseptic preparation and processing` - Order or place only (verified mechanically): every stored word run of this discrepancy is printed on the clause's pages, and every page run it lacks is stored word for word (in this clause or another), so no word is lost or added; the engines read table cells, columns or figure labels in different orders.
- pics-pe009-18-annexes.pdf Annex 1 8.10 (clause): `-annex 1 manufacture of sterile medicinal products` - Order or place only (verified mechanically): every stored word run of this discrepancy is printed on the clause's pages, and every page run it lacks is stored word for word (in this clause or another), so no word is lost or added; the engines read table cells, columns or figure labels in different orders.
- pics-pe009-18-annexes.pdf Annex 1 Glossary (section): `+− | +−` - NOT EXPLAINED
- pics-pe009-18-annexes.pdf Annex 2A 2 (clause): `-1 application of this annex applies to manufacturing steps illustrated in dark grey application of this annex or principles of this annex apply to steps illustrated in light grey apply depending on the requirements of national legislation 2 refer to points 5.32 for establishment of cell banks and s` - Order or place only (verified mechanically): every stored word run of this discrepancy is printed on the clause's pages, and every page run it lacks is stored word for word (in this clause or another), so no word is lost or added; the engines read table cells, columns or figure labels in different orders.
- pics-pe009-18-annexes.pdf Annex 2A 3 (clause): `+atmp manufacturing | -atmp manufacturing plasmid atmp manufacturing | -manufacturing transcription establishing mcb or | -plasmid dna construct wcb | -purification preparation thawing transfer of plasmid harvest | -dna to starter colony transfection | -formulation e g e coli induction | -filling ex` - NOT EXPLAINED
- pics-pe009-18-annexes.pdf Annex 14 10 (clause): `-annex 14 manufacture of products derived from human blood or plasma 2 for collection and regulatory submission of data information for plasma for fractionation annex 14 manufacture of products derived from human blood or plasma b other relevant documents reference should be made to the latest revis` - NOT EXPLAINED
- pics-pe009-18-annexes.pdf Annex 20 15 (clause): `-initiate quality risk management process risk assessment risk identification risk analysis risk evaluation unacceptable risk management tools risk communication risk control risk reduction risk acceptance output result of the quality risk management process risk review review events` - NOT EXPLAINED
- pics-pe009-18-annexes.pdf page 218 (uncovered): `+in table row: blood` - NOT EXPLAINED
- pics-pe009-18-annexes.pdf page 9 (uncovered): `+next to Annex 1 1: 2 principle` - NOT EXPLAINED
- pics-pe009-18-annexes.pdf page 9 (uncovered): `+next to Annex 1 2.1: principle 2` - NOT EXPLAINED
- pics-pe009-18-annexes.pdf page 79 (uncovered): `+next to Annex 2A 1 Principle: manufacture` - NOT EXPLAINED
- pics-pe009-18-annexes.pdf page 165 (uncovered): `+next to Annex 7 Principle: products` - NOT EXPLAINED
- pics-pe009-18-annexes.pdf page 135 (uncovered): `+in two clauses Annex 2B Glossary and Annex 3: annex 3 manufacture of radiopharmaceuticals` - NOT EXPLAINED
- pics-pe009-18-annexes.pdf page 154 (uncovered): `+in two clauses Annex 5 68 and Annex 6: annex 6 manufacture of medicinal gases` - NOT EXPLAINED
- pics-pe009-18-annexes.pdf page 165 (uncovered): `+in two clauses Annex 6 Glossary and Annex 7: annex 7 manufacture of herbal medicinal products` - NOT EXPLAINED
- pics-pe009-18-annexes.pdf page 170 (uncovered): `+in two clauses Annex 7 16 and Annex 8: annex 8 sampling of starting and packaging materials` - NOT EXPLAINED
- pics-pe009-18-annexes.pdf page 172 (uncovered): `+in two clauses Annex 8 5 and Annex 9: annex 9 manufacture of liquids creams and ointments` - NOT EXPLAINED
- pics-pe009-18-annexes.pdf page 174 (uncovered): `+in two clauses Annex 10 #2 and Annex 9 9: annex 10 manufacture of pressurised metered dose aerosol preparations for inhalation` - NOT EXPLAINED
- pics-pe009-18-annexes.pdf page 176 (uncovered): `+in two clauses Annex 10 9 and Annex 11: annex 11 computerised systems` - NOT EXPLAINED
- pics-pe009-18-annexes.pdf page 253 (uncovered): `+in two clauses Annex 17 Glossary and Annex 19: annex 19 reference and retention samples` - NOT EXPLAINED
- pics-pe009-18-part1.pdf Part I (section): `+i | +table of contents | -i | +ii | -table of contents | -pe 009 18 part i ii 24 september 2026` - NOT EXPLAINED
- pics-pe009-18-part1.pdf Part I 1.2 (clause): `-pe 009 18 part i − 1 24 september 2026` - Parser defect (0b): the PIC/S GMP Guide page footer ('PE 009-18 (Part I) -1- 24 September 2026') of the first pages is stored inside the clause; the regulation's words are intact.
- pics-pe009-18-part1.pdf Part I 1.4 (clause): `-pe 009 18 part i − 2 24 september 2026` - Parser defect (0b): the PIC/S GMP Guide page footer ('PE 009-18 (Part I) -1- 24 September 2026') of the first pages is stored inside the clause; the regulation's words are intact.
- pics-pe009-18-part1.pdf Part I 1.7 (clause): `-pe 009 18 part i − 3 24 september 2026` - Parser defect (0b): the PIC/S GMP Guide page footer ('PE 009-18 (Part I) -1- 24 September 2026') of the first pages is stored inside the clause; the regulation's words are intact.
- pics-pe009-18-part1.pdf Part I 1.8 (clause): `-pe 009 18 part i − 4 24 september 2026` - Parser defect (0b): the PIC/S GMP Guide page footer ('PE 009-18 (Part I) -1- 24 September 2026') of the first pages is stored inside the clause; the regulation's words are intact.
- pics-pe009-18-part1.pdf Part I 1.9 (clause): `-pe 009 18 part i − 5 24 september 2026` - Parser defect (0b): the PIC/S GMP Guide page footer ('PE 009-18 (Part I) -1- 24 September 2026') of the first pages is stored inside the clause; the regulation's words are intact.
- pics-pe009-18-part1.pdf Part I 1.11 (clause): `-pe 009 18 part i − 6 24 september 2026` - Parser defect (0b): the PIC/S GMP Guide page footer ('PE 009-18 (Part I) -1- 24 September 2026') of the first pages is stored inside the clause; the regulation's words are intact.
- pics-pe009-18-part1.pdf Part I 1.13 (clause): `-pe 009 18 part i − 7 24 september 2026` - Parser defect (0b): the PIC/S GMP Guide page footer ('PE 009-18 (Part I) -1- 24 September 2026') of the first pages is stored inside the clause; the regulation's words are intact.
- pics-pe009-18-part1.pdf Part I 2.4 (clause): `-pe 009 18 part i − 8 24 september 2026` - Parser defect (0b): the PIC/S GMP Guide page footer ('PE 009-18 (Part I) -1- 24 September 2026') of the first pages is stored inside the clause; the regulation's words are intact.
- pics-pe009-18-part1.pdf Part I 2.7 (clause): `-pe 009 18 part i − 9 24 september 2026` - Parser defect (0b): the PIC/S GMP Guide page footer ('PE 009-18 (Part I) -1- 24 September 2026') of the first pages is stored inside the clause; the regulation's words are intact.
- pics-pe009-18-part2.pdf Part II (section): `+i` - NOT EXPLAINED
- pics-pe009-18-part2.pdf Part II 1.2 (clause): `-pe 009 18 part ii − 1 24 september 2026 | -pe 009 18 part ii − 2 24 september 2026 | -increasing gmp requirements pe 009 18 part ii − 3 24 september 2026 quality management` - Parser defect (0b): the PIC/S GMP Guide page footer ('PE 009-18 (Part I) -1- 24 September 2026') of the first pages is stored inside the clause; the regulation's words are intact.
- pics-pe009-18-part2.pdf Part II 2.21 (clause): `-pe 009 18 part ii − 4 24 september 2026` - Parser defect (0b): the PIC/S GMP Guide page footer ('PE 009-18 (Part I) -1- 24 September 2026') of the first pages is stored inside the clause; the regulation's words are intact.
- pics-pe009-18-part2.pdf Part II 2.32 (clause): `-pe 009 18 part ii − 5 24 september 2026` - Parser defect (0b): the PIC/S GMP Guide page footer ('PE 009-18 (Part I) -1- 24 September 2026') of the first pages is stored inside the clause; the regulation's words are intact.
- pics-pe009-18-part2.pdf Part II 2.60 (clause): `-pe 009 18 part ii − 6 24 september 2026` - Parser defect (0b): the PIC/S GMP Guide page footer ('PE 009-18 (Part I) -1- 24 September 2026') of the first pages is stored inside the clause; the regulation's words are intact.
- pics-pe009-18-part2.pdf Part II 3.24 (clause): `-pe 009 18 part ii − 7 24 september 2026` - Parser defect (0b): the PIC/S GMP Guide page footer ('PE 009-18 (Part I) -1- 24 September 2026') of the first pages is stored inside the clause; the regulation's words are intact.
- pics-pe009-18-part2.pdf Part II 4.15 (clause): `-pe 009 18 part ii − 8 24 september 2026` - Parser defect (0b): the PIC/S GMP Guide page footer ('PE 009-18 (Part I) -1- 24 September 2026') of the first pages is stored inside the clause; the regulation's words are intact.
- pics-pe009-18-part2.pdf Part II 4.33 (clause): `-pe 009 18 part ii − 9 24 september 2026` - Parser defect (0b): the PIC/S GMP Guide page footer ('PE 009-18 (Part I) -1- 24 September 2026') of the first pages is stored inside the clause; the regulation's words are intact.
- pics-pe009-18-part2.pdf page 6 (uncovered): `+next to Part II 1.1: introduction 1` - NOT EXPLAINED
- pics-pi007-6-aseptic-validation.pdf _unnumbered:1 (unnumbered): `+pi 007 6 1 january 2011 | +i` - Front matter (cover page, document history, contents): the two engines read the cover's text boxes, address blocks and history table in different orders; not regulation text.
- pics-pi009-4-am-utilities.pdf Table 2 1. #2 (table_row): `-area operation items medicinal products notes crucial questions supporting documents` - Aide-memoire table layout (0b review): the stored row includes the repeated column-header row ('Area of operation / Items / Notes / Crucial questions / Supporting documents') or a cell continued from the previous page, which the second engine places outside the row's band; no requirement word changed.
- pics-pi009-4-am-utilities.pdf Table 3 2. #2 (table_row): `-2 area items pharmaceutical system notes crucial questions supporting documents` - Aide-memoire table layout (0b review): the stored row includes the repeated column-header row ('Area of operation / Items / Notes / Crucial questions / Supporting documents') or a cell continued from the previous page, which the second engine places outside the row's band; no requirement word changed.
- pics-pi009-4-am-utilities.pdf Table 3 2. #3 (table_row): `-2 area of operation items pharmaceutical water system notes crucial questions supporting documents` - Order or place only (verified mechanically): every stored word run of this discrepancy is printed on the clause's pages, and every page run it lacks is stored word for word (in this clause or another), so no word is lost or added; the engines read table cells, columns or figure labels in different orders.
- pics-pi009-4-am-utilities.pdf Table 4 3. #3 (table_row): `-3 steam systems` - Aide-memoire table layout (0b review): the stored row includes the repeated column-header row ('Area of operation / Items / Notes / Crucial questions / Supporting documents') or a cell continued from the previous page, which the second engine places outside the row's band; no requirement word changed.
- pics-pi009-4-am-utilities.pdf Table 5 4. #2 (table_row): `-capacity consumption` - Aide-memoire table layout (0b review): the stored row includes the repeated column-header row ('Area of operation / Items / Notes / Crucial questions / Supporting documents') or a cell continued from the previous page, which the second engine places outside the row's band; no requirement word changed.
- pics-pi009-4-am-utilities.pdf page 2 (uncovered): `+next to 2.1: introduction 2` - NOT EXPLAINED
- pics-pi009-4-am-utilities.pdf page 2 (uncovered): `+next to 2.2: 3 purpose` - NOT EXPLAINED
- pics-pi009-4-am-utilities.pdf page 2 (uncovered): `+next to 3.1: purpose 3` - NOT EXPLAINED
- pics-pi009-4-am-utilities.pdf page 2 (uncovered): `+next to 3.2: 4 scope` - NOT EXPLAINED
- pics-pi009-4-am-utilities.pdf page 2 (uncovered): `+next to 4.1: scope 4` - NOT EXPLAINED
- pics-pi009-4-am-utilities.pdf page 2 (uncovered): `+in two clauses 1 and _unnumbered:1: 1 document history` - NOT EXPLAINED
- pics-pi009-4-am-utilities.pdf page 2 (uncovered): `+in two clauses 5 and _unnumbered:1: 5 aide memoire` - NOT EXPLAINED
- pics-pi011-3-computerised-systems.pdf _unnumbered:1 (unnumbered): `+pi 011 3 25 september 2007 | +i | -pi 011 3 i 25 september 2007` - Front matter (cover page, document history, contents): the two engines read the cover's text boxes, address blocks and history table in different orders; not regulation text.
- pics-pi011-3-computerised-systems.pdf 6.2 (clause): `+9 | -operating software procedures and people hardware equipment firmware computer system controlled function controlling system or process computerised system operating environment including other networked or standalone computerised systems other systems media people equipment and procedures` - Parser defect (0b): figure text (system diagram, V-model) and a boxed note stored in the wrong clause order; the words are stored, their place is not.
- pics-pi011-3-computerised-systems.pdf 8.6 (clause): `+security` - NOT EXPLAINED
- pics-pi011-3-computerised-systems.pdf 9.1 (clause): `+14 | +development` - NOT EXPLAINED
- pics-pi011-3-computerised-systems.pdf 11 (clause): `-user requirements pq specification verifies functional specification oq verifies design specifications iq verifies system build` - Parser defect (0b): figure text (system diagram, V-model) and a boxed note stored in the wrong clause order; the words are stored, their place is not.
- pics-pi011-3-computerised-systems.pdf 20.1 (clause): `+authorities | +34` - NOT EXPLAINED
- pics-pi011-3-computerised-systems.pdf 20.2 (clause): `+records` - NOT EXPLAINED
- pics-pi011-3-computerised-systems.pdf 21.1 (clause): `+37` - A footnote reference number (verified: it starts a line or is printed small on the clause's pages) that the parser drops with the footnote mark; no regulation word changes.
- pics-pi011-3-computerised-systems.pdf 21.7 (clause): `+43` - A footnote reference number (verified: it starts a line or is printed small on the clause's pages) that the parser drops with the footnote mark; no regulation word changes.
- pics-pi011-3-computerised-systems.pdf 24 (clause): `-some of the details below are not relevant for cots but it is necessary to have clearly defined the requirements for intended use and to have assessed the application s fitness for purpose 56 under some circumstances access to source code cannot be guaranteed regulated users are expected to have as` - Parser defect (0b): figure text (system diagram, V-model) and a boxed note stored in the wrong clause order; the words are stored, their place is not.
- pics-pi011-3-computerised-systems.pdf 15 #2 (clause): `+58` - A footnote reference number (verified: it starts a line or is printed small on the clause's pages) that the parser drops with the footnote mark; no regulation word changes.
- pics-pi011-3-computerised-systems.pdf page 12 (uncovered): `+operating environment including other networked or standalone computerised systems other systems media people equipment and procedures computerised system computer system controlling system controlled function or process operating procedures and people equipment hardware firmware software` - Parser defect (0b): figure text (system diagram, V-model) and a boxed note stored in the wrong clause order; the words are stored, their place is not.
- pics-pi011-3-computerised-systems.pdf page 32 (uncovered): `+in two clauses 21.6 and 21.7: 21.7 whilst ec directive 2001 83 43` - NOT EXPLAINED
- pics-pi012-3-sterility-testing.pdf _unnumbered:1 (unnumbered): `+pi 012 3 25 september 2007 | +i` - Front matter (cover page, document history, contents): the two engines read the cover's text boxes, address blocks and history table in different orders; not regulation text.
- pics-pi012-3-sterility-testing.pdf 6.1 (clause): `+−` - Exponent minus (verified: every minus sign on the clause's pages follows a number or a unit, as in '10⁻⁶' or 'mg⁻¹'): the stored text has poppler's rendering of the superscript without the sign ('10-6' or '106'). Known superscript limitation (0b: keep superscripts as '10^-6').
- pics-pi014-3-isolators.pdf _unnumbered:1 (unnumbered): `+pi 014 3 25 september 2007 | -pi 014 3 25 september 2007` - NOT EXPLAINED
- pics-pi014-3-isolators.pdf page 3 (uncovered): `+next to 2.1: introduction 2` - NOT EXPLAINED
- pics-pi014-3-isolators.pdf page 4 (uncovered): `+next to 3: 4 scope` - NOT EXPLAINED
- pics-pi014-3-isolators.pdf page 4 (uncovered): `+next to 4.1: scope 4` - NOT EXPLAINED
- pics-pi023-2-am-qc-labs.pdf _unnumbered:1 (unnumbered): `+pi 023 2 25 september 2007 | +page 1 of 2` - Front matter (cover page, document history, contents): the two engines read the cover's text boxes, address blocks and history table in different orders; not regulation text.
- pics-pi023-2-am-qc-labs.pdf 3.2 (clause): `-1 | +2` - NOT EXPLAINED
- pics-pi023-2-am-qc-labs.pdf 5 (clause): `-2 | +i | -2 | +ii` - NOT EXPLAINED
- pics-pi023-2-am-qc-labs.pdf 8.7 (clause): `-i | +ii` - NOT EXPLAINED
- pics-pi023-2-am-qc-labs.pdf 9.4 (clause): `-pi 023 2 page ii of ii 25 september 2007 | -note some more details and specific items related to testing in chemical physical chemical and microbiological laboratories to be investigated in addition to above described subjects are involved in supplements 1 and 2 supplement no 1 to pi 023 1 aide mem` - NOT EXPLAINED
- pics-pi023-2-am-qc-labs.pdf Table 3 5.2. (table_row): `-premises continued area operation items notes crucial questions show me supporting` - Aide-memoire table layout (0b review): the stored row includes the repeated column-header row ('Area of operation / Items / Notes / Crucial questions / Supporting documents') or a cell continued from the previous page, which the second engine places outside the row's band; no requirement word changed.
- pics-pi023-2-am-qc-labs.pdf Table 3 6.1. (table_row): `-supplies continued area operation items notes show me crucial questions supporting documents` - Aide-memoire table layout (0b review): the stored row includes the repeated column-header row ('Area of operation / Items / Notes / Crucial questions / Supporting documents') or a cell continued from the previous page, which the second engine places outside the row's band; no requirement word changed.
- pics-pi023-2-am-qc-labs.pdf page 9 (uncovered): `+show me supporting documents` - Text read outside any clause's stretch that is stored word for word in another clause of the document (verified mechanically): a running title, table caption or text read in another order.
- pics-pi023-2-am-qc-labs.pdf page 10 (uncovered): `+show me supporting documents` - Text read outside any clause's stretch that is stored word for word in another clause of the document (verified mechanically): a running title, table caption or text read in another order.
- pics-pi023-2-am-qc-labs.pdf page 18 (uncovered): `+show me supporting documents` - Text read outside any clause's stretch that is stored word for word in another clause of the document (verified mechanically): a running title, table caption or text read in another order.
- pics-pi023-2-am-qc-labs.pdf page 2 (uncovered): `+next to 2: 3 purpose` - NOT EXPLAINED
- pics-pi023-2-am-qc-labs.pdf page 2 (uncovered): `+next to 3.1: purpose 3` - NOT EXPLAINED
- pics-pi023-2-am-qc-labs.pdf page 3 (uncovered): `+next to 3.2: 4 scope` - NOT EXPLAINED
- pics-pi023-2-am-qc-labs.pdf page 3 (uncovered): `+next to 4.1: scope 4` - NOT EXPLAINED
- pics-pi028-2-am-packaging.pdf Table 2 1.2 (table_row): `-material material received de dusting cleaning on outside separate area` - Aide-memoire table layout (0b review): the stored row includes the repeated column-header row ('Area of operation / Items / Notes / Crucial questions / Supporting documents') or a cell continued from the previous page, which the second engine places outside the row's band; no requirement word changed.
- pics-pi028-2-am-packaging.pdf Table 2 1.7 (table_row): `-documented` - Aide-memoire table layout (0b review): the stored row includes the repeated column-header row ('Area of operation / Items / Notes / Crucial questions / Supporting documents') or a cell continued from the previous page, which the second engine places outside the row's band; no requirement word changed.
- pics-pi028-2-am-packaging.pdf page 5 (uncovered): `+items notes crucial questions supporting documents` - Text read outside any clause's stretch that is stored word for word in another clause of the document (verified mechanically): a running title, table caption or text read in another order.
- pics-pi028-2-am-packaging.pdf page 6 (uncovered): `+items notes crucial questions supporting documents` - Text read outside any clause's stretch that is stored word for word in another clause of the document (verified mechanically): a running title, table caption or text read in another order.
- pics-pi028-2-am-packaging.pdf page 7 (uncovered): `+items notes crucial questions supporting documents adequate and documented investigation of packaging process deviations` - Aide-memoire page layout: repeated column headers and section headings of the table, which the stored rows hold once per table.
- pics-pi028-2-am-packaging.pdf page 2 (uncovered): `+next to 2.1: introduction 2` - NOT EXPLAINED
- pics-pi028-2-am-packaging.pdf page 2 (uncovered): `+next to 2.3: 3 purpose` - NOT EXPLAINED
- pics-pi028-2-am-packaging.pdf page 2 (uncovered): `+next to 3.1: purpose 3` - NOT EXPLAINED
- pics-pi028-2-am-packaging.pdf page 3 (uncovered): `+next to 3.2: 4 scope` - NOT EXPLAINED
- pics-pi028-2-am-packaging.pdf page 3 (uncovered): `+next to 4.1: scope 4` - NOT EXPLAINED
- pics-pi028-2-am-packaging.pdf page 2 (uncovered): `+in two clauses 1 and _unnumbered:1: 1 document history` - NOT EXPLAINED
- pics-pi028-2-am-packaging.pdf page 2 (uncovered): `+in two clauses 5 and _unnumbered:1: 5 aide memoire` - NOT EXPLAINED
- pics-pi030-1-am-api.pdf 5 (clause): `-5 aide memoire | +systems for material status control are acceptable in such cases physical segregation may not be required | -10.11 5.40 7.20 systems for material | -status control are | -acceptable in such | -cases physical | -segregation may not be | -required` - NOT EXPLAINED
- pics-pi030-1-am-api.pdf Table 3 Product Quality Review (PQR) (table_row): `-critical ipc api test deviations complaints returns recalls non conformances related including effectiveness corrective preventive actions conducted changes conducted stability program verified based validation status recorded required changes highlighted implemented through change control system 2` - Aide-memoire table layout (0b review): the stored row includes the repeated column-header row ('Area of operation / Items / Notes / Crucial questions / Supporting documents') or a cell continued from the previous page, which the second engine places outside the row's band; no requirement word changed.
- pics-pi030-1-am-api.pdf Table 10 Packaging and labelling (table_row): `-packaging impact packaging materials product quality do packaging materials alter quality intermediate 9.21` - Aide-memoire table layout (0b review): the stored row includes the repeated column-header row ('Area of operation / Items / Notes / Crucial questions / Supporting documents') or a cell continued from the previous page, which the second engine places outside the row's band; no requirement word changed.
- pics-pi030-1-am-api.pdf Table 13 Validation Documentation (table_row): `-corrective actions implemented` - Order or place only (verified mechanically): every stored word run of this discrepancy is printed on the clause's pages, and every page run it lacks is stored word for word (in this clause or another), so no word is lost or added; the engines read table cells, columns or figure labels in different orders.
- pics-pi030-1-am-api.pdf page 6 (uncovered): `+a review of oos critical ipc and api test results deviations complaints returns and recalls non conformances and related investigations including the effectiveness of the corrective and preventive actions conducted a review of changes conducted stability program data verified are required changes h` - Aide-memoire page layout: repeated column headers and section headings of the table, which the stored rows hold once per table.
- pics-pi030-1-am-api.pdf page 7 (uncovered): `+2 quality management system` - Text read outside any clause's stretch that is stored word for word in another clause of the document (verified mechanically): a running title, table caption or text read in another order.
- pics-pi030-1-am-api.pdf page 8 (uncovered): `+in table row: 4 building and facilities` - NOT EXPLAINED
- pics-pi030-1-am-api.pdf page 8 (uncovered): `+in table row: operations items notes crucial questions show me supporting documents` - NOT EXPLAINED
- pics-pi030-1-am-api.pdf page 9 (uncovered): `+4 building and facilities` - Text read outside any clause's stretch that is stored word for word in another clause of the document (verified mechanically): a running title, table caption or text read in another order.
- pics-pi030-1-am-api.pdf page 10 (uncovered): `+in table row: 4 building` - NOT EXPLAINED
- pics-pi030-1-am-api.pdf page 10 (uncovered): `+in table row: facilities` - NOT EXPLAINED
- pics-pi030-1-am-api.pdf page 10 (uncovered): `+in table row: and` - NOT EXPLAINED
- pics-pi030-1-am-api.pdf page 14 (uncovered): `+in table row: 8 production` - NOT EXPLAINED
- pics-pi030-1-am-api.pdf page 14 (uncovered): `+in table row: controls` - NOT EXPLAINED
- pics-pi030-1-am-api.pdf page 14 (uncovered): `+in table row: process` - NOT EXPLAINED
- pics-pi030-1-am-api.pdf page 14 (uncovered): `+in table row: and` - NOT EXPLAINED
- pics-pi030-1-am-api.pdf page 15 (uncovered): `+in table row: 8 production` - NOT EXPLAINED
- pics-pi030-1-am-api.pdf page 15 (uncovered): `+in table row: controls` - NOT EXPLAINED
- pics-pi030-1-am-api.pdf page 15 (uncovered): `+operations items notes crucial questions show me supporting documents in process` - Aide-memoire page layout: repeated column headers and section headings of the table, which the stored rows hold once per table.
- pics-pi030-1-am-api.pdf page 15 (uncovered): `+in table row: and` - NOT EXPLAINED
- pics-pi030-1-am-api.pdf page 15 (uncovered): `+packaging and labelling impact of packaging materials on product quality do packaging materials alter the quality of the api or intermediate 9.21` - Aide-memoire page layout: repeated column headers and section headings of the table, which the stored rows hold once per table.
- pics-pi030-1-am-api.pdf page 17 (uncovered): `+in table row: 10 storage` - NOT EXPLAINED
- pics-pi030-1-am-api.pdf page 17 (uncovered): `+in table row: distribution` - NOT EXPLAINED
- pics-pi030-1-am-api.pdf page 17 (uncovered): `+in table row: operations items notes crucial questions show me supporting documents` - NOT EXPLAINED
- pics-pi030-1-am-api.pdf page 17 (uncovered): `+in table row: and` - NOT EXPLAINED
- pics-pi030-1-am-api.pdf page 19 (uncovered): `+in table row: 12 validation` - NOT EXPLAINED
- pics-pi030-1-am-api.pdf page 20 (uncovered): `+in table row: 12 validation` - NOT EXPLAINED
- pics-pi030-1-am-api.pdf page 2 (uncovered): `+next to 2.1: introduction 2` - NOT EXPLAINED
- pics-pi030-1-am-api.pdf page 2 (uncovered): `+next to 2.3: 3 purpose` - NOT EXPLAINED
- pics-pi030-1-am-api.pdf page 2 (uncovered): `+next to 3.1: purpose 3` - NOT EXPLAINED
- pics-pi030-1-am-api.pdf page 2 (uncovered): `+next to 3.2: 4 scope` - NOT EXPLAINED
- pics-pi030-1-am-api.pdf page 2 (uncovered): `+next to 4.1: scope 4` - NOT EXPLAINED
- pics-pi030-1-am-api.pdf page 2 (uncovered): `+in two clauses 1 and _unnumbered:1: 1 document history` - NOT EXPLAINED
- pics-pi038-2-am-qrm.pdf Table 2 1.12 (table_row): `-2 expectations on how qrm should be implemented` - Order or place only (verified mechanically): every stored word run of this discrepancy is printed on the clause's pages, and every page run it lacks is stored word for word (in this clause or another), so no word is lost or added; the engines read table cells, columns or figure labels in different orders.
- pics-pi038-2-am-qrm.pdf page 2 (uncovered): `+next to 2.1: introduction 2` - NOT EXPLAINED
- pics-pi038-2-am-qrm.pdf page 3 (uncovered): `+next to 2.5: 3 purpose` - NOT EXPLAINED
- pics-pi038-2-am-qrm.pdf page 3 (uncovered): `+next to 3.1: purpose 3` - NOT EXPLAINED
- pics-pi038-2-am-qrm.pdf page 3 (uncovered): `+next to 3.2: 4 scope` - NOT EXPLAINED
- pics-pi038-2-am-qrm.pdf page 3 (uncovered): `+next to 4.1: scope 4` - NOT EXPLAINED
- pics-pi040-1-deficiency-classification.pdf page 3 (uncovered): `+next to Appendix 2 2.1: introduction 2` - NOT EXPLAINED
- pics-pi040-1-deficiency-classification.pdf page 2 (uncovered): `+in two clauses 1 and Appendix 2 1: 1 document history` - NOT EXPLAINED
- pics-pi040-1-deficiency-classification.pdf page 2 (uncovered): `+in two clauses 3 and Appendix 2 3: 3 purpose and scope` - NOT EXPLAINED
- pics-pi041-1-data-integrity.pdf 8.4 (clause): `+item generation` - Parser defect (0b): the section's lead-in and the table title ('Item: Generation') sit between the clause and its table rows; the clause boundary falls inside the heading.
- pics-pi041-1-data-integrity.pdf 8.6.1 (clause): `-8.6.1 the items listed in the table below should be controlled to assure that a record is properly filled out` - Order or place only (verified mechanically): every stored word run of this discrepancy is printed on the clause's pages, and every page run it lacks is stored word for word (in this clause or another), so no word is lost or added; the engines read table cells, columns or figure labels in different orders.
- pics-pi041-1-data-integrity.pdf 8.10.2 (clause): `-9 note that storage periods for some documents may be dictated by other local or national legislation` - Order or place only (verified mechanically): every stored word run of this discrepancy is printed on the clause's pages, and every page run it lacks is stored word for word (in this clause or another), so no word is lost or added; the engines read table cells, columns or figure labels in different orders.
- pics-pi041-1-data-integrity.pdf 9.3 (clause): `-9.3 validation and maintenance` - Order or place only (verified mechanically): every stored word run of this discrepancy is printed on the clause's pages, and every page run it lacks is stored word for word (in this clause or another), so no word is lost or added; the engines read table cells, columns or figure labels in different orders.
- pics-pi041-1-data-integrity.pdf 9.4 (clause): `-9.4 data transfer` - Order or place only (verified mechanically): every stored word run of this discrepancy is printed on the clause's pages, and every page run it lacks is stored word for word (in this clause or another), so no word is lost or added; the engines read table cells, columns or figure labels in different orders.
- pics-pi041-1-data-integrity.pdf 2 #2 (clause): `-2 expectation computerised systems should be protected from accidental changes or deliberate manipulation companies should assess systems and their design to prevent unauthorised changes to validated settings that may ultimately affect data integrity consideration should be given to the physical se` - Parser defect (0b): known limitation - the numbered table rows '1. Expectation' / '2. Expectation' start clauses that hold following text, so this clause's text is out of order against the page.
- pics-pi041-1-data-integrity.pdf page 17 (uncovered): `+in table row: data integrity attribute requirement` - NOT EXPLAINED
- pics-pi041-1-data-integrity.pdf page 3 (uncovered): `+next to 2.1: introduction 2` - NOT EXPLAINED
- pics-pi043-1-am-cross-contamination.pdf Table 7 Nr. (table_row): `-general organisational controls` - Order or place only (verified mechanically): every stored word run of this discrepancy is printed on the clause's pages, and every page run it lacks is stored word for word (in this clause or another), so no word is lost or added; the engines read table cells, columns or figure labels in different orders.
- pics-pi043-1-am-cross-contamination.pdf page 16 (uncovered): `+in table row: 3.2` - NOT EXPLAINED
- pics-pi043-1-am-cross-contamination.pdf page 16 (uncovered): `+in table row: 3.9` - NOT EXPLAINED
- pics-pi043-1-am-cross-contamination.pdf page 16 (uncovered): `+in table row: 1.12 1.13 4.3 4.4 annex 15` - NOT EXPLAINED
- pics-pi043-1-am-cross-contamination.pdf page 3 (uncovered): `+next to 2.1: introduction 2` - NOT EXPLAINED
- pics-pi045-1-excipient-risk-assessment.pdf page 3 (uncovered): `+next to 2: 3 scope` - NOT EXPLAINED
- pics-pi045-1-excipient-risk-assessment.pdf page 3 (uncovered): `+next to 3.1: scope 3` - NOT EXPLAINED
- pics-pi047-1-gdp-active-substances.pdf Annex (section): `+substances | -substances` - NOT EXPLAINED
- pics-pi047-1-gdp-active-substances.pdf page 2 (uncovered): `+in two clauses 1 and _unnumbered:1: 1 chapter 1 scope` - NOT EXPLAINED
- pics-pi052-1-am-hbel.pdf Table 3 row 1 (table_row): `-section 2 qrm study for organisational technical control measures based on` - Aide-memoire table layout (0b review): the stored row includes the repeated column-header row ('Area of operation / Items / Notes / Crucial questions / Supporting documents') or a cell continued from the previous page, which the second engine places outside the row's band; no requirement word changed.
- pics-pi052-1-am-hbel.pdf page 2 (uncovered): `+next to 2.1: introduction 2` - NOT EXPLAINED
- pics-pi052-1-am-hbel.pdf page 3 (uncovered): `+next to 2.7: 3 purpose` - NOT EXPLAINED
- pics-pi052-1-am-hbel.pdf page 3 (uncovered): `+next to 3.1: purpose 3` - NOT EXPLAINED
- pics-pi052-1-am-hbel.pdf page 3 (uncovered): `+next to 3.1: 4 scope` - NOT EXPLAINED
- pics-pi052-1-am-hbel.pdf page 3 (uncovered): `+next to 4.1: scope 4` - NOT EXPLAINED
- pics-pi052-1-am-hbel.pdf page 2 (uncovered): `+in two clauses 1 and _unnumbered:1: 1 document history` - NOT EXPLAINED
- pics-pi053-1-qa-cross-contamination.pdf _unnumbered:2 (unnumbered): `-1 document history` - Order or place only (verified mechanically): every stored word run of this discrepancy is printed on the clause's pages, and every page run it lacks is stored word for word (in this clause or another), so no word is lost or added; the engines read table cells, columns or figure labels in different orders.
- pics-pi054-1-pqs-effectiveness.pdf page 5 (uncovered): `+in table row: changes` - NOT EXPLAINED
- pics-pi054-1-pqs-effectiveness.pdf page 5 (uncovered): `+in table row: proposed in a` - NOT EXPLAINED
- pics-pi054-1-pqs-effectiveness.pdf page 5 (uncovered): `+in table row: proposed` - NOT EXPLAINED
- pics-pi054-1-pqs-effectiveness.pdf page 5 (uncovered): `+in table row: potential impacts of` - NOT EXPLAINED
- pics-pi054-1-pqs-effectiveness.pdf page 5 (uncovered): `+in table row: on other products processes` - NOT EXPLAINED
- pics-pi054-1-pqs-effectiveness.pdf page 2 (uncovered): `+next to 2.3: 3 purpose` - NOT EXPLAINED
- pics-pi054-1-pqs-effectiveness.pdf page 2 (uncovered): `+next to 3.1: purpose 3` - NOT EXPLAINED
- pics-pi058-1-annex1-interpretation.pdf 4.10 (clause): `-10 revision history` - Order or place only (verified mechanically): every stored word run of this discrepancy is printed on the clause's pages, and every page run it lacks is stored word for word (in this clause or another), so no word is lost or added; the engines read table cells, columns or figure labels in different orders.
- pics-pi058-1-annex1-interpretation.pdf Table 11 9.30 (table_row): `-viii` - NOT EXPLAINED
- pics-pi058-1-annex1-interpretation.pdf page 3 (uncovered): `+2 introduction 2.1 purpose and scope` - NOT EXPLAINED
- pics-pi058-1-annex1-interpretation.pdf page 3 (uncovered): `+next to 2.1.2: 2.2 basics` - NOT EXPLAINED
- pics-pi058-1-annex1-interpretation.pdf page 3 (uncovered): `+next to 2.2.1: basics 2.2` - NOT EXPLAINED
- who-trs1010-a10-stability.pdf Appendix 3 1.2 (clause): `+1.3` - NOT EXPLAINED
- who-trs1010-a10-stability.pdf Appendix 3 2.1.7.1 (clause): `-12 months or 6 months as | -described in point 2.1.7 | +12 months or 6 months as described in point 2.1.7` - NOT EXPLAINED
- who-trs1010-a10-stability.pdf Appendix 3 2.1.7.2 (clause): `-6 months | +6 months` - NOT EXPLAINED
- who-trs1010-a10-stability.pdf Appendix 3 2.2.7.1 (clause): `-12 months or 6 months as | -referred to in section 2.2.7 | +12 months or 6 months as referred to in section 2.2.7 o t e c h r e p o r t s e s n o 1 0 1 0 2 0 1 8` - NOT EXPLAINED
- who-trs1010-a10-stability.pdf Appendix 3 2.2.7.3 (clause): `-12 months or 6 months as | -6 months | +6 months | +testing conditions | +condition | -calculation testing conditions condition | +calculation` - NOT EXPLAINED
- who-trs1010-a10-stability.pdf Appendix 3 2.2.7.4 (clause): `-6 months | +6 months` - NOT EXPLAINED
- who-trs1010-a10-stability.pdf Appendix 2 1 (clause): `-recommended labelling statementa | +recommended labelling statementa | +accelerated | -accelerated | -intermediate failure during accelerated stability studies 30 c 65 % rh | +accelerated | -accelerated | +accelerated | -accelerated` - NOT EXPLAINED
- who-trs1010-a10-stability.pdf Appendix 2 2 (clause): `-recommended labelling statementa | +recommended labelling statementa | +accelerated | -accelerated | -intermediate failure during accelerated stability studies 30 c 65 % rh | +accelerated | -accelerated | +accelerated | -accelerated | +that cannot tolerate refrigeration | -that cannot tolerate refr` - NOT EXPLAINED
- who-trs1010-a10-stability.pdf Appendix 3 (section): `+products approved in zone ii | -who recommended products approved in | +are based who recommended | -zone ii are based | +does not require any special storage conditions or similar i e no temperature mentioned eu | +finished pharmaceutical product fpp is stable at long term conditions with no signi` - NOT EXPLAINED
- who-trs1010-a10-stability.pdf page 4 (uncovered): `+next to Appendix 3 1.1: introduction 1` - NOT EXPLAINED
- who-trs1010-a8-hvac-nonsterile.pdf 7.11 (clause): `-1.8 | +annex table | -elbat aseicnelaviuqe etamixorppa sdradnats tset retlfi fo nosirapmoc 0101 on seires troper lacinhcet ohw deunitnoc 1.8 a elbat deunitnoc 1.8 a elbat tnerruc si noitacfiissalc eht taht erusne a ezis elcitrap gnitartenep tsom sppm retlfi ot setaler | +8.1 comparison of filter te` - Parser defect (0b): Table A8.1 (filter classes) is printed on landscape pages; poppler reads the turned text backwards ('elbat' for 'table') into clause 7.11 and splits the table's columns, so the stored rows lack or misplace values. Re-extract the landscape pages along their lines.
- who-trs1010-a8-hvac-nonsterile.pdf Table 1 ISO 29463 (table_row): `-iso 29463` - Parser defect (0b): Table A8.1 (filter classes) is printed on landscape pages; poppler reads the turned text backwards ('elbat' for 'table') into clause 7.11 and splits the table's columns, so the stored rows lack or misplace values. Re-extract the landscape pages along their lines.
- who-trs1010-a8-hvac-nonsterile.pdf Table 1 EN 779 & EN 1822 (table_row): `-779 1822 1822 2009 u 17 99.999995 u 16 99.99995 u 15 99.9995 h 14 99.995 h 13 99.95 e 99.5 e e 85 779 2012 f 9 f 8 f 7` - Parser defect (0b): Table A8.1 (filter classes) is printed on landscape pages; poppler reads the turned text backwards ('elbat' for 'table') into clause 7.11 and splits the table's columns, so the stored rows lack or misplace values. Re-extract the landscape pages along their lines.
- who-trs1010-a8-hvac-nonsterile.pdf Table 1 Eurovent 4/5 ASHRAE 52.1 BS6540 Part 1 (table_row): `-> 95 95 90 85 80` - Parser defect (0b): Table A8.1 (filter classes) is printed on landscape pages; poppler reads the turned text backwards ('elbat' for 'table') into clause 7.11 and splits the table's columns, so the stored rows lack or misplace values. Re-extract the landscape pages along their lines.
- who-trs1010-a8-hvac-nonsterile.pdf Table 1 Eurovent 4/5 ASHRAE 52.1 BS6540 Part 1 #2 (table_row): `-> 98 > 98` - Parser defect (0b): Table A8.1 (filter classes) is printed on landscape pages; poppler reads the turned text backwards ('elbat' for 'table') into clause 7.11 and splits the table's columns, so the stored rows lack or misplace values. Re-extract the landscape pages along their lines.
- who-trs1010-a8-hvac-nonsterile.pdf Table 1 ASHRAE 52.2 (table_row): `-ashrae 52.2 rating` - Parser defect (0b): Table A8.1 (filter classes) is printed on landscape pages; poppler reads the turned text backwards ('elbat' for 'table') into clause 7.11 and splits the table's columns, so the stored rows lack or misplace values. Re-extract the landscape pages along their lines.
- who-trs1010-a8-hvac-nonsterile.pdf Table 2 ISO 29463 (table_row): `-iso 29463` - Parser defect (0b): Table A8.1 (filter classes) is printed on landscape pages; poppler reads the turned text backwards ('elbat' for 'table') into clause 7.11 and splits the table's columns, so the stored rows lack or misplace values. Re-extract the landscape pages along their lines.
- who-trs1010-a8-hvac-nonsterile.pdf Table 2 header (table_header): `-2012` - Parser defect (0b): Table A8.1 (filter classes) is printed on landscape pages; poppler reads the turned text backwards ('elbat' for 'table') into clause 7.11 and splits the table's columns, so the stored rows lack or misplace values. Re-extract the landscape pages along their lines.
- who-trs1010-a8-hvac-nonsterile.pdf Table 2 row 3 (table_row): `-mpps integral overall efficiency %` - Parser defect (0b): Table A8.1 (filter classes) is printed on landscape pages; poppler reads the turned text backwards ('elbat' for 'table') into clause 7.11 and splits the table's columns, so the stored rows lack or misplace values. Re-extract the landscape pages along their lines.
- who-trs1010-a8-hvac-nonsterile.pdf Table 2 Eurovent 4/5 ASHRAE 52.1 BS6540 Part 1 (table_row): `-70 65 60 55 50 40 35 30 25 20 < 20` - Parser defect (0b): Table A8.1 (filter classes) is printed on landscape pages; poppler reads the turned text backwards ('elbat' for 'table') into clause 7.11 and splits the table's columns, so the stored rows lack or misplace values. Re-extract the landscape pages along their lines.
- who-trs1010-a8-hvac-nonsterile.pdf Table 2 Eurovent 4/5 ASHRAE 52.1 BS6540 Part 1 #2 (table_row): `-eurovent ashrae 52.1 bs 6540 part 1 average arrestance am % superseded` - Parser defect (0b): Table A8.1 (filter classes) is printed on landscape pages; poppler reads the turned text backwards ('elbat' for 'table') into clause 7.11 and splits the table's columns, so the stored rows lack or misplace values. Re-extract the landscape pages along their lines.
- who-trs1010-a8-hvac-nonsterile.pdf Table 2 ASHRAE 52.2 (table_row): `-ashrae 52.2 rating` - Parser defect (0b): Table A8.1 (filter classes) is printed on landscape pages; poppler reads the turned text backwards ('elbat' for 'table') into clause 7.11 and splits the table's columns, so the stored rows lack or misplace values. Re-extract the landscape pages along their lines.
- who-trs1010-a8-hvac-nonsterile.pdf Table 3 ISO 29463 (table_row): `-iso 29463` - Parser defect (0b): Table A8.1 (filter classes) is printed on landscape pages; poppler reads the turned text backwards ('elbat' for 'table') into clause 7.11 and splits the table's columns, so the stored rows lack or misplace values. Re-extract the landscape pages along their lines.
- who-trs1010-a8-hvac-nonsterile.pdf Table 3 header (table_header): `-2012` - Parser defect (0b): Table A8.1 (filter classes) is printed on landscape pages; poppler reads the turned text backwards ('elbat' for 'table') into clause 7.11 and splits the table's columns, so the stored rows lack or misplace values. Re-extract the landscape pages along their lines.
- who-trs1010-a8-hvac-nonsterile.pdf Table 3 row 3 (table_row): `-g 2 g 1` - Parser defect (0b): Table A8.1 (filter classes) is printed on landscape pages; poppler reads the turned text backwards ('elbat' for 'table') into clause 7.11 and splits the table's columns, so the stored rows lack or misplace values. Re-extract the landscape pages along their lines.
- who-trs1010-a8-hvac-nonsterile.pdf Table 3 Eurovent 4/5 ASHRAE 52.1 BS6540 Part 1 #2 (table_row): `-<` - Parser defect (0b): Table A8.1 (filter classes) is printed on landscape pages; poppler reads the turned text backwards ('elbat' for 'table') into clause 7.11 and splits the table's columns, so the stored rows lack or misplace values. Re-extract the landscape pages along their lines.
- who-trs1010-a8-hvac-nonsterile.pdf Table 3 ASHRAE 52.2 (table_row): `-ashrae 52.2 rating` - Parser defect (0b): Table A8.1 (filter classes) is printed on landscape pages; poppler reads the turned text backwards ('elbat' for 'table') into clause 7.11 and splits the table's columns, so the stored rows lack or misplace values. Re-extract the landscape pages along their lines.
- who-trs1010-a8-hvac-nonsterile.pdf page 15 (uncovered): `+90 f 8` - Same as clause 7.11 (0b): text of the landscape Table A8.1 that no stored clause holds in readable form.
- who-trs1010-a8-hvac-nonsterile.pdf page 15 (uncovered): `+> 98 85 f 7 eu 7 > 98 80` - Same as clause 7.11 (0b): text of the landscape Table A8.1 that no stored clause holds in readable form.
- who-trs1010-a8-hvac-nonsterile.pdf page 16 (uncovered): `+264 who technical report series no 1010 2018 who expert committee on specifications for pharmaceutical preparations fifty second report table a 8.1 continued` - Same as clause 7.11 (0b): text of the landscape Table A8.1 that no stored clause holds in readable form.
- who-trs1010-a8-hvac-nonsterile.pdf page 16 (uncovered): `+36492 osi superseded` - Same as clause 7.11 (0b): text of the landscape Table A8.1 that no stored clause holds in readable form.
- who-trs1010-a8-hvac-nonsterile.pdf page 16 (uncovered): `+75 eu 6` - Same as clause 7.11 (0b): text of the landscape Table A8.1 that no stored clause holds in readable form.
- who-trs1010-a8-hvac-nonsterile.pdf page 16 (uncovered): `+70 m 6 2102 977 ne` - Same as clause 7.11 (0b): text of the landscape Table A8.1 that no stored clause holds in readable form.
- who-trs1010-a8-hvac-nonsterile.pdf page 16 (uncovered): `+65 > 95 60` - Same as clause 7.11 (0b): text of the landscape Table A8.1 that no stored clause holds in readable form.
- who-trs1010-a8-hvac-nonsterile.pdf page 16 (uncovered): `+> 95 55 eu 5` - Same as clause 7.11 (0b): text of the landscape Table A8.1 that no stored clause holds in readable form.
- who-trs1010-a8-hvac-nonsterile.pdf page 16 (uncovered): `+> 95 50 m 5` - Same as clause 7.11 (0b): text of the landscape Table A8.1 that no stored clause holds in readable form.
- who-trs1010-a8-hvac-nonsterile.pdf page 16 (uncovered): `+> 95 45 > 95 40` - Same as clause 7.11 (0b): text of the landscape Table A8.1 that no stored clause holds in readable form.
- who-trs1010-a8-hvac-nonsterile.pdf page 16 (uncovered): `+> 90 35 eu` - Same as clause 7.11 (0b): text of the landscape Table A8.1 that no stored clause holds in readable form.
- who-trs1010-a8-hvac-nonsterile.pdf page 16 (uncovered): `+> 90 30 g` - Same as clause 7.11 (0b): text of the landscape Table A8.1 that no stored clause holds in readable form.
- who-trs1010-a8-hvac-nonsterile.pdf page 16 (uncovered): `+90 25 eu 3` - Same as clause 7.11 (0b): text of the landscape Table A8.1 that no stored clause holds in readable form.
- who-trs1010-a8-hvac-nonsterile.pdf page 16 (uncovered): `+85 20 g 3 80 < 20` - Same as clause 7.11 (0b): text of the landscape Table A8.1 that no stored clause holds in readable form.
- who-trs1010-a8-hvac-nonsterile.pdf page 17 (uncovered): `+annex table a 8.1 continued` - Same as clause 7.11 (0b): text of the landscape Table A8.1 that no stored clause holds in readable form.
- who-trs1010-a8-hvac-nonsterile.pdf page 17 (uncovered): `+36492 osi superseded` - Same as clause 7.11 (0b): text of the landscape Table A8.1 that no stored clause holds in readable form.
- who-trs1010-a8-hvac-nonsterile.pdf page 17 (uncovered): `+in table row: en rating` - NOT EXPLAINED
- who-trs1010-a8-hvac-nonsterile.pdf page 17 (uncovered): `+2102 977 ne eu 2` - Same as clause 7.11 (0b): text of the landscape Table A8.1 that no stored clause holds in readable form.
- who-trs1010-a8-hvac-nonsterile.pdf page 17 (uncovered): `+ensure that the classification is current mpps most penetrating particle size note the filter classifications referred to above relate to the` - Same as clause 7.11 (0b): text of the landscape Table A8.1 that no stored clause holds in readable form.
- who-trs1010-a8-hvac-nonsterile.pdf page 17 (uncovered): `+in table row: 2009 and` - NOT EXPLAINED
- who-trs1010-a8-hvac-nonsterile.pdf page 17 (uncovered): `+in table row: test standards` - NOT EXPLAINED
- who-trs1010-a8-hvac-nonsterile.pdf page 17 (uncovered): `+relates to filter classes` - Same as clause 7.11 (0b): text of the landscape Table A8.1 that no stored clause holds in readable form.
- who-trs1010-a8-hvac-nonsterile.pdf page 17 (uncovered): `+1822 relates to filter classes e 10 to u 17` - Same as clause 7.11 (0b): text of the landscape Table A8.1 that no stored clause holds in readable form.
- who-trs1019-a2-hvac-nonsterile-part2.pdf 4.2 (clause): `+w h o t e c h r e p o r t s e s n o 1 0 1 9 2 0 fig a 2.1 | +fig a 2.2 | +fig a 2.5 | +fig a 2.6 | +w h o t e c h r e p o r t s e s n o 1 0 1 9 2 0 fig a 2.7` - NOT EXPLAINED
- who-trs1019-a2-hvac-nonsterile-part2.pdf 7 (clause): `+fig a 2.9 | +w h o t e c h r e p o r t s e s n o 1 0 1 9 2 0 fig a 2.10` - NOT EXPLAINED
- who-trs1019-a2-hvac-nonsterile-part2.pdf 7.1 (clause): `+fig a 2.11 | +w h o t e c h r e p o r t s e s n o 1 0 1 9 2 0 fig a 2.13` - NOT EXPLAINED
- who-trs1019-a2-hvac-nonsterile-part2.pdf 12 (clause): `+who technical report series no 961 6 relative humidity iso 14644 3 and who technical report series no 961 6 | -who technical | -report series | -no 961 6 | -relative humidity iso 14644 3 and | -who technical | -report series | -no 961 6 | +company procedure smoke test airflow velocity iso 14644 3 r` - NOT EXPLAINED
- who-trs1019-a3-validation.pdf Appendix 4 9.2 (clause): `+procedure | +procedure` - NOT EXPLAINED
- who-trs1019-a3-validation.pdf page 3 (uncovered): `+next to 1.1: introduction 1` - NOT EXPLAINED
- who-trs1019-a3-validation.pdf page 3 (uncovered): `+next to 1.4: 2 scope` - NOT EXPLAINED
- who-trs1019-a3-validation.pdf page 3 (uncovered): `+next to 2.1: scope 2` - NOT EXPLAINED
- who-trs1019-a3-validation.pdf page 20 (uncovered): `+next to Appendix 3 1.1: principle 1` - NOT EXPLAINED
- who-trs1019-a3-validation.pdf page 20 (uncovered): `+next to Appendix 3 1.6: 2 scope` - NOT EXPLAINED
- who-trs1019-a3-validation.pdf page 20 (uncovered): `+next to Appendix 3 2.1: scope 2` - NOT EXPLAINED
- who-trs1019-a3-validation.pdf page 31 (uncovered): `+next to Appendix 4 1.1: principle 1` - NOT EXPLAINED
- who-trs1019-a3-validation.pdf page 31 (uncovered): `+next to Appendix 4 1.5: 2 general` - NOT EXPLAINED
- who-trs1019-a3-validation.pdf page 31 (uncovered): `+next to Appendix 4 2.1: general 2` - NOT EXPLAINED
- who-trs1019-a3-validation.pdf page 65 (uncovered): `+next to Appendix 6 1.1: principle 1` - NOT EXPLAINED
- who-trs1019-a3-validation.pdf page 65 (uncovered): `+next to Appendix 6 1.4: 2 scope` - NOT EXPLAINED
- who-trs1019-a3-validation.pdf page 65 (uncovered): `+next to Appendix 6 2.1: scope 2` - NOT EXPLAINED
- who-trs1019-a3-validation.pdf page 42 (uncovered): `+in two clauses Appendix 5 and Appendix 5 1: 1 introduction and scope` - NOT EXPLAINED
- who-trs1025-a3-wfi-non-distillation.pdf 3.2 (clause): `-who technical report series no 1025 2020` - NOT EXPLAINED
- who-trs1025-a3-wfi-non-distillation.pdf 7.2 (clause): `-who technical report series no 1025 2020` - NOT EXPLAINED
- who-trs1025-a3-wfi-non-distillation.pdf page 2 (uncovered): `+next to 1.1: introduction 1` - NOT EXPLAINED
- who-trs1025-a3-wfi-non-distillation.pdf page 2 (uncovered): `+next to 1.2: 2 scope` - NOT EXPLAINED
- who-trs1025-a3-wfi-non-distillation.pdf page 2 (uncovered): `+next to 2.1: scope 2` - NOT EXPLAINED
- who-trs1025-a3-wfi-non-distillation.pdf page 2 (uncovered): `+next to 2.2: 3 monographs` - NOT EXPLAINED
- who-trs1025-a3-wfi-non-distillation.pdf page 2 (uncovered): `+next to 3.1: monographs 3` - NOT EXPLAINED
- who-trs1025-a7-storage-distribution.pdf Appendix 1 (section): `+label description recommended limits` - Order or place only (verified mechanically): every stored word run of this discrepancy is printed on the clause's pages, and every page run it lacks is stored word for word (in this clause or another), so no word is lost or added; the engines read table cells, columns or figure labels in different orders.
- who-trs1025-a7-storage-distribution.pdf page 2 (uncovered): `+next to 1.1: introduction 1` - NOT EXPLAINED
- who-trs1033-a2-hbel-cleaning.pdf Appendix 1 (section): `+pde | +msc a g | -msc a g | -1202 3301 on who technical report serie | +api pde ug day mdd mg day batch size kg shared equipment surface m 2 1 2 3 4 5 | +mssr | -mssr` - NOT EXPLAINED
- who-trs1033-a2-hbel-cleaning.pdf Table 2 Pre- Ce- ding Product a (table_row): `-5 6` - NOT EXPLAINED
- who-trs1033-a4-data-integrity.pdf page 2 (uncovered): `+next to 1.3: 2 scope` - NOT EXPLAINED
- who-trs1033-a4-data-integrity.pdf page 2 (uncovered): `+next to 2.1: scope 2` - NOT EXPLAINED
- who-trs1044-a2-sterile.pdf _unnumbered:1 (unnumbered): `-2011.1 | +2011 1 | -contents background 87 abbreviations 89` - Front matter (cover page, document history, contents): the two engines read the cover's text boxes, address blocks and history table in different orders; not regulation text.
- who-trs1044-a2-sterile.pdf 4.27 (clause): `+grade maximum limits for total particle ≥ 0.5 μm m 3 maximum limits for total particle ≥ 5 μm m 3 at rest in operation at rest in operation a 3 520 3 520 not specifieda not specifieda b 3 520 352 000 not specifieda 2 930 c 352 000 3 520 000 2 930 29 300 d 3 520 000 not predetermined b 29 300 not pr` - Parser defect (0b): the cleanroom grade tables (particle limits, microbial limits) are stored as one merged row whose cells lost the grade letters A-D and footnote letters ('Not specified a'); the values are all stored but cannot be tied to their grade. Store one row per grade.
- who-trs1044-a2-sterile.pdf 4.31 (clause): `+grade air sample cfu m 3 settle plates diameter 90 mm cfu 4 hoursa contact plates diameter 55 mm cfu plate` - Order or place only (verified mechanically): every stored word run of this discrepancy is printed on the clause's pages, and every page run it lacks is stored word for word (in this clause or another), so no word is lost or added; the engines read table cells, columns or figure labels in different orders.
- who-trs1044-a2-sterile.pdf 8.6 (clause): `+operation grade` - NOT EXPLAINED
- who-trs1044-a2-sterile.pdf 8.10 (clause): `-2 02 4 who technical report series no 104 | +grade operation | +grade operation` - NOT EXPLAINED
- who-trs1044-a2-sterile.pdf 9.15 (clause): `+grade maximum limits for total particle ≥ 0.5 μm m 3 maximum limits for total particle ≥ 5 μm m 3 at rest in operation at rest in operation a 3 520 3 520 29 29 b 3 520 352 000 29 2 930 c 352 000 3 520 000 2 930 29 300 d 3 520 000 not predetermineda 29 300 not predetermineda` - Parser defect (0b): the cleanroom grade tables (particle limits, microbial limits) are stored as one merged row whose cells lost the grade letters A-D and footnote letters ('Not specified a'); the values are all stored but cannot be tied to their grade. Store one row per grade.
- who-trs1044-a2-sterile.pdf 9.30 (clause): `+grade air sample cfu m 3 settle plates diam 90 mm cfu 4 hoursa contact plates diam 55 mm cfu plate b glove print incl 5 fingers on both hands cfu glove` - Order or place only (verified mechanically): every stored word run of this discrepancy is printed on the clause's pages, and every page run it lacks is stored word for word (in this clause or another), so no word is lost or added; the engines read table cells, columns or figure labels in different orders.
- who-trs1044-a2-sterile.pdf Table 1 Grade (table_row): `-predetermined specified specified` - Parser defect (0b): the cleanroom grade tables (particle limits, microbial limits) are stored as one merged row whose cells lost the grade letters A-D and footnote letters ('Not specified a'); the values are all stored but cannot be tied to their grade. Store one row per grade.
- who-trs1044-a2-sterile.pdf Table 2 Grade (table_row): `-hours a` - Parser defect (0b): the cleanroom grade tables (particle limits, microbial limits) are stored as one merged row whose cells lost the grade letters A-D and footnote letters ('Not specified a'); the values are all stored but cannot be tied to their grade. Store one row per grade.
- who-trs1044-a2-sterile.pdf Table 7 Grade (table_row): `-hours a` - Parser defect (0b): the cleanroom grade tables (particle limits, microbial limits) are stored as one merged row whose cells lost the grade letters A-D and footnote letters ('Not specified a'); the values are all stored but cannot be tied to their grade. Store one row per grade.
- who-trs1044-a4-tech-transfer.pdf Appendix 1 (section): `+aspect related documentation | +pharmaceutical ingredients apis and excipients | -pharmaceutical ingredients | -apis and excipients` - NOT EXPLAINED
- who-trs1044-a4-tech-transfer.pdf _unnumbered:4 (unnumbered): `+aspect related documentation` - Order or place only (verified mechanically): every stored word run of this discrepancy is printed on the clause's pages, and every page run it lacks is stored word for word (in this clause or another), so no word is lost or added; the engines read table cells, columns or figure labels in different orders.
- who-trs1052-a4-qc-labs.pdf Appendix 1 (section): `-who technical report series no 1052 2024 | +o t e c h r e p o r t s e s n o 1 0 5 2 2 0 2 4 first stage laboratory continued optional items quantity | +o t e c h r e p o r t s e s n o 1 0 5 2 2 0 2 4 medium sized laboratory continued equipment and major instruments quantity | +1 | +2 | +equipment f` - NOT EXPLAINED
- who-trs1052-a4-qc-labs.pdf Appendix 2 (section): `-tg | +o t e c h r e p o r t s e s n o 1 0 5 2 2 0 2 4 | -uitg | +tg` - NOT EXPLAINED
- who-trs1052-a4-qc-labs.pdf Appendix 3 1 #2 (clause): `-tg | -umeas | +u tg meas | +u | -umeas | +meas` - NOT EXPLAINED
- who-trs1052-a4-qc-labs.pdf Appendix 3 1 #3 (clause): `+substance being tested | -substance being tested` - NOT EXPLAINED
- who-trs1052-a4-qc-labs.pdf Appendix 3 5 #2 (clause): `+reference substance | -reference substance` - NOT EXPLAINED
- who-trs1052-a4-qc-labs.pdf Appendix 3 8 (clause): `-4202 2501 on who technical report series | +test solution` - NOT EXPLAINED
- who-trs1060-a2-nitrosamines.pdf _unnumbered:2 (unnumbered): `+7` - A footnote reference number (verified: it starts a line or is printed small on the clause's pages) that the parser drops with the footnote mark; no regulation word changes.
- who-trs1060-a3-excipients.pdf Appendix 1 7.2 #2 (clause): `-annex x 3 table continued wh o expert committee on specifications for pharmaceutical preparations fifty eighth report table continued` - NOT EXPLAINED
- who-trs1060-a3-excipients.pdf Appendix 1 7.3 #2 (clause): `+equipment risk | +construction | -construction` - NOT EXPLAINED
- who-trs1060-a3-excipients.pdf Appendix 1 7.4 #2 (clause): `+materials risk` - NOT EXPLAINED
- who-trs1060-a3-excipients.pdf Appendix 1 7.5 #2 (clause): `+utilities risk | +environmental air | -environmental air` - NOT EXPLAINED
- who-trs1060-a3-excipients.pdf Appendix 1 7.6 (clause): `+personnel risk` - NOT EXPLAINED
- who-trs1060-a3-excipients.pdf Appendix 1 7.7 (clause): `+risk production` - NOT EXPLAINED
- who-trs1060-a3-excipients.pdf Appendix 1 7.8 (clause): `+repackaging risk` - NOT EXPLAINED
- who-trs1060-a3-excipients.pdf Appendix 1 7.9 (clause): `+storage risk` - NOT EXPLAINED
- who-trs1060-a3-excipients.pdf Appendix 1 7.10 (clause): `+risk distribution` - NOT EXPLAINED
- who-trs1060-a3-excipients.pdf Table 1 Premises (table_row): `-location flow personnel flow access services` - NOT EXPLAINED
- who-trs1060-a3-excipients.pdf page 35 (uncovered): `+material flow personnel flow location access services` - NOT EXPLAINED
- who-trs1060-a3-excipients.pdf page 36 (uncovered): `+who technical report series no 1060 2025` - NOT EXPLAINED
- who-trs1060-a3-excipients.pdf page 2 (uncovered): `+in two clauses 1 and Appendix 1 1: 1 introduction and scope` - NOT EXPLAINED
- who-trs902-a9-packaging.pdf _unnumbered:1 (unnumbered): `-who technical report series no 902 2002` - Order or place only (verified mechanically): every stored word run of this discrepancy is printed on the clause's pages, and every page run it lacks is stored word for word (in this clause or another), so no word is lost or added; the engines read table cells, columns or figure labels in different orders.
- who-trs902-a9-packaging.pdf Annex 9 Appendix 4 1.1 (clause): `-table 1 types of raw materials used in packaging types of materials uses cardboard boxes display units paper labels leaflets glass ampoules bottles vials syringes cartridges plastic closures bottles bags tubes laminates with paper or foil metal e g aluminium collapsible tubes rigid cans foils needl` - NOT EXPLAINED
- who-trs902-a9-packaging.pdf Annex 9 Appendix 4 4.1 (clause): `-table 2 methods of disposal of uncontaminated packaging material recycling landfill incineration paper cardboard plastics glass na rubber metal na highly recommended recommended acceptable na not applicable` - Order or place only (verified mechanically): every stored word run of this discrepancy is printed on the clause's pages, and every page run it lacks is stored word for word (in this clause or another), so no word is lost or added; the engines read table cells, columns or figure labels in different orders.
- who-trs929-a4-sampling.pdf _unnumbered:1 (unnumbered): `+annex 4 | -technical report series no 929 2005` - Front matter (cover page, document history, contents): the two engines read the cover's text boxes, address blocks and history table in different orders; not regulation text.
- who-trs929-a4-sampling.pdf Annex 4 1.1 (clause): `-1.1` - Parser defect (0b): the contents list of Annex 4 is stored as clauses ('1.2 Glossary 61'); contents entries, not requirements.
- who-trs929-a4-sampling.pdf Annex 4 1.2 (clause): `-1.2` - Parser defect (0b): the contents list of Annex 4 is stored as clauses ('1.2 Glossary 61'); contents entries, not requirements.
- who-trs929-a4-sampling.pdf Annex 4 1.3 (clause): `-1.3` - Parser defect (0b): the contents list of Annex 4 is stored as clauses ('1.2 Glossary 61'); contents entries, not requirements.
- who-trs929-a4-sampling.pdf Annex 4 1.4 (clause): `-1.4` - Parser defect (0b): the contents list of Annex 4 is stored as clauses ('1.2 Glossary 61'); contents entries, not requirements.
- who-trs929-a4-sampling.pdf Annex 4 1.5 (clause): `-1.5` - Parser defect (0b): the contents list of Annex 4 is stored as clauses ('1.2 Glossary 61'); contents entries, not requirements.
- who-trs929-a4-sampling.pdf Annex 4 1.6 (clause): `-1.6` - Parser defect (0b): the contents list of Annex 4 is stored as clauses ('1.2 Glossary 61'); contents entries, not requirements.
- who-trs929-a4-sampling.pdf Annex 4 1.7 (clause): `-1.7` - Parser defect (0b): the contents list of Annex 4 is stored as clauses ('1.2 Glossary 61'); contents entries, not requirements.
- who-trs929-a4-sampling.pdf Annex 4 2.1 (clause): `-2.1` - Parser defect (0b): the contents list of Annex 4 is stored as clauses ('1.2 Glossary 61'); contents entries, not requirements.
- who-trs929-a4-sampling.pdf Annex 4 2.2 (clause): `-2.2` - Parser defect (0b): the contents list of Annex 4 is stored as clauses ('1.2 Glossary 61'); contents entries, not requirements.
- who-trs929-a4-sampling.pdf Annex 4 2.3 (clause): `-2.3` - Parser defect (0b): the contents list of Annex 4 is stored as clauses ('1.2 Glossary 61'); contents entries, not requirements.
- who-trs929-a4-sampling.pdf Annex 4 3.1 (clause): `-3.1` - Parser defect (0b): the contents list of Annex 4 is stored as clauses ('1.2 Glossary 61'); contents entries, not requirements.
- who-trs929-a4-sampling.pdf Annex 4 3.2 (clause): `-3.2` - Parser defect (0b): the contents list of Annex 4 is stored as clauses ('1.2 Glossary 61'); contents entries, not requirements.
- who-trs929-a4-sampling.pdf Annex 4 4.1 (clause): `-4.1` - Parser defect (0b): the contents list of Annex 4 is stored as clauses ('1.2 Glossary 61'); contents entries, not requirements.
- who-trs929-a4-sampling.pdf Annex 4 4.2 (clause): `-4.2` - Parser defect (0b): the contents list of Annex 4 is stored as clauses ('1.2 Glossary 61'); contents entries, not requirements.
- who-trs929-a4-sampling.pdf Annex 4 4.3 (clause): `-4.3` - Parser defect (0b): the contents list of Annex 4 is stored as clauses ('1.2 Glossary 61'); contents entries, not requirements.
- who-trs929-a4-sampling.pdf Annex 4 4.4 (clause): `-4.4` - Parser defect (0b): the contents list of Annex 4 is stored as clauses ('1.2 Glossary 61'); contents entries, not requirements.
- who-trs929-a4-sampling.pdf Annex 4 5.1 (clause): `-5.1` - Parser defect (0b): the contents list of Annex 4 is stored as clauses ('1.2 Glossary 61'); contents entries, not requirements.
- who-trs929-a4-sampling.pdf Annex 4 5.2 (clause): `-5.2` - Parser defect (0b): the contents list of Annex 4 is stored as clauses ('1.2 Glossary 61'); contents entries, not requirements.
- who-trs929-a4-sampling.pdf Annex 4 5.3 (clause): `-5.3` - Parser defect (0b): the contents list of Annex 4 is stored as clauses ('1.2 Glossary 61'); contents entries, not requirements.
- who-trs929-a4-sampling.pdf Annex 4 Appendix 5 5 (clause): `-table 1 values of n p or r for the n sampling unitsa value of n p or r values of n n plan p plan r plan 2 up to 3 up to 25 up to 2 3 4 6 26 56 3 4 4 7 13 57 100 5 7 5 14 20 101 156 8 11 6 21 30 157 225 12 16 7 31 42 17 22 8 43 56 23 28 9 57 72 29 36 10 73 90 37 44 a an example of how these plans wo` - NOT EXPLAINED
- who-trs929-a4-sampling.pdf Annex 4 Appendix 5 5.1.1 (clause): `+table 1 values of n p or r for the n sampling units a value of n p or r values of n n plan p plan r plan 2 up to 3 up to 25 up to 2 3 4 6 26 56 3 4 4 7 13 57 100 5 7 5 14 20 101 156 8 11 6 21 30 157 225 12 16 7 31 42 17 22 8 43 56 23 28 9 57 72 29 36 10 73 90 37 44 a an example of how these plans w` - Order or place only (verified mechanically): every stored word run of this discrepancy is printed on the clause's pages, and every page run it lacks is stored word for word (in this clause or another), so no word is lost or added; the engines read table cells, columns or figure labels in different orders.
- who-trs929-a4-sampling.pdf Annex 4 Appendix 1 (section): `-figure 4 typical sample thieves | +figure 4 typical sample thieves` - NOT EXPLAINED
- who-trs929-a4-sampling.pdf page 1 (uncovered): `+in two clauses Annex 4 and _unnumbered:1: annex 4 who` - NOT EXPLAINED
- who-trs943-a3-reference-substances.pdf page 21 (uncovered): `+next to Annex 3 B 4.3: predefi ned` - NOT EXPLAINED
- who-trs943-a3-reference-substances.pdf page 21 (uncovered): `+next to Annex 3 B 4.4: ned predefi` - NOT EXPLAINED
- who-trs953-a2-app1-stability-conditions.pdf _unnumbered:1 (unnumbered): `-stability testing of active pharmaceutical ingredients and finished pharmaceutical products stability conditions for who member states by region 1 update march 2021 previously included as table 2 in stability testing of active pharmaceutical ingredients and finished pharmaceutical products annex 2 ` - Front matter (cover page, document history, contents): the two engines read the cover's text boxes, address blocks and history table in different orders; not regulation text.
- who-trs957-a2-api.pdf _unnumbered:1 (unnumbered): `-who technical report series no 957 2010` - Order or place only (verified mechanically): every stored word run of this discrepancy is printed on the clause's pages, and every page run it lacks is stored word for word (in this clause or another), so no word is lost or added; the engines read table cells, columns or figure labels in different orders.
- who-trs957-a2-api.pdf Annex 2 Appendix 2 1.3 (clause): `-a this table has been taken from the ich harmonised tripartite guideline active pharmaceutical ingredients q 7 current step 4 version dated 10 november 2000 increasing gmp requirements` - Order or place only (verified mechanically): every stored word run of this discrepancy is printed on the clause's pages, and every page run it lacks is stored word for word (in this clause or another), so no word is lost or added; the engines read table cells, columns or figure labels in different orders.
- who-trs957-a2-api.pdf page 1 (uncovered): `+next to Annex 2 3.1: qualifi cations` - NOT EXPLAINED
- who-trs957-a2-api.pdf page 1 (uncovered): `+next to Annex 2 3.2: cations qualifi` - NOT EXPLAINED
- who-trs957-a2-api.pdf page 1 (uncovered): `+next to Annex 2 6.1: specifi cations` - NOT EXPLAINED
- who-trs957-a2-api.pdf page 1 (uncovered): `+next to Annex 2 6.2: cations specifi` - NOT EXPLAINED
- who-trs957-a2-api.pdf page 2 (uncovered): `+next to Annex 2 12.3: qualifi cation` - NOT EXPLAINED
- who-trs957-a2-api.pdf page 2 (uncovered): `+next to Annex 2 12.4: cation qualifi` - NOT EXPLAINED
- who-trs957-a2-api.pdf page 3 (uncovered): `+next to Annex 2 18.4: purifi cation` - NOT EXPLAINED
- who-trs957-a2-api.pdf page 3 (uncovered): `+next to Annex 2 18.5: cation purifi` - NOT EXPLAINED
- who-trs957-a2-api.pdf page 7 (uncovered): `+next to Annex 2 Appendix 2 2.14: specifi ed` - NOT EXPLAINED
- who-trs957-a2-api.pdf page 7 (uncovered): `+next to Annex 2 Appendix 2 2.15: ed specifi` - NOT EXPLAINED
- who-trs957-a2-api.pdf page 9 (uncovered): `+next to Annex 2 Appendix 2 2.3: qualifi ed` - NOT EXPLAINED
- who-trs957-a2-api.pdf page 9 (uncovered): `+next to Annex 2 Appendix 2 2.4: ed qualifi` - NOT EXPLAINED
- who-trs957-a2-api.pdf page 10 (uncovered): `+next to Annex 2 Appendix 2 3.1: qualifi cations` - NOT EXPLAINED
- who-trs957-a2-api.pdf page 10 (uncovered): `+next to Annex 2 Appendix 2 3.10: cations qualifi` - NOT EXPLAINED
- who-trs957-a2-api.pdf page 13 (uncovered): `+next to Annex 2 Appendix 2 4.60: identifi ed` - NOT EXPLAINED
- who-trs957-a2-api.pdf page 13 (uncovered): `+next to Annex 2 Appendix 2 4.7: ed identifi` - NOT EXPLAINED
- who-trs957-a2-api.pdf page 14 (uncovered): `+next to Annex 2 Appendix 2 5.11: specifi cations` - NOT EXPLAINED
- who-trs957-a2-api.pdf page 14 (uncovered): `+next to Annex 2 Appendix 2 5.12: cations specifi` - NOT EXPLAINED
- who-trs957-a2-api.pdf page 14 (uncovered): `+next to Annex 2 Appendix 2 5.13: identifi ed` - NOT EXPLAINED
- who-trs957-a2-api.pdf page 14 (uncovered): `+next to Annex 2 Appendix 2 5.14: ed identifi` - NOT EXPLAINED
- who-trs957-a2-api.pdf page 15 (uncovered): `+next to Annex 2 Appendix 2 5.22: specifi cations` - NOT EXPLAINED
- who-trs957-a2-api.pdf page 15 (uncovered): `+next to Annex 2 Appendix 2 5.23: cations specifi` - NOT EXPLAINED
- who-trs957-a2-api.pdf page 15 (uncovered): `+next to Annex 2 Appendix 2 5.25: justifi ed` - NOT EXPLAINED
- who-trs957-a2-api.pdf page 15 (uncovered): `+next to Annex 2 Appendix 2 5.26: ed justifi` - NOT EXPLAINED
- who-trs957-a2-api.pdf page 15 (uncovered): `+next to Annex 2 Appendix 2 5.33: verifi able` - NOT EXPLAINED
- who-trs957-a2-api.pdf page 15 (uncovered): `+next to Annex 2 Appendix 2 5.34: able verifi` - NOT EXPLAINED
- who-trs957-a2-api.pdf page 17 (uncovered): `+next to Annex 2 Appendix 2 6.1: specifi cations` - NOT EXPLAINED
- who-trs957-a2-api.pdf page 17 (uncovered): `+next to Annex 2 Appendix 2 6.10: cations specifi` - NOT EXPLAINED
- who-trs957-a2-api.pdf page 17 (uncovered): `+next to Annex 2 Appendix 2 6.12: specifi ed` - NOT EXPLAINED
- who-trs957-a2-api.pdf page 17 (uncovered): `+next to Annex 2 Appendix 2 6.13: ed specifi` - NOT EXPLAINED
- who-trs957-a2-api.pdf page 22 (uncovered): `+next to Annex 2 Appendix 2 7.23: identifi ed` - NOT EXPLAINED
- who-trs957-a2-api.pdf page 22 (uncovered): `+next to Annex 2 Appendix 2 7.24: ed identifi` - NOT EXPLAINED
- who-trs957-a2-api.pdf page 23 (uncovered): `+next to Annex 2 Appendix 2 7.42: fi rst` - NOT EXPLAINED
- who-trs957-a2-api.pdf page 23 (uncovered): `+next to Annex 2 Appendix 2 7.43: rst fi` - NOT EXPLAINED
- who-trs957-a2-api.pdf page 27 (uncovered): `+next to Annex 2 Appendix 2 8.52: purifi cation` - NOT EXPLAINED
- who-trs957-a2-api.pdf page 27 (uncovered): `+next to Annex 2 Appendix 2 9: cation purifi` - NOT EXPLAINED
- who-trs957-a2-api.pdf page 28 (uncovered): `+next to Annex 2 Appendix 2 9.32: identifi cation` - NOT EXPLAINED
- who-trs957-a2-api.pdf page 28 (uncovered): `+next to Annex 2 Appendix 2 9.33: cation identifi` - NOT EXPLAINED
- who-trs957-a2-api.pdf page 31 (uncovered): `+next to Annex 2 Appendix 2 11.20: specifi cations` - NOT EXPLAINED
- who-trs957-a2-api.pdf page 31 (uncovered): `+next to Annex 2 Appendix 2 11.21: cations specifi` - NOT EXPLAINED
- who-trs957-a2-api.pdf page 31 (uncovered): `+next to Annex 2 Appendix 2 11.23: specifi ed` - NOT EXPLAINED
- who-trs957-a2-api.pdf page 35 (uncovered): `+next to Annex 2 Appendix 2 12.22: defi ciencies` - NOT EXPLAINED
- who-trs957-a2-api.pdf page 35 (uncovered): `+next to Annex 2 Appendix 2 12.23: ciencies defi` - NOT EXPLAINED
- who-trs957-a2-api.pdf page 35 (uncovered): `+next to Annex 2 Appendix 2 12.23: justifi cation` - NOT EXPLAINED
- who-trs957-a2-api.pdf page 35 (uncovered): `+next to Annex 2 Appendix 2 12.3: cation justifi` - NOT EXPLAINED
- who-trs957-a2-api.pdf page 35 (uncovered): `+next to Annex 2 Appendix 2 12.3: qualifi cation` - NOT EXPLAINED
- who-trs957-a2-api.pdf page 35 (uncovered): `+next to Annex 2 Appendix 2 12.30: cation qualifi` - NOT EXPLAINED
- who-trs957-a2-api.pdf page 35 (uncovered): `+next to Annex 2 Appendix 2 12.30: specifi cations` - NOT EXPLAINED
- who-trs957-a2-api.pdf page 35 (uncovered): `+next to Annex 2 Appendix 2 12.4: cations specifi` - NOT EXPLAINED
- who-trs957-a2-api.pdf page 36 (uncovered): `+next to Annex 2 Appendix 2 12.50: justifi ed` - NOT EXPLAINED
- who-trs957-a2-api.pdf page 36 (uncovered): `+next to Annex 2 Appendix 2 12.51: ed justifi` - NOT EXPLAINED
- who-trs957-a2-api.pdf page 37 (uncovered): `+next to Annex 2 Appendix 2 12.73: microfl uidizers` - NOT EXPLAINED
- who-trs957-a2-api.pdf page 37 (uncovered): `+next to Annex 2 Appendix 2 12.74: uidizers microfl` - NOT EXPLAINED
- who-trs957-a2-api.pdf page 48 (uncovered): `+next to Annex 2 Appendix 2 18.4: purifi cation` - NOT EXPLAINED
- who-trs957-a2-api.pdf page 48 (uncovered): `+next to Annex 2 Appendix 2 18.40: cation purifi` - NOT EXPLAINED
- who-trs957-a2-api.pdf page 50 (uncovered): `+next to Annex 2 Appendix 2 19.40: suffi ce` - NOT EXPLAINED
- who-trs957-a2-api.pdf page 50 (uncovered): `+next to Annex 2 Appendix 2 19.41: ce suffi` - NOT EXPLAINED
- who-trs957-a3-hazardous.pdf _unnumbered:1 (unnumbered): `+annex 3 | -technical report series no 957 2010` - Front matter (cover page, document history, contents): the two engines read the cover's text boxes, address blocks and history table in different orders; not regulation text.
- who-trs957-a3-hazardous.pdf Annex 3 9.3 (clause): `-figure 1 typical airflow pattern for contaminant p p p p` - NOT EXPLAINED
- who-trs957-a3-hazardous.pdf Annex 3 11.1 (clause): `-e shut off vfd damper exhaust | +m 11.2 the fi nal fi lters on the safe change unit should be hepa fi lters with at least an h 13 classifi cation according to en 1822 fi lter standards for dusty return | -fan secondary m m m filter vfd velocity sensor v m m m | +pre fi ltration may also be required` - NOT EXPLAINED
- who-trs957-a3-hazardous.pdf Annex 3 11.3 (clause): `-first filter fail` - NOT EXPLAINED
- who-trs957-a3-hazardous.pdf Annex 3 11.6 (clause): `+fi lter condition 11.7` - NOT EXPLAINED
- who-trs957-a3-hazardous.pdf Annex 3 13 (clause): `-effluent treatment` - NOT EXPLAINED
- who-trs957-a3-hazardous.pdf page 2 (uncovered): `+next to Annex 3 1.1: introduction 1` - NOT EXPLAINED
- who-trs957-a3-hazardous.pdf page 2 (uncovered): `+next to Annex 3 1.4: 2 general` - NOT EXPLAINED
- who-trs957-a3-hazardous.pdf page 2 (uncovered): `+next to Annex 3 2.1: general 2` - NOT EXPLAINED
- who-trs957-a3-hazardous.pdf page 12 (uncovered): `+next to Annex 3 9.5: airfl ow` - NOT EXPLAINED
- who-trs957-a3-hazardous.pdf page 12 (uncovered): `+next to Annex 3 9.6: ow airfl` - NOT EXPLAINED
- who-trs957-a3-hazardous.pdf page 1 (uncovered): `+in two clauses Annex 3 and _unnumbered:1: annex 3 who` - NOT EXPLAINED
- who-trs957-a3-hazardous.pdf page 14 (uncovered): `+in two clauses Annex 3 11.1 and Annex 3 11.2: 11.2 the fi nal fi lters on the safe change unit should be hepa fi lters with at least an h 13 classifi cation according to en 1822 fi lter standards for dusty return air pre fi ltration may also be required to prolong the life of the hepa fi lters the ` - NOT EXPLAINED
- who-trs961-a14-site-master-file.pdf Annex 14 2.3 (clause): `+1` - A footnote reference number (verified: it starts a line or is printed small on the clause's pages) that the parser drops with the footnote mark; no regulation word changes.
- who-trs961-a14-site-master-file.pdf page 2 (uncovered): `+next to Annex 14 1.1: introduction 1` - NOT EXPLAINED
- who-trs961-a2-micro-labs.pdf _unnumbered:1 (unnumbered): `+annex 2 | -technical report series no 961 2011` - Front matter (cover page, document history, contents): the two engines read the cover's text boxes, address blocks and history table in different orders; not regulation text.
- who-trs961-a2-micro-labs.pdf Annex 2 Appendix 1 (section): `-appendix 1` - NOT EXPLAINED
- who-trs961-a2-micro-labs.pdf Annex 2 Appendix 2 (section): `-appendix 2` - NOT EXPLAINED
- who-trs961-a2-micro-labs.pdf Annex 2 Appendix 3 (section): `-appendix 3` - NOT EXPLAINED
- who-trs961-a2-micro-labs.pdf Annex 2 Appendix 4 (section): `-appendix 4` - NOT EXPLAINED
- who-trs961-a2-micro-labs.pdf _unnumbered:5 (unnumbered): `-examples of calibration checks and intervals for different laboratory equipment this information is provided as an example and the frequency will be based on the need type previous performance and criticality of the equipment examples of equipment qualification and monitoring this information is pr` - NOT EXPLAINED
- who-trs961-a2-micro-labs.pdf Table 2 Laboratory (table_row): `-other` - NOT EXPLAINED
- who-trs961-a2-micro-labs.pdf page 21 (uncovered): `+in table row: othersurfaces` - NOT EXPLAINED
- who-trs961-a2-micro-labs.pdf page 25 (uncovered): `+general use of reference cultures all parts of the process should be fully documented and detailed records of all stages must be maintained purity checks and biochemical tests should be made as appropriate reference strain from source recognized by accreditation body reference stock g 1 freeze drie` - NOT EXPLAINED
- who-trs961-a2-micro-labs.pdf page 1 (uncovered): `+next to Annex 2 4.2: qualifi cation` - NOT EXPLAINED
- who-trs961-a2-micro-labs.pdf page 1 (uncovered): `+next to Annex 2 4.3: cation qualifi` - NOT EXPLAINED
- who-trs961-a2-micro-labs.pdf page 2 (uncovered): `+next to Annex 2 8: identifi cation` - NOT EXPLAINED
- who-trs961-a2-micro-labs.pdf page 2 (uncovered): `+next to Annex 2 9: cation identifi` - NOT EXPLAINED
- who-trs961-a2-micro-labs.pdf page 7 (uncovered): `+next to Annex 2 Appendix 4 2.1.7: classifi cations` - NOT EXPLAINED
- who-trs961-a2-micro-labs.pdf page 7 (uncovered): `+next to Annex 2 Appendix 4 2.1.8: cations classifi` - NOT EXPLAINED
- who-trs961-a2-micro-labs.pdf page 8 (uncovered): `+next to Annex 2 Appendix 4 2.4.5: fi lters` - NOT EXPLAINED
- who-trs961-a2-micro-labs.pdf page 8 (uncovered): `+next to Annex 2 Appendix 4 2.4.6: lters fi` - NOT EXPLAINED
- who-trs961-a2-micro-labs.pdf page 8 (uncovered): `+next to Annex 2 Appendix 4 2.4.7: specifi cation` - NOT EXPLAINED
- who-trs961-a2-micro-labs.pdf page 8 (uncovered): `+next to Annex 2 Appendix 4 2.4.8: cation specifi` - NOT EXPLAINED
- who-trs961-a2-micro-labs.pdf page 10 (uncovered): `+next to Annex 2 Appendix 4 4.2: qualifi cation` - NOT EXPLAINED
- who-trs961-a2-micro-labs.pdf page 10 (uncovered): `+next to Annex 2 Appendix 4 4.2.1: cation qualifi` - NOT EXPLAINED
- who-trs961-a2-micro-labs.pdf page 11 (uncovered): `+next to Annex 2 Appendix 4 4.3.5.1: verifi ed` - NOT EXPLAINED
- who-trs961-a2-micro-labs.pdf page 11 (uncovered): `+next to Annex 2 Appendix 4 4.3.5.2: ed verifi` - NOT EXPLAINED
- who-trs961-a2-micro-labs.pdf page 14 (uncovered): `+next to Annex 2 Appendix 4 5.2.8: verifi ed` - NOT EXPLAINED
- who-trs961-a2-micro-labs.pdf page 14 (uncovered): `+next to Annex 2 Appendix 4 5.2.9: ed verifi` - NOT EXPLAINED
- who-trs961-a2-micro-labs.pdf page 14 (uncovered): `+next to Annex 2 Appendix 4 5.2.9: specifi cation` - NOT EXPLAINED
- who-trs961-a2-micro-labs.pdf page 14 (uncovered): `+next to Annex 2 Appendix 4 5.2.10: cation specifi` - NOT EXPLAINED
- who-trs961-a2-micro-labs.pdf page 16 (uncovered): `+next to Annex 2 Appendix 4 8: identifi cation` - NOT EXPLAINED
- who-trs961-a2-micro-labs.pdf page 16 (uncovered): `+next to Annex 2 Appendix 4 8.1: cation identifi` - NOT EXPLAINED
- who-trs961-a2-micro-labs.pdf page 1 (uncovered): `+in two clauses Annex 2 and _unnumbered:1: annex 2 who` - NOT EXPLAINED
- who-trs961-a9-storage-transport-ttsp.pdf Annex 9 3.9.1 (clause): `+22` - A footnote reference number (verified: it starts a line or is printed small on the clause's pages) that the parser drops with the footnote mark; no regulation word changes.
- who-trs961-a9-storage-transport-ttsp.pdf Annex 9 6.5.1 (clause): `+14` - A footnote reference number (verified: it starts a line or is printed small on the clause's pages) that the parser drops with the footnote mark; no regulation word changes.
- who-trs961-a9-storage-transport-ttsp.pdf Annex 9 6.5.2 (clause): `+28` - A footnote reference number (verified: it starts a line or is printed small on the clause's pages) that the parser drops with the footnote mark; no regulation word changes.
- who-trs961-a9-storage-transport-ttsp.pdf _unnumbered:2 (unnumbered): `+monitoring | +monitoring | +administration | +chengdu institute | +department | -department | +pereira | -pereira | +monitoring | -dcvmn india | +dcvmn india | -regulatory indonesia | +regulatory indonesia | +vladakhani | +pharmaceutical narcotics | -vladakhani pharmaceutical | -narcotics | -who sw` - NOT EXPLAINED
- who-trs961-a9-storage-transport-ttsp.pdf page 29 (uncovered): `+next to Annex 9 6.7.1: justifi ed` - NOT EXPLAINED
- who-trs961-a9-storage-transport-ttsp.pdf page 29 (uncovered): `+next to Annex 9 6.7.2: ed justifi` - NOT EXPLAINED
- who-trs961-a9-storage-transport-ttsp.pdf page 29 (uncovered): `+next to Annex 9 6.7.2: justifi ed` - NOT EXPLAINED
- who-trs961-a9-storage-transport-ttsp.pdf page 29 (uncovered): `+next to Annex 9 6.7.3: ed justifi` - NOT EXPLAINED
- who-trs961-a9-storage-transport-ttsp.pdf page 29 (uncovered): `+next to Annex 9 6.7.3: justifi ed` - NOT EXPLAINED
- who-trs961-a9-storage-transport-ttsp.pdf page 29 (uncovered): `+next to Annex 9 6.7.4: ed justifi` - NOT EXPLAINED
- who-trs961-a9-storage-transport-ttsp.pdf page 49 (uncovered): `+next to _unnumbered:2: who switzerland` - NOT EXPLAINED
- who-trs981-a2-qrm.pdf 6 (clause): `+4 8 12 16 20 | +3 6 9 12 15 | +2 4 6 8 10 | -t 4 ffo fwfsz 1 negligible t p sfhvmbupsz jttvf | -t p fõfdu po boe opu | +1 negligible | -t 4 ffo fwfsz 2 marginal t bz sfrvjsf 3 | +2 marginal | -t % fdjtjpo up sfmfbtf | -t 4 ffo fwfsz 3 moderate t 3 jotqfdujpo | +3 moderate | -efmdjfodz rvjuf | -t jn` - NOT EXPLAINED
- who-trs981-a2-qrm.pdf _unnumbered:2 (unnumbered): `+table 3 continued o t e c h r e p o r t s e s n o 9 8 1 2 0 1 3` - Front matter (cover page, document history, contents): the two engines read the cover's text boxes, address blocks and history table in different orders; not regulation text.
- who-trs981-a2-qrm.pdf Table 3 Hazard operability analysis (HAZOP) (table_row): `-t tool t uses ufdiojrvf up ifmq jefoujgz t gbdjmjujft boe frvjqnfou t` - Parser defect (0b): the QRM tool tables use a font whose text poppler extracts shifted by one letter ('ufdiojrvf' for 'technique'); the stored text of these rows is unreadable, pdfminer reads it correctly. Re-extract these pages.
- who-trs981-a2-qrm.pdf Table 3 Hazard analysis and critical control… (table_row): `-t identify fõfdujwfmz qsfwfou ib bse t bottom up t nqibtj ft tusfohui pg t t valuable t assessment` - Parser defect (0b): the QRM tool tables use a font whose text poppler extracts shifted by one letter ('ufdiojrvf' for 'technique'); the stored text of these rows is unreadable, pdfminer reads it correctly. Re-extract these pages.
- who-trs981-a2-qrm.pdf Table 3 'BJMVSFNPEFTFõFDUT BOBMZTJT '.&" (table_row): `-bjmvsf npeft fõfdut bobmztjt assumes assesses uif qspcbcmf fõfdu wbmvbuf frvjqnfou` - Parser defect (0b): the QRM tool tables use a font whose text poppler extracts shifted by one letter ('ufdiojrvf' for 'technique'); the stored text of these rows is unreadable, pdfminer reads it correctly. Re-extract these pages.
- who-trs981-a2-qrm.pdf Table 4 'BJMVSFNPEFTFõFDUT BOBMZTJT '.&" (table_row): `-bjmvsf npeft fõfdut bobmztjt t highly t` - Parser defect (0b): the QRM tool tables use a font whose text poppler extracts shifted by one letter ('ufdiojrvf' for 'technique'); the stored text of these rows is unreadable, pdfminer reads it correctly. Re-extract these pages.
- who-trs981-a2-qrm.pdf Table 4 Source: Based on reference 9. This… (table_row): `-64 xfc tjuf iuuq xxx qrsj psh joefy btq 123 ibt ljoemz bhsffe up uif vtf pg jut` - Parser defect (0b): the QRM tool tables use a font whose text poppler extracts shifted by one letter ('ufdiojrvf' for 'technique'); the stored text of these rows is unreadable, pdfminer reads it correctly. Re-extract these pages.
- who-trs981-a2-qrm.pdf page 30 (uncovered): `+table 3 continued continues` - NOT EXPLAINED
- who-trs981-a2-qrm.pdf page 2 (uncovered): `+next to 1.1: introduction 1` - NOT EXPLAINED
- who-trs992-a4-hold-time.pdf Glossary (section): `+specification | +viscosity if applicable | -viscosity if applicable | +including granulation pastes coating solution and coating suspension | +gravity viscosity sedimentation ph microbial test | -including granulation gravity viscosity sedimentation | -pastes coating solution ph microbial test and ` - NOT EXPLAINED
- who-trs992-a5-ttsp-supplements.pdf 1.1 (clause): `+1 | -table a 5.1 continued title section s` - NOT EXPLAINED
- who-trs992-a5-ttsp-supplements.pdf 5 (clause): `+table a 5.1 continued` - Order or place only (verified mechanically): every stored word run of this discrepancy is printed on the clause's pages, and every page run it lacks is stored word for word (in this clause or another), so no word is lost or added; the engines read table cells, columns or figure labels in different orders.
- who-trs992-a5-ttsp-supplements.pdf 7 (clause): `+2 | +o t e c h r e p o r t s e s n o 9 9 2 2 0 1 5 supplement 1` - NOT EXPLAINED
- who-trs992-a5-ttsp-supplements.pdf _unnumbered:3 (unnumbered): `+supplement 2` - NOT EXPLAINED
- who-trs992-a5-ttsp-supplements.pdf Annex 2 A 2.3 (clause): `+supplement 3` - NOT EXPLAINED
- who-trs992-a5-ttsp-supplements.pdf _unnumbered:7 (unnumbered): `+o t e c h r e p o r t s e s n o 9 9 2 2 0 1 5 supplement 4` - NOT EXPLAINED
- who-trs992-a5-ttsp-supplements.pdf Annex 3 (section): `-annex 3` - NOT EXPLAINED
- who-trs992-a5-ttsp-supplements.pdf Annex 3 A 3.5 (clause): `+o t e c h r e p o r t s e s n o 9 9 2 2 0 1 5 supplement 5` - NOT EXPLAINED
- who-trs992-a5-ttsp-supplements.pdf Annex 2 (section): `-annex 2 | +supplement 6` - NOT EXPLAINED
- who-trs992-a5-ttsp-supplements.pdf Annex 1 (section): `-annex 1 | +supplement 7` - NOT EXPLAINED
- who-trs992-a5-ttsp-supplements.pdf _unnumbered:16 (unnumbered): `-revision` - NOT EXPLAINED
- who-trs992-a5-ttsp-supplements.pdf Annex 1 #2 (section): `-annex 1 | +supplement 8` - NOT EXPLAINED
- who-trs992-a5-ttsp-supplements.pdf Annex 1 A 1.3 #2 (clause): `+o t e c h r e p o r t s e s n o 9 9 2 2 0 1 5 supplement 9` - NOT EXPLAINED
- who-trs992-a5-ttsp-supplements.pdf Annex 1 #3 (section): `-annex 1 | +supplement 11` - NOT EXPLAINED
- who-trs992-a5-ttsp-supplements.pdf _unnumbered:24 (unnumbered): `+supplement 12` - NOT EXPLAINED
- who-trs992-a5-ttsp-supplements.pdf Annex 1 #4 (section): `-annex 1 | +o t e c h r e p o r t s e s n o 9 9 2 2 0 1 5 supplement 13` - NOT EXPLAINED
- who-trs992-a5-ttsp-supplements.pdf Annex 1 A 1.3.2 (clause): `+o t e c h r e p o r t s e s n o 9 9 2 2 0 1 5 supplement 15` - NOT EXPLAINED
- who-trs992-a5-ttsp-supplements.pdf Annex 1 #5 (section): `-annex 1` - NOT EXPLAINED
- who-trs992-a5-ttsp-supplements.pdf page 4 (uncovered): `+in table row: title section s` - NOT EXPLAINED
- who-trs992-a5-ttsp-supplements.pdf page 4 (uncovered): `+in table row: 10 checking the accuracy` - NOT EXPLAINED
- who-trs992-a5-ttsp-supplements.pdf page 4 (uncovered): `+in table row: control` - NOT EXPLAINED
- who-trs992-a5-ttsp-supplements.pdf page 4 (uncovered): `+in table row: devices` - NOT EXPLAINED
- who-trs992-a5-ttsp-supplements.pdf page 4 (uncovered): `+in table row: 4.10` - NOT EXPLAINED
- who-trs992-a5-ttsp-supplements.pdf page 13 (uncovered): `+acknowledgements abbreviations glossary 1 introduction 1.1 requirements` - NOT EXPLAINED
- who-trs992-a5-ttsp-supplements.pdf page 18 (uncovered): `+acknowledgements abbreviations glossary 1 introduction 1.1 requirements 1.2 objectives 1.3 target readership 2 guidance` - NOT EXPLAINED
- who-trs992-a5-ttsp-supplements.pdf page 21 (uncovered): `+acknowledgements abbreviations glossary 1 introduction 1.1 requirements 1.2 objectives` - NOT EXPLAINED
- who-trs992-a5-ttsp-supplements.pdf page 21 (uncovered): `+1.3 target readership 2 guidance` - Text read outside any clause's stretch that is stored word for word in another clause of the document (verified mechanically): a running title, table caption or text read in another order.
- who-trs992-a5-ttsp-supplements.pdf page 27 (uncovered): `+acknowledgements abbreviations glossary 1 introduction 1.1 requirements 1.2 objectives 1.3 target readership 2 guidance` - NOT EXPLAINED
- who-trs992-a5-ttsp-supplements.pdf page 10 (uncovered): `+next to _unnumbered:7: acknowledgements abbreviations` - NOT EXPLAINED
- who-trs992-a5-ttsp-supplements.pdf page 10 (uncovered): `+next to Annex 2 Glossary #2: abbreviations acknowledgements` - NOT EXPLAINED
- who-trs992-a5-ttsp-supplements.pdf page 10 (uncovered): `+next to Annex 2 2.7.4: references` - NOT EXPLAINED
- who-trs992-a5-ttsp-supplements.pdf page 17 (uncovered): `+next to Annex 1 2.5 #2: references` - NOT EXPLAINED
- who-trs992-a5-ttsp-supplements.pdf page 23 (uncovered): `+next to Annex 1 2.9: references` - NOT EXPLAINED
- who-trs992-a5-ttsp-supplements.pdf page 25 (uncovered): `+next to _unnumbered:28: 14 supplement` - NOT EXPLAINED
- who-trs992-a5-ttsp-supplements.pdf page 27 (uncovered): `+next to _unnumbered:32: 16 supplement` - NOT EXPLAINED
- who-trs992-a5-ttsp-supplements.pdf page 12 (uncovered): `+in two clauses _unnumbered:10 and _unnumbered:12: acknowledgements abbreviations glossary 1 introduction 1.1 requirements 1.2 objectives 1.3 target readership 2 guidance 2.1 associated materials and equipment` - NOT EXPLAINED
- who-trs992-a5-ttsp-supplements.pdf page 23 (uncovered): `+in two clauses Annex 1 1 #3 and Annex 1 1 #4: 1 introduction 1.1 requirements 1.2 objectives 1.3 target readership 2 guidance` - NOT EXPLAINED
- who-trs996-a4-app1-model-inspection-report.pdf Appendix 1 (section): `+information | +performed at the site | -performed at the site | +o t e c h r e p o r t s e s n o 9 9 6 2 0 1 6 part 1 general information | +authority | +used for assessing compliance | -used for assessing | -compliance` - NOT EXPLAINED
- who-trs996-a4-app1-model-inspection-report.pdf Appendix 1 1 (clause): `+introduction | +the manufacturing activities | -the manufacturing | -activities | +where applicable` - NOT EXPLAINED
- who-trs996-a4-app1-model-inspection-report.pdf Appendix 1 2 #2 (clause): `+practices for pharmaceutical products | -practices | +implemented 3 sanitation and hygiene describe procedures and records relating to sanitation and hygiene | -implemented pharmaceutical products` - NOT EXPLAINED
- who-trs996-a4-app1-model-inspection-report.pdf Appendix 1 3 #2 (clause): `+hygiene` - NOT EXPLAINED
- who-trs996-a4-app1-model-inspection-report.pdf Appendix 1 4 #2 (clause): `+validation | -validation` - NOT EXPLAINED
- who-trs996-a4-app1-model-inspection-report.pdf Appendix 1 7 (clause): `+analysis and other activities | -analysis and other | -activities` - NOT EXPLAINED
- who-trs996-a4-app1-model-inspection-report.pdf Appendix 1 8 (clause): `-self inspection a | +suppliers audits and approval a self inspection | -suppliers audits and | -approval` - NOT EXPLAINED
- who-trs996-a4-app1-model-inspection-report.pdf Appendix 1 16 (clause): `+production` - NOT EXPLAINED
- who-trs996-a4-app1-model-inspection-report.pdf Appendix 1 17 (clause): `+quality control | -quality control | +where applicable | +master file` - NOT EXPLAINED
- who-trs996-a4-app1-model-inspection-report.pdf Appendix 1 3 #3 (clause): `+part 4 outcome | +o t e c h r e p o r t s e s n o 9 9 6 2 0 1 6 part 5 list of gmp guidelines referenced in the inspection` - NOT EXPLAINED
- who-trs996-a4-app1-model-inspection-report.pdf Annex 3 (section): `-annex 3 | +the inspection | -the inspection | +due for planning purposes | -due for planning | -purposes` - NOT EXPLAINED
- who-trs996-a4-app1-model-inspection-report.pdf page 16 (uncovered): `+in table row: category` - NOT EXPLAINED
- who-trs996-a4-app1-model-inspection-report.pdf page 16 (uncovered): `+in table row: the site` - NOT EXPLAINED
- who-trs996-a4-app1-model-inspection-report.pdf page 2 (uncovered): `+next to Appendix 2 1.1: introduction 1` - NOT EXPLAINED
- who-trs996-a4-app1-model-inspection-report.pdf page 2 (uncovered): `+next to Appendix 2 1.1: 2 scope` - NOT EXPLAINED
- who-trs996-a4-app1-model-inspection-report.pdf page 2 (uncovered): `+next to Appendix 2 2.1: scope 2` - NOT EXPLAINED
- who-trs996-a4-app1-model-inspection-report.pdf page 10 (uncovered): `+next to Appendix 1 2 #2: applicable where` - NOT EXPLAINED
- who-trs996-a4-app1-model-inspection-report.pdf page 10 (uncovered): `+in two clauses Appendix 1 2 #2 and Appendix 1 3 #2: 3 sanitation and hygiene describe procedures and records relating to sanitation and hygiene for` - NOT EXPLAINED
