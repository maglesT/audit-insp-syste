// End-to-end API test on a throwaway DB: login, template (remove with reason, company item), audit, answers, export, scoping.
import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'mac-'));
process.env.AUDIT_DB = path.join(tmp, 't.sqlite');
process.env.WEB_ASK_FLAG = path.join(tmp, 'ask-enabled');
fs.writeFileSync(path.join(tmp, 'stub.py'), 'import json,sys\nq=json.load(sys.stdin)\nprint(json.dumps({"v":1,"status":"answered","points":[],"meta":{"model":"stub","seconds":0.1,"cost_usd":0.012}}))\n');
process.env.WEB_ASK_CMD = path.join(tmp, 'stub.py');
const { start } = await import('../server.js');
const { hashPw } = await import('../src/store-sqlite.js');
const { server, deps } = await start(); const db = deps.store.db;
const DATA = JSON.parse(fs.readFileSync(new URL('../data/items.json', import.meta.url)));
await new Promise((r) => server.listen(0, '127.0.0.1', r));
const base = `http://127.0.0.1:${server.address().port}`;
for (const [co, em] of [['A', 'a@x.test'], ['B', 'b@x.test']]) {
  const cid = Number(db.prepare('INSERT INTO companies (name) VALUES (?)').run(co).lastInsertRowid);
  db.prepare('INSERT INTO users (company_id,email,name,pw,created) VALUES (?,?,?,?,?)').run(cid, em, co + ' user', hashPw('correct-horse-1'), 'now');
}
async function login(email) {
  const r = await fetch(base + '/api/login', { method: 'POST', headers: { 'X-Requested-With': 'mac' }, body: JSON.stringify({ email, password: 'correct-horse-1' }) });
  assert.equal(r.status, 200);
  const ck = r.headers.get('set-cookie').split(';')[0];
  return (m, u, b) => fetch(base + u, { method: m, headers: { cookie: ck, 'X-Requested-With': 'mac' }, body: b ? JSON.stringify(b) : undefined });
}
test.after(() => { server.close(); fs.rmSync(tmp, { recursive: true }); });

test('no login -> 401; bad password -> 401; no CSRF header -> 403', async () => {
  assert.equal((await fetch(base + '/api/templates')).status, 401);
  assert.equal((await fetch(base + '/api/login', { method: 'POST', headers: { 'X-Requested-With': 'mac' }, body: '{"email":"a@x.test","password":"nope"}' })).status, 401);
  assert.equal((await fetch(base + '/api/login', { method: 'POST', body: '{}' })).status, 403);
});

test('data file: no internal texts, counts match merged', async () => {
  const r = await fetch(base + '/data/items.json', { headers: { 'accept-encoding': 'gzip' } });
  const s = await r.text();
  assert.ok(!s.includes('also_texts') && !s.includes('sources.json'));
  assert.equal(DATA.items.length, 4032);
  assert.equal(DATA.counts.duty_units, 8510);
  // "Also" texts: every SHOWN-regulator ref (EU / US FDA / Schedule M) has its text; WHO / PIC/S never
  const shown = new Set(DATA.items.flatMap((x) => x.refs || []).filter((r) => !/^(WHO|PIC\/S)\b/.test(r)));
  assert.ok(shown.size >= 285); assert.deepEqual([...shown].filter((r) => !DATA.ref_texts[r]), []);
  assert.ok(Object.keys(DATA.ref_texts).every((r) => shown.has(r) && !/^(WHO|PIC\/S)\b/.test(r)));
  // editor insertions: only placeholders + recorded cross-refs; source brackets like [sic] are never marked
  const eds = DATA.items.flatMap((x) => (x.ed || []).map(([a, b]) => x.text.slice(a, b)));
  assert.ok(eds.length >= 19 && eds.every((t) => /^\[(?:(?:Table|Figure) .+, shown below|.*Part [IVX]+ [\d.]+.*)\]$/.test(t)), JSON.stringify(eds));
  assert.ok(!DATA.items.some((x) => (x.ed || []).some(([a, b]) => x.text.slice(a, b) === '[sic]')));
  assert.equal((await fetch(base + '/../merged/sources.json')).headers.get('content-type'), 'text/html; charset=utf-8'); // falls back to the app page
  assert.equal((await fetch(base + '/brand/../server.js')).headers.get('content-type'), 'text/html; charset=utf-8');
});

