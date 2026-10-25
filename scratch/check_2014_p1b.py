# -*- coding: utf-8 -*-
import json, sys, io

OUT = r"D:\deepseek-harness\default-workspace\f6chem\scratch\map\2014_p1b.json"
CAT = r"D:\deepseek-harness\default-workspace\f6chem\scratch\pp\catalog.tsv"

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
errs = []

raw = open(OUT, 'rb').read()
if b'\xef\xbf\xbd' in raw:
    errs.append('output contains U+FFFD bytes')

data = json.loads(raw.decode('utf-8'))
if data.get('year') != 2014:
    errs.append('year != 2014')

cat_ids = set()
for line in open(CAT, encoding='utf-8'):
    parts = line.rstrip('\n').split('\t')
    if parts and parts[0]:
        cat_ids.add(parts[0])

seen = set()
refs = set()
for m in data['mappings']:
    ref = m['ref']
    if ref in refs:
        errs.append('duplicate ref: ' + ref)
    refs.add(ref)
    if not m['points']:
        print('NOTE empty points: ' + ref)
    for p in m['points']:
        seen.add(p)
        if p not in cat_ids:
            errs.append('unknown point id %s in %s' % (p, ref))
    fl = m['focus']
    if len(fl) > 40:
        errs.append('focus >40 chars: %s (%d)' % (ref, len(fl)))

for k in data['kw']:
    if k not in seen:
        errs.append('kw key not in mappings: ' + k)
    for w in data['kw'][k]:
        if not (2 <= len(w) <= 8):
            errs.append('kw word length %d: %s/%s' % (len(w), k, w))

# 2014 p1b 乙部题号覆盖检查（按子问题粒度，题号 1-14 至少各出现一次）
qnums = set()
for r in refs:
    body = r.replace('2014-P1B-Q', '')
    num = body.split('(')[0]
    qnums.add(int(num))
missing_q = [n for n in range(1, 15) if n not in qnums]
if missing_q:
    errs.append('missing question numbers: %s' % missing_q)

print('units: %d' % len(data['mappings']))
print('questions covered: %s' % sorted(qnums))
print('distinct points: %d' % len(seen))
print('kw points: %d, kw words: %d' % (len(data['kw']), sum(len(v) for v in data['kw'].values())))
if errs:
    print('FAIL')
    for e in errs:
        print(' - ' + e)
else:
    print('PASS')
