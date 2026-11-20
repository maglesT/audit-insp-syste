// AUDIT LAYER batches (session audit-layer-65, 19 Nov 2026; brief: HANDOVER.md; owner: Opus only).
// Pattern copied from api-proof/full.mjs (key handling, batch split, submit guards, collect).
//
//   OUT=<dir> node layer.mjs draft-build [calib|all]   one DRAFT request per block (blocks.json) -> <dir>/batch-NN.jsonl
//   OUT=<dir> node layer.mjs check-build <draftDir>    one blind CHECK request per drafted point (from <draftDir>/drafts.json)
//   OUT=<dir> node layer.mjs check-block-build <draftDir> [ids.json]  per-BLOCK check (full run); ids = re-check only these
//   OUT=<dir> node layer.mjs repair-build <draftDir> <checkDir|->      re-draft failed points / no_point / uncovered per block
//   OUT=<dir> node layer.mjs sample-build <draftDir> [sample.json]   final proof: one request per sampled point / no_point
//   OUT=<sampleDir>/opinions node layer.mjs opinion-build <sampleDir>   2 more opinions per sample FAIL (2-of-3 rule)
//   OUT=<dir> node layer.mjs submit --yes              OWNER ONLY (over SSH): sends the batch files once
//   OUT=<dir> node layer.mjs collect                   polls; when ended writes drafts.json (draft) or checks.json (check)
//
// Input guard: build stores sha256 of blocks.json (+ the draft file for checks); submit refuses if it changed.
// The API key is read from /root/audit-admin/.secrets/anthropic.env and is never printed or written anywhere.
// Only Schedule M / US FDA / EU text is sent (blocks.json has no WHO / PIC/S text).
import fs from "fs";
import crypto from "crypto";
import Anthropic from "@anthropic-ai/sdk";

const ROOT = "/root/audit-admin";
const HERE = `${ROOT}/audit-layer`;
const OUT = process.env.OUT ? (process.env.OUT.startsWith("/") ? process.env.OUT : `${HERE}/${process.env.OUT}`) : null;
// Models (owner 19 Nov): checks always claude-opus-5-5; drafts / repairs use DRAFT_MODEL (default Opus; the owner's
// test: DRAFT_MODEL=claude-fable-5-2). Fable 5.2: thinking always on (no "thinking" param sent), effort high, no
// prefill, no forced tool choice; a "refusal" stop_reason is counted and the block is re-run (no fallback model, so the
// comparison stays clean).
const CHECK_MODEL = "claude-opus-5-5", EFFORT = "high";
const DRAFT_MODEL = process.env.DRAFT_MODEL || "claude-opus-5-5";
const PRICES = { "claude-opus-5-5": [4, 20], "claude-fable-5-2": [8, 40] };   // US$ / MTok (standard; batch -50 %)
if (!PRICES[DRAFT_MODEL]) throw new Error(`unknown DRAFT_MODEL ${DRAFT_MODEL}`);
const MAX_REQ = 2000, MAX_BYTES = 200 * 1024 * 1024;
const BATCH = 0.5;      // batch discount 50 %
const ESTIMATE_LIMIT = 40;
const J = (p) => JSON.parse(fs.readFileSync(p, "utf8"));
const sha = (p) => crypto.createHash("sha256").update(fs.readFileSync(p)).digest("hex");
function client() {
  const env = fs.readFileSync(`${ROOT}/.secrets/anthropic.env`, "utf8");
  const m = env.match(/^ANTHROPIC_API_KEY=(.+)$/m);
  if (!m) throw new Error("ANTHROPIC_API_KEY line not found");
  return new Anthropic({ apiKey: m[1].trim() });
}
function seeded(seed) { let x = seed >>> 0; return () => ((x = (x * 1664525 + 1013904223) >>> 0) / 4294967296); }

