import re, json
html = open('gh-pages/index.html', encoding='utf-8').read()
bio32_idx = html.find('"id":"bio32"')
if bio32_idx >= 0:
    ctx = html[bio32_idx:bio32_idx+3000]
    tags_matches = re.findall(r'"tags"\s*:\s*\[[^\]]*\]', ctx)
    print('All tags fields near bio32:')
    for m in tags_matches[:10]:
        print('  ', m[:120])
else:
    print('bio32 id not found')
