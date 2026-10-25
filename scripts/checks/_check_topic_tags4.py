import re, json

html = open('gh-pages/index.html', encoding='utf-8').read()

# Check if topic-level "tags" field exists anywhere
topic_tag_pattern = re.compile(r'"tags"\s*:\s*\["[^"]*"\]')
all_topic_tags = topic_tag_pattern.findall(html)
print("Topic-level tags in HTML:", all_topic_tags[:20])

# Check specifically near bio32
bio32_idx = html.find('"id":"bio32"')
if bio32_idx >= 0:
    ctx = html[bio32_idx:bio32_idx+3000]
    topic_tags_near = topic_tag_pattern.findall(ctx[:3000])
    print("Topic tags near bio32:", topic_tags_near[:5])
    
    # Check if "tags" appears right after "pdf" field for bio32
    pdf_match = re.search(r'"pdf"\s*:\s*"[^"]*"', ctx[:500])
    if pdf_match:
        print("Found pdf field:", pdf_match.group())
        after_pdf = ctx[pdf_match.end():pdf_match.end()+100]
        print("After pdf:", after_pdf[:100])
