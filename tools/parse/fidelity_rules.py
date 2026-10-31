"""Writes library/fidelity-explanations.csv (D40): mechanical verdicts first, then the categorised rules below.

Each rule: (source regex, ref regex, discrepancy regex, reason). The first matching rule explains a flag; the CSV
row quotes the exact discrepancy, so the explanation lapses when the stored text changes. Unmatched flags are
printed for review.
"""
import csv, json, re, sys
ROOT = str(__import__('pathlib').Path(__file__).resolve().parents[2])
doc = json.load(open(f'{ROOT}/library/fidelity-report.json'))

B = "0b"  # fixes planned in the parser-limits work
R = []


def rule(src, ref, disc, reason):
    R.append((re.compile(src), re.compile(ref), re.compile(disc), reason))


# ---- defects of the stored text (fix in 0b) ----
rule(r"ema-nitrosamines", r"Q\d+|_unnumbered:2", r"(-questions and answers for marketing authorisation holders applicants on the chmp|-questions|-answers for marketing authorisation holders applicants on the chmp|\+[^|]*|-[ivx]+|-aii.*)( \| .*)?",
     f"Parser defect ({B}): the running page header 'Questions and answers for marketing authorisation "
     "holders/applicants on the CHMP Opinion...' is stored inside the answer at each page break (and the footer "
     "'EMA/409815/2020 Page n/27' the second engine keeps); answer text intact.")
rule(r"india-schedule-m", r"Part XIII 7 #2", r"-manoj kumar digitally signed.*",
     f"Parser defect ({B}): the digital-signature stamp of the gazette signatory is stored inside the clause; "
     "clause text intact.")
rule(r"india-schedule-m|india-drugs-rules", r"Part III 9\.1", r"-dop injection.*",
     f"Parser defect ({B}): the labels of the HVAC schematic figure ('Shut- off Damper', 'VFD', 'EXHAUSTAI') are "
     "stored in the clause in layout order and glued; figure text, not regulatory prose.")
rule(r"india-schedule-m", r"Part I 1\.2", r"-7986 gi 2023 148",
     f"Parser defect ({B}): the gazette's page-reference line '7986 GI/2023 (148)' is stored in the clause.")
rule(r"eu-written-confirmation", r"2|page 1", r".*",
     f"Parser defect ({B}): the page footer (the Commission's address in French and Dutch) is interleaved with "
     "footnote 2 and stored glued onto the clause; the clause's own sentence is intact.")
rule(r"pics-pi041-1", r"8\.10\.2|2 #2", r".*",
     f"Parser defect ({B}): known limitation - the numbered table rows '1. Expectation' / '2. Expectation' "
     "start clauses that hold following text, so this clause's text is out of order against the page.")
rule(r"pics-pi041-1", r"8\.4|8\.6\.1|9\.3|9\.4", r".*",
     f"Parser defect ({B}): the section's lead-in and the table title ('Item: Generation') sit between the "
     "clause and its table rows; the clause boundary falls inside the heading.")
rule(r"pics-pi011-3", r"6\.2|11|24|page (12|39)", r".*",
     f"Parser defect ({B}): figure text (system diagram, V-model) and a boxed note stored in the wrong clause "
     "order; the words are stored, their place is not.")
rule(r"pics-pi011-3", r"9\.1|20\.1|21\.\d|14\.2|15 #2", r"\+\d{1,2}",
     f"Parser defect ({B}): a footnote reference number sits inside the clause's last line in the PDF and the "
     "parser drops it; no regulation word changes.")
rule(r"india-cdsco", r"Table \d+ .*", r"-\d{1,2}(\.\d+)? .*",
     f"Parser defect ({B}): the table extractor merges the section-heading row printed below this row (e.g. "
     "'26 Sterilization', no ruled line between them) into this row, or the row continues across a page; the words "
     "are all in the PDF, in the next row.")
rule(r"who-trs929-a4-sampling", r"Annex 4 \d\.\d", r"-\d\.\d",
     f"Parser defect ({B}): the contents list of Annex 4 is stored as clauses ('1.2 Glossary 61'); contents "
     "entries, not requirements.")
rule(r"pics-pi009-4|pics-pi023-2|pics-pi028-2|pics-pi030-1|pics-pi038-2|pics-pi043-1|pics-pi052-1",
     r"Table .*", r"-.*",
     f"Aide-memoire table layout ({B} review): the stored row includes the repeated column-header row "
     "('Area of operation / Items / Notes / Crucial questions / Supporting documents') or a cell continued from "
     "the previous page, which the second engine places outside the row's band; no requirement word changed.")
rule(r"pics-pi0(09|23|28|30)", r"page \d+", r"\+.*(supporting documents|items notes|quality management system|building and facilities|packaging and labelling|review of oos).*",
     "Aide-memoire page layout: repeated column headers and section headings of the table, which the stored rows "
     "hold once per table.")

# ---- layout effects of the two engines (no stored word wrong) ----
# ---- reviewed flags (D39 review of the unmatched list) ----
rule(r"ema-hbel-qa-cross-contamination", r"Q2", r"-30 churchill place canary wharf london .* reproduction is authorised provided the source is acknowledged",
     f"Parser defect ({B}): the page-1 footer (EMA postal address, telephone, copyright line) is stored at the end of "
     "answer Q2; the answer's own words are intact.")
rule(r"ema-sterilisation-guideline", r"4\.1\.5", r"-4\.1\.5 sterile filtration the filter data to be provided in the quality dossier is summarised in table 3 table 3 filter data to be provided in the quality dossier for filters in contact with the drug product or components of the drug product",
     "The clause's opening sentence and the title of Table 3 are printed on page 12, above the running header and the "
     "table body (stored as its own table rows); the check aligns the clause only from the table footnotes on, so "
     "the opening reads as absent. Checked: it is printed, word for word.")
rule(r"ema-water-quality-guideline", r"Table 5 AS is in solution, not sterile, and…", r"-wfi",
     f"Parser defect ({B}): this cell has two sub-rows (any step except final isolation: Purified Water; final "
     "isolation and purification: WFI); the stored row merges them, so 'WFI' is no longer tied to its step. "
     "'WFI' lies below the row's band, hence the flag.")
rule(r"eu-anx08_en", r"Annex 8 3", r"\+n",
     f"Parser defect ({B}): the page header '■ Annex 8 Sampling of starting and packaging materials ___' is stored "
     "inside clause 3 at the page break (pdfminer reads the '■' glyph as 'n'); clause words intact.")
rule(r"eu-chapter_3", r"3 Principle", r"\+p remises general 3\.1( \| -general)?",
     f"Parser defect ({B}): the section headings 'PREMISES / General' are stored at the end of the Principle "
     "clause; pdfminer reads the small-capital heading as 'P remises'. No regulation word changes.")
rule(r"eu-chapter_3", r"3\.33", r"\+e quipment 3\.34 manufacturing",
     f"Parser defect ({B}): the section heading 'EQUIPMENT' is stored at the end of clause 3.33; pdfminer reads the "
     "small-capital heading as 'E quipment'. No regulation word changes.")
rule(r"eu-2015-c95-02-excipients", r"Chapter 2 2\.3|Chapter 2 2\.6|Chapter 4 4\.1", r"(-|\+)(21\.3\.2015|c 95 1[0-3])( \| (-|\+)(21\.3\.2015|c 95 1[0-3])){3}",
     f"Parser defect ({B}): the Official Journal running header ('21.3.2015 EN Official Journal of the European "
     "Union C 95/11') is stored inside the clause at each page break; clause words intact.")
rule(r"eu-p3-gmp-mah-reflection-paper", r"5\.2", r"\+manufac the document titled guidance for the template for the qualified person s declaration concerning gmp compliance of active substance manufacture also addresses the responsibility of the mah to ensure that a written confirmation of compliance of the",
     "The PDF prints a stray, cut-off copy of one paragraph of 5.2 at the foot of page 12 (ending 'manufac'); the "
     "paragraph is stored once, in full, in its place.")
rule(r"fda-aseptic-2004", r"IV", r"-classificationsa \| \+classifications a clean area classification 0\.5 um particles ft 3 iso designation b > 0\.5 μm particles m 3 microbiological active air action levels c cfu m 3 microbiological settling plates action levels c d diam 90 mm cfu 4 hours 100 5 3,520 1 e 1 e 1000 6 35,200 7 3 10,000 7 352,000 10 5 100,000 8 3,520,000 100 50",
     f"Parser defect ({B}): the table title's footnote letter is glued onto the last word ('Classificationsa'). "
     "The body of Table 1 (air classifications) is stored as its own table rows with the same values.")
rule(r"fda-cp-7346-832", r"Part II 2\.A", r".*|-yes risk assessment supports determination pai not needed of pai objectives no no risk assessment supports potential use of alternative tools ats in lieu of inspection yes \| -no yes \| \+pai needed risk assessment supports determination of pai objectives yes yes no no no risk assessment supports potential use of alternative tools ats in lieu of inspection yes",
     "Labels of the PAI decision-tree figure (boxes 'PAI Needed' / 'PAI Not Needed', arrows Yes/No) read in another "
     "order by the two engines; all labels are stored, figure text not prose.")
rule(r"fda-cp-7346-832", r"_unnumbered:6", r".*",
     f"Parser defect ({B}): the two-column acronym list is read across both columns line by line, so wrapped "
     "definitions are split from their acronyms (e.g. 'corrective action and preventive FD&C Act: ... action'); "
     "the clause also starts with a stray contents line ('Attachment D: ...'). All words are stored.")
rule(r"fda-cp-7346-832", r"Attachment B|page 53", r".*",
     f"Parser defect ({B}): the page 53-54 row 'Sterility control and assurance' of Table 3 was not recognised as a "
     "table row; its four columns are stored inside Attachment B interleaved line by line (garbled), followed by "
     "the table's acronym list and a footnote. All words are stored, their order is not usable.")
rule(r"fda-cp-7346-832", r"Table 3 Novel excipient manufacturing \(e\.g\.…|Table 3 Manufacturing and control of finished… #[24]|Table 4 Manufacturing and control of finished…", r"-.*",
     "A long table row of Attachment B whose example cells run below the row's band or onto the next page; every "
     "word the check misses is printed on the row's pages (verified), the engines only band the row differently.")
rule(r"fda-cp-7346-832", r"page (4[89]|5[0-2])", r"\+((addressing quality )?(related topics via an )?integrated approach )?quality topic integrated approach",
     "Table 3's title and column header row ('Quality Topic / Integrated Approach') repeated on each continuation "
     "page; stored once with the table.")
rule(r"fda-cp-7346-832", r"page 47", r"\+resolve outstanding quality issues for",
     "Cell text of the first Table 3 row ('...to resolve outstanding quality issues.') stored in that row; pdfminer "
     "reads it joined to the 'For example' cell below.")
rule(r"fda-guidance-container-closure-systems-1999", r"I|II\.A|II\.B|II\.C\.2|III\.A|III\.B\.[12]|III\.C\.[234]|III\.E\.[12]|III\.F(\.[13])?|III\.G|VI\.[AB]|Attachment [ABCE]|page 4", r".*",
     f"Parser defect ({B}): footnote texts, table notes (a-d) and the attachment page labels ('A-1', 'C-1') are "
     "stored inside the clause where the page breaks, often mid-sentence and some without their footnote number "
     "(e.g. 3.C.4 'using the container [footnote 18] closure systems'); pdfminer reads them at the page foot. "
     "Checked: no word of the guidance is lost or changed.")
rule(r"fda-guidance-container-closure-systems-1999", r"Table 1 Highest|Table 2 Route of Administration/ Dosage Form|Table 2 Oral Tablets and Oral \(Hard and Soft…", r"-(suspensions a|delivery|capsules)",
     "The last word of a wrapped table cell is printed on a second line below the row's band; the stored row holds "
     "it in its place.")
rule(r"who-trs992-a5-ttsp", r"1\.1", r"\+1 \| -table a 5\.1 continued title section s",
     f"Parser defect ({B}): Table A5.1 (supplement titles and model-guidance sections) is split: rows 1, 3, 5, 7 "
     "are stored as text of clause 1.1 together with footnote 1's URL and the 'Table A5.1 continued' heading, the "
     "even rows and rows 8-16 as table rows. All entries are stored.")
rule(r"who-trs992-a5-ttsp", r"7", r"\+2 \| \+o t e c h r e p o r t s e s n o 9 9 2 2 0 1 5 supplement 1",
     f"Parser defect ({B}): footnote 2's URL and the start of Supplement 1's reproduced contents page are stored at "
     "the end of clause 7; the 'Supplement 1' tab label and the vertical series title are not stored.")
rule(r"who-trs992-a5-ttsp", r"_unnumbered:(3|7|16|24)|Annex [123]( #[2-5])?|Annex [123] A [0-9.]+( #2)?", r"((\+|-)(o t e c h r e p o r t s e s n o 9 9 2 2 0 1 5 )?(supplement \d+|annex [123]|revision)( \| )?)+",
     "Reproduced contents pages of the 16 technical supplements: the parser stores their entries as clauses or "
     "sections; the 'Supplement N' tab label, the vertical series title and a repeated 'Annex N' entry heading are "
     "read in another place. Contents listing, not requirements.")
rule(r"who-trs992-a5-ttsp", r"page (13|18|21|27)", r"\+(acknowledgements abbreviations glossary 1 introduction 1\.1 requirements( 1\.2 objectives( 1\.3 target readership 2 guidance)?)?|1\.3 target readership 2 guidance)",
     "Entries of the reproduced supplement contents pages (Acknowledgements, Glossary, 1.1 Requirements...) that "
     "repeat on every supplement and that the parser drops as repeated text; contents listing, not requirements.")
rule(r"ich-q3c-r9", r"Part I 3\.3|Part I Appendix 3|Part (II|III|IV #2|V|VI)|_unnumbered:[36]|Part VI 6|page 29", r".*",
     f"Parser defect ({B}): the PDE and limit equations are stored flattened line by line, so numerators, "
     "denominators and results are separated (e.g. '225 x 50 PDE = = 45 mg/day 5 x 10 x 1 x 1 x 5'); pdfminer "
     "reads the same equations letter-spaced and with the factors in reverse order. Checked against poppler: every "
     "number is stored and unchanged.")
rule(r"ich-q3c-r9", r"Part (II 7\.2|III 5\.3)", r"-(7\.2 x 1000 limit 720|5\.3 x 1000 limit 530) ppm 10",
     f"Parser defect ({B}): the numerator of the limit equation ('7.2 x 1000' / '5.3 x 1000') is taken as a clause "
     "number, so a bogus clause starts there and holds the rest of the section; values unchanged.")
rule(r"ich-q3c-r9", r"Part I Appendix 1( [235])?", r".*|((-|\+)(cl|o o 1,4 dioxane|1,4 dioxane|1,2 ethanediol|class 2 n o|o class|methyltetrahydrofuran 4 2|tetrahydrosylvan|methyltetrahydrofuran 4 tetrahydrosylvan|dioxide s|dioxide s o o|oxacyclopentane o|o oxacyclopentane|xylol ch 3|ch 3 xylol)( \| )?)+",
     f"Parser defect ({B}): Appendix 1's solvent table is stored as running text, and its footnotes 2, 3 and 5 "
     "start clauses ('2', '3', '5') that hold the following table rows. The flagged words are atom labels of the "
     "structure drawings (O, Cl, CH3) and wrapped 'Other names' read in another order; no name or class changed.")
rule(r"ich-q3d-r2", r"Appendix 5 5\.[23]", r"(-manufacturing drug equipment substance elemental impurities in drug product water container excipients closure system|\+elemental impurities in drug product container closure system drug substance excipients manufacturing equipment water)",
     "Labels of the fishbone figure (sources of elemental impurities) read in another order and assigned to the "
     "neighbouring clause; figure text, all labels stored.")
rule(r"ich-q3d-r2", r"Appendix 5 7", r"\+day g product drug of amount daily day g \| -day \| \+g ion \| -ion g g \| -daily amount of drug product g day \| -pde g day c \| \+1 k k \| -k \| \+c day g pde \| -k 1",
     f"Parser defect ({B}): Equation 1 (concentration = PDE / daily amount of drug product) is stored flattened, "
     "numerator and denominator on separate lines; pdfminer reads the symbols in reverse order. No value changes.")
rule(r"ich-q3d-r2", r"Table 1 Q3D #3", r"-2013",
     "The year of the date cell ('30 September 2013') wraps below the row's band; the stored row holds the full date.")
rule(r"ich-q3d-r2", r"Table (28|29) header|Table 3[01] Component", r"-component( potential)?( concentration μg)?",
     "Header cells ('Component', 'Concentration (µg/g)') printed vertically centred across two header lines, "
     "outside the band of the stored header row; header words, not values.")
rule(r"ich-q3d-r2", r"Table 37 3 Pd", r"-3",
     f"Parser defect ({B}): the footnote mark 3 printed above 'Pd' is stored as the start of the row label "
     "('3 Pd'); the element and its values are unchanged.")
rule(r"ich-q3d-r2", r"page 5", r"\+2 s cope",
     "Heading '2. SCOPE' in small capitals, read by pdfminer as 's cope'; stored as the start of clause 2.")
rule(r"ich-q8-q9-q10-qa-r4", r"page \d+", r"\+approval questions answers",
     "Running title words of the Q&A document ('...approval: Questions & Answers') repeated on each page; not "
     "regulation text.")
rule(r"who-trs1060-a3-excipients", r"Appendix 1 7\.2 #2", r"-annex x 3 table continued wh o expert committee on specifications for pharmaceutical preparations fifty eighth report table continued",
     f"Parser defect ({B}): the running headers of the landscape table pages ('Annex 3', 'WHO Expert Committee... "
     "Fifty-eighth report') and two 'Table continued' captions are stored inside clause 7.2.")
rule(r"who-trs1060-a3-excipients", r"Appendix 1 7\.([3-9]|10)( #2)?", r".*|\+(equipment risk|materials risk|utilities risk|personnel risk|risk production|repackaging risk|storage risk|risk distribution)",
     f"Parser defect ({B}): the two-column risk table under the risk statement is stored as clause text without its "
     "header row ('Equipment | Risk'), and wrapped left-column labels are split by the right column ('Materials of "
     "Not smooth... construction'). All words stored.")
rule(r"who-trs1060-a3-excipients", r"Table 1 Premises|page 35", r"(-location flow personnel flow access services|\+material flow personnel flow location access services)",
     "Failure-mode labels of the landscape FMEA table (Location, Material flow, Personnel flow, Access, Services) "
     "read in another order; all stored in the row.")
rule(r"who-trs1060-a3-excipients", r"page 36", r"\+who technical report series no 1060 2025",
     "The series footer printed sideways on a landscape table page; not regulation text.")
rule(r"india-schedule-m-2023", r"page (42|60|81|9[4569]|10[23]|11[79]|12[37])", r"\+((\d+(\.\d+)?|[ivx]+) ?)+",
     "Numbers and Roman list numerals left on the Hindi (Devanagari) pages of the bilingual gazette once the "
     "Devanagari words are dropped (checked on pages 42, 60, 119, 127); the English text is stored from its own "
     "pages.")
rule(r"india-schedule-m-2023", r"page 1", r"\+(gi 2023 1|extraordinary part ii section 3 sub section i published by authority no 738 new delhi thursday december 28 2023 pausha 7 1945 cg dl e 05012024 251166 cg dl e 05012024 251166)",
     "Gazette masthead on the cover page (registration number, 'EXTRAORDINARY Part II Section 3', issue number "
     "and date); publication data, not regulation text.")
rule(r"who-trs996-a4-app1-model-inspection-report", r"Appendix 1|Appendix 1 (1|2 #2|3 #2|4 #2|7|8|16|17|3 #3)|Annex 3", r".*",
     f"Parser defect ({B}): the two-column model report form is stored line by line across both columns, so wrapped "
     "item labels are split by the description text ('2. Good manufacturing Briefly describe how the elements of "
     "GMP are practices for implemented pharmaceutical products'); the 'Part N' headings are stored as separate "
     "table rows and footnote references start clauses. All words are stored.")
rule(r"who-trs961-a2-micro-labs", r"Annex 2 Appendix [1-4]", r"-appendix [1-4]",
     "Contents-page entries ('Appendix 1 Examples of zones...') stored as sections; pdfminer reads the 'Appendix N' "
     "label apart from its title. Contents listing, not requirements.")
rule(r"who-trs961-a2-micro-labs", r"_unnumbered:5|page 25", r".*",
     f"Parser defect ({B}): the titles and notes of Appendices 1-4 and the whole Appendix 5 (reference-culture "
     "flowchart and its closing requirement 'All parts of the process should be fully documented...') are stored "
     "inside the 'Further reading' clause, the flowchart boxes in layout order. All words are stored.")
rule(r"who-trs961-a2-micro-labs", r"Table 2 Laboratory", r"-other",
     "A wrapped cell line ('Clean and disinfect other surfaces') printed below the row's band; stored in the row.")
rule(r"who-trs1010-a10-stability", r"Appendix 3 1\.2", r"\+1\.3",
     f"Parser defect ({B}): the section heading 'General principles' is stored at the end of clause 1.2; pdfminer "
     "reads the next clause number '1.3' beside it. No word changes.")
rule(r"who-trs1010-a10-stability", r"Appendix 3 2\.[12]\.7\.[1-4]|Appendix 2 [12]|Appendix 3", r".*",
     f"Parser defect ({B}): the storage-condition and labelling-statement tables (A10.1-A10.4 and the study tables "
     "of 2.1.7/2.2.7) are stored as running text with multi-line cells interleaved line by line (e.g. 'or 12 months "
     "or 6 months as 30 °C ... or described in point 2.1.7'), so values are separated from their conditions; the "
     "running footer and 'Table continued' captions are inside. All words and values are stored.")
rule(r"pics-pe009-18-annexes", r"Annex (2A|4|10)", r".*|-(i|ii|iii) \| \+(ii|iii|iv)",
     f"Parser defect ({B}): contents-page entries stored as sections, with the contents page footer "
     "('PE 009-18 (Annexes) -i- 24 September 2026') inside; pdfminer reads the next page's footer numeral. Contents "
     "listing, not requirements.")
rule(r"pics-pe009-18-annexes", r"Annex 1 Glossary", r"\+− \| \+−",
     "Exponent minus: the stored text has '≤10-6' and '1 x 10-6' with a hyphen where the PDF prints a superscript "
     "minus; the value is unchanged. (Same glossary: 10⁷ CFU/cm² is stored as '107', the known superscript "
     "limitation, 0b.)")
rule(r"pics-pe009-18-annexes", r"Annex 2A 3|Annex 20 15", r".*",
     "Labels of a flow diagram (Annex 2A ATMP manufacturing figure; Annex 20 Figure 1 QRM process) stored in "
     "layout order; pdfminer reads the boxes in another order. Figure text, all labels stored.")
rule(r"pics-pe009-18-annexes", r"Annex 14 10", r"-annex 14 manufacture of products derived from human blood or plasma 2 for collection and regulatory submission of data information for plasma for fractionation annex 14 manufacture of products derived from human blood or plasma b other relevant documents reference should be made to the latest revisions of these documents for current guidance annex 15 qualification and validation",
     f"Parser defect ({B}): the Addendum's running page header ('Annex 14 Manufacture of products derived from "
     "human blood or plasma') and the next annex's title ('Annex 15 Qualification and validation') are stored "
     "inside clause 10; the Addendum's tables are stored as table rows.")
rule(r"fda-guidance-quality-systems-approach-2006", r"IV\.B\.3", r"\+21 cfr cgmp regulations related to resources quality system element regulatory citation .*",
     "The table 'CGMP Regulations Related to Resources' printed within the clause's pages is stored as its own table "
     "rows (Table 2), with the same citations; the check does not credit it inside the clause.")
rule(r"fda-guidance-quality-systems-approach-2006", r"Table 1 row 1|Table 2 3\. Facilities and Equipment|Table 4 1\. Design and Develop Product and…|Table 4 2\. Examine Inputs|Table 5 3\. Risk Assessment", r"-(system element|3 and buildings and 211\.28 c|develop|211\.122 211\.125|3)",
     "Wrapped cell lines (header 'Quality System Element', continued citations '211.122, 211.125', the item "
     "number) printed outside the row's band; stored in the row unchanged. (The PDF itself prints '211.58, 211.173' "
     "twice, overlapping, in Table 2 row 3.)")
rule(r"ich-q7-qa", r"Glossary", r"-20 glossary",
     "Heading '20. GLOSSARY' (a section with no text of its own in this Q&A) read by pdfminer away from the next "
     "heading; stored once as the section heading.")
rule(r"ich-q7-qa", r"Table 1[89] header", r"-questions answers",
     "Header cells 'Questions' / 'Answers' printed vertically centred over two lines, outside the stored header "
     "row's band; header words.")
rule(r"ich-q7-qa", r"Table 3[01] row 1", r"-introduction quality personnel buildings facilities process equipment documentation records 7 8 production process packaging identification labelling intermediates storage distribution manufacturers other ich guidelines",
     "Column headers of the Annex matrix (ICH Q7 section titles 1-19) printed rotated; pdfminer reads them letter "
     "by letter, so the stored header row's words are not found in its band. Header text, not requirements.")
rule(r"fda-guidance-nitrosamine-control-2024", r"III\.A(\.2)?|III\.B\.2", r".*|(-1 hno \| -n n o x n n o n o r 2 r 2|\+api \| -n h api n n o n o)",
     "Atom labels of the reaction-scheme figures (Figures 1 and 3: R1, R2, N, H, NO, HNO2, API) read in another "
     "order; figure text, not prose.")
rule(r"fda-guidance-nitrosamine-control-2024", r"Table 1 𝑛𝑛𝑖𝑖=2 𝑋𝑋𝑋𝑋|Table 1 ∑ 𝐴𝐴𝐴𝐴𝐴𝐴 ∗ 100% ≤ 100%", r"-(nnii xxxx|aaaaaa)",
     f"Parser defect ({B}): the total-nitrosamine formula (sum of Xi/AIi x 100% ≤ 100%) is stored as two bogus "
     "table rows of doubled math-italic glyphs ('𝑛𝑛𝑖𝑖=2 𝑋𝑋𝑋𝑋'); the formula is unreadable in the stored text, "
     "the definitions of Xi and AIi below it are intact.")
rule(r"who-trs957-a3-hazardous", r"Annex 3 9\.3", r"-figure 1 typical airflow pattern for contaminant p p p p",
     f"Parser defect ({B}): the caption and labels of Figure 1 ('Typical airflow pattern for contaminant', '•p') are "
     "stored inside the clause mid-sentence ('where HEPA filters are [Figure 1 ...] mentioned'); pdfminer reads the "
     "printer's slug 'TRS 957.indd 201' there instead. No clause word changes.")
rule(r"who-trs957-a3-hazardous", r"Annex 3 11\.1", r"-e shut off vfd damper exhaust \| \+m 11\.2 .* \| -fan secondary m m m filter vfd velocity sensor v m m m \| \+pre fi ltration may also be required to prolong the life of the \| -v variable frequency drive filte.*",
     f"Parser defect ({B}): the labels of Figure 2 (safe-change filter bypass schematic: 'Shut-off Damper', 'VFD', "
     "'EXHAUST AIR FAN', '•p') are stored in the clause in layout order and glued; figure text. Clause 11.2's text, "
     "read by pdfminer beside the figure, is stored in 11.2.")
rule(r"who-trs957-a3-hazardous", r"Annex 3 11\.6", r"\+fi lter condition 11\.7( \| -condition)?",
     "Words of the next clause (11.7, 'filter condition') read by pdfminer beside this clause's last line; stored in "
     "11.7.")
rule(r"who-trs957-a3-hazardous", r"Annex 3 13", r"-effluent treatment",
     "Heading '13. Effluent treatment' set with an 'ffl' ligature that pdfminer reads apart from the number; stored "
     "heading unchanged.")
rule(r"who-trs1052-a4-qc-labs", r"Appendix 1", r"-who technical report series no 1052 2024 \| .*",
     f"Parser defect ({B}): the equipment lists of Appendix 1 are stored both as table rows and as the section's "
     "text, and the running footer 'WHO Technical Report Series No. 1052, 2024' is stored inside the section; the "
     "list headings ('First stage laboratory (continued)') are stored as table rows.")
rule(r"who-trs1052-a4-qc-labs", r"Appendix 2|Appendix 3 1 #2|Appendix 3 5 #2", r".*|(-tg \| \+o t e c h r e p o r t s e s n o 1 0 5 2 2 0 2 4 \| -uitg \| \+tg|-umeas \| \+u tg meas \| \+u \| -umeas \| \+meas)",
     "Symbols with subscripts and superscripts (U with 'tg' above and 'i' or 'meas' below) are stored with the "
     "letters glued ('Uitg', 'Umeas'), as poppler prints them; pdfminer reads the sub- and superscript apart. Known "
     "notation limitation (0b: keep as U_i^tg); no value changes.")
rule(r"who-trs1019-a2-hvac-nonsterile-part2", r"4\.2|7|7\.1", r"(\+(w h o t e c h r e p o r t s e s n o 1 0 1 9 2 0 )?fig a 2\.\d+( \| )?)+",
     f"Parser defect ({B}): the figure numbers of the drawings ('Fig. A2.1' ... 'Fig. A2.13') are dropped while "
     "their captions ('Example of a weighing area') are stored in the clause; the vertical series title beside them "
     "is not text. Drawings, not prose.")
rule(r"who-trs1019-a2-hvac-nonsterile-part2", r"12", r".*",
     f"Parser defect ({B}): Table A2.3 (test parameters, procedures, notes) is stored as running text at the end of "
     "clause 12 with its multi-line cells interleaved line by line ('Adapt ISO tests in case of longer WHO "
     "Technical periods, and consider the Report Series...'), so procedures and notes are mixed. All words stored.")
rule(r"pics-pi023-2-am-qc-labs", r"3\.2|5|8\.7", r"(-1 \| \+2|-2 \| \+i \| -2 \| \+ii|-i \| \+ii)",
     f"Parser defect ({B}): contents entries stored as clauses, with the page footer ('PI 023-2 Page 1 of 2 25 "
     "September 2007') inside them at the page break; pdfminer reads the next page's footer number. Contents "
     "listing, not requirements.")
