// FULL DRAFT with Fable 5.2 Claude Code agents (owner choice C, 19 Nov 2026; lead audit-admin-2c).
// Resumable state on disk: full/state.json. Prompts are FROZEN: full/prompt.lock.json holds sha256 of the draft rules
// + schema; every command refuses if layer.mjs's prompt changed (a new session must not draft with another prompt).
//
//   node waves.mjs init                 freeze prompt, all 1087 blocks pending
//   node waves.mjs plan <n>             make n new task folders (~100 duty units each, block order) -> prints their paths
//   node waves.mjs gather               read every assigned task's out.json: valid blocks -> done (full/results/<id>.json),
//                                       invalid (no answer / bad tail echo / bad shape) -> pending again
//   node waves.mjs build                full/draft/raw.json from all done blocks (then: python3 -I assemble.py full/draft)
//   node waves.mjs redo <id...>         put blocks back to pending (code-check failures), old result moved to full/redo/
//   node waves.mjs release <task>       an agent died: its unanswered blocks back to pending
//   node waves.mjs status
// Agent: model "fable", prompt = read <task>/task.md, write <task>/out.json only. Max 4 at a time (lead).
import fs from "fs";
import crypto from "crypto";
import { DRAFT_RULES, DRAFT_SCHEMA, blockText, CHECK_BLOCK_RULES, CHECK_BLOCK_SCHEMA, REPAIR_RULES, repairText } from "./layer.mjs";

