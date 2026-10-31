# FDA work list

Build order and status for FDA, document by document (owner decision: regulator by regulator, FDA first; D17 pilot scope OSD + INJ).
Kept up to date by the working session. Status: not started / drafted / verified / in review / done.

An item ships only if it is proven: the automatic route (quote confirmed, all Layer 1 checks pass, both blind verifiers say correct) or the human route (confirmed in the review queue). Everything else is not shipped.

Columns: items = checklist items drafted; auto = items passing the automatic route; review = items in the owner's review queue.

## Group 1: regulations (eCFR XML, read directly; quotes exact by construction)

| # | Document | File | Priority | Plant types | Pages | Status | Items | Auto | Review |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 21 CFR Part 211 - CGMP for finished pharmaceuticals | `ecfr-21cfr211-2026-10-27.xml` | must | OSD, LIQ, SEMI, INJ | - | verified (60 of 60 sections) | 399 | 365 | 34 |
| 2 | 21 CFR Part 210 - CGMP in manufacturing processing packing or holding of drugs; general | `ecfr-21cfr210-2026-10-27.xml` | must | ALL | - | verified | 1 | 0 | 1 |
| 3 | 21 CFR 314.81 Other postmarketing reports (incl. field alert reports  annual reports) | `fda-cfr-21-314.81.xml` | must | OSD, LIQ, SEMI, INJ | - | verified | 104 | 91 | 13 |
| 4 | 21 CFR Part 11 Electronic Records; Electronic Signatures | `fda-cfr-21-part-11.xml` | must | ALL | - | verified | 48 | 45 | 3 |
| 5 | 21 CFR 314.70 Supplements and other changes to an approved NDA | `fda-cfr-21-314.70.xml` | should | OSD, LIQ, SEMI, INJ | - | verified | 78 | 53 | 25 |
| 6 | 21 CFR Part 200 General (incl. 200.10 contract facilities  200.50 ophthalmic sterility) | `fda-cfr-21-part-200.xml` | should | ALL | - | verified | 24 | 18 | 6 |
| 7 | 21 CFR Part 207 Establishment registration  drug listing | `fda-cfr-21-part-207.xml` | should | ALL | - | verified | 149 | 121 | 28 |
| 8 | 21 CFR Part 4 Regulation of combination products (Subpart A CGMP relevant for prefilled syringes/co-packaged; device QS parts not fetched) | `fda-cfr-21-part-4.xml` | should | INJ | - | verified | 64 | 27 | 37 |

## Group 2: FDA web pages (HTML, read directly)

| # | Document | File | Priority | Plant types | Pages | Status | Items | Auto | Review |
|---|---|---|---|---|---|---|---|---|---|
| 9 | Guide to Inspections of Dosage Form Drug Manufacturers - CGMPs | `fda-ora-guide-dosage-form-cgmps-1993.html` | must | OSD, LIQ, SEMI, INJ | - | not started | | | |
| 10 | Guide to Inspections of High Purity Water Systems | `fda-ora-guide-high-purity-water-1993.html` | must | ALL | - | not started | | | |
| 11 | Guide to Inspections of Lyophilization of Parenterals | `fda-ora-guide-lyophilization-parenterals-1993.html` | must | INJ | - | not started | | | |
| 12 | Guide to Inspections of Microbiological Pharmaceutical QC Laboratories | `fda-ora-guide-micro-qc-labs-1993.html` | must | ALL | - | not started | | | |
| 13 | Guide to Inspections of Oral Solid Dosage Forms Pre/Post Approval Issues | `fda-ora-guide-osd-pre-post-approval-1994.html` | must | OSD | - | not started | | | |
| 14 | Guide to Inspections of Pharmaceutical QC Laboratories | `fda-ora-guide-pharma-qc-labs-1993.html` | must | ALL | - | not started | | | |
| 15 | Guide to Inspections of Sterile Drug Substance Manufacturers | `fda-ora-guide-sterile-drug-substance-1994.html` | must | API, INJ | - | not started | | | |
| 16 | Guide to Inspections: Validation of Cleaning Processes | `fda-ora-guide-cleaning-validation-1993.html` | must | ALL | - | not started | | | |
| 17 | Questions and Answers on CGMP for Drugs: Buildings and Facilities | `fda-cgmp-qa-buildings-facilities.html` | must | ALL | - | verified | 16 | 13 | 3 |
| 18 | Questions and Answers on CGMP for Drugs: Control of Components and Drug Product Containers and Closures | `fda-cgmp-qa-components-containers-closures.html` | must | ALL | - | not started | | | |
| 19 | Questions and Answers on CGMP for Drugs: Equipment | `fda-cgmp-qa-equipment.html` | must | ALL | - | verified | 57 | 51 | 6 |
| 20 | Questions and Answers on CGMP for Drugs: General Provisions | `fda-cgmp-qa-general-provisions.html` | must | ALL | - | verified | 0 | 0 | 0 |
| 21 | Questions and Answers on CGMP for Drugs: Holding and Distribution | `fda-cgmp-qa-holding-distribution.html` | must | ALL | - | verified | 9 | 7 | 2 |
| 22 | Questions and Answers on CGMP for Drugs: Laboratory Controls | `fda-cgmp-qa-laboratory-controls.html` | must | ALL | - | not started | | | |
| 23 | Questions and Answers on CGMP for Drugs: Production and Process Controls | `fda-cgmp-qa-production-process-controls.html` | must | ALL | - | not started | | | |
| 24 | Questions and Answers on CGMP for Drugs: Records and Reports | `fda-cgmp-qa-records-reports.html` | must | ALL | - | not started | | | |
| 25 | Questions and Answers on CGMP for Drugs: Returned and Salvaged Drug Products | `fda-cgmp-qa-returned-salvaged.html` | must | ALL | - | not started | | | |
| 26 | CPG Sec. 490.200 Parametric Release of Parenteral Drug Products Terminally Sterilized by Moist Heat | `fda-cpg-490-200-parametric-release.html` | should | INJ | - | not started | | | |
| 27 | FDA alert to drug manufacturers on risk of benzene contamination | `fda-alert-benzene-contamination.html` | should | OSD, LIQ, SEMI | - | not started | | | |
| 28 | Guide to Inspections of Foreign Pharmaceutical Manufacturers | `fda-ora-guide-foreign-pharma-manufacturers-1996.html` | should | ALL | - | not started | | | |
| 29 | Inspection Technical Guide: Bacterial Endotoxins/Pyrogens | `fda-itg-bacterial-endotoxins-pyrogens.html` | should | INJ, API | - | not started | | | |
| 30 | Inspection Technical Guide: Expiration Dating and Stability Testing for Human Drug Products | `fda-itg-expiration-dating-stability.html` | should | ALL | - | not started | | | |
| 31 | Inspection Technical Guide: Water for Pharmaceutical Use | `fda-itg-water-pharmaceutical-use.html` | should | ALL | - | not started | | | |
| 32 | Guide to Inspections of Oral Solutions and Suspensions | `fda-ora-guide-oral-solutions-suspensions-1994.html` | must | LIQ | - | deferred (D17: LIQ/SEMI or API only) | | | |
| 33 | Guide to Inspections of Topical Drug Products | `fda-ora-guide-topical-drug-products-1994.html` | must | SEMI | - | deferred (D17: LIQ/SEMI or API only) | | | |

