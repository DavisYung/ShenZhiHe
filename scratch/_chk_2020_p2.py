# -*- coding: utf-8 -*-
import json, sys, re, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE = r"C:\Users\guomi\OneDrive\文件\deepseek-harness\default-workspace\f6chem\scratch"
MAP = BASE + r"\map\2020_p2.json"
CAT = BASE + r"\pp\catalog.tsv"

raw = open(MAP, 'rb').read()
assert b'\xef\xbf\xbd' not in raw, 'output contains U+FFFD bytes'

data = json.load(open(MAP, encoding='utf-8'))
assert data['year'] == 2020

cat_ids = set()
for line in open(CAT, encoding='utf-8'):
    line = line.rstrip('\n')
    if not line:
        continue
    cat_ids.add(line.split('\t')[0])

errors = []
used = set()
refs = []
for m in data['mappings']:
    ref, pts, focus = m['ref'], m['points'], m['focus']
    refs.append(ref)
    if not re.match(r'^2020-P2[A-C]-Q\d(\([a-z0-9ivx]+\))+$', ref):
        errors.append('bad ref format: ' + ref)
    if not (1 <= len(pts) <= 3):
        errors.append('points count out of range: ' + ref)
    if len(focus) > 40:
        errors.append('focus >40 chars: %s (%d)' % (ref, len(focus)))
    if re.search(r'\ufffd', focus):
        errors.append('focus has U+FFFD: ' + ref)
    for p in pts:
        if p not in cat_ids:
            errors.append('unknown point id %s in %s' % (p, ref))
        used.add(p)

if len(refs) != len(set(refs)):
    errors.append('duplicate refs')

for k, words in data['kw'].items():
    if k not in used:
        errors.append('kw key not in mappings: ' + k)
    if not (1 <= len(words) <= 8):
        errors.append('kw list length out of range: ' + k)
    for w in words:
        if not (2 <= len(w) <= 8):
            errors.append('kw word length %d (not 2-8): %s / %s' % (len(w), k, w))
        if '\ufffd' in w:
            errors.append('kw has U+FFFD: ' + k)

print('units:', len(data['mappings']))
print('refs:', ', '.join(sorted(set(r.split('-Q')[1][0] if False else r for r in refs))))
print('distinct points:', len(used))
print('kw keys:', len(data['kw']), 'kw words:', sum(len(v) for v in data['kw'].values()))
if errors:
    print('ERRORS:')
    for e in errors:
        print(' -', e)
    sys.exit(1)
print('ALL OK')