// ---------------- DRAFT ----------------
export const DRAFT_RULES = `You write AUDIT POINTS for a GMP audit checklist used by auditors in pharmaceutical plants.
You get one block of regulation clauses (ITEMS) from ONE section of ONE regulation. Each item is split into numbered sentence UNITS:
  [DUTY] = a requirement the plant must meet (or a recommendation, if it says "should") -> must be covered by audit points;
  [INFO] = background (scope, definition, explanation) -> context only, never the content of a point.
Write audit points that together cover EVERY [DUTY] unit (each DUTY unit in at least one point's "units").

Each point:
- question: ONE short question an auditor answers by looking at evidence, in your OWN plain words (start with Is / Are / Does / Has / Have ...).
- verify: one or two sentences starting "Verify that ..." stating exactly what must be true, in your own words.
- evidence: 1-4 places the auditor looks: type document (procedure, specification, plan, file), record (logs, reports, batch records, data), observation (what is seen on the shop floor / in the lab), or interview (asking staff); "what" = a few words.
- units: the ids of the DUTY units this point checks (e.g. "SchM-I-6.3#2").
- grade_hint: the usual grade of a finding if this point fails: critical (can directly put patients at risk: sterility, mix-ups, wrong product or strength, contamination, falsified data), major (significant GMP failure), other (minor / administrative).

STRICT RULES (an independent check rejects any point that breaks them):
R1 NO MORE: question, verify and evidence say nothing that is not in the covered units: no added numbers, limits, frequencies, timings, roles, documents, conditions, methods, scope (e.g. "the whole site" for "premises used for X") or examples, and no narrower method (e.g. "interlocked" for "synchronized").
R1e EVIDENCE = only where THIS requirement itself can be seen. If a unit says what a document must contain, the evidence is that document (no shop-floor observation, no batch records, no staff interview about practice). Never name evidence of something the unit does not require: no qualification / validation / calibration / approval / signature / follow-up / mock-recall / inventory / check records unless the unit requires that thing. Neutral wording is fine ("records showing ...", "procedure or records showing ...").
R2 NO LESS: verify keeps every condition, scope word ("immediate", "where possible", "during the validation activity", "to be used"), exception, number, limit, list entry, negation and "where/when/unless" of the covered units, every softening or limiting qualifier ("preferably", "as far as possible", "where possible", "normally", "generally"), and every cross-reference or pointer as written (e.g. "under § 314.70(b)", "in accordance with § 211.84", "Article 81 of Directive 2001/83/EC", "(see Section 7.2)", "described in paragraph (b)(1) of this section"). If a unit has several duties (e.g. "shall be documented ... and there shall be a follow-up programme"), verify states each one. NEVER split one unit between points: a point that lists a unit verifies ALL of that unit's content (put a unit with several duties in one point that states them all). When a point covers several units, check that EACH unit's every duty is in verify; if that makes the point long, split by units, not inside a unit. Never use content of a unit the point does not list. Do not generalise ("appropriate", "relevant", "as required") where the unit is specific.
R3 MODALITY: "must / shall / is required" stays a duty. "should" / "is recommended" is a RECOMMENDATION: do not put recommendation units and duty units in the same point; set "modality" to "should" for a recommendation point and "must" otherwise; for a should-point end the question with "(recommended)?" and write "Verify that ... (recommended)." A should-point never uses "must", "shall", "required" or "as required" (they would harden it). A list entry takes the modality of its lead-in (e.g. under "As a minimum, the following should be documented:" every entry is "should").
R3p PERMISSION / BENEFIT: a unit that only permits ("may", "can", "could be accepted", "consideration can be given"), or only states a benefit or a fact, is not a duty: do not turn it into a requirement or a restriction. If it carries a checkable condition (e.g. "X could be accepted if adequately justified"), write the point as that condition with modality "should": "Where X is used, is it <condition> (recommended)?" / "Where X is used, verify that <condition> (recommended)."; otherwise put it in no_point (reason "permission only" / "states a benefit"). "may" (a permission) is not a duty: mention it only as an allowed option inside verify if needed.
R4 GROUPING: put units in one point only when the SAME evidence checks them and the point stays short (usually 1-4 units). Units of different items of this block may share a point. Never merge different requirements just to shorten the list.
R5 OWN WORDS: the QUESTION must be rephrased, not the unit sentence turned into a question (no run of 10 or more words from a unit; ask about the evidence, e.g. "Do records show that ...?"). The verify sentence may keep the regulation's exact terms. Never use wording of other published checklists or aide-memoires (PIC/S, CDSCO, APIC, WHO); write fresh.
R6 Plain, short English (Indian plant auditors). No references or clause numbers inside question/verify.
R7 [INFO] units may help you understand a DUTY unit; never write a point only for an INFO unit; never list INFO ids in "units".
R8 NO FORCING (owner rule): if a DUTY unit cannot be turned into a clean, answerable audit point without adding or dropping content (e.g. a pure general aim, a duty of an authority, a statement no auditor can verify by evidence), do NOT force it: put it in "no_point" as {unit, reason} (reason: a few words). Use this rarely; a duty that can be checked by any document, record, observation or interview gets a point. A requirement that something be agreed, approved or authorised by an authority gets a point (checked from the approval / authorisation documents on file). Every DUTY unit must be in at least one point OR in no_point.`;

