import json, sys
sys.stdout.reconfigure(encoding='utf-8')
d = json.load(open(r'D:\deepseek-harness\default-workspace\f6chem\data\4b.json', encoding='utf-8'))
print('TOP:', list(d.keys()) if isinstance(d, dict) else type(d))
secs = d['sections'] if isinstance(d, dict) and 'sections' in d else d
for s in secs:
    print('---', s.get('id'), '|', s.get('title'), '| pts=', len(s.get('points', [])))
    for p in s.get('points', []):
        print('   ', p.get('id'), '|', p.get('title'))