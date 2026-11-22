// "Find a clause" (home page) rule, on the real data file.
import test from 'node:test'; import assert from 'node:assert/strict'; import fs from 'node:fs';
import { findItems } from '../public/select.js';
const D = JSON.parse(fs.readFileSync(new URL('../data/items.json', import.meta.url)));
test('find a clause: numbers match whole reference numbers, words match text; reference hits first', () => {
  const a = findItems(D.items, '1.7');
  assert.equal(a[0].ref, 'Schedule M 1.7');
  assert.ok(a.every((x) => /(^|[^\d.])1\.7(?!\d)/.test(x.ref)), 'no 11.7 / 1.71');
  const b = findItems(D.items, '211.84'); assert.ok(b.length >= 4 && b.every((x) => x.ref.startsWith('21 CFR 211.84')));
  const c = findItems(D.items, 'supplier'); assert.ok(c.length > 50 && c.every((x) => (x.ref + x.id + (x.title || '') + x.text).toLowerCase().includes('supplier')));
  assert.equal(findItems(D.items, 'Schedule M 1.7')[0].ref, 'Schedule M 1.7');
  assert.deepEqual(findItems(D.items, 'x'), []); assert.deepEqual(findItems(D.items, ''), []);
  assert.deepEqual(findItems(D.items, '((('), []);
});

import { askQuestionFor } from '../public/select.js';
test('"Ask about this": question built by code from the line', () => {
  const B = new Map(D.items.map((x) => [x.id, x]));
  assert.equal(askQuestionFor({ item: B.get('SchM-I-1.7') }), 'What do the regulations require about: The product quality system shall be defined and documented?');
  const titled = D.items.find((x) => x.title); assert.ok(askQuestionFor({ item: titled }).includes(titled.title.replace(/[\s.,;:—–-]+$/, '')));
  for (const x of D.items) { const q = askQuestionFor({ item: x }); assert.ok(q.length <= 250 && q.endsWith('?') && q.startsWith('What do the regulations require about: '), q); }
  if (D.points) assert.equal(askQuestionFor({ point: D.points[0] }), D.points[0].question);
  const o = D.other_requirements?.[0];
  if (o) { const it = B.get(o.item); const u = it.u.find((z) => z[0] === o.unit); const q = askQuestionFor({ other: o, item: it, text: it.text.slice(u[1], u[2]) });
    assert.ok(q.startsWith('What do the regulations require about: ') && q.length <= 250); }
});
