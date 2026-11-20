# Notes from session audit-admin-db (the API proof run), for the audit-layer build (19 Nov 2026)

Read the lead's brief (HANDOVER.md here) first. These are practical lessons from api-proof/ (read-only for you; copy
code into this folder, don't edit it there). Full story: api-proof/REPORT-FINAL.md, api-proof/HANDOVER.md,
api-proof/FULL-RUN.md.

## Reusable code: api-proof/full.mjs (Node, @anthropic-ai/sdk in api-proof/node_modules)
- client(): reads the key from /root/audit-admin/.secrets/anthropic.env; never print or log it.
- params(system, content, schema): model + max_tokens 16000 + output_config {effort, format: json_schema}. Structured
  output works in batches. For Sonnet use model "claude-sonnet-5-5" (check the effort default; set it explicitly).
- splitBatches(): <= 2000 requests and <= 200 MB per batch (API limit 256 MB; images make batches big).
- submit / collect pattern: build writes batch-NN.jsonl + key.json + build-report.json (with inputs sha256 of merged/);
  submit refuses without --yes, refuses double submit (batches.json), refuses if merged/ changed after the build;
  collect polls, scores, writes results.json. FULL_OUT=<folder> switches the output folder.
- count_tokens on every request (free) gives an exact input estimate; output: use measured usage (Opus effort high
  averaged ~205-260 output tokens per short structured answer).
- Batch price = 50 % (Opus 5.5 4/20 US$ per MTok -> 2/10; Sonnet 5.5 2/10 -> 1/5).

## How batches get submitted
This session's permission check BLOCKS "node ... submit --yes" (it spends money). The OWNER runs the submit himself
over SSH, e.g. `cd /root/audit-admin/audit-layer && FULL_OUT=<dir> node <script> submit --yes`. Give the lead the
exact command + estimate; never try to work around the block.

## Lessons that cost money to learn
- Ask checkers to echo the last words of each text, but compare with a TAIL rule (3-8 words ending in the text's last
  words); exact-5 fails on harmless miscounts (2217 false alarms in the first run).
- A prompt hint added midway splits standards between rounds: give every round the SAME prompt.
- One-opinion zero-error samples fail on genuinely borderline cases (~2-5 %); decide the borderline rule up front.
- Source evidence (PDF word boxes, 200+ dpi crops, both readers) beats an API opinion. 90 dpi page images caused
  misreads; use 200 dpi crops (2 per page, under the ~1568 px edge) + the PDF text layer as a reading aid.
- Coordinate with audit-admin-dd before building: any rebuild of merged/ after your build trips the input guard.
- Final marks: merged/checkpoints.json "mark" = final (duty 8510 / background 2118; owner rule: duty only if every
  API opinion said duty). code_mark / code_rule are the program's original marks.