export const DRAFT_SCHEMA = {
  type: "object",
  properties: {
    points: {
      type: "array",
      items: {
        type: "object",
        properties: {
          units: { type: "array", items: { type: "string" } },
          question: { type: "string" },
          verify: { type: "string" },
          evidence: {
            type: "array",
            items: {
              type: "object",
              properties: { type: { type: "string", enum: ["document", "record", "observation", "interview"] }, what: { type: "string" } },
              required: ["type", "what"], additionalProperties: false,
            },
          },
          grade_hint: { type: "string", enum: ["critical", "major", "other"] },
          modality: { type: "string", enum: ["must", "should"] },
        },
        required: ["units", "question", "verify", "evidence", "grade_hint", "modality"], additionalProperties: false,
      },
    },
    no_point: {
      type: "array",
      items: { type: "object", properties: { unit: { type: "string" }, reason: { type: "string" } }, required: ["unit", "reason"], additionalProperties: false },
    },
  },
  required: ["points", "no_point"], additionalProperties: false,
};

const tableText = (t) => [`TABLE ${t.id}${t.title ? ` "${t.title}"` : ""}:`,
  ...(t.header || []).map((r) => "  | " + r.join(" | ")), ...(t.rows || []).map((r) => "  | " + r.join(" | "))].join("\n");

export function blockText(b) {
  const L = [`REGULATION: ${b.regulator} (${b.part})`, `SECTION: ${b.path.join(" > ") || "(none)"}`, `PLANT AREA: ${b.area}`, ""];
  for (const it of b.items) {
    L.push(`ITEM ${it.id} (${it.ref})${it.title ? ` TITLE: ${it.title}` : ""}`);
    if (it.lead) L.push(`  LEAD-IN: ${it.lead}`);
    for (const u of it.units) L.push(`  ${u.uid} [${u.mark === "duty" ? "DUTY" : "INFO"}] ${u.text}`);
    for (const t of it.tables) L.push(tableText(t));
    L.push("");
  }
  return L.join("\n");
}

const params = (system, text, schema, max_tokens = 32000, model = CHECK_MODEL) => ({
  model, max_tokens, system,
  output_config: { effort: EFFORT, format: { type: "json_schema", schema } },
  messages: [{ role: "user", content: [{ type: "text", text }] }],
});

function calibPick(blocks) {
  // 50 blocks, seed 20261119: 18 Schedule M, 8 FDA, 24 EU, random within regulator, plus the 2 largest blocks
  const rnd = seeded(20261119), want = { "Schedule M": 18, "US FDA": 8, EU: 24 };
  const big = [...blocks].sort((a, b) => nduty(b) - nduty(a)).slice(0, 2).map((b) => b.id);
  const pick = new Set(big);
  for (const [reg, n] of Object.entries(want)) {
    const pool = blocks.filter((b) => b.regulator === reg && !pick.has(b.id));
    const have = () => blocks.filter((b) => b.regulator === reg && pick.has(b.id)).length;
    while (have() < n && pool.length) pick.add(pool.splice(Math.floor(rnd() * pool.length), 1)[0].id);
  }
  return blocks.filter((b) => pick.has(b.id));
}
const nduty = (b) => b.items.reduce((s, it) => s + it.units.filter((u) => u.mark === "duty").length, 0);