test('template -> audit -> answers -> excel; company scoping', async () => {
  const A = await login('a@x.test'); const B = await login('b@x.test');
  const rid = 'SchM-I-1.1';
  let r = await A('POST', '/api/templates', { name: 'T1', config: { markets: ['india'], plants: ['oral-solid'], removed: { [rid]: '' } } });
  assert.equal(r.status, 400, 'remove without reason must fail');
  r = await A('POST', '/api/templates', { name: 'T1', config: { markets: ['india', 'zz'], plants: ['oral-solid', 'bad'], removed: { [rid]: 'not used here' },
    company_items: [{ area: 'QS', title: 'Own', text: 'Our QA head signs every PQR.' }] } });
  assert.equal(r.status, 200); const tid = (await r.json()).id;
  const t = await (await A('GET', '/api/templates/' + tid)).json();
  assert.deepEqual(t.config.markets, ['india']); assert.deepEqual(t.config.plants, ['oral-solid']);
  assert.equal(t.config.removed[rid], 'not used here'); assert.equal(t.config.company_items.length, 1);
  assert.ok(!JSON.stringify(t).includes('The manufacturer must assume'), 'template stores no regulation text');
  assert.equal((await B('GET', '/api/templates/' + tid)).status, 404, 'other company cannot see it');
  r = await A('POST', '/api/audits', { template_id: tid, name: 'Audit 1' }); const aid = (await r.json()).id;
  const it = DATA.items.find((x) => x.reg === 'Schedule M' && x.id !== rid && x.u.some((u) => u[3]));
  const bgu = DATA.items.flatMap((x) => x.u.filter((u) => !u[3]).map((u) => x.id + '#' + u[0]))[0];
  const ck = 'C:' + t.config.company_items[0].cid;
  r = await A('PUT', '/api/audits/' + aid, { answers: { [it.id + '#' + it.u.find((u) => u[3])[0]]: { a: 'No', note: 'SOP missing' }, [bgu]: { a: 'Yes' }, [ck]: { a: 'Yes' }, 'x#1': { a: 'Yes' } } });
  assert.equal(r.status, 200);
  const a = await (await A('GET', '/api/audits/' + aid)).json();
  assert.equal(Object.keys(a.answers).length, 2, 'background units and unknown keys are dropped');
  const list = await (await A('GET', '/api/audits')).json();
  assert.equal(list[0].no, 1); assert.equal(list[0].yes, 1);
  assert.ok(list[0].total > 100);
  assert.deepEqual(await (await B('GET', '/api/audits')).json(), []);
  r = await A('GET', `/api/audits/${aid}/export.xlsx`);
  assert.equal(r.status, 200); const buf = Buffer.from(await r.arrayBuffer());
  assert.equal(buf.subarray(0, 2).toString(), 'PK');
  const ExcelJS = (await import('exceljs')).default; const wb = new ExcelJS.Workbook(); await wb.xlsx.load(buf);
  const ws = wb.getWorksheet('Check points');
  assert.equal(ws.rowCount - 1, list[0].total);
  const hdr = ws.getRow(1).values; const ci = hdr.indexOf('Also (text)'); assert.ok(ci > 0);
  let withText = 0;
  ws.eachRow((row, n) => { if (n === 1) return; const v = String(row.getCell(ci).value || ''); if (v) withText++;
    assert.ok(!/(^|\n)(WHO|PIC\/S)\b/.test(v), 'no WHO / PIC/S text in Excel'); });
  assert.ok(withText > 0, 'some rows carry their EU text');
  assert.ok(wb.getWorksheet('Removed items'));
  r = await A('PUT', '/api/audits/' + aid, { status: 'closed' }); assert.equal(r.status, 200);
  r = await A('PUT', '/api/audits/' + aid, { answers: {} }); assert.equal(r.status, 409, 'closed audit is read-only');
});

