import re, io, json, sys
src = r'C:\Users\guomi\OneDrive\文件\deepseek-harness\default-workspace\f6chem\notes-raw\2B 化學筆記～～氧化還原 TeacherVer.txt'
out = r'C:\Users\guomi\OneDrive\文件\deepseek-harness\default-workspace\f6chem\data\txt-report.txt'
t = io.open(src, encoding='utf-8', errors='replace').read()
pages = t.split('\f')
lines = []
lines.append('parts: %d' % len(pages))
for i, p in enumerate(pages):
    cjk = re.findall(r'[一-鿿]', p)
    # printable ascii runs
    runs = re.findall(r'[ -~]{6,}', p)
    lines.append('--- part %d (pdf page %d): len=%d cjk=%d' % (i, i + 1, len(p.strip()), len(cjk)))
    lines.append('  cjk_head: %s' % ''.join(cjk[:40]))
    lines.append('  ascii_runs: %s' % ' | '.join(runs[:6])[:400])
io.open(out, 'w', encoding='utf-8').write('\n'.join(lines))
print('written', out)