// ---------------- CHECK ----------------
export const CHECK_RULES = `You are an independent, strict checker of ONE audit point of a GMP audit checklist.
You get the audit point (question, verify, evidence) and the regulation UNITS it claims to check (each shown inside its whole clause for context).
Judge four things; answer PASS or FAIL for each, with a short reason naming the exact words when FAIL:
1 no_more: the question, verify and evidence say NOTHING the units do not say: no added number, limit, frequency, timing, role, document, condition, method, example or stricter/looser modality. Evidence is only where to look; it FAILS if it implies an extra requirement (e.g. "monthly", "approved by QA" not in the units). Neutral audit words ("records", "procedure or records showing") are fine. A "should" unit must stay a recommendation (marked "(recommended)"); a "must/shall" unit must not be weakened to a recommendation.
2 no_less: verify (with the question) keeps EVERY requirement of every listed unit: each condition, scope word, exception, number, limit, list entry, negation and where/when/unless. Plain paraphrase is fine; dropping or generalising content FAILS.
3 answerable: an auditor can answer the question YES or NO by looking at the listed evidence.
4 own_words: the QUESTION is not a copy of a unit sentence (technical terms are fine); FAIL only if the question copies a whole unit sentence word for word. The verify sentence MAY keep the regulation's own words (allowed by the owner).
Look explicitly for these known error classes: (a) evidence that implies an extra duty (e.g. shop-floor observation or batch records when the unit only says what a document must contain; qualification, approval, signature, follow-up, mock-recall or inventory records the unit does not require); (b) a permission or benefit ("may", "can", "could be accepted", "consideration can be given", "will help") turned into a duty or a restriction; (c) added, wider or narrower scope or method (e.g. "the site" for "premises used for X", "interlocked" for "synchronized"); (d) a dropped cross-reference or pointer (e.g. "under § 314.70(b)", "(see Section 7.2)"), a dropped scope word or qualifier (e.g. "immediate", "where possible", "preferably", "as far as possible"), or a dropped second duty of a unit (a unit split between points: each point listing it must verify all of it); (e) content taken from a unit the point does not list.
Agreed borderline rules (do not FAIL these): a conditional permission ("X could be accepted if adequately justified") written as "Where X is used, ... justified (recommended)" is correct; a requirement for an authority's agreement or approval checked from the approval documents on file is a valid point; neutral evidence words ("records showing ...", "procedure or records showing ...") add nothing.
Context sentences of the clause that are NOT listed units are not required in the point; the SECTION heading and item TITLE / LEAD-IN may be used by the point. When in doubt, FAIL and explain. reason: "" when PASS; when FAIL one short sentence naming the exact words.`;
const CHECK_SCHEMA = {
  type: "object",
  properties: Object.fromEntries(["no_more", "no_less", "answerable", "own_words"].map((k) => [k, {
    type: "object", properties: { result: { type: "string", enum: ["PASS", "FAIL"] }, reason: { type: "string" } },
    required: ["result", "reason"], additionalProperties: false,
  }])),
  required: ["no_more", "no_less", "answerable", "own_words"], additionalProperties: false,
};
function checkText(p, unitIdx) {
  const L = ["AUDIT POINT", `question: ${p.question}`, `verify: ${p.verify}`, "evidence:",
    ...p.evidence.map((e) => `  - ${e.type}: ${e.what}`), "", "UNITS IT CLAIMS TO CHECK (each inside its whole clause):"];
  const byItem = new Map();
  for (const uid of p.units) { const u = unitIdx[uid]; if (!byItem.has(u.item.id)) byItem.set(u.item.id, { item: u.item, ids: [] }); byItem.get(u.item.id).ids.push(uid); }
  for (const { item, ids } of byItem.values()) {
    L.push("", `CLAUSE ${item.ref}${item.title ? ` (title: ${item.title})` : ""}`);
    if (item.lead) L.push(`  lead-in: ${item.lead}`);
    for (const u of item.units) L.push(`  ${ids.includes(u.uid) ? ">> LISTED UNIT" : "   context    "}: ${u.text}`);
    for (const t of item.tables) L.push(tableText(t));
  }
  return L.join("\n");
}

// per-BLOCK check: all points of one block judged in one request (block text sent once). Same criteria as CHECK_RULES.
export const CHECK_BLOCK_RULES = CHECK_RULES.replace("ONE audit point", "EVERY audit point listed")
  .replace("You get the audit point (question, verify, evidence) and the regulation UNITS it claims to check (each shown inside its whole clause for context).",
    "You get a block of regulation clauses split into numbered UNITS, then a list of audit points; each point names the unit ids it claims to check. Judge EACH point on its own, only against ITS listed units (other units of the block are context).")
  + "\nAnswer every listed point once, in \"points\", with its id."
  + "\nThen judge every listed NOT-ACTIONABLE unit (the writer found no clean audit point for it): in \"no_point\" answer {unit, result, major, reason}. major = true if an inspector would likely raise a CRITICAL or MAJOR finding if this duty were not met. result: FAIL if major is true (owner: nothing major may be missed; it must be a point), or if a clean audit point could be written (say which); PASS if it is truly not checkable by any document, record, observation or interview (or a point would have to add or drop content) and it is not major.";
