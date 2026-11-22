// "Download PDF" (owner, 20 Nov 2026): the audit report as a ready PDF file, made on the server with pdfmake (no browser).
// Same content as the print page (public/app.js viewPrint): header, Beta label for audit-point audits, summary, one
// table per area (reference, check point / audit point, answer, note + names), removed items, the not-affiliated note.
// WHO / PIC/S appear only as clause numbers (in "Also"), never their text. The same file is used in web/ and platform/.
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import PdfPrinter from 'pdfmake';
import { MARKETS, AREA_NAMES, ANSWERS, POS, NEG, modeOf, auditLines, lineStats } from '../public/select.js';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const font = (f) => path.join(ROOT, 'fonts', f);
// Embedded Unicode font (Noto Sans, SIL Open Font Licence: fonts/OFL.txt) so names and symbols print as entered.
const printer = new PdfPrinter({ Noto: { normal: font('NotoSans-Regular.ttf'), bold: font('NotoSans-Bold.ttf'), italics: font('NotoSans-Regular.ttf'), bolditalics: font('NotoSans-Bold.ttf') } });
const LOGO = (() => { try { return fs.readFileSync(path.join(ROOT, 'brand', 'clear-logo.svg'), 'utf8'); } catch { return null; } })();
export const BETA = 'Beta – independently checked, not yet expert-certified';
const KIND_LABEL = { room: 'room / area', equipment: 'equipment', product: 'product' };
const refLabel = (x) => (x.code ? x.code + ' ' : '') + x.name;
const evText = (ev) => [].concat(ev || []).map((e) => (typeof e === 'string' ? e : (e.type ? e.type + ': ' : '') + e.what)).join('; ');

/** Returns the PDF (Buffer) of one audit. a: the stored audit row (config, answers, header parsed). product: the name printed
 *  (web/ demo: Medhanta Audit Checklist; platform/: Medhanta CLEAR). */
