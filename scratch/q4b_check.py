# -*- coding: utf-8 -*-
import json, sys, collections
sys.stdout.reconfigure(encoding='utf-8')
BASE = r'D:\deepseek-harness\default-workspace\f6chem'
q = json.load(open(BASE + r'\quiz\4b.json', encoding='utf-8'))
d = json.load(open(BASE + r'\data\4b.json', encoding='utf-8'))

err = []
if q.get('topic') != '4b': err.append('topic 錯')
qs = q['questions']
print('總題數:', len(qs))

valid = {p['id']: (s['id'], p['title']) for s in d['sections'] for p in s.get('points', [])}

t = collections.Counter(x['type'] for x in qs)
print('類型:', dict(t), ' 比例: mc %.0f%% tf %.0f%% fill %.0f%%' % (
    100*t['mc']/len(qs), 100*t['tf']/len(qs), 100*t['fill']/len(qs)))
if not (22 <= len(qs) <= 26): err.append('題數超出 22-26')

for i, x in enumerate(qs, 1):
    if x['id'] != '4b-q%d' % i: err.append('id 不連續: %s' % x['id'])
    if x.get('point') not in valid: err.append('point 不存在: %s' % x.get('point'))
    if not x.get('q'): err.append('缺題幹 %s' % x['id'])
    if not x.get('explanation'): err.append('缺解析 %s' % x['id'])
    tp = x['type']
    if tp == 'mc':
        o = x.get('options')
        if not isinstance(o, list) or len(o) != 4: err.append('%s 選項非 4 個' % x['id'])
        a = x.get('answer')
        if not isinstance(a, int) or not (0 <= a <= 3): err.append('%s answer 非 0-3 索引' % x['id'])
        if isinstance(o, list) and len(set(o)) != len(o): err.append('%s 選項重複' % x['id'])
    elif tp == 'tf':
        if not isinstance(x.get('answer'), bool): err.append('%s answer 非布林' % x['id'])
    elif tp == 'fill':
        if '____' not in x['q']: err.append('%s 缺 ____' % x['id'])
        a = x.get('answer')
        if not isinstance(a, (str, list)) or (isinstance(a, list) and not a): err.append('%s fill answer 格式錯' % x['id'])
        if isinstance(a, list) and len(a) != len(set(a)): err.append('%s fill 備選重複' % x['id'])
    else:
        err.append('%s 未知 type=%s' % (x['id'], tp))
    if '（OCR 不清）' in x.get('q','') or 'OCR' in x.get('q',''): err.append('%s 題幹含 OCR 標記' % x['id'])

tfq = [x for x in qs if x['type'] == 'tf']
print('tf: True=%d False=%d' % (sum(1 for x in tfq if x['answer']), sum(1 for x in tfq if not x['answer'])))

sec = collections.Counter(valid[x['point']][0] for x in qs if x.get('point') in valid)
print('section 覆蓋:')
for s in d['sections']:
    print('  %s %-14s %d 題 %s' % (s['id'], s['title'], sec.get(s['id'], 0), 'OK' if sec.get(s['id'],0) >= 2 else '不足'))
    if sec.get(s['id'], 0) < 2: err.append('%s 少於 2 題' % s['id'])

pc = collections.Counter(x['point'] for x in qs)
print('重複 point 最多的:', pc.most_common(3))
print('未出題 point:', sorted(set(valid) - set(pc)))

print('\n驗證結果:', '全部通過' if not err else err)
print('檔案大小:', __import__('os').path.getsize(BASE + r'\quiz\4b.json'), 'bytes')