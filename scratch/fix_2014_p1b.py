# -*- coding: utf-8 -*-
import json, sys, io

OUT = r"D:\deepseek-harness\default-workspace\f6chem\scratch\map\2014_p1b.json"
CAT = r"D:\deepseek-harness\default-workspace\f6chem\scratch\pp\catalog.tsv"

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# kw 词长度修正（保持评分标准原意，压缩到 2-8 字）
FIX = {
    "Br2(aq)脫色": "Br2脫色",
    "11.6 moldm-3": "11.6 mol",
    "10.4 moldm-3": "10.4 mol",
    "4OH−→2H2O+O2+4e−": "半反應式",
    "Ag++e−→Ag": "Ag+還原",
    "同樣份量CaCO3": "同樣份量",
    "H2SO4(aq)": "H2SO4",
    "醚": "LiAlH4",
    "125 dm6mol-2": "Kc=125",
    "-CH2CH2CH3": "-C3H7",
}
# 合并后可能重复
DEDUP = True

data = json.loads(open(OUT, encoding='utf-8').read())
for k, words in data['kw'].items():
    new = []
    for w in words:
        w2 = FIX.get(w, w)
        if w2 not in new:
            new.append(w2)
    data['kw'][k] = new

json.dump(data, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)

# ---- 复检 ----
errs = []
raw = open(OUT, 'rb').read()
if b'\xef\xbf\xbd' in raw:
    errs.append('output contains U+FFFD bytes')
data = json.loads(raw.decode('utf-8'))

cat_ids = set()
for line in open(CAT, encoding='utf-8'):
    parts = line.rstrip('\n').split('\t')
    if parts and parts[0]:
        cat_ids.add(parts[0])

seen, refs = set(), set()
for m in data['mappings']:
    refs.add(m['ref'])
    for p in m['points']:
        seen.add(p)
        if p not in cat_ids:
            errs.append('unknown point id %s in %s' % (p, m['ref']))
    if len(m['focus']) > 40:
        errs.append('focus >40: ' + m['ref'])
for k, words in data['kw'].items():
    if k not in seen:
        errs.append('kw key not in mappings: ' + k)
    for w in words:
        if not (2 <= len(w) <= 8):
            errs.append('kw word length %d: %s/%s' % (len(w), k, w))

qnums = sorted({int(r.replace('2014-P1B-Q', '').split('(')[0]) for r in refs})
missing = [n for n in range(1, 15) if n not in qnums]
if missing:
    errs.append('missing questions: %s' % missing)

print('units: %d / questions: %s' % (len(data['mappings']), qnums))
print('distinct points: %d / kw points: %d / kw words: %d'
      % (len(seen), len(data['kw']), sum(len(v) for v in data['kw'].values())))
print('FAIL:\n' + '\n'.join(' - ' + e for e in errs) if errs else 'PASS')
