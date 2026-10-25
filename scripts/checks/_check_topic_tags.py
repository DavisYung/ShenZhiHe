import re, json
html = open('gh-pages/index.html', encoding='utf-8').read()

# Check if topic-level tags exist in embedded data
bio32_idx = html.find('"id":"bio32"')
if bio32_idx >= 0:
    ctx = html[bio32_idx:bio32_idx+3000]
    # Look for topic-level tags (right after title and pdf)
    topic_tags_match = re.search(r'"tags"\s*:\s*\[[^\]]*\]', ctx)
    if topic_tags_match:
        print("Topic-level tags found:", topic_tags_match.group())
    else:
        print("No topic-level tags found near bio32 id")
        # Show the first 500 chars after "id":"bio32"
        print("Context:", ctx[:500])
else:
    print("bio32 id not found")
