import json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
d = json.load(open(r'C:\Users\guomi\OneDrive\文件\deepseek-harness\default-workspace\f6chem\data\6.json', encoding='utf-8'))
print('top keys:', list(d.keys()))
for s in d['sections']:
    print('==', s.get('id'), s.get('title'))
    for p in s.get('points', []):
        body = p.get('body') or ''
        print('   ', p.get('id'), '|', p.get('title'), '| len=', len(body))