test('MED-11 PL-06: an audit is withdrawn with a reason and kept, never deleted; a closed audit cannot be withdrawn', async () => {
  const A = await login('a@x.test'); const B = await login('b@x.test');
  const tid = (await (await A('POST', '/api/templates', { name: 'TW', config: { markets: ['india'], plants: ['oral-solid'] } })).json()).id;
  const aid = (await (await A('POST', '/api/audits', { template_id: tid, name: 'To withdraw' })).json()).id;
  assert.equal((await A('DELETE', '/api/audits/' + aid)).status, 400, 'a reason is required');
  assert.equal((await A('DELETE', '/api/audits/' + aid, { reason: '  ' })).status, 400, 'a blank reason is refused');
  assert.equal((await B('DELETE', '/api/audits/' + aid, { reason: 'not mine' })).status, 404, 'other company cannot withdraw it');
  assert.equal((await A('DELETE', '/api/audits/' + aid, { reason: 'started on the wrong template' })).status, 200);
  const a = await (await A('GET', '/api/audits/' + aid)).json();
  assert.equal(a.status, 'withdrawn'); assert.equal(a.withdrawn_reason, 'started on the wrong template'); assert.equal(a.updated_by, 'a@x.test');
  assert.equal((await A('GET', '/api/audits')).status, 200);
  assert.equal((await (await A('GET', '/api/audits')).json()).find((x) => x.id === aid).status, 'withdrawn', 'listed, marked withdrawn');
  const tr = db.prepare("SELECT user_name, detail FROM audit_trail WHERE action='audit.withdraw' AND object_id=?").get(aid);
  assert.equal(tr.user_name, 'a@x.test'); assert.equal(JSON.parse(tr.detail).reason, 'started on the wrong template');
  assert.equal((await A('PUT', '/api/audits/' + aid, { status: 'open' })).status, 409, 'a withdrawn audit cannot be re-opened');
  assert.equal((await A('PUT', '/api/audits/' + aid, { answers: {} })).status, 409, 'nor changed');
  assert.equal((await A('DELETE', '/api/audits/' + aid, { reason: 'again' })).status, 409);
  const cid = (await (await A('POST', '/api/audits', { template_id: tid, name: 'Closed one' })).json()).id;
  assert.equal((await A('PUT', '/api/audits/' + cid, { status: 'closed' })).status, 200);
  assert.equal((await A('DELETE', '/api/audits/' + cid, { reason: 'try' })).status, 409, 'a closed audit cannot be withdrawn');
  assert.equal((await (await A('GET', '/api/audits/' + cid)).json()).status, 'closed');
});

test('ask: disabled until the flag exists; then answers, logs cost without question text, limits per hour', async () => {
  const A = await login('a@x.test');
  let r = await (await A('POST', '/api/ask', { question: 'water for injection?' })).json();
  assert.equal(r.status, 'unavailable');
  fs.writeFileSync(process.env.WEB_ASK_FLAG, 'on');
  r = await (await A('POST', '/api/ask', { question: 'SECRET-QUESTION-TEXT water?' })).json();
  assert.equal(r.status, 'answered'); assert.equal(r.meta.cost_usd, 0.012);
  await new Promise((ok) => setTimeout(ok, 100));
  const log = fs.readFileSync(path.join(tmp, 'ask-log.jsonl'), 'utf8');
  assert.ok(log.includes('"cost_usd":0.012') && !log.includes('SECRET'), log);
  for (let i = 0; i < 29; i++) await A('POST', '/api/ask', { question: 'q number ' + i });
  assert.equal((await A('POST', '/api/ask', { question: 'one too many' })).status, 429);
});