## Group 3: guidance PDFs (text first; page images only for tables and figures)

| # | Document | File | Priority | Plant types | Pages | Status | Items | Auto | Review |
|---|---|---|---|---|---|---|---|---|---|
| 34 | Container and Closure System Integrity Testing in Lieu of Sterility Testing as a Component of the Stability Protocol for Sterile Products | `fda-guidance-cci-in-lieu-of-sterility-2008.pdf` | must | INJ | 9 | not started | | | |
| 35 | Contract Manufacturing Arrangements for Drugs: Quality Agreements | `fda-guidance-quality-agreements-2016.pdf` | must | ALL | 16 | not started | | | |
| 36 | Control of Nitrosamine Impurities in Human Drugs (Rev 2) | `fda-guidance-nitrosamine-control-2024.pdf` | must | ALL | 46 | not started | | | |
| 37 | Field Alert Report Submission: Questions and Answers | `fda-guidance-field-alert-report-qa-2021.pdf` | must | OSD, LIQ, SEMI, INJ | 13 | not started | | | |
| 38 | Guidance: Sterile Drug Products Produced by Aseptic Processing - CGMP | `fda-aseptic-2004.pdf` | must | INJ | 63 | not started | | | |
| 39 | Non-Penicillin Beta-Lactam Drugs: A CGMP Framework for Preventing Cross-Contamination | `fda-guidance-npbl-cross-contamination-2013.pdf` | must | ALL | 10 | not started | | | |
| 40 | Part 11  Electronic Records; Electronic Signatures - Scope and Application | `fda-guidance-part11-scope-application-2003.pdf` | must | ALL | 12 | not started | | | |
| 41 | Pyrogen and Endotoxins Testing: Questions and Answers | `fda-guidance-pyrogen-endotoxins-qa-2026.pdf` | must | INJ, API | 12 | not started | | | |
| 42 | Quality Systems Approach to Pharmaceutical CGMP Regulations | `fda-guidance-quality-systems-approach-2006.pdf` | must | ALL | 32 | not started | | | |
| 43 | Testing of Glycerin  Propylene Glycol  Maltitol Solution  HSH  Sorbitol Solution and Other High-Risk Drug Components for DEG and EG | `fda-guidance-deg-eg-high-risk-components-2023.pdf` | must | LIQ, SEMI, OSD | 11 | not started | | | |
| 44 | ANDAs: Stability Testing of Drug Substances and Products | `fda-guidance-anda-stability-2013.pdf` | should | ALL | 5 | not started | | | |
| 45 | Analytical Procedures and Methods Validation for Drugs and Biologics | `fda-guidance-analytical-procedures-validation-2015.pdf` | should | ALL | 18 | not started | | | |
| 46 | Changes to an Approved NDA or ANDA | `fda-guidance-changes-approved-nda-anda-2004.pdf` | should | OSD, LIQ, SEMI, INJ | 40 | not started | | | |
| 47 | Circumstances that Constitute Delaying  Denying  Limiting  or Refusing a Drug or Device Inspection | `fda-guidance-delaying-denying-inspection-2024.pdf` | should | ALL | 13 | not started | | | |
| 48 | Conducting Remote Regulatory Assessments Questions and Answers | `fda-guidance-remote-regulatory-assessments-2025.pdf` | should | ALL | 18 | not started | | | |
| 49 | Container Closure Systems for Packaging Human Drugs and Biologics | `fda-guidance-container-closure-systems-1999.pdf` | should | ALL | 56 | not started | | | |
| 50 | Elemental Impurities in Drug Products | `fda-guidance-elemental-impurities-2018.pdf` | should | OSD, LIQ, SEMI, INJ | 11 | not started | | | |
| 51 | Guidance: Data Integrity and Compliance With Drug CGMP - Q&A | `fda-data-integrity-2018.pdf` | should | ALL | 17 | not started | | | |
| 52 | Guidance: Investigating Out-of-Specification (OOS) Test Results | `fda-oos-2022.pdf` | should | OSD, LIQ, SEMI, INJ, API | 17 | not started | | | |
| 53 | Guidance: Process Validation - General Principles and Practices | `fda-process-validation-2011.pdf` | should | OSD, LIQ, SEMI, INJ, API | 22 | not started | | | |
| 54 | Initiation of Voluntary Recalls Under 21 CFR Part 7  Subpart C | `fda-guidance-voluntary-recalls-initiation-2022.pdf` | should | ALL | 13 | not started | | | |
| 55 | Pharmaceutical Components at Risk for Melamine Contamination | `fda-guidance-melamine-components-2009.pdf` | should | ALL | 8 | not started | | | |
| 56 | Product Recalls  Including Removals and Corrections | `fda-guidance-product-recalls-2020.pdf` | should | ALL | 18 | not started | | | |
| 57 | Recommended Acceptable Intake Limits for Nitrosamine Drug Substance-Related Impurities | `fda-guidance-nitrosamine-ndsri-ai-limits-2023.pdf` | should | ALL | 28 | not started | | | |
| 58 | Submission Documentation for Sterilization Process Validation in Applications for Human and Veterinary Drug Products | `fda-guidance-sterilization-validation-submission-1994.pdf` | should | INJ | 23 | not started | | | |
| 59 | The Use of Mechanical Calibration of Dissolution Apparatus 1 and 2 - CGMP | `fda-guidance-dissolution-mechanical-calibration-2010.pdf` | should | OSD | 8 | not started | | | |
| 60 | Policy for Testing of Alcohol (Ethanol) and Isopropyl Alcohol for Methanol | `fda-guidance-methanol-testing-alcohol-2023.pdf` | must | LIQ, SEMI | 12 | deferred (D17: LIQ/SEMI or API only) | | | |
| 61 | Reformulating Drug Products That Contain Carbomers Manufactured With Benzene | `fda-guidance-benzene-carbomers-2023.pdf` | should | SEMI, LIQ | 13 | deferred (D17: LIQ/SEMI or API only) | | | |

