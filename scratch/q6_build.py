# -*- coding: utf-8 -*-
import json, io, os, sys, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
BASE = r'D:\deepseek-harness\default-workspace\f6chem'

src = json.load(open(os.path.join(BASE, 'data', '6.json'), encoding='utf-8'))
valid_points = set()
for s in src['sections']:
    for p in s.get('points', []):
        valid_points.add(p['id'])

qs = []
for name in ['q6_part_a', 'q6_part_b', 'q6_part_c', 'q6_part_d']:
    qs.extend(json.load(open(os.path.join(BASE, 'scratch', name + '.json'), encoding='utf-8')))

# trim to the 25-30 band, keeping every section >= 2 questions and the 60/20/20 mix
DROP = {'6-q1', '6-q8', '6-q23', '6-q34'}  # 34 -> 30
qs = [q for q in qs if q['id'] not in DROP]

# renumber ids continuously
for i, q in enumerate(qs, 1):
    q['id'] = '6-q%d' % i

errs = []
if len(qs) != len({q['id'] for q in qs}):
    errs.append('duplicate ids')
for q in qs:
    t = q.get('type')
    if q.get('point') not in valid_points:
        errs.append('%s: bad point %r' % (q['id'], q.get('point')))
    for f in ('q', 'explanation', 'type', 'point'):
        if not str(q.get(f, '')).strip():
            errs.append('%s: empty %s' % (q['id'], f))
    if '（OCR 不清）' in q['q'] or 'OCR 不清' in q['q']:
        errs.append('%s: OCR flagged' % q['id'])
    if t == 'mc':
        if not isinstance(q.get('options'), list) or len(q['options']) != 4:
            errs.append('%s: mc needs 4 options' % q['id'])
        elif len(set(q['options'])) != 4:
            errs.append('%s: duplicate options' % q['id'])
        a = q.get('answer')
        if not isinstance(a, int) or isinstance(a, bool) or not (0 <= a <= 3):
            errs.append('%s: mc answer index bad' % q['id'])
    elif t == 'tf':
        if not isinstance(q.get('answer'), bool):
            errs.append('%s: tf answer not bool' % q['id'])
    elif t == 'fill':
        a = q.get('answer')
        if not (isinstance(a, str) or (isinstance(a, list) and a and all(isinstance(x, str) for x in a))):
            errs.append('%s: fill answer bad' % q['id'])
        if '____' not in q['q']:
            errs.append('%s: fill missing ____' % q['id'])
    else:
        errs.append('%s: unknown type %r' % (q['id'], t))

counts = collections.Counter(q['type'] for q in qs)
n = len(qs)
tfq = [q for q in qs if q['type'] == 'tf']
sec = collections.Counter(q['point'] for q in qs)
missing_sec = [s['id'] for s in src['sections']
               if sum(1 for q in qs if q['point'].startswith(s['id'] + '-')) < 2]
per_sec = {s['id']: sum(1 for q in qs if q['point'].startswith(s['id'] + '-'))
           for s in src['sections']}
tfs = collections.Counter(q['answer'] for q in tfq)

print('total       :', n)
print('mc/tf/fill  : %d / %d / %d' % (counts['mc'], counts['tf'], counts['fill']))
print('ratios      : mc %.0f%%  tf %.0f%%  fill %.0f%%' % (
    counts['mc'] / n * 100, counts['tf'] / n * 100, counts['fill'] / n * 100))
print('tf true/false: %d / %d' % (tfs[True], tfs[False]))
print('section cov :', per_sec)
print('missing sec :', missing_sec or 'none')
print('errors      :', errs or 'none')

if not errs:
    out = {'topic': '6', 'questions': qs}
    path = os.path.join(BASE, 'quiz', '6.json')
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    # reload verification
    d2 = json.load(open(path, encoding='utf-8'))
    print('WROTE + reload ok:', d2['topic'], len(d2['questions']), 'questions;',
          'last id =', d2['questions'][-1]['id'])