// AUDIT LAYER calibration with Claude Code agents (owner 19 Nov: "do without the api to find what is working").
// Same system prompt, rules, block input and JSON schema as the API batch (layer.mjs); only the runner differs.
//
//   node agentio.mjs draft-inputs <roundDir> <ids.json> <nAgents>   -> <roundDir>/draft/aN/{task.md}, key.json, build-report.json
//   node agentio.mjs draft-gather <roundDir>                         -> <roundDir>/draft/raw.json  (then: python3 -I assemble.py <roundDir>/draft)
//   node agentio.mjs check-inputs <roundDir> <nAgents>               -> <roundDir>/check/aN/task.md (blind: units + points only)
//   node agentio.mjs check-gather <roundDir>                         -> <roundDir>/check/raw.json  (then: python3 -I score.py <roundDir>/check <roundDir>/draft)
// Agent output file: <aN>/out.json = {"blocks": {"<block id>": {<schema answer>, "last5": "<last 5 words of the block input>"}}}
// The last5 echo (tail rule) proves the agent read each block to its end; a missing/false echo = error for that block.
import fs from "fs";
import { DRAFT_RULES, DRAFT_SCHEMA, blockText, CHECK_BLOCK_RULES, CHECK_BLOCK_SCHEMA, checkBlockText } from "./layer.mjs";