export const CHECK_BLOCK_SCHEMA = {
  type: "object",
  properties: { points: { type: "array", items: { type: "object",
    properties: { id: { type: "string" }, ...CHECK_SCHEMA.properties },
    required: ["id", ...CHECK_SCHEMA.required], additionalProperties: false } },
    no_point: { type: "array", items: { type: "object",
      properties: { unit: { type: "string" }, result: { type: "string", enum: ["PASS", "FAIL"] }, major: { type: "boolean" }, reason: { type: "string" } },
      required: ["unit", "result", "major", "reason"], additionalProperties: false } } },
  required: ["points", "no_point"], additionalProperties: false,
};
export function checkBlockText(b, pts, np = []) {
  const L = [blockText(b).replace(/ \[(DUTY|INFO)\]/g, ""), "AUDIT POINTS TO JUDGE:"];
  for (const p of pts) {
    L.push("", `POINT ${p.id}`, `  units: ${p.units.join(", ")}`, `  question: ${p.question}`, `  verify: ${p.verify}`, "  evidence:",
      ...p.evidence.map((e) => `    - ${e.type}: ${e.what}`));
  }
  L.push("", "NOT-ACTIONABLE UNITS TO JUDGE:", ...(np.length ? np.map((x) => `  ${x.unit}: writer's reason: ${x.reason}`) : ["  (none)"]));
  return L.join("\n");
}
async function checkBlockBuild() {
  const dd = process.argv[3]; if (!dd) throw new Error("check-block-build needs the draft folder");
  const D = J(`${dd}/drafts.json`), B = Object.fromEntries(J(`${HERE}/blocks.json`).blocks.map((b) => [b.id, b]));
  const by = new Map();
  const only = process.argv[4] ? new Set(J(process.argv[4])) : null;     // optional: re-check only these point ids / no_point units
  for (const p of D.points) if (!(p.problems || []).some((x) => x.startsWith("A1")) && (!only || only.has(p.id))) { if (!by.has(p.block)) by.set(p.block, []); by.get(p.block).push(p); }
  const reqs = [], key = [];
  const npBy = new Map();
  for (const x of (D.no_point || []).filter((x) => !only || only.has(x.unit))) { if (!npBy.has(x.block)) npBy.set(x.block, []); npBy.get(x.block).push(x); }
  for (const bid of npBy.keys()) if (!by.has(bid)) by.set(bid, []);
  for (const [bid, pts] of by) {
    const np = npBy.get(bid) || [];
    reqs.push({ custom_id: bid, params: params(CHECK_BLOCK_RULES, checkBlockText(B[bid], pts, np), CHECK_BLOCK_SCHEMA) });
    key.push({ id: bid, points: pts.map((p) => p.id), no_point: np.map((x) => x.unit) });
  }
  const per = Number(process.env.OUT_PER_CHECK || 400);
  await writeBuild("checkblock", reqs, key, { "blocks.json": sha(`${HERE}/blocks.json`), "drafts.json": sha(`${dd}/drafts.json`) },
    () => key.reduce((s, k) => s + 600 + per * k.points.length, 0));
}

// REPAIR: failed points of a block re-drafted with the checker's reason (same rules + schema as the draft).
export const REPAIR_RULES = DRAFT_RULES + `

REPAIR TASK: below the block you get audit points that FAILED an independent check, each with the reason, and possibly DUTY units that are not covered yet. Write NEW points (and no_point entries) that cover exactly these units: every unit of the failed points and every uncovered unit listed, each in at least one point or in no_point. Fix the stated problem; do not repeat it. The other points of the block are fine and are not shown.`;
export function repairText(b, failed, units) {
  const L = [blockText(b), "FAILED POINTS (rewrite these):"];
  for (const f of failed) L.push("", `units: ${f.units.join(", ")}`, `question: ${f.question}`, `verify: ${f.verify}`,
    `evidence: ${f.evidence.map((e) => `${e.type}: ${e.what}`).join("; ")}`, `CHECK RESULT: ${f.why}`);
  L.push("", "UNITS TO COVER (all of them, in points or no_point): " + units.join(", "));
  return L.join("\n");
}
async function repairBuild() {
  // repair-build <draftDir> <checkDir|-> : code problems (A2-A7), checker FAILs, failed no_point, uncovered units
  const dd = process.argv[3], cd = process.argv[4];
  const D = J(`${dd}/drafts.json`), B = Object.fromEntries(J(`${HERE}/blocks.json`).blocks.map((b) => [b.id, b]));
  const C = cd && cd !== "-" ? J(`${cd}/checks.json`) : { fails: [], no_point_fails: [] };
  const why = new Map();
  for (const p of D.points) if ((p.problems || []).length) why.set(p.id, "code check: " + p.problems.join("; "));
  for (const f of C.fails) why.set(f.id, f.error ? `no check answer (${f.error})` : f.fail.map((k) => `${k}: ${f[k].reason}`).join(" | "));
  const by = new Map(), add = (bid) => { if (!by.has(bid)) by.set(bid, { failed: [], units: new Set(), np: [] }); return by.get(bid); };
  for (const p of D.points) if (why.has(p.id)) { const e = add(p.block); e.failed.push({ ...p, why: why.get(p.id) }); p.units.forEach((u) => e.units.add(u)); }
  for (const x of C.no_point_fails || []) { const n = D.no_point.find((y) => y.unit === x.unit); const e = add(n.block); e.np.push(x.unit); e.units.add(x.unit);
    e.failed.push({ units: [x.unit], question: "(none: listed as not actionable)", verify: `(writer's reason: ${n.reason})`, evidence: [], why: `no_point rejected: ${x.reason}` }); }
  for (const x of D.uncovered) { const e = add(x.block); e.units.add(x.unit); }
  const reqs = [], key = [];
  for (const [bid, e] of by) {
    const units = [...e.units];
    reqs.push({ custom_id: bid, params: params(REPAIR_RULES, repairText(B[bid], e.failed, units), DRAFT_SCHEMA, 32000, DRAFT_MODEL) });
    key.push({ id: bid, replace_points: e.failed.filter((f) => f.id).map((f) => f.id), replace_no_point: e.np, units });
  }
  await writeBuild("repair", reqs, key, { "blocks.json": sha(`${HERE}/blocks.json`), "drafts.json": sha(`${dd}/drafts.json`) },
    () => key.reduce((s, k) => s + 600 + 250 * k.units.length, 0));
}

