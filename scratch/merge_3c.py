# -*- coding: utf-8 -*-
"""合併 3c 兩份轉錄為正式 data/chem/3c.json。

- title 用「焓變」（照 PDF 命名慣例：3A～～有機化合物 → 有機化合物）
- page 轉 int（與既有課題一致）
- 全量校驗：id 唯一、s 連續、p 連續、必填欄位、無 \\ufffd
成功後刪除中間檔。
"""
import io, json, os, sys

sys.stdout.reconfigure(encoding="utf-8")
D = "f6chem/data/chem"

parts = [json.load(io.open(os.path.join(D, n), encoding="utf-8"))
         for n in ("_3c_part1.json", "_3c_part2.json")]

sections = []
for p in parts:
    sections += p["sections"]

# page → int
for s in sections:
    for pt in s["points"]:
        if isinstance(pt.get("page"), str) and pt["page"].isdigit():
            pt["page"] = int(pt["page"])

# 校驗
ids = [s["id"] for s in sections]
assert ids == ["3c-s%d" % i for i in range(1, len(ids) + 1)], ids
allp = []
for s in sections:
    pids = [p["id"] for p in s["points"]]
    assert pids == ["%s-p%d" % (s["id"], i + 1) for i in range(len(pids))], (s["id"], pids)
    allp += pids
    for p in s["points"]:
        for k in ("title", "body", "page", "tags"):
            assert p.get(k) not in (None, ""), (p["id"], k)
        assert isinstance(p["page"], int), p["id"]
assert len(allp) == len(set(allp))
blob = json.dumps(sections, ensure_ascii=False)
assert chr(0xfffd) not in blob
print("validated: %d sections, %d points, pages %s-%s"
      % (len(sections), len(allp),
         min(p["page"] for s in sections for p in s["points"]),
         max(p["page"] for s in sections for p in s["points"])))

topic = {
    "id": "3c",
    "title": "焓變",
    "pdf": "3C 化學筆記～～焓變 TeacherVer.pdf",
    "sections": sections,
}
out = os.path.join(D, "3c.json")
with io.open(out, "w", encoding="utf-8") as f:
    json.dump(topic, f, ensure_ascii=False, indent=1)
    f.write("\n")
print("written", out, os.path.getsize(out), "bytes")

# 復讀驗證
again = json.load(io.open(out, encoding="utf-8"))
assert again["id"] == "3c" and len(again["sections"]) == len(sections)
print("re-read OK")

for n in ("_3c_part1.json", "_3c_part2.json", "_3c_check.py", "_check3c.py"):
    p = os.path.join(D, n)
    if os.path.exists(p):
        os.remove(p)
        print("removed", n)
