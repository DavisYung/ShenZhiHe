# -*- coding: utf-8 -*-
import io, re, sys
src = r'C:\Users\guomi\OneDrive\文件\deepseek-harness\default-workspace\f6chem\notes-raw\2B 化學筆記～～氧化還原 TeacherVer.txt'
t = io.open(src, encoding='utf-8', errors='replace').read()
pages = t.split('\f')
out = []
keys = ['1.5', '180+', '0.5', '3.7', '500+', '1200', '220']
for i, p in enumerate(pages):
    hits = [k for k in keys if k in p]
    if hits:
        out.append('page %d hits=%s :: %r' % (i + 1, hits, p.strip()[:200]))
io.open(r'C:\Users\guomi\OneDrive\文件\deepseek-harness\default-workspace\f6chem\data\tnum.txt', 'w', encoding='utf-8').write('\n'.join(out) or 'NONE')
print('done', len(out))
