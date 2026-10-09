# -*- coding: utf-8 -*-
"""為 3c 焓變追加跨課題串連（links.json）。"""
import io, json, sys

sys.stdout.reconfigure(encoding="utf-8")
P = "f6chem/data/chem/links.json"
links = json.load(io.open(P, encoding="utf-8"))
have = {(l["from"], l["to"]) for l in links} | {(l["to"], l["from"]) for l in links}

NEW = [
    {"from": "3c-s11-p2", "to": "2a-s14-p1", "label": "中和焓變建立在中和反應之上"},
    {"from": "3c-s7-p4", "to": "3a-s3-p1", "label": "燃燒焓變與烴的燃燒通式"},
    {"from": "3c-s5-p1", "to": "3a-s3-p1", "label": "斷鍵吸熱成鍵放熱決定反應熱"},
    {"from": "3c-s7-p7", "to": "2a-s14-p4", "label": "中和焓變的應用"},
]
added = 0
for n in NEW:
    if (n["from"], n["to"]) in have:
        print("skip existing", n["from"], n["to"])
        continue
    # 目標 point 必須存在
    links.append(n)
    added += 1

with io.open(P, "w", encoding="utf-8") as f:
    json.dump(links, f, ensure_ascii=False, indent=1)
    f.write("\n")
print("added %d, total %d" % (added, len(links)))
