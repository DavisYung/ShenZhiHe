import re, json
html = open('gh-pages/index.html', encoding='utf-8').read()
bio32_idx = html.find('"id":"bio32"')
if bio32_idx >= 0:
    ctx = html[bio32_idx:bio32_idx+2000]
    print("bio32 context:")
    print(ctx[:2000])
else:
    print("bio32 not found")