rule(r"pics-pi023-2-am-qc-labs", r"9\.4", r"-pi 023 2 page ii of ii 25 september 2007 \| -note some more details .*",
     f"Parser defect ({B}): the last contents entry (9.4) holds the page footer, the Annex's explanation of "
     "abbreviations, the note on Supplements 1 and 2 and the two supplement titles; this text belongs to the Annex "
     "introduction, not to a clause 9.4. All words stored.")
rule(r"india-gsr127e-2025-schm-timeline", r"4", r"-4 the gazette of india extraordinary part ii sec 3 i form a application for seeking extension of compliance with revised good manufacturing practices gmp under schedule m of the drugs rules 1945 \| -sarvesh kumar digitally signed by sarvesh kumar srivastava srivastava date 2025\.02\.11 22 35 41 05 30",
     f"Parser defect ({B}): the gazette page header ('4 THE GAZETTE OF INDIA : EXTRAORDINARY [PART II—SEC. 3(i)]'), "
     "the title of Form A and the signatory's digital-signature stamp are stored inside clause 4; the clause's own "
     "words are intact.")
rule(r"india-gsr127e-2025-schm-timeline", r"page 1", r"\+(1031 gi 2025 1|extraordinary part ii section 3 sub section i published by authority no 94 new delhi tuesday february 11 2025 magha 22 1946 cg dl e 11022025 260908)",
     "Gazette masthead on the cover page (registration and issue numbers, date); publication data, not regulation "
     "text.")
rule(r"india-gsr127e-2025-schm-timeline", r"page 2", r"\+3 i iii vii viii",
     "Numbers and Roman list numerals left on the Hindi (Devanagari) part of page 2 once the Devanagari words are "
     "dropped; the English text is stored from its own pages.")
rule(r"fda-cp-7356-002-drug-manufacturing", r"Part VI 3\.B|page 38", r".*",
     f"Parser defect ({B}): the two-column acronym list is read across both columns line by line, so wrapped "
     "definitions are split from their acronyms; all acronyms and definitions are stored.")
rule(r"ich-q3a-r2", r"3 #2", r".*",
     f"Parser defect ({B}): footnote 3 starts a clause '3' that holds Attachments 2 and 3; the decision-tree labels "
     "of Attachment 3 are stored in layout order with their note letters glued ('thresholdc', 'risksd'). Every label "
     "is stored; figure text, not prose.")
rule(r"ich-q3[ab]-r2", r"Table 2 Q3[AB]\(R2\)", r"-2006",
     "The year of the date cell ('... 2006') wraps below the row's band; the stored row holds the full date.")
rule(r"ich-q3a-r2", r"Table 5 “Raw” Result \(%\)", r"-1\.0",
     "Header cell '(Threshold 1.0 mg TDI exceeded?)' wraps over three lines; its '1.0' falls outside the stored "
     "header row's band. Value unchanged.")
rule(r"ich-q3b-r2", r"Glossary", r".*",
     f"Parser defect ({B}): the Attachment 1 threshold graph (axis labels and scale 0.00-1.00) and the decision-tree "
     "labels of Attachment 3 are stored inside the Glossary section, the rotated axis titles letter-spaced "
     "('m ax im u m d aily d o se') and note letters glued ('thresholdc'). Figure text; no requirement value.")
rule(r"ich-q2-r2", r"5", r"-2 \| \+1|-1 \| -2 \| \+1",
     f"Parser defect ({B}): the References clause also holds the Annex 1 heading and Figure 2 title, with the "
     "Annex page numbers ('1', '2') stored inside; pdfminer reads the page footer there. No word changes.")
rule(r"ich-q2-r2", r"7", r"-table 4 example for elemental impurities .*",
     "Titles of Annex 2 Tables 4-8 stored together at the end of clause 7, while their bodies are stored as table "
     "rows; pdfminer reads each title above its own table. All titles stored.")
rule(r"ich-q2-r2", r"Table 10 development as", r"-before measurement",
     "Wrapped cell text '(...before measurement)' printed below the row's band; stored in the row.")
rule(r"ich-q1e", r"Appendix A", r"-i evaluation of stability data",
     "Heading 'Appendix A: Decision Tree for Data Evaluation...' with the figure title 'I. Evaluation of stability "
     "data' read by pdfminer elsewhere on the figure page; figure title, stored.")
rule(r"ich-q1e", r"Appendix A #2|Appendix B 8", r".*",
     "Boxes of the Appendix A decision tree and axis labels/scale of the Appendix B regression graphs stored in "
     "layout order; pdfminer reads them in another order and the rotated axis title letter by letter. Figure text, "
     "not prose; the stored figure values match the PDF.")
rule(r"ich-q1d", r"Table 3 Container size|Table [45] row 3", r"-(15|s batch batch batch batch batch|batch batch batch batch batch)",
     "Row labels of the bracketing/matrixing design tables ('15 ml', 'Batch 1-3', strength 'S2') printed on two lines "
     "or as a spanning cell, outside the row's band; stored in the row unchanged.")
rule(r"fda-guidance-sterilization-validation-submission-1994", r"I\.A", r"-1 this guidance has been prepared by the sterility technical committee .*",
     f"Parser defect ({B}): footnote 1's text (who prepared the guidance, how to obtain copies) is stored inside the "
     "clause mid-sentence, between 'Sterile Pharmaceuticals' and 'for Human and Veterinary Use'; no clause word "
     "changes.")
rule(r"fda-guidance-sterilization-validation-submission-1994", r"II\.A\.3", r"-fo \| \+f",
     "The symbol F0 (F with subscript 0) stored as 'Fo'; pdfminer reads the subscript apart. Notation only.")
rule(r"fda-guidance-sterilization-validation-submission-1994", r"II\.C", r"\+or −( \| -or)?",
     "Exponent minus: the stored text has '10-6' with a hyphen where the PDF prints a superscript minus (pdfminer "
     "also reads the 'or' before it); the value and words are unchanged.")
rule(r"eu-2015-c95-02-excipients", r"Chapter (2 2\.[36]|4 4\.1)", r".*",
     f"Parser defect ({B}): the Official Journal running header ('21.3.2015 EN Official Journal of the European "
     "Union C 95/11') is stored inside the clause at each page break; clause words intact.")
rule(r"who-trs1033-a2-hbel-cleaning", r"Table 2 Pre- Ce- ding Product a", r"-5 6",
     "Header cells '5' and '6' of the product matrix sit outside the row's band; stored in the row unchanged.")
rule(r"who-trs1025-a3-wfi", r"3\.2|7\.2", r"-who technical report series no 1025 2020",
     f"Parser defect ({B}): the running footer 'WHO Technical Report Series, No. 1025, 2020' is stored inside the "
     "clause at the page break; clause words intact.")
rule(r"pics-pi058-1-annex1-interpretation", r"Table 11 9\.30", r"-viii",
     "The reference cell '9.33, 9.36, viii' wraps to a third line below the row's band; stored in the row.")
rule(r"pics-pi058-1-annex1-interpretation", r"page 3", r"\+2 introduction 2\.1 purpose and scope",
     "Headings '2. Introduction / 2.1 Purpose and scope' printed on page 3; pdfminer reads them apart from the "
     "clauses that start with them.")
rule(r"india-gsr666e-2024", r"page 1", r"\+(6992 gi 2024 1|extraordinary part ii section 3 sub section i published by authority no 608 new delhi monday october 28 2024 kartika 6 1946 cg dl e 29102024 258309)",
     "Gazette masthead on the cover page (registration and issue numbers, date); publication data, not regulation "
     "text.")
rule(r"fda-guidance-remote-regulatory-assessments-2025", r"III\.C", r"-33 \| \+34",
     "A footnote reference number: the stored clause keeps footnote mark 33 where pdfminer reads 34 beside it (two "
     "adjacent footnote marks); no guidance word changes.")
rule(r"fda-guidance-remote-regulatory-assessments-2025", r"Appendix 1", r"-appendix 1",
     "Heading 'Appendix 1' read by pdfminer apart from its title; stored heading unchanged.")
rule(r"fda-cp-7356-021-dqrs", r"page 1", r"\+(food and drug administration chapter 56 drug quality assurance|7356\.021 compliance program guidance manual)",
     "Cover-page header block of the compliance program ('Food and Drug Administration', 'Compliance Program "
     "Guidance Manual', 'Chapter 56 Drug Quality Assurance'); document metadata, not program text.")
rule(r"fda-cp-7356-002a-sterile", r"Part II 2\.2\.C", r"-end part ii",
     "The end marker 'End of Part II' printed apart from the clause's last line; stored marker, not a requirement.")
rule(r"fda-cp-7356-002a-sterile", r"Part VII B", r".*|-sterilization depyrogenation dry heat \| \+dry heat sterilization depyrogenation",
     "Words of a two-line table cell ('Dry heat sterilization / depyrogenation') read in another order; same words.")
rule(r"who-trs992-a4-hold-time", r"Glossary", r".*",
     f"Parser defect ({B}): the hold-time study table (Table A4.1: stage, tests, time points) is stored as running "
     "text inside the Glossary section with its columns interleaved line by line, so test lists are separated from "
     "their time points ('water 30th day 45th day content'). All words stored.")
rule(r"who-trs981-a2-qrm", r"page 30", r"\+table 3 continued continues",
     "Table continuation captions ('Table 3 continued', 'continues') on a page break; not regulation text.")
rule(r"who-trs929-a4-sampling", r"Annex 4 Appendix 5 5", r"-table 1 values of n p or r for the n sampling unitsa .*",
     f"Parser defect ({B}): Table 1 (values of n, p, r for the n, p and r sampling plans) is stored as running text "
     "inside clause 5 with its three columns flattened row by row and the note letter glued ('unitsa'); pdfminer "
     "reads the columns in another order. Numbers checked present on the page.")
rule(r"who-trs1044-a4-tech-transfer", r"Appendix 1", r".*|\+aspect related documentation \| \+pharmaceutical ingredients apis and excipients",
     "Header row ('Aspect | Related documentation') and a wrapped cell of the appendix table that pdfminer reads "
     "outside the stored section's stretch; the table is stored as rows.")
rule(r"pics-pi030-1-am-api", r"5", r".*",
     f"Parser defect ({B}): clause 5 spans pages 4-23 and holds the aide-memoire table text with its columns "
     "interleaved line by line ('where status control of material is 10.11 5.40 7.20 systems for material by "
     "physical location'), with the page title 'Aide-Memoire' inside; cross-references are split from their items. "
     "All words stored.")
rule(r"pics-pi011-3", r"9\.1", r"\+14 \| \+development( \| -development)?",
     "Footnote mark 14 and the word 'development' of the boxed V-model figure label read by pdfminer beside the "
     "clause; clause words unchanged.")
rule(r"pics-pe009-18-part2", r"Part II", r"\+i",
     "Roman page number 'i' of the contents page read beside the stored section heading; page artefact.")
rule(r"ich-q9r1", r"4", r"-initiate quality risk management process .* review events",
     "Labels of Figure 1 (overview of a typical QRM process) stored in layout order at the end of clause 4; "
     "pdfminer reads the boxes in another order. Figure text, all labels stored.")
rule(r"ich-q(7|6a|1a|10)\.pdf|ich-q1a-r2|ich-q10", r"Table 2 (Q7A|Q6A|Q1A\(R2\)|Q10)", r"-(2000|1999|2003|2008)",
     "The year of the history table's date cell wraps below the row's band; the stored row holds the full date.")
rule(r"ich-q12", r"Appendix 1", r"\+q as from training sessions q 8 q 9 q 10 points to consider a ppendix",
     "Running title of the Q8/Q9/Q10 'Points to consider' appendix pages, partly in small capitals ('A PPENDIX'); "
     "page artefact, not regulation text.")
rule(r"ich-q11-qa-pmda", r"12", r"-iii",
     f"Parser defect ({B}): the contents page's numeral 'iii' is stored at the end of the contents entry '12'; "
     "pdfminer reads the page header (date, 'Q11 Q&As') there. Contents listing.")
rule(r"ich-m7-r2", r"page 5", r"\+a ssessment and c ontrol of dna r eactive m utagenic i mpurities in p harmaceuticals to l imit p otential c arcinogenic r isk m 7 r 2 1 i",
     "The guideline's title in small capitals on page 5, read by pdfminer as split words; the title is stored with "
     "the front matter.")
rule(r"fda-guidance-product-recalls", r"II", r"(-o( o)?( \| )?)+",
     "Bullet glyphs of the lists (printed as a Wingdings 'o') that the stored text keeps as 'o' and pdfminer drops; "
     "no guidance word changes.")
rule(r"fda-guidance-nitrosamine-ndsri", r"Appendix A", r".*",
     f"Parser defect ({B}): the potency-categorisation tables of Appendix A (alpha-hydrogen score, deactivating and "
     "activating feature scores) are stored partly as clause text, partly as table rows, so labels and scores are "
     "read in another order. Values checked present on the page.")
rule(r"fda-guidance-dissolution", r"II", r"-2005,3 \| \+2005 3",
     f"Parser defect ({B}): footnote mark 3 is glued to the year ('2005,3'); the year and the footnote are both "
     "right.")
rule(r"fda-guidance-benzene", r"III", r"\+11 \| -cbe 30 changes being effected in 30 days pas prior approval supplement",
     "Footnote mark 11 dropped by the parser, and the abbreviation note of the Appendix table ('CBE-30 ...; PAS "
     "...') stored at the end of the clause where pdfminer reads it with the table. No guidance word changes.")
rule(r"fda-cp-7356-843", r"Part VI 4", r".*",
     f"Parser defect ({B}): the two-column acronym list is read across both columns line by line, so wrapped "
     "definitions are split from their acronyms; all acronyms and definitions are stored.")
rule(r"india-drugs-rules-1945", r"Part VII|Part VII 9|Part XV 5 #9", r"(-73\.297 \| \+73 297|-1977,370 \| \+1977 370 \| \+436|-1\.896 \| \+1 896)",
     f"Parser defect ({B}): a superscript footnote number of the consolidation is glued to the number before it, "
     "giving a false value ('73.297[***]' for rule 73 + note 297; '1977,370' for 1977 + note 370; '1.896' for item "
     "1 + note 896); a '+' number is a footnote mark the parser drops. The rule text itself is unchanged.")
rule(r"india-drugs-rules-1945", r"Part XV", r"\+677 679",
     "Footnote marks 677 and 679 of the consolidation that the parser drops; no rule word changes.")
rule(r"india-drugs-rules-1945", r"Part XV 6 #6|Part XV (2[4579]|3[0-9])( #2)?|page 31[56]", r".*",
     "Two-column list of Unani and Siddha dosage forms: the parser reads the columns in layout order and the list "
     "numbers become clause numbers (known parser limitation, 0b); every list entry is stored (checked).")
rule(r"india-drugs-rules-1945", r"Part IV ([1-9]|1[0-6])( #2)?|page 50[3]|page 510", r".*",
     "Two-column drug list (Schedule H/H1 style numbered drug names): the parser reads the columns in layout order "
     "and list numbers become clause numbers (known parser limitation, 0b); every drug name is stored (checked).")
rule(r"india-drugs-rules-1945", r"Part IV 99|page 518", r".*",
     f"Parser defect ({B}): clause 'Part IV 99' (an item of a numbered brand list) runs over pages 513-545 and holds "
     "the rest of that list, Schedules I, J and K, the whole of Schedule L-I (GLP) and the start of Schedule M; "
     "Schedule J's two-column disease list is interleaved across columns. All words stored, but these schedules "
     "have no clauses of their own.")
rule(r"india-drugs-rules-1945", r"Part XV 30", r".*",
     f"Parser defect ({B}): the Siddha shelf-life table is stored partly as clause text with its two columns "
     "interleaved and partly as table rows, so dosage forms and shelf lives are read in another order; values "
     "checked present on the page.")
rule(r"india-drugs-rules-1945", r"Part XI|Part XV 3 #28|Part XV 3 #30|Part XIII 4 #2|Part XIII 15|Part II #3|Part II 1 #7|Part II 29|Part II 6 #7|Part IV 2", r".*",
     f"Parser defect ({B}): a schedule's tables (colour list, laboratory equipment and calibration table, condom "
     "sampling plans, herb/extract forms, vitamin table, psychotropic list) are stored both as table rows and as "
     "clause text read in layout order, with notes and headings placed differently; the check finds the words in "
     "another order. Every word is on the clause's pages (checked); no value changed.")
rule(r"india-drugs-rules-1945", r"page 1(59|60|61)", r"\+serial number common name of colour colour index number chemical name of colour 1 2 3 4( concentrated pyrene trisulfonic acid| acid)?",
     "The colour table's header row and column numbers (1-4) repeated at the top of each page; stored once with the "
     "table.")
rule(r"india-drugs-rules-1945", r"page 34[34]", r"\+(5 danti 6 dhattura|8 jaipala seed 9 karaveera 10 langali|17 mancevikkalli exempted for external use euphorbia species)",
     "Entries of a two-column list of poisonous Siddha/Ayurveda drugs read in another column order; stored in the "
     "list's clause (checked).")
rule(r"india-drugs-rules-1945", r"Table (2 3\.|2 37\.|9 \(1\) \(2\) \(3\) \(I\) Rasayoga Containing…|11 \((1|xi|xiii|xiv)\)|29 D|32 row 1|35 43\.|35 4\. #5|46 12\.|56 Group)", r"-.*",
     "Wrapped cell text, a spanning cell or a column-number row ('1 2 3', 'M F') printed outside the row's band; "
     "the stored row holds the same words.")
rule('ema\\-nitrosamines\\-qa\\-mah\\-rev23\\-2025\\.pdf', 'page\\ 7', '\\+in\\ two\\ clauses\\ Q2\\ and\\ Q3:\\ 3\\ for\\ the\\ call\\ for\\ review\\ for\\ chemically\\ synthesised\\ and',
     "Stored once, in Q3 (where it belongs); the check's alignment of Q2 reaches over the clause boundary and claims the same page words.")
rule('ema\\-nitrosamines\\-qa\\-mah\\-rev23\\-2025\\.pdf', 'page\\ 15', '\\+in\\ two\\ clauses\\ Q8\\ and\\ Q9:\\ 9\\ what\\ are\\ the\\ requirements\\ of\\ the\\ analytical\\ method\\ s\\ the\\ analytical\\ methods\\ need\\ to\\ be\\ sufficiently\\ sensitive\\ in\\ order\\ to\\ adequately\\ detect\\ and',
     "Stored once, in Q9 (where it belongs); the check's alignment of Q8 reaches over the clause boundary and claims the same page words.")
rule('eu\\-20220825_gmp\\-an1_en_0\\.pdf', 'page\\ 2', '\\+in\\ two\\ clauses\\ Annex\\ 1\\ and\\ _unnumbered:1:\\ annex\\ 1\\ manufacture\\ of\\ sterile\\ medicinal\\ products\\ legal\\ context\\ for\\ publishing\\ the\\ detailed\\ guidelines\\ article\\ 47\\ of\\ directive\\ 2001\\ 83\\ ec\\ on\\ the\\ community\\ code\\ relating\\ to\\ medicinal\\ products\\ for\\ human\\ use\\ and\\ regulation\\ 2019\\ 6\\ on\\ the\\ community\\ code\\ relating\\ to\\ veterinary\\ medicinal\\ products\\ this\\ document\\ provides\\ technical\\ guidance\\ on\\ the\\ principles\\ and\\ guidelines\\ of\\ good\\ manufacturing\\ practice\\ gmp\\ for\\ medicinal\\ products\\ as\\ laid\\ down\\ in\\ commission\\ directive\\ eu\\ 2017\\ 1572\\ for\\ medicinal\\ products\\ for\\ human\\ use\\ directive\\ 91\\ 412\\ eec\\ for\\ veterinary\\ use',
     "Stored once, in Annex 1 (where it belongs); the check's alignment of _unnumbered:1 reaches over the clause boundary and claims the same page words.")
rule('eu\\-annex19\\-2026\\-c2026\\-4135\\.pdf', 'page\\ 2', '\\+in\\ two\\ clauses\\ Annex\\ 19\\ and\\ _unnumbered:1:\\ annex\\ 19\\ reference\\ and\\ retention\\ samples\\ legal\\ basis\\ for\\ publishing\\ the\\ detailed\\ guidelines\\ article\\ 47\\ of\\ directive\\ 2001\\ 83\\ ec\\ on\\ the\\ community\\ code\\ relating\\ to\\ medicinal\\ products',
     "Stored once, in Annex 19 (where it belongs); the check's alignment of _unnumbered:1 reaches over the clause boundary and claims the same page words.")
rule('eu\\-chapter_3\\.pdf', 'page\\ 5', '\\+in\\ two\\ clauses\\ 3\\.33\\ and\\ 3\\.34:\\ 3\\.34\\ manufacturing\\ equipment',
     "Stored once, in 3.34 (where it belongs); the check's alignment of 3.33 reaches over the clause boundary and claims the same page words.")
rule('eu\\-chapter_5\\.pdf', 'page\\ 1', '\\+in\\ two\\ clauses\\ Chapter\\ 5\\ and\\ _unnumbered:1:\\ ref\\ ares\\ 2015\\ 283689\\ 23\\ 01\\ 2015',
     "Stored once, in _unnumbered:1 (where it belongs); the check's alignment of Chapter 5 reaches over the clause boundary and claims the same page words.")
rule('fda\\-cp\\-7346\\-832\\-preapproval\\-inspections\\.pdf', 'page\\ 43', '\\+in\\ two\\ clauses\\ Part\\ VII\\ and\\ _unnumbered:6:\\ part\\ vii\\ center\\ and\\ oii\\ responsibilities\\ cder\\ and\\ oii\\ redefined\\ their\\ roles\\ and\\ responsibilities\\ regarding\\ application\\ assessments\\ and\\ inspections\\ of',
     "Stored once, in Part VII (where it belongs); the check's alignment of _unnumbered:6 reaches over the clause boundary and claims the same page words.")
rule('fda\\-cp\\-7356\\-002a\\-sterile\\-drug\\-process\\.pdf', 'page\\ 6', '\\+in\\ two\\ clauses\\ Part\\ II\\ 2\\.2\\.A\\ and\\ Part\\ III:\\ part\\ iii\\ inspectional',
     "Parser defect (0b): the heading 'PART III - INSPECTIONAL' is stored inside Part II 2.2.A as well as starting Part III; it belongs to Part III.")
rule('fda\\-guidance\\-container\\-closure\\-systems\\-1999\\.pdf', 'page\\ 3', '\\+in\\ two\\ clauses\\ I\\ and\\ _unnumbered:2:\\ that\\ concern\\ packaging\\ b\\ 1\\ attachment\\ c\\ c\\ 1\\ extraction\\ studies\\ c\\ 1\\ attachment\\ d\\ d\\ 1\\ abbreviations\\ d\\ 1\\ attachment\\ e\\ e\\ 1\\ references\\ e\\ 1',
     "Stored once, in _unnumbered:2 (where it belongs); the check's alignment of I reaches over the clause boundary and claims the same page words.")
rule('fda\\-guidance\\-container\\-closure\\-systems\\-1999\\.pdf', 'page\\ 20', '\\+in\\ two\\ clauses\\ III\\.C\\ and\\ III\\.C\\.2:\\ c\\ information\\ that\\ should\\ be\\ submitted\\ in\\ support\\ of\\ an\\ original\\ application\\ for\\ any\\ drug\\ product\\ 15\\ additional\\ discussion\\ and\\ information\\ regarding\\ the\\ cmc\\ information\\ to\\ be\\ provided\\ in\\ an\\ application\\ nda\\ anda\\ or\\ bla\\ can\\ be\\ found\\ in\\ the\\ guidances\\ and\\ guidelines\\ listed\\ in\\ attachment\\ e\\ 1\\ description\\ a\\ general\\ description\\ of\\ the\\ entire\\ container\\ closure\\ system\\ should\\ be\\ provided\\ in\\ the\\ cmc\\ section\\ of\\ the\\ application\\ in\\ addition\\ the\\ following\\ information\\ should\\ be\\ provided\\ by\\ the\\ applicant\\ for\\ each\\ individual\\ component\\ of\\ the\\ packaging\\ system\\ a\\ identification\\ by\\ product\\ name\\ product\\ code\\ if\\ available\\ the\\ name\\ and\\ address\\ of\\ the\\ manufacturer\\ and\\ a\\ physical\\ description\\ of\\ the\\ packaging\\ component\\ e\\ g\\ type\\ size\\ shape\\ and\\ color\\ b\\ identification\\ of\\ the\\ materials\\ of\\ construction\\ i\\ e\\ plastics\\ paper\\ metal\\ glass\\ elastomers\\ coatings\\ adhesives\\ and\\ other\\ such\\ materials\\ should\\ be\\ identified\\ by\\ a\\ specific\\ product\\ designation\\ code\\ name\\ and\\ or\\ code\\ number\\ and\\ the\\ source\\ name\\ of\\ the\\ manufacturer\\ alternate\\ materials\\ of\\ construction\\ should\\ also\\ be\\ 16\\ indicated\\ postconsumer\\ recycled\\ plastic\\ should\\ not\\ be\\ used\\ in\\ the\\ manufacture\\ of\\ a\\ primary\\ packaging\\ component\\ if\\ used\\ for\\ a\\ secondary\\ or\\ associated\\ component\\ then\\ the\\ safety\\ and\\ compatibility\\ of\\ the\\ material\\ for\\ its\\ intended\\ use\\ should\\ be\\ addressed\\ appropriately\\ c\\ description\\ of\\ any\\ operations\\ or\\ preparations\\ that\\ are\\ performed\\ on\\ a\\ packaging\\ component\\ by\\ the\\ applicant\\ such\\ as\\ washing\\ coating\\ sterilization\\ or\\ depyrogenation\\ 17',
     "Stored once, in III.C (where it belongs); the check's alignment of III.C.2 reaches over the clause boundary and claims the same page words.")
rule('fda\\-guidance\\-container\\-closure\\-systems\\-1999\\.pdf', 'page\\ 45', '\\+in\\ two\\ clauses\\ Attachment\\ A\\ and\\ VI\\.B:\\ attachment\\ a\\ 25\\ regulatory',
     "Stored once, in Attachment A (where it belongs); the check's alignment of VI.B reaches over the clause boundary and claims the same page words.")
rule('fda\\-guidance\\-delaying\\-denying\\-inspection\\-2024\\.pdf', 'page\\ 4', '\\+in\\ two\\ clauses\\ I\\ and\\ _unnumbered:2:\\ this\\ guidance\\ represents\\ the\\ current\\ thinking\\ of\\ the\\ food\\ and\\ drug\\ administration\\ fda\\ or\\ agency\\ on\\ this\\ topic\\ it\\ does\\ not\\ establish\\ any\\ rights\\ for\\ any\\ person\\ and\\ is\\ not\\ binding\\ on\\ fda\\ or\\ the\\ public\\ you\\ can\\ use\\ an\\ alternative\\ approach\\ if\\ it\\ satisfies\\ the\\ requirements\\ of\\ the\\ applicable\\ statutes\\ and\\ regulations\\ to\\ discuss\\ an\\ alternative\\ approach\\ contact\\ the\\ fda\\ office\\ responsible\\ for\\ this\\ guidance\\ as\\ listed\\ on\\ the\\ title\\ page',
     "Stored once, in _unnumbered:2 (where it belongs); the check's alignment of I reaches over the clause boundary and claims the same page words.")
rule('fda\\-guidance\\-remote\\-regulatory\\-assessments\\-2025\\.pdf', 'page\\ 4', '\\+in\\ two\\ clauses\\ I\\ and\\ _unnumbered:2:\\ this\\ guidance\\ represents\\ the\\ current\\ thinking\\ of\\ the\\ food\\ and\\ drug\\ administration\\ fda\\ or\\ agency\\ on\\ this\\ topic\\ it\\ does\\ not\\ establish\\ any\\ rights\\ for\\ any\\ person\\ and\\ is\\ not\\ binding\\ on\\ fda\\ or\\ the\\ public\\ you\\ can\\ use\\ an\\ alternative\\ approach\\ if\\ it\\ satisfies\\ the\\ requirements\\ of\\ the\\ applicable\\ statutes\\ and\\ regulations\\ to\\ discuss\\ an\\ alternative\\ approach\\ contact\\ the\\ fda\\ staff\\ or\\ office\\ responsible\\ for\\ this\\ guidance\\ as\\ listed\\ on\\ the\\ title\\ page',
     "Stored once, in _unnumbered:2 (where it belongs); the check's alignment of I reaches over the clause boundary and claims the same page words.")
rule('fda\\-guidance\\-voluntary\\-recalls\\-initiation\\-2022\\.pdf', 'page\\ 4', '\\+in\\ two\\ clauses\\ I\\ and\\ _unnumbered:2:\\ this\\ guidance\\ represents\\ the\\ current\\ thinking\\ of\\ the\\ u\\ s\\ food\\ and\\ drug\\ administration\\ fda\\ we\\ or\\ agency\\ on\\ this\\ topic\\ it\\ does\\ not\\ establish\\ any\\ rights\\ for\\ any\\ person\\ and\\ is\\ not\\ binding\\ on\\ fda\\ or\\ the\\ public\\ you\\ can\\ use\\ an\\ alternative\\ approach\\ if\\ it\\ satisfies\\ the\\ requirements\\ of\\ the\\ applicable\\ statutes\\ and\\ regulations\\ to\\ discuss\\ an\\ alternative\\ approach\\ contact\\ the\\ fda\\ staff\\ responsible\\ for\\ this\\ guidance\\ as\\ listed\\ on\\ the\\ title\\ page',
     "Stored once, in _unnumbered:2 (where it belongs); the check's alignment of I reaches over the clause boundary and claims the same page words.")
rule('ich\\-q12\\.pdf', 'page\\ 10', '\\+in\\ two\\ clauses\\ 3\\ and\\ 3\\.1:\\ established\\ conditions\\ for\\ manufacturing\\ and\\ control\\ referred\\ to\\ as\\ ecs',
     "Stored once, in 3.1 (where it belongs); the check's alignment of 3 reaches over the clause boundary and claims the same page words.")
rule('ich\\-q12\\.pdf', 'page\\ 19', '\\+in\\ two\\ clauses\\ 6\\ and\\ 6\\.1:\\ and\\ change\\ management',
     "Heading words of section 6 ('PQS and change management'), stored in heading clause 6, where they belong; the alignment of 6.1 reaches over the boundary.")
