# Table Transformer trial: verdicts per page (D41, D43)

Grids: `grids.json` (`python3 tools/parse/tatr.py run`, pinned models, CPU). Side by side: `trial.md`
(`tatr.py compare`). A page is adopted (`tatr.ADOPTED`) only where the model's grid is right on review, holds every
word of the table once (lost 0, twice 0), and the fidelity check is no worse.

| Page(s) | tables.py | Model | Verdict |
|---|---|---|---|
| WHO TRS 1044 A2 p17; EU Annex 1 p13, 14, 45, 47; PE 009 Annex 1 p20, 21 (grade tables) | right (since D42) | the same rows and columns; the merged "No growth" cell sits under another empty column on EU p14, p47 and PE 009 p20 (empty cells are not stored, so the stored text is the same) | keep tables.py (no gain) |
| **WHO TRS 1044 A2 p19** (Table 2 microbial limits) | header row only; grades A-D stored inside 4.31 without columns | 5 rows x 4 columns, right; grade A's "No growth" (printed across the three limit columns) falls in one column, as no spanning cell is found; stored as "A \| No growth", as before inside 4.31 | **adopted** |
| EU Annex 1 p22 | 3 x 2, right | a third, empty column | keep tables.py |
| EU Annex 1 p23 | right | 28 words in no cell | keep tables.py |
| **ICH Q3C p11** (Table 1, Class 1 solvents) | no table (unruled; stored as text lines) | 6 x 3, right | **adopted** |
| ICH Q3C p12-13 (Table 2) | no table | p12 right, but the continuation on p13 is detected at 0.36 only, so half the table would be rows and half text | not adopted |
| ICH Q3C p13 (Table 3) | no table | a list printed in two columns, read as rows that pair unrelated solvents | not adopted |
| ICH Q3C p17-18 (Appendix 1) | no table | rows misplaced: "Propan-2-one" (Acetone) put with Acetonitrile, "Vinylidene chloride" (1,1-) with 1,2-Dichloroethene | not adopted (worse than text) |
| CDSCO circular p45-66 | section-heading rows ("21 Sanitation:") continue the row above (0b defect) | heading rows right, but the right-hand columns fall outside the model's table, and on p48-49 the top row is cut (1-4 words in no cell) | not adopted; left to a rule in tables.py (0b list) |
| CDSCO circular p116, 119, 120 | right (row 27.4 fixed in D42) | fewer rows, words lost or in two cells | keep tables.py |
| WHO TRS 1010 A8 p15-17 (Table A8.1, landscape) | words in two overlapping cells ("EU 6 EU 5 EU 4 EU 3") | a vertically merged cell split over rows ("EN", "779:", "M5 2012"), a column dropped | neither right; keep tables.py (0b defect stays listed) |
| FDA CP 7346.832 p53-54 | the p53-54 row 'Sterility control and assurance' not found (0b defect) | 58 and 124 words in no cell | not adopted |
| Former TEXT LOST pages: CP 7346.832 p44, CP 7356.002 p41, nitrosamine 2024 p41 | no table (D42 rule) | p44: a 2 x 1 "table" losing 6 words; the other two: no table | keep the rule; the model agrees on 2 of 3 |

Result: the model beats tables.py on 2 of 34 trial pages; on 7 it gives the same stored rows; on the rest it is worse or
neither is right. It is kept only for the 2 pages, from the committed grids.
