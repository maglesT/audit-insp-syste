"""WHO / PIC/S text scan (lead 20 Nov, before any push). Usage: python3 -I whoscan.py [--points | --files]
10-word runs of all WHO / PIC/S clause texts (merged/sources.json, read only for this comparison) minus runs that also
occur in any SHOWN text (Schedule M / FDA / EU clauses, item source_text, checklist texts incl. tables / also_texts).
--points: ids of points / other requirements whose own wording contains such a run (-> who-hits.json)
--files : tracked files containing such a run."""
import json, re, subprocess, sys, collections
W = lambda s: re.findall(r"[a-z0-9]+", s.lower())
def sh(ws, n=10): return {" ".join(ws[i:i + n]) for i in range(len(ws) - n + 1)}
def only_set():
    S = json.load(open('/root/audit-admin/merged/sources.json')); ck = json.load(open('/root/audit-admin/merged/checklist.json'))
    prot, shown = set(), set()
    for c in S['clauses'].values():
        (prot if c.get('regulator') in ('WHO', 'PIC/S') else shown).update(sh(W(c.get('text', ''))))
    for it in S['items'].values(): shown.update(sh(W(it.get('source_text', ''))))
    for it in ck: shown.update(sh(W(json.dumps({k: it.get(k) for k in ('text', 'title', 'lead', 'tables', 'also_texts')}))))
    return prot - shown
def hit(text, only):
    ws = W(text); return any(" ".join(ws[i:i + 10]) in only for i in range(len(ws) - 9))
if __name__ == "__main__":
    only = only_set()
    if "--files" in sys.argv:
        files = [f for f in subprocess.run(['git', 'ls-files'], capture_output=True, text=True).stdout.split('\n') if f]
        bad = [f for f in files if hit(open(f, encoding='utf-8', errors='ignore').read(), only)]
        print(json.dumps({"tracked_files": len(files), "files_with_hits": len(bad), "examples": bad[:20]}, indent=1))
    else:
        d = json.load(open('full/draft/drafts.json'))
        ids = [p['id'] for p in d['points'] if hit(p['question'] + ' ' + p['verify'] + ' ' + json.dumps(p['evidence']), only)]
        ids += [x['unit'] for x in d['no_point'] if hit(x['reason'], only)]
        json.dump(ids, open('who-hits.json', 'w'), indent=1); print(len(ids), ids)