rule('ich\\-q12\\.pdf', 'page\\ 23', '\\+in\\ two\\ clauses\\ 11\\ and\\ Appendix\\ 1:\\ appendix\\ q\\ as\\ from\\ training\\ sessions\\ q\\ 8\\ q\\ 9\\ q\\ 10\\ points\\ to\\ consider',
     "Stored once, in 11 (where it belongs); the check's alignment of Appendix 1 reaches over the clause boundary and claims the same page words.")
rule('ich\\-q3c\\-r9\\.pdf', 'page\\ 30', '\\+in\\ two\\ clauses\\ Part\\ III\\ 5\\.3\\ and\\ Part\\ IV\\ \\#2:\\ pde\\ for\\ cumene',
     "Parser defect (0b): the running page title 'PDE for Cumene' is stored at the end of Part III 5.3 and inside Part IV; it is a page header of Part IV, not clause text.")
rule('ich\\-q3c\\-r9\\.pdf', 'page\\ 34', '\\+in\\ two\\ clauses\\ Part\\ V\\ and\\ _unnumbered:2:\\ pde\\ for\\ triethylamine\\ and\\ methylisobutylketone',
     "Parser defect (0b): the running page title 'PDE for Triethylamine and Methylisobutylketone' is stored at the end of the preceding references and inside Part V; page header of Part V, not clause text.")
rule('ich\\-q3c\\-r9\\.pdf', 'page\\ 41', '\\+in\\ two\\ clauses\\ Part\\ VI\\ and\\ _unnumbered:4:\\ pde\\ for\\ 2\\ methyltetrahydrofuran\\ cyclopentyl\\ methyl\\ ether\\ and\\ tertiary\\ butyl\\ alcohol',
     "Parser defect (0b): the running page title 'PDE for 2-MTHF, CPME and TBA' is stored at the end of the preceding references and inside Part VI; page header of Part VI, not clause text.")
rule('ich\\-q3d\\-r2\\.pdf', 'page\\ 4', '\\+in\\ two\\ clauses\\ 3\\ and\\ Appendix\\ 5\\ 3:\\ 3\\ safety\\ assessment\\ of\\ potential\\ elemental\\ impurities',
     "The PDF prints the same text twice (pages 4 and 5); each copy is stored in its own clause, and this page's copy belongs to 3.")
rule('india\\-drugs\\-rules\\-1945\\-consolidated\\-2024\\-07\\.pdf', 'page\\ 215', '\\+in\\ two\\ clauses\\ Part\\ XV\\ 2\\ \\#2\\ and\\ Part\\ XV\\ 2\\ \\#3:\\ 2\\ each\\ batch\\ of\\ drug\\ imported\\ into\\ india\\ shall\\ be\\ accompanied\\ with\\ a\\ detailed\\ batch\\ test\\ report\\ and\\ a\\ batch\\ release\\ certificate\\ duly\\ signed\\ and\\ authenticated\\ by\\ the\\ manufacturer\\ with\\ date\\ of\\ testing\\ date\\ of\\ release\\ and\\ date\\ of\\ forwarding\\ such\\ reports\\ the\\ imported\\ batch\\ of\\ each\\ drug\\ shall\\ be\\ subjected\\ to\\ examination\\ and\\ testing\\ as\\ the\\ licensing\\ authority\\ deems\\ fit\\ prior\\ to\\ its\\ marketing',
     "The PDF prints the same text twice (pages 215 and 216); each copy is stored in its own clause, and this page's copy belongs to Part XV 2 #2.")
rule('india\\-drugs\\-rules\\-1945\\-consolidated\\-2024\\-07\\.pdf', 'page\\ 218', '\\+in\\ two\\ clauses\\ Part\\ XV\\ 1\\ \\#4\\ and\\ Part\\ XV\\ 1\\ \\#5:\\ 1\\ the\\ licence\\ shall\\ be\\ displayed\\ in\\ the\\ office\\ of\\ the\\ medical\\ superintendent\\ of\\ government\\ hospital\\ head\\ of\\ institution\\ of\\ autonomous\\ medical\\ institution',
     "The PDF prints the same text twice (pages 218 and 219); each copy is stored in its own clause, and this page's copy belongs to Part XV 1 #4.")
rule('india\\-drugs\\-rules\\-1945\\-consolidated\\-2024\\-07\\.pdf', 'page\\ 240', '\\+in\\ two\\ clauses\\ Part\\ XV\\ 1\\ \\#10\\ and\\ Part\\ XV\\ 1\\ \\#11:\\ 1\\ this\\ licence\\ shall\\ be\\ displayed\\ in\\ a\\ prominent\\ place\\ in\\ a\\ part\\ of\\ the\\ premises\\ open\\ to\\ the\\ public',
     "The PDF prints the same text twice (pages 240 and 241); each copy is stored in its own clause, and this page's copy belongs to Part XV 1 #10.")
rule('india\\-drugs\\-rules\\-1945\\-consolidated\\-2024\\-07\\.pdf', 'page\\ 258', '\\+in\\ two\\ clauses\\ Part\\ XV\\ 1\\ \\#16\\ and\\ Part\\ XV\\ 5\\ \\#8:\\ 1\\ this\\ licence\\ and\\ 889',
     "Parser defect (0b): condition 1 ('This licence and [***] shall be kept...') is stored in Part XV 1 #16, where it belongs; its footnote mark 889 and the heading 'Conditions of Licence' are stored at the end of Part XV 5 #8.")
rule('india\\-drugs\\-rules\\-1945\\-consolidated\\-2024\\-07\\.pdf', 'page\\ 411', '\\+in\\ two\\ clauses\\ Part\\ I\\ 5\\ \\#4\\ and\\ Part\\ I\\ 6\\ \\#3:\\ 5\\ labelling\\ and\\ storage\\ should\\ comply\\ with\\ the\\ requirements\\ for\\ labelling\\ and\\ storage\\ as\\ laid\\ down\\ in\\ the\\ general\\ monograph\\ on\\ bacterial\\ vaccine',
     "Standard monograph sentence printed in several monographs; this page's copy is stored in Part I 6 #3 (pages 407-411), the other copy in Part I 5 #4 on page 412.")
rule('india\\-drugs\\-rules\\-1945\\-consolidated\\-2024\\-07\\.pdf', 'page\\ 502', '\\+in\\ two\\ clauses\\ Part\\ IV\\ 1\\ \\#2\\ and\\ Part\\ IV\\ 2\\ \\#2:\\ 2\\ abciximab\\ 3\\ acamprosate\\ calcium\\ 4\\ acebutol\\ hydrochloride\\ 5\\ aclarubicin\\ 6\\ albendazole',
     'Two-column drug list: the parser reads the columns in layout order and list numbers become clause numbers (known parser limitation, 0b); the drug names are stored in Part IV 4.')
rule('india\\-drugs\\-rules\\-1945\\-consolidated\\-2024\\-07\\.pdf', 'page\\ 829', '\\+in\\ two\\ clauses\\ Part\\ II\\ 1\\ \\#5\\ and\\ Part\\ II\\ 3\\ \\#4:\\ 1\\ si\\ no\\ 2\\ batch\\ no',
     "Stored once, in Part II 3 #4 (where it belongs); the check's alignment of Part II 1 #5 reaches over the clause boundary and claims the same page words.")
rule('india\\-drugs\\-rules\\-1945\\-consolidated\\-2024\\-07\\.pdf', 'page\\ 829', '\\+in\\ two\\ clauses\\ Part\\ II\\ 4\\ \\#5\\ and\\ Part\\ II\\ 7\\ \\#4:\\ 4\\ name\\ of\\ the\\ material\\ and\\ quantity',
     "Register field '4. Name of the material and quantity' printed in two registers; this page's copy is stored in Part II 7 #4 (Bhavana register), the other in Part II 4 #5 on page 830.")
rule('india\\-drugs\\-rules\\-1945\\-consolidated\\-2024\\-07\\.pdf', 'page\\ 835', '\\+in\\ two\\ clauses\\ Part\\ II\\ 1\\ \\#7\\ and\\ Part\\ II\\ 2\\ \\#7:\\ 2\\ shortage\\ of\\ raw\\ material\\ s\\ inputs\\ during\\ the\\ preceding\\ year\\ yes\\ no\\ if\\ yes\\ please\\ indicate\\ name',
     "Stored once, in Part II 2 #7 (where it belongs); the check's alignment of Part II 1 #7 reaches over the clause boundary and claims the same page words.")
rule('pics\\-pe009\\-18\\-annexes\\.pdf', 'page\\ 135', '\\+in\\ two\\ clauses\\ Annex\\ 2B\\ Glossary\\ and\\ Annex\\ 3:\\ annex\\ 3\\ manufacture\\ of\\ radiopharmaceuticals',
     'Parser defect (0b): text stored twice - at the end of Annex 2B Glossary and as the start of Annex 3; it belongs to Annex 3 (its heading or title).')
rule('pics\\-pe009\\-18\\-annexes\\.pdf', 'page\\ 154', '\\+in\\ two\\ clauses\\ Annex\\ 5\\ 68\\ and\\ Annex\\ 6:\\ annex\\ 6\\ manufacture\\ of\\ medicinal\\ gases',
     'Parser defect (0b): text stored twice - at the end of Annex 5 68 and as the start of Annex 6; it belongs to Annex 6 (its heading or title).')
rule('pics\\-pe009\\-18\\-annexes\\.pdf', 'page\\ 165', '\\+in\\ two\\ clauses\\ Annex\\ 6\\ Glossary\\ and\\ Annex\\ 7:\\ annex\\ 7\\ manufacture\\ of\\ herbal\\ medicinal\\ products',
     'Parser defect (0b): text stored twice - at the end of Annex 6 Glossary and as the start of Annex 7; it belongs to Annex 7 (its heading or title).')
rule('pics\\-pe009\\-18\\-annexes\\.pdf', 'page\\ 170', '\\+in\\ two\\ clauses\\ Annex\\ 7\\ 16\\ and\\ Annex\\ 8:\\ annex\\ 8\\ sampling\\ of\\ starting\\ and\\ packaging\\ materials',
     'Parser defect (0b): text stored twice - at the end of Annex 7 16 and as the start of Annex 8; it belongs to Annex 8 (its heading or title).')
rule('pics\\-pe009\\-18\\-annexes\\.pdf', 'page\\ 172', '\\+in\\ two\\ clauses\\ Annex\\ 8\\ 5\\ and\\ Annex\\ 9:\\ annex\\ 9\\ manufacture\\ of\\ liquids\\ creams\\ and\\ ointments',
     'Parser defect (0b): text stored twice - at the end of Annex 8 5 and as the start of Annex 9; it belongs to Annex 9 (its heading or title).')
rule('pics\\-pe009\\-18\\-annexes\\.pdf', 'page\\ 174', '\\+in\\ two\\ clauses\\ Annex\\ 10\\ \\#2\\ and\\ Annex\\ 9\\ 9:\\ annex\\ 10\\ manufacture\\ of\\ pressurised\\ metered\\ dose\\ aerosol\\ preparations\\ for\\ inhalation',
     'Parser defect (0b): text stored twice - at the end of Annex 9 9 and as the start of Annex 10 #2; it belongs to Annex 10 #2 (its heading or title).')
rule('pics\\-pe009\\-18\\-annexes\\.pdf', 'page\\ 176', '\\+in\\ two\\ clauses\\ Annex\\ 10\\ 9\\ and\\ Annex\\ 11:\\ annex\\ 11\\ computerised\\ systems',
     'Parser defect (0b): text stored twice - at the end of Annex 10 9 and as the start of Annex 11; it belongs to Annex 11 (its heading or title).')
rule('pics\\-pe009\\-18\\-annexes\\.pdf', 'page\\ 253', '\\+in\\ two\\ clauses\\ Annex\\ 17\\ Glossary\\ and\\ Annex\\ 19:\\ annex\\ 19\\ reference\\ and\\ retention\\ samples',
     'Parser defect (0b): text stored twice - at the end of Annex 17 Glossary and as the start of Annex 19; it belongs to Annex 19 (its heading or title).')
rule('pics\\-pi009\\-4\\-am\\-utilities\\.pdf', 'page\\ 2', '\\+in\\ two\\ clauses\\ 1\\ and\\ _unnumbered:1:\\ 1\\ document\\ history',
     "Contents entry on the front-matter contents page (held in _unnumbered:1) with the same words as the heading of clause 1; this page's copy is the contents entry, the heading belongs to clause 1.")
rule('pics\\-pi009\\-4\\-am\\-utilities\\.pdf', 'page\\ 2', '\\+in\\ two\\ clauses\\ 5\\ and\\ _unnumbered:1:\\ 5\\ aide\\ memoire',
     "Contents entry on the front-matter contents page (held in _unnumbered:1) with the same words as the heading of clause 5; this page's copy is the contents entry, the heading belongs to clause 5.")
rule('pics\\-pi011\\-3\\-computerised\\-systems\\.pdf', 'page\\ 32', '\\+in\\ two\\ clauses\\ 21\\.6\\ and\\ 21\\.7:\\ 21\\.7\\ whilst\\ ec\\ directive\\ 2001\\ 83\\ 43',
     'Start of clause 21.7, stored in 21.7 (its footnote mark 43 dropped); the alignment of 21.6 reaches over the boundary.')
rule('pics\\-pi028\\-2\\-am\\-packaging\\.pdf', 'page\\ 2', '\\+in\\ two\\ clauses\\ 1\\ and\\ _unnumbered:1:\\ 1\\ document\\ history',
     "Contents entry on the front-matter contents page (held in _unnumbered:1) with the same words as the heading of clause 1; this page's copy is the contents entry, the heading belongs to clause 1.")
rule('pics\\-pi028\\-2\\-am\\-packaging\\.pdf', 'page\\ 2', '\\+in\\ two\\ clauses\\ 5\\ and\\ _unnumbered:1:\\ 5\\ aide\\ memoire',
     "Contents entry on the front-matter contents page (held in _unnumbered:1) with the same words as the heading of clause 5; this page's copy is the contents entry, the heading belongs to clause 5.")
rule('pics\\-pi030\\-1\\-am\\-api\\.pdf', 'page\\ 2', '\\+in\\ two\\ clauses\\ 1\\ and\\ _unnumbered:1:\\ 1\\ document\\ history',
     "Contents entry on the front-matter contents page (held in _unnumbered:1) with the same words as the heading of clause 1; this page's copy is the contents entry, the heading belongs to clause 1.")
rule('pics\\-pi040\\-1\\-deficiency\\-classification\\.pdf', 'page\\ 2', '\\+in\\ two\\ clauses\\ 1\\ and\\ Appendix\\ 2\\ 1:\\ 1\\ document\\ history',
     "The PDF prints the same text twice (pages 2 and 3); each copy is stored in its own clause, and this page's copy belongs to 1.")
rule('pics\\-pi040\\-1\\-deficiency\\-classification\\.pdf', 'page\\ 2', '\\+in\\ two\\ clauses\\ 3\\ and\\ Appendix\\ 2\\ 3:\\ 3\\ purpose\\ and\\ scope',
     "The PDF prints the same text twice (pages 2 and 3); each copy is stored in its own clause, and this page's copy belongs to 3.")
rule('pics\\-pi047\\-1\\-gdp\\-active\\-substances\\.pdf', 'page\\ 2', '\\+in\\ two\\ clauses\\ 1\\ and\\ _unnumbered:1:\\ 1\\ chapter\\ 1\\ scope',
     "Contents entry on the front-matter contents page (held in _unnumbered:1) with the same words as the heading of clause 1; this page's copy is the contents entry, the heading belongs to clause 1.")
rule('pics\\-pi052\\-1\\-am\\-hbel\\.pdf', 'page\\ 2', '\\+in\\ two\\ clauses\\ 1\\ and\\ _unnumbered:1:\\ 1\\ document\\ history',
     "Contents entry on the front-matter contents page (held in _unnumbered:1) with the same words as the heading of clause 1; this page's copy is the contents entry, the heading belongs to clause 1.")
rule('who\\-trs1019\\-a3\\-validation\\.pdf', 'page\\ 42', '\\+in\\ two\\ clauses\\ Appendix\\ 5\\ and\\ Appendix\\ 5\\ 1:\\ 1\\ introduction\\ and\\ scope',
     "Appendix 5's own contents list (held in the Appendix 5 section) and the heading of its clause 1 both read '1. Introduction and scope'; this page's copy is the contents entry.")
rule('who\\-trs1060\\-a3\\-excipients\\.pdf', 'page\\ 2', '\\+in\\ two\\ clauses\\ 1\\ and\\ Appendix\\ 1\\ 1:\\ 1\\ introduction\\ and\\ scope',
     "The PDF prints the same text twice (pages 2 and 3); each copy is stored in its own clause, and this page's copy belongs to 1.")
rule('who\\-trs929\\-a4\\-sampling\\.pdf', 'page\\ 1', '\\+in\\ two\\ clauses\\ Annex\\ 4\\ and\\ _unnumbered:1:\\ annex\\ 4\\ who',
     "Stored once, in Annex 4 (where it belongs); the check's alignment of _unnumbered:1 reaches over the clause boundary and claims the same page words.")
rule('who\\-trs957\\-a3\\-hazardous\\.pdf', 'page\\ 1', '\\+in\\ two\\ clauses\\ Annex\\ 3\\ and\\ _unnumbered:1:\\ annex\\ 3\\ who',
     "Stored once, in Annex 3 (where it belongs); the check's alignment of _unnumbered:1 reaches over the clause boundary and claims the same page words.")
rule('who\\-trs957\\-a3\\-hazardous\\.pdf', 'page\\ 14', '\\+in\\ two\\ clauses\\ Annex\\ 3\\ 11\\.1\\ and\\ Annex\\ 3\\ 11\\.2:\\ 11\\.2\\ the\\ fi\\ nal\\ fi\\ lters\\ on\\ the\\ safe\\ change\\ unit\\ should\\ be\\ hepa\\ fi\\ lters\\ with\\ at\\ least\\ an\\ h\\ 13\\ classifi\\ cation\\ according\\ to\\ en\\ 1822\\ fi\\ lter\\ standards\\ for\\ dusty\\ return\\ air\\ pre\\ fi\\ ltration\\ may\\ also\\ be\\ required\\ to\\ prolong\\ the\\ life\\ of\\ the\\ hepa\\ fi\\ lters\\ the\\ pre\\ fi\\ ltration\\ fi\\ lters\\ should\\ also\\ be\\ removable\\ through\\ the\\ bag\\ in\\ bag\\ out',
     "Stored once, in Annex 3 11.2 (where it belongs); the check's alignment of Annex 3 11.1 reaches over the clause boundary and claims the same page words.")
rule('who\\-trs961\\-a2\\-micro\\-labs\\.pdf', 'page\\ 1', '\\+in\\ two\\ clauses\\ Annex\\ 2\\ and\\ _unnumbered:1:\\ annex\\ 2\\ who',
     "Stored once, in Annex 2 (where it belongs); the check's alignment of _unnumbered:1 reaches over the clause boundary and claims the same page words.")
rule('who\\-trs992\\-a5\\-ttsp\\-supplements\\.pdf', 'page\\ 12', '\\+in\\ two\\ clauses\\ _unnumbered:10\\ and\\ _unnumbered:12:\\ acknowledgements\\ abbreviations\\ glossary\\ 1\\ introduction\\ 1\\.1\\ requirements\\ 1\\.2\\ objectives\\ 1\\.3\\ target\\ readership\\ 2\\ guidance\\ 2\\.1\\ associated\\ materials\\ and\\ equipment',
     'Entries of a reproduced supplement contents page (Acknowledgements, Glossary, 1.1 Requirements...) that repeat on every supplement; contents listing, not requirements.')
rule('who\\-trs992\\-a5\\-ttsp\\-supplements\\.pdf', 'page\\ 23', '\\+in\\ two\\ clauses\\ Annex\\ 1\\ 1\\ \\#3\\ and\\ Annex\\ 1\\ 1\\ \\#4:\\ 1\\ introduction\\ 1\\.1\\ requirements\\ 1\\.2\\ objectives\\ 1\\.3\\ target\\ readership\\ 2\\ guidance',
     'Entries of a reproduced supplement contents page that repeat on every supplement; contents listing, not requirements.')
rule('who\\-trs996\\-a4\\-app1\\-model\\-inspection\\-report\\.pdf', 'page\\ 10', '\\+in\\ two\\ clauses\\ Appendix\\ 1\\ 2\\ \\#2\\ and\\ Appendix\\ 1\\ 3\\ \\#2:\\ 3\\ sanitation\\ and\\ hygiene\\ describe\\ procedures\\ and\\ records\\ relating\\ to\\ sanitation\\ and\\ hygiene\\ for',
     "Parser defect (0b): two-column model report form stored line by line across both columns; item '3. Sanitation and hygiene' belongs to Appendix 1 3 #2, where its words are stored interleaved.")
rule('eu\\-2018_annex17_en\\.pdf', 'page\\ 3', '\\+next\\ to\\ 1\\.1:\\ principle\\ 1',
     "A section heading printed on its own line (verified in poppler's text) that the parser keeps as structure, not as clause text; heading words, not requirement text.")
rule('eu\\-2018_annex17_en\\.pdf', 'page\\ 3', '\\+next\\ to\\ 1\\.1:\\ 2\\ scope',
     "A section heading printed on its own line (verified in poppler's text) that the parser keeps as structure, not as clause text; heading words, not requirement text.")
rule('eu\\-2018_annex17_en\\.pdf', 'page\\ 3', '\\+next\\ to\\ 2\\.1:\\ scope\\ 2',
     "A section heading printed on its own line (verified in poppler's text) that the parser keeps as structure, not as clause text; heading words, not requirement text.")
rule('eu\\-20220825_gmp\\-an1_en_0\\.pdf', 'page\\ 4', '\\+next\\ to\\ Annex\\ 1\\ 1:\\ 2\\ principle',
     "A section heading printed on its own line (verified in poppler's text) that the parser keeps as structure, not as clause text; heading words, not requirement text.")
rule('eu\\-20220825_gmp\\-an1_en_0\\.pdf', 'page\\ 4', '\\+next\\ to\\ Annex\\ 1\\ 2\\.1:\\ principle\\ 2',
     "A section heading printed on its own line (verified in poppler's text) that the parser keeps as structure, not as clause text; heading words, not requirement text.")
rule('fda\\-cp\\-7346\\-832\\-preapproval\\-inspections\\.pdf', 'page\\ 37', '\\+next\\ to\\ Part\\ VI:\\ references',
     "A section heading printed on its own line (verified in poppler's text) that the parser keeps as structure, not as clause text; heading words, not requirement text.")
rule('fda\\-cp\\-7346\\-832\\-preapproval\\-inspections\\.pdf', 'page\\ 37', '\\+next\\ to\\ Part\\ VI\\ A:\\ references',
     "A section heading printed on its own line (verified in poppler's text) that the parser keeps as structure, not as clause text; heading words, not requirement text.")
rule('fda\\-guidance\\-analytical\\-procedures\\-validation\\-2015\\.pdf', 'page\\ 4', '\\+next\\ to\\ _unnumbered:2:\\ i\\ introduction',
     "A section heading printed on its own line (verified in poppler's text) that the parser keeps as structure, not as clause text; heading words, not requirement text.")
rule('fda\\-guidance\\-analytical\\-procedures\\-validation\\-2015\\.pdf', 'page\\ 4', '\\+next\\ to\\ I:\\ introduction\\ i',
     "A section heading printed on its own line (verified in poppler's text) that the parser keeps as structure, not as clause text; heading words, not requirement text.")
rule('fda\\-guidance\\-part11\\-scope\\-application\\-2003\\.pdf', 'page\\ 4', '\\+next\\ to\\ _unnumbered:2:\\ i\\ introduction',
     "A section heading printed on its own line (verified in poppler's text) that the parser keeps as structure, not as clause text; heading words, not requirement text.")
rule('fda\\-guidance\\-part11\\-scope\\-application\\-2003\\.pdf', 'page\\ 4', '\\+next\\ to\\ I:\\ introduction\\ i',
     "A section heading printed on its own line (verified in poppler's text) that the parser keeps as structure, not as clause text; heading words, not requirement text.")
rule('fda\\-guidance\\-remote\\-regulatory\\-assessments\\-2025\\.pdf', 'page\\ 18', '\\+next\\ to\\ III\\.D:\\ appendix\\ 1',
     "A section heading printed on its own line (verified in poppler's text) that the parser keeps as structure, not as clause text; heading words, not requirement text.")
rule('ich\\-q12\\.pdf', 'page\\ 15', '\\+next\\ to\\ 4\\.1:\\ pacmp',
     "Last word of the section 4 heading ('Post-approval change management protocol (PACMP)'), which the parser stores without its line end; heading, not requirement text.")
rule('ich\\-q3d\\-r2\\.pdf', 'page\\ 4', '\\+next\\ to\\ _unnumbered:1:\\ c\\ ontents',
     "The 'TABLE OF CONTENTS' heading in small capitals, read as split words; front matter.")
rule('ich\\-q3d\\-r2\\.pdf', 'page\\ 4', '\\+next\\ to\\ 1:\\ ontents\\ c',
     "The 'TABLE OF CONTENTS' heading in small capitals, read as split words; front matter.")
rule('ich\\-q3d\\-r2\\.pdf', 'page\\ 18', '\\+next\\ to\\ Appendix\\ 5\\ Glossary:\\ lossary\\ g',
     "A section heading in small capitals on its own line (verified in poppler's text), read by pdfminer as split letters ('r eferences'); the parser keeps headings as structure. Not requirement text.")
rule('ich\\-q3d\\-r2\\.pdf', 'page\\ 29', '\\+next\\ to\\ Appendix\\ 3:\\ r\\ eferences',
     "A section heading in small capitals on its own line (verified in poppler's text), read by pdfminer as split letters ('r eferences'); the parser keeps headings as structure. Not requirement text.")
rule('ich\\-q3d\\-r2\\.pdf', 'page\\ 29', '\\+next\\ to\\ _unnumbered:4:\\ eferences\\ r',
     "A section heading in small capitals on its own line (verified in poppler's text), read by pdfminer as split letters ('r eferences'); the parser keeps headings as structure. Not requirement text.")
rule('ich\\-q3d\\-r2\\.pdf', 'page\\ 31', '\\+next\\ to\\ _unnumbered:4:\\ r\\ eferences',
     "A section heading in small capitals on its own line (verified in poppler's text), read by pdfminer as split letters ('r eferences'); the parser keeps headings as structure. Not requirement text.")
rule('ich\\-q3d\\-r2\\.pdf', 'page\\ 31', '\\+next\\ to\\ _unnumbered:5:\\ eferences\\ r',
     "A section heading in small capitals on its own line (verified in poppler's text), read by pdfminer as split letters ('r eferences'); the parser keeps headings as structure. Not requirement text.")
rule('ich\\-q3d\\-r2\\.pdf', 'page\\ 34', '\\+next\\ to\\ Appendix\\ 3\\ 7\\.3:\\ r\\ eferences',
     "A section heading in small capitals on its own line (verified in poppler's text), read by pdfminer as split letters ('r eferences'); the parser keeps headings as structure. Not requirement text.")
rule('ich\\-q3d\\-r2\\.pdf', 'page\\ 34', '\\+next\\ to\\ _unnumbered:6:\\ eferences\\ r',
     "A section heading in small capitals on its own line (verified in poppler's text), read by pdfminer as split letters ('r eferences'); the parser keeps headings as structure. Not requirement text.")
rule('ich\\-q3d\\-r2\\.pdf', 'page\\ 36', '\\+next\\ to\\ _unnumbered:6:\\ r\\ eferences',
     "A section heading in small capitals on its own line (verified in poppler's text), read by pdfminer as split letters ('r eferences'); the parser keeps headings as structure. Not requirement text.")
rule('ich\\-q3d\\-r2\\.pdf', 'page\\ 36', '\\+next\\ to\\ _unnumbered:7:\\ eferences\\ r',
     "A section heading in small capitals on its own line (verified in poppler's text), read by pdfminer as split letters ('r eferences'); the parser keeps headings as structure. Not requirement text.")
rule('ich\\-q3d\\-r2\\.pdf', 'page\\ 39', '\\+next\\ to\\ _unnumbered:7:\\ r\\ eferences',
     "A section heading in small capitals on its own line (verified in poppler's text), read by pdfminer as split letters ('r eferences'); the parser keeps headings as structure. Not requirement text.")
rule('ich\\-q3d\\-r2\\.pdf', 'page\\ 39', '\\+next\\ to\\ _unnumbered:8:\\ eferences\\ r',
     "A section heading in small capitals on its own line (verified in poppler's text), read by pdfminer as split letters ('r eferences'); the parser keeps headings as structure. Not requirement text.")
rule('ich\\-q3d\\-r2\\.pdf', 'page\\ 41', '\\+next\\ to\\ _unnumbered:8:\\ r\\ eferences',
     "A section heading in small capitals on its own line (verified in poppler's text), read by pdfminer as split letters ('r eferences'); the parser keeps headings as structure. Not requirement text.")
rule('ich\\-q3d\\-r2\\.pdf', 'page\\ 41', '\\+next\\ to\\ _unnumbered:9:\\ eferences\\ r',
     "A section heading in small capitals on its own line (verified in poppler's text), read by pdfminer as split letters ('r eferences'); the parser keeps headings as structure. Not requirement text.")
rule('ich\\-q3d\\-r2\\.pdf', 'page\\ 42', '\\+next\\ to\\ _unnumbered:9:\\ r\\ eferences',
     "A section heading in small capitals on its own line (verified in poppler's text), read by pdfminer as split letters ('r eferences'); the parser keeps headings as structure. Not requirement text.")
rule('ich\\-q3d\\-r2\\.pdf', 'page\\ 42', '\\+next\\ to\\ _unnumbered:10:\\ eferences\\ r',
     "A section heading in small capitals on its own line (verified in poppler's text), read by pdfminer as split letters ('r eferences'); the parser keeps headings as structure. Not requirement text.")
