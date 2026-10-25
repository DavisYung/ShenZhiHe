import re, json
html = open('gh-pages/index.html', encoding='utf-8').read()
bio32_idx = html.find('"id":"bio32"')
if bio32_idx >= 0:
    ctx = html[bio32_idx:bio32_idx+2000]
    # Find topic-level tags
    topic_tags = re.search(r'"pdf":\s*"[^"]*"\s*,\s*"tags"\s*:\s*\[[^\]]*\]', ctx)
    if topic_tags:
        print('Topic-level tags found:', topic_tags.group())
    else:
        print('No topic-level tags found after pdf field')
    print()
    print(ctx[:400])
else:
    print("bio32 id not found")