export function auditPdf(DATA, a, { printedBy = '', product = 'Medhanta Audit Checklist' } = {}) {
  const ITEM = new Map(DATA.items.map((x) => [x.id, x]));
  const cfg = a.config; const ans = a.answers || {}; const mode = modeOf(cfg); const A = ANSWERS[mode];
  const beta = mode === 'points' && DATA.points_status === 'beta';
  const lines = auditLines(DATA, cfg); const s = lineStats(lines, ans);
  const pointRefs = (p) => [...new Set(p.clauses.map((c) => ITEM.get(c.item)?.ref).filter(Boolean))];
  const hd = a.header || {};

  const body = [[{ text: 'Reference', style: 'th' }, { text: mode === 'points' ? 'Audit point' : 'Check point (regulation text)', style: 'th' }, { text: 'Answer', style: 'th' }, { text: A.note, style: 'th' }]];
  const groups = new Map(DATA.areas.map((x) => [x, []]));
  for (const l of lines) groups.get(l.area)?.push(l);
  for (const [area, ls] of groups) {
    if (!ls.length) continue;
    body.push([{ text: AREA_NAMES[area] || area, colSpan: 4, style: 'area' }, '', '', '']);
    for (const l of ls) {
      const v = ans[l.key] || {}; let ref, text;
      if (l.kind === 'company') { ref = 'Company item' + (l.company.ref ? ' ' + l.company.ref : ''); text = (l.company.title ? l.company.title + ': ' : '') + l.text; }
      else if (l.kind === 'other') { ref = l.item.ref; text = 'Other requirement (check the clause): ' + l.text; }
      else if (l.kind === 'unit') { ref = l.item.ref + (l.item.refs?.length ? '\nAlso: ' + l.item.refs.join(' · ') : ''); text = l.text; }
      else { ref = pointRefs(l.point).join('\n'); text = (l.point.modality === 'should' ? '(Recommended) ' : '') + l.point.question + (l.point.verify ? '\nVerify: ' + l.point.verify : '') + (l.point.evidence?.length ? '\nEvidence: ' + evText(l.point.evidence) : ''); }
      const names = (v.links || []).map((x) => `${KIND_LABEL[x.kind] || x.kind}: ${refLabel(x)}`).join('; ');
      const fill = POS.has(v.a) ? '#e4f5ea' : NEG.has(v.a) ? '#fdebe9' : null;
      body.push([{ text: ref, style: 'ref' }, text, { text: (v.a || '–') + (v.grade ? ` (${v.grade})` : ''), fillColor: fill, bold: !!v.a },
        [v.note, names && 'Names: ' + names].filter(Boolean).join('\n')]);
    }
  }
  const removed = Object.entries(cfg.removed || {});
  const remName = (k) => ITEM.get(k)?.ref || (DATA.points || []).find((p) => 'P:' + p.id === k)?.question
    || (k.startsWith('O:') ? 'Other requirement: ' + (ITEM.get(k.slice(2).split('#')[0])?.ref || '') : k);
  const info = [a.site && 'Site: ' + a.site, a.auditor && 'Auditor: ' + a.auditor, hd.auditees?.length && 'Auditees: ' + hd.auditees.map((x) => x.name).join(', '),
    hd.rooms?.length && 'Rooms / areas: ' + hd.rooms.map(refLabel).join(', '), a.audit_date && 'Date: ' + a.audit_date, 'Status: ' + a.status].filter(Boolean).join(' · ');
  const printed = new Date().toISOString().replace('T', ' ').slice(0, 16) + ' UTC';
  const def = {
    pageSize: 'A4', pageMargins: [32, 40, 32, 44],
    info: { title: a.name, creator: product, producer: product },
    defaultStyle: { font: 'Noto', fontSize: 8, lineHeight: 1.15 },
    header: beta ? { text: 'Audit points: ' + BETA, fontSize: 7, color: '#8a5a00', margin: [32, 18, 32, 0] } : undefined,
    footer: (page, pages) => ({ columns: [{ text: `${product} · ${a.name}`, fontSize: 7, color: '#777' }, { text: `Page ${page} of ${pages}`, alignment: 'right', fontSize: 7, color: '#777' }], margin: [32, 12, 32, 0] }),
    content: [
      LOGO ? { svg: LOGO, width: 130, margin: [0, 0, 0, 8] } : null,
      { text: a.name, style: 'h1' },
      { text: info, margin: [0, 0, 0, 4] },
      beta ? { text: 'Audit points: ' + BETA, bold: true, color: '#8a5a00', margin: [0, 0, 0, 4] } : null,
      { text: `Template: ${a.template_name} · Markets: ${cfg.markets.map((m) => MARKETS[m]?.label || m).join(', ')} · Plant types: ${['general GMP', ...(cfg.plants || [])].join(', ')}`, fontSize: 7.5, margin: [0, 0, 0, 4] },
      { text: `${s.total} ${mode === 'points' ? 'lines (audit points + other requirements)' : 'check points'}: ${mode === 'points' ? 'Compliant/Yes' : 'Yes'} ${s.yes} · ${mode === 'points' ? 'Not compliant/No' : 'No'} ${s.no} · N/A ${s.na} · not answered ${s.total - s.yes - s.no - s.na}`, bold: true, margin: [0, 0, 0, 8] },
      { table: { headerRows: 1, widths: [78, '*', 52, 120], body, dontBreakRows: false }, layout: { hLineColor: '#dddddd', vLineColor: '#dddddd', paddingTop: () => 2, paddingBottom: () => 2 } },
      removed.length ? [{ text: 'Removed from the template', style: 'h2' },
        { table: { headerRows: 1, widths: [160, '*'], body: [[{ text: 'Removed', style: 'th' }, { text: 'Reason', style: 'th' }], ...removed.map(([k, why]) => [remName(k), why])] }, layout: { hLineColor: '#dddddd', vLineColor: '#dddddd' } }] : null,
      { text: `Printed ${printed}${printedBy ? ' by ' + printedBy : ''} · ${product} · library ${a.data_version}. Not affiliated with or endorsed by CDSCO, the European Commission, US FDA, WHO or PIC/S. WHO and PIC/S are cited by clause number only (text not reproduced, licence).`, fontSize: 7, color: '#666', margin: [0, 10, 0, 0] },
    ].filter(Boolean),
    styles: {
      h1: { fontSize: 15, bold: true, margin: [0, 0, 0, 4] }, h2: { fontSize: 11, bold: true, margin: [0, 12, 0, 4] },
      th: { bold: true, color: '#ffffff', fillColor: '#e8500f' }, area: { bold: true, fillColor: '#f3efec', fontSize: 9 }, ref: { fontSize: 7.5 },
    },
  };
  return new Promise((ok, bad) => {
    const doc = printer.createPdfKitDocument(def); const parts = [];
    doc.on('data', (c) => parts.push(c)); doc.on('end', () => ok(Buffer.concat(parts))); doc.on('error', bad);
    doc.end();
  });
}
