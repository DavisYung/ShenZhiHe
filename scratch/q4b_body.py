import json, sys
sys.stdout.reconfigure(encoding='utf-8')
d = json.load(open(r'D:\deepseek-harness\default-workspace\f6chem\data\4b.json', encoding='utf-8'))
want = set(sys.argv[1].split(',')) if len(sys.argv) > 1 else None
for s in d['sections']:
    for p in s.get('points', []):
        if want and p['id'] not in want:
            continue
        print('=== ', p['id'], '|', p['title'])
        print(json.dumps({k: v for k, v in p.items() if k not in ('id', 'title')}, ensure_ascii=False, indent=1))
        print()