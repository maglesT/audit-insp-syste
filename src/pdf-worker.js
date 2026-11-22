// Builds an audit PDF off the main thread (a big audit takes seconds of pure layout work: the server stays responsive).
// One PDF at a time per process (memory: a 500-page report needs a few hundred MB); a short queue, then "busy".
import { Worker, isMainThread, parentPort, workerData } from 'node:worker_threads';
import fs from 'node:fs';
import { fileURLToPath } from 'node:url';

if (!isMainThread) {
  const { auditPdf } = await import('./pdf.js');
  const DATA = JSON.parse(fs.readFileSync(workerData.dataFile));
  const buf = await auditPdf(DATA, workerData.audit, workerData.opts);
  parentPort.postMessage(buf, [buf.buffer]);
}

const MAX_QUEUE = 4;
let running = Promise.resolve(); let waiting = 0;
export function pdfInWorker(dataFile, audit, opts = {}) {
  if (waiting >= MAX_QUEUE) return Promise.reject(Object.assign(new Error('The PDF service is busy. Please try again in a minute.'), { busy: true }));
  waiting++;
  const job = running.then(() => new Promise((ok, bad) => {
    const w = new Worker(fileURLToPath(import.meta.url), { workerData: { dataFile, audit, opts } });
    const timer = setTimeout(() => { w.terminate(); bad(new Error('PDF timed out')); }, 120_000);
    w.once('message', (b) => { clearTimeout(timer); ok(Buffer.from(b.buffer, b.byteOffset, b.byteLength)); });
    w.once('error', (e) => { clearTimeout(timer); bad(e); });
    w.once('exit', (c) => { clearTimeout(timer); if (c) bad(new Error('PDF worker stopped (' + c + ')')); });
  })).finally(() => { waiting--; });
  running = job.catch(() => {});
  return job;
}