rule('ich\\-q3d\\-r2\\.pdf', 'page\\ 45', '\\+next\\ to\\ _unnumbered:10:\\ r\\ eferences',
     "A section heading in small capitals on its own line (verified in poppler's text), read by pdfminer as split letters ('r eferences'); the parser keeps headings as structure. Not requirement text.")
rule('ich\\-q3d\\-r2\\.pdf', 'page\\ 45', '\\+next\\ to\\ _unnumbered:11:\\ eferences\\ r',
     "A section heading in small capitals on its own line (verified in poppler's text), read by pdfminer as split letters ('r eferences'); the parser keeps headings as structure. Not requirement text.")
rule('ich\\-q3d\\-r2\\.pdf', 'page\\ 46', '\\+next\\ to\\ _unnumbered:11:\\ r\\ eferences',
     "A section heading in small capitals on its own line (verified in poppler's text), read by pdfminer as split letters ('r eferences'); the parser keeps headings as structure. Not requirement text.")
rule('ich\\-q3d\\-r2\\.pdf', 'page\\ 46', '\\+next\\ to\\ _unnumbered:12:\\ eferences\\ r',
     "A section heading in small capitals on its own line (verified in poppler's text), read by pdfminer as split letters ('r eferences'); the parser keeps headings as structure. Not requirement text.")
rule('ich\\-q3d\\-r2\\.pdf', 'page\\ 48', '\\+next\\ to\\ _unnumbered:12:\\ r\\ eferences',
     "A section heading in small capitals on its own line (verified in poppler's text), read by pdfminer as split letters ('r eferences'); the parser keeps headings as structure. Not requirement text.")
rule('ich\\-q3d\\-r2\\.pdf', 'page\\ 48', '\\+next\\ to\\ _unnumbered:13:\\ eferences\\ r',
     "A section heading in small capitals on its own line (verified in poppler's text), read by pdfminer as split letters ('r eferences'); the parser keeps headings as structure. Not requirement text.")
rule('ich\\-q3d\\-r2\\.pdf', 'page\\ 50', '\\+next\\ to\\ _unnumbered:13:\\ r\\ eferences',
     "A section heading in small capitals on its own line (verified in poppler's text), read by pdfminer as split letters ('r eferences'); the parser keeps headings as structure. Not requirement text.")
rule('ich\\-q3d\\-r2\\.pdf', 'page\\ 50', '\\+next\\ to\\ _unnumbered:14:\\ eferences\\ r',
     "A section heading in small capitals on its own line (verified in poppler's text), read by pdfminer as split letters ('r eferences'); the parser keeps headings as structure. Not requirement text.")
rule('ich\\-q3d\\-r2\\.pdf', 'page\\ 52', '\\+next\\ to\\ _unnumbered:14:\\ r\\ eferences',
     "A section heading in small capitals on its own line (verified in poppler's text), read by pdfminer as split letters ('r eferences'); the parser keeps headings as structure. Not requirement text.")
rule('ich\\-q3d\\-r2\\.pdf', 'page\\ 52', '\\+next\\ to\\ _unnumbered:15:\\ eferences\\ r',
     "A section heading in small capitals on its own line (verified in poppler's text), read by pdfminer as split letters ('r eferences'); the parser keeps headings as structure. Not requirement text.")
rule('ich\\-q3d\\-r2\\.pdf', 'page\\ 54', '\\+next\\ to\\ _unnumbered:15:\\ r\\ eferences',
     "A section heading in small capitals on its own line (verified in poppler's text), read by pdfminer as split letters ('r eferences'); the parser keeps headings as structure. Not requirement text.")
rule('ich\\-q3d\\-r2\\.pdf', 'page\\ 54', '\\+next\\ to\\ _unnumbered:16:\\ eferences\\ r',
     "A section heading in small capitals on its own line (verified in poppler's text), read by pdfminer as split letters ('r eferences'); the parser keeps headings as structure. Not requirement text.")
rule('ich\\-q3d\\-r2\\.pdf', 'page\\ 57', '\\+next\\ to\\ _unnumbered:16:\\ r\\ eferences',
     "A section heading in small capitals on its own line (verified in poppler's text), read by pdfminer as split letters ('r eferences'); the parser keeps headings as structure. Not requirement text.")
rule('ich\\-q3d\\-r2\\.pdf', 'page\\ 57', '\\+next\\ to\\ _unnumbered:17:\\ eferences\\ r',
     "A section heading in small capitals on its own line (verified in poppler's text), read by pdfminer as split letters ('r eferences'); the parser keeps headings as structure. Not requirement text.")
rule('ich\\-q3d\\-r2\\.pdf', 'page\\ 59', '\\+next\\ to\\ _unnumbered:17:\\ r\\ eferences',
     "A section heading in small capitals on its own line (verified in poppler's text), read by pdfminer as split letters ('r eferences'); the parser keeps headings as structure. Not requirement text.")
rule('ich\\-q3d\\-r2\\.pdf', 'page\\ 59', '\\+next\\ to\\ _unnumbered:18:\\ eferences\\ r',
     "A section heading in small capitals on its own line (verified in poppler's text), read by pdfminer as split letters ('r eferences'); the parser keeps headings as structure. Not requirement text.")
rule('ich\\-q3d\\-r2\\.pdf', 'page\\ 62', '\\+next\\ to\\ _unnumbered:18:\\ r\\ eferences',
     "A section heading in small capitals on its own line (verified in poppler's text), read by pdfminer as split letters ('r eferences'); the parser keeps headings as structure. Not requirement text.")
rule('ich\\-q3d\\-r2\\.pdf', 'page\\ 62', '\\+next\\ to\\ _unnumbered:19:\\ eferences\\ r',
     "A section heading in small capitals on its own line (verified in poppler's text), read by pdfminer as split letters ('r eferences'); the parser keeps headings as structure. Not requirement text.")
rule('ich\\-q3d\\-r2\\.pdf', 'page\\ 64', '\\+next\\ to\\ _unnumbered:19:\\ r\\ eferences',
     "A section heading in small capitals on its own line (verified in poppler's text), read by pdfminer as split letters ('r eferences'); the parser keeps headings as structure. Not requirement text.")
rule('ich\\-q3d\\-r2\\.pdf', 'page\\ 64', '\\+next\\ to\\ _unnumbered:20:\\ eferences\\ r',
     "A section heading in small capitals on its own line (verified in poppler's text), read by pdfminer as split letters ('r eferences'); the parser keeps headings as structure. Not requirement text.")
rule('ich\\-q3d\\-r2\\.pdf', 'page\\ 66', '\\+next\\ to\\ _unnumbered:20:\\ r\\ eferences',
     "A section heading in small capitals on its own line (verified in poppler's text), read by pdfminer as split letters ('r eferences'); the parser keeps headings as structure. Not requirement text.")
rule('ich\\-q3d\\-r2\\.pdf', 'page\\ 66', '\\+next\\ to\\ _unnumbered:21:\\ eferences\\ r',
     "A section heading in small capitals on its own line (verified in poppler's text), read by pdfminer as split letters ('r eferences'); the parser keeps headings as structure. Not requirement text.")
rule('ich\\-q3d\\-r2\\.pdf', 'page\\ 68', '\\+next\\ to\\ _unnumbered:22:\\ eferences\\ r',
     "A section heading in small capitals on its own line (verified in poppler's text), read by pdfminer as split letters ('r eferences'); the parser keeps headings as structure. Not requirement text.")
rule('ich\\-q3d\\-r2\\.pdf', 'page\\ 69', '\\+next\\ to\\ _unnumbered:22:\\ r\\ eferences',
     "A section heading in small capitals on its own line (verified in poppler's text), read by pdfminer as split letters ('r eferences'); the parser keeps headings as structure. Not requirement text.")
rule('ich\\-q3d\\-r2\\.pdf', 'page\\ 72', '\\+next\\ to\\ _unnumbered:24:\\ eferences\\ r',
     "A section heading in small capitals on its own line (verified in poppler's text), read by pdfminer as split letters ('r eferences'); the parser keeps headings as structure. Not requirement text.")
rule('ich\\-q9r1\\.pdf', 'page\\ 3', '\\+next\\ to\\ _unnumbered:1:\\ c\\ ontents',
     "The 'TABLE OF CONTENTS' heading in small capitals, read as split words; front matter.")
rule('india\\-cdsco\\-gdp\\-guidelines\\-2024\\.pdf', 'page\\ 11', '\\+next\\ to\\ 11\\.15:\\ pressurized\\ gases',
     "Parser defect (0b): the PDF's text layer has 'pressurizedgases' without a space (poppler keeps it, pdfminer splits it); the stored clause 11.15 has the glued word.")
rule('india\\-cdsco\\-gdp\\-guidelines\\-2024\\.pdf', 'page\\ 11', '\\+next\\ to\\ 11\\.16:\\ gases\\ pressurized',
     "Parser defect (0b): the PDF's text layer has 'pressurizedgases' without a space (poppler keeps it, pdfminer splits it); the stored clause 11.15 has the glued word.")
rule('india\\-cdsco\\-gdp\\-guidelines\\-2024\\.pdf', 'page\\ 19', '\\+next\\ to\\ 16\\.17:\\ the\\ records',
     "Parser defect (0b): the PDF's text layer has 'therecords' without a space; the stored clause 16.17 ends with the glued word.")
rule('india\\-cdsco\\-gdp\\-guidelines\\-2024\\.pdf', 'page\\ 19', '\\+next\\ to\\ 16\\.18:\\ records\\ the',
     "Parser defect (0b): the PDF's text layer has 'therecords' without a space; the stored clause 16.17 ends with the glued word.")
rule('india\\-drugs\\-rules\\-1945\\-consolidated\\-2024\\-07\\.pdf', 'page\\ 326', '\\+next\\ to\\ Part\\ XV\\ 4\\ \\#25:\\ injections\\ parenteral',
     "Item '[3. Vaccines for parenteral injections.]' of the list of biological products, stored with the list's earlier clause; pdfminer reads its words beside item 4.")
rule('india\\-drugs\\-rules\\-1945\\-consolidated\\-2024\\-07\\.pdf', 'page\\ 502', '\\+next\\ to\\ Part\\ IV\\ 3:\\ 8\\ actilyse',
     "Two-column drug list: entry '8. Actilyse' is stored in Part IV 4 (columns read in layout order, known parser limitation).")
rule('pics\\-pe009\\-18\\-annexes\\.pdf', 'page\\ 9', '\\+next\\ to\\ Annex\\ 1\\ 1:\\ 2\\ principle',
     "A section heading printed on its own line (verified in poppler's text) that the parser keeps as structure, not as clause text; heading words, not requirement text.")
rule('pics\\-pe009\\-18\\-annexes\\.pdf', 'page\\ 9', '\\+next\\ to\\ Annex\\ 1\\ 2\\.1:\\ principle\\ 2',
     "A section heading printed on its own line (verified in poppler's text) that the parser keeps as structure, not as clause text; heading words, not requirement text.")
rule('pics\\-pe009\\-18\\-annexes\\.pdf', 'page\\ 79', '\\+next\\ to\\ Annex\\ 2A\\ 1\\ Principle:\\ manufacture',
     "A word of the running page header 'Annex 2A Manufacture of advanced therapy medicinal products'; page artefact.")
rule('pics\\-pe009\\-18\\-annexes\\.pdf', 'page\\ 165', '\\+next\\ to\\ Annex\\ 7\\ Principle:\\ products',
     "A word of the running page header 'Annex 7 Manufacture of herbal medicinal products'; page artefact.")
rule('pics\\-pe009\\-18\\-part2\\.pdf', 'page\\ 6', '\\+next\\ to\\ Part\\ II\\ 1\\.1:\\ introduction\\ 1',
     "A section heading printed on its own line (verified in poppler's text) that the parser keeps as structure, not as clause text; heading words, not requirement text.")
rule('pics\\-pi009\\-4\\-am\\-utilities\\.pdf', 'page\\ 2', '\\+next\\ to\\ 2\\.1:\\ introduction\\ 2',
     "A section heading printed on its own line (verified in poppler's text) that the parser keeps as structure, not as clause text; heading words, not requirement text.")
rule('pics\\-pi009\\-4\\-am\\-utilities\\.pdf', 'page\\ 2', '\\+next\\ to\\ 2\\.2:\\ 3\\ purpose',
     "A section heading printed on its own line (verified in poppler's text) that the parser keeps as structure, not as clause text; heading words, not requirement text.")
rule('pics\\-pi009\\-4\\-am\\-utilities\\.pdf', 'page\\ 2', '\\+next\\ to\\ 3\\.1:\\ purpose\\ 3',
     "A section heading printed on its own line (verified in poppler's text) that the parser keeps as structure, not as clause text; heading words, not requirement text.")
rule('pics\\-pi009\\-4\\-am\\-utilities\\.pdf', 'page\\ 2', '\\+next\\ to\\ 3\\.2:\\ 4\\ scope',
     "A section heading printed on its own line (verified in poppler's text) that the parser keeps as structure, not as clause text; heading words, not requirement text.")
rule('pics\\-pi009\\-4\\-am\\-utilities\\.pdf', 'page\\ 2', '\\+next\\ to\\ 4\\.1:\\ scope\\ 4',
     "A section heading printed on its own line (verified in poppler's text) that the parser keeps as structure, not as clause text; heading words, not requirement text.")
rule('pics\\-pi014\\-3\\-isolators\\.pdf', 'page\\ 3', '\\+next\\ to\\ 2\\.1:\\ introduction\\ 2',
     "A section heading printed on its own line (verified in poppler's text) that the parser keeps as structure, not as clause text; heading words, not requirement text.")
rule('pics\\-pi014\\-3\\-isolators\\.pdf', 'page\\ 4', '\\+next\\ to\\ 3:\\ 4\\ scope',
     "A section heading printed on its own line (verified in poppler's text) that the parser keeps as structure, not as clause text; heading words, not requirement text.")
rule('pics\\-pi014\\-3\\-isolators\\.pdf', 'page\\ 4', '\\+next\\ to\\ 4\\.1:\\ scope\\ 4',
     "A section heading printed on its own line (verified in poppler's text) that the parser keeps as structure, not as clause text; heading words, not requirement text.")
rule('pics\\-pi023\\-2\\-am\\-qc\\-labs\\.pdf', 'page\\ 2', '\\+next\\ to\\ 2:\\ 3\\ purpose',
     "A section heading printed on its own line (verified in poppler's text) that the parser keeps as structure, not as clause text; heading words, not requirement text.")
rule('pics\\-pi023\\-2\\-am\\-qc\\-labs\\.pdf', 'page\\ 2', '\\+next\\ to\\ 3\\.1:\\ purpose\\ 3',
     "A section heading printed on its own line (verified in poppler's text) that the parser keeps as structure, not as clause text; heading words, not requirement text.")
rule('pics\\-pi023\\-2\\-am\\-qc\\-labs\\.pdf', 'page\\ 3', '\\+next\\ to\\ 3\\.2:\\ 4\\ scope',
     "A section heading printed on its own line (verified in poppler's text) that the parser keeps as structure, not as clause text; heading words, not requirement text.")
rule('pics\\-pi023\\-2\\-am\\-qc\\-labs\\.pdf', 'page\\ 3', '\\+next\\ to\\ 4\\.1:\\ scope\\ 4',
     "A section heading printed on its own line (verified in poppler's text) that the parser keeps as structure, not as clause text; heading words, not requirement text.")
rule('pics\\-pi028\\-2\\-am\\-packaging\\.pdf', 'page\\ 2', '\\+next\\ to\\ 2\\.1:\\ introduction\\ 2',
     "A section heading printed on its own line (verified in poppler's text) that the parser keeps as structure, not as clause text; heading words, not requirement text.")
rule('pics\\-pi028\\-2\\-am\\-packaging\\.pdf', 'page\\ 2', '\\+next\\ to\\ 2\\.3:\\ 3\\ purpose',
     "A section heading printed on its own line (verified in poppler's text) that the parser keeps as structure, not as clause text; heading words, not requirement text.")
rule('pics\\-pi028\\-2\\-am\\-packaging\\.pdf', 'page\\ 2', '\\+next\\ to\\ 3\\.1:\\ purpose\\ 3',
     "A section heading printed on its own line (verified in poppler's text) that the parser keeps as structure, not as clause text; heading words, not requirement text.")
rule('pics\\-pi028\\-2\\-am\\-packaging\\.pdf', 'page\\ 3', '\\+next\\ to\\ 3\\.2:\\ 4\\ scope',
     "A section heading printed on its own line (verified in poppler's text) that the parser keeps as structure, not as clause text; heading words, not requirement text.")
rule('pics\\-pi028\\-2\\-am\\-packaging\\.pdf', 'page\\ 3', '\\+next\\ to\\ 4\\.1:\\ scope\\ 4',
     "A section heading printed on its own line (verified in poppler's text) that the parser keeps as structure, not as clause text; heading words, not requirement text.")
rule('pics\\-pi030\\-1\\-am\\-api\\.pdf', 'page\\ 2', '\\+next\\ to\\ 2\\.1:\\ introduction\\ 2',
     "A section heading printed on its own line (verified in poppler's text) that the parser keeps as structure, not as clause text; heading words, not requirement text.")
rule('pics\\-pi030\\-1\\-am\\-api\\.pdf', 'page\\ 2', '\\+next\\ to\\ 2\\.3:\\ 3\\ purpose',
     "A section heading printed on its own line (verified in poppler's text) that the parser keeps as structure, not as clause text; heading words, not requirement text.")
rule('pics\\-pi030\\-1\\-am\\-api\\.pdf', 'page\\ 2', '\\+next\\ to\\ 3\\.1:\\ purpose\\ 3',
     "A section heading printed on its own line (verified in poppler's text) that the parser keeps as structure, not as clause text; heading words, not requirement text.")
rule('pics\\-pi030\\-1\\-am\\-api\\.pdf', 'page\\ 2', '\\+next\\ to\\ 3\\.2:\\ 4\\ scope',
     "A section heading printed on its own line (verified in poppler's text) that the parser keeps as structure, not as clause text; heading words, not requirement text.")
rule('pics\\-pi030\\-1\\-am\\-api\\.pdf', 'page\\ 2', '\\+next\\ to\\ 4\\.1:\\ scope\\ 4',
     "A section heading printed on its own line (verified in poppler's text) that the parser keeps as structure, not as clause text; heading words, not requirement text.")
rule('pics\\-pi038\\-2\\-am\\-qrm\\.pdf', 'page\\ 2', '\\+next\\ to\\ 2\\.1:\\ introduction\\ 2',
     "A section heading printed on its own line (verified in poppler's text) that the parser keeps as structure, not as clause text; heading words, not requirement text.")
rule('pics\\-pi038\\-2\\-am\\-qrm\\.pdf', 'page\\ 3', '\\+next\\ to\\ 2\\.5:\\ 3\\ purpose',
     "A section heading printed on its own line (verified in poppler's text) that the parser keeps as structure, not as clause text; heading words, not requirement text.")
rule('pics\\-pi038\\-2\\-am\\-qrm\\.pdf', 'page\\ 3', '\\+next\\ to\\ 3\\.1:\\ purpose\\ 3',
     "A section heading printed on its own line (verified in poppler's text) that the parser keeps as structure, not as clause text; heading words, not requirement text.")
rule('pics\\-pi038\\-2\\-am\\-qrm\\.pdf', 'page\\ 3', '\\+next\\ to\\ 3\\.2:\\ 4\\ scope',
     "A section heading printed on its own line (verified in poppler's text) that the parser keeps as structure, not as clause text; heading words, not requirement text.")
rule('pics\\-pi038\\-2\\-am\\-qrm\\.pdf', 'page\\ 3', '\\+next\\ to\\ 4\\.1:\\ scope\\ 4',
     "A section heading printed on its own line (verified in poppler's text) that the parser keeps as structure, not as clause text; heading words, not requirement text.")
rule('pics\\-pi040\\-1\\-deficiency\\-classification\\.pdf', 'page\\ 3', '\\+next\\ to\\ Appendix\\ 2\\ 2\\.1:\\ introduction\\ 2',
     "A section heading printed on its own line (verified in poppler's text) that the parser keeps as structure, not as clause text; heading words, not requirement text.")
rule('pics\\-pi041\\-1\\-data\\-integrity\\.pdf', 'page\\ 3', '\\+next\\ to\\ 2\\.1:\\ introduction\\ 2',
     "A section heading printed on its own line (verified in poppler's text) that the parser keeps as structure, not as clause text; heading words, not requirement text.")
rule('pics\\-pi043\\-1\\-am\\-cross\\-contamination\\.pdf', 'page\\ 3', '\\+next\\ to\\ 2\\.1:\\ introduction\\ 2',
     "A section heading printed on its own line (verified in poppler's text) that the parser keeps as structure, not as clause text; heading words, not requirement text.")
rule('pics\\-pi045\\-1\\-excipient\\-risk\\-assessment\\.pdf', 'page\\ 3', '\\+next\\ to\\ 2:\\ 3\\ scope',
     "A section heading printed on its own line (verified in poppler's text) that the parser keeps as structure, not as clause text; heading words, not requirement text.")
rule('pics\\-pi045\\-1\\-excipient\\-risk\\-assessment\\.pdf', 'page\\ 3', '\\+next\\ to\\ 3\\.1:\\ scope\\ 3',
     "A section heading printed on its own line (verified in poppler's text) that the parser keeps as structure, not as clause text; heading words, not requirement text.")
rule('pics\\-pi052\\-1\\-am\\-hbel\\.pdf', 'page\\ 2', '\\+next\\ to\\ 2\\.1:\\ introduction\\ 2',
     "A section heading printed on its own line (verified in poppler's text) that the parser keeps as structure, not as clause text; heading words, not requirement text.")
rule('pics\\-pi052\\-1\\-am\\-hbel\\.pdf', 'page\\ 3', '\\+next\\ to\\ 2\\.7:\\ 3\\ purpose',
     "A section heading printed on its own line (verified in poppler's text) that the parser keeps as structure, not as clause text; heading words, not requirement text.")
rule('pics\\-pi052\\-1\\-am\\-hbel\\.pdf', 'page\\ 3', '\\+next\\ to\\ 3\\.1:\\ purpose\\ 3',
     "A section heading printed on its own line (verified in poppler's text) that the parser keeps as structure, not as clause text; heading words, not requirement text.")
rule('pics\\-pi052\\-1\\-am\\-hbel\\.pdf', 'page\\ 3', '\\+next\\ to\\ 3\\.1:\\ 4\\ scope',
     "A section heading printed on its own line (verified in poppler's text) that the parser keeps as structure, not as clause text; heading words, not requirement text.")
rule('pics\\-pi052\\-1\\-am\\-hbel\\.pdf', 'page\\ 3', '\\+next\\ to\\ 4\\.1:\\ scope\\ 4',
     "A section heading printed on its own line (verified in poppler's text) that the parser keeps as structure, not as clause text; heading words, not requirement text.")
rule('pics\\-pi054\\-1\\-pqs\\-effectiveness\\.pdf', 'page\\ 2', '\\+next\\ to\\ 2\\.3:\\ 3\\ purpose',
     "A section heading printed on its own line (verified in poppler's text) that the parser keeps as structure, not as clause text; heading words, not requirement text.")
rule('pics\\-pi054\\-1\\-pqs\\-effectiveness\\.pdf', 'page\\ 2', '\\+next\\ to\\ 3\\.1:\\ purpose\\ 3',
     "A section heading printed on its own line (verified in poppler's text) that the parser keeps as structure, not as clause text; heading words, not requirement text.")
rule('pics\\-pi058\\-1\\-annex1\\-interpretation\\.pdf', 'page\\ 3', '\\+next\\ to\\ 2\\.1\\.2:\\ 2\\.2\\ basics',
     "A section heading printed on its own line (verified in poppler's text) that the parser keeps as structure, not as clause text; heading words, not requirement text.")
rule('pics\\-pi058\\-1\\-annex1\\-interpretation\\.pdf', 'page\\ 3', '\\+next\\ to\\ 2\\.2\\.1:\\ basics\\ 2\\.2',
     "A section heading printed on its own line (verified in poppler's text) that the parser keeps as structure, not as clause text; heading words, not requirement text.")
rule('who\\-trs1010\\-a10\\-stability\\.pdf', 'page\\ 4', '\\+next\\ to\\ Appendix\\ 3\\ 1\\.1:\\ introduction\\ 1',
     "A section heading printed on its own line (verified in poppler's text) that the parser keeps as structure, not as clause text; heading words, not requirement text.")
rule('who\\-trs1019\\-a3\\-validation\\.pdf', 'page\\ 3', '\\+next\\ to\\ 1\\.1:\\ introduction\\ 1',
     "A section heading printed on its own line (verified in poppler's text) that the parser keeps as structure, not as clause text; heading words, not requirement text.")
rule('who\\-trs1019\\-a3\\-validation\\.pdf', 'page\\ 3', '\\+next\\ to\\ 1\\.4:\\ 2\\ scope',
     "A section heading printed on its own line (verified in poppler's text) that the parser keeps as structure, not as clause text; heading words, not requirement text.")
rule('who\\-trs1019\\-a3\\-validation\\.pdf', 'page\\ 3', '\\+next\\ to\\ 2\\.1:\\ scope\\ 2',
     "A section heading printed on its own line (verified in poppler's text) that the parser keeps as structure, not as clause text; heading words, not requirement text.")
rule('who\\-trs1019\\-a3\\-validation\\.pdf', 'page\\ 20', '\\+next\\ to\\ Appendix\\ 3\\ 1\\.1:\\ principle\\ 1',
     "A section heading printed on its own line (verified in poppler's text) that the parser keeps as structure, not as clause text; heading words, not requirement text.")
rule('who\\-trs1019\\-a3\\-validation\\.pdf', 'page\\ 20', '\\+next\\ to\\ Appendix\\ 3\\ 1\\.6:\\ 2\\ scope',
     "A section heading printed on its own line (verified in poppler's text) that the parser keeps as structure, not as clause text; heading words, not requirement text.")
rule('who\\-trs1019\\-a3\\-validation\\.pdf', 'page\\ 20', '\\+next\\ to\\ Appendix\\ 3\\ 2\\.1:\\ scope\\ 2',
     "A section heading printed on its own line (verified in poppler's text) that the parser keeps as structure, not as clause text; heading words, not requirement text.")
rule('who\\-trs1019\\-a3\\-validation\\.pdf', 'page\\ 31', '\\+next\\ to\\ Appendix\\ 4\\ 1\\.1:\\ principle\\ 1',
     "A section heading printed on its own line (verified in poppler's text) that the parser keeps as structure, not as clause text; heading words, not requirement text.")
rule('who\\-trs1019\\-a3\\-validation\\.pdf', 'page\\ 31', '\\+next\\ to\\ Appendix\\ 4\\ 1\\.5:\\ 2\\ general',
     "A section heading printed on its own line (verified in poppler's text) that the parser keeps as structure, not as clause text; heading words, not requirement text.")
rule('who\\-trs1019\\-a3\\-validation\\.pdf', 'page\\ 31', '\\+next\\ to\\ Appendix\\ 4\\ 2\\.1:\\ general\\ 2',
     "A section heading printed on its own line (verified in poppler's text) that the parser keeps as structure, not as clause text; heading words, not requirement text.")
rule('who\\-trs1019\\-a3\\-validation\\.pdf', 'page\\ 65', '\\+next\\ to\\ Appendix\\ 6\\ 1\\.1:\\ principle\\ 1',
     "A section heading printed on its own line (verified in poppler's text) that the parser keeps as structure, not as clause text; heading words, not requirement text.")
rule('who\\-trs1019\\-a3\\-validation\\.pdf', 'page\\ 65', '\\+next\\ to\\ Appendix\\ 6\\ 1\\.4:\\ 2\\ scope',
     "A section heading printed on its own line (verified in poppler's text) that the parser keeps as structure, not as clause text; heading words, not requirement text.")
rule('who\\-trs1019\\-a3\\-validation\\.pdf', 'page\\ 65', '\\+next\\ to\\ Appendix\\ 6\\ 2\\.1:\\ scope\\ 2',
     "A section heading printed on its own line (verified in poppler's text) that the parser keeps as structure, not as clause text; heading words, not requirement text.")
rule('who\\-trs1025\\-a3\\-wfi\\-non\\-distillation\\.pdf', 'page\\ 2', '\\+next\\ to\\ 1\\.1:\\ introduction\\ 1',
     "A section heading printed on its own line (verified in poppler's text) that the parser keeps as structure, not as clause text; heading words, not requirement text.")
rule('who\\-trs1025\\-a3\\-wfi\\-non\\-distillation\\.pdf', 'page\\ 2', '\\+next\\ to\\ 1\\.2:\\ 2\\ scope',
     "A section heading printed on its own line (verified in poppler's text) that the parser keeps as structure, not as clause text; heading words, not requirement text.")
rule('who\\-trs1025\\-a3\\-wfi\\-non\\-distillation\\.pdf', 'page\\ 2', '\\+next\\ to\\ 2\\.1:\\ scope\\ 2',
     "A section heading printed on its own line (verified in poppler's text) that the parser keeps as structure, not as clause text; heading words, not requirement text.")
rule('who\\-trs1025\\-a3\\-wfi\\-non\\-distillation\\.pdf', 'page\\ 2', '\\+next\\ to\\ 2\\.2:\\ 3\\ monographs',
     "A section heading printed on its own line (verified in poppler's text) that the parser keeps as structure, not as clause text; heading words, not requirement text.")
rule('who\\-trs1025\\-a3\\-wfi\\-non\\-distillation\\.pdf', 'page\\ 2', '\\+next\\ to\\ 3\\.1:\\ monographs\\ 3',
     "A section heading printed on its own line (verified in poppler's text) that the parser keeps as structure, not as clause text; heading words, not requirement text.")
rule('who\\-trs1025\\-a7\\-storage\\-distribution\\.pdf', 'page\\ 2', '\\+next\\ to\\ 1\\.1:\\ introduction\\ 1',
     "A section heading printed on its own line (verified in poppler's text) that the parser keeps as structure, not as clause text; heading words, not requirement text.")
rule('who\\-trs1033\\-a4\\-data\\-integrity\\.pdf', 'page\\ 2', '\\+next\\ to\\ 1\\.3:\\ 2\\ scope',
     "A section heading printed on its own line (verified in poppler's text) that the parser keeps as structure, not as clause text; heading words, not requirement text.")