// FINAL PROOF SAMPLE (lead 20 Nov): 59 random points + 59 random no_point units, ONE item per request, same frozen
// criteria. sample.json = {seed, points:[ids], no_point:[unit ids]} (made by sample.py). custom_id "P:<id>" / "N:<unit>".
export const NP_RULES = `You are an independent, strict checker of a GMP audit checklist. The writer found NO clean audit point for ONE regulation unit (it is listed under "Other requirements (check the clause)" instead of as an audit point).
You get the whole block of clauses (context), the unit and the writer's reason. Decide:
major = true if an inspector would likely raise a CRITICAL or MAJOR finding if this duty were not met.
result: FAIL if major is true (nothing major may be missed; it must be a point), or if a clean audit point could be written (say which); PASS if it is truly not checkable by any document, record, observation or interview (or a point would have to add or drop content) and it is not major.
reason: "" when PASS; when FAIL one short sentence.`;
const NP_SCHEMA = { type: "object", properties: { result: { type: "string", enum: ["PASS", "FAIL"] }, major: { type: "boolean" }, reason: { type: "string" } },
  required: ["result", "major", "reason"], additionalProperties: false };
async function sampleBuild() {
  const dd = process.argv[3], S = J(`${HERE}/${process.argv[4] || "sample.json"}`);
  const D = J(`${dd}/drafts.json`), B = Object.fromEntries(J(`${HERE}/blocks.json`).blocks.map((b) => [b.id, b]));
  const unitIdx = {};
  for (const b of Object.values(B)) for (const it of b.items) for (const u of it.units) unitIdx[u.uid] = { ...u, item: it };
  const P = Object.fromEntries(D.points.map((p) => [p.id, p])), N = Object.fromEntries(D.no_point.map((x) => [x.unit, x]));
  const reqs = [], key = [];
  // custom_id must match ^[a-zA-Z0-9_-]{1,64}$ -> P001 / N001; key.json maps it back to "P:<point id>" / "N:<unit id>"
  S.points.forEach((id, i) => { const cid = `P${String(i + 1).padStart(3, "0")}`;
    reqs.push({ custom_id: cid, params: params(CHECK_RULES, checkText(P[id], unitIdx), CHECK_SCHEMA, 16000) }); key.push({ id: cid, item: `P:${id}` }); });
  S.no_point.forEach((u, i) => { const cid = `N${String(i + 1).padStart(3, "0")}`;
    const x = N[u], text = [blockText(B[x.block]).replace(/ \[(DUTY|INFO)\]/g, ""), `NOT-ACTIONABLE UNIT TO JUDGE: ${u}`, `writer's reason: ${x.reason}`].join("\n");
    reqs.push({ custom_id: cid, params: params(NP_RULES, text, NP_SCHEMA, 16000) }); key.push({ id: cid, item: `N:${u}` }); });
  await writeBuild("sample", reqs, key, { "blocks.json": sha(`${HERE}/blocks.json`), "drafts.json": sha(`${dd}/drafts.json`) }, (r) => r.length * 400);
}

// 2-OF-3 RULE (owner 20 Nov): every FAIL of a proof sample gets 2 more independent opinions = the SAME request sent
// again twice (fresh calls). opinion-build <sampleDir> -> <sampleDir>/opinions/{batch-01.jsonl,key.json}; custom ids
// <cid>o1 / <cid>o2; key items = the sample item ids.
async function opinionBuild() {
  const sd = process.argv[3].startsWith("/") ? process.argv[3] : `${HERE}/${process.argv[3]}`;
  const key = Object.fromEntries(J(`${sd}/key.json`).map((k) => [k.id, k.item]));
  const raw = J(`${sd}/raw.json`).results;
  const failed = raw.filter((r) => {
    if (r.error) return true;
    const d = r.data;
    return "result" in d ? (d.result !== "PASS" || d.major) : ["no_more", "no_less", "answerable", "own_words"].some((k) => d[k].result !== "PASS");
  }).map((r) => r.id);
  const lines = Object.fromEntries(fs.readFileSync(`${sd}/batch-01.jsonl`, "utf8").trim().split("\n").map((l) => { const o = JSON.parse(l); return [o.custom_id, o]; }));
  const reqs = [], k2 = [];
  for (const cid of failed) for (const n of [1, 2]) { reqs.push({ custom_id: `${cid}o${n}`, params: lines[cid].params }); k2.push({ id: `${cid}o${n}`, item: key[cid], opinion: n + 1 }); }
  if (!reqs.length) { console.log("no FAIL in the sample: nothing to do"); return; }
  const save = OUT;
  await writeBuild("opinions", reqs, k2, { "blocks.json": sha(`${HERE}/blocks.json`) }, (r) => r.length * 250);
  console.log(`opinions for ${failed.length} failed items: ${failed.map((c) => key[c]).join(", ")}`);
}

