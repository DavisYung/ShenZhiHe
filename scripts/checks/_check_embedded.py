import re, json
html = open('gh-pages/index.html', encoding='utf-8').read()
# Find the embedded data for bio32
bio32_idx = html.find('"id":"bio32"')
if bio32_idx >= 0:
    ctx = html[bio32_idx-200:bio32_idx+500]
    print("bio32 embedded data context:")
    print(ctx[:700])
else:
    print("bio32 not found in embedded data")

# Also check if tags field exists anywhere
tag_fields = re.findall(r'"tags"\s*:\s*\[[^\]]*\]', html)
print("\nNumber of 'tags' fields in HTML:", len(tag_fields))
for tf in tag_fields[:5]:
    print("  ", tf[:80])
