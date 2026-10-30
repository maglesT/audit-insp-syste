# Source fidelity report

Built by `python3 tools/parse/fidelity.py run` (D39): every parsed clause of every PDF source compared in both directions with a second reading (pdfminer.six via pdfplumber); the rules are in the module docstring. Every flagged clause is fixed or explained in `library/fidelity-explanations.csv`.

Sources: 146; clauses: 20562; tokens: 1593633; flagged clauses: 911; unexplained: 911.

| Source | Clauses | Flagged |
|---|---|---|
| ema-hbel-guideline.pdf | 26 | 2 |
| ema-hbel-qa-cross-contamination.pdf | 14 | 1 |
| ema-manufacture-finished-dosage-form.pdf | 32 | 3 |
| ema-nitrosamines-qa-mah-rev23-2025.pdf | 61 | 18 |
| ema-process-validation-finished-products.pdf | 30 | 1 |
| ema-qa-microbial-contamination-nonsterile.pdf | 3 | 2 |
| ema-qa-wfi-non-distillation.pdf | 21 | 1 |
| ema-sterilisation-guideline.pdf | 58 | 6 |
| ema-water-quality-guideline.pdf | 66 | 2 |
| eu-2014-03_chapter_2.pdf | 25 | 1 |
| eu-2014-08_gmp_chap8.pdf | 33 | 0 |
| eu-2014-08_gmp_part1.pdf | 439 | 0 |
| eu-2014-11_vol4_chapter_6.pdf | 43 | 0 |
| eu-2015-10_annex15.pdf | 118 | 1 |
| eu-2015-c95-01-gdp-active-substances.pdf | 62 | 0 |
| eu-2015-c95-02-excipients-risk-assessment.pdf | 19 | 4 |
| eu-2018_annex17_en.pdf | 37 | 0 |
| eu-20220825_gmp-an1_en_0.pdf | 335 | 3 |
| eu-annex11_01-2011_en.pdf | 40 | 0 |
| eu-annex19-2026-c2026-4135.pdf | 51 | 1 |
| eu-annex21-importation.pdf | 30 | 0 |
| eu-anx08_en.pdf | 7 | 1 |
| eu-anx09_en.pdf | 11 | 0 |
| eu-cap9_en.pdf | 5 | 0 |
| eu-chapter4_01-2011_en.pdf | 35 | 0 |
| eu-chapter_3.pdf | 46 | 3 |
| eu-chapter_5.pdf | 74 | 2 |
| eu-directive-2017-1572-gmp.pdf | 67 | 0 |
| eu-p3-gmp-mah-reflection-paper.pdf | 16 | 3 |
| eu-p3-site-master-file.pdf | 39 | 0 |
| eu-regulation-1252-2014-gmp-active-substances.pdf | 99 | 0 |
| eu-v4_an16_201510_en.pdf | 74 | 0 |
| eu-vol4-chap1_2013-01_en.pdf | 15 | 0 |
| eu-vol4-chap7_2012-06_en.pdf | 19 | 0 |
| eu-written-confirmation-template-2013.pdf | 13 | 3 |
| fda-aseptic-2004.pdf | 80 | 3 |
| fda-cp-7346-832-preapproval-inspections.pdf | 75 | 23 |
| fda-cp-7356-002-drug-manufacturing-inspections.pdf | 60 | 5 |
| fda-cp-7356-002a-sterile-drug-process.pdf | 54 | 3 |
| fda-cp-7356-002f-api.pdf | 35 | 4 |
| fda-cp-7356-021-dqrs-field-alerts.pdf | 26 | 1 |
| fda-cp-7356-843-postapproval-inspections.pdf | 44 | 2 |
| fda-data-integrity-2018.pdf | 29 | 1 |
| fda-guidance-analytical-procedures-validation-2015.pdf | 32 | 34 |
| fda-guidance-anda-stability-2013.pdf | 5 | 2 |
| fda-guidance-benzene-carbomers-2023.pdf | 10 | 1 |
| fda-guidance-cci-in-lieu-of-sterility-2008.pdf | 9 | 1 |
| fda-guidance-changes-approved-nda-anda-2004.pdf | 74 | 1 |
| fda-guidance-container-closure-systems-1999.pdf | 86 | 29 |
| fda-guidance-deg-eg-high-risk-components-2023.pdf | 6 | 3 |
| fda-guidance-delaying-denying-inspection-2024.pdf | 15 | 2 |
| fda-guidance-dissolution-mechanical-calibration-2010.pdf | 5 | 3 |
| fda-guidance-elemental-impurities-2018.pdf | 15 | 3 |
| fda-guidance-field-alert-report-qa-2021.pdf | 16 | 3 |
| fda-guidance-melamine-components-2009.pdf | 6 | 2 |
| fda-guidance-methanol-testing-alcohol-2023.pdf | 7 | 2 |
| fda-guidance-nitrosamine-control-2024.pdf | 58 | 9 |
| fda-guidance-nitrosamine-ndsri-ai-limits-2023.pdf | 52 | 3 |
| fda-guidance-npbl-cross-contamination-2013.pdf | 9 | 3 |
| fda-guidance-part11-scope-application-2003.pdf | 16 | 17 |
| fda-guidance-product-recalls-2020.pdf | 6 | 1 |
| fda-guidance-pyrogen-endotoxins-qa-2026.pdf | 19 | 3 |
| fda-guidance-quality-agreements-2016.pdf | 21 | 3 |
| fda-guidance-quality-systems-approach-2006.pdf | 67 | 14 |
| fda-guidance-remote-regulatory-assessments-2025.pdf | 20 | 3 |
| fda-guidance-sterilization-validation-submission-1994.pdf | 91 | 7 |
| fda-guidance-voluntary-recalls-initiation-2022.pdf | 10 | 5 |
| fda-oos-2022.pdf | 24 | 3 |
| fda-process-validation-2011.pdf | 23 | 0 |
| ich-m7-r2.pdf | 109 | 11 |
| ich-q10.pdf | 58 | 2 |
| ich-q11-qa-pmda.pdf | 68 | 3 |
| ich-q12.pdf | 137 | 10 |
| ich-q1a-r2.pdf | 73 | 3 |
| ich-q1b.pdf | 11 | 3 |
| ich-q1d.pdf | 46 | 2 |
| ich-q1e.pdf | 68 | 4 |
| ich-q2-r2.pdf | 202 | 22 |
| ich-q3a-r2.pdf | 33 | 4 |
| ich-q3b-r2.pdf | 26 | 3 |
| ich-q3c-r9.pdf | 68 | 20 |
| ich-q3d-r2.pdf | 381 | 21 |
| ich-q6a.pdf | 35 | 3 |
| ich-q7-qa.pdf | 206 | 7 |
| ich-q7.pdf | 446 | 3 |
| ich-q8-q9-q10-qa-r4.pdf | 89 | 11 |
| ich-q9r1.pdf | 45 | 2 |
| india-cdsco-circ-2024-03-risk-based-inspection.pdf | 1314 | 126 |
| india-cdsco-gdp-guidelines-2024.pdf | 217 | 0 |
| india-drugs-rules-1945-consolidated-2024-07.pdf | 2981 | 91 |
| india-gsr127e-2025-schm-timeline.pdf | 14 | 6 |
| india-gsr666e-2024-schm-corrigendum.pdf | 1 | 3 |
| india-schedule-m-2023-GSR922E.pdf | 1593 | 18 |
| pics-pe008-4-site-master-file.pdf | 47 | 1 |
| pics-pe009-18-annexes.pdf | 1303 | 12 |
| pics-pe009-18-part1.pdf | 286 | 10 |
| pics-pe009-18-part2.pdf | 449 | 9 |
| pics-pi006-4-qualification-validation.pdf | 282 | 0 |
| pics-pi007-6-aseptic-validation.pdf | 172 | 1 |
| pics-pi009-4-am-utilities.pdf | 56 | 5 |
| pics-pi011-3-computerised-systems.pdf | 260 | 10 |
| pics-pi012-3-sterility-testing.pdf | 125 | 2 |
| pics-pi014-3-isolators.pdf | 113 | 0 |
| pics-pi023-2-am-qc-labs.pdf | 97 | 11 |
| pics-pi028-2-am-packaging.pdf | 29 | 5 |
| pics-pi030-1-am-api.pdf | 114 | 9 |
| pics-pi038-2-am-qrm.pdf | 94 | 1 |
| pics-pi040-1-deficiency-classification.pdf | 55 | 0 |
| pics-pi041-1-data-integrity.pdf | 401 | 5 |
| pics-pi043-1-am-cross-contamination.pdf | 154 | 1 |
| pics-pi045-1-excipient-risk-assessment.pdf | 26 | 0 |
| pics-pi047-1-gdp-active-substances.pdf | 70 | 0 |
| pics-pi052-1-am-hbel.pdf | 39 | 1 |
| pics-pi053-1-qa-cross-contamination.pdf | 18 | 1 |
| pics-pi054-1-pqs-effectiveness.pdf | 125 | 0 |
| pics-pi058-1-annex1-interpretation.pdf | 109 | 2 |
| who-trs1010-a10-stability.pdf | 82 | 8 |
| who-trs1010-a8-hvac-nonsterile.pdf | 121 | 38 |
| who-trs1019-a2-hvac-nonsterile-part2.pdf | 24 | 4 |
| who-trs1019-a3-validation.pdf | 407 | 0 |
| who-trs1025-a3-wfi-non-distillation.pdf | 39 | 2 |
| who-trs1025-a4-chromatography.pdf | 100 | 0 |
| who-trs1025-a6-amr-environment.pdf | 14 | 0 |
| who-trs1025-a7-storage-distribution.pdf | 215 | 1 |
| who-trs1033-a2-hbel-cleaning.pdf | 51 | 2 |
| who-trs1033-a3-water.pdf | 121 | 0 |
| who-trs1033-a4-data-integrity.pdf | 88 | 0 |
| who-trs1044-a2-sterile.pdf | 315 | 10 |
| who-trs1044-a4-tech-transfer.pdf | 136 | 2 |
| who-trs1052-a4-qc-labs.pdf | 382 | 4 |
| who-trs1060-a2-nitrosamines.pdf | 130 | 1 |
| who-trs1060-a3-excipients.pdf | 272 | 12 |
| who-trs902-a9-packaging.pdf | 110 | 2 |
| who-trs929-a4-sampling.pdf | 83 | 22 |
| who-trs943-a3-reference-substances.pdf | 42 | 0 |
| who-trs953-a2-app1-stability-conditions.pdf | 208 | 1 |
| who-trs957-a2-api.pdf | 559 | 2 |
| who-trs957-a3-hazardous.pdf | 94 | 10 |
| who-trs961-a14-site-master-file.pdf | 32 | 1 |
| who-trs961-a2-micro-labs.pdf | 206 | 12 |
| who-trs961-a9-storage-transport-ttsp.pdf | 142 | 9 |
| who-trs981-a2-qrm.pdf | 46 | 8 |
| who-trs986-a2-gmp-main.pdf | 322 | 0 |
| who-trs992-a4-hold-time.pdf | 6 | 1 |
| who-trs992-a5-ttsp-supplements.pdf | 318 | 27 |
| who-trs996-a4-app1-model-inspection-report.pdf | 84 | 11 |

## Flagged clauses