test('standalone: people, rooms and finding names are typed (no link); kept as typed; ids never trusted', async () => {
  const A = await login('a@x.test');
  const me = await (await A('GET', '/api/me')).json();
  assert.equal(me.mode, 'standalone'); assert.equal(me.permissions.length, 4); assert.deepEqual(me.links, { identity: false, master_data: false });
  assert.equal((await A('GET', '/api/pick/room?q=a')).status, 404, 'no pickers without a link');
  const tid = (await (await A('POST', '/api/templates', { name: 'T9', config: { markets: ['india'] } })).json()).id;
  const aid = (await (await A('POST', '/api/audits', { template_id: tid, name: 'Typed', auditor: 'Old style auditor' })).json()).id;
  let a = await (await A('GET', '/api/audits/' + aid)).json();
  assert.equal(a.auditor, 'Old style auditor'); assert.deepEqual(a.header.auditors, [{ name: 'Old style auditor' }]);
  const it = DATA.items.find((x) => x.reg === 'Schedule M' && x.pt.includes('all') && x.aud === 'manufacturer' && x.u.some((u) => u[3]));
  const k = it.id + '#' + it.u.find((u) => u[3])[0];
  const r = await A('PUT', '/api/audits/' + aid, { header: { auditors: [{ name: 'Asha' }, { name: 'Asha' }], auditees: [{ name: 'Ravi', id: '00000000-0000-4000-8000-000000000001' }], rooms: [{ name: 'Granulation' }] },
    answers: { [k]: { a: 'No', links: [{ kind: 'equipment', name: 'FBD-2' }, { kind: 'spaceship', name: 'x' }] } } });
  assert.equal(r.status, 200);
  a = await (await A('GET', '/api/audits/' + aid)).json();
  assert.deepEqual(a.header, { auditors: [{ name: 'Asha' }], auditees: [{ name: 'Ravi' }], rooms: [{ name: 'Granulation' }] }, 'typed, an unchecked id is dropped');
  assert.equal(a.auditor, 'Asha');
  assert.deepEqual(a.answers[k].links, [{ kind: 'equipment', name: 'FBD-2' }]);
  const tr = deps.store.db.prepare("SELECT action FROM audit_trail WHERE object_id=? AND object_type='audit' ORDER BY id").all(aid).map((x) => x.action);
  assert.deepEqual(tr, ['audit.create', 'audit.answers', 'audit.header']);
  assert.throws(() => deps.store.db.prepare('DELETE FROM audit_trail').run(), /insert-only/);
});

test('Download PDF: same content as the print page (answers, names, removed items, note); company scoping', async () => {
  const { execFileSync } = await import('node:child_process');
  const A = await login('a@x.test'); const B = await login('b@x.test');
  const tid = (await (await A('POST', '/api/templates', { name: 'PDF T', config: { markets: ['india'], removed: { 'SchM-I-1.1': 'not used here' } } })).json()).id;
  const aid = (await (await A('POST', '/api/audits', { template_id: tid, name: 'PDF Audit Ünit-2', auditor: 'Asha' })).json()).id;
  const it = DATA.items.find((x) => x.reg === 'Schedule M' && x.id !== 'SchM-I-1.1' && x.pt.includes('all') && x.aud === 'manufacturer' && x.u.some((u) => u[3]));
  const k = it.id + '#' + it.u.find((u) => u[3])[0];
  await A('PUT', '/api/audits/' + aid, { answers: { [k]: { a: 'No', note: 'SOP-QA-001 missing', links: [{ kind: 'equipment', name: 'FBD-2' }] } } });
  const t0 = Date.now();
  const r = await A('GET', `/api/audits/${aid}/export.pdf`);
  assert.equal(r.status, 200); assert.equal(r.headers.get('content-type'), 'application/pdf');
  assert.match(r.headers.get('content-disposition'), /attachment; filename="PDF Audit nit-2.pdf"/);
  const buf = Buffer.from(await r.arrayBuffer()); assert.equal(buf.subarray(0, 5).toString(), '%PDF-');
  const f = path.join(tmp, 'a.pdf'); fs.writeFileSync(f, buf);
  const txt = execFileSync('pdftotext', ['-layout', f, '-']).toString().replace(/\s+/g, ' ');
  for (const w of ['PDF Audit Ünit-2', 'Auditor: Asha', 'SOP-QA-001 missing', 'Names: equipment: FBD-2', 'Removed from the template', 'not used here',
    'Not affiliated with or endorsed by', 'Page 1 of']) assert.ok(txt.includes(w), w);
  assert.ok(!txt.includes('Beta'), 'no Beta label on a clause audit');
  console.log(`# pdf ${Math.round(buf.length / 1024)} kB, ${Date.now() - t0} ms`);
  assert.equal((await B('GET', `/api/audits/${aid}/export.pdf`)).status, 404, 'other company cannot get it');
  assert.equal((await fetch(`${base}/api/audits/${aid}/export.pdf`)).status, 401);
});
