# Working in this repository
- Read `HANDOVER.md` first, then `docs/00-brief.md`. Update `HANDOVER.md` at every milestone and before a session ends.
- Record small decisions in `docs/decisions.md`. Ask the owner only for decisions that are genuinely theirs.
- Never edit or replace files in `sources/official/` without re-running `tools/inventory.py write` and noting why in decisions.
- Quotes from PIC/S, WHO and ICH stay internal; nothing customer-facing may contain quotes or clause numbers (option A).
- Working sessions read PDFs as text (`pdftotext -layout` + grep), never as page images. By owner decision (D45), the drafting and verifier agents, and the vision check, receive rendered page images together with the page's text layer.
- Work on branches; tests with every feature; CI green before merge; commit trailers carry no model name.
