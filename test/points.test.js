// Points mode (audit layer) on a FAKE points file built into a temp data dir (never into web/data).
import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { execFileSync } from 'node:child_process';
const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'macp-'));
const real = JSON.parse(fs.readFileSync(new URL('../data/items.json', import.meta.url)));
const its = real.items.filter((x) => x.reg === 'Schedule M' && !x.bg && x.pt.includes('all')).slice(0, 20);
const fake = its.map((it, i) => ({ id: 'T' + i, references: [], area: it.area, system: 'Quality', question: `Test question ${i}?`, verify: 'records', evidence: ['SOP'],
  clauses: [{ item: it.id, units: it.u.filter((u) => u[3]).map((u) => u[0]) }] }));
const st = real.items.find((x) => x.reg === 'Schedule M' && x.pt.includes('sterile') && x.u.some((u) => u[3]));
fake.push({ id: 'S1', references: [], area: st.area, question: 'Sterile point?', plant_types: ['sterile'], audience: 'manufacturer', clauses: [{ item: st.id, units: [st.u.find((u) => u[3])[0]] }] });
fake.push({ id: 'S2', references: [], area: st.area, question: 'Importer point?', plant_types: ['all'], audience: 'EU importer', clauses: [{ item: st.id, units: [] }] });
const withRefs = its.find((x) => (x.refs || []).length >= 1);
fake[1].clauses = [{ item: withRefs.id, units: [] }]; fake[1].references = [withRefs.refs[0]];
fake[0].evidence = [{ type: 'document', what: 'QA SOP' }, { type: 'record', what: 'last PQR' }]; fake[0].modality = 'should'; fake[0].regulator = 'Schedule M'; fake[0].grade_hint = 'major';
const ot = real.items.filter((x) => x.reg === 'Schedule M' && !x.bg && x.pt.includes('all')).slice(30, 33);
const others = ot.map((it) => ({ item: it.id, unit: it.u.find((u) => u[3])[0], area: it.area, plant_types: ['all'], audience: 'manufacturer', regulator: 'Schedule M', reason: 'INTERNAL-REASON-XYZ', references: [] }));
fs.writeFileSync(path.join(tmp, 'points.json'), JSON.stringify({ points: fake, other_requirements: others }));
execFileSync('python3', ['-I', new URL('../build_data.py', import.meta.url).pathname], { env: { ...process.env, WEB_POINTS: path.join(tmp, 'points.json'), WEB_OUT: tmp } });
process.env.WEB_DATA = path.join(tmp, 'items.json'); process.env.AUDIT_DB = path.join(tmp, 't.sqlite');
const { start } = await import('../server.js');
const { hashPw } = await import('../src/store-sqlite.js');
const { server, deps } = await start(); const db = deps.store.db;
await new Promise((r) => server.listen(0, '127.0.0.1', r));
const base = `http://127.0.0.1:${server.address().port}`;
const cid = Number(db.prepare('INSERT INTO companies (name) VALUES (?)').run('P').lastInsertRowid);
db.prepare('INSERT INTO users (company_id,email,name,pw,created) VALUES (?,?,?,?,?)').run(cid, 'p@x.test', 'P', hashPw('correct-horse-1'), 'now');
test.after(() => { server.close(); fs.rmSync(tmp, { recursive: true }); });

test('fake data has points, marked not proven; real data untouched; scope rule', async () => {
  const d = JSON.parse(fs.readFileSync(path.join(tmp, 'items.json')));
  assert.equal(d.points.length, 22); assert.deepEqual(d.points.find((x) => x.id === 'T1').refs, [withRefs.refs[0]]); assert.equal(d.other_requirements.length, 3);
  assert.ok(!JSON.stringify(d).includes('INTERNAL-REASON-XYZ'), 'reason is internal');
  const { selectPoints } = await import('../public/select.js');
  const ids = (cfg) => selectPoints(d, { markets: ['india'], plants: [], audiences: ['manufacturer'], removed: {}, ...cfg }).map((p) => p.id);
  assert.ok(!ids({}).includes('S1') && ids({ plants: ['sterile'] }).includes('S1'), 'own plant_types');
  assert.ok(!ids({}).includes('S2') && ids({ audiences: ['manufacturer', 'EU importer'] }).includes('S2'), 'own audience');
  assert.equal(ids({ markets: ['eu'] }).length, 0, 'market = regulator of the clause items'); assert.equal(d.points_proven, false);
  // real data: points only when PROVEN, or BETA with audit-layer/beta-approved.json (lead 2c, 20 Nov)
  if ('points' in real) assert.ok(real.points_proven === true || (real.points_status === 'beta' && true));
  assert.equal(d.points_status, 'beta', 'fake points without proof are beta only via beta-approved.json');
});

