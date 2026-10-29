# Decisions

Small decisions taken by the build session, recorded so the owner can overrule any of them.
Owner decisions from the 29 October 2026 brief are summarised in `docs/00-brief.md`.

| # | Date | Decision | Why |
|---|---|---|---|
| D1 | 2026-10-29 | Official PDFs are stored in the private repo under `sources/official/` (about 17 MB) and fingerprinted by sha256 in `sources/inventory.csv`; CI fails if one changes. | Layer 1 needs the exact source bytes. A changed text must trigger re-verification. |
| D2 | 2026-10-29 | FDA regulations come from the eCFR XML API (dated snapshot), not a PDF. | The XML carries section and paragraph structure, so clause references can be checked deterministically. |
| D3 | 2026-10-29 | The PIC/S version is PE 009-18 (24 Sept 2026), the current one. EU and PIC/S are mapped separately and never assumed identical. | PE 009-18 is newer than several EU chapters, so their wording can differ. |
| D4 | 2026-10-29 | Library tooling is Python 3, standard library only, plus poppler-utils. | Simple, no dependency churn. The app stack is decided in deliverable (b)/(c). |
| D5 | 2026-10-29 | Files behind a bot check are requested from the owner, never fetched by working around the check. | Respect the publishers' access controls. |
| D6 | 2026-10-29 | Plant-type codes: OSD, LIQ (oral liquids), SEMI (gels/semisolids), INJ (sterile injectables), API; ALL = every type. | Short tags for the catalogue and, later, the app filter. |