const HERE = "/root/audit-admin/audit-layer";
const J = (p) => JSON.parse(fs.readFileSync(p, "utf8"));
const W = (s) => String(s || "").toLowerCase().replace(/[^a-z0-9 ]/g, " ").split(/\s+/).filter(Boolean);
// unit-id / mark prefixes ("  EU C4 4.23#6 [DUTY] ") are labels, not text: stripped before the tail comparison
const strip = (text) => String(text).replace(/^ {2}[^\n]*?#\d+ (\[(DUTY|INFO)\] )?/gm, " ");
const tail1 = (echo, t) => { const e = W(echo); return e.length >= 3 && e.length <= 20 && e.join(" ") === t.slice(-e.length).join(" "); };
const tailOk = (echo, text) => tail1(echo, W(strip(text))) || tail1(echo, W(text));   // labels stripped, or raw text
const blocks = () => Object.fromEntries(J(`${HERE}/blocks.json`).blocks.map((b) => [b.id, b]));
const nduty = (b) => b.items.reduce((s, it) => s + it.units.filter((u) => u.mark === "duty").length, 0);

function split(ids, n, weight) {          // balanced by weight, order kept inside each agent
  const bins = Array.from({ length: n }, () => ({ ids: [], w: 0 }));
  for (const id of [...ids].sort((a, b) => weight(b) - weight(a))) { const t = bins.reduce((m, x) => (x.w < m.w ? x : m)); t.ids.push(id); t.w += weight(id); }
  return bins.map((b) => b.ids.sort());
}
function task(kind, rules, schema, parts) {
  return [`# ${kind} task (GMP audit layer calibration)`, "",
    "Work ONLY from this file. Do not open any other file except writing your answer file named below.",
    "For EACH block below, answer exactly as the SYSTEM PROMPT says, as JSON matching the SCHEMA, and add \"last5\": the last 5 words of that block's input text (as you read them).",
    "Write ONE file: out.json in the same folder as this task file: {\"blocks\": {\"<block id>\": {...answer..., \"last5\": \"...\"}}}. Answer EVERY block.",
    "", "## SYSTEM PROMPT", "", rules, "", "## SCHEMA (per block answer)", "", "```json", JSON.stringify(schema), "```", "",
    ...parts.flatMap(([id, text]) => [`## BLOCK ${id}`, "", "```text", text, "```", ""])].join("\n");
}

function draftInputs(rd, idsFile, n) {
  const B = blocks(), ids = J(idsFile);
  const dir = `${rd}/draft`; fs.mkdirSync(dir, { recursive: true });
  const bins = split(ids, n, (id) => nduty(B[id]) + 2);
  bins.forEach((bin, i) => {
    fs.mkdirSync(`${dir}/a${i + 1}`, { recursive: true });
    fs.writeFileSync(`${dir}/a${i + 1}/task.md`, task("DRAFT", DRAFT_RULES, DRAFT_SCHEMA, bin.map((id) => [id, blockText(B[id])])));
  });
  fs.writeFileSync(`${dir}/key.json`, JSON.stringify(ids.map((id) => ({ id })), null, 1));
  fs.writeFileSync(`${dir}/build-report.json`, JSON.stringify({ kind: "draft", runner: "claude-code-agents", agents: bins }, null, 1));
  bins.forEach((b, i) => console.log(`a${i + 1}: ${b.length} blocks, ${b.reduce((s, id) => s + nduty(B[id]), 0)} duty units`));
}
function gather(dir, inputText) {
  const rep = J(`${dir}/build-report.json`), results = [];
  rep.agents.forEach((bin, i) => {
    const f = `${dir}/a${i + 1}/out.json`;
    const out = fs.existsSync(f) ? J(f).blocks || {} : {};
    for (const id of bin) {
      const d = out[id];
      if (!d) { results.push({ id, error: "no answer" }); continue; }
      const { last5, ...data } = d;
      if (!tailOk(last5, inputText(id))) { results.push({ id, error: `last5 not a tail: "${last5}"`, data }); continue; }
      results.push({ id, data });
    }
  });
  fs.writeFileSync(`${dir}/raw.json`, JSON.stringify({ usage: { runner: "claude-code-agents" }, results }, null, 1));
  console.log(`${results.length} blocks, errors ${results.filter((r) => r.error).length}`, results.filter((r) => r.error).map((r) => `${r.id}: ${r.error}`));
}
const draftGather = (rd) => { const B = blocks(); gather(`${rd}/draft`, (id) => blockText(B[id])); };

function checkParts(rd) {
  const B = blocks(), D = J(`${rd}/draft/drafts.json`), by = new Map(), np = new Map();
  for (const p of D.points) if (!(p.problems || []).some((x) => x.startsWith("A1"))) { if (!by.has(p.block)) by.set(p.block, []); by.get(p.block).push(p); }
  for (const x of D.no_point || []) { if (!np.has(x.block)) np.set(x.block, []); np.get(x.block).push(x); if (!by.has(x.block)) by.set(x.block, []); }
  return [...by.keys()].sort().map((id) => ({ id, pts: by.get(id), np: np.get(id) || [], text: checkBlockText(B[id], by.get(id), np.get(id) || []) }));
}
function checkInputs(rd, n) {
  const parts = checkParts(rd), dir = `${rd}/check`; fs.mkdirSync(dir, { recursive: true });
  const P = Object.fromEntries(parts.map((p) => [p.id, p]));
  const bins = split(parts.map((p) => p.id), n, (id) => P[id].pts.length + P[id].np.length + 2);
  bins.forEach((bin, i) => {
    fs.mkdirSync(`${dir}/a${i + 1}`, { recursive: true });
    fs.writeFileSync(`${dir}/a${i + 1}/task.md`, task("CHECK", CHECK_BLOCK_RULES, CHECK_BLOCK_SCHEMA, bin.map((id) => [id, P[id].text])));
  });
  fs.writeFileSync(`${dir}/key.json`, JSON.stringify(parts.map((p) => ({ id: p.id, points: p.pts.map((x) => x.id), no_point: p.np.map((x) => x.unit) })), null, 1));
  fs.writeFileSync(`${dir}/build-report.json`, JSON.stringify({ kind: "checkblock", runner: "claude-code-agents", agents: bins }, null, 1));
  bins.forEach((b, i) => console.log(`a${i + 1}: ${b.length} blocks, ${b.reduce((s, id) => s + P[id].pts.length, 0)} points`));
}
const checkGather = (rd) => { const P = Object.fromEntries(checkParts(rd).map((p) => [p.id, p])); gather(`${rd}/check`, (id) => P[id].text); };

const [mode, rd, a, b] = process.argv.slice(2);
const R = rd && (rd.startsWith("/") ? rd : `${HERE}/${rd}`);
({ "draft-inputs": () => draftInputs(R, a, Number(b || 4)), "draft-gather": () => draftGather(R),
   "check-inputs": () => checkInputs(R, Number(a || 4)), "check-gather": () => checkGather(R) }[mode] || (() => console.log("modes: draft-inputs, draft-gather, check-inputs, check-gather")))();