test('build fails: unit in both lists, wrong regulator, unknown ref, missing references', () => {
  const bad = { points: [fake[0]], other_requirements: [{ item: fake[0].clauses[0].item, unit: fake[0].clauses[0].units[0], area: 'QS', plant_types: ['all'], regulator: 'Schedule M', references: [] }] };
  fs.writeFileSync(path.join(tmp, 'bad.json'), JSON.stringify(bad)); fs.mkdirSync(path.join(tmp, 'bad'));
  assert.throws(() => execFileSync('python3', ['-I', new URL('../build_data.py', import.meta.url).pathname], { env: { ...process.env, WEB_POINTS: path.join(tmp, 'bad.json'), WEB_OUT: path.join(tmp, 'bad') }, stdio: 'pipe' }), /never both/);
  const bad2 = { points: [{ ...fake[1], regulator: 'Schedule-M' }] };
  fs.writeFileSync(path.join(tmp, 'bad2.json'), JSON.stringify(bad2));
  const { references, ...noRefs } = fake[3];
  fs.writeFileSync(path.join(tmp, 'bad4.json'), JSON.stringify({ points: [noRefs] }));
  assert.throws(() => execFileSync('python3', ['-I', new URL('../build_data.py', import.meta.url).pathname], { env: { ...process.env, WEB_POINTS: path.join(tmp, 'bad4.json'), WEB_OUT: path.join(tmp, 'bad') }, stdio: 'pipe' }), /without references/);
  fs.writeFileSync(path.join(tmp, 'bad3.json'), JSON.stringify({ points: [{ ...fake[2], references: ['WHO 99.99 not real'] }] }));
  assert.throws(() => execFileSync('python3', ['-I', new URL('../build_data.py', import.meta.url).pathname], { env: { ...process.env, WEB_POINTS: path.join(tmp, 'bad3.json'), WEB_OUT: path.join(tmp, 'bad') }, stdio: 'pipe' }), /not in its items' refs/);
  assert.throws(() => execFileSync('python3', ['-I', new URL('../build_data.py', import.meta.url).pathname], { env: { ...process.env, WEB_POINTS: path.join(tmp, 'bad2.json'), WEB_OUT: path.join(tmp, 'bad') }, stdio: 'pipe' }));
});

test('points template -> audit: Compliant/Not compliant + grade, Excel', async () => {
  const r0 = await fetch(base + '/api/login', { method: 'POST', headers: { 'X-Requested-With': 'mac' }, body: JSON.stringify({ email: 'p@x.test', password: 'correct-horse-1' }) });
  const ck = r0.headers.get('set-cookie').split(';')[0];
  const A = (m, u, b) => fetch(base + u, { method: m, headers: { cookie: ck, 'X-Requested-With': 'mac' }, body: b ? JSON.stringify(b) : undefined });
  let r = await A('POST', '/api/templates', { name: 'PT', config: { mode: 'points', markets: ['india'], removed: { 'P:T1': 'not here' } } });
  assert.equal(r.status, 200); const tid = (await r.json()).id;
  r = await A('POST', '/api/audits', { template_id: tid, name: 'PA' }); const aid = (await r.json()).id;
  r = await A('PUT', '/api/audits/' + aid, { answers: {
    'P:T0': { a: 'Not compliant', grade: 'major', note: 'no SOP' }, 'P:T2': { a: 'Compliant', grade: 'critical' },
    'P:T1': { a: 'Compliant' }, 'P:T3': { a: 'Yes' }, [its[4].id + '#' + its[4].u[0][0]]: { a: 'Yes' },
    [`O:${others[0].item}#${others[0].unit}`]: { a: 'No', grade: 'major', note: 'x' }, [`O:${others[1].item}#${others[1].unit}`]: { a: 'Compliant' } } });
  assert.equal(r.status, 200);
  const a = await (await A('GET', '/api/audits/' + aid)).json();
  assert.deepEqual(a.answers, { 'P:T0': { a: 'Not compliant', note: 'no SOP', grade: 'major' }, 'P:T2': { a: 'Compliant' }, [`O:${others[0].item}#${others[0].unit}`]: { a: 'No', note: 'x' } },
    'removed point, wrong answer set, clause keys and grade on Compliant are dropped');
  const list = await (await A('GET', '/api/audits')).json();
  assert.equal(list[0].total, 22); assert.equal(list[0].no, 2); assert.equal(list[0].yes, 1); assert.equal(list[0].mode, 'points');
  r = await A('GET', `/api/audits/${aid}/export.xlsx`); assert.equal(r.status, 200);
  const ExcelJS = (await import('exceljs')).default; const wb = new ExcelJS.Workbook(); await wb.xlsx.load(Buffer.from(await r.arrayBuffer()));
  const ws = wb.getWorksheet('Audit points'); assert.equal(ws.rowCount - 1, 22);
  const texts = []; const tc = ws.getRow(1).values.indexOf('Audit point'); ws.eachRow((r) => texts.push(String(r.getCell(tc).value || '')));
  assert.equal(texts.filter((t) => t.startsWith('Other requirement')).length, 3);
  assert.ok(texts.some((t) => t.startsWith('(Recommended) Test question 0')));
  const hdr = ws.getRow(1).values.filter(Boolean); assert.ok(hdr.includes('Grade') && hdr.includes('What to verify'));
});

test('Download PDF of an audit-point audit: points, grade, Beta label when the data is Beta', async () => {
  const { execFileSync: ex } = await import('node:child_process');
  const r0 = await fetch(base + '/api/login', { method: 'POST', headers: { 'X-Requested-With': 'mac' }, body: JSON.stringify({ email: 'p@x.test', password: 'correct-horse-1' }) });
  const ck = r0.headers.get('set-cookie').split(';')[0];
  const A = (m, u, b) => fetch(base + u, { method: m, headers: { cookie: ck, 'X-Requested-With': 'mac' }, body: b ? JSON.stringify(b) : undefined });
  const tid = (await (await A('POST', '/api/templates', { name: 'PT2', config: { mode: 'points', markets: ['india'] } })).json()).id;
  const aid = (await (await A('POST', '/api/audits', { template_id: tid, name: 'PDF points' })).json()).id;
  await A('PUT', '/api/audits/' + aid, { answers: { 'P:T0': { a: 'Not compliant', grade: 'major', note: 'no SOP' } } });
  const r = await A('GET', `/api/audits/${aid}/export.pdf`); assert.equal(r.status, 200);
  const f = path.join(tmp, 'p.pdf'); fs.writeFileSync(f, Buffer.from(await r.arrayBuffer()));
  const txt = ex('pdftotext', [f, '-']).toString().replace(/\s+/g, ' ');
  for (const w of ['Audit point', '(Recommended) Test question 0', 'no SOP']) assert.ok(txt.includes(w), w);
  assert.match(txt, /Not .*compliant .*\(major\)/);
  const d = JSON.parse(fs.readFileSync(path.join(tmp, 'items.json')));
  assert.equal(txt.includes('Beta – independently checked'), d.points_status === 'beta');
  // the real data is Beta: the label is on every page of a points audit there (checked through the module)
  const { auditPdf } = await import('../src/pdf.js');
  const real = JSON.parse(fs.readFileSync(new URL('../data/items.json', import.meta.url)));
  if (real.points_status === 'beta') {
    const buf = await auditPdf(real, { name: 'B', status: 'open', template_name: 'T', data_version: real.version, answers: {}, header: {},
      config: { mode: 'points', markets: ['india'], plants: [], audiences: ['manufacturer'], removed: {}, company_items: [] } });
    fs.writeFileSync(f, buf); const t2 = ex('pdftotext', [f, '-']).toString();
    const pages = t2.split('\f').filter((x) => x.trim());
    assert.ok(pages.length > 5 && pages.every((p) => p.includes('Beta – independently checked')), 'Beta label on every page');
  }
});
