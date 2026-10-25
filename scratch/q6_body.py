import json, sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
BASE = r'D:\deepseek-harness\default-workspace\f6chem'
d = json.load(open(os.path.join(BASE, 'data', '6.json'), encoding='utf-8'))
want = sys.argv[1].split(',') if len(sys.argv) > 1 else None
for s in d['sections']:
    for p in s.get('points', []):
        pid = p.get('id')
        if want and pid not in want and s['id'] not in want:
            continue
        print('###', pid, '|', p.get('title'))
        print(p.get('body') or '')
        print()