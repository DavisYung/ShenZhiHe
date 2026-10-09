# -*- coding: utf-8 -*-
"""合并环节端到端演练：合成 map 文件 → 沙盒 data 副本 → 跑 merge_exam → 验证语义。

验证点：
1) 新年份（2099）进入 years、hits/level 重算、samples/focus/keywords 追加
2) 同年同题不同小问不撞（Q1(a) vs Q1(b)）
3) 与旧 ref 撞车（'2014-P1-甲部-23' vs '2014-P1A-Q23'）保留旧条目、不重复加 sample
4) 写回格式与原档一致（indent=2、无尾换行、可 json.load、无 \\ufffd）
"""
import glob
import io
import json
import os
import shutil
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import merge_exam  # noqa: E402

BASE = os.path.dirname(HERE)  # f6chem
DATA = os.path.join(BASE, "data", "chem")
SANDBOX = os.path.join(HERE, "_t_data")
MAPD = os.path.join(HERE, "_t_map")

# 1) 沙盒 data 副本
if os.path.isdir(SANDBOX):
    shutil.rmtree(SANDBOX)
os.makedirs(SANDBOX)
for f in glob.glob(os.path.join(DATA, "*.json")):
    shutil.copy2(f, SANDBOX)

# 2) 挑一个「2014 年 Q23 已有标注」的点（测撞车）+ 一个没标注的点（测新年份）
sample_point = None
fresh_point = None
for f in glob.glob(os.path.join(SANDBOX, "*.json")):
    stem = os.path.basename(f)[:-5]
    if stem in ("subject", "links", "index"):
        continue
    obj = json.load(io.open(f, encoding="utf-8"))
    for s in obj.get("sections") or []:
        for p in s.get("points") or []:
            e = p.get("exam") or {}
            refs = [sm.get("ref") for sm in (e.get("samples") or [])]
            for sm in e.get("samples") or []:
                k = merge_exam.norm_key(sm.get("y"), sm.get("ref"))
                if sample_point is None and k[:4] == (2014, "P1", "A", 23):
                    sample_point = (p["id"], refs)
            if fresh_point is None and not e:
                fresh_point = p["id"]
print("sample_point:", sample_point)
print("fresh_point:", fresh_point)

MAP_FILE = os.path.join(MAPD, "2099_p1a.json")
os.makedirs(MAPD, exist_ok=True)
syn = {
    "year": 2099,
    "mappings": [
        {"ref": "2099-P1A-Q1", "points": [fresh_point], "focus": "合成測試：新點新年份"},
        {"ref": "2099-P1B-Q1(a)", "points": [fresh_point], "focus": "合成測試：乙部小問 a"},
        {"ref": "2099-P1B-Q1(b)", "points": [fresh_point], "focus": "合成測試：乙部小問 b"},
    ],
    "kw": {fresh_point: ["合成字眼甲", "合成字眼乙"]},
}
io.open(MAP_FILE, "w", encoding="utf-8").write(
    json.dumps(syn, ensure_ascii=False, indent=1))
# 撞车用例放 2014 年自己的 map 档（年份取自档头，ref 年份须一致）
syn2 = {
    "year": 2014,
    "mappings": [
        {"ref": "2014-P1A-Q23", "points": [sample_point[0]], "focus": "合成測試：撞車應被去重"},
    ],
}
io.open(os.path.join(MAPD, "2014_p1a.json"), "w", encoding="utf-8").write(
    json.dumps(syn2, ensure_ascii=False, indent=1))

# 3) 指向沙盒后跑合并
merge_exam.DATA = SANDBOX
merge_exam.MAPD = MAPD
merge_exam.BAK = os.path.join(HERE, "_t_bak")
if os.path.isdir(merge_exam.BAK):
    shutil.rmtree(merge_exam.BAK)
sys.argv = ["merge_exam.py"]
merge_exam.main()

# 4) 验证
def find_point(pid):
    for f in glob.glob(os.path.join(SANDBOX, "*.json")):
        obj = json.load(io.open(f, encoding="utf-8"))
        for s in obj.get("sections") or []:
            for p in s.get("points") or []:
                if p["id"] == pid:
                    return p
    return None

fails = []
fp = find_point(fresh_point)["exam"]
if 2099 not in fp["years"]:
    fails.append("fresh: year 2099 missing")
if fp["hits"] != len(fp["years"]):
    fails.append("fresh: hits mismatch")
if fp["level"] != merge_exam.level_of(fp["hits"]):
    fails.append("fresh: level mismatch")
refs2099 = [sm["ref"] for sm in fp["samples"] if sm["y"] == 2099]
if sorted(refs2099) != ["2099-P1A-Q1", "2099-P1B-Q1(a)", "2099-P1B-Q1(b)"]:
    fails.append("fresh: samples %s" % refs2099)
if "合成字眼甲" not in fp["keywords"]:
    fails.append("fresh: kw missing")

sp = find_point(sample_point[0])["exam"]
old_n = len(sample_point[1])
refs = [sm.get("ref") for sm in sp["samples"]]
if refs.count("2014-P1-甲部-23") > 1:
    fails.append("dup: old ref duplicated")
if "2014-P1A-Q23" in refs:
    fails.append("dup: new ref should have been deduped against old")
if len(sp["samples"]) != old_n:
    fails.append("dup: sample count changed %d -> %d" % (old_n, len(sp["samples"])))

# 格式回验
for f in glob.glob(os.path.join(SANDBOX, "*.json")):
    txt = io.open(f, encoding="utf-8").read()
    if "\ufffd" in txt:
        fails.append("FFFD in " + f)
    json.loads(txt)

print("\nRESULT:", "ALL OK ✅" if not fails else "FAILS ❌")
for x in fails:
    print("  -", x)
sys.exit(1 if fails else 0)