rule('who\\-trs1033\\-a4\\-data\\-integrity\\.pdf', 'page\\ 2', '\\+next\\ to\\ 2\\.1:\\ scope\\ 2',
     "A section heading printed on its own line (verified in poppler's text) that the parser keeps as structure, not as clause text; heading words, not requirement text.")
rule('who\\-trs943\\-a3\\-reference\\-substances\\.pdf', 'page\\ 21', '\\+next\\ to\\ Annex\\ 3\\ B\\ 4\\.3:\\ predefi\\ ned',
     "A word set with an fi/fl ligature at a clause edge, read by pdfminer as two pieces ('specifi cations'); the joined word is stored in the neighbouring clause (verified). No word lost.")
rule('who\\-trs943\\-a3\\-reference\\-substances\\.pdf', 'page\\ 21', '\\+next\\ to\\ Annex\\ 3\\ B\\ 4\\.4:\\ ned\\ predefi',
     "A word set with an fi/fl ligature at a clause edge, read by pdfminer as two pieces ('specifi cations'); the joined word is stored in the neighbouring clause (verified). No word lost.")
rule('who\\-trs957\\-a2\\-api\\.pdf', 'page\\ 1', '\\+next\\ to\\ Annex\\ 2\\ 3\\.1:\\ qualifi\\ cations',
     "A word set with an fi/fl ligature at a clause edge, read by pdfminer as two pieces ('specifi cations'); the joined word is stored in the neighbouring clause (verified). No word lost.")
rule('who\\-trs957\\-a2\\-api\\.pdf', 'page\\ 1', '\\+next\\ to\\ Annex\\ 2\\ 3\\.2:\\ cations\\ qualifi',
     "A word set with an fi/fl ligature at a clause edge, read by pdfminer as two pieces ('specifi cations'); the joined word is stored in the neighbouring clause (verified). No word lost.")
rule('who\\-trs957\\-a2\\-api\\.pdf', 'page\\ 1', '\\+next\\ to\\ Annex\\ 2\\ 6\\.1:\\ specifi\\ cations',
     "A word set with an fi/fl ligature at a clause edge, read by pdfminer as two pieces ('specifi cations'); the joined word is stored in the neighbouring clause (verified). No word lost.")
rule('who\\-trs957\\-a2\\-api\\.pdf', 'page\\ 1', '\\+next\\ to\\ Annex\\ 2\\ 6\\.2:\\ cations\\ specifi',
     "A word set with an fi/fl ligature at a clause edge, read by pdfminer as two pieces ('specifi cations'); the joined word is stored in the neighbouring clause (verified). No word lost.")
rule('who\\-trs957\\-a2\\-api\\.pdf', 'page\\ 2', '\\+next\\ to\\ Annex\\ 2\\ 12\\.3:\\ qualifi\\ cation',
     "A word set with an fi/fl ligature at a clause edge, read by pdfminer as two pieces ('specifi cations'); the joined word is stored in the neighbouring clause (verified). No word lost.")
rule('who\\-trs957\\-a2\\-api\\.pdf', 'page\\ 2', '\\+next\\ to\\ Annex\\ 2\\ 12\\.4:\\ cation\\ qualifi',
     "A word set with an fi/fl ligature at a clause edge, read by pdfminer as two pieces ('specifi cations'); the joined word is stored in the neighbouring clause (verified). No word lost.")
rule('who\\-trs957\\-a2\\-api\\.pdf', 'page\\ 3', '\\+next\\ to\\ Annex\\ 2\\ 18\\.4:\\ purifi\\ cation',
     "A word set with an fi/fl ligature at a clause edge, read by pdfminer as two pieces ('specifi cations'); the joined word is stored in the neighbouring clause (verified). No word lost.")
rule('who\\-trs957\\-a2\\-api\\.pdf', 'page\\ 3', '\\+next\\ to\\ Annex\\ 2\\ 18\\.5:\\ cation\\ purifi',
     "A word set with an fi/fl ligature at a clause edge, read by pdfminer as two pieces ('specifi cations'); the joined word is stored in the neighbouring clause (verified). No word lost.")
rule('who\\-trs957\\-a2\\-api\\.pdf', 'page\\ 7', '\\+next\\ to\\ Annex\\ 2\\ Appendix\\ 2\\ 2\\.14:\\ specifi\\ ed',
     "A word set with an fi/fl ligature at a clause edge, read by pdfminer as two pieces ('specifi cations'); the joined word is stored in the neighbouring clause (verified). No word lost.")
rule('who\\-trs957\\-a2\\-api\\.pdf', 'page\\ 7', '\\+next\\ to\\ Annex\\ 2\\ Appendix\\ 2\\ 2\\.15:\\ ed\\ specifi',
     "A word set with an fi/fl ligature at a clause edge, read by pdfminer as two pieces ('specifi cations'); the joined word is stored in the neighbouring clause (verified). No word lost.")
rule('who\\-trs957\\-a2\\-api\\.pdf', 'page\\ 9', '\\+next\\ to\\ Annex\\ 2\\ Appendix\\ 2\\ 2\\.3:\\ qualifi\\ ed',
     "A word set with an fi/fl ligature at a clause edge, read by pdfminer as two pieces ('specifi cations'); the joined word is stored in the neighbouring clause (verified). No word lost.")
rule('who\\-trs957\\-a2\\-api\\.pdf', 'page\\ 9', '\\+next\\ to\\ Annex\\ 2\\ Appendix\\ 2\\ 2\\.4:\\ ed\\ qualifi',
     "A word set with an fi/fl ligature at a clause edge, read by pdfminer as two pieces ('specifi cations'); the joined word is stored in the neighbouring clause (verified). No word lost.")
rule('who\\-trs957\\-a2\\-api\\.pdf', 'page\\ 10', '\\+next\\ to\\ Annex\\ 2\\ Appendix\\ 2\\ 3\\.1:\\ qualifi\\ cations',
     "A word set with an fi/fl ligature at a clause edge, read by pdfminer as two pieces ('specifi cations'); the joined word is stored in the neighbouring clause (verified). No word lost.")
rule('who\\-trs957\\-a2\\-api\\.pdf', 'page\\ 10', '\\+next\\ to\\ Annex\\ 2\\ Appendix\\ 2\\ 3\\.10:\\ cations\\ qualifi',
     "A word set with an fi/fl ligature at a clause edge, read by pdfminer as two pieces ('specifi cations'); the joined word is stored in the neighbouring clause (verified). No word lost.")
rule('who\\-trs957\\-a2\\-api\\.pdf', 'page\\ 13', '\\+next\\ to\\ Annex\\ 2\\ Appendix\\ 2\\ 4\\.60:\\ identifi\\ ed',
     "A word set with an fi/fl ligature at a clause edge, read by pdfminer as two pieces ('specifi cations'); the joined word is stored in the neighbouring clause (verified). No word lost.")
rule('who\\-trs957\\-a2\\-api\\.pdf', 'page\\ 13', '\\+next\\ to\\ Annex\\ 2\\ Appendix\\ 2\\ 4\\.7:\\ ed\\ identifi',
     "A word set with an fi/fl ligature at a clause edge, read by pdfminer as two pieces ('specifi cations'); the joined word is stored in the neighbouring clause (verified). No word lost.")
rule('who\\-trs957\\-a2\\-api\\.pdf', 'page\\ 14', '\\+next\\ to\\ Annex\\ 2\\ Appendix\\ 2\\ 5\\.11:\\ specifi\\ cations',
     "A word set with an fi/fl ligature at a clause edge, read by pdfminer as two pieces ('specifi cations'); the joined word is stored in the neighbouring clause (verified). No word lost.")
rule('who\\-trs957\\-a2\\-api\\.pdf', 'page\\ 14', '\\+next\\ to\\ Annex\\ 2\\ Appendix\\ 2\\ 5\\.12:\\ cations\\ specifi',
     "A word set with an fi/fl ligature at a clause edge, read by pdfminer as two pieces ('specifi cations'); the joined word is stored in the neighbouring clause (verified). No word lost.")
rule('who\\-trs957\\-a2\\-api\\.pdf', 'page\\ 14', '\\+next\\ to\\ Annex\\ 2\\ Appendix\\ 2\\ 5\\.13:\\ identifi\\ ed',
     "A word set with an fi/fl ligature at a clause edge, read by pdfminer as two pieces ('specifi cations'); the joined word is stored in the neighbouring clause (verified). No word lost.")
rule('who\\-trs957\\-a2\\-api\\.pdf', 'page\\ 14', '\\+next\\ to\\ Annex\\ 2\\ Appendix\\ 2\\ 5\\.14:\\ ed\\ identifi',
     "A word set with an fi/fl ligature at a clause edge, read by pdfminer as two pieces ('specifi cations'); the joined word is stored in the neighbouring clause (verified). No word lost.")
rule('who\\-trs957\\-a2\\-api\\.pdf', 'page\\ 15', '\\+next\\ to\\ Annex\\ 2\\ Appendix\\ 2\\ 5\\.22:\\ specifi\\ cations',
     "A word set with an fi/fl ligature at a clause edge, read by pdfminer as two pieces ('specifi cations'); the joined word is stored in the neighbouring clause (verified). No word lost.")
rule('who\\-trs957\\-a2\\-api\\.pdf', 'page\\ 15', '\\+next\\ to\\ Annex\\ 2\\ Appendix\\ 2\\ 5\\.23:\\ cations\\ specifi',
     "A word set with an fi/fl ligature at a clause edge, read by pdfminer as two pieces ('specifi cations'); the joined word is stored in the neighbouring clause (verified). No word lost.")
rule('who\\-trs957\\-a2\\-api\\.pdf', 'page\\ 15', '\\+next\\ to\\ Annex\\ 2\\ Appendix\\ 2\\ 5\\.25:\\ justifi\\ ed',
     "A word set with an fi/fl ligature at a clause edge, read by pdfminer as two pieces ('specifi cations'); the joined word is stored in the neighbouring clause (verified). No word lost.")
rule('who\\-trs957\\-a2\\-api\\.pdf', 'page\\ 15', '\\+next\\ to\\ Annex\\ 2\\ Appendix\\ 2\\ 5\\.26:\\ ed\\ justifi',
     "A word set with an fi/fl ligature at a clause edge, read by pdfminer as two pieces ('specifi cations'); the joined word is stored in the neighbouring clause (verified). No word lost.")
rule('who\\-trs957\\-a2\\-api\\.pdf', 'page\\ 15', '\\+next\\ to\\ Annex\\ 2\\ Appendix\\ 2\\ 5\\.33:\\ verifi\\ able',
     "A word set with an fi/fl ligature at a clause edge, read by pdfminer as two pieces ('specifi cations'); the joined word is stored in the neighbouring clause (verified). No word lost.")
rule('who\\-trs957\\-a2\\-api\\.pdf', 'page\\ 15', '\\+next\\ to\\ Annex\\ 2\\ Appendix\\ 2\\ 5\\.34:\\ able\\ verifi',
     "A word set with an fi/fl ligature at a clause edge, read by pdfminer as two pieces ('specifi cations'); the joined word is stored in the neighbouring clause (verified). No word lost.")
rule('who\\-trs957\\-a2\\-api\\.pdf', 'page\\ 17', '\\+next\\ to\\ Annex\\ 2\\ Appendix\\ 2\\ 6\\.1:\\ specifi\\ cations',
     "A word set with an fi/fl ligature at a clause edge, read by pdfminer as two pieces ('specifi cations'); the joined word is stored in the neighbouring clause (verified). No word lost.")
rule('who\\-trs957\\-a2\\-api\\.pdf', 'page\\ 17', '\\+next\\ to\\ Annex\\ 2\\ Appendix\\ 2\\ 6\\.10:\\ cations\\ specifi',
     "A word set with an fi/fl ligature at a clause edge, read by pdfminer as two pieces ('specifi cations'); the joined word is stored in the neighbouring clause (verified). No word lost.")
rule('who\\-trs957\\-a2\\-api\\.pdf', 'page\\ 17', '\\+next\\ to\\ Annex\\ 2\\ Appendix\\ 2\\ 6\\.12:\\ specifi\\ ed',
     "A word set with an fi/fl ligature at a clause edge, read by pdfminer as two pieces ('specifi cations'); the joined word is stored in the neighbouring clause (verified). No word lost.")
rule('who\\-trs957\\-a2\\-api\\.pdf', 'page\\ 17', '\\+next\\ to\\ Annex\\ 2\\ Appendix\\ 2\\ 6\\.13:\\ ed\\ specifi',
     "A word set with an fi/fl ligature at a clause edge, read by pdfminer as two pieces ('specifi cations'); the joined word is stored in the neighbouring clause (verified). No word lost.")
rule('who\\-trs957\\-a2\\-api\\.pdf', 'page\\ 22', '\\+next\\ to\\ Annex\\ 2\\ Appendix\\ 2\\ 7\\.23:\\ identifi\\ ed',
     "A word set with an fi/fl ligature at a clause edge, read by pdfminer as two pieces ('specifi cations'); the joined word is stored in the neighbouring clause (verified). No word lost.")
rule('who\\-trs957\\-a2\\-api\\.pdf', 'page\\ 22', '\\+next\\ to\\ Annex\\ 2\\ Appendix\\ 2\\ 7\\.24:\\ ed\\ identifi',
     "A word set with an fi/fl ligature at a clause edge, read by pdfminer as two pieces ('specifi cations'); the joined word is stored in the neighbouring clause (verified). No word lost.")
rule('who\\-trs957\\-a2\\-api\\.pdf', 'page\\ 23', '\\+next\\ to\\ Annex\\ 2\\ Appendix\\ 2\\ 7\\.42:\\ fi\\ rst',
     "The word 'first' set with an 'fi' ligature, read by pdfminer as two pieces; stored joined at the end of clause 7.42.")
rule('who\\-trs957\\-a2\\-api\\.pdf', 'page\\ 23', '\\+next\\ to\\ Annex\\ 2\\ Appendix\\ 2\\ 7\\.43:\\ rst\\ fi',
     "The word 'first' set with an 'fi' ligature, read by pdfminer as two pieces; stored joined at the end of clause 7.42.")
rule('who\\-trs957\\-a2\\-api\\.pdf', 'page\\ 27', '\\+next\\ to\\ Annex\\ 2\\ Appendix\\ 2\\ 8\\.52:\\ purifi\\ cation',
     "A word set with an fi/fl ligature at a clause edge, read by pdfminer as two pieces ('specifi cations'); the joined word is stored in the neighbouring clause (verified). No word lost.")
rule('who\\-trs957\\-a2\\-api\\.pdf', 'page\\ 27', '\\+next\\ to\\ Annex\\ 2\\ Appendix\\ 2\\ 9:\\ cation\\ purifi',
     "A word set with an fi/fl ligature at a clause edge, read by pdfminer as two pieces ('specifi cations'); the joined word is stored in the neighbouring clause (verified). No word lost.")
rule('who\\-trs957\\-a2\\-api\\.pdf', 'page\\ 28', '\\+next\\ to\\ Annex\\ 2\\ Appendix\\ 2\\ 9\\.32:\\ identifi\\ cation',
     "A word set with an fi/fl ligature at a clause edge, read by pdfminer as two pieces ('specifi cations'); the joined word is stored in the neighbouring clause (verified). No word lost.")
rule('who\\-trs957\\-a2\\-api\\.pdf', 'page\\ 28', '\\+next\\ to\\ Annex\\ 2\\ Appendix\\ 2\\ 9\\.33:\\ cation\\ identifi',
     "A word set with an fi/fl ligature at a clause edge, read by pdfminer as two pieces ('specifi cations'); the joined word is stored in the neighbouring clause (verified). No word lost.")
rule('who\\-trs957\\-a2\\-api\\.pdf', 'page\\ 31', '\\+next\\ to\\ Annex\\ 2\\ Appendix\\ 2\\ 11\\.20:\\ specifi\\ cations',
     "A word set with an fi/fl ligature at a clause edge, read by pdfminer as two pieces ('specifi cations'); the joined word is stored in the neighbouring clause (verified). No word lost.")
rule('who\\-trs957\\-a2\\-api\\.pdf', 'page\\ 31', '\\+next\\ to\\ Annex\\ 2\\ Appendix\\ 2\\ 11\\.21:\\ cations\\ specifi',
     "A word set with an fi/fl ligature at a clause edge, read by pdfminer as two pieces ('specifi cations'); the joined word is stored in the neighbouring clause (verified). No word lost.")
rule('who\\-trs957\\-a2\\-api\\.pdf', 'page\\ 31', '\\+next\\ to\\ Annex\\ 2\\ Appendix\\ 2\\ 11\\.23:\\ specifi\\ ed',
     "A word set with an fi/fl ligature at a clause edge, read by pdfminer as two pieces ('specifi cations'); the joined word is stored in the neighbouring clause (verified). No word lost.")
rule('who\\-trs957\\-a2\\-api\\.pdf', 'page\\ 35', '\\+next\\ to\\ Annex\\ 2\\ Appendix\\ 2\\ 12\\.22:\\ defi\\ ciencies',
     "A word set with an fi/fl ligature at a clause edge, read by pdfminer as two pieces ('specifi cations'); the joined word is stored in the neighbouring clause (verified). No word lost.")
rule('who\\-trs957\\-a2\\-api\\.pdf', 'page\\ 35', '\\+next\\ to\\ Annex\\ 2\\ Appendix\\ 2\\ 12\\.23:\\ ciencies\\ defi',
     "A word set with an fi/fl ligature at a clause edge, read by pdfminer as two pieces ('specifi cations'); the joined word is stored in the neighbouring clause (verified). No word lost.")
rule('who\\-trs957\\-a2\\-api\\.pdf', 'page\\ 35', '\\+next\\ to\\ Annex\\ 2\\ Appendix\\ 2\\ 12\\.23:\\ justifi\\ cation',
     "A word set with an fi/fl ligature at a clause edge, read by pdfminer as two pieces ('specifi cations'); the joined word is stored in the neighbouring clause (verified). No word lost.")
rule('who\\-trs957\\-a2\\-api\\.pdf', 'page\\ 35', '\\+next\\ to\\ Annex\\ 2\\ Appendix\\ 2\\ 12\\.3:\\ cation\\ justifi',
     "A word set with an fi/fl ligature at a clause edge, read by pdfminer as two pieces ('specifi cations'); the joined word is stored in the neighbouring clause (verified). No word lost.")
rule('who\\-trs957\\-a2\\-api\\.pdf', 'page\\ 35', '\\+next\\ to\\ Annex\\ 2\\ Appendix\\ 2\\ 12\\.3:\\ qualifi\\ cation',
     "A word set with an fi/fl ligature at a clause edge, read by pdfminer as two pieces ('specifi cations'); the joined word is stored in the neighbouring clause (verified). No word lost.")
rule('who\\-trs957\\-a2\\-api\\.pdf', 'page\\ 35', '\\+next\\ to\\ Annex\\ 2\\ Appendix\\ 2\\ 12\\.30:\\ cation\\ qualifi',
     "A word set with an fi/fl ligature at a clause edge, read by pdfminer as two pieces ('specifi cations'); the joined word is stored in the neighbouring clause (verified). No word lost.")
rule('who\\-trs957\\-a2\\-api\\.pdf', 'page\\ 35', '\\+next\\ to\\ Annex\\ 2\\ Appendix\\ 2\\ 12\\.30:\\ specifi\\ cations',
     "A word set with an fi/fl ligature at a clause edge, read by pdfminer as two pieces ('specifi cations'); the joined word is stored in the neighbouring clause (verified). No word lost.")
rule('who\\-trs957\\-a2\\-api\\.pdf', 'page\\ 35', '\\+next\\ to\\ Annex\\ 2\\ Appendix\\ 2\\ 12\\.4:\\ cations\\ specifi',
     "A word set with an fi/fl ligature at a clause edge, read by pdfminer as two pieces ('specifi cations'); the joined word is stored in the neighbouring clause (verified). No word lost.")
rule('who\\-trs957\\-a2\\-api\\.pdf', 'page\\ 36', '\\+next\\ to\\ Annex\\ 2\\ Appendix\\ 2\\ 12\\.50:\\ justifi\\ ed',
     "A word set with an fi/fl ligature at a clause edge, read by pdfminer as two pieces ('specifi cations'); the joined word is stored in the neighbouring clause (verified). No word lost.")
rule('who\\-trs957\\-a2\\-api\\.pdf', 'page\\ 36', '\\+next\\ to\\ Annex\\ 2\\ Appendix\\ 2\\ 12\\.51:\\ ed\\ justifi',
     "A word set with an fi/fl ligature at a clause edge, read by pdfminer as two pieces ('specifi cations'); the joined word is stored in the neighbouring clause (verified). No word lost.")
rule('who\\-trs957\\-a2\\-api\\.pdf', 'page\\ 37', '\\+next\\ to\\ Annex\\ 2\\ Appendix\\ 2\\ 12\\.73:\\ microfl\\ uidizers',
     "A word set with an fi/fl ligature at a clause edge, read by pdfminer as two pieces ('specifi cations'); the joined word is stored in the neighbouring clause (verified). No word lost.")
rule('who\\-trs957\\-a2\\-api\\.pdf', 'page\\ 37', '\\+next\\ to\\ Annex\\ 2\\ Appendix\\ 2\\ 12\\.74:\\ uidizers\\ microfl',
     "A word set with an fi/fl ligature at a clause edge, read by pdfminer as two pieces ('specifi cations'); the joined word is stored in the neighbouring clause (verified). No word lost.")
rule('who\\-trs957\\-a2\\-api\\.pdf', 'page\\ 48', '\\+next\\ to\\ Annex\\ 2\\ Appendix\\ 2\\ 18\\.4:\\ purifi\\ cation',
     "A word set with an fi/fl ligature at a clause edge, read by pdfminer as two pieces ('specifi cations'); the joined word is stored in the neighbouring clause (verified). No word lost.")
rule('who\\-trs957\\-a2\\-api\\.pdf', 'page\\ 48', '\\+next\\ to\\ Annex\\ 2\\ Appendix\\ 2\\ 18\\.40:\\ cation\\ purifi',
     "A word set with an fi/fl ligature at a clause edge, read by pdfminer as two pieces ('specifi cations'); the joined word is stored in the neighbouring clause (verified). No word lost.")
rule('who\\-trs957\\-a2\\-api\\.pdf', 'page\\ 50', '\\+next\\ to\\ Annex\\ 2\\ Appendix\\ 2\\ 19\\.40:\\ suffi\\ ce',
     "A word set with an fi/fl ligature at a clause edge, read by pdfminer as two pieces ('specifi cations'); the joined word is stored in the neighbouring clause (verified). No word lost.")
rule('who\\-trs957\\-a2\\-api\\.pdf', 'page\\ 50', '\\+next\\ to\\ Annex\\ 2\\ Appendix\\ 2\\ 19\\.41:\\ ce\\ suffi',
     "A word set with an fi/fl ligature at a clause edge, read by pdfminer as two pieces ('specifi cations'); the joined word is stored in the neighbouring clause (verified). No word lost.")
rule('who\\-trs957\\-a3\\-hazardous\\.pdf', 'page\\ 2', '\\+next\\ to\\ Annex\\ 3\\ 1\\.1:\\ introduction\\ 1',
     "A section heading printed on its own line (verified in poppler's text) that the parser keeps as structure, not as clause text; heading words, not requirement text.")
rule('who\\-trs957\\-a3\\-hazardous\\.pdf', 'page\\ 2', '\\+next\\ to\\ Annex\\ 3\\ 1\\.4:\\ 2\\ general',
     "A section heading printed on its own line (verified in poppler's text) that the parser keeps as structure, not as clause text; heading words, not requirement text.")
rule('who\\-trs957\\-a3\\-hazardous\\.pdf', 'page\\ 2', '\\+next\\ to\\ Annex\\ 3\\ 2\\.1:\\ general\\ 2',
     "A section heading printed on its own line (verified in poppler's text) that the parser keeps as structure, not as clause text; heading words, not requirement text.")
rule('who\\-trs957\\-a3\\-hazardous\\.pdf', 'page\\ 12', '\\+next\\ to\\ Annex\\ 3\\ 9\\.5:\\ airfl\\ ow',
     "A word set with an fi/fl ligature at a clause edge, read by pdfminer as two pieces ('specifi cations'); the joined word is stored in the neighbouring clause (verified). No word lost.")
rule('who\\-trs957\\-a3\\-hazardous\\.pdf', 'page\\ 12', '\\+next\\ to\\ Annex\\ 3\\ 9\\.6:\\ ow\\ airfl',
     "A word set with an fi/fl ligature at a clause edge, read by pdfminer as two pieces ('specifi cations'); the joined word is stored in the neighbouring clause (verified). No word lost.")
rule('who\\-trs961\\-a14\\-site\\-master\\-file\\.pdf', 'page\\ 2', '\\+next\\ to\\ Annex\\ 14\\ 1\\.1:\\ introduction\\ 1',
     "A section heading printed on its own line (verified in poppler's text) that the parser keeps as structure, not as clause text; heading words, not requirement text.")
rule('who\\-trs961\\-a2\\-micro\\-labs\\.pdf', 'page\\ 1', '\\+next\\ to\\ Annex\\ 2\\ 4\\.2:\\ qualifi\\ cation',
     "A word set with an fi/fl ligature at a clause edge, read by pdfminer as two pieces ('specifi cations'); the joined word is stored in the neighbouring clause (verified). No word lost.")
rule('who\\-trs961\\-a2\\-micro\\-labs\\.pdf', 'page\\ 1', '\\+next\\ to\\ Annex\\ 2\\ 4\\.3:\\ cation\\ qualifi',
     "A word set with an fi/fl ligature at a clause edge, read by pdfminer as two pieces ('specifi cations'); the joined word is stored in the neighbouring clause (verified). No word lost.")
rule('who\\-trs961\\-a2\\-micro\\-labs\\.pdf', 'page\\ 2', '\\+next\\ to\\ Annex\\ 2\\ 8:\\ identifi\\ cation',
     "A word set with an fi/fl ligature at a clause edge, read by pdfminer as two pieces ('specifi cations'); the joined word is stored in the neighbouring clause (verified). No word lost.")
rule('who\\-trs961\\-a2\\-micro\\-labs\\.pdf', 'page\\ 2', '\\+next\\ to\\ Annex\\ 2\\ 9:\\ cation\\ identifi',
     "A word set with an fi/fl ligature at a clause edge, read by pdfminer as two pieces ('specifi cations'); the joined word is stored in the neighbouring clause (verified). No word lost.")
rule('who\\-trs961\\-a2\\-micro\\-labs\\.pdf', 'page\\ 7', '\\+next\\ to\\ Annex\\ 2\\ Appendix\\ 4\\ 2\\.1\\.7:\\ classifi\\ cations',
     "A word set with an fi/fl ligature at a clause edge, read by pdfminer as two pieces ('specifi cations'); the joined word is stored in the neighbouring clause (verified). No word lost.")
rule('who\\-trs961\\-a2\\-micro\\-labs\\.pdf', 'page\\ 7', '\\+next\\ to\\ Annex\\ 2\\ Appendix\\ 4\\ 2\\.1\\.8:\\ cations\\ classifi',
     "A word set with an fi/fl ligature at a clause edge, read by pdfminer as two pieces ('specifi cations'); the joined word is stored in the neighbouring clause (verified). No word lost.")
rule('who\\-trs961\\-a2\\-micro\\-labs\\.pdf', 'page\\ 8', '\\+next\\ to\\ Annex\\ 2\\ Appendix\\ 4\\ 2\\.4\\.5:\\ fi\\ lters',
     "A word set with an fi/fl ligature at a clause edge, read by pdfminer as two pieces ('specifi cations'); the joined word is stored in the neighbouring clause (verified). No word lost.")
rule('who\\-trs961\\-a2\\-micro\\-labs\\.pdf', 'page\\ 8', '\\+next\\ to\\ Annex\\ 2\\ Appendix\\ 4\\ 2\\.4\\.6:\\ lters\\ fi',
     "A word set with an fi/fl ligature at a clause edge, read by pdfminer as two pieces ('specifi cations'); the joined word is stored in the neighbouring clause (verified). No word lost.")
rule('who\\-trs961\\-a2\\-micro\\-labs\\.pdf', 'page\\ 8', '\\+next\\ to\\ Annex\\ 2\\ Appendix\\ 4\\ 2\\.4\\.7:\\ specifi\\ cation',
     "A word set with an fi/fl ligature at a clause edge, read by pdfminer as two pieces ('specifi cations'); the joined word is stored in the neighbouring clause (verified). No word lost.")
rule('who\\-trs961\\-a2\\-micro\\-labs\\.pdf', 'page\\ 8', '\\+next\\ to\\ Annex\\ 2\\ Appendix\\ 4\\ 2\\.4\\.8:\\ cation\\ specifi',
     "A word set with an fi/fl ligature at a clause edge, read by pdfminer as two pieces ('specifi cations'); the joined word is stored in the neighbouring clause (verified). No word lost.")
rule('who\\-trs961\\-a2\\-micro\\-labs\\.pdf', 'page\\ 10', '\\+next\\ to\\ Annex\\ 2\\ Appendix\\ 4\\ 4\\.2:\\ qualifi\\ cation',
     "A word set with an fi/fl ligature at a clause edge, read by pdfminer as two pieces ('specifi cations'); the joined word is stored in the neighbouring clause (verified). No word lost.")
rule('who\\-trs961\\-a2\\-micro\\-labs\\.pdf', 'page\\ 10', '\\+next\\ to\\ Annex\\ 2\\ Appendix\\ 4\\ 4\\.2\\.1:\\ cation\\ qualifi',
     "A word set with an fi/fl ligature at a clause edge, read by pdfminer as two pieces ('specifi cations'); the joined word is stored in the neighbouring clause (verified). No word lost.")
rule('who\\-trs961\\-a2\\-micro\\-labs\\.pdf', 'page\\ 11', '\\+next\\ to\\ Annex\\ 2\\ Appendix\\ 4\\ 4\\.3\\.5\\.1:\\ verifi\\ ed',
     "A word set with an fi/fl ligature at a clause edge, read by pdfminer as two pieces ('specifi cations'); the joined word is stored in the neighbouring clause (verified). No word lost.")