## Group 4: compliance programs (long PDFs with tables; page images on table pages)

| # | Document | File | Priority | Plant types | Pages | Status | Items | Auto | Review |
|---|---|---|---|---|---|---|---|---|---|
| 62 | Compliance Program 7346.832 Preapproval Inspections | `fda-cp-7346-832-preapproval-inspections.pdf` | must | ALL | 56 | not started | | | |
| 63 | Compliance Program 7356.002 Drug Manufacturing Inspections | `fda-cp-7356-002-drug-manufacturing-inspections.pdf` | must | ALL | 44 | not started | | | |
| 64 | Compliance Program 7356.002A Sterile Drug Process Inspections | `fda-cp-7356-002a-sterile-drug-process.pdf` | must | INJ, API | 54 | not started | | | |
| 65 | Compliance Program 7356.021 Drug Quality Reporting System and NDA Field Alert Reporting | `fda-cp-7356-021-dqrs-field-alerts.pdf` | should | OSD, LIQ, SEMI, INJ | 15 | not started | | | |
| 66 | Compliance Program 7356.843 Postapproval Inspections | `fda-cp-7356-843-postapproval-inspections.pdf` | should | ALL | 50 | not started | | | |
| 67 | Compliance Program 7356.002F Active Pharmaceutical Ingredients | `fda-cp-7356-002f-api.pdf` | must | API | 41 | deferred (D17: LIQ/SEMI or API only) | | | |

## Not in this build

33 FDA documents marked `reference` in `sources/catalog.csv` are kept for context only and are not drafted into checklist items.
