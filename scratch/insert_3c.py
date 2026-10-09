# -*- coding: utf-8 -*-
"""把 3c 插入 subject.json topics（排在 3b 之後），並更新描述統計。"""
import io, json, sys

sys.stdout.reconfigure(encoding="utf-8")
P = "f6chem/data/chem/subject.json"
d = json.load(io.open(P, encoding="utf-8"))
t = d.get("topics") or []
if "3c" not in t:
    i = t.index("3b") + 1
    t.insert(i, "3c")
    d["topics"] = t
n = len(t)
d["description"] = "%d 個課題、各有獨立章節；知識點之間互相串連，學到哪裡都能找到關聯，還可以隨時測驗自己。" % n
d["source"] = "24-27 F6 化學共用資料夾 · %d 份教師版筆記 PDF" % n
with io.open(P, "w", encoding="utf-8") as f:
    json.dump(d, f, ensure_ascii=False, indent=1)
    f.write("\n")
print("topics:", d["topics"])