rule('who\\-trs961\\-a2\\-micro\\-labs\\.pdf', 'page\\ 11', '\\+next\\ to\\ Annex\\ 2\\ Appendix\\ 4\\ 4\\.3\\.5\\.2:\\ ed\\ verifi',
     "A word set with an fi/fl ligature at a clause edge, read by pdfminer as two pieces ('specifi cations'); the joined word is stored in the neighbouring clause (verified). No word lost.")
rule('who\\-trs961\\-a2\\-micro\\-labs\\.pdf', 'page\\ 14', '\\+next\\ to\\ Annex\\ 2\\ Appendix\\ 4\\ 5\\.2\\.8:\\ verifi\\ ed',
     "A word set with an fi/fl ligature at a clause edge, read by pdfminer as two pieces ('specifi cations'); the joined word is stored in the neighbouring clause (verified). No word lost.")
rule('who\\-trs961\\-a2\\-micro\\-labs\\.pdf', 'page\\ 14', '\\+next\\ to\\ Annex\\ 2\\ Appendix\\ 4\\ 5\\.2\\.9:\\ ed\\ verifi',
     "A word set with an fi/fl ligature at a clause edge, read by pdfminer as two pieces ('specifi cations'); the joined word is stored in the neighbouring clause (verified). No word lost.")
rule('who\\-trs961\\-a2\\-micro\\-labs\\.pdf', 'page\\ 14', '\\+next\\ to\\ Annex\\ 2\\ Appendix\\ 4\\ 5\\.2\\.9:\\ specifi\\ cation',
     "A word set with an fi/fl ligature at a clause edge, read by pdfminer as two pieces ('specifi cations'); the joined word is stored in the neighbouring clause (verified). No word lost.")
rule('who\\-trs961\\-a2\\-micro\\-labs\\.pdf', 'page\\ 14', '\\+next\\ to\\ Annex\\ 2\\ Appendix\\ 4\\ 5\\.2\\.10:\\ cation\\ specifi',
     "A word set with an fi/fl ligature at a clause edge, read by pdfminer as two pieces ('specifi cations'); the joined word is stored in the neighbouring clause (verified). No word lost.")
rule('who\\-trs961\\-a2\\-micro\\-labs\\.pdf', 'page\\ 16', '\\+next\\ to\\ Annex\\ 2\\ Appendix\\ 4\\ 8:\\ identifi\\ cation',
     "A word set with an fi/fl ligature at a clause edge, read by pdfminer as two pieces ('specifi cations'); the joined word is stored in the neighbouring clause (verified). No word lost.")
rule('who\\-trs961\\-a2\\-micro\\-labs\\.pdf', 'page\\ 16', '\\+next\\ to\\ Annex\\ 2\\ Appendix\\ 4\\ 8\\.1:\\ cation\\ identifi',
     "A word set with an fi/fl ligature at a clause edge, read by pdfminer as two pieces ('specifi cations'); the joined word is stored in the neighbouring clause (verified). No word lost.")
rule('who\\-trs961\\-a9\\-storage\\-transport\\-ttsp\\.pdf', 'page\\ 29', '\\+next\\ to\\ Annex\\ 9\\ 6\\.7\\.1:\\ justifi\\ ed',
     "A word set with an fi/fl ligature at a clause edge, read by pdfminer as two pieces ('specifi cations'); the joined word is stored in the neighbouring clause (verified). No word lost.")
rule('who\\-trs961\\-a9\\-storage\\-transport\\-ttsp\\.pdf', 'page\\ 29', '\\+next\\ to\\ Annex\\ 9\\ 6\\.7\\.2:\\ ed\\ justifi',
     "A word set with an fi/fl ligature at a clause edge, read by pdfminer as two pieces ('specifi cations'); the joined word is stored in the neighbouring clause (verified). No word lost.")
rule('who\\-trs961\\-a9\\-storage\\-transport\\-ttsp\\.pdf', 'page\\ 29', '\\+next\\ to\\ Annex\\ 9\\ 6\\.7\\.2:\\ justifi\\ ed',
     "A word set with an fi/fl ligature at a clause edge, read by pdfminer as two pieces ('specifi cations'); the joined word is stored in the neighbouring clause (verified). No word lost.")
rule('who\\-trs961\\-a9\\-storage\\-transport\\-ttsp\\.pdf', 'page\\ 29', '\\+next\\ to\\ Annex\\ 9\\ 6\\.7\\.3:\\ ed\\ justifi',
     "A word set with an fi/fl ligature at a clause edge, read by pdfminer as two pieces ('specifi cations'); the joined word is stored in the neighbouring clause (verified). No word lost.")
rule('who\\-trs961\\-a9\\-storage\\-transport\\-ttsp\\.pdf', 'page\\ 29', '\\+next\\ to\\ Annex\\ 9\\ 6\\.7\\.3:\\ justifi\\ ed',
     "A word set with an fi/fl ligature at a clause edge, read by pdfminer as two pieces ('specifi cations'); the joined word is stored in the neighbouring clause (verified). No word lost.")
rule('who\\-trs961\\-a9\\-storage\\-transport\\-ttsp\\.pdf', 'page\\ 29', '\\+next\\ to\\ Annex\\ 9\\ 6\\.7\\.4:\\ ed\\ justifi',
     "A word set with an fi/fl ligature at a clause edge, read by pdfminer as two pieces ('specifi cations'); the joined word is stored in the neighbouring clause (verified). No word lost.")
rule('who\\-trs961\\-a9\\-storage\\-transport\\-ttsp\\.pdf', 'page\\ 49', '\\+next\\ to\\ _unnumbered:2:\\ who\\ switzerland',
     "Cells of the acknowledgements table (organisation 'WHO', country 'Switzerland') of the front matter; not regulation text.")
rule('who\\-trs981\\-a2\\-qrm\\.pdf', 'page\\ 2', '\\+next\\ to\\ 1\\.1:\\ introduction\\ 1',
     "A section heading printed on its own line (verified in poppler's text) that the parser keeps as structure, not as clause text; heading words, not requirement text.")
rule('who\\-trs992\\-a5\\-ttsp\\-supplements\\.pdf', 'page\\ 10', '\\+next\\ to\\ _unnumbered:7:\\ acknowledgements\\ abbreviations',
     'Entries of a reproduced supplement contents page; contents listing, not requirements.')
rule('who\\-trs992\\-a5\\-ttsp\\-supplements\\.pdf', 'page\\ 10', '\\+next\\ to\\ Annex\\ 2\\ Glossary\\ \\#2:\\ abbreviations\\ acknowledgements',
     'Entries of a reproduced supplement contents page; contents listing, not requirements.')
rule('who\\-trs992\\-a5\\-ttsp\\-supplements\\.pdf', 'page\\ 10', '\\+next\\ to\\ Annex\\ 2\\ 2\\.7\\.4:\\ references',
     "A section heading printed on its own line (verified in poppler's text) that the parser keeps as structure, not as clause text; heading words, not requirement text.")
rule('who\\-trs992\\-a5\\-ttsp\\-supplements\\.pdf', 'page\\ 17', '\\+next\\ to\\ Annex\\ 1\\ 2\\.5\\ \\#2:\\ references',
     "A section heading printed on its own line (verified in poppler's text) that the parser keeps as structure, not as clause text; heading words, not requirement text.")
rule('who\\-trs992\\-a5\\-ttsp\\-supplements\\.pdf', 'page\\ 23', '\\+next\\ to\\ Annex\\ 1\\ 2\\.9:\\ references',
     "A section heading printed on its own line (verified in poppler's text) that the parser keeps as structure, not as clause text; heading words, not requirement text.")
rule('who\\-trs992\\-a5\\-ttsp\\-supplements\\.pdf', 'page\\ 25', '\\+next\\ to\\ _unnumbered:28:\\ 14\\ supplement',
     "A section heading printed on its own line (verified in poppler's text) that the parser keeps as structure, not as clause text; heading words, not requirement text.")
rule('who\\-trs992\\-a5\\-ttsp\\-supplements\\.pdf', 'page\\ 27', '\\+next\\ to\\ _unnumbered:32:\\ 16\\ supplement',
     "A section heading printed on its own line (verified in poppler's text) that the parser keeps as structure, not as clause text; heading words, not requirement text.")
rule('who\\-trs996\\-a4\\-app1\\-model\\-inspection\\-report\\.pdf', 'page\\ 2', '\\+next\\ to\\ Appendix\\ 2\\ 1\\.1:\\ introduction\\ 1',
     "A section heading printed on its own line (verified in poppler's text) that the parser keeps as structure, not as clause text; heading words, not requirement text.")
rule('who\\-trs996\\-a4\\-app1\\-model\\-inspection\\-report\\.pdf', 'page\\ 2', '\\+next\\ to\\ Appendix\\ 2\\ 1\\.1:\\ 2\\ scope',
     "A section heading printed on its own line (verified in poppler's text) that the parser keeps as structure, not as clause text; heading words, not requirement text.")
rule('who\\-trs996\\-a4\\-app1\\-model\\-inspection\\-report\\.pdf', 'page\\ 2', '\\+next\\ to\\ Appendix\\ 2\\ 2\\.1:\\ scope\\ 2',
     "A section heading printed on its own line (verified in poppler's text) that the parser keeps as structure, not as clause text; heading words, not requirement text.")
rule('who\\-trs996\\-a4\\-app1\\-model\\-inspection\\-report\\.pdf', 'page\\ 10', '\\+next\\ to\\ Appendix\\ 1\\ 2\\ \\#2:\\ applicable\\ where',
     "A section heading printed on its own line (verified in poppler's text) that the parser keeps as structure, not as clause text; heading words, not requirement text.")
rule('ema\\-water\\-quality\\-guideline\\.pdf', 'page\\ 7', '\\+in\\ table\\ row:\\ during\\ manufacture\\ of\\ active\\ substances\\ and\\ medicinal\\ products\\ excluding',
     "Words printed inside this table row's area that the row lacks; they are stored word for word in 5.2 on the same page (verified): a cell continued from a neighbouring row, a header cell or note text read into the row's band. No value lost.")
rule('ema\\-water\\-quality\\-guideline\\.pdf', 'page\\ 7', '\\+in\\ table\\ row:\\ present\\ as\\ an\\ excipient',
     "Words printed inside this table row's area that the row lacks; they are stored word for word in 5.1 on the same page (verified): a cell continued from a neighbouring row, a header cell or note text read into the row's band. No value lost.")
rule('ema\\-water\\-quality\\-guideline\\.pdf', 'page\\ 7', '\\+in\\ table\\ row:\\ the\\ final',
     "Words printed inside this table row's area that the row lacks; they are stored word for word in 5.1 on the same page (verified): a cell continued from a neighbouring row, a header cell or note text read into the row's band. No value lost.")
rule('ema\\-water\\-quality\\-guideline\\.pdf', 'page\\ 7', '\\+in\\ table\\ row:\\ the\\ grade\\ of',
     "Words printed inside this table row's area that the row lacks; they are stored word for word in 5.2 on the same page (verified): a cell continued from a neighbouring row, a header cell or note text read into the row's band. No value lost.")
rule('ema\\-water\\-quality\\-guideline\\.pdf', 'page\\ 7', '\\+in\\ table\\ row:\\ will\\ depend\\ on\\ the\\ stage\\ at\\ which\\ it\\ is',
     "Words printed inside this table row's area that the row lacks; they are stored word for word in 5.2 on the same page (verified): a cell continued from a neighbouring row, a header cell or note text read into the row's band. No value lost.")
rule('ema\\-water\\-quality\\-guideline\\.pdf', 'page\\ 7', '\\+in\\ table\\ row:\\ during\\ manufacture\\ the\\ subsequent\\ processing\\ steps\\ and\\ the\\ nature\\ of\\ the\\ final\\ product\\ according',
     "Words printed inside this table row's area that the row lacks; they are stored word for word in 5.2 on the same page (verified): a cell continued from a neighbouring row, a header cell or note text read into the row's band. No value lost.")
rule('ema\\-water\\-quality\\-guideline\\.pdf', 'page\\ 7', '\\+in\\ table\\ row:\\ final\\ isolation\\ and\\ purification',
     "Words printed inside this table row's area that the row lacks; they are stored word for word in Table 5 No requirement for sterility or… on the same page (verified): a cell continued from a neighbouring row, a header cell or note text read into the row's band. No value lost.")
rule('fda\\-cp\\-7346\\-832\\-preapproval\\-inspections\\.pdf', 'page\\ 47', '\\+in\\ table\\ row:\\ evaluates',
     "Words printed inside this table row's area that the row lacks; they are stored word for word in Attachment B on the same page (verified): a cell continued from a neighbouring row, a header cell or note text read into the row's band. No value lost.")
rule('fda\\-cp\\-7346\\-832\\-preapproval\\-inspections\\.pdf', 'page\\ 47', '\\+in\\ table\\ row:\\ conformance\\ with',
     "Words printed inside this table row's area that the row lacks; they are stored word for word in Attachment B on the same page (verified): a cell continued from a neighbouring row, a header cell or note text read into the row's band. No value lost.")
rule('fda\\-cp\\-7346\\-832\\-preapproval\\-inspections\\.pdf', 'page\\ 47', '\\+in\\ table\\ row:\\ on\\ site\\ mitigation\\ strategy',
     "Words printed inside this table row's area that the row lacks; they are stored word for word in Table 4 API * manufacturing and control (e.g.… on the same page (verified): a cell continued from a neighbouring row, a header cell or note text read into the row's band. No value lost.")
rule('fda\\-cp\\-7346\\-832\\-preapproval\\-inspections\\.pdf', 'page\\ 47', '\\+in\\ table\\ row:\\ controls\\ for\\ the',
     "Words printed inside this table row's area that the row lacks; they are stored word for word in Table 4 API * manufacturing and control (e.g.… on the same page (verified): a cell continued from a neighbouring row, a header cell or note text read into the row's band. No value lost.")
rule('fda\\-cp\\-7346\\-832\\-preapproval\\-inspections\\.pdf', 'page\\ 47', '\\+in\\ table\\ row:\\ and',
     "Words printed inside this table row's area that the row lacks; they are stored word for word in Attachment B on the same page (verified): a cell continued from a neighbouring row, a header cell or note text read into the row's band. No value lost.")
rule('fda\\-cp\\-7346\\-832\\-preapproval\\-inspections\\.pdf', 'page\\ 47', '\\+in\\ table\\ row:\\ and\\ their\\ impact\\ on\\ application\\ approval\\ cder\\ on\\ behalf\\ of\\ the\\ iqa\\ team\\ may\\ communicate\\ with\\ the',
     "Words printed inside this table row's area that the row lacks; they are stored word for word in Attachment B on the same page (verified): a cell continued from a neighbouring row, a header cell or note text read into the row's band. No value lost.")
rule('fda\\-cp\\-7346\\-832\\-preapproval\\-inspections\\.pdf', 'page\\ 47', '\\+in\\ table\\ row:\\ identified\\ by\\ the',
     "Words printed inside this table row's area that the row lacks; they are stored word for word in Attachment B on the same page (verified): a cell continued from a neighbouring row, a header cell or note text read into the row's band. No value lost.")
rule('fda\\-cp\\-7346\\-832\\-preapproval\\-inspections\\.pdf', 'page\\ 47', '\\+in\\ table\\ row:\\ inspection',
     "Words printed inside this table row's area that the row lacks; they are stored word for word in Attachment B on the same page (verified): a cell continued from a neighbouring row, a header cell or note text read into the row's band. No value lost.")
rule('fda\\-cp\\-7346\\-832\\-preapproval\\-inspections\\.pdf', 'page\\ 47', '\\+in\\ table\\ row:\\ lead\\ or\\ pam\\ provides\\ the',
     "Words printed inside this table row's area that the row lacks; they are stored word for word in Table 4 API * manufacturing and control (e.g.… on the same page (verified): a cell continued from a neighbouring row, a header cell or note text read into the row's band. No value lost.")
rule('fda\\-cp\\-7346\\-832\\-preapproval\\-inspections\\.pdf', 'page\\ 47', '\\+in\\ table\\ row:\\ team\\ with\\ its\\ initial',
     "Words printed inside this table row's area that the row lacks; they are stored word for word in Table 4 API * manufacturing and control (e.g.… on the same page (verified): a cell continued from a neighbouring row, a header cell or note text read into the row's band. No value lost.")
rule('fda\\-cp\\-7346\\-832\\-preapproval\\-inspections\\.pdf', 'page\\ 47', '\\+in\\ table\\ row:\\ recommendation\\ the\\ iqa\\ team\\ assesses\\ the\\ inspection\\ findings',
     "Words printed inside this table row's area that the row lacks; they are stored word for word in Table 4 API * manufacturing and control (e.g.… on the same page (verified): a cell continued from a neighbouring row, a header cell or note text read into the row's band. No value lost.")
rule('fda\\-cp\\-7346\\-832\\-preapproval\\-inspections\\.pdf', 'page\\ 47', '\\+in\\ table\\ row:\\ dmf\\ holder\\ or\\ inspected\\ facility',
     "Words printed inside this table row's area that the row lacks; they are stored word for word in Attachment B on the same page (verified): a cell continued from a neighbouring row, a header cell or note text read into the row's band. No value lost.")
rule('fda\\-cp\\-7346\\-832\\-preapproval\\-inspections\\.pdf', 'page\\ 47', '\\+in\\ table\\ row:\\ the\\ facility',
     "Words printed inside this table row's area that the row lacks; they are stored word for word in Attachment B on the same page (verified): a cell continued from a neighbouring row, a header cell or note text read into the row's band. No value lost.")
rule('fda\\-cp\\-7346\\-832\\-preapproval\\-inspections\\.pdf', 'page\\ 47', '\\+in\\ table\\ row:\\ the\\ applicant\\ as\\ appropriate',
     "Words printed inside this table row's area that the row lacks; they are stored word for word in Attachment B on the same page (verified): a cell continued from a neighbouring row, a header cell or note text read into the row's band. No value lost.")
rule('fda\\-cp\\-7346\\-832\\-preapproval\\-inspections\\.pdf', 'page\\ 47', '\\+in\\ table\\ row:\\ the\\ iqa\\ team',
     "Words printed inside this table row's area that the row lacks; they are stored word for word in Attachment B on the same page (verified): a cell continued from a neighbouring row, a header cell or note text read into the row's band. No value lost.")
rule('fda\\-cp\\-7346\\-832\\-preapproval\\-inspections\\.pdf', 'page\\ 47', '\\+in\\ table\\ row:\\ facility\\ and',
     "Words printed inside this table row's area that the row lacks; they are stored word for word in Table 4 API * manufacturing and control (e.g.… on the same page (verified): a cell continued from a neighbouring row, a header cell or note text read into the row's band. No value lost.")
rule('fda\\-cp\\-7346\\-832\\-preapproval\\-inspections\\.pdf', 'page\\ 47', '\\+in\\ table\\ row:\\ the',
     "Words printed inside this table row's area that the row lacks; they are stored word for word in Attachment B on the same page (verified): a cell continued from a neighbouring row, a header cell or note text read into the row's band. No value lost.")
rule('fda\\-cp\\-7346\\-832\\-preapproval\\-inspections\\.pdf', 'page\\ 47', '\\+in\\ table\\ row:\\ risks\\ and\\ concerns\\ to\\ the\\ inspection\\ team',
     "Words printed inside this table row's area that the row lacks; they are stored word for word in Table 4 API * manufacturing and control (e.g.… on the same page (verified): a cell continued from a neighbouring row, a header cell or note text read into the row's band. No value lost.")
rule('fda\\-cp\\-7346\\-832\\-preapproval\\-inspections\\.pdf', 'page\\ 47', '\\+in\\ table\\ row:\\ cont\\ next\\ page',
     "Words printed inside this table row's area that the row lacks; they are stored word for word in Attachment B on the same page (verified): a cell continued from a neighbouring row, a header cell or note text read into the row's band. No value lost.")
rule('fda\\-cp\\-7346\\-832\\-preapproval\\-inspections\\.pdf', 'page\\ 48', '\\+in\\ table\\ row:\\ addressing\\ quality\\ related\\ topics\\ via',
     "Words printed inside this table row's area that the row lacks; they are stored word for word in Table 4 Addressing Quality-Related Topics via… on the same page (verified): a cell continued from a neighbouring row, a header cell or note text read into the row's band. No value lost.")
rule('fda\\-cp\\-7346\\-832\\-preapproval\\-inspections\\.pdf', 'page\\ 48', '\\+in\\ table\\ row:\\ iqa\\ team',
     "Words printed inside this table row's area that the row lacks; they are stored word for word in Attachment B on the same page (verified): a cell continued from a neighbouring row, a header cell or note text read into the row's band. No value lost.")
rule('fda\\-cp\\-7346\\-832\\-preapproval\\-inspections\\.pdf', 'page\\ 48', '\\+in\\ table\\ row:\\ adequacy',
     "Words printed inside this table row's area that the row lacks; they are stored word for word in Attachment B on the same page (verified): a cell continued from a neighbouring row, a header cell or note text read into the row's band. No value lost.")
rule('fda\\-cp\\-7346\\-832\\-preapproval\\-inspections\\.pdf', 'page\\ 48', '\\+in\\ table\\ row:\\ supplier\\ s\\ qualifications\\ ongoing\\ qc\\ testing',
     "Words printed inside this table row's area that the row lacks; they are stored word for word in Table 4 Novel excipient manufacturing (e.g.… on the same page (verified): a cell continued from a neighbouring row, a header cell or note text read into the row's band. No value lost.")
rule('fda\\-cp\\-7346\\-832\\-preapproval\\-inspections\\.pdf', 'page\\ 48', '\\+in\\ table\\ row:\\ storage\\ handling',
     "Words printed inside this table row's area that the row lacks; they are stored word for word in Table 4 Novel excipient manufacturing (e.g.… on the same page (verified): a cell continued from a neighbouring row, a header cell or note text read into the row's band. No value lost.")
rule('fda\\-cp\\-7346\\-832\\-preapproval\\-inspections\\.pdf', 'page\\ 48', '\\+in\\ table\\ row:\\ procedures',
     "Words printed inside this table row's area that the row lacks; they are stored word for word in Attachment B on the same page (verified): a cell continued from a neighbouring row, a header cell or note text read into the row's band. No value lost.")
rule('fda\\-cp\\-7346\\-832\\-preapproval\\-inspections\\.pdf', 'page\\ 48', '\\+in\\ table\\ row:\\ cont\\ next\\ page',
     "Words printed inside this table row's area that the row lacks; they are stored word for word in Attachment B on the same page (verified): a cell continued from a neighbouring row, a header cell or note text read into the row's band. No value lost.")
rule('fda\\-cp\\-7346\\-832\\-preapproval\\-inspections\\.pdf', 'page\\ 49', '\\+in\\ table\\ row:\\ cont\\ next\\ page',
     "Words printed inside this table row's area that the row lacks; they are stored word for word in Attachment B on the same page (verified): a cell continued from a neighbouring row, a header cell or note text read into the row's band. No value lost.")
rule('fda\\-cp\\-7346\\-832\\-preapproval\\-inspections\\.pdf', 'page\\ 50', '\\+in\\ table\\ row:\\ addressing',
     "A repeated table title or section label printed in the row's area ('addressing'); stored once, in Table 4 Addressing Quality-Related Topics via…. Not a value of this row.")
rule('fda\\-cp\\-7346\\-832\\-preapproval\\-inspections\\.pdf', 'page\\ 50', '\\+in\\ table\\ row:\\ cont\\ next\\ page',
     "Words printed inside this table row's area that the row lacks; they are stored word for word in Attachment B on the same page (verified): a cell continued from a neighbouring row, a header cell or note text read into the row's band. No value lost.")
rule('fda\\-cp\\-7346\\-832\\-preapproval\\-inspections\\.pdf', 'page\\ 51', '\\+in\\ table\\ row:\\ addressing',
     "A repeated table title or section label printed in the row's area ('addressing'); stored once, in Table 4 Addressing Quality-Related Topics via…. Not a value of this row.")
rule('fda\\-cp\\-7346\\-832\\-preapproval\\-inspections\\.pdf', 'page\\ 51', '\\+in\\ table\\ row:\\ evaluates',
     "Words printed inside this table row's area that the row lacks; they are stored word for word in Attachment B on the same page (verified): a cell continued from a neighbouring row, a header cell or note text read into the row's band. No value lost.")
rule('fda\\-cp\\-7346\\-832\\-preapproval\\-inspections\\.pdf', 'page\\ 51', '\\+in\\ table\\ row:\\ facility\\ for\\ conformance',
     "Words printed inside this table row's area that the row lacks; they are stored word for word in Table 4 Manufacturing and control of finished… #3 on the same page (verified): a cell continued from a neighbouring row, a header cell or note text read into the row's band. No value lost.")
rule('fda\\-cp\\-7346\\-832\\-preapproval\\-inspections\\.pdf', 'page\\ 51', '\\+in\\ table\\ row:\\ cgmp',
     "Words printed inside this table row's area that the row lacks; they are stored word for word in Attachment B on the same page (verified): a cell continued from a neighbouring row, a header cell or note text read into the row's band. No value lost.")
rule('fda\\-cp\\-7346\\-832\\-preapproval\\-inspections\\.pdf', 'page\\ 51', '\\+in\\ table\\ row:\\ objectives\\ of\\ this\\ compliance\\ program',
     "Words printed inside this table row's area that the row lacks; they are stored word for word in Attachment B on the same page (verified): a cell continued from a neighbouring row, a header cell or note text read into the row's band. No value lost.")
rule('fda\\-cp\\-7346\\-832\\-preapproval\\-inspections\\.pdf', 'page\\ 51', '\\+in\\ table\\ row:\\ risks',
     "Words printed inside this table row's area that the row lacks; they are stored word for word in Attachment B on the same page (verified): a cell continued from a neighbouring row, a header cell or note text read into the row's band. No value lost.")
rule('fda\\-cp\\-7346\\-832\\-preapproval\\-inspections\\.pdf', 'page\\ 51', '\\+in\\ table\\ row:\\ concerns\\ identified\\ by',
     "Words printed inside this table row's area that the row lacks; they are stored word for word in Attachment B on the same page (verified): a cell continued from a neighbouring row, a header cell or note text read into the row's band. No value lost.")
rule('fda\\-cp\\-7346\\-832\\-preapproval\\-inspections\\.pdf', 'page\\ 51', '\\+in\\ table\\ row:\\ inspection',
     "Words printed inside this table row's area that the row lacks; they are stored word for word in Attachment B on the same page (verified): a cell continued from a neighbouring row, a header cell or note text read into the row's band. No value lost.")
rule('fda\\-cp\\-7346\\-832\\-preapproval\\-inspections\\.pdf', 'page\\ 51', '\\+in\\ table\\ row:\\ inspection\\ team\\ lead\\ or\\ pam\\ provides\\ the',
     "Words printed inside this table row's area that the row lacks; they are stored word for word in Attachment B on the same page (verified): a cell continued from a neighbouring row, a header cell or note text read into the row's band. No value lost.")
rule('fda\\-cp\\-7346\\-832\\-preapproval\\-inspections\\.pdf', 'page\\ 51', '\\+in\\ table\\ row:\\ with\\ the',
     "Words printed inside this table row's area that the row lacks; they are stored word for word in Attachment B on the same page (verified): a cell continued from a neighbouring row, a header cell or note text read into the row's band. No value lost.")
rule('fda\\-cp\\-7346\\-832\\-preapproval\\-inspections\\.pdf', 'page\\ 51', '\\+in\\ table\\ row:\\ team\\ with\\ its\\ initial\\ facility\\ recommendation\\ the\\ iqa\\ team\\ assesses\\ the\\ inspection\\ findings\\ and\\ their',
     "Words printed inside this table row's area that the row lacks; they are stored word for word in Table 4 Manufacturing and control of finished… on the same page (verified): a cell continued from a neighbouring row, a header cell or note text read into the row's band. No value lost.")
rule('fda\\-cp\\-7346\\-832\\-preapproval\\-inspections\\.pdf', 'page\\ 51', '\\+in\\ table\\ row:\\ on\\ the',
     "Words printed inside this table row's area that the row lacks; they are stored word for word in Attachment B on the same page (verified): a cell continued from a neighbouring row, a header cell or note text read into the row's band. No value lost.")
rule('fda\\-cp\\-7346\\-832\\-preapproval\\-inspections\\.pdf', 'page\\ 51', '\\+in\\ table\\ row:\\ control\\ strategy',
     "Words printed inside this table row's area that the row lacks; they are stored word for word in Attachment B on the same page (verified): a cell continued from a neighbouring row, a header cell or note text read into the row's band. No value lost.")
rule('fda\\-cp\\-7346\\-832\\-preapproval\\-inspections\\.pdf', 'page\\ 51', '\\+in\\ table\\ row:\\ make\\ the\\ quality\\ recommendation\\ if\\ the\\ inspection\\ findings',
     "Words printed inside this table row's area that the row lacks; they are stored word for word in Table 4 Manufacturing and control of finished… #3 on the same page (verified): a cell continued from a neighbouring row, a header cell or note text read into the row's band. No value lost.")
rule('fda\\-cp\\-7346\\-832\\-preapproval\\-inspections\\.pdf', 'page\\ 51', '\\+in\\ table\\ row:\\ and',
     "Words printed inside this table row's area that the row lacks; they are stored word for word in Attachment B on the same page (verified): a cell continued from a neighbouring row, a header cell or note text read into the row's band. No value lost.")
rule('fda\\-cp\\-7346\\-832\\-preapproval\\-inspections\\.pdf', 'page\\ 51', '\\+in\\ table\\ row:\\ and\\ the',
     "Words printed inside this table row's area that the row lacks; they are stored word for word in Attachment B on the same page (verified): a cell continued from a neighbouring row, a header cell or note text read into the row's band. No value lost.")
rule('fda\\-cp\\-7346\\-832\\-preapproval\\-inspections\\.pdf', 'page\\ 51', '\\+in\\ table\\ row:\\ impact',
     "Words printed inside this table row's area that the row lacks; they are stored word for word in Attachment B on the same page (verified): a cell continued from a neighbouring row, a header cell or note text read into the row's band. No value lost.")
rule('fda\\-cp\\-7346\\-832\\-preapproval\\-inspections\\.pdf', 'page\\ 51', '\\+in\\ table\\ row:\\ quality\\ cder\\ on\\ behalf\\ of\\ the\\ iqa\\ team',
     "Words printed inside this table row's area that the row lacks; they are stored word for word in Table 4 Manufacturing and control of finished… #3 on the same page (verified): a cell continued from a neighbouring row, a header cell or note text read into the row's band. No value lost.")