// ---------------- build / submit / collect ----------------
function splitBatches(reqs) {
  const out = []; let cur = [], bytes = 0;
  for (const r of reqs) {
    const line = JSON.stringify(r) + "\n", b = Buffer.byteLength(line);
    if (cur.length && (cur.length >= MAX_REQ || bytes + b > MAX_BYTES)) { out.push(cur); cur = []; bytes = 0; }
    cur.push(line); bytes += b;
  }
  if (cur.length) out.push(cur);
  return out;
}
async function writeBuild(kind, reqs, key, guard, outFactor) {
  if (fs.existsSync(`${OUT}/batches.json`)) throw new Error(`${OUT}/batches.json exists (already submitted): use a new OUT`);
  fs.mkdirSync(OUT, { recursive: true });
  for (const f of fs.readdirSync(OUT)) if (/^batch-\d+\.jsonl$/.test(f)) fs.unlinkSync(`${OUT}/${f}`);
  splitBatches(reqs).forEach((lines, i) => fs.writeFileSync(`${OUT}/batch-${String(i + 1).padStart(2, "0")}.jsonl`, lines.join("")));
  fs.writeFileSync(`${OUT}/key.json`, JSON.stringify(key, null, 1));
  const c = client();
  let inTok = 0;   // count_tokens on EVERY request (free)
  for (const r of reqs) inTok += (await c.messages.countTokens({ model: r.params.model, system: r.params.system, messages: r.params.messages, output_config: r.params.output_config })).input_tokens;
  const outTok = outFactor(reqs, inTok);
  const model = reqs[0].params.model, [pi, po] = PRICES[model];
  const cost = (inTok * pi + outTok * po) / 1e6 * BATCH;
  const rep = { kind, built: new Date().toISOString(), model, effort: EFFORT, requests: reqs.length, guard,
    estimate: { input_tokens: inTok, output_tokens_assumed: outTok, cost_usd: +cost.toFixed(2) } };
  fs.writeFileSync(`${OUT}/build-report.json`, JSON.stringify(rep, null, 1));
  console.log(JSON.stringify(rep, null, 1));
}

async function draftBuild() {
  const which = process.argv[3] || "calib";
  const B = J(`${HERE}/blocks.json`).blocks;
  const sel = which === "all" ? B : which === "calib" ? calibPick(B) : B.filter((b) => J(which).includes(b.id));
  const reqs = sel.map((b) => ({ custom_id: b.id, params: params(DRAFT_RULES, blockText(b), DRAFT_SCHEMA, 32000, DRAFT_MODEL) }));
  const key = sel.map((b) => ({ id: b.id, duty: b.items.flatMap((it) => it.units.filter((u) => u.mark === "duty").map((u) => u.uid)) }));
  // output estimate: ~900 tokens thinking + ~170 tokens per duty unit (until calibration usage is known)
  const per = Number(process.env.OUT_PER_DUTY || 170), base = Number(process.env.OUT_BASE || 900);
  await writeBuild("draft", reqs, key, { "blocks.json": sha(`${HERE}/blocks.json`) },
    () => sel.reduce((s, b) => s + base + per * nduty(b), 0));
}

async function checkBuild() {
  const dd = process.argv[3]; if (!dd) throw new Error("check-build needs the draft folder");
  const D = J(`${dd}/drafts.json`);
  const B = J(`${HERE}/blocks.json`).blocks;
  const unitIdx = {};
  for (const b of B) for (const it of b.items) for (const u of it.units) unitIdx[u.uid] = { ...u, item: it };
  const reqs = [], key = [];
  const only = process.argv[4] ? new Set(J(process.argv[4])) : null;     // optional: only these point ids (proof sample)
  for (const p of D.points) {
    if (only && !only.has(p.id)) continue;
    if ((p.problems || []).some((x) => x.startsWith("A1"))) continue;   // invalid unit ids: fixed first, not checked
    reqs.push({ custom_id: p.id, params: params(CHECK_RULES, checkText(p, unitIdx), CHECK_SCHEMA, 16000) });
    key.push({ id: p.id, block: p.block });
  }
  const per = Number(process.env.OUT_PER_CHECK || 700);
  await writeBuild("check", reqs, key, { "blocks.json": sha(`${HERE}/blocks.json`), "drafts.json": sha(`${dd}/drafts.json`) },
    (r) => r.length * per);
}