- ema-hbel-guideline.pdf _unnumbered:1 (unnumbered): `-churchill place canary wharf london e 14 5 eu united kingdom telephone 44 0 | +june 2013 adoption by cvmp 11 september 2014 adopted by safety working party october 2014 adoption by chmp | -3660 6000 facsimile 44 0 20 3660 5555 send a question via our website www ema europa eu contact an agency of t` - NOT EXPLAINED
- ema-hbel-guideline.pdf 5.1 (clause): `+−` - NOT EXPLAINED
- ema-hbel-qa-cross-contamination.pdf Q2 (clause): `-30 churchill place canary wharf london e 14 5 eu united kingdom telephone 44 0 20 3660 6000 facsimile 44 0 20 3660 5555 send a question via our website www ema europa eu contact an agency of the european union european medicines agency 2018 reproduction is authorised provided the source is acknowle` - NOT EXPLAINED
- ema-manufacture-finished-dosage-form.pdf _unnumbered:1 (unnumbered): `-4 july 2017 ema chmp qwp 245074 2015 committee for human medicinal products chmp guideline on manufacture of the finished dosage form this guideline replaces the note for guidance on manufacture of the finished dosage form cpmp qwp 486 95 | -an agency of the european union | -table of contents exec` - NOT EXPLAINED
- ema-manufacture-finished-dosage-form.pdf Table 4 6/ Wet massing (table_row): `-cpp cpp cpp 150 190 1800 2500 3 7` - NOT EXPLAINED
- ema-manufacture-finished-dosage-form.pdf Table 4 7/ Wet screening mass (table_row): `-screening` - NOT EXPLAINED
- ema-nitrosamines-qa-mah-rev23-2025.pdf _unnumbered:1 (unnumbered): `-official address domenico scarlattilaan 6 1083 hs amsterdam the netherlands address for visits and deliveries refer to www ema europa eu how to find us send us a question go to www ema europa eu contact telephone 31 0 88 781 6000 an agency of the european union european medicines agency 2025 reprod` - NOT EXPLAINED
- ema-nitrosamines-qa-mah-rev23-2025.pdf _unnumbered:2 (unnumbered): `-revision history questions and answers for marketing authorisation holders applicants on the chmp questions and answers for marketing authorisation holders applicants on the chmp | -questions and answers for marketing authorisation holders applicants on the chmp` - NOT EXPLAINED
- ema-nitrosamines-qa-mah-rev23-2025.pdf Q1 (clause): `-questions and answers for marketing authorisation holders applicants on the chmp` - NOT EXPLAINED
- ema-nitrosamines-qa-mah-rev23-2025.pdf Q2 (clause): `-questions | +3 for the call for review for chemically synthesised | -answers for marketing authorisation holders applicants on the chmp` - NOT EXPLAINED
- ema-nitrosamines-qa-mah-rev23-2025.pdf Q3 (clause): `-questions and answers for marketing authorisation holders applicants on the chmp | -questions and answers for marketing authorisation holders applicants on the chmp` - NOT EXPLAINED
- ema-nitrosamines-qa-mah-rev23-2025.pdf Q4 (clause): `-questions and answers for marketing authorisation holders applicants on the chmp | -questions and answers for marketing authorisation holders applicants on the chmp` - NOT EXPLAINED
- ema-nitrosamines-qa-mah-rev23-2025.pdf Q5 (clause): `-questions and answers for marketing authorisation holders applicants on the chmp` - NOT EXPLAINED
- ema-nitrosamines-qa-mah-rev23-2025.pdf Q7 (clause): `-questions and answers for marketing authorisation holders applicants on the chmp` - NOT EXPLAINED
- ema-nitrosamines-qa-mah-rev23-2025.pdf Q8 (clause): `-questions and answers for marketing authorisation holders applicants on the chmp | -questions | +9 what are the requirements of the analytical method s the analytical methods need to be sufficiently sensitive in order to adequately detect | -answers for marketing authorisation holders applicants on` - NOT EXPLAINED
- ema-nitrosamines-qa-mah-rev23-2025.pdf Q10 (clause): `-questions and answers for marketing authorisation holders applicants on the chmp | -questions and answers for marketing authorisation holders applicants on the chmp | +xi aii | -xi | +i 2 | -aii i 2 questions and answers for marketing authorisation holders applicants on the chmp | -320 ppb 88 ppb |` - NOT EXPLAINED
- ema-nitrosamines-qa-mah-rev23-2025.pdf Q12 (clause): `-questions and answers for marketing authorisation holders applicants on the chmp` - NOT EXPLAINED
- ema-nitrosamines-qa-mah-rev23-2025.pdf Q14 (clause): `-questions and answers for marketing authorisation holders applicants on the chmp | -questions and answers for marketing authorisation holders applicants on the chmp` - NOT EXPLAINED
- ema-nitrosamines-qa-mah-rev23-2025.pdf Q16 (clause): `-questions and answers for marketing authorisation holders applicants on the chmp` - NOT EXPLAINED
- ema-nitrosamines-qa-mah-rev23-2025.pdf Q20 (clause): `-questions and answers for marketing authorisation holders applicants on the chmp` - NOT EXPLAINED
- ema-nitrosamines-qa-mah-rev23-2025.pdf Q22 (clause): `-questions and answers for marketing authorisation holders applicants on the chmp | -questions and answers for marketing authorisation holders applicants on the chmp | -questions and answers for marketing authorisation holders applicants on the chmp` - NOT EXPLAINED
- ema-nitrosamines-qa-mah-rev23-2025.pdf Table 1 4* (table_row): `-4 updates 3 on when perform step 2 confirmatory testing in order meet the established deadline step 3 and nmor 29 th june` - NOT EXPLAINED
- ema-nitrosamines-qa-mah-rev23-2025.pdf Table 1 6 (table_row): `-guidance on confirmatory testing requirements marketed q a 8 and on going applications q a 14 to include cases where a potential nitrosamine impurity cannot be synthesised and when a product available in multiple strengths of same dosage form 14 th october 2021 14 th october 2021` - NOT EXPLAINED
- ema-nitrosamines-qa-mah-rev23-2025.pdf Table 4 row 1 (table_row): `-results 2 fixed example 20 80 ratio results 2 flexible results` - NOT EXPLAINED
- ema-process-validation-finished-products.pdf _unnumbered:1 (unnumbered): `-30 churchill place canary wharf london e 14 | +draft agreed by chmp cvmp quality working party 2 february 2012 adoption by cvmp for release for consultation 8 march 2012 adoption by chmp for release for consultation 15 march 2012 end of consultation deadline for comments 31 october 2012 agreed by q` - NOT EXPLAINED
- ema-qa-microbial-contamination-nonsterile.pdf _unnumbered:1 (unnumbered): `-official address domenico scarlattilaan 6 1083 hs amsterdam the netherlands address for visits and deliveries refer to www ema europa eu how to find us an agency of the european union send us a question go to www ema europa eu contact telephone 31 0 88 781 6000 european medicines agency 2026 reprod` - NOT EXPLAINED
- ema-qa-microbial-contamination-nonsterile.pdf Q2 (clause): `-what are technical and organisational measures that should be taken into consideration to prevent microbial contamination of non sterile medicinal products ema ins gmp 161750 2026 page 3 3` - NOT EXPLAINED
- ema-qa-wfi-non-distillation.pdf _unnumbered:1 (unnumbered): `-30 churchill place canary wharf london e 14 5 eu united kingdom telephone 44 0 20 3660 6000 facsimile 44 0 20 3660 5555 send a question via our website www ema europa eu contact an agency of the european union european medicines agency 2017 reproduction is authorised provided the source is acknowle` - NOT EXPLAINED
- ema-sterilisation-guideline.pdf _unnumbered:1 (unnumbered): `-official address domenico scarlattilaan 6 1083 hs amsterdam the netherlands address for visits and deliveries refer to www ema europa eu how to find us send us a question go to www ema europa eu contact telephone 31 0 88 781 6000 an agency of the european union european medicines agency 2019 reprod` - NOT EXPLAINED
- ema-sterilisation-guideline.pdf 4.1.1 (clause): `+−` - NOT EXPLAINED
- ema-sterilisation-guideline.pdf 4.1.2 (clause): `+− | +−` - NOT EXPLAINED
- ema-sterilisation-guideline.pdf 4.1.4.1 (clause): `+−` - NOT EXPLAINED
- ema-sterilisation-guideline.pdf 4.1.6 (clause): `+−` - NOT EXPLAINED
- ema-sterilisation-guideline.pdf Definitions (section): `+− | +−` - NOT EXPLAINED
- ema-water-quality-guideline.pdf _unnumbered:1 (unnumbered): `-guideline on the | +draft agreed by | -water | +public consultation 15 november 2018 end of consultation deadline | -pharmaceutical use | +comments 15 may 2019 agreed by gmdp iwg 5 march 2020 agreed by bwp 18 march 2020 agreed by qwp 6 may 2020 adopted by chmp for publication 28 may 2020 adopted by` - NOT EXPLAINED
- ema-water-quality-guideline.pdf Table 5 AS is in solution, not sterile, and… (table_row): `-wfi` - NOT EXPLAINED
- eu-2014-03_chapter_2.pdf _unnumbered:1 (unnumbered): `-ref ares 2014 968076 28 03 2014` - NOT EXPLAINED
- eu-2015-10_annex15.pdf _unnumbered:1 (unnumbered): `-ref ares 2015 1380025 30 03 2015 | -commission européenne europese commissie 1049 bruxelles brussel belgique belgië tel 32 22991111` - NOT EXPLAINED
- eu-2015-c95-02-excipients-risk-assessment.pdf _unnumbered:1 (unnumbered): `-c 95 10 en official journal of the european union 21.3.2015` - NOT EXPLAINED
- eu-2015-c95-02-excipients-risk-assessment.pdf Chapter 2 2.3 (clause): `-21.3.2015 | +c 95 10 | -c 95 11 | +21.3.2015` - NOT EXPLAINED
- eu-2015-c95-02-excipients-risk-assessment.pdf Chapter 2 2.6 (clause): `-c 95 12 | +21.3.2015 | -21.3.2015 | +c 95 11` - NOT EXPLAINED
- eu-2015-c95-02-excipients-risk-assessment.pdf Chapter 4 4.1 (clause): `-21.3.2015 | +c 95 12 | -c 95 13 | +21.3.2015` - NOT EXPLAINED
- eu-20220825_gmp-an1_en_0.pdf _unnumbered:1 (unnumbered): `-european commission brussels 22.8.2022 | -2022 5938 final guidelines | +u d o n p r o il na un 2 2 a a n e d i c i 0 n p m 8 2 8 f i u r o o r 2 3 ef s e l s 2 2 2 5 9 n t h e a c t i c e u s e u s 2 0 s i p b r c t r e unn l i n p r o d t u r i e t e r i no n g u i d d i c i n a m a n u f n a n d ` - NOT EXPLAINED
- eu-20220825_gmp-an1_en_0.pdf Annex 1 8.6 (clause): `-aseptic preparation and processing` - NOT EXPLAINED
- eu-20220825_gmp-an1_en_0.pdf Annex 1 Glossary (section): `+− | +−` - NOT EXPLAINED
- eu-annex19-2026-c2026-4135.pdf _unnumbered:1 (unnumbered): `-european commission brussels 23.6.2026 | +o mm i ss i o n b r u ss e l s 23 6 | -4135 final guidelines | +c 20 26 413 5 f i n a l g u i d el i n e s t h e r u l e s g ov er n i n g m e d i c i n a l p r o d u c t s i n t h e e u r o p e a n u n i o n v o l u m e 4 e u g u i d e li n e s f o r g oo ` - NOT EXPLAINED
- eu-anx08_en.pdf Annex 8 3 (clause): `+n` - NOT EXPLAINED
- eu-chapter_3.pdf _unnumbered:1 (unnumbered): `-ref ares 2015 283695 23 01 2015 | -commission européenne b 1049 bruxelles europese commissie b 1049 brussel belgium telephone 32 2 299 11 11 | +ref ares 2015 283695 23 01 2015` - NOT EXPLAINED
- eu-chapter_3.pdf 3 Principle (principle): `+p remises general 3.1` - NOT EXPLAINED
- eu-chapter_3.pdf 3.33 (clause): `+e quipment 3.34 manufacturing` - NOT EXPLAINED
- eu-chapter_5.pdf Chapter 5 (section): `-commission européenne b 1049 bruxelles europese commissie b 1049 brussel belgium telephone 32 2 299 11 11 | +ref ares 2015 283689 23 01 2015` - NOT EXPLAINED
- eu-chapter_5.pdf Chapter 5 5.71 (clause): `+4` - NOT EXPLAINED
- eu-p3-gmp-mah-reflection-paper.pdf _unnumbered:1 (unnumbered): `-an agency of the european union` - NOT EXPLAINED
- eu-p3-gmp-mah-reflection-paper.pdf 5.2 (clause): `+manufac the document titled guidance for the template for the qualified person s declaration concerning gmp compliance of active substance manufacture also addresses the responsibility of the mah to ensure that a written confirmation of compliance of the` - NOT EXPLAINED
- eu-p3-gmp-mah-reflection-paper.pdf 5.3 (clause): `-the document titled guidance for the template for the qualified person s declaration concerning gmp compliance of active substance manufacture also addresses the responsibility of the mah to ensure that a written confirmation of compliance of the manufac` - NOT EXPLAINED
- eu-written-confirmation-template-2013.pdf _unnumbered:1 (unnumbered): `-ref ares 2013 101580 28 01 2013` - NOT EXPLAINED
- eu-written-confirmation-template-2013.pdf 2 (clause): `-2 the template for this written confirmation is set out in annex 1 http ec europa eu health documents pharmaceutical committee index en htm commission 2 writteneuropéenne europese confirmations basedcommissie 1049 bruxelles brussel on the previous belgique belgië version of the template tel 32 2299` - NOT EXPLAINED
- eu-written-confirmation-template-2013.pdf page 1 (uncovered): `+written confirmations based on the previous version of the template remain valid` - NOT EXPLAINED
- fda-aseptic-2004.pdf IV (clause): `-classificationsa | +classifications a clean area classification 0.5 um particles ft 3 iso designation b > 0.5 μm particles m 3 microbiological active air action levels c cfu m 3 microbiological settling plates action levels c d diam 90 mm cfu 4 hours 100 5 3,520 1 e 1 e 1000 6 35,200 7 3 10,000 7 3` - NOT EXPLAINED
- fda-aseptic-2004.pdf IX.C.1 (clause): `+−` - NOT EXPLAINED
- fda-aseptic-2004.pdf _unnumbered:4 (unnumbered): `+−` - NOT EXPLAINED
- fda-cp-7346-832-preapproval-inspections.pdf Part II 2.A (clause): `-yes risk assessment supports determination pai not needed of pai objectives no no risk assessment supports potential use of alternative tools ats in lieu of inspection yes | -no yes | +pai needed risk assessment supports determination of pai objectives yes yes no no no risk assessment supports pote` - NOT EXPLAINED
- fda-cp-7346-832-preapproval-inspections.pdf Part III 1.B (clause): `+29` - NOT EXPLAINED
- fda-cp-7346-832-preapproval-inspections.pdf Part V B (clause): `+45` - NOT EXPLAINED
- fda-cp-7346-832-preapproval-inspections.pdf Part VI D (clause): `+46` - NOT EXPLAINED
- fda-cp-7346-832-preapproval-inspections.pdf _unnumbered:6 (unnumbered): `-dmf drug master file | -eir establishment inspection report | -far field alert report | +action cder center for drug evaluation and research cgmp current good manufacturing practice cmc chemistry manufacturing and controls cms compliance management system conops concept of operations cqa critical q` - NOT EXPLAINED
- fda-cp-7346-832-preapproval-inspections.pdf Attachment A (clause): `+in addition to its inspectional authority fda may conduct remote regulatory assessments rras under certain circumstances to support oversight of fda regulated products and establishments 1` - NOT EXPLAINED
- fda-cp-7346-832-preapproval-inspections.pdf Attachment B (clause): `-cont next page cont next page cont next page cont next page cont next page cont next page manufacturing and control the iqa team assesses the the inspection team inspection team lead or pam of finished product sterility control and assurance evaluates the facility provides the iqa team with informa` - NOT EXPLAINED
- fda-cp-7346-832-preapproval-inspections.pdf Table 4 Novel excipient manufacturing (e.g.… (table_row): `-recommends a pai better communicates finds released lots do meet manufacturer observations form fda 483 communicates requests assessment before pai pai assessment after pai` - NOT EXPLAINED
- fda-cp-7346-832-preapproval-inspections.pdf Table 5 Manufacturing and control of finished… (table_row): `-finds deficient includes observations on form 483 works with understand impact on communicates quality with requests they update reflect a higher e g consistent with recommendations guidance communicates quality with inspected example identifies blender revolutions as proposes a lower e g annual re` - NOT EXPLAINED
- fda-cp-7346-832-preapproval-inspections.pdf page 47 (uncovered): `+resolve outstanding quality issues for` - NOT EXPLAINED
- fda-cp-7346-832-preapproval-inspections.pdf page 48 (uncovered): `+integrated approach quality topic integrated approach` - NOT EXPLAINED
- fda-cp-7346-832-preapproval-inspections.pdf page 49 (uncovered): `+addressing quality related topics via an integrated approach quality topic integrated approach` - NOT EXPLAINED
- fda-cp-7346-832-preapproval-inspections.pdf page 50 (uncovered): `+related topics via an integrated approach quality topic integrated approach` - NOT EXPLAINED
- fda-cp-7346-832-preapproval-inspections.pdf page 51 (uncovered): `+addressing quality related topics via an integrated approach quality topic integrated approach` - NOT EXPLAINED
- fda-cp-7346-832-preapproval-inspections.pdf page 52 (uncovered): `+addressing quality related topics via an integrated approach quality topic integrated approach` - NOT EXPLAINED
- fda-cp-7346-832-preapproval-inspections.pdf page 53 (uncovered): `+of finished product sterility assurance` - NOT EXPLAINED
- fda-cp-7346-832-preapproval-inspections.pdf page 53 (uncovered): `+sterile drug products the iqa team assesses the sterility control and assurance information provided in the application e g suitability of the selected methods of sterilization adequacy of critical process parameters test method selection specifications` - NOT EXPLAINED
- fda-cp-7346-832-preapproval-inspections.pdf page 53 (uncovered): `+for example the inspection team evaluates the state of control of the process as well as the manufacturing procedures practices` - NOT EXPLAINED
- fda-cp-7346-832-preapproval-inspections.pdf page 53 (uncovered): `+controls employed to ensure product sterility the inspection team also evaluates` - NOT EXPLAINED
- fda-cp-7346-832-preapproval-inspections.pdf page 53 (uncovered): `+are about the aseptic process` - NOT EXPLAINED
- fda-cp-7346-832-preapproval-inspections.pdf page 53 (uncovered): `+for example the iqa team identifies risks and concerns regarding the sterilization process and controls for sterility assurance` - NOT EXPLAINED
- fda-cp-7346-832-preapproval-inspections.pdf page 53 (uncovered): `+environmental monitoring program media fill process validation and communicates them to` - NOT EXPLAINED
- fda-cp-7346-832-preapproval-inspections.pdf page 53 (uncovered): `+the aseptic processing area is deficient regarding the environmental monitoring program and includes its observations on form fda 483 the iqa team uses the inspection findings to request that the facility update its environmental monitoring program to address the risks to sterility assurance of the` - NOT EXPLAINED
- fda-cp-7356-002-drug-manufacturing-inspections.pdf _unnumbered:1 (unnumbered): `-food and drug administration compliance program program 7356.002 chapter 56 drug quality assurance 1 we update guidances periodically for the most recent version of a guidance check the fda guidance web page at https www fda gov regulatory information search fda guidance documents` - NOT EXPLAINED
- fda-cp-7356-002-drug-manufacturing-inspections.pdf Part IV 2 (clause): `+23` - NOT EXPLAINED
- fda-cp-7356-002-drug-manufacturing-inspections.pdf Part VI 3.B (clause): `-dqrs drug quality reporting system | -eir establishment inspection report | +research cgmp current good manufacturing practice cms compliance management system dqrs drug quality reporting system ec established condition eir establishment inspection report | -cgmp current good manufacturing | -opq o` - NOT EXPLAINED
- fda-cp-7356-002-drug-manufacturing-inspections.pdf Attachment A (clause): `+in addition to its inspectional authority fda may conduct remote regulatory assessments rras under certain circumstances to support oversight of fda regulated products and establishments 1 an rra is an examination of an fda regulated establishment and or its` - NOT EXPLAINED
- fda-cp-7356-002-drug-manufacturing-inspections.pdf page 38 (uncovered): `+opq office of pharmaceutical quality oqs office of quality surveillance ora office of regulatory affairs ors office of regulatory science pac product assignment code pam preapproval program manager pet positron emission tomography plcm product lifecycle management poai potential official action ind` - NOT EXPLAINED
- fda-cp-7356-002a-sterile-drug-process.pdf Part II 2.2.C (clause): `-end part ii` - NOT EXPLAINED
- fda-cp-7356-002a-sterile-drug-process.pdf Part VII B (clause): `-sterilization depyrogenation dry heat | +dry heat sterilization depyrogenation` - NOT EXPLAINED
- fda-cp-7356-002a-sterile-drug-process.pdf page 6 (uncovered): `+end part i` - NOT EXPLAINED
- fda-cp-7356-002f-api.pdf Part I 2 (clause): `+7 | +10` - NOT EXPLAINED
- fda-cp-7356-002f-api.pdf Part III 1.B (clause): `+28 | +35` - NOT EXPLAINED
- fda-cp-7356-002f-api.pdf Part III 1.C (clause): `+38` - NOT EXPLAINED
- fda-cp-7356-002f-api.pdf Part VI 1 (clause): `+41` - NOT EXPLAINED
- fda-cp-7356-021-dqrs-field-alerts.pdf _unnumbered:1 (unnumbered): `-compliance program guidance manual 7356.021` - NOT EXPLAINED
- fda-cp-7356-843-postapproval-inspections.pdf Part II 4.A (clause): `+27` - NOT EXPLAINED
- fda-cp-7356-843-postapproval-inspections.pdf Part VI 4 (clause): `-cder center for drug evaluation and | +anda abbreviated new drug application api active pharmaceutical ingredient capa corrective action and preventive action cbe changes being effected cder center for drug evaluation and research | -anda abbreviated new drug application | -api active pharmaceutica` - NOT EXPLAINED
- fda-data-integrity-2018.pdf III.1.f (clause): `+8` - NOT EXPLAINED
- fda-guidance-analytical-procedures-validation-2015.pdf _unnumbered:1 (unnumbered): `-2015 | -3128 | -2015` - NOT EXPLAINED
- fda-guidance-analytical-procedures-validation-2015.pdf _unnumbered:2 (unnumbered): `-1 4 5 | -11 12 13` - NOT EXPLAINED
- fda-guidance-analytical-procedures-validation-2015.pdf I (clause): `-i introduction 15 this guidance supersedes the draft of the same name that published on february 19 2014 79 fr 9467 and replaces the 2000 draft guidance for industry on analytical procedures | -2,3 and the 1987 guidelines for submitting samples and analytical data for methods validation it provides` - NOT EXPLAINED
- fda-guidance-analytical-procedures-validation-2015.pdf II (clause): `-74 | -10 82 | -11 86 | -94 95` - NOT EXPLAINED
- fda-guidance-analytical-procedures-validation-2015.pdf III (clause): `-97 | -104 | -112 | -121 122 | +11` - NOT EXPLAINED
- fda-guidance-analytical-procedures-validation-2015.pdf IV (clause): `-133` - NOT EXPLAINED
- fda-guidance-analytical-procedures-validation-2015.pdf IV.A (clause): `-135 | -139` - NOT EXPLAINED
- fda-guidance-analytical-procedures-validation-2015.pdf IV.B (clause): `-141 | -144` - NOT EXPLAINED
- fda-guidance-analytical-procedures-validation-2015.pdf IV.C (clause): `-146 | -151` - NOT EXPLAINED
- fda-guidance-analytical-procedures-validation-2015.pdf IV.D (clause): `-153 | -155 | -170` - NOT EXPLAINED
- fda-guidance-analytical-procedures-validation-2015.pdf IV.E (clause): `-172 | -178` - NOT EXPLAINED
- fda-guidance-analytical-procedures-validation-2015.pdf IV.F (clause): `-180 | -184` - NOT EXPLAINED
- fda-guidance-analytical-procedures-validation-2015.pdf IV.G (clause): `-186 | -191` - NOT EXPLAINED
- fda-guidance-analytical-procedures-validation-2015.pdf IV.H (clause): `-193 | -201` - NOT EXPLAINED
- fda-guidance-analytical-procedures-validation-2015.pdf IV.I (clause): `-203` - NOT EXPLAINED
- fda-guidance-analytical-procedures-validation-2015.pdf IV.J (clause): `-220 221` - NOT EXPLAINED
- fda-guidance-analytical-procedures-validation-2015.pdf V (clause): `-223 | -236 | -248 | -255 256` - NOT EXPLAINED
- fda-guidance-analytical-procedures-validation-2015.pdf VI (clause): `-258` - NOT EXPLAINED
- fda-guidance-analytical-procedures-validation-2015.pdf VI.A (clause): `-260 | -271` - NOT EXPLAINED
- fda-guidance-analytical-procedures-validation-2015.pdf VI.B (clause): `-273 | -276 | -284 | -288 | -296 | -15 302 | -16 306` - NOT EXPLAINED
- fda-guidance-analytical-procedures-validation-2015.pdf VI.C (clause): `-308 | -314 | -327 328` - NOT EXPLAINED
- fda-guidance-analytical-procedures-validation-2015.pdf VII (clause): `-330` - NOT EXPLAINED
- fda-guidance-analytical-procedures-validation-2015.pdf VII.A (clause): `-332 | +17 | -349` - NOT EXPLAINED
- fda-guidance-analytical-procedures-validation-2015.pdf VII.B (clause): `-351 | -356 357` - NOT EXPLAINED
- fda-guidance-analytical-procedures-validation-2015.pdf VIII (clause): `-359 | -368 | -375 | -382 | -389` - NOT EXPLAINED
- fda-guidance-analytical-procedures-validation-2015.pdf VIII.A (clause): `-391 | -399 | -403` - NOT EXPLAINED
- fda-guidance-analytical-procedures-validation-2015.pdf VIII.B (clause): `-405 | -411` - NOT EXPLAINED
- fda-guidance-analytical-procedures-validation-2015.pdf VIII.B.1 (clause): `-413 | -21 422 | -22 432 | -437 | -440 | -443 | -449 | -451 | -464` - NOT EXPLAINED
- fda-guidance-analytical-procedures-validation-2015.pdf VIII.B.2 (clause): `-466 | -478` - NOT EXPLAINED
- fda-guidance-analytical-procedures-validation-2015.pdf VIII.C (clause): `-480 | -489 490` - NOT EXPLAINED
- fda-guidance-analytical-procedures-validation-2015.pdf IX (clause): `-492 | -500 | -507` - NOT EXPLAINED
- fda-guidance-analytical-procedures-validation-2015.pdf X (clause): `-x references 509 guidance for industry 27 511 andas impurities in drug products november 2010 513 | -515 | -517 | -520 | -523 | -527 | -530 | -533 | -536 | -538 | -540 | -543 | -547 | -550 | -552 | -554 | -556 | -558 | -560 | -562 | -565 | -568 | -571 | -574 | -576 | -578 | -580 | -582 | -584 | -58` - NOT EXPLAINED
- fda-guidance-analytical-procedures-validation-2015.pdf page 4 (uncovered): `+i introduction this guidance supersedes the draft of the same name that published on february 19 2014 79 fr 9467 and replaces the 2000 draft guidance for industry on analytical procedures and methods validation` - NOT EXPLAINED
- fda-guidance-analytical-procedures-validation-2015.pdf page 16 (uncovered): `+x references guidance for industry andas impurities in drug products november 2010` - NOT EXPLAINED
- fda-guidance-anda-stability-2013.pdf _unnumbered:1 (unnumbered): `-guidance for industry | -guidance for industry` - NOT EXPLAINED
- fda-guidance-anda-stability-2013.pdf _unnumbered:2 (unnumbered): `-guidance for industry` - NOT EXPLAINED
- fda-guidance-benzene-carbomers-2023.pdf III (clause): `+11 | -cbe 30 changes being effected in 30 days pas prior approval supplement` - NOT EXPLAINED
- fda-guidance-cci-in-lieu-of-sterility-2008.pdf V (clause): `+4` - NOT EXPLAINED
- fda-guidance-changes-approved-nda-anda-2004.pdf _unnumbered:1 (unnumbered): `+15 20` - NOT EXPLAINED
- fda-guidance-container-closure-systems-1999.pdf _unnumbered:2 (unnumbered): `-guidance for industry 1 container closure systems for packaging human drugs and biologics chemistry manufacturing and controls documentation` - NOT EXPLAINED
- fda-guidance-container-closure-systems-1999.pdf I (clause): `-i introduction this document is intended to provide guidance on general principles 2 for submitting information on packaging materials used for human drugs and biologics 3 this guidance supersedes the fda guideline for submitting documentation for packaging for human drugs and biologics issued in f` - NOT EXPLAINED
- fda-guidance-container-closure-systems-1999.pdf II.A (clause): `-5 these definitions are intended to clarify | -use | +materials | -certain terms in this guidance only and are not intended to supersede the definitions of container and package as provided for in 21 cfr 600.3 6 this term is | +construction | +the labeling are | -general sense for | +concern from a` - NOT EXPLAINED
- fda-guidance-container-closure-systems-1999.pdf II.B (clause): `-7 the materials of construction used in the labeling are a concern from a packaging perspective if they affect the protection and or safety of the drug product` - NOT EXPLAINED
- fda-guidance-container-closure-systems-1999.pdf II.C.2 (clause): `+this discussion does not apply to the repackaging of drug products for dispensing under the practice of pharmacy 8 fda compliance policy guides expiration dating of unit repackaged drugs 480.200 february 1 1984 rev 9 march 1995 cpg 7132 b 11 fda compliance policy guides regulatory action regarding ` - NOT EXPLAINED
- fda-guidance-container-closure-systems-1999.pdf III.A (clause): `-8 this discussion does not apply to the repackaging of drug products for dispensing under the practice of pharmacy 9 fda compliance policy guides expiration dating of unit repackaged drugs 480.200 february 1 1984 rev march 1995 cpg 7132 b 11 10 fda compliance policy guides regulatory action regardi` - NOT EXPLAINED
- fda-guidance-container-closure-systems-1999.pdf III.B.1 (clause): `+for further information regarding photostability studies see the fda guideline for the photostability testing of new 11 drug substances and products may 1997 | -11 for further information regarding photostability studies see the fda guideline for the photostability testing of new drug substances an` - NOT EXPLAINED
- fda-guidance-container-closure-systems-1999.pdf III.B.2 (clause): `+these are substances not previously determined to be safe by extraction toxicological evaluation studies e g the usp 14 biological reactivity tests or another appropriate method conducted on the packaging component as part of the qualifying process | -these are substances not previously determined ` - NOT EXPLAINED
- fda-guidance-container-closure-systems-1999.pdf III.C.2 (clause): `-2 information about suitability 15 see table 3 for additional information this section applies to primary packaging components and to those associated | +c information that should be submitted in support of an original application for any drug product 15 additional discussion and information regard` - NOT EXPLAINED
- fda-guidance-container-closure-systems-1999.pdf III.C.3 (clause): `+statistical process control is defined as t he application of statistical techniques for measuring and analyzing the 18 variation in processes juran j m ed 1988 quality control handbook 4 th ed mcgraw hill p 24.2` - NOT EXPLAINED
- fda-guidance-container-closure-systems-1999.pdf III.C.4 (clause): `-4 stability data packaging concerns stability testing of the drug product should be conducted using the container 18 statistical process control is defined as t he application of statistical techniques for measuring and analyzing the variation in processes juran j m ed 1988 quality control handbook` - NOT EXPLAINED
- fda-guidance-container-closure-systems-1999.pdf III.E.1 (clause): `-19 the terms svp and lvp as used in this guidance correspond to the definitions of small volume injection and large volume injection respectively in usp 23 page 1650` - NOT EXPLAINED
- fda-guidance-container-closure-systems-1999.pdf III.E.2 (clause): `-a including any additives used in the manufacture of a packaging component b testing for plastics should be performed on the packaging component not on the unformed resin c note that applicant s acceptance tests may include among others test parameters indicated under the description suitability an` - NOT EXPLAINED
- fda-guidance-container-closure-systems-1999.pdf III.F (clause): `+see attachment a for a listing of the fda regulations for indirect food additives 20` - NOT EXPLAINED
- fda-guidance-container-closure-systems-1999.pdf III.F.1 (clause): `-a | +c | -listing | +discussion | -the fda regulations for indirect food additives | +extraction studies 21` - NOT EXPLAINED
- fda-guidance-container-closure-systems-1999.pdf III.F.2 (clause): `-see attachment c for a discussion of extraction studies` - NOT EXPLAINED
- fda-guidance-container-closure-systems-1999.pdf III.F.3 (clause): `-a including any additives used in the manufacture of a packaging component b the materials of construction should be acceptable for contact with foods that have extraction characteristics similar to those of the drug product e g aqueous acidic alcoholic or fatty c plastics testing should be perform` - NOT EXPLAINED
- fda-guidance-container-closure-systems-1999.pdf III.G (clause): `+hartauer k j et al the effects of rayon coiler on the dissolution stability of hard shelled gelatin capsules 22 pharmaceutical technology 17 76 83 1993 | -22 hartauer k j et al the effects of rayon coiler on the dissolution stability of hard shelled gelatin capsules pharmaceutical technology 17 76 ` - NOT EXPLAINED
- fda-guidance-container-closure-systems-1999.pdf VI.A (clause): `+the 1987 stability guidance will be superseded by the fda guidance for industry stability testing of drug 23 substances and drug products issued in draft for comment in june 1998 once it is issued in final form` - NOT EXPLAINED
- fda-guidance-container-closure-systems-1999.pdf VI.B (clause): `-23 the 1987 stability guidance will be superseded by the | -guidance for industry stability testing of drug substances | +compliance policy guides regulatory action regarding approved new drugs | +antibiotic | -issued in draft for comment in june 1998 once it is issued in final form | +24 subjected` - NOT EXPLAINED
- fda-guidance-container-closure-systems-1999.pdf Attachment A (clause): `-applicants should check the appropriate sources directly for the most up to date information | -1 | +2 | +federal register volume 49 march 5 1984 page 8008 49 fr 8008 prescribed drugs distributed to prescribing 26 practitioners withdrawal of proposed statement of policy and interpretation | -2 | +3` - NOT EXPLAINED
- fda-guidance-container-closure-systems-1999.pdf Attachment B (clause): `-1 | +2` - NOT EXPLAINED
- fda-guidance-container-closure-systems-1999.pdf Attachment C (clause): `-c | +d` - NOT EXPLAINED
- fda-guidance-container-closure-systems-1999.pdf Attachment E (clause): `-27 a list of cder and cber guidances and guidelines is provided on the internet at www fda gov cder guidances index htm and www fda gov cber guidelines htm respectively | -1 | +2` - NOT EXPLAINED
- fda-guidance-container-closure-systems-1999.pdf Table 1 Degree of Concern Associated with the… (table_row): `-degree concern associated with likelihood packaging component interaction high medium low` - NOT EXPLAINED
- fda-guidance-container-closure-systems-1999.pdf Table 1 Highest (table_row): `-suspensions a` - NOT EXPLAINED
- fda-guidance-container-closure-systems-1999.pdf Table 2 Route of Administration/ Dosage Form (table_row): `-delivery` - NOT EXPLAINED
- fda-guidance-container-closure-systems-1999.pdf Table 2 Oral Tablets and Oral (Hard and Soft… (table_row): `-capsules` - NOT EXPLAINED
- fda-guidance-container-closure-systems-1999.pdf page 4 (uncovered): `+guidance for industry 1 container closure systems for packaging human drugs and biologics chemistry manufacturing and controls documentation i introduction this document is intended to provide guidance on general principles for submitting information` - NOT EXPLAINED
- fda-guidance-deg-eg-high-risk-components-2023.pdf _unnumbered:1 (unnumbered): `+i` - NOT EXPLAINED
- fda-guidance-deg-eg-high-risk-components-2023.pdf _unnumbered:2 (unnumbered): `+table of contents i introduction 1 ii background 2 iii regulatory requirements 3 iv recommendations to safeguard the quality and safety of medicines from deg and eg contamination 6` - NOT EXPLAINED
- fda-guidance-deg-eg-high-risk-components-2023.pdf I (clause): `+1` - NOT EXPLAINED
- fda-guidance-delaying-denying-inspection-2024.pdf _unnumbered:2 (unnumbered): `-this guidance represents the current thinking of the food and drug administration fda or agency on this topic it does not establish any rights for any person and is not binding on fda or the public you can use an alternative approach if it satisfies the requirements of the applicable statutes and r` - NOT EXPLAINED
- fda-guidance-delaying-denying-inspection-2024.pdf II (clause): `+6` - NOT EXPLAINED
- fda-guidance-dissolution-mechanical-calibration-2010.pdf _unnumbered:1 (unnumbered): `-guidance for industry | -guidance for industry | +the use of mechanical calibration` - NOT EXPLAINED
- fda-guidance-dissolution-mechanical-calibration-2010.pdf _unnumbered:2 (unnumbered): `-guidance for industry | +ii background 2 iii recommendations 3 the use of mechanical calibration` - NOT EXPLAINED
- fda-guidance-dissolution-mechanical-calibration-2010.pdf II (clause): `-2005,3 | +2005 3` - NOT EXPLAINED
- fda-guidance-elemental-impurities-2018.pdf _unnumbered:1 (unnumbered): `-9073135 fnl 8 1 2018 | +i` - NOT EXPLAINED
- fda-guidance-elemental-impurities-2018.pdf _unnumbered:2 (unnumbered): `+table of contents i introduction 1 ii background 2 a ich q 3 d 2 b usp general chapters < 232 > and < 233 > 2 iii implementation 3 a new compendial nda or anda drug products 4 b new noncompendial nda and anda drug products 4 c compendial drug products not approved under an nda or anda 4 d noncompen` - NOT EXPLAINED
- fda-guidance-elemental-impurities-2018.pdf I (clause): `+1 | +6` - NOT EXPLAINED
- fda-guidance-field-alert-report-qa-2021.pdf _unnumbered:1 (unnumbered): `+i` - NOT EXPLAINED
- fda-guidance-field-alert-report-qa-2021.pdf _unnumbered:2 (unnumbered): `+table of contents i introduction 1 ii background 1 iii questions and answers 2 1 what is a far and what triggers its submission 2 2 who is responsible for submitting the far 6 3 when should i submit a far 6 4 how do i submit a far 7 5 where do i submit a far 8 6 should i submit a follow up or final` - NOT EXPLAINED
- fda-guidance-field-alert-report-qa-2021.pdf III.1.b (clause): `+13` - NOT EXPLAINED
- fda-guidance-melamine-components-2009.pdf _unnumbered:1 (unnumbered): `+pharmaceutical components | +pharmaceutical components` - NOT EXPLAINED
- fda-guidance-melamine-components-2009.pdf _unnumbered:2 (unnumbered): `-1 | +pharmaceutical components` - NOT EXPLAINED
- fda-guidance-methanol-testing-alcohol-2023.pdf II (clause): `+19` - NOT EXPLAINED
- fda-guidance-methanol-testing-alcohol-2023.pdf III.A (clause): `+34` - NOT EXPLAINED
- fda-guidance-nitrosamine-control-2024.pdf _unnumbered:1 (unnumbered): `+i` - NOT EXPLAINED
- fda-guidance-nitrosamine-control-2024.pdf _unnumbered:2 (unnumbered): `-control of nitrosamine impurities in human drugs guidance for industry 1 this guidance represents the current thinking of the food and drug administration fda or agency on this topic it does not establish any rights for any person and is not binding on fda or the public you can use an alternative a` - NOT EXPLAINED
- fda-guidance-nitrosamine-control-2024.pdf III.A (clause): `-1 hno | -n n o x n n o n o r 2 r 2` - NOT EXPLAINED
- fda-guidance-nitrosamine-control-2024.pdf III.A.2 (clause): `+api | -n h api n n o n o` - NOT EXPLAINED
- fda-guidance-nitrosamine-control-2024.pdf V.A (clause): `+68` - NOT EXPLAINED
- fda-guidance-nitrosamine-control-2024.pdf V.C.2 (clause): `+82` - NOT EXPLAINED
- fda-guidance-nitrosamine-control-2024.pdf _unnumbered:3 (unnumbered): `-ity | +voluntarily recall ranitidine and nizatidine products with ndma levels above those fda calculated using the methods in the international council for harmonisation of technical requirements for pharmaceuticals for human use guidance for industry m 7 r 2 assessment and control of dna reactive ` - NOT EXPLAINED
- fda-guidance-nitrosamine-control-2024.pdf Table 2 𝑛𝑛𝑖𝑖=2 𝑋𝑋𝑋𝑋 (table_row): `-nnii xxxx` - NOT EXPLAINED
- fda-guidance-nitrosamine-control-2024.pdf Table 2 ∑ 𝐴𝐴𝐴𝐴𝐴𝐴 ∗ 100% ≤ 100% (table_row): `-aaaaaa` - NOT EXPLAINED
- fda-guidance-nitrosamine-ndsri-ai-limits-2023.pdf III.A (clause): `+20` - NOT EXPLAINED
- fda-guidance-nitrosamine-ndsri-ai-limits-2023.pdf IV.A (clause): `+23` - NOT EXPLAINED
- fda-guidance-nitrosamine-ndsri-ai-limits-2023.pdf Appendix A (clause): `-potency score α hydrogen score deactivating feature score sum all scores for features present in ndsri activating feature score sum all scores for features present in ndsri | +count of hydrogen atoms on each α carbon lowest first example α hydrogen score 0,2 3 0,3 2 1,2 3 1,3 3 2,2 1 potency score ` - NOT EXPLAINED
- fda-guidance-npbl-cross-contamination-2013.pdf _unnumbered:1 (unnumbered): `-guidance for industry | -guidance for industry` - NOT EXPLAINED
- fda-guidance-npbl-cross-contamination-2013.pdf _unnumbered:2 (unnumbered): `-guidance for industry | +introduction | +ii background 2 iii recommendations 7 i` - NOT EXPLAINED
- fda-guidance-npbl-cross-contamination-2013.pdf II.A (clause): `+4` - NOT EXPLAINED
- fda-guidance-part11-scope-application-2003.pdf _unnumbered:1 (unnumbered): `-guidance for industry | -2003 | -guidance for industry | -2003` - NOT EXPLAINED
- fda-guidance-part11-scope-application-2003.pdf _unnumbered:2 (unnumbered): `-guidance for industry 1 part 11 electronic records electronic signatures scope and application 4 5 6 | -13 14 15` - NOT EXPLAINED
- fda-guidance-part11-scope-application-2003.pdf I (clause): `-i introduction 17 this guidance is intended to describe the food and drug administration s fda s current thinking regarding the scope and application of part 11 of title 21 of the code of federal regulations electronic records electronic signatures 21 cfr part 11 2 21 | -32 | +1 | -43 | -48 | -51 |` - NOT EXPLAINED
- fda-guidance-part11-scope-application-2003.pdf II (clause): `-60 | -67 | -83 | -91 | -104 | -110 111` - NOT EXPLAINED
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
- fda-guidance-part11-scope-application-2003.pdf IV (clause): `-321 | -323 | -327 | -331 | -335 | -339 340 | -342 | -345 | -348` - NOT EXPLAINED
- fda-guidance-part11-scope-application-2003.pdf page 4 (uncovered): `+i introduction this guidance is intended to describe the food and drug administration s fda s current thinking regarding the scope and application of part 11 of title 21 of the code of federal regulations electronic records electronic signatures 21 cfr part 11` - NOT EXPLAINED
- fda-guidance-product-recalls-2020.pdf II (clause): `-o | -o | -o | -o | -o | -o | -o | -o | -o | -o | -o | -o | -o | -o | -o | -o | -o | -o | -o | -o | -o | -o o | -o | -o | -o | -o | -o | -o | -o | -o | -o | -o | -o | -o | -o | -o | -o | -o | -o | -o | -o | -o | -o | -o | -o | -o | -o | -o | -o | -o | -o | -o | -o | -o | -o | -o | -o | -o | -o | -o ` - NOT EXPLAINED
- fda-guidance-pyrogen-endotoxins-qa-2026.pdf _unnumbered:1 (unnumbered): `+i` - NOT EXPLAINED
- fda-guidance-pyrogen-endotoxins-qa-2026.pdf _unnumbered:2 (unnumbered): `-guidance for industry 1 pyrogen and endotoxins testing questions and answers edition 2` - NOT EXPLAINED
- fda-guidance-pyrogen-endotoxins-qa-2026.pdf III.6 (clause): `+25` - NOT EXPLAINED
- fda-guidance-quality-agreements-2016.pdf _unnumbered:1 (unnumbered): `+i` - NOT EXPLAINED
- fda-guidance-quality-agreements-2016.pdf _unnumbered:2 (unnumbered): `+table of contents i introduction 1 ii defining the who and what of contract manufacturing 2 iii responsibilities of parties involved in contract manufacturing 3 iv documenting cgmp activities in quality agreements 5 a what is a quality agreement 6 b elements of a quality agreement 6 1 manufacturing` - NOT EXPLAINED
- fda-guidance-quality-agreements-2016.pdf II (clause): `+2` - NOT EXPLAINED
- fda-guidance-quality-systems-approach-2006.pdf II.B (clause): `+3` - NOT EXPLAINED
- fda-guidance-quality-systems-approach-2006.pdf III.G (clause): `+8` - NOT EXPLAINED
- fda-guidance-quality-systems-approach-2006.pdf IV.A.3 (clause): `+quality standard that will be followed the | -the quality standard that will be followed` - NOT EXPLAINED
- fda-guidance-quality-systems-approach-2006.pdf IV.B.3 (clause): `+21 cfr cgmp regulations related to resources quality system element regulatory citation quality system element regulatory citation quality system element regulatory citation quality system element regulatory citation 1 general arrangements qualifications 211.25 a 2 develop personnel staff training ` - NOT EXPLAINED
- fda-guidance-quality-systems-approach-2006.pdf IV.B.4 (clause): `-see reference 4` - NOT EXPLAINED
- fda-guidance-quality-systems-approach-2006.pdf IV.C.1 (clause): `+resources and facilities used` - NOT EXPLAINED
- fda-guidance-quality-systems-approach-2006.pdf IV.C.3 (clause): `+17` - NOT EXPLAINED
- fda-guidance-quality-systems-approach-2006.pdf Table 1 row 1 (table_row): `-system element` - NOT EXPLAINED
- fda-guidance-quality-systems-approach-2006.pdf Table 2 3. Facilities and Equipment (table_row): `-3 and buildings and 211.28 c` - NOT EXPLAINED
- fda-guidance-quality-systems-approach-2006.pdf Table 4 Quality System Element (table_row): `-element regulatory citation` - NOT EXPLAINED
- fda-guidance-quality-systems-approach-2006.pdf Table 4 1. Design and Develop Product and… (table_row): `-develop` - NOT EXPLAINED
- fda-guidance-quality-systems-approach-2006.pdf Table 4 2. Examine Inputs (table_row): `-211.122 211.125` - NOT EXPLAINED
- fda-guidance-quality-systems-approach-2006.pdf Table 5 1. Analyze Data for Trends (table_row): `-data for trends` - NOT EXPLAINED
- fda-guidance-quality-systems-approach-2006.pdf Table 5 3. Risk Assessment (table_row): `-3` - NOT EXPLAINED
- fda-guidance-remote-regulatory-assessments-2025.pdf _unnumbered:2 (unnumbered): `-this guidance represents the current thinking of the food and drug administration fda or agency on this topic it does not establish any rights for any person and is not binding on fda or the public you can use an alternative approach if it satisfies the requirements of the applicable statutes and r` - NOT EXPLAINED
- fda-guidance-remote-regulatory-assessments-2025.pdf III.A.7 (clause): `+19` - NOT EXPLAINED
- fda-guidance-remote-regulatory-assessments-2025.pdf III.C (clause): `-33 | +34` - NOT EXPLAINED
- fda-guidance-sterilization-validation-submission-1994.pdf I.A (clause): `-1 this guidance has been prepared by the sterility technical committee of the chemistry manufacturing controls coordinating committee of the center for drug evaluation and research cder and the center for veterinary medicine cvm at the food and drug administration although this guidance does not cr` - NOT EXPLAINED
- fda-guidance-sterilization-validation-submission-1994.pdf II.A.3 (clause): `-fo | +f` - NOT EXPLAINED
- fda-guidance-sterilization-validation-submission-1994.pdf II.C (clause): `+or −` - NOT EXPLAINED
- fda-guidance-sterilization-validation-submission-1994.pdf page 4 (uncovered): `+2 the packaging of the product 10 3 multiple dose mapping studies 10 4 microbiological methods and controls 11 5 monitoring stability 11 iv information for aseptic fill manufacturing processes which should be included in drug applications 11 a buildings and facilities 11 1 floor plan 11 2 location ` - NOT EXPLAINED
- fda-guidance-sterilization-validation-submission-1994.pdf page 5 (uncovered): `+g container closure and package integrity 15 h sterility testing methods and release criteria 16 i bacterial endotoxins test and method 16 j evidence of formal written procedures 16 v maintenance of microbiological control and quality stability considerations 16 a container closure integrity 16 b p` - NOT EXPLAINED
- fda-guidance-sterilization-validation-submission-1994.pdf page 6 (uncovered): `+this guidance has been prepared by the sterility technical committee of th e` - NOT EXPLAINED
- fda-guidance-sterilization-validation-submission-1994.pdf page 6 (uncovered): `+chemistry manufacturing controls coordinating committee of the center for dru g evaluation and research cder and the center for veterinary medicine cvm at the food and drug administration although this guidance does not create or confer an y rights for or on any person and does not operate to bind ` - NOT EXPLAINED
- fda-guidance-voluntary-recalls-initiation-2022.pdf _unnumbered:2 (unnumbered): `-this guidance represents the current thinking of the u s food and drug administration fda we or agency on this topic it does not establish any rights for any person and is not binding on fda or the public you can use an alternative approach if it satisfies the requirements of the applicable statute` - NOT EXPLAINED
- fda-guidance-voluntary-recalls-initiation-2022.pdf I (clause): `+1` - NOT EXPLAINED
- fda-guidance-voluntary-recalls-initiation-2022.pdf III.A.1 (clause): `+23` - NOT EXPLAINED
- fda-guidance-voluntary-recalls-initiation-2022.pdf III.B (clause): `+28 | +29` - NOT EXPLAINED
- fda-guidance-voluntary-recalls-initiation-2022.pdf III.D (clause): `-how | +where necessary follow up communication should occur for any direct account that fails to respond to a recall communication to ensure the direct account has received and understands the recall communication see 21 cfr 7.49 c 2 d h ow` - NOT EXPLAINED
- fda-oos-2022.pdf _unnumbered:1 (unnumbered): `+i` - NOT EXPLAINED
- fda-oos-2022.pdf _unnumbered:2 (unnumbered): `+table of contents i introduction 1 ii background 2 iii identifying and assessing oos test results phase i laboratory investigation 3 a responsibility of the analyst 3 b responsibilities of the laboratory supervisor 4 iv investigating oos test results phase ii full scale oos investigation 6 a review` - NOT EXPLAINED
- fda-oos-2022.pdf V.C (clause): `+20` - NOT EXPLAINED
- ich-m7-r2.pdf 1 (clause): `-introduction | +scope scenarios for application of the ich m 7 guideline 23 appendix 2 case examples to illustrate potential control approaches 24 appendix 3 list of compounds in ich m 7 addendum 27 ich m 7 addendum separate document a ssessment and c ontrol of dna r eactive m utagenic i mpurities ` - NOT EXPLAINED
- ich-m7-r2.pdf 2 (clause): `-2 scope of guideline` - NOT EXPLAINED
- ich-m7-r2.pdf 3 (clause): `-3 general principles | +−` - NOT EXPLAINED
- ich-m7-r2.pdf 4 (clause): `-4 considerations | -this guideline is not intended to be applied retrospectively i e to products marketed prior to adoption of this guideline however some types of post approval changes warrant a reassessment of safety relative to mutagenic impurities this section applies to these post approval cha` - NOT EXPLAINED
- ich-m7-r2.pdf 5 (clause): `-5 drug substance and drug product impurity assessment` - NOT EXPLAINED
- ich-m7-r2.pdf 6 (clause): `-6 hazard assessment elements` - NOT EXPLAINED
- ich-m7-r2.pdf 7 (clause): `-risk characterization as a result of hazard assessment described in section 6 each impurity will be assigned to one of the five classes in table 1 for impurities belonging in classes 1 2 and 3 the principles of risk characterization used to derive acceptable intakes are described in this section` - NOT EXPLAINED
- ich-m7-r2.pdf 7.3.1 (clause): `+− | +−` - NOT EXPLAINED
- ich-m7-r2.pdf 8 (clause): `-control a control strategy is a planned set of controls derived from current product and process understanding that assures process performance and product quality ich q 10 ref 8 a control strategy can include but is not limited to the following controls on material attributes including raw materia` - NOT EXPLAINED
- ich-m7-r2.pdf 9.2 (clause): `+− | +− | +− | +−` - NOT EXPLAINED
- ich-m7-r2.pdf Appendix 3 (section): `-route specific limit` - NOT EXPLAINED
- ich-q10.pdf _unnumbered:1 (unnumbered): `-pharmaceutical quality system | +q 10 approval by the steering committee under step 4 and recommendation for adoption to the three ich regulatory bodies 4 june i p harmaceutical q uality s ystem` - NOT EXPLAINED
- ich-q10.pdf Table 2 Q10 (table_row): `-2008` - NOT EXPLAINED
- ich-q11-qa-pmda.pdf _unnumbered:1 (unnumbered): `-implementation working group ich q 11 guideline development and manufacture of drug substances chemical entities and biotechnological biological entities questions and answers version 23 august 2017 | +implementation working group ich q 11 guideline development and manufacture of drug substances ch` - NOT EXPLAINED
- ich-q11-qa-pmda.pdf _unnumbered:2 (unnumbered): `-ii | +iii` - NOT EXPLAINED
- ich-q11-qa-pmda.pdf 12 (clause): `-iii` - NOT EXPLAINED
- ich-q12.pdf 2 (clause): `+for reporting according to risk the mah may propose reporting categories for changes to ecs based on risk and knowledge gained through enhanced pharmaceutical development a system with risk based reporting categories also facilitates the use of post approval change management protocols which provid` - NOT EXPLAINED
- ich-q12.pdf 3 (clause): `-established conditions ecs` - NOT EXPLAINED
- ich-q12.pdf 4 (clause): `-change management protocol pacmp` - NOT EXPLAINED
- ich-q12.pdf 6 (clause): `-and change management` - NOT EXPLAINED
- ich-q12.pdf 7 (clause): `-regulatory assessment and inspection regulatory assessment and inspection are complementary activities and their fundamental roles remain unchanged by this guideline nevertheless effective communication between assessors and inspectors can facilitate regulatory oversight of product lifecycle | +kno` - NOT EXPLAINED
- ich-q12.pdf 9 (clause): `-9 stability data approaches to support the evaluation of cmc changes` - NOT EXPLAINED
- ich-q12.pdf Appendix 1 (section): `+q as from training sessions q 8 q 9 q 10 points to consider a ppendix` - NOT EXPLAINED
- ich-q12.pdf Appendix 2 (section): `-appendix 2 principles of change management` - NOT EXPLAINED
- ich-q12.pdf Table 4 row 1 (table_row): `-source of materials e g cell and seed source raw materials and control of critical materials of biological origin generation and control of master working cell bank master working seed lot etc applicable to biotechnological biological products` - NOT EXPLAINED
- ich-q12.pdf Table 4 3.2.P.3 (table_row): `-3.2 p 3 manufacture` - NOT EXPLAINED
- ich-q1a-r2.pdf _unnumbered:1 (unnumbered): `-cover note | +q 1 a r 2 approval by the steering committee of the second revision directly under step 4 without further public consultation to include consequences of the adoption of q 1 f stability data package | -revision | +registration applications in climatic zones iii and iv and recommendatio` - NOT EXPLAINED
- ich-q1a-r2.pdf Table 2 Q1A(R2) (table_row): `-2003` - NOT EXPLAINED
- ich-q1a-r2.pdf page 7 (uncovered): `+s tability t esting of n ew d rug s ubstances and p roducts` - NOT EXPLAINED
- ich-q1b.pdf _unnumbered:1 (unnumbered): `-stability testing photostability testing | +q 1 b approval by the steering committee under step 4 and recommendation for adoption to the three ich regulatory bodies 6 november 1996 q 1 b s tability t esting p hotostability t esting` - NOT EXPLAINED
- ich-q1b.pdf 3 (clause): `-3 drug product` - NOT EXPLAINED
- ich-q1b.pdf page 9 (uncovered): `+3 d rug p roduct` - NOT EXPLAINED
- ich-q1d.pdf _unnumbered:1 (unnumbered): `-bracketing | +q 1 d approval by the steering committee under step 4 | -matrixing designs | +recommendation | -stability testing | +adoption to the three ich regulatory bodies 7 february 2002 q 1 d b racketing and m atrixing d esigns for s tability t esting` - NOT EXPLAINED
- ich-q1d.pdf Table 3 Container size (table_row): `-15` - NOT EXPLAINED
- ich-q1e.pdf Appendix A (section): `-evaluation of stability data` - NOT EXPLAINED
- ich-q1e.pdf Appendix A #2 (section): `+significant change at accelerated condition within 3 months yes no | -tabulate and or plot | -stability data on all | -attributes at all storage yes | +show variability tabulate and or plot stability data on all attributes at all storage conditions and evaluate | -3 | +6 | -significant significant ` - NOT EXPLAINED
- ich-q1e.pdf Appendix B 8 (clause): `+80 85 90 95 100 105 110 115 | -115 assay % of label claim 110 105 raw data 100 upper confidence limit 95 lower confidence limit regression line 90 upper acceptance 85 criterion 105 lower acceptance 80 criterion 95 | +a s s a y % o f l a b e l c l a i m raw data upper confidence limit lower confiden` - NOT EXPLAINED
- ich-q1e.pdf page 5 (uncovered): `+e valuation of s tability d ata` - NOT EXPLAINED
- ich-q2-r2.pdf _unnumbered:1 (unnumbered): `+i` - NOT EXPLAINED
- ich-q2-r2.pdf 5 (clause): `-2 | +1` - NOT EXPLAINED
- ich-q2-r2.pdf 7 (clause): `-table 4 example for elemental impurities by icp oes or icp ms table 5 example for dissolution with hplc as product performance test for an immediate release dosage form table 6 example for quantitative 1 h nmr for the assay of a drug substance table 7 example for biological assays table 8 example f` - NOT EXPLAINED
- ich-q2-r2.pdf Table 5 Robustness and (table_row): `-stability test conditions sample digestion technique preparation nebulizer sheath flow settings plasma settings` - NOT EXPLAINED
- ich-q2-r2.pdf Table 6 (performed as (table_row): `-surfactant concentration use` - NOT EXPLAINED
- ich-q2-r2.pdf Table 6 part of (table_row): `-sinkers ph deaeration volume` - NOT EXPLAINED
- ich-q2-r2.pdf Table 7 Robustness and (table_row): `-e g temperature concentration field shim tuning matching nmr probe solution stability` - NOT EXPLAINED
- ich-q2-r2.pdf Table 8 Robustness and (table_row): `-plate type buffer components incubation times incubation conditions instruments reaction times reagent lots including controls for binding assay procedures coating proteins capture detection antibody for cell based assay procedures cell density effector target cell ratio cell generation number` - NOT EXPLAINED
- ich-q2-r2.pdf Table 9 considerations (table_row): `-equipment master mix composition concentrations of salts` - NOT EXPLAINED
- ich-q2-r2.pdf Table 9 (performed as part of (table_row): `-dntps adjuvants master mix lots reaction volume probe and` - NOT EXPLAINED
- ich-q2-r2.pdf Table 9 analytical procedure (table_row): `-primer concentrations thermal cycling parameters` - NOT EXPLAINED
- ich-q2-r2.pdf Table 10 other (table_row): `-evaluation expected size ranges for the intended use the analytical` - NOT EXPLAINED
- ich-q2-r2.pdf Table 10 of analytical (table_row): `-dispersion stability for liquid dispersions stability over potential` - NOT EXPLAINED
- ich-q2-r2.pdf Table 10 procedure (table_row): `-analysis time stir rate dispersion energy equilibration or stir time` - NOT EXPLAINED
- ich-q2-r2.pdf Table 10 development as (table_row): `-before measurement` - NOT EXPLAINED
- ich-q2-r2.pdf Table 11 other (table_row): `-chemical and physical factors that can impact nir spectrum and` - NOT EXPLAINED
- ich-q2-r2.pdf Table 11 considerations (table_row): `-model prediction should be represented in data sets examples include` - NOT EXPLAINED
- ich-q2-r2.pdf Table 11 (performed as part (table_row): `-various sources of drug substance and excipients water content tablet` - NOT EXPLAINED
- ich-q2-r2.pdf Table 11 of analytical (table_row): `-hardness and orientation in the holder` - NOT EXPLAINED
- ich-q2-r2.pdf Table 11 development as (table_row): `-note nir measurements are sensitive to changes in tablet composition` - NOT EXPLAINED
- ich-q2-r2.pdf Table 11 per ICH Q14) (table_row): `-and properties outside variation present in the calibration set` - NOT EXPLAINED
- ich-q2-r2.pdf Table 12 other (table_row): `-lc flow rate lc injection volume ms drying desolvation temperature` - NOT EXPLAINED
- ich-q3a-r2.pdf _unnumbered:1 (unnumbered): `-impurities in new drug substances | +q 3 a r 2 approval by the steering committee of the revision of the attachment 2 directly under step 4 without further public consultation 25 october q 3 a r 2 i mpurities i n n ew d rug s ubstances` - NOT EXPLAINED
- ich-q3a-r2.pdf 3 #2 (clause): `+no yes structure identified | -any | +no greater than qualification threshold c | -known human yes reduce to structure relevant risksd identified safe level no no | -yes | +≤ qualification threshold c | -thresholdc yes no | +≤ identification threshold c | -greater than | +reduce to safe level | -≤ ` - NOT EXPLAINED
- ich-q3a-r2.pdf Table 2 Q3A(R2) (table_row): `-2006` - NOT EXPLAINED
- ich-q3a-r2.pdf Table 5 “Raw” Result (%) (table_row): `-1.0` - NOT EXPLAINED
- ich-q3b-r2.pdf _unnumbered:1 (unnumbered): `-impurities | +q 3 b r 2 approval by the steering committee of the revision of the attachment 2 directly under step 4 without further public consultation 2 june q 3 b r 2 i mpurities` - NOT EXPLAINED
- ich-q3b-r2.pdf Glossary (section): `-0 0 r ep o rtin g id en tific atio n percentage of drug substance q u alificatio n 0 8 0 0 6 0 0 4 0 0 2 0 0 0 0 | +0.00 0.20 0.40 0.60 0.80 1.00 | -m ax im u m d aily d o se | +maximum daily dose expressed in mg of drug substance p | -x p ressed in m | +r c e n t a | +reporting identification qual` - NOT EXPLAINED
- ich-q3b-r2.pdf Table 2 Q3B(R2) (table_row): `-2006` - NOT EXPLAINED
- ich-q3c-r9.pdf Part I 3.3 (clause): `+c on ce n t r a ti on pp m | -pde concentration ppm | +p d e do s e` - NOT EXPLAINED
- ich-q3c-r9.pdf Part I Appendix 1 (section): `-cl` - NOT EXPLAINED
- ich-q3c-r9.pdf Part I Appendix 1 2 (clause): `+1,4 dioxane | -o o 1,4 dioxane` - NOT EXPLAINED
- ich-q3c-r9.pdf Part I Appendix 1 3 (clause): `-class 2 n o | +o class | +methyltetrahydrofuran 4 2 | +tetrahydrosylvan | -methyltetrahydrofuran 4 tetrahydrosylvan | +dioxide s | -dioxide s o o | +oxacyclopentane o | -o oxacyclopentane` - NOT EXPLAINED
- ich-q3c-r9.pdf Part I Appendix 1 5 (clause): `+xylol ch 3 | -ch 3 xylol` - NOT EXPLAINED
- ich-q3c-r9.pdf Part I Appendix 3 (section): `+pde | -pde 1 | +pde | -pde 4.22 mg day − 1 | +1 4.22 mg day − 1 − 1 − | +v | -− 6 atm | +a t m | -mg mol − 1 46.15 mg − 1 − 1 1.89 mg | +m g m o | -v rt 0.082 | -24.45 | +46 15 m g 24 45 | +1 89 m g l 6 1 1 1 0082` - NOT EXPLAINED
- ich-q3c-r9.pdf Part II (section): `-200 x 72.10 200 ppm 589.8 mg | +pp | -3 0.59 mg l 24.45 0.59 x 6 x 5 for continuous dosing 0.105 mg l 24 | +720 m g d ay 7 2 10 1000 | -0.105 x 290 daily dose 71.65 mg kg 0.425 71.65 x 50 pde 7.165 mg day 7.2 mg day 5 | +2 l i m it m g d a y 7 165 1 | +5 50 x 71 65 m g kg 65` - NOT EXPLAINED
- ich-q3c-r9.pdf Part II 7.2 (clause): `-1000 limit 720 ppm | +7 2 l i m it m g d a y 7 165 1 x | +x 1 x 10 x 5 50 x 71 65 m g kg 65 1 7 0 425 290 x 0 105 do s e d a il y m g l 0 105 7 x 24 5 x 6 x 0 59 do s i ng c on ti nuou s f o r m g l 59 0 m g m 8 89 5 24 45 72 10 x 200 pp m 200 3` - NOT EXPLAINED
- ich-q3c-r9.pdf Part III (section): `-part iii impurities residual solvents maintenance pde for n methylpyrrolidone | -150 | +pp m 530 m g d ay 5 3 10 1000 | -99.13 150 ppm 608.16 mg | +5 3 l i | -3 0.608 mg l 24.45 0.608 | +it 5 | -6 for continuous dosing 0.152 mg l 24 0.152 | +5 | -290 daily dose 133.58 mg kg 0.33 133.58 x 50 pde 5.3` - NOT EXPLAINED
- ich-q3c-r9.pdf Part III 5.3 (clause): `-5.3 | -1000 limit 530 ppm | +5 3 l i m it 5 x 5 x 1 x | +x 5 50 x 133 58 m g kg 133 58 0 33 290 x 0 152 do s e d a il y m g l 0 152 24 6 x 0 608 do s i ng c on ti nuou s f o r m g l 608 0 m g m 608 16 24 45 99 13 x 150 pp m 150 3` - NOT EXPLAINED
- ich-q3c-r9.pdf Part IV #2 (section): `-part iv impurities residual solvents maintenance pde for cumene | -250 x 120.19 250 ppm 1229 mg | +m g l 23 1 m g | -1.23 mg | +1229 24 45 120 19 x 250 pp m 250 m g | -24.45 1.23 | +0 22 7 x 24 5 | -5 for continuous dosing 0.22 mg | +1 23 do s i ng c on ti nuou s f o r m g kg d a y 150 kg 0 425 d a` - NOT EXPLAINED
- ich-q3c-r9.pdf Part V (section): `-part v impurities residual solvents maintenance pde for triethylamine and | -247 x 101.19 247 ppm 1022.2 mg | +m g l 022 1 m g | -1.022 | +1022 2 24 45 101 19 x 247 pp m 247 | -24.45 1.022 | +0.183 7 x 24 5 | -5 | +1.022 dosing continuous | -continuous dosing 0.183 mg | +m g kg d a y 124 9 kg 0 425` - NOT EXPLAINED
- ich-q3c-r9.pdf _unnumbered:3 (unnumbered): `-450 x 100.16 450 ppm 1843 mg | +m g l 843 1 m g | -1.843 mg | +1843 24 45 100 16 x 450 pp m 450 m g | -24.45 1.843 | +0 329 7 x 24 5 | -5 for continuous dosing 0.329 mg l 24 x 7 0.329 mg l | -x 290 l day − 1 daily dose 225 | +843 do s i ng c on ti nuou s f o r | +225 kg | -kg | +day l 290 x l mg 0.` - NOT EXPLAINED
- ich-q3c-r9.pdf Part VI (section): `-part vi impurities residual solvents maintenance pde for 2 methyltetrahydrofuran cyclopentyl methyl ether and tertiary butyl alcohol | -250 x 50 pde 50 | +50 1 x 1 x | -1 x 1 | +250 pde` - NOT EXPLAINED
- ich-q3c-r9.pdf Part VI 6 (clause): `-150 x 50 pde 15 mg day 5 x 10 x 10 x 1 x 1` - NOT EXPLAINED
- ich-q3c-r9.pdf _unnumbered:6 (unnumbered): `+mg day 15 1 x 1 x 10 x 10 x 5 50 x 150 pde | -175 x 50 pde 35 mg day 5 x 10 x 1 x 1 x 5 | +mg day 35 5 x 1 x 1 x 10 x 5 50 x 175 pde | -510 x 50 pde 42.5 mg day 12 x 10 x 1 x 1 x 5 | +mg day 42.5 5 x 1 x 1 x 10 x 12 50 x 510 pde` - NOT EXPLAINED
- ich-q3c-r9.pdf page 28 (uncovered): `+part iii i mpurities r esidual s olvents m aintenance pde for n m ethylpyrrolidone` - NOT EXPLAINED
- ich-q3c-r9.pdf page 30 (uncovered): `+part iv i mpurities r esidual s olvents m aintenance pde for c umene` - NOT EXPLAINED
- ich-q3c-r9.pdf page 34 (uncovered): `+part v i mpurities r esidual s olvents m aintenance pde for t riethylamine and` - NOT EXPLAINED
- ich-q3c-r9.pdf page 41 (uncovered): `+part vi i mpurities r esidual s olvents m aintenance pde for 2 m ethyltetrahydrofuran c yclopentyl m ethyl e ther and t ertiary b utyl a lcohol` - NOT EXPLAINED
- ich-q3d-r2.pdf Appendix 5 1 (clause): `+2 2 scope 2 3 safety assessment of potential elemental impurities 2 3.1 principles of the safety assessment of elemental impurities for oral parenteral and inhalation routes of administration 2 3.2 other routes of administration 3 3.3 justification for elemental impurity levels higher than an estab` - NOT EXPLAINED
- ich-q3d-r2.pdf Appendix 5 2 (clause): `+2 3 safety assessment of potential elemental impurities 2 3.1 principles of the safety assessment of elemental impurities for oral parenteral and inhalation routes of administration 2 3.2 other routes of administration 3 3.3 justification for elemental impurity levels higher than an established pde` - NOT EXPLAINED
- ich-q3d-r2.pdf Appendix 5 4 (clause): `+days this | -classification | +is an impurity in an oral drug product administered once every 3 weeks 5 half lives using first order kinetics the established pde of 1000 μg day is modified as follows proposed level 0.02 mg kg d x 50 kg 1 3.16 3.16 mg day for practical purposes this value is rounded` - NOT EXPLAINED
- ich-q3d-r2.pdf Appendix 5 5 (clause): `-5 risk assessment and control | +and routes of administration the outcome of the risk assessment will determine those components that may require additional controls which may in some cases include testing for class 1 elements it is not expected that all components will require testing for class 1 ` - NOT EXPLAINED
- ich-q3d-r2.pdf Appendix 5 5.2 (clause): `-manufacturing drug equipment substance elemental impurities in drug product water container excipients closure system` - NOT EXPLAINED
- ich-q3d-r2.pdf Appendix 5 5.3 (clause): `+elemental impurities in drug product container closure system drug substance excipients manufacturing equipment water` - NOT EXPLAINED
- ich-q3d-r2.pdf Appendix 5 6 (clause): `-6 control | -control of elemental impurities is one part of the overall control strategy for a drug product that assures that elemental impurities do not exceed the pdes when the level of an elemental impurity may exceed the control threshold additional measures should be implemented to assure that` - NOT EXPLAINED
- ich-q3d-r2.pdf Appendix 5 7 (clause): `+day g product drug of amount daily day g | -day | +g ion | -ion g g | -daily amount of drug product g day | -pde g day c | +1 k k | -k | +c day g pde | -k 1` - NOT EXPLAINED
- ich-q3d-r2.pdf Appendix 5 10 (clause): `-lifecycle management the quality systems and management responsibilities described in ich q 10 are intended to encourage the use of science based and risk based approaches at each lifecycle stage thereby promoting continual improvement across the entire product lifecycle product and process knowled` - NOT EXPLAINED
- ich-q3d-r2.pdf Appendix 5 Glossary (section): `+−` - NOT EXPLAINED
- ich-q3d-r2.pdf _unnumbered:14 (unnumbered): `+− | +−` - NOT EXPLAINED
- ich-q3d-r2.pdf Table 1 Q3D #3 (table_row): `-2013` - NOT EXPLAINED
- ich-q3d-r2.pdf Table 28 header (table_header): `-maximum permitted concentration μg g` - NOT EXPLAINED
- ich-q3d-r2.pdf Table 29 header (table_header): `-maximum permitted concentration μg g` - NOT EXPLAINED
- ich-q3d-r2.pdf Table 30 Component (table_row): `-component concentration μg` - NOT EXPLAINED
- ich-q3d-r2.pdf Table 31 Component (table_row): `-component potential concentration μg` - NOT EXPLAINED
- ich-q3d-r2.pdf Table 32 row 1 (table_row): `-daily maximum permitted concentration μg` - NOT EXPLAINED
- ich-q3d-r2.pdf Table 37 3 Pd (table_row): `-3` - NOT EXPLAINED
- ich-q3d-r2.pdf page 5 (uncovered): `+3 s afety a ssessment of p otential e lemental i mpurities` - NOT EXPLAINED
- ich-q3d-r2.pdf page 14 (uncovered): `+6 c ontrol of e lemental i mpurities control of elemental impurities is one part of the overall control strategy for a drug product that assures that elemental impurities do not exceed the pdes when the level of an elemental impurity may exceed the control threshold additional measures should be im` - NOT EXPLAINED
- ich-q3d-r2.pdf page 16 (uncovered): `+10 l ifecycle m anagement the quality systems and management responsibilities described in ich q 10 are intended to encourage the use of science based and risk based approaches at each lifecycle stage thereby promoting continual improvement across the entire product lifecycle product and process kn` - NOT EXPLAINED
- ich-q6a.pdf _unnumbered:1 (unnumbered): `-specifications test procedures | +q 6 a approval by the steering committee under step 4 | -acceptance criteria | +recommendation | -new drug substances | +adoption to the three ich regulatory bodies 6 october q 6 a s pecifications t est p rocedures | -new drug products chemical substances | +a ccep` - NOT EXPLAINED
- ich-q6a.pdf Table 2 Q6A (table_row): `-1999` - NOT EXPLAINED
- ich-q6a.pdf page 5 (uncovered): `+s pecifications t est p rocedures and a cceptance c riteria for n ew d rug s ubstances and n ew d rug p roducts c hemical s ubstances 1 introduction` - NOT EXPLAINED
- ich-q7-qa.pdf _unnumbered:1 (unnumbered): `-q 7 implementation working group ich q 7 guideline good manufacturing practice guide for active pharmaceutical ingredients questions and answers current version dated 10 june 2015 | +q 7 implementation working group ich q 7 guideline good manufacturing practice guide for active pharmaceutical ingre` - NOT EXPLAINED
- ich-q7-qa.pdf _unnumbered:2 (unnumbered): `-i | +ii` - NOT EXPLAINED
- ich-q7-qa.pdf Glossary (section): `-21 annex q as linked to the respective sections of ich q 7` - NOT EXPLAINED
- ich-q7-qa.pdf Table 18 header (table_header): `-questions answers` - NOT EXPLAINED
- ich-q7-qa.pdf Table 19 header (table_header): `-questions answers` - NOT EXPLAINED
- ich-q7-qa.pdf Table 30 row 1 (table_row): `-introduction quality personnel buildings facilities process equipment documentation records 7 8 production process controls 9 packaging identification labelling intermediates storage distribution laboratory controls manufacturers other ich guidelines` - NOT EXPLAINED
- ich-q7-qa.pdf Table 31 row 1 (table_row): `-introduction quality personnel buildings facilities process equipment documentation records 7 8 production process controls 9 packaging identification labelling intermediates storage distribution laboratory controls manufacturers other ich guidelines` - NOT EXPLAINED
- ich-q7.pdf _unnumbered:1 (unnumbered): `-good manufacturing practice guide | +q 7 a approval by the steering committee under step 4 and recommendation | -active pharmaceutical ingredients | +adoption to the three ich regulatory bodies 10 november q 7 i g ood m anufacturing p ractice g uide for a ctive p harmaceutical i ngredients` - NOT EXPLAINED
- ich-q7.pdf 1.3 (clause): `-increasing gmp requirements` - NOT EXPLAINED
- ich-q7.pdf Table 2 Q7A (table_row): `-2000` - NOT EXPLAINED
- ich-q8-q9-q10-qa-r4.pdf _unnumbered:1 (unnumbered): `-table of contents 1 introduction 1` - NOT EXPLAINED
- ich-q8-q9-q10-qa-r4.pdf _unnumbered:2 (unnumbered): `-approved nov 10 2005 | -approved nov 13 2008 | +approved aug 2009 approved nov 10 2005 approved nov 13 2008 | -approved jun 04 2008` - NOT EXPLAINED
- ich-q8-q9-q10-qa-r4.pdf page 7 (uncovered): `+approval questions answers` - NOT EXPLAINED
- ich-q8-q9-q10-qa-r4.pdf page 9 (uncovered): `+approval questions answers` - NOT EXPLAINED
- ich-q8-q9-q10-qa-r4.pdf page 11 (uncovered): `+approval questions answers` - NOT EXPLAINED
- ich-q8-q9-q10-qa-r4.pdf page 12 (uncovered): `+approval questions answers` - NOT EXPLAINED
- ich-q8-q9-q10-qa-r4.pdf page 12 (uncovered): `+approval questions answers` - NOT EXPLAINED
- ich-q8-q9-q10-qa-r4.pdf page 13 (uncovered): `+approval questions answers` - NOT EXPLAINED
- ich-q8-q9-q10-qa-r4.pdf page 15 (uncovered): `+approval questions answers` - NOT EXPLAINED
- ich-q8-q9-q10-qa-r4.pdf page 16 (uncovered): `+approval questions answers` - NOT EXPLAINED
- ich-q8-q9-q10-qa-r4.pdf page 18 (uncovered): `+approval questions answers` - NOT EXPLAINED
- ich-q9r1.pdf _unnumbered:1 (unnumbered): `+i` - NOT EXPLAINED
- ich-q9r1.pdf 4 (clause): `-initiate quality risk management process risk assessment hazard identification risk analysis risk evaluation unacceptable risk management tools risk control risk communication risk reduction risk acceptance output result of the quality risk management process risk review review events` - NOT EXPLAINED
- india-cdsco-circ-2024-03-risk-based-inspection.pdf 12 (clause): `-s` - NOT EXPLAINED
- india-cdsco-circ-2024-03-risk-based-inspection.pdf 3 #2 (clause): `-observations should be descriptive without ambiguity and answer like yes or no should be avoided list of observations deficiencies 1 critical 1.1 1.2 2 major 2.1 2.2 3 others 3.1 3.2 3.3 concluding remarks name and signatures of the inspecting officials established hold time system remarks recommen` - NOT EXPLAINED
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 10 17.3 #2 (table_row): `-18 air handling system central air conditioning` - NOT EXPLAINED
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 11 18.13 (table_row): `-19 environmental monitoring annexe 06` - NOT EXPLAINED
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 12 20.6 (table_row): `-20.6 the made of latex or other suitable plastic material` - NOT EXPLAINED
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 12 20.9 (table_row): `-20.9 used made of plastic or rubber material` - NOT EXPLAINED
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 12 20.1 (table_row): `-does numbered glasses worn inside critical areas have side extensions` - NOT EXPLAINED
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 13 20.2 (table_row): `-21 sanitation who trs 961 annexe 06 how the clean areas are cleaned and sterilized` - NOT EXPLAINED
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 13 21.5 (table_row): `-21.5 quality of water preparation of sanitising solution` - NOT EXPLAINED
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 13 21.10 (table_row): `-21.10 whether any sop exist for purpose fumigation if so mentioned sop nos` - NOT EXPLAINED
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 13 21.1 #4 (table_row): `-22 equipment` - NOT EXPLAINED
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 13 22.6 (table_row): `-22.6 22.7 whether provisions cip or sip available whether pure steams use` - NOT EXPLAINED
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 13 22.9 (table_row): `-22.9 material construction glass containers` - NOT EXPLAINED
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 13 22.2 #3 (table_row): `-23 manufacturing whether calibration status documented and displayed on equipment and gauges` - NOT EXPLAINED
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 13 23.10 (table_row): `-24 aseptic processing and sterilization by filtration annexe 06` - NOT EXPLAINED
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 13 24.6 (table_row): `-25 product containers closures` - NOT EXPLAINED
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 13 25.6 (table_row): `-26 sterilization` - NOT EXPLAINED
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 14 26.10 (table_row): `-26.10 27 by records including thermographs and monitoring slips attached with batch production record` - NOT EXPLAINED
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 14 27.2 (table_row): `-27.2 position temperature probes used for controlling and or recording determined during validation and where applicable been checked against second independent temperature probe located in same position` - NOT EXPLAINED
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 15 27.1 (table_row): `-27.1 28 moist sch m whether the process of intended to remove the pyrogens if so has the validation been done with challenge tests using endo toxins` - NOT EXPLAINED
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 15 28.1 #2 (table_row): `-29 others whether the steam used for sterilization is of suitable quality and doesn t contain additives at a level which could cause contamination of the product or equipment` - NOT EXPLAINED
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 15 29.3 (table_row): `-30 documentation and records` - NOT EXPLAINED
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 15 30.3 (table_row): `-30.3 are approved signed dated by appropriate authorized person` - NOT EXPLAINED
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 17 row 1 (table_row): `-31 labels other printed materials material signature of the competent technical staff responsible for manufacture testing` - NOT EXPLAINED
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 17 31.4 (table_row): `-32 master formula records` - NOT EXPLAINED
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 17 32.1 (table_row): `-32.1 how records for each product are prepared authorized and controlled` - NOT EXPLAINED
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 17 32.4 (table_row): `-33 batch processing manufacturing records` - NOT EXPLAINED
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 17 33.4 (table_row): `-34 packaging records` - NOT EXPLAINED
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 18 34.4 (table_row): `-34.4 how line clearance is performed whether records of line clearance is maintained according to appropriate checklist` - NOT EXPLAINED
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 18 34.16 (table_row): `-35 standard operating procedure and records` - NOT EXPLAINED
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 18 35.1 (table_row): `-35.1 list of mention total number of followed by firm` - NOT EXPLAINED
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 18 36.3 (table_row): `-37 finished product` - NOT EXPLAINED
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 18 37.2 (table_row): `-38 quality control area` - NOT EXPLAINED
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 18 38.1 (table_row): `-38.1 whether area is independent of production area` - NOT EXPLAINED
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 18 38.8 (table_row): `-39 microbiology lab` - NOT EXPLAINED
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 19 39.3 #6 (table_row): `-40 quality control system sch m whether firm has provided microbiology lab for mlt test for nonsterile dosage form if no how this test is complied` - NOT EXPLAINED
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 21 40.2 #6 (table_row): `-retention samples after testing is completed` - NOT EXPLAINED
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 21 40.2 #7 (table_row): `-41 analytical method validation amv specify procedures for safe removal waste from the laboratory` - NOT EXPLAINED
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 22 41.1 (table_row): `-42 hplc calibration` - NOT EXPLAINED
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 22 42.1 (table_row): `-43 dissolution apparatus` - NOT EXPLAINED
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 22 43.1 (table_row): `-44 uv vis` - NOT EXPLAINED
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 22 44.1 (table_row): `-46 ftir` - NOT EXPLAINED
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 22 46.1 (table_row): `-46.1 47 toc analyser parameters verification wave number scale control resolution performance` - NOT EXPLAINED
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 23 row 1 (table_row): `-48 stability studies` - NOT EXPLAINED
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 23 48.1 #2 (table_row): `-49 quality assurance who trs 986 specify the temperature and humidity for real times studies carried out for fixing shelf life of drug in the country` - NOT EXPLAINED
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 24 49.9 (table_row): `-49.9 is production batch record release test results reviewed for accuracy completeness before a batch lot of finished product is released` - NOT EXPLAINED
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 24 49.1 (table_row): `-50 annual product quality review apqr` - NOT EXPLAINED
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 24 51.4 (table_row): `-51.4 52 adverse reactions sch m verify the sop for recall of products clearly defining responsibility procedure reporting reconciliation etc` - NOT EXPLAINED
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 25 52.8 (table_row): `-53 site master file` - NOT EXPLAINED
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 25 53.2 (table_row): `-53.2 quality policy has been included in the site master file` - NOT EXPLAINED
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 25 53.4 (table_row): `-54 validation` - NOT EXPLAINED
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 25 54.2 #4 (table_row): `-55 internal quality gmp audit programme who trs 988 are trend analyses performed to assess the need to re validate in order to assure the processes and procedures continue to obtain the desired results` - NOT EXPLAINED
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 26 55.4 (table_row): `-56 pharmaceutical development` - NOT EXPLAINED
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 26 56.4 (table_row): `-57 risk assessment system` - NOT EXPLAINED
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 26 57.5 (table_row): `-58 data integrity` - NOT EXPLAINED
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 27 58.9 (table_row): `-59 pharmaceutical quality management system pqs` - NOT EXPLAINED
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 29 1.4 (table_row): `-quality rating` - NOT EXPLAINED
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 29 3.2 (table_row): `-quality rating` - NOT EXPLAINED
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 29 4.4 (table_row): `-quality rating` - NOT EXPLAINED
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 29 4.10 (table_row): `-quality rating` - NOT EXPLAINED
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 29 4.17.1 (table_row): `-loop system quality rating` - NOT EXPLAINED
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 29 4.19 (table_row): `-circulation rate` - NOT EXPLAINED
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 29 4.30 (table_row): `-quality rating` - NOT EXPLAINED
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 29 6.6 (table_row): `-quality rating` - NOT EXPLAINED
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 29 8.2 (table_row): `-quality rating` - NOT EXPLAINED
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 29 8.11 (table_row): `-quality rating` - NOT EXPLAINED
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 29 8.21 (table_row): `-quality rating` - NOT EXPLAINED
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 29 8.32 (table_row): `-quality rating` - NOT EXPLAINED
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 29 9.9 (table_row): `-quality rating` - NOT EXPLAINED
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 29 10.6 (table_row): `-quality rating` - NOT EXPLAINED
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 29 11.2 (table_row): `-quality rating` - NOT EXPLAINED
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 29 11.4 (table_row): `-area` - NOT EXPLAINED
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 29 11.5 (table_row): `-3 pressure gradients` - NOT EXPLAINED
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 29 11.8 (table_row): `-quality rating` - NOT EXPLAINED
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 29 12.9 (table_row): `-quality rating` - NOT EXPLAINED
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 29 13.7 (table_row): `-quality rating` - NOT EXPLAINED
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 29 14.5 (table_row): `-quality rating` - NOT EXPLAINED
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 29 14.14 (table_row): `-quality rating` - NOT EXPLAINED
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 29 16.12 (table_row): `-quality rating` - NOT EXPLAINED
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 29 17.6 (table_row): `-quality rating` - NOT EXPLAINED
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 29 17.21 (table_row): `-quality rating` - NOT EXPLAINED
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 29 18.2 (table_row): `-quality rating` - NOT EXPLAINED
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 29 18.11 (table_row): `-quality rating` - NOT EXPLAINED
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 29 19.2 (table_row): `-quality rating` - NOT EXPLAINED
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 29 20.5 (table_row): `-condition` - NOT EXPLAINED
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 29 20.14 (table_row): `-quality rating` - NOT EXPLAINED
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 29 21.6 (table_row): `-quality rating` - NOT EXPLAINED
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 29 21.13 (table_row): `-quality rating` - NOT EXPLAINED
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 29 22.3 (table_row): `-quality rating` - NOT EXPLAINED
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 29 22.8 (table_row): `-quality rating` - NOT EXPLAINED
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 29 22.15 (table_row): `-quality rating` - NOT EXPLAINED
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 29 23.5 (table_row): `-by suitable pipes` - NOT EXPLAINED
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 29 23.6 (table_row): `-quality rating` - NOT EXPLAINED
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 29 24.3 (table_row): `-quality rating` - NOT EXPLAINED
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 29 25.4 (table_row): `-quality rating` - NOT EXPLAINED
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 29 26.6 (table_row): `-quality rating` - NOT EXPLAINED
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 29 27.1 (table_row): `-quality rating` - NOT EXPLAINED
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 29 27.8 (table_row): `-quality rating` - NOT EXPLAINED
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 29 28.4 (table_row): `-quality rating` - NOT EXPLAINED
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 29 28.10 (table_row): `-quality rating` - NOT EXPLAINED
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 29 29. Others sterilization is tested… (table_row): `-29 others` - NOT EXPLAINED
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 29 30.5 (table_row): `-quality rating` - NOT EXPLAINED
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 29 30.9 (table_row): `-30.9 do manufacturing pertaining to manufacture sterile non sterile products indicate following details serial number batch manufacturing record name product reference to master formula record batch lot number batch lot size date commencement completion manufacture date manufacture assigned date ex` - NOT EXPLAINED
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 29 31.2 (table_row): `-quality rating` - NOT EXPLAINED
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 29 34.1 (table_row): `-quality rating` - NOT EXPLAINED
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 29 34.11 (table_row): `-quality rating` - NOT EXPLAINED
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 29 39.3 (table_row): `-quality rating` - NOT EXPLAINED
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 29 39.14 (table_row): `-quality rating` - NOT EXPLAINED
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 29 39.24 (table_row): `-quality rating` - NOT EXPLAINED
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 29 40.3 (table_row): `-quality rating` - NOT EXPLAINED
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 29 40.12 (table_row): `-quality rating` - NOT EXPLAINED
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 29 40.24 (table_row): `-quality rating` - NOT EXPLAINED
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 29 48.3 (table_row): `-quality rating` - NOT EXPLAINED
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 29 49.4 (table_row): `-quality rating` - NOT EXPLAINED
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 29 49.11 (table_row): `-quality rating` - NOT EXPLAINED
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 29 50.3 (table_row): `-relevant equipment utilities` - NOT EXPLAINED
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 29 51.1 (table_row): `-quality rating` - NOT EXPLAINED
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 29 52.7 (table_row): `-quality rating` - NOT EXPLAINED
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 29 54.9 (table_row): `-988 quality rating` - NOT EXPLAINED
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 29 55.4 (table_row): `-rating` - NOT EXPLAINED
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 29 1 and premises: - 56 Building… (table_row): `-56 pharmaceutical development` - NOT EXPLAINED
- india-cdsco-circ-2024-03-risk-based-inspection.pdf Table 29 59.2 (table_row): `-rating` - NOT EXPLAINED
- india-cdsco-circ-2024-03-risk-based-inspection.pdf page 46 (uncovered): `+annexe 06 19 environmental monitoring` - NOT EXPLAINED
- india-cdsco-circ-2024-03-risk-based-inspection.pdf page 51 (uncovered): `+annexe 06 24 aseptic processing and sterilization by filtration` - NOT EXPLAINED
- india-cdsco-circ-2024-03-risk-based-inspection.pdf page 55 (uncovered): `+30.3 sch m whether documents are approved signed and dated by appropriate and authorized person` - NOT EXPLAINED
- india-cdsco-circ-2024-03-risk-based-inspection.pdf page 116 (uncovered): `+the sterilizers are not studied for heat distribution penetration effectiveness of sterilization process not established by using microbial spore indicators` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf Part VII (section): `-73.297 | +73 297` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf Part VII 9 (clause): `-1977,370 | +1977 370 | +436` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf Part XI (section): `-4 lakes the aluminium or calcium salts lakes of any of the water soluble colours listed above 663 provided that in case of disinfectants in addition to the above said colours the colours referred in is 4707 part i as amended by bureau of indian standards from time to time or any of the colours list` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf Part XV (section): `+677 679` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf Part XV 30 (clause): `+xviii | -xviii | +bhasma | +si no dosage form shelf life or date of expiry with effect from the date of manufacture 1 2 3 i curanam kutinir curanam adai curanam kanchi curanam utkali curanam pittu curanam podithimirthal curanam podi 2 years pattru curanam pottanam or kizhi curanam ottratam curanam ` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf Part XV 4 #5 (clause): `+805` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf Part XV 5 #8 (clause): `+1 this licence and` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf Part XV 5 #9 (clause): `-1.896 | +1 896` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf Part XV 5 #10 (clause): `+899` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf Part XV 4 #20 (clause): `-form 28 b see rule 76 966 licence to manufacture for sale or for distribution of drugs specified in schedules c c l and x no of licence 1 is hereby licensed to manufacture at the premises situated at the following drugs specified in schedules c c l and x to the drugs rules 1945 name of drugs 2 name` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf Part XV 5 #18 (clause): `+986` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf Part XV 6 #6 (clause): `-5 raughan 6 ghrita ney 6 zimad` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf Part XV 24 (clause): `-24 jauhar` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf Part XV 25 (clause): `-25 natool` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf Part XV 26 (clause): `-26 nashooq naswar` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf Part XV 27 (clause): `-27 shamoom` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf Part XV 28 (clause): `-28 saoot nasal drops` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf Part XV 29 (clause): `-29 mazoogh 30 tila` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf Part XV 30 #2 (clause): `-lashooq` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf Part XV 31 (clause): `-gulqand` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf Part XV 32 (clause): `-fateela` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf Part XV 33 (clause): `-ghaza ubtan sabhgh` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf Part XV 35 (clause): `-35 capsule` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf Part XV 36 (clause): `-36 huqna` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf Part XV 37 (clause): `-37 naurah` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf Part XV 38 (clause): `-38 latookh` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf Part XV 39 (clause): `-39 vajoor throat pain | +24 jauhar 25 natool 26 nashooq naswar 27 shamoom 28 saoot nasal drops 29 mazoogh 30 tila 31 lashooq 32 gulqand 33 fateela 34 ghaza ubtan sabhgh 35 capsule 36 huqna 37 naurah 38 latookh 39 vajoor throat pain` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf Part XV 3 #28 (clause): `-note sample testing charges shall be determined or revised by the director pharmacopoeia commission for indian medicine and homoeopathy or government analyst of its central laboratory as the case may be in consultation with the ministry of ayurveda yoga and naturopathy unani siddha and homoeopathy ` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf Part XV 3 #30 (clause): `+equipment performance frequency frequency of calibration 1 temperature recorder compare against thermometer daily as often as necessary 2 refrigerated centrifuge observe speed and temperature each day of use as often as necessary 3 hematocrit centrifuge standardize before initial use after repair o` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf Part I 4 #2 (clause): `+− | +−` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf Part I 3 #18 (clause): `+− | +−` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf Part IV 2 (clause): `-chlorthalidone and other derivatives of | -cyclophosphamide its salts 1105 | +2 4 benzothiadiazine chlorpropamide its salts chlorthalidone and other derivatives of chlorobenzene compound 1105 cis platin cyclophosphamide its salts 1105 cytarabine daunorubicin | +glibenclamide hydantoin its salts its` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf Part IV 1 #2 (clause): `+2 abciximab 3 acamprosate calcium 4 acebutol hydrochloride` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf Part IV 2 #2 (clause): `+3 acamprosate calcium 4 acebutol hydrochloride 5 aclarubicin` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf Part IV 3 (clause): `+4 acebutol hydrochloride 5 aclarubicin 6 albendazole` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf Part IV 4 (clause): `-4 acebutol hydrochloride 8 actilyse 9 acyclovir 51 basiliximab 10 adenosine | -11 adrenocorticotrophic hormone | -acth | -12 alendronate sodium | -13 aliopurinol | -14 alphachymotrypsin | -1109 15 | -16 alprostadil | -17 amantadine hydrochloride | -18 amifostine | -19 amikacin sulphate | -hydrochlo` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf Part IV 5 (clause): `-21 cycloserine 37 pentazocine` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf Part IV 6 (clause): `-22 diazepam 38 prulifloxacin` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf Part IV 7 (clause): `-23 diphenoxylate 39 pyrazinamide` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf Part IV 8 (clause): `-24 doripenem 40 rifabutin` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf Part IV 9 #2 (clause): `-25 ertapenem 41 rifampicin` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf Part IV 10 (clause): `-10 cefoperazone 26 ethambutol hydrochloride` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf Part IV 11 (clause): `-27 ethionamide 43 sparfloxacin` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf Part IV 12 (clause): `-28 feropenem 44 tniacetazone` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf Part IV 13 (clause): `-29 gemifloxacin 45 tramadol` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf Part IV 14 (clause): `-14 ceftazidime 30 imipenem` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf Part IV 15 (clause): `-15 ceftibuten 31 lsoniazid` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf Part IV 16 (clause): `-16 ceftizoxime 32 levofloxacin` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf Part IV 99 (clause): `-30 mprovement in size and shape of | -the sexual organ and in duration of | -31 improvement in the strength of the | -32 improvement in vision | -33 jaundice hepatitis liverdisorders | -36 maintenance or improvement of | -capacity of the human being for | -37 mental retardation subnormalities | -42` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf Part III 9.1 (clause): `-dop injection filterintegrity test de contamination by pass duct shut offdamper e s shut vfd offdampe r exhaustai secondaryfi m m m lter vfd velocitysensor v v variable frequencydrive m m m hepafil ter m filter pressuredifferensialgua ge hepabag in bag outunits` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf Part XIII 4 #2 (clause): `-3 when stored at 4 c 8 rabies vaccine 6 in cold place 9 typhoid vaccine 18 in cold place typhoid and para typhoid 10 18 in cold place vaccine typhoid para typhoid a and b 11 18 in cold place vaccine typhoid para typhoid a b and 12 18 in cold place c vaccine typhoid para typhoid a b and 13 18 in col` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf Part XIII 15 (clause): `+batch size 35001 to 1.5 lakhs single sampling plan sample size 200 aql 0.25 ac 1 r 2 batch size 150001 to 5 lakhs single sampling plan sample size 315 aql 0.25 ac 2 r 3 batch size over 5 lakhs single sampling plan sample size 500 aql 0.25 ac 3 r 4 | +batch size 150001 to 5 lakhs single sampling pla` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf Part II #3 (section): `-b list of machinery equipment and minimum manufacturing premises required for the manufacturer of various categories of unani system of medicines one machine indicated for one category of medicine could be used for the manufacturing of other category of medicine also similarly some of the manufactu` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf Part II 8 #4 (clause): `-note the above requirements of machinery equipments space are made subject to the modification at the discretion of the licensing authority if he is of the opinion that having regard to the nature and extent of the manufacturing operations it is necessary to relax or alter then in the circumstances` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf Part II 1 #7 (clause): `+common name as in afi api plant s botanical name quantity used per annum in kgs sources of supply part used traders manufacturers forest collectors cultivators imported total whole plants root leaf others | +name of extracts quantity used per annum in kgs sources of supply common name as in afi api` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf Part II 29 (clause): `-note 1 patent or proprietary medicines containing vitamins intended for prophylactic therapeutic or paediatric use shall bear on the label the words for prophylactic use for therapeutic use or for paediatric use as the case may be in the cases of paediatric preparations the age of the infant or the` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf Part II 6 #7 (clause): `-phencyclidine dexamphetamine | -barbital methylphenidate | -methamphetamine secobarbital | +hydrochloride amphetamine meprobamate phencyclidine barbital methamphetamine | +cyclobarbital 1288 1289 dexamphetamine methylphenidate secobarbital | -hydrochloride cyclobarbital | -1288 amphetamine 1289 mep` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf Part II Appendix III 1.8 (clause): `+route of administration duration of proposed human administration human phase s for which study is proposed to be conducted long term toxicity requirements 1309 oral or parentral or transdermal single dose or several doses in one day upto 1 wk i ii iii 2 sp 2 wks > 1 wk but upto 2 wks i ii iii 2 sp` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf Part II Appendix III 1.9 (clause): `+group 14 28 days 84 182 days rodent rat non rodent dog or monkey rodent rat non rodent dog or monkey control 6 10 6 10 2 3 2 3 15 30 15 30 4 6 4 6 low dose 6 10 6 10 2 3 2 3 15 30 15 30 4 6 4 6 intermediate dose 6 10 6 10 2 3 2 3 15 30 15 30 4 6 4 6 high dose 6 10 6 10 2 3 2 3 15 30 15 30 4 6 4 6` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf _unnumbered:2 (unnumbered): `+3 | +32 | +43` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf Table 2 3. (table_row): `-3 tartrazine 19140 trisodium salt of 3 carboxy 5 hydroxy 1 p sulfophenyl 4 p` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf Table 2 17. (table_row): `-concentrated pyrene trisulfonic acid` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf Table 2 37. (table_row): `-acid` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf Table 9 (1) (2) (3) (I) Rasayoga Containing… (table_row): `-1 i rasayoga containing only rasa uprasa bhasma except naga vanga and tamra bhasma 10 ii rasayoga containing rasa uprasa bhasma along with kasthaushadhi guggulu 5 rasayoga xx` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf Table 11 (1) (table_row): `-1 3` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf Table 11 (xi) (table_row): `-xi` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf Table 11 (xiii) (table_row): `-xiii` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf Table 11 (xiv) (table_row): `-xiv` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf Table 29 D (table_row): `-3` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf Table 32 row 1 (table_row): `-glove print` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf Table 33 API derived from animal sources (table_row): `-material into process` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf Table 35 43. (table_row): `-24` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf Table 35 4. #5 (table_row): `-absorbed diphtheria toxoid` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf Table 46 12. (table_row): `-12 office total 1500` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf Table 56 Group (table_row): `-m f m f m f m f` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf page 158 (uncovered): `+serial number common name of colour colour index number chemical name of colour 1 2 3 4` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf page 159 (uncovered): `+serial number common name of colour colour index number chemical name of colour 1 2 3 4 concentrated pyrene trisulfonic acid` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf page 160 (uncovered): `+serial number common name of colour colour index number chemical name of colour 1 2 3 4 acid` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf page 161 (uncovered): `+serial number common name of colour colour index number chemical name of colour 1 2 3 4` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf page 315 (uncovered): `+5 raughan 6 zimad 7 habb pill 8 shiyaf 9 qutoor drops 10 kohal surma kajal 11 satt usara 12 kushta 13 joshanda single drugs 14 sharbat sikanjabeen 15 sayyal arq distillates 16 qurs tablet 17 marham qairooti 18 humool furzaja 19 bakhoor 20 nabati advia 21 maadni advia 22 ajsad advia 23 haiwani advia` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf page 329 (uncovered): `+class of drugs extent and conditions of exemption` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf page 329 (uncovered): `+1060 schedule d i see rule 21 d and rule 24 a information and undertaking required to be submitted by the manufacturer or his authorised agent with the application form for a registration certificate the format shall be properly filled in for each application in form 40 the detailed information sec` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf page 344 (uncovered): `+17 mancevikkalli exempted for external use euphorbia species` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf page 503 (uncovered): `+9 acyclovir 10 adenosine 11 adrenocorticotrophic hormone acth 12 alendronate sodium 13 aliopurinol 14 alphachymotrypsin 15` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf page 503 (uncovered): `+16 alprostadil 17 amantadine hydrochloride 18 amifostine 19 amikacin sulphate 20 amiloride hydrochloride 21 aminepline 22 aminoglu tethimide 23 aminosalicylic acid 24 amiodarone hydrochloride 25 amitriptyline 26 amlodipine besylate 27 amoscanate 28 amoxopine 29 amrinone lactate 30 analgin 31 androg` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf page 510 (uncovered): `+37 pentazocine 38 prulifloxacin 39 pyrazinamide 40 rifabutin 41 rifampicin` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf page 510 (uncovered): `+43 sparfloxacin 44 tniacetazone 45 tramadol` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf page 796 (uncovered): `+3 when stored at 4 c 8 rabies vaccine 6 in cold place 9 typhoid vaccine 18 in cold place 10 typhoid and para typhoid vaccine 18 in cold place 11 typhoid para typhoid a and b vaccine 18 in cold place 12 typhoid para typhoid a b and c vaccine 18 in cold place 13 typhoid para typhoid a b and c and tet` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf page 796 (uncovered): `+16 anti rabies vaccine cell culture 24 in cold place` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf page 798 (uncovered): `+name of the drug dosage form pack size isoniazide syrup 200 ml ipecacuanha syrup 10 ml oral rehydration salt ors powder pouches to be reconstituted to one litre in one pack or in 5 unit dose sachets in one pack piperazine granules 5 gm syrup 30 ml pyrantel pamoate syrup 8 ml or 10 ml potassium chlo` - NOT EXPLAINED
- india-drugs-rules-1945-consolidated-2024-07.pdf page 826 (uncovered): `+s no category of medicine minimum manufacturing space required machinery equipment recommended 1 2 3 4` - NOT EXPLAINED
- india-gsr127e-2025-schm-timeline.pdf 4 (clause): `-4 the gazette of india extraordinary part ii sec 3 i form a application for seeking extension of compliance with revised good manufacturing practices gmp under schedule m of the drugs rules 1945 | -sarvesh kumar digitally signed by sarvesh kumar srivastava srivastava date 2025.02.11 22 35 41 05 30` - NOT EXPLAINED
- india-gsr127e-2025-schm-timeline.pdf page 1 (uncovered): `+1031 gi 2025 1` - NOT EXPLAINED
- india-gsr127e-2025-schm-timeline.pdf page 1 (uncovered): `+extraordinary part ii section 3 sub section i published by authority no 94 new delhi tuesday february 11 2025 magha 22 1946 cg dl e 11022025 260908` - NOT EXPLAINED
- india-gsr127e-2025-schm-timeline.pdf page 2 (uncovered): `+2 the gazette of india extraordinary p` - NOT EXPLAINED
- india-gsr127e-2025-schm-timeline.pdf page 2 (uncovered): `+3 i iii vii viii` - NOT EXPLAINED
- india-gsr127e-2025-schm-timeline.pdf page 4 (uncovered): `+4 the gazette of india extraordinary p art ii s ec 3 i form a application for seeking extension of compliance with revised good manufacturing practices gmp under schedule m of the drugs rules 1945` - NOT EXPLAINED
- india-gsr666e-2024-schm-corrigendum.pdf _unnumbered:1 (unnumbered): `-digitally signed by amit kumar amit kumar jaiswal jaiswal date 2024.10.29 19 30 05 05 30` - NOT EXPLAINED
- india-gsr666e-2024-schm-corrigendum.pdf page 1 (uncovered): `+6992 gi 2024 1` - NOT EXPLAINED
- india-gsr666e-2024-schm-corrigendum.pdf page 1 (uncovered): `+extraordinary part ii section 3 sub section i published by authority no 608 new delhi monday october 28 2024 kartika 6 1946 cg dl e 29102024 258309` - NOT EXPLAINED
- india-schedule-m-2023-GSR922E.pdf Part I 1.2 (clause): `-7986 gi 2023 148` - NOT EXPLAINED
- india-schedule-m-2023-GSR922E.pdf Part III 9.1 (clause): `-dop injection filterintegrity test de contamination by pass duct shut offdamper e s shut vfd offdampe r exhaustai secondaryfi m m m lter vfd velocitysensor v v variable frequencydrive m m m hepafil ter m filter pressuredifferensialgua ge hepabag in bag outunits` - NOT EXPLAINED
- india-schedule-m-2023-GSR922E.pdf Part XIII 7 #2 (clause): `-manoj kumar digitally signed by manoj kumar verma date 2024.01.05 21 05 12 verma 05 30` - NOT EXPLAINED
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
- india-schedule-m-2023-GSR922E.pdf page 123 (uncovered): `+vii i ii iii iii` - NOT EXPLAINED
- india-schedule-m-2023-GSR922E.pdf page 127 (uncovered): `+10.1 ii iii` - NOT EXPLAINED
- pics-pe008-4-site-master-file.pdf _unnumbered:1 (unnumbered): `-p 008 4 1 of 8 1 december 2010` - NOT EXPLAINED
- pics-pe009-18-annexes.pdf _unnumbered:1 (unnumbered): `+pe 009 18 annexes 24 september 2026 | +i` - NOT EXPLAINED
- pics-pe009-18-annexes.pdf Annex 2A (section): `-i | +ii` - NOT EXPLAINED
- pics-pe009-18-annexes.pdf Annex 4 (section): `-ii | +iii` - NOT EXPLAINED
- pics-pe009-18-annexes.pdf Annex 10 (section): `-iii | +iv` - NOT EXPLAINED
- pics-pe009-18-annexes.pdf Annex 14 (section): `-iv | +v | -v | +vi | -pe 009 18 annexes vi 24 september 2026` - NOT EXPLAINED
- pics-pe009-18-annexes.pdf Annex 1 8.6 (clause): `-aseptic preparation and processing` - NOT EXPLAINED
- pics-pe009-18-annexes.pdf Annex 1 8.10 (clause): `-annex 1 manufacture of sterile medicinal products` - NOT EXPLAINED
- pics-pe009-18-annexes.pdf Annex 1 Glossary (section): `+− | +−` - NOT EXPLAINED
- pics-pe009-18-annexes.pdf Annex 2A 2 (clause): `-1 application of this annex applies to manufacturing steps illustrated in dark grey application of this annex or principles of this annex apply to steps illustrated in light grey apply depending on the requirements of national legislation 2 refer to points 5.32 for establishment of cell banks and s` - NOT EXPLAINED
- pics-pe009-18-annexes.pdf Annex 2A 3 (clause): `-atmp manufacturing plasmid atmp manufacturing | -manufacturing transcription establishing mcb or | -plasmid dna construct wcb | -purification preparation thawing transfer of plasmid harvest | -dna to starter colony transfection | -formulation e g e coli induction | -filling expansion | -storage dis` - NOT EXPLAINED
- pics-pe009-18-annexes.pdf Annex 14 10 (clause): `-annex 14 manufacture of products derived from human blood or plasma 2 for collection and regulatory submission of data information for plasma for fractionation annex 14 manufacture of products derived from human blood or plasma b other relevant documents reference should be made to the latest revis` - NOT EXPLAINED
- pics-pe009-18-annexes.pdf Annex 20 15 (clause): `-initiate quality risk management process risk assessment risk identification risk analysis risk evaluation unacceptable risk management tools risk communication risk control risk reduction risk acceptance output result of the quality risk management process risk review review events` - NOT EXPLAINED
- pics-pe009-18-part1.pdf Part I (section): `+i | -i | +ii | -pe 009 18 part i ii 24 september 2026` - NOT EXPLAINED
- pics-pe009-18-part1.pdf Part I 1.2 (clause): `-pe 009 18 part i − 1 24 september 2026` - NOT EXPLAINED
- pics-pe009-18-part1.pdf Part I 1.4 (clause): `-pe 009 18 part i − 2 24 september 2026` - NOT EXPLAINED
- pics-pe009-18-part1.pdf Part I 1.7 (clause): `-pe 009 18 part i − 3 24 september 2026` - NOT EXPLAINED
- pics-pe009-18-part1.pdf Part I 1.8 (clause): `-pe 009 18 part i − 4 24 september 2026` - NOT EXPLAINED
- pics-pe009-18-part1.pdf Part I 1.9 (clause): `-pe 009 18 part i − 5 24 september 2026` - NOT EXPLAINED
- pics-pe009-18-part1.pdf Part I 1.11 (clause): `-pe 009 18 part i − 6 24 september 2026` - NOT EXPLAINED
- pics-pe009-18-part1.pdf Part I 1.13 (clause): `-pe 009 18 part i − 7 24 september 2026` - NOT EXPLAINED
- pics-pe009-18-part1.pdf Part I 2.4 (clause): `-pe 009 18 part i − 8 24 september 2026` - NOT EXPLAINED
- pics-pe009-18-part1.pdf Part I 2.7 (clause): `-pe 009 18 part i − 9 24 september 2026` - NOT EXPLAINED
- pics-pe009-18-part2.pdf Part II (section): `+i` - NOT EXPLAINED
- pics-pe009-18-part2.pdf Part II 1.2 (clause): `-pe 009 18 part ii − 1 24 september 2026 | -pe 009 18 part ii − 2 24 september 2026 | -increasing gmp requirements pe 009 18 part ii − 3 24 september 2026 quality management` - NOT EXPLAINED
- pics-pe009-18-part2.pdf Part II 2.21 (clause): `-pe 009 18 part ii − 4 24 september 2026` - NOT EXPLAINED
- pics-pe009-18-part2.pdf Part II 2.32 (clause): `-pe 009 18 part ii − 5 24 september 2026` - NOT EXPLAINED
- pics-pe009-18-part2.pdf Part II 2.60 (clause): `-pe 009 18 part ii − 6 24 september 2026` - NOT EXPLAINED
- pics-pe009-18-part2.pdf Part II 3.24 (clause): `-pe 009 18 part ii − 7 24 september 2026` - NOT EXPLAINED
- pics-pe009-18-part2.pdf Part II 4.15 (clause): `-pe 009 18 part ii − 8 24 september 2026` - NOT EXPLAINED
- pics-pe009-18-part2.pdf Part II 4.33 (clause): `-pe 009 18 part ii − 9 24 september 2026` - NOT EXPLAINED
- pics-pe009-18-part2.pdf page 4 (uncovered): `+table of contents page pe 009 18 part ii iii 24 september 2026 11 laboratory controls 26` - NOT EXPLAINED
- pics-pi007-6-aseptic-validation.pdf _unnumbered:1 (unnumbered): `+pi 007 6 1 january 2011 | +i` - NOT EXPLAINED
- pics-pi009-4-am-utilities.pdf Table 2 1. #2 (table_row): `-area operation items medicinal products notes crucial questions supporting documents` - NOT EXPLAINED
- pics-pi009-4-am-utilities.pdf Table 3 2. #2 (table_row): `-setting and cleaning parameters i stage consistently producing desired quality the work is performed what do signatures mean` - NOT EXPLAINED
- pics-pi009-4-am-utilities.pdf Table 3 2. #3 (table_row): `-di column regeneration ph uv light pw conductivity leakage toc annex 1 4472` - NOT EXPLAINED
- pics-pi009-4-am-utilities.pdf Table 4 3. #3 (table_row): `-change control reports the system cleaning sanitation sterilisation logbook monitoring parameters see 1.6 incidents filter changes shut down periods cleaning sanitation maintenance 4.29,4.314.1 4.26 4.28 4.29` - NOT EXPLAINED
- pics-pi009-4-am-utilities.pdf Table 5 4. #2 (table_row): `-capacity consumption` - NOT EXPLAINED
- pics-pi011-3-computerised-systems.pdf _unnumbered:1 (unnumbered): `+pi 011 3 25 september 2007 | +i | -pi 011 3 i 25 september 2007` - NOT EXPLAINED
- pics-pi011-3-computerised-systems.pdf 6.2 (clause): `+9 | -operating software procedures and people hardware equipment firmware computer system controlled function controlling system or process computerised system operating environment including other networked or standalone computerised systems other systems media people equipment and procedures` - NOT EXPLAINED
- pics-pi011-3-computerised-systems.pdf 9.1 (clause): `+14` - NOT EXPLAINED
- pics-pi011-3-computerised-systems.pdf 11 (clause): `-user requirements pq specification verifies functional specification oq verifies design specifications iq verifies system build` - NOT EXPLAINED
- pics-pi011-3-computerised-systems.pdf 20.1 (clause): `+34` - NOT EXPLAINED
- pics-pi011-3-computerised-systems.pdf 21.1 (clause): `+37` - NOT EXPLAINED
- pics-pi011-3-computerised-systems.pdf 21.7 (clause): `+43` - NOT EXPLAINED
- pics-pi011-3-computerised-systems.pdf 24 (clause): `-some of the details below are not relevant for cots but it is necessary to have clearly defined the requirements for intended use and to have assessed the application s fitness for purpose 56 under some circumstances access to source code cannot be guaranteed regulated users are expected to have as` - NOT EXPLAINED
- pics-pi011-3-computerised-systems.pdf 15 #2 (clause): `+58` - NOT EXPLAINED
- pics-pi011-3-computerised-systems.pdf page 12 (uncovered): `+operating environment including other networked or standalone computerised systems other systems media people equipment and procedures computerised system computer system controlling system controlled function or process operating procedures and people equipment hardware firmware software` - NOT EXPLAINED
- pics-pi012-3-sterility-testing.pdf _unnumbered:1 (unnumbered): `+pi 012 3 25 september 2007 | +i` - NOT EXPLAINED
- pics-pi012-3-sterility-testing.pdf 6.1 (clause): `+−` - NOT EXPLAINED
- pics-pi023-2-am-qc-labs.pdf _unnumbered:1 (unnumbered): `+pi 023 2 25 september 2007 | +page 1 of 2` - NOT EXPLAINED
- pics-pi023-2-am-qc-labs.pdf 3.2 (clause): `-1 | +2` - NOT EXPLAINED
- pics-pi023-2-am-qc-labs.pdf 5 (clause): `-2 | +i | -2 | +ii` - NOT EXPLAINED
- pics-pi023-2-am-qc-labs.pdf 8.7 (clause): `-i | +ii` - NOT EXPLAINED
- pics-pi023-2-am-qc-labs.pdf 9.4 (clause): `-pi 023 2 page ii of ii 25 september 2007 | -note some more details and specific items related to testing in chemical physical chemical and microbiological laboratories to be investigated in addition to above described subjects are involved in supplements 1 and 2 supplement no 1 to pi 023 1 aide mem` - NOT EXPLAINED
- pics-pi023-2-am-qc-labs.pdf Table 3 5.2. (table_row): `-premises continued area operation items note 5.4 below notes crucial questions show me supporting` - NOT EXPLAINED
- pics-pi023-2-am-qc-labs.pdf Table 3 6.1. (table_row): `-supplies continued area operation items notes show me crucial questions supporting documents` - NOT EXPLAINED
- pics-pi023-2-am-qc-labs.pdf Table 3 7.2. (table_row): `-3.2` - NOT EXPLAINED
- pics-pi023-2-am-qc-labs.pdf page 9 (uncovered): `+show me supporting documents` - NOT EXPLAINED
- pics-pi023-2-am-qc-labs.pdf page 10 (uncovered): `+show me supporting documents` - NOT EXPLAINED
- pics-pi023-2-am-qc-labs.pdf page 18 (uncovered): `+show me supporting documents` - NOT EXPLAINED
- pics-pi028-2-am-packaging.pdf Table 2 1.2 (table_row): `-material material received de dusting cleaning on outside separate area` - NOT EXPLAINED
- pics-pi028-2-am-packaging.pdf Table 2 1.7 (table_row): `-documented` - NOT EXPLAINED
- pics-pi028-2-am-packaging.pdf page 5 (uncovered): `+items notes crucial questions supporting documents` - NOT EXPLAINED
- pics-pi028-2-am-packaging.pdf page 6 (uncovered): `+items notes crucial questions supporting documents` - NOT EXPLAINED
- pics-pi028-2-am-packaging.pdf page 7 (uncovered): `+items notes crucial questions supporting documents adequate and documented investigation of packaging process deviations` - NOT EXPLAINED
- pics-pi030-1-am-api.pdf 5 (clause): `-5 aide memoire validated electronic | -10.11 5.40 7.20 systems for material | -status control are | -acceptable in such | -cases physical | -segregation may not be` - NOT EXPLAINED
- pics-pi030-1-am-api.pdf Table 3 Product Quality Review (PQR) (table_row): `-critical ipc api test deviations complaints returns recalls non conformances related including effectiveness corrective preventive actions conducted changes conducted stability program verified based validation status recorded required changes highlighted implemented through change control system 2` - NOT EXPLAINED
- pics-pi030-1-am-api.pdf Table 13 Validation Documentation (table_row): `-corrective actions implemented` - NOT EXPLAINED
- pics-pi030-1-am-api.pdf Table 15 Reworking (table_row): `-reworking an investigation before decision rework carried out 14.30` - NOT EXPLAINED
- pics-pi030-1-am-api.pdf page 6 (uncovered): `+a review of oos critical ipc and api test results deviations complaints returns and recalls non conformances and related investigations including the effectiveness of the corrective and preventive actions conducted a review of changes conducted stability program data verified are required changes h` - NOT EXPLAINED
- pics-pi030-1-am-api.pdf page 7 (uncovered): `+2 quality management system` - NOT EXPLAINED
- pics-pi030-1-am-api.pdf page 9 (uncovered): `+4 building and facilities` - NOT EXPLAINED
- pics-pi030-1-am-api.pdf page 11 (uncovered): `+validated electronic systems for material status control are acceptable in such cases physical segregation may not be required` - NOT EXPLAINED
- pics-pi030-1-am-api.pdf page 15 (uncovered): `+operations items notes crucial questions show me supporting documents in process` - NOT EXPLAINED
- pics-pi038-2-am-qrm.pdf Table 2 1.12 (table_row): `-1.12 2 expectations on how implemented are systems in place to ensure risks to quality medicinal product are assessed controlled communicated reviewed as part routine quality management review process gmp guide 1.12` - NOT EXPLAINED
- pics-pi041-1-data-integrity.pdf 8.4 (clause): `+item generation` - NOT EXPLAINED
- pics-pi041-1-data-integrity.pdf 8.10.2 (clause): `-9 note that storage periods for some documents may be dictated by other local or national legislation` - NOT EXPLAINED
- pics-pi041-1-data-integrity.pdf 9.3 (clause): `-6 expectation operating systems and network components including hardware should be updated in a timely manner according to vendor recommendations and migration of applications from older to newer platforms should be planned and conducted in advance of the time before the platforms reach an unsuppo` - NOT EXPLAINED
- pics-pi041-1-data-integrity.pdf 9.4 (clause): `-2 expectation where system software including operating system is installed or updated the user should ensure that existing and archived data can be` - NOT EXPLAINED
- pics-pi041-1-data-integrity.pdf 2 #2 (clause): `-2 expectation computerised systems should be protected from accidental changes or deliberate manipulation companies should assess systems and their design to prevent unauthorised changes to validated settings that may ultimately affect data integrity consideration should be given to the physical se` - NOT EXPLAINED
- pics-pi043-1-am-cross-contamination.pdf Table 7 Nr. (table_row): `-general organisational controls` - NOT EXPLAINED
- pics-pi052-1-am-hbel.pdf Table 3 row 1 (table_row): `-section 2 qrm study organisational and technical control measures based on difference is > 10 fold and there is a potential to patient safety as a result of used and reference to an within competent authorities is recommended assess margin of safety that has been established between value and clean` - NOT EXPLAINED
- pics-pi053-1-qa-cross-contamination.pdf _unnumbered:2 (unnumbered): `+2 2 introduction 2 3 scope 3 4 questions answers on implementation of risk based prevention of cross contamination in production and guideline on setting health based exposure limits for use in risk identification in the manufacture of different medicinal products in shared facilities 3 5 reference` - NOT EXPLAINED
- pics-pi058-1-annex1-interpretation.pdf 4.10 (clause): `-10 revision history` - NOT EXPLAINED
- pics-pi058-1-annex1-interpretation.pdf page 3 (uncovered): `+2 introduction 2.1 purpose and scope` - NOT EXPLAINED
- who-trs1010-a10-stability.pdf Appendix 3 1.2 (clause): `+1.3` - NOT EXPLAINED
- who-trs1010-a10-stability.pdf Appendix 3 1.3 (clause): `+general principles 312 2 guidelines 313 2.1 active pharmaceutical ingredient 313 2.1.1 general 313 2.1.2 stress testing 313 2.1.3 selection of batches 314 2.1.4 container closure system 314 2.1.5 specification 315 2.1.6 testing frequency 315 2.1.7 storage conditions 315 2.1.8 stability commitments ` - NOT EXPLAINED
- who-trs1010-a10-stability.pdf Appendix 3 2.1.7.1 (clause): `-12 months or 6 months as | -described in point 2.1.7 | +12 months or 6 months as described in point 2.1.7` - NOT EXPLAINED
- who-trs1010-a10-stability.pdf Appendix 3 2.2.7.1 (clause): `-12 months or 6 months as | -referred to in section 2.2.7 | +12 months or 6 months as referred to in section 2.2.7 o t e c h r e p o r t s e s n o 1 0 1 0 2 0 1 8` - NOT EXPLAINED
- who-trs1010-a10-stability.pdf Appendix 3 2.2.7.3 (clause): `-12 months or 6 months as | +testing conditions | +condition | -calculation testing conditions condition | +calculation` - NOT EXPLAINED
- who-trs1010-a10-stability.pdf Appendix 2 1 (clause): `-intermediate failure during accelerated stability studies 30 c 65 % rh` - NOT EXPLAINED
- who-trs1010-a10-stability.pdf Appendix 2 2 (clause): `-intermediate failure during accelerated stability studies 30 c 65 % rh | -store in the original package | +blister store in the original package` - NOT EXPLAINED
- who-trs1010-a10-stability.pdf Appendix 3 (section): `+products approved in zone ii | -who recommended products approved in | +are based who recommended | -zone ii are based | +does not require any special storage conditions or similar i e no temperature mentioned eu | +finished pharmaceutical product fpp is stable at long term conditions with no signi` - NOT EXPLAINED
- who-trs1010-a8-hvac-nonsterile.pdf 7.11 (clause): `-1.8 | +annex table | -elbat aseicnelaviuqe etamixorppa sdradnats tset retlfi fo nosirapmoc 0101 on seires troper lacinhcet ohw deunitnoc 1.8 a elbat deunitnoc 1.8 a elbat tnerruc si noitacfiissalc eht taht erusne a ezis elcitrap gnitartenep tsom sppm retlfi ot setaler | +8.1 comparison of filter te` - NOT EXPLAINED
- who-trs1010-a8-hvac-nonsterile.pdf Table 1 ISO 29463 (table_row): `-iso 29463` - NOT EXPLAINED
- who-trs1010-a8-hvac-nonsterile.pdf Table 1 EN 779 & EN 1822 (table_row): `-779 1822 mpps integral 1822 2009 u 17 99.999995 u 16 99.99995 u 15 99.9995 h 14 99.995 h 13 99.95 e 99.5 e e 85 779 2012 f 9 f 8 f 7` - NOT EXPLAINED
- who-trs1010-a8-hvac-nonsterile.pdf Table 1 Eurovent 4/5 ASHRAE 52.1 BS6540 Part 1 (table_row): `-> 95 95 90 85 80` - NOT EXPLAINED
- who-trs1010-a8-hvac-nonsterile.pdf Table 1 Eurovent 4/5 ASHRAE 52.1 BS6540 Part 1 #2 (table_row): `-> 98 > 98` - NOT EXPLAINED
- who-trs1010-a8-hvac-nonsterile.pdf Table 1 ASHRAE 52.2 (table_row): `-ashrae 52.2 rating 16` - NOT EXPLAINED
- who-trs1010-a8-hvac-nonsterile.pdf Table 2 ISO 29463 (table_row): `-iso 29463` - NOT EXPLAINED
- who-trs1010-a8-hvac-nonsterile.pdf Table 2 header (table_header): `-2012` - NOT EXPLAINED
- who-trs1010-a8-hvac-nonsterile.pdf Table 2 row 3 (table_row): `-mpps integral overall efficiency %` - NOT EXPLAINED
- who-trs1010-a8-hvac-nonsterile.pdf Table 2 Eurovent 4/5 ASHRAE 52.1 BS6540 Part 1 (table_row): `-70 65 60 55 50 40 35 30 25 20 < 20` - NOT EXPLAINED
- who-trs1010-a8-hvac-nonsterile.pdf Table 2 Eurovent 4/5 ASHRAE 52.1 BS6540 Part 1 #2 (table_row): `-eurovent ashrae 52.1 bs 6540 part 1 average arrestance am % superseded` - NOT EXPLAINED
- who-trs1010-a8-hvac-nonsterile.pdf Table 2 ASHRAE 52.2 (table_row): `-ashrae 52.2 rating 12` - NOT EXPLAINED
- who-trs1010-a8-hvac-nonsterile.pdf Table 3 ISO 29463 (table_row): `-iso 29463` - NOT EXPLAINED
- who-trs1010-a8-hvac-nonsterile.pdf Table 3 header (table_header): `-2012` - NOT EXPLAINED
- who-trs1010-a8-hvac-nonsterile.pdf Table 3 row 3 (table_row): `-g 2 g 1` - NOT EXPLAINED
- who-trs1010-a8-hvac-nonsterile.pdf Table 3 Eurovent 4/5 ASHRAE 52.1 BS6540 Part 1 #2 (table_row): `-<` - NOT EXPLAINED
- who-trs1010-a8-hvac-nonsterile.pdf Table 3 ASHRAE 52.2 (table_row): `-ashrae 52.2 rating 4` - NOT EXPLAINED
- who-trs1010-a8-hvac-nonsterile.pdf page 15 (uncovered): `+90 f 8` - NOT EXPLAINED
- who-trs1010-a8-hvac-nonsterile.pdf page 15 (uncovered): `+> 98 85 f 7 eu 7 > 98 80` - NOT EXPLAINED
- who-trs1010-a8-hvac-nonsterile.pdf page 16 (uncovered): `+264 who technical report series no 1010 2018 who expert committee on specifications for pharmaceutical preparations fifty second report table a 8.1 continued` - NOT EXPLAINED
- who-trs1010-a8-hvac-nonsterile.pdf page 16 (uncovered): `+36492 osi superseded` - NOT EXPLAINED
- who-trs1010-a8-hvac-nonsterile.pdf page 16 (uncovered): `+75 eu 6` - NOT EXPLAINED
- who-trs1010-a8-hvac-nonsterile.pdf page 16 (uncovered): `+70 m 6 2102 977 ne` - NOT EXPLAINED
- who-trs1010-a8-hvac-nonsterile.pdf page 16 (uncovered): `+65 > 95 60` - NOT EXPLAINED
- who-trs1010-a8-hvac-nonsterile.pdf page 16 (uncovered): `+> 95 55 eu 5` - NOT EXPLAINED
- who-trs1010-a8-hvac-nonsterile.pdf page 16 (uncovered): `+> 95 50 m 5` - NOT EXPLAINED
- who-trs1010-a8-hvac-nonsterile.pdf page 16 (uncovered): `+> 95 45 > 95 40` - NOT EXPLAINED
- who-trs1010-a8-hvac-nonsterile.pdf page 16 (uncovered): `+> 90 35 eu` - NOT EXPLAINED
- who-trs1010-a8-hvac-nonsterile.pdf page 16 (uncovered): `+> 90 30 g` - NOT EXPLAINED
- who-trs1010-a8-hvac-nonsterile.pdf page 16 (uncovered): `+90 25 eu 3` - NOT EXPLAINED
- who-trs1010-a8-hvac-nonsterile.pdf page 16 (uncovered): `+85 20 g 3 80 < 20` - NOT EXPLAINED
- who-trs1010-a8-hvac-nonsterile.pdf page 17 (uncovered): `+annex table a 8.1 continued` - NOT EXPLAINED
- who-trs1010-a8-hvac-nonsterile.pdf page 17 (uncovered): `+36492 osi superseded` - NOT EXPLAINED
- who-trs1010-a8-hvac-nonsterile.pdf page 17 (uncovered): `+2102 977 ne eu 2` - NOT EXPLAINED
- who-trs1010-a8-hvac-nonsterile.pdf page 17 (uncovered): `+ensure that the classification is current` - NOT EXPLAINED
- who-trs1010-a8-hvac-nonsterile.pdf page 17 (uncovered): `+most penetrating particle size note the filter classifications referred to above relate to the` - NOT EXPLAINED
- who-trs1010-a8-hvac-nonsterile.pdf page 17 (uncovered): `+relates to filter classes` - NOT EXPLAINED
- who-trs1010-a8-hvac-nonsterile.pdf page 17 (uncovered): `+1822 relates to filter classes e 10 to u 17` - NOT EXPLAINED
- who-trs1019-a2-hvac-nonsterile-part2.pdf 4.2 (clause): `+w h o t e c h r e p o r t s e s n o 1 0 1 9 2 0 fig a 2.1 | +fig a 2.2 | +fig a 2.5 | +fig a 2.6 | +w h o t e c h r e p o r t s e s n o 1 0 1 9 2 0 fig a 2.7` - NOT EXPLAINED
- who-trs1019-a2-hvac-nonsterile-part2.pdf 7 (clause): `+fig a 2.9 | +w h o t e c h r e p o r t s e s n o 1 0 1 9 2 0 fig a 2.10` - NOT EXPLAINED
- who-trs1019-a2-hvac-nonsterile-part2.pdf 7.1 (clause): `+fig a 2.11 | +w h o t e c h r e p o r t s e s n o 1 0 1 9 2 0 fig a 2.13` - NOT EXPLAINED
- who-trs1019-a2-hvac-nonsterile-part2.pdf 12 (clause): `+who technical report series no 961 6 relative humidity iso 14644 3 and who technical report series no 961 6 | -relative humidity iso 14644 3 and | +company procedure smoke test airflow velocity iso 14644 3 recovery in house procedure air change rate | -airflow velocity iso 14644 3 recovery in house` - NOT EXPLAINED
- who-trs1025-a3-wfi-non-distillation.pdf 3.2 (clause): `-who technical report series no 1025 2020` - NOT EXPLAINED
- who-trs1025-a3-wfi-non-distillation.pdf 7.2 (clause): `-who technical report series no 1025 2020` - NOT EXPLAINED
- who-trs1025-a7-storage-distribution.pdf Appendix 1 (section): `+label description recommended limits` - NOT EXPLAINED
- who-trs1033-a2-hbel-cleaning.pdf Appendix 1 (section): `-1202 3301 on who technical report serie | +api pde ug day mdd mg day batch size kg shared equipment surface m 2 1 2 3 4 5` - NOT EXPLAINED
- who-trs1033-a2-hbel-cleaning.pdf Table 2 Pre- Ce- ding Product a (table_row): `-5 6` - NOT EXPLAINED
- who-trs1044-a2-sterile.pdf _unnumbered:1 (unnumbered): `-2011.1 | +2011 1 | -contents background 87 abbreviations 89` - NOT EXPLAINED
- who-trs1044-a2-sterile.pdf 4.27 (clause): `+grade maximum limits for total particle ≥ 0.5 μm m 3 maximum limits for total particle ≥ 5 μm m 3 at rest in operation at rest in operation a 3 520 3 520 not specifieda not specifieda b 3 520 352 000 not specifieda 2 930 c 352 000 3 520 000 2 930 29 300 d 3 520 000 not predetermined b 29 300 not pr` - NOT EXPLAINED
- who-trs1044-a2-sterile.pdf 4.31 (clause): `+grade air sample cfu m 3 settle plates diameter 90 mm cfu 4 hoursa contact plates diameter 55 mm cfu plate` - NOT EXPLAINED
- who-trs1044-a2-sterile.pdf 8.6 (clause): `+operation grade` - NOT EXPLAINED
- who-trs1044-a2-sterile.pdf 8.10 (clause): `-2 02 4 who technical report series no 104 | +grade operation | +grade operation` - NOT EXPLAINED
- who-trs1044-a2-sterile.pdf 9.15 (clause): `+grade maximum limits for total particle ≥ 0.5 μm m 3 maximum limits for total particle ≥ 5 μm m 3 at rest in operation at rest in operation a 3 520 3 520 29 29 b 3 520 352 000 29 2 930 c 352 000 3 520 000 2 930 29 300 d 3 520 000 not predetermineda 29 300 not predetermineda` - NOT EXPLAINED
- who-trs1044-a2-sterile.pdf 9.30 (clause): `+grade air sample cfu m 3 settle plates diam 90 mm cfu 4 hoursa contact plates diam 55 mm cfu plate b glove print incl 5 fingers on both hands cfu glove` - NOT EXPLAINED
- who-trs1044-a2-sterile.pdf Table 1 Grade (table_row): `-predetermined specified specified` - NOT EXPLAINED
- who-trs1044-a2-sterile.pdf Table 2 Grade (table_row): `-hours a` - NOT EXPLAINED
- who-trs1044-a2-sterile.pdf Table 7 Grade (table_row): `-hours a` - NOT EXPLAINED
- who-trs1044-a4-tech-transfer.pdf Appendix 1 (section): `+aspect related documentation | +pharmaceutical ingredients apis and excipients` - NOT EXPLAINED
- who-trs1044-a4-tech-transfer.pdf _unnumbered:4 (unnumbered): `+aspect related documentation` - NOT EXPLAINED
- who-trs1052-a4-qc-labs.pdf Appendix 1 (section): `-who technical report series no 1052 2024 | +o t e c h r e p o r t s e s n o 1 0 5 2 2 0 2 4 first stage laboratory continued optional items quantity | +o t e c h r e p o r t s e s n o 1 0 5 2 2 0 2 4 medium sized laboratory continued equipment and major instruments quantity | +1 | +2 | +equipment f` - NOT EXPLAINED
- who-trs1052-a4-qc-labs.pdf Appendix 2 (section): `-tg | +o t e c h r e p o r t s e s n o 1 0 5 2 2 0 2 4 | -uitg | +tg` - NOT EXPLAINED
- who-trs1052-a4-qc-labs.pdf Appendix 3 1 #2 (clause): `-umeas | +u tg meas | +u | -umeas | +meas` - NOT EXPLAINED
- who-trs1052-a4-qc-labs.pdf Appendix 3 8 (clause): `-4202 2501 on who technical report series | +test solution` - NOT EXPLAINED
- who-trs1060-a2-nitrosamines.pdf _unnumbered:2 (unnumbered): `+7` - NOT EXPLAINED
- who-trs1060-a3-excipients.pdf Appendix 1 7.2 #2 (clause): `-annex x 3 table continued wh o expert committee on specifications for pharmaceutical preparations fifty eighth report table continued` - NOT EXPLAINED
- who-trs1060-a3-excipients.pdf Appendix 1 7.3 #2 (clause): `+equipment risk` - NOT EXPLAINED
- who-trs1060-a3-excipients.pdf Appendix 1 7.4 #2 (clause): `+materials risk` - NOT EXPLAINED
- who-trs1060-a3-excipients.pdf Appendix 1 7.5 #2 (clause): `+utilities risk` - NOT EXPLAINED
- who-trs1060-a3-excipients.pdf Appendix 1 7.6 (clause): `+personnel risk` - NOT EXPLAINED
- who-trs1060-a3-excipients.pdf Appendix 1 7.7 (clause): `+risk production` - NOT EXPLAINED
- who-trs1060-a3-excipients.pdf Appendix 1 7.8 (clause): `+repackaging risk` - NOT EXPLAINED
- who-trs1060-a3-excipients.pdf Appendix 1 7.9 (clause): `+storage risk` - NOT EXPLAINED
- who-trs1060-a3-excipients.pdf Appendix 1 7.10 (clause): `+risk distribution` - NOT EXPLAINED
- who-trs1060-a3-excipients.pdf Table 1 Premises (table_row): `-location flow personnel flow access services` - NOT EXPLAINED
- who-trs1060-a3-excipients.pdf page 35 (uncovered): `+material flow personnel flow location access services` - NOT EXPLAINED
- who-trs1060-a3-excipients.pdf page 36 (uncovered): `+who technical report series no 1060 2025` - NOT EXPLAINED
- who-trs902-a9-packaging.pdf _unnumbered:1 (unnumbered): `-who technical report series no 902 2002` - NOT EXPLAINED
- who-trs902-a9-packaging.pdf Annex 9 Appendix 4 4.1 (clause): `-table 2 methods of disposal of uncontaminated packaging material recycling landfill incineration paper cardboard plastics glass na rubber metal na highly recommended recommended acceptable na not applicable` - NOT EXPLAINED
- who-trs929-a4-sampling.pdf _unnumbered:1 (unnumbered): `+annex 4 | -technical report series no 929 2005` - NOT EXPLAINED
- who-trs929-a4-sampling.pdf Annex 4 1.1 (clause): `-1.1` - NOT EXPLAINED
- who-trs929-a4-sampling.pdf Annex 4 1.2 (clause): `-1.2` - NOT EXPLAINED
- who-trs929-a4-sampling.pdf Annex 4 1.3 (clause): `-1.3` - NOT EXPLAINED
- who-trs929-a4-sampling.pdf Annex 4 1.4 (clause): `-1.4` - NOT EXPLAINED
- who-trs929-a4-sampling.pdf Annex 4 1.5 (clause): `-1.5` - NOT EXPLAINED
- who-trs929-a4-sampling.pdf Annex 4 1.6 (clause): `-1.6` - NOT EXPLAINED
- who-trs929-a4-sampling.pdf Annex 4 1.7 (clause): `-1.7` - NOT EXPLAINED
- who-trs929-a4-sampling.pdf Annex 4 2.1 (clause): `-2.1` - NOT EXPLAINED
- who-trs929-a4-sampling.pdf Annex 4 2.2 (clause): `-2.2` - NOT EXPLAINED
- who-trs929-a4-sampling.pdf Annex 4 2.3 (clause): `-2.3` - NOT EXPLAINED
- who-trs929-a4-sampling.pdf Annex 4 3.1 (clause): `-3.1` - NOT EXPLAINED
- who-trs929-a4-sampling.pdf Annex 4 3.2 (clause): `-3.2` - NOT EXPLAINED
- who-trs929-a4-sampling.pdf Annex 4 4.1 (clause): `-4.1` - NOT EXPLAINED
- who-trs929-a4-sampling.pdf Annex 4 4.2 (clause): `-4.2` - NOT EXPLAINED
- who-trs929-a4-sampling.pdf Annex 4 4.3 (clause): `-4.3` - NOT EXPLAINED
- who-trs929-a4-sampling.pdf Annex 4 4.4 (clause): `-4.4` - NOT EXPLAINED
- who-trs929-a4-sampling.pdf Annex 4 5.1 (clause): `-5.1` - NOT EXPLAINED
- who-trs929-a4-sampling.pdf Annex 4 5.2 (clause): `-5.2` - NOT EXPLAINED
- who-trs929-a4-sampling.pdf Annex 4 5.3 (clause): `-5.3` - NOT EXPLAINED
- who-trs929-a4-sampling.pdf Annex 4 Appendix 5 5 (clause): `-table 1 values of n p or r for the n sampling unitsa value of n p or r values of n n plan p plan r plan 2 up to 3 up to 25 up to 2 3 4 6 26 56 3 4 4 7 13 57 100 5 7 5 14 20 101 156 8 11 6 21 30 157 225 12 16 7 31 42 17 22 8 43 56 23 28 9 57 72 29 36 10 73 90 37 44 a an example of how these plans wo` - NOT EXPLAINED
- who-trs929-a4-sampling.pdf Annex 4 Appendix 5 5.1.1 (clause): `+table 1 values of n p or r for the n sampling units a value of n p or r values of n n plan p plan r plan 2 up to 3 up to 25 up to 2 3 4 6 26 56 3 4 4 7 13 57 100 5 7 5 14 20 101 156 8 11 6 21 30 157 225 12 16 7 31 42 17 22 8 43 56 23 28 9 57 72 29 36 10 73 90 37 44 a an example of how these plans w` - NOT EXPLAINED
- who-trs953-a2-app1-stability-conditions.pdf _unnumbered:1 (unnumbered): `-stability testing of active pharmaceutical ingredients and finished pharmaceutical products stability conditions for who member states by region 1 update march 2021 previously included as table 2 in stability testing of active pharmaceutical ingredients and finished pharmaceutical products annex 2 ` - NOT EXPLAINED
- who-trs957-a2-api.pdf _unnumbered:1 (unnumbered): `-who technical report series no 957 2010` - NOT EXPLAINED
- who-trs957-a2-api.pdf Annex 2 Appendix 2 1.3 (clause): `-a this table has been taken from the ich harmonised tripartite guideline active pharmaceutical ingredients q 7 current step 4 version dated 10 november 2000 increasing gmp requirements` - NOT EXPLAINED
- who-trs957-a3-hazardous.pdf _unnumbered:1 (unnumbered): `+annex 3 | -technical report series no 957 2010` - NOT EXPLAINED
- who-trs957-a3-hazardous.pdf Annex 3 9.3 (clause): `-figure 1 typical airflow pattern for contaminant p p p p` - NOT EXPLAINED
- who-trs957-a3-hazardous.pdf Annex 3 11.1 (clause): `-e shut off vfd damper exhaust | +m 11.2 the fi nal fi lters on the safe change unit should be hepa fi lters with at least an h 13 classifi cation according to en 1822 fi lter standards for dusty return | -fan secondary m m m filter vfd velocity sensor v m m m | +pre fi ltration may also be required` - NOT EXPLAINED
- who-trs957-a3-hazardous.pdf Annex 3 11.3 (clause): `-first filter fail` - NOT EXPLAINED
- who-trs957-a3-hazardous.pdf Annex 3 11.6 (clause): `+fi lter condition 11.7` - NOT EXPLAINED
- who-trs957-a3-hazardous.pdf Annex 3 13 (clause): `-effluent treatment` - NOT EXPLAINED
- who-trs957-a3-hazardous.pdf page 11 (uncovered): `+figure 1 typical airfl ow pattern for contaminant` - NOT EXPLAINED
- who-trs957-a3-hazardous.pdf page 13 (uncovered): `+fi lter housings` - NOT EXPLAINED
- who-trs957-a3-hazardous.pdf page 14 (uncovered): `+fi rst fi lter fail` - NOT EXPLAINED
- who-trs957-a3-hazardous.pdf page 16 (uncovered): `+13 effl uent treatment` - NOT EXPLAINED
- who-trs961-a14-site-master-file.pdf Annex 14 2.3 (clause): `+1` - NOT EXPLAINED
- who-trs961-a2-micro-labs.pdf _unnumbered:1 (unnumbered): `+annex 2 | -technical report series no 961 2011` - NOT EXPLAINED
- who-trs961-a2-micro-labs.pdf Annex 2 Appendix 1 (section): `-appendix | -examples of zones in which operations could be carried out` - NOT EXPLAINED
- who-trs961-a2-micro-labs.pdf Annex 2 Appendix 2 (section): `-appendix | -examples of maintenance of equipment` - NOT EXPLAINED
- who-trs961-a2-micro-labs.pdf Annex 2 Appendix 3 (section): `-appendix | -examples of calibration checks and intervals for different laboratory equipment` - NOT EXPLAINED
- who-trs961-a2-micro-labs.pdf Annex 2 Appendix 4 (section): `-appendix 4 examples of equipment qualification` - NOT EXPLAINED
- who-trs961-a2-micro-labs.pdf _unnumbered:5 (unnumbered): `-examples of calibration checks and intervals for different laboratory equipment this information is provided as an example and the frequency will be based on the need type previous performance and criticality of the equipment examples of equipment qualification and monitoring this information is pr` - NOT EXPLAINED
- who-trs961-a2-micro-labs.pdf Table 2 Laboratory (table_row): `-other` - NOT EXPLAINED
- who-trs961-a2-micro-labs.pdf page 2 (uncovered): `+examples of equipment qualifi cation` - NOT EXPLAINED
- who-trs961-a2-micro-labs.pdf page 23 (uncovered): `+examples of equipment qualifi cation and monitoring th is information is provided as an example and the frequency will be based on the need type previous performance and criticality of the equipment` - NOT EXPLAINED
- who-trs961-a2-micro-labs.pdf page 24 (uncovered): `+examples of equipment qualifi cation and monitoring continued` - NOT EXPLAINED
- who-trs961-a2-micro-labs.pdf page 24 (uncovered): `+hepa high effi ciency particulate air` - NOT EXPLAINED
- who-trs961-a2-micro-labs.pdf page 25 (uncovered): `+general use of reference cultures all parts of the process should be fully documented and detailed records of all stages must be maintained purity checks and biochemical tests should be made as appropriate reference strain from source recognized by accreditation body reference stock g 1 freeze drie` - NOT EXPLAINED
- who-trs961-a9-storage-transport-ttsp.pdf Annex 9 3.9.1 (clause): `+22` - NOT EXPLAINED
- who-trs961-a9-storage-transport-ttsp.pdf Annex 9 4.7 (clause): `-4.7 qualification of temperature controlled stores qualify new temperature controlled storage areas and new refrigeration equipment before it becomes operational the qualification` - NOT EXPLAINED
- who-trs961-a9-storage-transport-ttsp.pdf Annex 9 6.5.1 (clause): `+14` - NOT EXPLAINED
- who-trs961-a9-storage-transport-ttsp.pdf Annex 9 6.5.2 (clause): `+28` - NOT EXPLAINED
- who-trs961-a9-storage-transport-ttsp.pdf Annex 9 6.6 (clause): `-6.6 qualification of temperature controlled road vehicles where temperature controlled vehicles are directly owned and or operated qualify each vehicle before it becomes operational wherever possible the qualification` - NOT EXPLAINED
- who-trs961-a9-storage-transport-ttsp.pdf _unnumbered:2 (unnumbered): `+vladakhani | +pharmaceutical narcotics | -vladakhani pharmaceutical` - NOT EXPLAINED
- who-trs961-a9-storage-transport-ttsp.pdf page 2 (uncovered): `+4.7 qualifi cation of temperature controlled stores` - NOT EXPLAINED
- who-trs961-a9-storage-transport-ttsp.pdf page 21 (uncovered): `+4.7 qualifi cation of temperature controlled stores qualify new temperature controlled storage areas and new refrigeration equipment before it becomes operational the qualifi cation` - NOT EXPLAINED
- who-trs961-a9-storage-transport-ttsp.pdf page 28 (uncovered): `+6.6 qualifi cation of temperature controlled road vehicles where temperature controlled vehicles are directly owned and or operated qualify each vehicle before it becomes operational wherever possible the qualifi cation` - NOT EXPLAINED
- who-trs981-a2-qrm.pdf 6 (clause): `+4 8 12 16 20 | +3 6 9 12 15 | +2 4 6 8 10 | -t 4 ffo fwfsz 1 negligible t p sfhvmbupsz jttvf | -t p fõfdu po boe opu | +1 negligible | -t 4 ffo fwfsz 2 marginal t bz sfrvjsf 3 | +2 marginal | -t % fdjtjpo up sfmfbtf | -t 4 ffo fwfsz 3 moderate t 3 jotqfdujpo | +3 moderate | -efmdjfodz rvjuf | -t jn` - NOT EXPLAINED
- who-trs981-a2-qrm.pdf _unnumbered:2 (unnumbered): `+table 3 continued o t e c h r e p o r t s e s n o 9 8 1 2 0 1 3` - NOT EXPLAINED
- who-trs981-a2-qrm.pdf Table 3 Hazard operability analysis (HAZOP) (table_row): `-t tool t uses ufdiojrvf up ifmq jefoujgz t gbdjmjujft boe frvjqnfou t` - NOT EXPLAINED
- who-trs981-a2-qrm.pdf Table 3 Hazard analysis and critical control… (table_row): `-t identify fõfdujwfmz qsfwfou ib bse t bottom up t nqibtj ft tusfohui pg t t valuable t assessment` - NOT EXPLAINED
- who-trs981-a2-qrm.pdf Table 3 'BJMVSFNPEFTFõFDUT BOBMZTJT '.&" (table_row): `-bjmvsf npeft fõfdut bobmztjt assumes assesses uif qspcbcmf fõfdu wbmvbuf frvjqnfou` - NOT EXPLAINED
- who-trs981-a2-qrm.pdf Table 4 'BJMVSFNPEFTFõFDUT BOBMZTJT '.&" (table_row): `-bjmvsf npeft fõfdut bobmztjt t highly dependent upon strong understanding of product process and or facility under evaluation t` - NOT EXPLAINED
- who-trs981-a2-qrm.pdf Table 4 Source: Based on reference 9. This… (table_row): `-64 xfc tjuf iuuq xxx qrsj psh joefy btq 123 ibt ljoemz bhsffe up uif vtf pg jut` - NOT EXPLAINED
- who-trs981-a2-qrm.pdf page 30 (uncovered): `+table 3 continued continues` - NOT EXPLAINED
- who-trs992-a4-hold-time.pdf Glossary (section): `+including granulation pastes coating solution and coating suspension | +gravity viscosity sedimentation ph microbial test | -including granulation gravity viscosity sedimentation | -pastes coating solution ph microbial test and coating suspension | -initial 15 th day | -30 th day 45 th day | +initi` - NOT EXPLAINED
- who-trs992-a5-ttsp-supplements.pdf 1.1 (clause): `+1 | -table a 5.1 continued title section s` - NOT EXPLAINED
- who-trs992-a5-ttsp-supplements.pdf 5 (clause): `+table a 5.1 continued` - NOT EXPLAINED
- who-trs992-a5-ttsp-supplements.pdf 7 (clause): `+2 | +o t e c h r e p o r t s e s n o 9 9 2 2 0 1 5 supplement 1` - NOT EXPLAINED
- who-trs992-a5-ttsp-supplements.pdf _unnumbered:3 (unnumbered): `+supplement 2` - NOT EXPLAINED
- who-trs992-a5-ttsp-supplements.pdf Annex 2 A 2.3 (clause): `+supplement 3` - NOT EXPLAINED
- who-trs992-a5-ttsp-supplements.pdf _unnumbered:7 (unnumbered): `+o t e c h r e p o r t s e s n o 9 9 2 2 0 1 5 supplement 4` - NOT EXPLAINED
- who-trs992-a5-ttsp-supplements.pdf Annex 3 (section): `-3 sop fire drills` - NOT EXPLAINED
- who-trs992-a5-ttsp-supplements.pdf Annex 3 A 3.5 (clause): `+o t e c h r e p o r t s e s n o 9 9 2 2 0 1 5 supplement 5` - NOT EXPLAINED
- who-trs992-a5-ttsp-supplements.pdf Annex 2 (section): `-annex 2 checklist for building weatherproofing` - NOT EXPLAINED
- who-trs992-a5-ttsp-supplements.pdf Annex 1 (section): `-annex 1 example of form for monitoring system start up` - NOT EXPLAINED
- who-trs992-a5-ttsp-supplements.pdf _unnumbered:16 (unnumbered): `-revision` - NOT EXPLAINED
- who-trs992-a5-ttsp-supplements.pdf Annex 1 #2 (section): `-annex 1 form for reporting deviations and corrective action` - NOT EXPLAINED
- who-trs992-a5-ttsp-supplements.pdf Annex 1 A 1.3 #2 (clause): `+o t e c h r e p o r t s e s n o 9 9 2 2 0 1 5 supplement 9` - NOT EXPLAINED
- who-trs992-a5-ttsp-supplements.pdf Annex 1 #3 (section): `-annex 1 generic temperature accuracy check form` - NOT EXPLAINED
- who-trs992-a5-ttsp-supplements.pdf _unnumbered:24 (unnumbered): `+supplement 12` - NOT EXPLAINED
- who-trs992-a5-ttsp-supplements.pdf Annex 1 #4 (section): `-annex 1 packing a refrigerated vehicle` - NOT EXPLAINED
- who-trs992-a5-ttsp-supplements.pdf _unnumbered:28 (unnumbered): `-transport route profiling qualification technical supplement to model guidance for the storage and transport of time and temperature sensitive pharmaceutical products who technical report series no 961 2011 annex 9 contents` - NOT EXPLAINED
- who-trs992-a5-ttsp-supplements.pdf Annex 1 A 1.3.2 (clause): `+o t e c h r e p o r t s e s n o 9 9 2 2 0 1 5 supplement 15` - NOT EXPLAINED
- who-trs992-a5-ttsp-supplements.pdf _unnumbered:32 (unnumbered): `-environmental management of refrigeration equipment technical supplement to model guidance for the storage and transport of time and temperature sensitive pharmaceutical products who technical report series no 961 2011 annex 9 contents` - NOT EXPLAINED
- who-trs992-a5-ttsp-supplements.pdf Annex 1 #5 (section): `+9 contents acknowledgements abbreviations glossary | -montreal protocol non article 5 countries` - NOT EXPLAINED
- who-trs992-a5-ttsp-supplements.pdf page 13 (uncovered): `+acknowledgements abbreviations glossary 1 introduction 1.1 requirements` - NOT EXPLAINED
- who-trs992-a5-ttsp-supplements.pdf page 18 (uncovered): `+acknowledgements abbreviations glossary 1 introduction 1.1 requirements 1.2 objectives 1.3 target readership 2 guidance` - NOT EXPLAINED
- who-trs992-a5-ttsp-supplements.pdf page 21 (uncovered): `+acknowledgements abbreviations glossary 1 introduction 1.1 requirements 1.2 objectives` - NOT EXPLAINED
- who-trs992-a5-ttsp-supplements.pdf page 21 (uncovered): `+1.3 target readership 2 guidance` - NOT EXPLAINED
- who-trs992-a5-ttsp-supplements.pdf page 25 (uncovered): `+supplement 14 transport route profiling qualification technical supplement to` - NOT EXPLAINED
- who-trs992-a5-ttsp-supplements.pdf page 27 (uncovered): `+supplement 16 environmental management of refrigeration equipment technical supplement to` - NOT EXPLAINED
- who-trs992-a5-ttsp-supplements.pdf page 27 (uncovered): `+contents acknowledgements abbreviations glossary 1 introduction 1.1 requirements 1.2 objectives 1.3 target readership 2 guidance` - NOT EXPLAINED
- who-trs996-a4-app1-model-inspection-report.pdf Appendix 1 (section): `+o t e c h r e p o r t s e s n o 9 9 6 2 0 1 6 part 1 general information | +used for assessing compliance` - NOT EXPLAINED
- who-trs996-a4-app1-model-inspection-report.pdf Appendix 1 1 (clause): `+introduction | +the manufacturing activities | +where applicable` - NOT EXPLAINED
- who-trs996-a4-app1-model-inspection-report.pdf Appendix 1 1 #2 (clause): `-1 pharmaceutical describe the pharmaceutical quality system pqs in quality system` - NOT EXPLAINED
- who-trs996-a4-app1-model-inspection-report.pdf Appendix 1 2 #2 (clause): `+practices for pharmaceutical products | -practices | +implemented 3 sanitation and hygiene describe procedures and records relating to sanitation and hygiene | -implemented pharmaceutical products` - NOT EXPLAINED
- who-trs996-a4-app1-model-inspection-report.pdf Appendix 1 7 (clause): `+analysis and other activities` - NOT EXPLAINED
- who-trs996-a4-app1-model-inspection-report.pdf Appendix 1 8 (clause): `-self inspection a | +suppliers audits and approval a self inspection` - NOT EXPLAINED
- who-trs996-a4-app1-model-inspection-report.pdf Appendix 1 17 (clause): `+where applicable` - NOT EXPLAINED
- who-trs996-a4-app1-model-inspection-report.pdf Appendix 1 3 #3 (clause): `+part 4 outcome | +o t e c h r e p o r t s e s n o 9 9 6 2 0 1 6 part 5 list of gmp guidelines referenced in the inspection` - NOT EXPLAINED
- who-trs996-a4-app1-model-inspection-report.pdf Annex 3 (section): `-annex 3 who technical report series no 937 http www who int medicines publications pharmprep en index html | +due for planning purposes` - NOT EXPLAINED
- who-trs996-a4-app1-model-inspection-report.pdf page 9 (uncovered): `+1 pharmaceutical quality system describe the pharmaceutical quality system pqs in` - NOT EXPLAINED
- who-trs996-a4-app1-model-inspection-report.pdf page 16 (uncovered): `+risk category of the site` - NOT EXPLAINED