rule('fda\\-cp\\-7346\\-832\\-preapproval\\-inspections\\.pdf', 'page\\ 51', '\\+in\\ table\\ row:\\ communicate\\ with\\ the',
     "Words printed inside this table row's area that the row lacks; they are stored word for word in Table 4 Manufacturing and control of finished… #3 on the same page (verified): a cell continued from a neighbouring row, a header cell or note text read into the row's band. No value lost.")
rule('fda\\-cp\\-7346\\-832\\-preapproval\\-inspections\\.pdf', 'page\\ 51', '\\+in\\ table\\ row:\\ or\\ inspected\\ facility\\ as\\ appropriate\\ the\\ iqa\\ team\\ may',
     "Words printed inside this table row's area that the row lacks; they are stored word for word in Table 4 Manufacturing and control of finished… #3 on the same page (verified): a cell continued from a neighbouring row, a header cell or note text read into the row's band. No value lost.")
rule('fda\\-cp\\-7346\\-832\\-preapproval\\-inspections\\.pdf', 'page\\ 51', '\\+in\\ table\\ row:\\ the\\ applicant',
     "Words printed inside this table row's area that the row lacks; they are stored word for word in Attachment B on the same page (verified): a cell continued from a neighbouring row, a header cell or note text read into the row's band. No value lost.")
rule('fda\\-cp\\-7346\\-832\\-preapproval\\-inspections\\.pdf', 'page\\ 51', '\\+in\\ table\\ row:\\ the',
     "Words printed inside this table row's area that the row lacks; they are stored word for word in Attachment B on the same page (verified): a cell continued from a neighbouring row, a header cell or note text read into the row's band. No value lost.")
rule('fda\\-cp\\-7346\\-832\\-preapproval\\-inspections\\.pdf', 'page\\ 51', '\\+in\\ table\\ row:\\ cont\\ next\\ page',
     "Words printed inside this table row's area that the row lacks; they are stored word for word in Attachment B on the same page (verified): a cell continued from a neighbouring row, a header cell or note text read into the row's band. No value lost.")
rule('fda\\-cp\\-7346\\-832\\-preapproval\\-inspections\\.pdf', 'page\\ 52', '\\+in\\ table\\ row:\\ iqa\\ team',
     "Words printed inside this table row's area that the row lacks; they are stored word for word in Attachment B on the same page (verified): a cell continued from a neighbouring row, a header cell or note text read into the row's band. No value lost.")
rule('fda\\-cp\\-7346\\-832\\-preapproval\\-inspections\\.pdf', 'page\\ 52', '\\+in\\ table\\ row:\\ manufacturing\\ and\\ control\\ of\\ finished\\ product\\ parametric\\ release\\ for\\ terminally\\ sterilized\\ drug\\ products\\ the\\ iqa\\ team\\ assesses\\ the\\ overall\\ drug\\ product\\ control\\ strategy\\ including\\ parametric\\ release\\ included\\ in\\ the\\ application\\ e\\ g\\ proposed\\ terminal\\ sterilization\\ cycle\\ critical\\ process\\ parameters\\ acceptance\\ criteria\\ that\\ will\\ allow\\ critical\\ process\\ controls\\ to\\ act\\ as\\ surrogates\\ for\\ sterility\\ testing',
     "Words printed inside this table row's area that the row lacks; they are stored word for word in Table 4 Manufacturing and control of finished… #4 on the same page (verified): a cell continued from a neighbouring row, a header cell or note text read into the row's band. No value lost.")
rule('fda\\-cp\\-7346\\-832\\-preapproval\\-inspections\\.pdf', 'page\\ 52', '\\+in\\ table\\ row:\\ e\\ g\\ preventative\\ maintenance\\ program\\ facility\\ equipment\\ quality\\ system\\ investigations\\ and\\ batch\\ release',
     "Words printed inside this table row's area that the row lacks; they are stored word for word in Table 4 Manufacturing and control of finished… #4 on the same page (verified): a cell continued from a neighbouring row, a header cell or note text read into the row's band. No value lost.")
rule('fda\\-cp\\-7346\\-832\\-preapproval\\-inspections\\.pdf', 'page\\ 52', '\\+in\\ table\\ row:\\ and\\ compliance\\ program\\ 7356\\.002\\ a',
     "Words printed inside this table row's area that the row lacks; they are stored word for word in Table 4 Manufacturing and control of finished… #4 on the same page (verified): a cell continued from a neighbouring row, a header cell or note text read into the row's band. No value lost.")
rule('fda\\-cp\\-7346\\-832\\-preapproval\\-inspections\\.pdf', 'page\\ 52', '\\+in\\ table\\ row:\\ regarding',
     "Words printed inside this table row's area that the row lacks; they are stored word for word in Attachment B on the same page (verified): a cell continued from a neighbouring row, a header cell or note text read into the row's band. No value lost.")
rule('fda\\-cp\\-7346\\-832\\-preapproval\\-inspections\\.pdf', 'page\\ 52', '\\+in\\ table\\ row:\\ parametric\\ release',
     "Words printed inside this table row's area that the row lacks; they are stored word for word in Attachment B on the same page (verified): a cell continued from a neighbouring row, a header cell or note text read into the row's band. No value lost.")
rule('fda\\-cp\\-7346\\-832\\-preapproval\\-inspections\\.pdf', 'page\\ 52', '\\+in\\ table\\ row:\\ include',
     "Words printed inside this table row's area that the row lacks; they are stored word for word in Attachment B on the same page (verified): a cell continued from a neighbouring row, a header cell or note text read into the row's band. No value lost.")
rule('fda\\-cp\\-7346\\-832\\-preapproval\\-inspections\\.pdf', 'page\\ 52', '\\+in\\ table\\ row:\\ issues\\ related\\ to\\ validation\\ data',
     "Words printed inside this table row's area that the row lacks; they are stored word for word in Table 4 Manufacturing and control of finished… #4 on the same page (verified): a cell continued from a neighbouring row, a header cell or note text read into the row's band. No value lost.")
rule('fda\\-guidance\\-container\\-closure\\-systems\\-1999\\.pdf', 'page\\ 26', '\\+in\\ table\\ row:\\ terms\\ svp',
     "Words printed inside this table row's area that the row lacks; they are stored word for word in III.E.1 on the same page (verified): a cell continued from a neighbouring row, a header cell or note text read into the row's band. No value lost.")
rule('fda\\-guidance\\-container\\-closure\\-systems\\-1999\\.pdf', 'page\\ 26', '\\+in\\ table\\ row:\\ lvp',
     "Words printed inside this table row's area that the row lacks; they are stored word for word in III.E.1 on the same page (verified): a cell continued from a neighbouring row, a header cell or note text read into the row's band. No value lost.")
rule('fda\\-guidance\\-container\\-closure\\-systems\\-1999\\.pdf', 'page\\ 26', '\\+in\\ table\\ row:\\ used',
     "Words printed inside this table row's area that the row lacks; they are stored word for word in III.C.4 on the same page (verified): a cell continued from a neighbouring row, a header cell or note text read into the row's band. No value lost.")
rule('fda\\-guidance\\-container\\-closure\\-systems\\-1999\\.pdf', 'page\\ 26', '\\+in\\ table\\ row:\\ this\\ guidance\\ correspond',
     "Words printed inside this table row's area that the row lacks; they are stored word for word in III.E.1 on the same page (verified): a cell continued from a neighbouring row, a header cell or note text read into the row's band. No value lost.")
rule('fda\\-guidance\\-container\\-closure\\-systems\\-1999\\.pdf', 'page\\ 26', '\\+in\\ table\\ row:\\ definitions',
     "Words printed inside this table row's area that the row lacks; they are stored word for word in III.E.1 on the same page (verified): a cell continued from a neighbouring row, a header cell or note text read into the row's band. No value lost.")
rule('fda\\-guidance\\-container\\-closure\\-systems\\-1999\\.pdf', 'page\\ 26', '\\+in\\ table\\ row:\\ small\\ volume\\ injection',
     "Words printed inside this table row's area that the row lacks; they are stored word for word in III.E.1 on the same page (verified): a cell continued from a neighbouring row, a header cell or note text read into the row's band. No value lost.")
rule('fda\\-guidance\\-container\\-closure\\-systems\\-1999\\.pdf', 'page\\ 26', '\\+in\\ table\\ row:\\ large',
     "Words printed inside this table row's area that the row lacks; they are stored word for word in III.E.1 on the same page (verified): a cell continued from a neighbouring row, a header cell or note text read into the row's band. No value lost.")
rule('fda\\-guidance\\-container\\-closure\\-systems\\-1999\\.pdf', 'page\\ 26', '\\+in\\ table\\ row:\\ volume\\ injection\\ respectively',
     "Words printed inside this table row's area that the row lacks; they are stored word for word in III.E.1 on the same page (verified): a cell continued from a neighbouring row, a header cell or note text read into the row's band. No value lost.")
rule('fda\\-guidance\\-quality\\-systems\\-approach\\-2006\\.pdf', 'page\\ 16', '\\+in\\ table\\ row:\\ systemelement',
     "Words printed inside this table row's area that the row lacks; they are stored word for word in Table 1 row 1 on the same page (verified): a cell continued from a neighbouring row, a header cell or note text read into the row's band. No value lost.")
rule('fda\\-guidance\\-quality\\-systems\\-approach\\-2006\\.pdf', 'page\\ 18', '\\+in\\ table\\ row:\\ andequipment',
     "Words printed inside this table row's area that the row lacks; they are stored word for word in IV.B.3 on the same page (verified): a cell continued from a neighbouring row, a header cell or note text read into the row's band. No value lost.")
rule('fda\\-guidance\\-quality\\-systems\\-approach\\-2006\\.pdf', 'page\\ 25', '\\+in\\ table\\ row:\\ systemelement',
     "Words printed inside this table row's area that the row lacks; they are stored word for word in Table 4 Quality System Element on the same page (verified): a cell continued from a neighbouring row, a header cell or note text read into the row's band. No value lost.")
rule('fda\\-guidance\\-quality\\-systems\\-approach\\-2006\\.pdf', 'page\\ 25', '\\+in\\ table\\ row:\\ anddevelop',
     "Words printed inside this table row's area that the row lacks; they are stored word for word in Table 4 1. Design and Develop Product and… on the same page (verified): a cell continued from a neighbouring row, a header cell or note text read into the row's band. No value lost.")
rule('fda\\-guidance\\-quality\\-systems\\-approach\\-2006\\.pdf', 'page\\ 25', '\\+in\\ table\\ row:\\ 211\\.122,211\\.125',
     "Citations '211.122, 211.125' that pdfminer reads without the space, so the tokenizer makes one number of them; the stored row has both citations.")
rule('fda\\-guidance\\-quality\\-systems\\-approach\\-2006\\.pdf', 'page\\ 28', '\\+in\\ table\\ row:\\ datafortrends',
     "Words printed inside this table row's area that the row lacks; they are stored word for word in Table 5 1. Analyze Data for Trends on the same page (verified): a cell continued from a neighbouring row, a header cell or note text read into the row's band. No value lost.")
rule('ich\\-q12\\.pdf', 'page\\ 26', '\\+in\\ table\\ row:\\ supportive\\ information',
     "Words printed inside this table row's area that the row lacks; they are stored word for word in Appendix 1 on the same page (verified): a cell continued from a neighbouring row, a header cell or note text read into the row's band. No value lost.")
rule('ich\\-q12\\.pdf', 'page\\ 26', '\\+in\\ table\\ row:\\ drug\\ product',
     "Words printed inside this table row's area that the row lacks; they are stored word for word in Table 4 3.2.S.7.3 on the same page (verified): a cell continued from a neighbouring row, a header cell or note text read into the row's band. No value lost.")
rule('ich\\-q2\\-r2\\.pdf', 'page\\ 34', '\\+in\\ table\\ row:\\ procedure',
     "Words printed inside this table row's area that the row lacks; they are stored word for word in 7 on the same page (verified): a cell continued from a neighbouring row, a header cell or note text read into the row's band. No value lost.")
rule('ich\\-q7\\-qa\\.pdf', 'page\\ 21', '\\+in\\ table\\ row:\\ 11\\.6',
     "Words printed inside this table row's area that the row lacks; they are stored word for word in Table 31 3 on the same page (verified): a cell continued from a neighbouring row, a header cell or note text read into the row's band. No value lost.")
rule('ich\\-q7\\-qa\\.pdf', 'page\\ 21', '\\+in\\ table\\ row:\\ 11\\.72',
     "Words printed inside this table row's area that the row lacks; they are stored word for word in Table 31 5 on the same page (verified): a cell continued from a neighbouring row, a header cell or note text read into the row's band. No value lost.")
rule('india\\-cdsco\\-circ\\-2024\\-03\\-risk\\-based\\-inspection\\.pdf', 'page\\ 81', '\\+in\\ table\\ row:\\ loop\\ system',
     "Words printed inside this table row's area that the row lacks; they are stored word for word in Table 29 4.17.1 on the same page (verified): a cell continued from a neighbouring row, a header cell or note text read into the row's band. No value lost.")
rule('india\\-cdsco\\-circ\\-2024\\-03\\-risk\\-based\\-inspection\\.pdf', 'page\\ 82', '\\+in\\ table\\ row:\\ circulation\\ rate',
     "Words printed inside this table row's area that the row lacks; they are stored word for word in Table 29 1 Building 4.18 on the same page (verified): a cell continued from a neighbouring row, a header cell or note text read into the row's band. No value lost.")
rule('india\\-cdsco\\-circ\\-2024\\-03\\-risk\\-based\\-inspection\\.pdf', 'page\\ 91', '\\+in\\ table\\ row:\\ area',
     "Words printed inside this table row's area that the row lacks; they are stored word for word in Table 29 10.6 on the same page (verified): a cell continued from a neighbouring row, a header cell or note text read into the row's band. No value lost.")
rule('india\\-cdsco\\-circ\\-2024\\-03\\-risk\\-based\\-inspection\\.pdf', 'page\\ 91', '\\+in\\ table\\ row:\\ 3\\ pressure\\ gradients',
     "Words printed inside this table row's area that the row lacks; they are stored word for word in Table 29 11.4 on the same page (verified): a cell continued from a neighbouring row, a header cell or note text read into the row's band. No value lost.")
rule('india\\-cdsco\\-circ\\-2024\\-03\\-risk\\-based\\-inspection\\.pdf', 'page\\ 105', '\\+in\\ table\\ row:\\ condition',
     "Words printed inside this table row's area that the row lacks; they are stored word for word in Table 29 1 Building 19.3 on the same page (verified): a cell continued from a neighbouring row, a header cell or note text read into the row's band. No value lost.")
rule('india\\-cdsco\\-circ\\-2024\\-03\\-risk\\-based\\-inspection\\.pdf', 'page\\ 111', '\\+in\\ table\\ row:\\ by\\ suitable\\ pipes',
     "Words printed inside this table row's area that the row lacks; they are stored word for word in Table 29 23.4 on the same page (verified): a cell continued from a neighbouring row, a header cell or note text read into the row's band. No value lost.")
rule('india\\-cdsco\\-circ\\-2024\\-03\\-risk\\-based\\-inspection\\.pdf', 'page\\ 111', '\\+in\\ table\\ row:\\ established\\ hold\\ time',
     "Words printed inside this table row's area that the row lacks; they are stored word for word in 3 #2 on the same page (verified): a cell continued from a neighbouring row, a header cell or note text read into the row's band. No value lost.")
rule('india\\-cdsco\\-circ\\-2024\\-03\\-risk\\-based\\-inspection\\.pdf', 'page\\ 117', '\\+in\\ table\\ row:\\ system',
     "Words printed inside this table row's area that the row lacks; they are stored word for word in 3 #2 on the same page (verified): a cell continued from a neighbouring row, a header cell or note text read into the row's band. No value lost.")
rule('india\\-cdsco\\-circ\\-2024\\-03\\-risk\\-based\\-inspection\\.pdf', 'page\\ 136', '\\+in\\ table\\ row:\\ relevant\\ equipment\\ and\\ utilities',
     "Words printed inside this table row's area that the row lacks; they are stored word for word in Table 29 50.2 on the same page (verified): a cell continued from a neighbouring row, a header cell or note text read into the row's band. No value lost.")
rule('india\\-drugs\\-rules\\-1945\\-consolidated\\-2024\\-07\\.pdf', 'page\\ 158', '\\+in\\ table\\ row:\\ serial\\ number\\ common\\ name\\ of\\ colour\\ colour\\ index\\ number\\ chemical\\ name\\ of\\ colour\\ 1\\ 2\\ 3\\ 4',
     "The colour table's header row and column numbers (1-4) repeated at the top of the page; stored once as the table's header row.")
rule('india\\-drugs\\-rules\\-1945\\-consolidated\\-2024\\-07\\.pdf', 'page\\ 325', '\\+in\\ table\\ row:\\ revised\\ by\\ the\\ director\\ pharmacopoeia\\ commission',
     "Words printed inside this table row's area that the row lacks; they are stored word for word in Part XV 3 #28 on the same page (verified): a cell continued from a neighbouring row, a header cell or note text read into the row's band. No value lost.")
rule('india\\-drugs\\-rules\\-1945\\-consolidated\\-2024\\-07\\.pdf', 'page\\ 325', '\\+in\\ table\\ row:\\ indian\\ medicine\\ and\\ homoeopathy\\ or\\ government\\ analyst',
     "Words printed inside this table row's area that the row lacks; they are stored word for word in Part XV 3 #28 on the same page (verified): a cell continued from a neighbouring row, a header cell or note text read into the row's band. No value lost.")
rule('india\\-drugs\\-rules\\-1945\\-consolidated\\-2024\\-07\\.pdf', 'page\\ 325', '\\+in\\ table\\ row:\\ its\\ central\\ laboratory',
     "Words of the note under the testing-charges table ('...Government Analyst of its Central Laboratory...'), read into the table's area; stored in clause Part XV 3 #28 (verified).")
rule('india\\-drugs\\-rules\\-1945\\-consolidated\\-2024\\-07\\.pdf', 'page\\ 325', '\\+in\\ table\\ row:\\ the\\ case\\ may\\ be\\ in\\ consultation\\ with\\ the\\ ministry\\ of\\ ayurveda\\ yoga',
     "Words printed inside this table row's area that the row lacks; they are stored word for word in Part XV 3 #28 on the same page (verified): a cell continued from a neighbouring row, a header cell or note text read into the row's band. No value lost.")
rule('india\\-drugs\\-rules\\-1945\\-consolidated\\-2024\\-07\\.pdf', 'page\\ 326', '\\+in\\ table\\ row:\\ serum\\ proteins\\ intended',
     "Words printed inside this table row's area that the row lacks; they are stored word for word in Part XV 3 #28 on the same page (verified): a cell continued from a neighbouring row, a header cell or note text read into the row's band. No value lost.")
rule('india\\-drugs\\-rules\\-1945\\-consolidated\\-2024\\-07\\.pdf', 'page\\ 328', '\\+in\\ table\\ row:\\ class\\ of\\ drugs\\ extent\\ and\\ conditions\\ of\\ exemption',
     "Words printed inside this table row's area that the row lacks; they are stored word for word in Table 22 header on the same page (verified): a cell continued from a neighbouring row, a header cell or note text read into the row's band. No value lost.")
rule('india\\-drugs\\-rules\\-1945\\-consolidated\\-2024\\-07\\.pdf', 'page\\ 526', '\\+in\\ table\\ row:\\ the',
     "Words printed inside this table row's area that the row lacks; they are stored word for word in Part IV 99 on the same page (verified): a cell continued from a neighbouring row, a header cell or note text read into the row's band. No value lost.")
rule('india\\-drugs\\-rules\\-1945\\-consolidated\\-2024\\-07\\.pdf', 'page\\ 795', '\\+in\\ table\\ row:\\ phosphate',
     "Words printed inside this table row's area that the row lacks; they are stored word for word in Table 35 6. #4 on the same page (verified): a cell continued from a neighbouring row, a header cell or note text read into the row's band. No value lost.")
rule('india\\-drugs\\-rules\\-1945\\-consolidated\\-2024\\-07\\.pdf', 'page\\ 821', '\\+in\\ table\\ row:\\ mixer',
     "Words printed inside this table row's area that the row lacks; they are stored word for word in Table 44 2. on the same page (verified): a cell continued from a neighbouring row, a header cell or note text read into the row's band. No value lost.")
rule('india\\-drugs\\-rules\\-1945\\-consolidated\\-2024\\-07\\.pdf', 'page\\ 822', '\\+in\\ table\\ row:\\ s\\ no\\ category\\ of\\ medicine\\ minimum\\ manufacturing\\ space\\ required\\ machinery\\ equipment\\ recommended\\ 1\\ 2\\ 3\\ 4',
     "Words printed inside this table row's area that the row lacks; they are stored word for word in Table 45 S.No. Category of Medicine Minimum… on the same page (verified): a cell continued from a neighbouring row, a header cell or note text read into the row's band. No value lost.")
rule('india\\-drugs\\-rules\\-1945\\-consolidated\\-2024\\-07\\.pdf', 'page\\ 897', '\\+in\\ table\\ row:\\ rodent\\ rat',
     "Words printed inside this table row's area that the row lacks; they are stored word for word in Table 56 Group on the same page (verified): a cell continued from a neighbouring row, a header cell or note text read into the row's band. No value lost.")
rule('india\\-schedule\\-m\\-2023\\-GSR922E\\.pdf', 'page\\ 184', '\\+in\\ table\\ row:\\ terminally\\ sterilised\\ products',
     "Words printed inside this table row's area that the row lacks; they are stored word for word in Part II 4.11.1 on the same page (verified): a cell continued from a neighbouring row, a header cell or note text read into the row's band. No value lost.")
rule('india\\-schedule\\-m\\-2023\\-GSR922E\\.pdf', 'page\\ 184', '\\+in\\ table\\ row:\\ risk',
     "Words printed inside this table row's area that the row lacks; they are stored word for word in Part II 4.7 on the same page (verified): a cell continued from a neighbouring row, a header cell or note text read into the row's band. No value lost.")
rule('pics\\-pe009\\-18\\-annexes\\.pdf', 'page\\ 218', '\\+in\\ table\\ row:\\ blood',
     "Words printed inside this table row's area that the row lacks; they are stored word for word in Annex 14 10 on the same page (verified): a cell continued from a neighbouring row, a header cell or note text read into the row's band. No value lost.")
rule('pics\\-pi030\\-1\\-am\\-api\\.pdf', 'page\\ 10', '\\+in\\ table\\ row:\\ 4\\ building',
     "A repeated table title or section label printed in the row's area ('4 building'); stored once, in Table 5 4. Building and facilities. Not a value of this row.")
rule('pics\\-pi030\\-1\\-am\\-api\\.pdf', 'page\\ 10', '\\+in\\ table\\ row:\\ facilities',
     "A repeated table title or section label printed in the row's area ('facilities'); stored once, in Table 2 Basic information related to the site. Not a value of this row.")
rule('pics\\-pi030\\-1\\-am\\-api\\.pdf', 'page\\ 10', '\\+in\\ table\\ row:\\ and',
     "Words printed inside this table row's area that the row lacks; they are stored word for word in Table 5 Water on the same page (verified): a cell continued from a neighbouring row, a header cell or note text read into the row's band. No value lost.")
rule('pics\\-pi030\\-1\\-am\\-api\\.pdf', 'page\\ 14', '\\+in\\ table\\ row:\\ 8\\ production',
     "Words printed inside this table row's area that the row lacks; they are stored word for word in Table 9 8. Production and in process controls on the same page (verified): a cell continued from a neighbouring row, a header cell or note text read into the row's band. No value lost.")
rule('pics\\-pi030\\-1\\-am\\-api\\.pdf', 'page\\ 14', '\\+in\\ table\\ row:\\ controls',
     "Words printed inside this table row's area that the row lacks; they are stored word for word in Table 9 8. Production and in process controls on the same page (verified): a cell continued from a neighbouring row, a header cell or note text read into the row's band. No value lost.")
rule('pics\\-pi030\\-1\\-am\\-api\\.pdf', 'page\\ 14', '\\+in\\ table\\ row:\\ process',
     "Words printed inside this table row's area that the row lacks; they are stored word for word in Table 9 8. Production and in process controls on the same page (verified): a cell continued from a neighbouring row, a header cell or note text read into the row's band. No value lost.")
rule('pics\\-pi030\\-1\\-am\\-api\\.pdf', 'page\\ 14', '\\+in\\ table\\ row:\\ and',
     "Words printed inside this table row's area that the row lacks; they are stored word for word in Table 9 8. Production and in process controls on the same page (verified): a cell continued from a neighbouring row, a header cell or note text read into the row's band. No value lost.")
rule('pics\\-pi030\\-1\\-am\\-api\\.pdf', 'page\\ 15', '\\+in\\ table\\ row:\\ 8\\ production',
     "A repeated table title or section label printed in the row's area ('8 production'); stored once, in Table 9 8. Production and in process controls. Not a value of this row.")
rule('pics\\-pi030\\-1\\-am\\-api\\.pdf', 'page\\ 15', '\\+in\\ table\\ row:\\ controls',
     "Words printed inside this table row's area that the row lacks; they are stored word for word in Table 9 Production Operations on the same page (verified): a cell continued from a neighbouring row, a header cell or note text read into the row's band. No value lost.")
rule('pics\\-pi030\\-1\\-am\\-api\\.pdf', 'page\\ 15', '\\+in\\ table\\ row:\\ and',
     "Words printed inside this table row's area that the row lacks; they are stored word for word in Table 9 Production Operations on the same page (verified): a cell continued from a neighbouring row, a header cell or note text read into the row's band. No value lost.")
rule('pics\\-pi030\\-1\\-am\\-api\\.pdf', 'page\\ 17', '\\+in\\ table\\ row:\\ 10\\ storage',
     "Words printed inside this table row's area that the row lacks; they are stored word for word in Table 11 10. Storage and distribution on the same page (verified): a cell continued from a neighbouring row, a header cell or note text read into the row's band. No value lost.")
rule('pics\\-pi030\\-1\\-am\\-api\\.pdf', 'page\\ 17', '\\+in\\ table\\ row:\\ distribution',
     "Words printed inside this table row's area that the row lacks; they are stored word for word in Table 11 10. Storage and distribution on the same page (verified): a cell continued from a neighbouring row, a header cell or note text read into the row's band. No value lost.")
rule('pics\\-pi030\\-1\\-am\\-api\\.pdf', 'page\\ 17', '\\+in\\ table\\ row:\\ and',
     "Words printed inside this table row's area that the row lacks; they are stored word for word in Table 10 Packaging and labelling on the same page (verified): a cell continued from a neighbouring row, a header cell or note text read into the row's band. No value lost.")
rule('pics\\-pi030\\-1\\-am\\-api\\.pdf', 'page\\ 19', '\\+in\\ table\\ row:\\ 12\\ validation',
     "A repeated table title or section label printed in the row's area ('12 validation'); stored once, in Table 13 12. Validation. Not a value of this row.")
rule('pics\\-pi030\\-1\\-am\\-api\\.pdf', 'page\\ 20', '\\+in\\ table\\ row:\\ 12\\ validation',
     "A repeated table title or section label printed in the row's area ('12 validation'); stored once, in Table 13 12. Validation. Not a value of this row.")
rule('pics\\-pi041\\-1\\-data\\-integrity\\.pdf', 'page\\ 17', '\\+in\\ table\\ row:\\ data\\ integrity\\ attribute\\ requirement',
     "Words printed inside this table row's area that the row lacks; they are stored word for word in Table 2 header on the same page (verified): a cell continued from a neighbouring row, a header cell or note text read into the row's band. No value lost.")
rule('pics\\-pi043\\-1\\-am\\-cross\\-contamination\\.pdf', 'page\\ 16', '\\+in\\ table\\ row:\\ 3\\.2',
     "Words printed inside this table row's area that the row lacks; they are stored word for word in Table 8 3.8 on the same page (verified): a cell continued from a neighbouring row, a header cell or note text read into the row's band. No value lost.")
rule('pics\\-pi043\\-1\\-am\\-cross\\-contamination\\.pdf', 'page\\ 16', '\\+in\\ table\\ row:\\ 3\\.9',
     "Words printed inside this table row's area that the row lacks; they are stored word for word in Table 8 3.9 on the same page (verified): a cell continued from a neighbouring row, a header cell or note text read into the row's band. No value lost.")
rule('pics\\-pi043\\-1\\-am\\-cross\\-contamination\\.pdf', 'page\\ 16', '\\+in\\ table\\ row:\\ 1\\.12\\ 1\\.13\\ 4\\.3\\ 4\\.4\\ annex\\ 15',
     "Words printed inside this table row's area that the row lacks; they are stored word for word in Table 8 3.21 on the same page (verified): a cell continued from a neighbouring row, a header cell or note text read into the row's band. No value lost.")
rule('pics\\-pi054\\-1\\-pqs\\-effectiveness\\.pdf', 'page\\ 5', '\\+in\\ table\\ row:\\ changes',
     "Words printed inside this table row's area that the row lacks; they are stored word for word in 3.6 on the same page (verified): a cell continued from a neighbouring row, a header cell or note text read into the row's band. No value lost.")
rule('pics\\-pi054\\-1\\-pqs\\-effectiveness\\.pdf', 'page\\ 5', '\\+in\\ table\\ row:\\ proposed\\ in\\ a',
     "Words printed inside this table row's area that the row lacks; they are stored word for word in Table 4 \uf09e The change management system ensures… on the same page (verified): a cell continued from a neighbouring row, a header cell or note text read into the row's band. No value lost.")
rule('pics\\-pi054\\-1\\-pqs\\-effectiveness\\.pdf', 'page\\ 5', '\\+in\\ table\\ row:\\ proposed',
     "Words printed inside this table row's area that the row lacks; they are stored word for word in 5.2 on the same page (verified): a cell continued from a neighbouring row, a header cell or note text read into the row's band. No value lost.")
