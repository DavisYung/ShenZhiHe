# -*- coding: utf-8 -*-
"""Independent re-check of quiz/6.json (does not reuse q6_build.py logic)."""
import json, io, os, sys, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
BASE = r'D:\deepseek-harness\default-workspace\f6chem'

src = json.load(open(os.path.join(BASE, 'data', '6.json'), encoding='utf-8'))
points = {}
for s in src['sections']:
    for p in s.get('points', []):
        points[p['id']] = s['id']

q = json.load(open(os.path.join(BASE, 'quiz', '6.json'), encoding='utf-8'))
assert q['topic'] == '6', 'topic mismatch'
L = q['questions']
print('file parses OK, topic =', q['topic'], '| questions =', len(L))
print('in 25-30 band  :', 25 <= len(L) <= 30)

exp = ['6-q%d' % i for i in range(1, len(L) + 1)]
got = [x['id'] for x in L]
print('ids continuous :', got == exp)

bad = [x['id'] for x in L if x['point'] not in points]
print('points valid   :', not bad, bad or '')
print('no OCR in q    :', not [x['id'] for x in L if 'OCR' in x['q']])

c = collections.Counter(x['type'] for x in L)
print('types          : mc=%d tf=%d fill=%d  (%.0f%%/%.0f%%/%.0f%%)' % (
    c['mc'], c['tf'], c['fill'], c['mc'] / len(L) * 100,
    c['tf'] / len(L) * 100, c['fill'] / len(L) * 100))
tf = [x for x in L if x['type'] == 'tf']
print('tf bool/false  : %d / %d' % (sum(1 for x in tf if x['answer'] is True),
                                    sum(1 for x in tf if x['answer'] is False)))
mcbad = [x['id'] for x in L if x['type'] == 'mc'
         and not (isinstance(x['answer'], int) and not isinstance(x['answer'], bool)
                  and 0 <= x['answer'] <= 3 and len(x['options']) == 4
                  and len(set(x['options'])) == 4)]
print('mc schema OK   :', not mcbad, mcbad or '')
filbad = [x['id'] for x in L if x['type'] == 'fill'
          and not (isinstance(x['answer'], str)
                   or (isinstance(x['answer'], list) and x['answer']))
          and '____' in x['q']]
print('fill schema OK :', not filbad, filbad or '')
print('explanations   :', all(x.get('explanation', '').strip() for x in L))

per = collections.Counter(points[x['point']] for x in L)
print('section counts :', dict(sorted(per.items())))
print('every sec >= 2 :', all(v >= 2 for v in per.values()))
print('points used    : %d / %d distinct' % (len({x['point'] for x in L}), len(points)))