async function submit() {
  if (!process.argv.includes("--yes")) { console.log("refused: submit needs --yes (owner, after the lead's go)"); return; }
  if (fs.existsSync(`${OUT}/batches.json`)) { console.log("refused: batches.json exists (already submitted)"); return; }
  const rep = J(`${OUT}/build-report.json`);
  if (rep.estimate.cost_usd > ESTIMATE_LIMIT) { console.log(`refused: estimate US$${rep.estimate.cost_usd} > ${ESTIMATE_LIMIT}`); return; }
  for (const [f, h] of Object.entries(rep.guard)) {
    const p = f === "blocks.json" ? `${HERE}/blocks.json` : null;
    if (p && sha(p) !== h) { console.log(`refused: ${f} changed after the build; build again`); return; }
  }
  const c = client(), done = [];
  for (const f of fs.readdirSync(OUT).filter((f) => /^batch-\d+\.jsonl$/.test(f)).sort()) {
    const requests = fs.readFileSync(`${OUT}/${f}`, "utf8").trim().split("\n").map((l) => JSON.parse(l));
    const b = await c.messages.batches.create({ requests });
    done.push({ file: f, id: b.id, requests: requests.length, created: new Date().toISOString() });
    fs.writeFileSync(`${OUT}/batches.json`, JSON.stringify(done, null, 1));
    console.log(`${f}: batch ${b.id}, ${requests.length} requests, ${b.processing_status}`);
  }
}

async function collect() {
  const c = client(), bs = J(`${OUT}/batches.json`), rep = J(`${OUT}/build-report.json`);
  for (const b of bs) {
    const s = await c.messages.batches.retrieve(b.id);
    if (s.processing_status !== "ended") { console.log(`${b.file} ${b.id}: ${s.processing_status}`, JSON.stringify(s.request_counts)); return; }
  }
  const raw = []; let inTok = 0, outTok = 0;
  for (const b of bs) for await (const r of await c.messages.batches.results(b.id)) {
    if (r.result.type !== "succeeded") { raw.push({ id: r.custom_id, error: r.result.type }); continue; }
    const m = r.result.message; inTok += m.usage.input_tokens; outTok += m.usage.output_tokens;
    if (m.stop_reason !== "end_turn") { raw.push({ id: r.custom_id, error: `stop_reason ${m.stop_reason}`, out_tokens: m.usage.output_tokens }); continue; }
    try { raw.push({ id: r.custom_id, out_tokens: m.usage.output_tokens, data: JSON.parse(m.content.find((x) => x.type === "text").text) }); }
    catch { raw.push({ id: r.custom_id, error: "unparsable output" }); }
  }
  const [pi, po] = PRICES[rep.model];
  const cost = (inTok * pi + outTok * po) / 1e6 * BATCH;
  const refusals = raw.filter((r) => r.error === "stop_reason refusal").length;
  fs.writeFileSync(`${OUT}/raw.json`, JSON.stringify({ usage: { model: rep.model, input_tokens: inTok, output_tokens: outTok, cost_usd: +cost.toFixed(2), refusals }, results: raw }, null, 1));
  console.log(`${rep.kind}: ${raw.length} results, errors ${raw.filter((r) => r.error).length} (refusals ${refusals}); model ${rep.model}; tokens in ${inTok} out ${outTok}; cost ~US$${cost.toFixed(2)}`);
  console.log(`next: ${rep.kind === "draft" ? `python3 -I assemble.py ${OUT}` : rep.kind === "repair" ? `python3 -I merge.py <draftDir> ${OUT} <newDraftDir>` : `python3 -I score.py ${OUT} <draftDir>`}`);
}

const mode = import.meta.url === `file://${process.argv[1]}` ? process.argv[2] : null;   // only when run directly
if (!OUT && mode) { console.log("set OUT=<folder>"); process.exit(1); }
const run = { "draft-build": draftBuild, "check-build": checkBuild, "check-block-build": checkBlockBuild, "repair-build": repairBuild, "sample-build": sampleBuild, "opinion-build": opinionBuild, submit, collect }[mode];
if (run) await run(); else if (mode) console.log("modes: draft-build [calib|all|<ids.json>], check-build <draftDir>, submit --yes, collect");