rule('pics\\-pi054\\-1\\-pqs\\-effectiveness\\.pdf', 'page\\ 5', '\\+in\\ table\\ row:\\ potential\\ impacts\\ of',
     "Words printed inside this table row's area that the row lacks; they are stored word for word in 5.2 on the same page (verified): a cell continued from a neighbouring row, a header cell or note text read into the row's band. No value lost.")
rule('pics\\-pi054\\-1\\-pqs\\-effectiveness\\.pdf', 'page\\ 5', '\\+in\\ table\\ row:\\ on\\ other\\ products\\ processes',
     "Words printed inside this table row's area that the row lacks; they are stored word for word in Table 4 \uf09e The potential impacts of the proposed… on the same page (verified): a cell continued from a neighbouring row, a header cell or note text read into the row's band. No value lost.")
rule('who\\-trs961\\-a2\\-micro\\-labs\\.pdf', 'page\\ 21', '\\+in\\ table\\ row:\\ othersurfaces',
     "Words printed inside this table row's area that the row lacks; they are stored word for word in Table 2 Laboratory on the same page (verified): a cell continued from a neighbouring row, a header cell or note text read into the row's band. No value lost.")
rule('who\\-trs992\\-a5\\-ttsp\\-supplements\\.pdf', 'page\\ 4', '\\+in\\ table\\ row:\\ title\\ section\\ s',
     "Words printed inside this table row's area that the row lacks; they are stored word for word in 1.1 on the same page (verified): a cell continued from a neighbouring row, a header cell or note text read into the row's band. No value lost.")
rule('who\\-trs992\\-a5\\-ttsp\\-supplements\\.pdf', 'page\\ 4', '\\+in\\ table\\ row:\\ 10\\ checking\\ the\\ accuracy',
     "Words printed inside this table row's area that the row lacks; they are stored word for word in Table 4 10. Checking the accuracy of… on the same page (verified): a cell continued from a neighbouring row, a header cell or note text read into the row's band. No value lost.")
rule('who\\-trs992\\-a5\\-ttsp\\-supplements\\.pdf', 'page\\ 4', '\\+in\\ table\\ row:\\ control',
     "Words printed inside this table row's area that the row lacks; they are stored word for word in 1.1 on the same page (verified): a cell continued from a neighbouring row, a header cell or note text read into the row's band. No value lost.")
rule('who\\-trs992\\-a5\\-ttsp\\-supplements\\.pdf', 'page\\ 4', '\\+in\\ table\\ row:\\ devices',
     "Words printed inside this table row's area that the row lacks; they are stored word for word in Table 4 10. Checking the accuracy of… on the same page (verified): a cell continued from a neighbouring row, a header cell or note text read into the row's band. No value lost.")
rule('who\\-trs992\\-a5\\-ttsp\\-supplements\\.pdf', 'page\\ 4', '\\+in\\ table\\ row:\\ 4\\.10',
     "Words printed inside this table row's area that the row lacks; they are stored word for word in Table 4 10. Checking the accuracy of… on the same page (verified): a cell continued from a neighbouring row, a header cell or note text read into the row's band. No value lost.")
rule('who\\-trs996\\-a4\\-app1\\-model\\-inspection\\-report\\.pdf', 'page\\ 16', '\\+in\\ table\\ row:\\ category',
     "Words printed inside this table row's area that the row lacks; they are stored word for word in Annex 3 Appendix 2 on the same page (verified): a cell continued from a neighbouring row, a header cell or note text read into the row's band. No value lost.")
rule('who\\-trs996\\-a4\\-app1\\-model\\-inspection\\-report\\.pdf', 'page\\ 16', '\\+in\\ table\\ row:\\ the\\ site',
     "Words printed inside this table row's area that the row lacks; they are stored word for word in Annex 3 Appendix 2 on the same page (verified): a cell continued from a neighbouring row, a header cell or note text read into the row's band. No value lost.")
rule(r"pics-pi011-3", r"8\.6|20\.[12]", r"(\+security \| -security|\+authorities \| -authorities \| \+34|\+records \| -records|\+security|\+authorities \| \+34|\+records)",
     "Footnote marks (13, 32-35) printed after the last word of a line: pdfminer places the word after the mark, the "
     "stored text before it; same words, one footnote number moved.")
rule(r"ich-q12", r"3|4", r"(-3|-4 \| -change management protocol pacmp)",
     "Heading clauses '3 Established Conditions (ECs)' / '4 Post-approval change management protocol (PACMP)': "
     "the heading wraps over two lines and pdfminer reads its words and number in another order. Headings only.")
rule(r"ich-q2-r2", r"3\.2\.3\.3", r"\+dl( \| -dl)? \| \+ql( \| -ql)?",
     f"Parser defect ({B}): the DL and QL equations ('DL = 3.3 σ / S', 'QL = 10 σ / S') are stored flattened with the "
     "symbol after the numerator ('3.3 σ DL S'); values unchanged.")
rule(r"ich-q3c-r9", r"Part I 4\.[12]", r"\+(ppm|methylisobutylketone)( \| -(ppm|methylisobutylketone))?",
     "A wrapped table cell (header 'Concentration limit (ppm)', solvent 'Methylisobutylketone') stored before the "
     "next cell, pdfminer reads it after; same words and values.")
rule(r"who-trs1019-a3-validation", r"Appendix 4 9\.2", r"\+procedure( \| -procedure)? \| \+procedure( \| -procedure)?",
     f"Parser defect ({B}): the validation-characteristics table (Table A4.1) is stored as clause text with wrapped "
     "header cells interleaved ('type of analytical testing for procedure impurities') and note letters glued "
     "('assaya'). All words stored.")
rule(r"india-cdsco-circ-2024-03", r"12", r"-s",
     "A stray letter at the end of the reference list entry (a plural 's' printed on its own); no requirement word.")
rule(r"india-cdsco-circ-2024-03", r"3 #2", r".*",
     f"Parser defect ({B}): reference '3' starts a clause that runs from page 16 to 143 and holds the annexure "
     "headings, the inspection-report form and stray table fragments ('established hold time. system.'); the "
     "annexure tables themselves are stored as table rows.")
rule(r"india-cdsco-circ-2024-03", r"Table 13 22\.6|Table 29 (4\.19|11\.4|20\.5|50\.3)", r"-(who trs 961|circulation rate|area|condition|relevant equipment utilities)",
     "Wrapped cell text of the risk-rating table printed outside the row's band; stored in the row unchanged.")
rule(r"india-cdsco-circ-2024-03", r"page (46|51)", r"\+annexe 06 (19 environmental monitoring|24 aseptic processing and sterilization by filtration)",
     "Section label of the annexure table ('Annexe-06', '19 Environmental Monitoring'), stored as the section name of "
     "the following table rows; heading, not requirement text.")
rule(r"india-cdsco-circ-2024-03", r"page 120", r"\+sch m specify the duration .*",
     f"Parser defect ({B}): row 30.9 of the example table is merged with the following row (its question 'Specify "
     "the duration of retaining the documents...' follows the next row's question), so the answers are no longer "
     "tied to their question. All words stored.")
rule(r"india-drugs-rules-1945", r"Part XV (8|5 #3|2 #12|4 #11|9)|Part II Appendix I|Part II 2 #7", r"(\+dated( \| -dated)?|\+restricted( \| -restricted)?|\+loan( \| -loan)? \| \+a( \| -a)?|\+d( \| -d)? \| \+c( \| -c)?|-1303|-reason)",
     "Form words of a licence form ('dated', 'restricted', 'loan', item letters) or a footnote number (1303) read in "
     "another place by pdfminer; the stored form text holds the same words.")
rule(r"pics-pi047-1-gdp", r"Annex", r"\+substances \| -substances",
     "One word of a two-line heading read in another order; same words.")
rule(r"fda-guidance-container-closure-systems-1999", r"_unnumbered:4", r"-d 1",
     f"Parser defect ({B}): the attachment page label 'D-1' is stored at the end of the abbreviations list.")
rule(r"ich-q9r1", r"6\.1", r"-i",
     f"Parser defect ({B}): the page number 'i' of the annex page is stored inside the list in clause 6.1; pdfminer "
     "reads the running header 'ICH Q9(R1) Guideline' there.")
rule(r"pics-pi011-3", r"18\.6|21\.10|23\.4", r"-(31|45|51)",
     "A footnote mark (31, 45, 51) printed small after the clause's last word, kept in the stored text; not a "
     "regulation number.")
rule(r"who-trs1010-a10-stability", r"Appendix 3 1\.3", r"-1\.3",
     "The clause number 1.3 read by pdfminer beside the heading 'General principles' above it (stored at the end of "
     "1.2); same number.")
rule(r"who-trs957-a2-api|who-trs961-a14-site-master-file|who-trs961-a2-micro-labs", r"Annex 2 Appendix 2 7\.42|Annex 14 1\.4|Annex 2 Appendix 4 2\.4\.5", r"-(first|file|filters)",
     "The clause's last word set with an 'fi' ligature ('ﬁrst', 'ﬁle', 'ﬁlters'), which pdfminer reads as two "
     "pieces outside the clause's stretch; the stored word is right.")
rule(r"who-trs992-a5-ttsp", r"_unnumbered:(28|32)", r"-references",
     "Contents-page entry 'References' of a reproduced supplement contents page read by pdfminer apart; contents "
     "listing, not requirements.")
rule(r"india-drugs-rules-1945", r"Part II Appendix III 1\.9", r"-1\.9 number of animals required for repeated dose toxicity studies \| -cerebrum cerebellum midbrain \| -mesenteric",
     f"Parser defect ({B}): clause 1.9 also holds section 2.0 (laboratory parameters), its table of animal numbers is "
     "stored as table rows, and the multi-column organ list is stored in layout order ('Eye (Middle Ear) Cerebrum, "
     "Cerebellum, Midbrain'). All words stored.")
rule('ema\\-water\\-quality\\-guideline\\.pdf', 'page\\ 7', '\\+in\\ table\\ row:\\ 5\\.2',
     "Words printed inside this table row's area that the row lacks; they are stored word for word in 5.2 on the same page (verified): a cell continued from a neighbouring row, a running header, a caption or note text read into the row's full band. No value lost.")
rule('ema\\-water\\-quality\\-guideline\\.pdf', 'page\\ 7', '\\+in\\ table\\ row:\\ the\\ final',
     "Words printed inside this table row's area that the row lacks; they are stored word for word in 5.1 on the same page (verified): a cell continued from a neighbouring row, a running header, a caption or note text read into the row's full band. No value lost.")
rule('ema\\-water\\-quality\\-guideline\\.pdf', 'page\\ 7', '\\+in\\ table\\ row:\\ the\\ grade\\ of',
     "Words printed inside this table row's area that the row lacks; they are stored word for word in 5.1 on the same page (verified): a cell continued from a neighbouring row, a running header, a caption or note text read into the row's full band. No value lost.")
rule('ema\\-water\\-quality\\-guideline\\.pdf', 'page\\ 7', '\\+in\\ table\\ row:\\ the',
     "Words printed inside this table row's area that the row lacks; they are stored word for word in 5.1 on the same page (verified): a cell continued from a neighbouring row, a running header, a caption or note text read into the row's full band. No value lost.")
rule('ema\\-water\\-quality\\-guideline\\.pdf', 'page\\ 7', '\\+in\\ table\\ row:\\ for\\ the\\ manufacture\\ of\\ active\\ substances\\ table\\ 3',
     "Words printed inside this table row's area that the row lacks; they are stored word for word in 5.2 on the same page (verified): a cell continued from a neighbouring row, a running header, a caption or note text read into the row's full band. No value lost.")
rule('ema\\-water\\-quality\\-guideline\\.pdf', 'page\\ 7', '\\+in\\ table\\ row:\\ used\\ during\\ the\\ manufacture\\ of\\ active\\ substances\\ as',
     "Words printed inside this table row's area that the row lacks; they are stored word for word in 5.2 on the same page (verified): a cell continued from a neighbouring row, a running header, a caption or note text read into the row's full band. No value lost.")
rule('fda\\-guidance\\-container\\-closure\\-systems\\-1999\\.pdf', 'page\\ 26', '\\+in\\ table\\ row:\\ 23\\ page\\ 1650',
     "Words printed inside this table row's area that the row lacks; they are stored word for word in III.E.1 on the same page (verified): a cell continued from a neighbouring row, a running header, a caption or note text read into the row's full band. No value lost.")
rule('fda\\-guidance\\-quality\\-systems\\-approach\\-2006\\.pdf', 'page\\ 28', '\\+in\\ table\\ row:\\ riskassessment',
     "Words printed inside this table row's area that the row lacks; they are stored word for word in IV.D.4 on the same page (verified): a cell continued from a neighbouring row, a running header, a caption or note text read into the row's full band. No value lost.")
rule('ich\\-q1d\\.pdf', 'page\\ 3', '\\+in\\ table\\ row:\\ 2\\.5\\ data\\ evaluation',
     "Words printed inside this table row's area that the row lacks; they are stored word for word in _toc:2.5 on the same page (verified): a cell continued from a neighbouring row, a running header, a caption or note text read into the row's full band. No value lost.")
rule('ich\\-q2\\-r2\\.pdf', 'page\\ 34', '\\+in\\ table\\ row:\\ table\\ 10\\ example\\ for\\ nir\\ analytical',
     "Words printed inside this table row's area that the row lacks; they are stored word for word in 7 on the same page (verified): a cell continued from a neighbouring row, a running header, a caption or note text read into the row's full band. No value lost.")
rule('india\\-drugs\\-rules\\-1945\\-consolidated\\-2024\\-07\\.pdf', 'page\\ 325', '\\+in\\ table\\ row:\\ note\\ sample',
     "Words printed inside this table row's area that the row lacks; they are stored word for word in Part XV 3 #28 on the same page (verified): a cell continued from a neighbouring row, a running header, a caption or note text read into the row's full band. No value lost.")
rule('india\\-drugs\\-rules\\-1945\\-consolidated\\-2024\\-07\\.pdf', 'page\\ 325', '\\+in\\ table\\ row:\\ charges\\ shall\\ be\\ determined',
     "Words printed inside this table row's area that the row lacks; they are stored word for word in Part XV 3 #28 on the same page (verified): a cell continued from a neighbouring row, a running header, a caption or note text read into the row's full band. No value lost.")
rule('india\\-drugs\\-rules\\-1945\\-consolidated\\-2024\\-07\\.pdf', 'page\\ 325', '\\+in\\ table\\ row:\\ 61\\ and\\ 76\\ and\\ part\\ x',
     "Words printed inside this table row's area that the row lacks; they are stored word for word in Part XV 3 #28 on the same page (verified): a cell continued from a neighbouring row, a running header, a caption or note text read into the row's full band. No value lost.")
rule('india\\-drugs\\-rules\\-1945\\-consolidated\\-2024\\-07\\.pdf', 'page\\ 326', '\\+in\\ table\\ row:\\ injection',
     "Words printed inside this table row's area that the row lacks; they are stored word for word in Part XV 3 #28 on the same page (verified): a cell continued from a neighbouring row, a running header, a caption or note text read into the row's full band. No value lost.")
rule('india\\-drugs\\-rules\\-1945\\-consolidated\\-2024\\-07\\.pdf', 'page\\ 326', '\\+in\\ table\\ row:\\ 3\\ vaccines',
     "Words printed inside this table row's area that the row lacks; they are stored word for word in Part XV 3 #28 on the same page (verified): a cell continued from a neighbouring row, a running header, a caption or note text read into the row's full band. No value lost.")
rule('india\\-drugs\\-rules\\-1945\\-consolidated\\-2024\\-07\\.pdf', 'page\\ 326', '\\+in\\ table\\ row:\\ parenteral\\ injections',
     "Words printed inside this table row's area that the row lacks; they are stored word for word in Part XV 3 #28 on the same page (verified): a cell continued from a neighbouring row, a running header, a caption or note text read into the row's full band. No value lost.")
rule('india\\-drugs\\-rules\\-1945\\-consolidated\\-2024\\-07\\.pdf', 'page\\ 794', '\\+in\\ table\\ row:\\ 4\\ aluminium\\ hydroxide',
     "Words printed inside this table row's area that the row lacks; they are stored word for word in Table 35 4. #5 on the same page (verified): a cell continued from a neighbouring row, a running header, a caption or note text read into the row's full band. No value lost.")
rule('india\\-drugs\\-rules\\-1945\\-consolidated\\-2024\\-07\\.pdf', 'page\\ 795', '\\+in\\ table\\ row:\\ 11',
     "Words printed inside this table row's area that the row lacks; they are stored word for word in Part XIII 4 #2 on the same page (verified): a cell continued from a neighbouring row, a running header, a caption or note text read into the row's full band. No value lost.")
rule('india\\-schedule\\-m\\-2023\\-GSR922E\\.pdf', 'page\\ 185', '\\+in\\ table\\ row:\\ aseptic\\ preparations',
     "Words printed inside this table row's area that the row lacks; they are stored word for word in Table 2 Grade #2 on the same page (verified): a cell continued from a neighbouring row, a running header, a caption or note text read into the row's full band. No value lost.")
rule('pics\\-pe009\\-18\\-annexes\\.pdf', 'page\\ 79', '\\+in\\ table\\ row:\\ manufacture',
     "Words printed inside this table row's area that the row lacks; they are stored word for word in Annex 2A 3 on the same page (verified): a cell continued from a neighbouring row, a running header, a caption or note text read into the row's full band. No value lost.")
rule('pics\\-pe009\\-18\\-annexes\\.pdf', 'page\\ 165', '\\+in\\ table\\ row:\\ products',
     "Words printed inside this table row's area that the row lacks; they are stored word for word in Annex 6 Glossary on the same page (verified): a cell continued from a neighbouring row, a running header, a caption or note text read into the row's full band. No value lost.")
rule('pics\\-pi007\\-6\\-aseptic\\-validation\\.pdf', 'page\\ 5', '\\+in\\ table\\ row:\\ 2001',
     "Words printed inside this table row's area that the row lacks; they are stored word for word in Table 1 Entry into force of version PI 007-1 on the same page (verified): a cell continued from a neighbouring row, a running header, a caption or note text read into the row's full band. No value lost.")
rule('pics\\-pi041\\-1\\-data\\-integrity\\.pdf', 'page\\ 25', '\\+in\\ table\\ row:\\ 8\\.6\\.1\\ the\\ items\\ listed\\ in\\ the\\ table\\ below',
     "Words printed inside this table row's area that the row lacks; they are stored word for word in 8.6.1 on the same page (verified): a cell continued from a neighbouring row, a running header, a caption or note text read into the row's full band. No value lost.")
rule('pics\\-pi054\\-1\\-pqs\\-effectiveness\\.pdf', 'page\\ 5', '\\+in\\ table\\ row:\\ change\\ proposals\\ that',
     "Words printed inside this table row's area that the row lacks; they are stored word for word in Table 4 \uf09e The potential impacts of the proposed… #2 on the same page (verified): a cell continued from a neighbouring row, a running header, a caption or note text read into the row's full band. No value lost.")
rule('pics\\-pi054\\-1\\-pqs\\-effectiveness\\.pdf', 'page\\ 6', '\\+in\\ table\\ row:\\ appropriate\\ science\\ and',
     "Words printed inside this table row's area that the row lacks; they are stored word for word in Table 5 The Change Management system ensures… on the same page (verified): a cell continued from a neighbouring row, a running header, a caption or note text read into the row's full band. No value lost.")
rule('pics\\-pi054\\-1\\-pqs\\-effectiveness\\.pdf', 'page\\ 6', '\\+in\\ table\\ row:\\ approval\\ to\\ proceed\\ with',
     "Words printed inside this table row's area that the row lacks; they are stored word for word in Table 6 \uf09e The change management system ensures… on the same page (verified): a cell continued from a neighbouring row, a running header, a caption or note text read into the row's full band. No value lost.")
rule(r".*", r"_unnumbered:[12]", r".*",
     "Front matter (cover page, document history, contents): the two engines read the cover's text boxes, "
     "address blocks and history table in different orders; not regulation text.")

sys.path.insert(0, f'{ROOT}/tools/parse')
import fidelity as F
from concurrent.futures import ProcessPoolExecutor


# ---- session 5, after the first 0b fixes (each inspected) ----
rule(r"fda-guidance-analytical-procedures-validation-2015", r"^(II|IV|VI\.[ABC]|VII\.A|VIII\.[BC])$", r"[-+]\d{2}( \| [-+]\d{2})*",
     "Footnote reference numbers 10-24 ('...intended purpose. 10 Analytical procedures...'), printed as superscripts "
     "after a sentence; the stored text keeps them as plain numbers next to the sentence end. The margin line "
     "numbers that were left in these sections are removed (0b); no guidance word changes.")
rule(r"fda-guidance-nitrosamine-control-2024", r"_unnumbered:3", r"\+each individual nitrosamine should be calculated .*",
     "The boxed paragraph of Appendix B ('Each individual nitrosamine should be calculated as a percentage of its AI "
     "limit...') is stored word for word as Table 1 row 1 (it is printed in a ruled box); the formula below it is the "
     "known math-glyph limitation.")
rule(r"india-cdsco-circ-2024-03", r"Table 29 (4\.17\.1|54\.9)", r"-(loop system|988)",
     "Cell text wrapped onto the next printed line or page ('...storage tank and loop system.', the reference "
     "'WHO TRS- 988') and stored in its row; the check bands the row by height and misses the wrapped line. The "
     "'Quality Rating' header that was glued into these rows is now stored once as the table header (0b).")
rule(r"india-drugs-rules-1945-consolidated", r"Part II Appendix III 1\.9", r".*",
     "Unruled table of animal groups and organs (rat / non-rodent, M/F columns, organ list) inside the clause, read by "
     "the two engines in different column orders; all words stored in both readings.")
rule(r"india-drugs-rules-1945-consolidated", r"Table 45 12\.", r"-12 office total 1500",
     "Last row of the premises table ('12. Office' with the total '1500 Sq. ft.]' printed below the ruled grid); "
     "stored in the row, the check's row band ends at the grid line.")
rule(r"who-trs1010-a8-hvac", r"7\.11|Table [123] .*", r"-.*",
     "Table A8.1 is printed on landscape pages. The parser now reads an upright copy of those pages (0b), so the "
     "stored rows and clause read forwards; the cells merged across rows (one EU class spans several filter classes) "
     "group several values in one row. The second engine bands the turned page by its own lines, so row stretches "
     "differ; every stored value is printed in the table.")
rule(r"who-trs1010-a8-hvac", r"page 1[567]", r"\+.*",
     "Text of the landscape Table A8.1 pages as the second engine reads them: the running header and 'Table A8.1 "
     "continued' (dropped by the parser as running text), cells set vertically within the turned page and read "
     "backwards by pdfminer ('9002 2281 ne' for 'EN 1822: 2009', '36492 osi' for 'ISO 29463'), and values the "
     "upright reading groups in a merged row. The upright copy stores them readably.")
rule(r"who-trs1033-a2-hbel-cleaning", r"Appendix 1", r".*",
     "The worked example's table header ('API | PDE | MDD | Batch size | Shared equipment surface') is stored as its "
     "own table row, so the clause lacks it here; a piece of the side title ('WHO Technical Report Serie') cut by a "
     "table band is left in the clause; the rest of the side title is removed (0b).")
rule(r"who-trs1044-a2-sterile", r"4\.27|9\.15", r"\+grade maximum limits.*",
     "The cleanroom grade table inside the clause is stored as table rows, one per grade (Table 1 A ... D, fixed in "
     "0b); the check sees the table's words inside the clause's stretch because the second engine glues the footnote "
     "letters ('not specifieda'), so the rows do not hold the run word for word.")
rule(r"who-trs1044-a2-sterile", r"Table [127] (A|B|Grade)", r"-(specified specified|specified a|hours a)",
     "Footnote letters of the grade tables ('Not specified a', 'CFU/4 hours a') stored apart; pdfminer glues them to "
     "the word ('specifieda'), so the check misses the word. Values and grades are stored together (0b).")
rule(r"who-trs1044-a2-sterile", r"8\.(6|10)", r".*",
     "The small grade tables in 8.6 and 8.10 ('Grade | Operation' column headers) are stored as table rows without "
     "the header; in 8.10 a piece of the turned side title ('2 ... 104') cut by a table band is left in the clause.")
rule(r"who-trs1052-a4-qc-labs", r"Appendix 1", r".*",
     "Side title set vertically (read character by character, 'o t e c h r e p o r t ...') next to the list "
     "headings ('First stage laboratory (continued)', 'Optional items', 'Quantity'), which are stored as table rows "
     "of the equipment lists, not in the section text.")
rule(r"who-trs1052-a4-qc-labs", r"Appendix 3 8", r"\+test solution",
     "'Test solution' is a cell of Table 1 stored as its own row; the turned side title that was stored backwards in "
     "this clause is removed (0b).")
rule(r"who-trs1060-a3-excipients", r"Appendix 1 7\.2 #2", r"-x 3 table continued wh table continued",
     "Remnants of the turned running title ('Annex 3', 'WHO ...') and the 'Table continued' captions on the "
     "risk-statement table pages; the running header itself is now dropped (0b). No requirement word.")
rule(r"who-trs981-a2-qrm", r"[1-5]( #2)?", r".*",
     "The likelihood and severity scales on page 28 are an unruled table whose rows start with 1-5; now that its "
     "text is readable (0b: glyph decoding) each row is stored as a numbered clause, with wrapped cells ('occur more "
     "/ than once a / year') in layout order. Same words, other order.")
rule(r"who-trs981-a2-qrm", r"page 3[01]", r"\+in table row: (fmea|22201 3042)",
     "Words printed in a QRM tool table row's band that belong to the neighbouring row or the source note "
     "('(FMEA)', the PQRI address '22201-3042'); stored in that row or note. Readable since 0b.")


def flat(text):
    return "".join(F.tokens(text))


def segments(d):
    out = {"+": [], "-": []}
    for part in d.split(" | "):
        out[part[0]].append(part[1:].split())
    return out


def verify(f):
    """{(ref, discrepancy): verdict} for the flags of one source: 'order' (order or place only), 'footnote'
    (a line-start or small number), 'elsewhere' (uncovered text stored in another clause), or None."""
    clauses = [json.loads(l) for l in open(F.CLAUSES / (f[:-4] + '.jsonl'))]
    by_ref = {c['ref']: c for c in clauses}
    pages, _ = F.second_reading(F.OFFICIAL / f)
    store = [flat(c['text']) for c in clauses]
    out = {}
    for c in doc['sources'][f]['flagged']:
        d, verdict = c['discrepancy'], None
        seg = segments(d)
        if c['kind'] == 'uncovered':
            if all(len(flat(" ".join(s))) >= 8 and any(flat(" ".join(s)) in t for t in store) for s in seg['+']):
                verdict = 'elsewhere'
        else:
            cl = by_ref[c['ref']]
            near = range(max(cl['page_start'] - 2, 0), min(cl['page_end'] + 1, len(pages)))
            page_text = "".join("".join(pages[p][0]) for p in near)
            starts = set().union(*[F.page_parts(pages[p])[2] for p in near])
            small = {pages[p][0][k] for p in near for k in F.page_parts(pages[p])[1]}
            toks = [t for p in near for t in pages[p][0]]
            minus_ok = all(k and re.fullmatch(r"\d+(\.\d+)?|[a-zμ]{1,3}", toks[k - 1])
                           for k, t in enumerate(toks) if t == "−")
            if seg['+'] and not seg['-'] and all(s == ["−"] for s in seg['+']) and minus_ok:
                verdict = 'exponent'
            elif seg['+'] and not seg['-'] and all(len(s) == 1 and re.fullmatch(r"\d{1,3}", s[0])
                                                  and (s[0] in starts or s[0] in small) for s in seg['+']):
                verdict = 'footnote'
            else:
                own = [t for i, t in enumerate(store) if clauses[i]['ref'] != c['ref']]
                ok_minus = all(len(s) >= 3 and len(flat(" ".join(s))) >= 12 and flat(" ".join(s)) in page_text
                               for s in seg['-'])
                ok_plus = all(len(s) >= 3 and len(flat(" ".join(s))) >= 12
                              and (any(flat(" ".join(s)) in t for t in own) or flat(" ".join(s)) in store[clauses.index(cl)])
                              for s in seg['+'])
                if ok_minus and ok_plus:
                    verdict = 'order'
        out[(c['ref'], d)] = verdict
    return f, out


with ProcessPoolExecutor(4) as pool:
    VERIFIED = dict(pool.map(verify, list(doc['sources'])))

AUTO = {
    'order': "Order or place only (verified mechanically): every stored word run of this discrepancy is printed on "
             "the clause's pages, and every page run it lacks is stored word for word (in this clause or another), "
             "so no word is lost or added; the engines read table cells, columns or figure labels in different orders.",
    'footnote': "A footnote reference number (verified: it starts a line or is printed small on the clause's pages) "
                "that the parser drops with the footnote mark; no regulation word changes.",
    'exponent': "Exponent minus (verified: every minus sign on the clause's pages follows a number or a unit, as "
                "in '10⁻⁶' or 'mg⁻¹'): the stored text has poppler's rendering of the superscript without the sign "
                "('10-6' or '106'). Known superscript limitation (0b: keep superscripts as '10^-6').",
    'elsewhere': "Text read outside any clause's stretch that is stored word for word in another clause of the "
                 "document (verified mechanically): a running title, table caption or text read in another order.",
}

rows = []
unmatched = []
for f, s in doc['sources'].items():
    for c in s['flagged']:
        auto = VERIFIED[f].get((c['ref'], c['discrepancy']))
        if auto:
            rows.append((f, c['ref'], c['discrepancy'], AUTO[auto]))
            continue
        for src, ref, disc, reason in R:
            if src.search(f) and ref.fullmatch(c['ref']) and disc.fullmatch(c['discrepancy']):
                rows.append((f, c['ref'], c['discrepancy'], reason))
                break
        else:
            unmatched.append((f, c['ref'], c['kind'], c['discrepancy']))
with open(f'{ROOT}/library/fidelity-explanations.csv', 'w', newline='', encoding='utf-8') as out:
    w = csv.writer(out)
    w.writerow(['source', 'ref', 'discrepancy', 'reason'])
    w.writerows(rows)
print(len(rows), 'explained,', len(unmatched), 'unmatched', file=sys.stderr)
for u in unmatched:
    print('\t'.join(u)[:230])