const HERE = "/root/audit-admin/audit-layer", F = `${HERE}/full`;
const J = (p) => JSON.parse(fs.readFileSync(p, "utf8"));
const W = (p, o) => fs.writeFileSync(p, JSON.stringify(o, null, 1));
const TARGET = 100, MAX_BLOCKS = 12;
const promptSha = () => crypto.createHash("sha256").update(DRAFT_RULES + "\n" + JSON.stringify(DRAFT_SCHEMA)).digest("hex");
const checkSha = () => crypto.createHash("sha256").update(CHECK_BLOCK_RULES + "\n" + JSON.stringify(CHECK_BLOCK_SCHEMA)).digest("hex");
const B = Object.fromEntries(J(`${HERE}/blocks.json`).blocks.map((b) => [b.id, b]));
const nduty = (b) => b.items.reduce((s, it) => s + it.units.filter((u) => u.mark === "duty").length, 0);
const words = (s) => String(s || "").toLowerCase().replace(/[^a-z0-9 ]/g, " ").split(/\s+/).filter(Boolean);
const strip = (t) => String(t).replace(/^ {2}[^\n]*?#\d+ (\[(DUTY|INFO)\] )?/gm, " ");
const tail1 = (e, t) => e.length >= 3 && e.length <= 20 && e.join(" ") === t.slice(-e.length).join(" ");
const ws = (t) => String(t || "").replace(/\s+/g, " ").trim();
// a raw tail (whitespace collapsed, >= 5 characters) also counts: blocks that end with a table row ("100 | 50 | -")
const tailOk = (echo, text) => tail1(words(echo), words(strip(text))) || tail1(words(echo), words(text)) ||
  (ws(echo).length >= 5 && ws(text).endsWith(ws(echo)));

function guard() {
  const lock = J(`${F}/prompt.lock.json`);
  if (lock.sha256 !== promptSha()) throw new Error("draft prompt changed since init (prompt.lock.json): do not draft with another prompt; ask the lead");
  if (lock.check_sha256 !== checkSha()) throw new Error("checker prompt changed since init (prompt.lock.json): ask the lead");
}
const state = () => J(`${F}/state.json`);
const save = (s) => W(`${F}/state.json`, s);

function taskMd(ids) {
  return ["# DRAFT task (GMP audit layer, full run)", "",
    "Work ONLY from this file. Do not open any other file except writing your answer file named below.",
    "For EACH block below, answer exactly as the SYSTEM PROMPT says, as JSON matching the SCHEMA, and add \"last5\": the last 5 words of that block's input text (as you read them).",
    "Write ONE file: out.json in the same folder as this task file: {\"blocks\": {\"<block id>\": {...answer..., \"last5\": \"...\"}}}. Answer EVERY block.",
    "", "## SYSTEM PROMPT", "", DRAFT_RULES, "", "## SCHEMA (per block answer)", "", "```json", JSON.stringify(DRAFT_SCHEMA), "```", "",
    ...ids.flatMap((id) => [`## BLOCK ${id}`, "", "```text", blockText(B[id]), "```", ""])].join("\n");
}

function valid(d, id) {        // shape + unit ids of this block (coverage etc. is assemble.py's job)
  if (!d || !Array.isArray(d.points) || !Array.isArray(d.no_point)) return "bad shape";
  const uids = new Set(B[id].items.flatMap((it) => it.units.map((u) => u.uid)));
  for (const p of d.points) {
    for (const k of ["units", "question", "verify", "evidence", "grade_hint", "modality"]) if (!(k in p)) return `point without ${k}`;
    if (!["must", "should"].includes(p.modality) || !["critical", "major", "other"].includes(p.grade_hint)) return "bad enum";
    for (const u of p.units) if (!uids.has(u)) return `unknown unit ${u}`;
  }
  for (const x of d.no_point) if (!uids.has(x.unit) || !x.reason) return `bad no_point ${x.unit}`;
  return null;
}

const cmd = {
  init() {
    if (fs.existsSync(`${F}/state.json`)) throw new Error("full/state.json exists");
    fs.mkdirSync(`${F}/tasks`, { recursive: true }); fs.mkdirSync(`${F}/results`, { recursive: true });
    W(`${F}/prompt.lock.json`, { sha256: promptSha(), check_sha256: checkSha(), frozen: new Date().toISOString(),
      note: "sha256 = DRAFT_RULES + DRAFT_SCHEMA (round-3 prompt, owner 19 Nov); check_sha256 = CHECK_BLOCK_RULES + schema (round-3 criteria + major on no_point)" });
    fs.writeFileSync(`${F}/prompt-frozen.txt`, DRAFT_RULES + "\n\n" + JSON.stringify(DRAFT_SCHEMA, null, 1));
    fs.writeFileSync(`${F}/check-prompt-frozen.txt`, CHECK_BLOCK_RULES + "\n\n" + JSON.stringify(CHECK_BLOCK_SCHEMA, null, 1));
    save({ next_task: 1, blocks: Object.fromEntries(Object.keys(B).map((id) => [id, { status: "pending", tries: 0 }])) });
    console.log(`init: ${Object.keys(B).length} blocks pending; draft sha256 ${promptSha()}; check sha256 ${checkSha()}`);
  },
  plan(n = "4") {
    guard(); const s = state(), made = [];
    const pend = Object.keys(s.blocks).filter((id) => s.blocks[id].status === "pending").sort();
    for (let k = 0; k < Number(n) && pend.length; k++) {
      const ids = []; let d = 0;
      while (pend.length && ids.length < MAX_BLOCKS && (ids.length === 0 || d + nduty(B[pend[0]]) <= TARGET)) { const id = pend.shift(); ids.push(id); d += nduty(B[id]); }
      const t = `t${String(s.next_task++).padStart(3, "0")}`, dir = `${F}/tasks/${t}`;
      fs.mkdirSync(dir, { recursive: true }); fs.writeFileSync(`${dir}/task.md`, taskMd(ids)); W(`${dir}/ids.json`, ids);
      for (const id of ids) Object.assign(s.blocks[id], { status: "assigned", task: t, tries: s.blocks[id].tries + 1 });
      made.push(`${dir}/task.md (${ids.length} blocks, ${d} duty units)`);
    }
    save(s); console.log(made.join("\n") || "nothing pending");
  },
  gather() {
    guard(); const s = state(); let done = 0, back = [];
    const tasks = [...new Set(Object.values(s.blocks).filter((b) => b.status === "assigned").map((b) => b.task))];
    for (const t of tasks) {
      const f = `${F}/tasks/${t}/out.json`; if (!fs.existsSync(f)) continue;
      let out; try { out = J(f).blocks || {}; } catch { out = {}; }
      for (const id of J(`${F}/tasks/${t}/ids.json`)) {
        if (s.blocks[id].status !== "assigned" || s.blocks[id].task !== t) continue;
        const a = out[id]; const { last5, ...data } = a || {};
        const why = !a ? "no answer" : !tailOk(last5, blockText(B[id])) ? `last5 not a tail: ${last5}` : valid(data, id);
        if (why) { Object.assign(s.blocks[id], { status: "pending", last_error: why }); back.push(`${id} (${t}): ${why}`); }
        else { W(`${F}/results/${id}.json`, { block: id, task: t, data }); Object.assign(s.blocks[id], { status: "done" }); done++; }
      }
    }
    save(s); console.log(`gathered: ${done} blocks done; back to pending: ${back.length}`); if (back.length) console.log(back.join("\n"));
    cmd.status();
  },
  build() {
    const s = state(), ids = Object.keys(s.blocks).filter((id) => s.blocks[id].status === "done").sort();
    fs.mkdirSync(`${F}/draft`, { recursive: true });
    W(`${F}/draft/raw.json`, { usage: { runner: "claude-code-agents (fable)", prompt_sha256: J(`${F}/prompt.lock.json`).sha256 },
      results: ids.map((id) => ({ id, data: J(`${F}/results/${id}.json`).data })) });
    console.log(`full/draft/raw.json: ${ids.length} blocks; next: python3 -I assemble.py full/draft`);
  },
  redo(...ids) {
    const s = state(); fs.mkdirSync(`${F}/redo`, { recursive: true });
    for (const id of ids) {
      if (fs.existsSync(`${F}/results/${id}.json`)) fs.renameSync(`${F}/results/${id}.json`, `${F}/redo/${id}-${Date.now()}.json`);
      Object.assign(s.blocks[id], { status: "pending", last_error: "code check (redo)" });
    }
    save(s); console.log(`redo: ${ids.length} blocks pending`);
  },
  release(t) {
    const s = state(); let n = 0;
    for (const [id, b] of Object.entries(s.blocks)) if (b.status === "assigned" && b.task === t) { Object.assign(b, { status: "pending", last_error: `released ${t}` }); n++; }
    save(s); console.log(`released ${n} blocks of ${t}`);
  },
  // ONE repair round per part (owner): Fable agents re-draft failed points / rejected no_point / code-flag points.
  //   node waves.mjs repair-tasks <partDir> [nTasks]  -> <partDir>/repair/rNN/task.md, key.json (blocks, replaced ids, units)
  //   node waves.mjs repair-gather <partDir>          -> <partDir>/repair/raw.json (then merge.py <partDir>/draft <partDir>/repair <partDir>/merged)
  "repair-tasks"(pd, n = "4") {
    guard(); const P = pd.startsWith("/") ? pd : `${HERE}/${pd}`;
    const D = J(`${P}/draft/drafts.json`), C = J(`${P}/check/checks.json`);
    // owner rule: ONE repair only -> skip points already repaired ("-R" ids) and no_point units re-drafted by an earlier
    // part's repair (those go to owner-review via finalize.py)
    const done = new Set();
    for (const d of fs.readdirSync(F).filter((x) => /^part-\d+$/.test(x))) {
      const k = `${F}/${d}/repair/key.json`;
      if (`${F}/${d}` !== P && fs.existsSync(k)) for (const x of J(k)) [...x.replace_no_point, ...x.units].forEach((u) => done.add(u));
    }
    const why = new Map();
    for (const p of D.points) if ((p.problems || []).length && !p.id.includes("-R")) why.set(p.id, "code check: " + p.problems.join("; "));
    for (const f of C.fails) if (!f.id.includes("-R") || process.env.ALLOW_R === "1") why.set(f.id, f.error ? `no check answer (${f.error})` : f.fail.map((k) => `${k}: ${f[k].reason}`).join(" | "));
    const by = new Map(), add = (bid) => { if (!by.has(bid)) by.set(bid, { failed: [], units: new Set(), np: [] }); return by.get(bid); };
    for (const p of D.points) if (why.has(p.id)) { const e = add(p.block); e.failed.push({ ...p, why: why.get(p.id) }); p.units.forEach((u) => e.units.add(u)); }
    for (const x of (C.no_point_fails || []).filter((x) => !done.has(x.unit))) { const nn = D.no_point.find((y) => y.unit === x.unit); const e = add(nn.block); e.np.push(x.unit); e.units.add(x.unit);
      e.failed.push({ units: [x.unit], question: "(none: listed as not actionable)", verify: `(writer's reason: ${nn.reason})`, evidence: [], why: `no_point rejected${x.major ? " (MAJOR: must be a point)" : ""}: ${x.reason}` }); }
    for (const x of D.uncovered || []) { const e = add(x.block); e.units.add(x.unit); }
    const blocks = [...by.keys()].sort(), key = blocks.map((bid) => ({ id: bid, replace_points: by.get(bid).failed.filter((f) => f.id).map((f) => f.id), replace_no_point: by.get(bid).np, units: [...by.get(bid).units] }));
    const R = `${P}/repair`; fs.mkdirSync(R, { recursive: true }); W(`${R}/key.json`, key);
    const k = Math.min(Number(n), blocks.length), bins = Array.from({ length: k }, () => []);
    blocks.forEach((b, i) => bins[i % k].push(b));
    const md = (ids) => ["# REPAIR task (GMP audit layer)", "", "Work ONLY from this file. Do not open any other file except writing your answer file named below.",
      "For EACH block below, answer exactly as the SYSTEM PROMPT says (REPAIR TASK), as JSON matching the SCHEMA, and add \"last5\": the last 5 words of that block's input text (as you read them).",
      "Write ONE file: out.json in the same folder as this task file: {\"blocks\": {\"<block id>\": {...answer..., \"last5\": \"...\"}}}. Answer EVERY block.",
      "", "## SYSTEM PROMPT", "", REPAIR_RULES, "", "## SCHEMA (per block answer)", "", "```json", JSON.stringify(DRAFT_SCHEMA), "```", "",
      ...ids.flatMap((id) => { const e = by.get(id); return [`## BLOCK ${id}`, "", "```text", repairText(B[id], e.failed, [...e.units]), "```", ""]; })].join("\n");
    bins.forEach((ids, i) => { const d = `${R}/r${String(i + 1).padStart(2, "0")}`; fs.mkdirSync(d, { recursive: true }); fs.writeFileSync(`${d}/task.md`, md(ids)); W(`${d}/ids.json`, ids); });
    console.log(`repair: ${blocks.length} blocks, ${key.reduce((s, x) => s + x.units.length, 0)} units, ${D.points.filter((p) => why.has(p.id)).length} points + ${(C.no_point_fails || []).length} no_point; tasks: ${bins.map((b, i) => `${R}/r${String(i + 1).padStart(2, "0")}/task.md (${b.length})`).join(", ")}`);
  },
  "repair-gather"(pd) {
    const P = pd.startsWith("/") ? pd : `${HERE}/${pd}`, R = `${P}/repair`, key = J(`${R}/key.json`);
    const D = J(`${P}/draft/drafts.json`), C = J(`${P}/check/checks.json`);
    // rebuild the same repair texts to check the tail echo
    const results = [], bad = [];
    for (const d of fs.readdirSync(R).filter((x) => /^r\d+$/.test(x)).sort()) {
      const out = fs.existsSync(`${R}/${d}/out.json`) ? (J(`${R}/${d}/out.json`).blocks || {}) : {};
      for (const id of J(`${R}/${d}/ids.json`)) {
        const a = out[id]; const { last5, ...data } = a || {};
        const k = key.find((x) => x.id === id);
        const units = new Set(k.units);
        let why = !a ? "no answer" : valid(data, id);
        if (!why) { const cov = new Set([...data.points.flatMap((p) => p.units), ...data.no_point.map((x) => x.unit)]); const miss = [...units].filter((u) => !cov.has(u)); if (miss.length) why = `units not covered: ${miss.join(", ")}`; }
        if (why) { bad.push(`${id}: ${why}`); results.push({ id, error: why }); } else results.push({ id, data });
      }
    }
    W(`${R}/raw.json`, { usage: { runner: "claude-code-agents (fable) repair" }, results });
    console.log(`repair-gather: ${results.length} blocks, bad ${bad.length}`); if (bad.length) console.log(bad.join("\n"));
  },
  status() {
    const s = state(), c = {}, du = {};
    for (const [id, b] of Object.entries(s.blocks)) { c[b.status] = (c[b.status] || 0) + 1; du[b.status] = (du[b.status] || 0) + nduty(B[id]); }
    console.log(`status: blocks ${JSON.stringify(c)}; duty units ${JSON.stringify(du)}`);
  },
};
const [m, ...args] = process.argv.slice(2);
(cmd[m] || (() => console.log("modes: " + Object.keys(cmd).join(", "))))(...args);
