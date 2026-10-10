# -*- coding: utf-8 -*-
import io, json

# 核物理链接文件路径
LINKS = r"D:\物理相关\核物理学\nuclear\links.json"

# 收集所有 knowledge point id
DATA = r"D:\物理相关\核物理学\nuclear\data"
all_ids = set()
for n in sorted(os.listdir(DATA)):
    if not n.endswith(".json") or n in ("subject.json", "links.json"):
        continue
    try:
        t = json.load(io.open(os.path.join(DATA, n), encoding="utf-8"))
    except Exception:
        continue
    if not isinstance(t, dict):
        continue
    for s in t.get("sections") or []:
        for pt in s.get("points") or []:
            if pt.get("id"):
                all_ids.add(pt["id"])

print("知识点 id 總計: %d" % len(all_ids))

links = []

# 跨科：核物理 → 力学
if "nuclear3-s1-p1" in all_ids and "mech6-s1-p1" in all_ids:
    links.append({
        "from": "nuclear3-s1-p1",
        "to": "mech6-s1-p1",
        "label": "能量守恆定律：核分裂釋放的能量可轉化為機械能與熱能"
    })

# 跨科：核物理 → 热学
if "nuclear2-s1-p2" in all_ids and "heat3-s1-p1" in all_ids:
    links.append({
        "from": "nuclear2-s1-p2",
        "to": "heat3-s1-p1",
        "label": "電離輻射的熱效應原理与电热水器原理相似：均以電流/輻射帶動物質温度升高"
    })

with io.open(LINKS, "w", encoding="utf-8") as f:
    json.dump(links, f, ensure_ascii=False, indent=1)
    f.write("\n")

print("串連 %d 條" % len(links))
print("已寫出", LINKS)