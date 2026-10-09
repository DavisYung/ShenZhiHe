# -*- coding: utf-8 -*-
"""把 _new_q_*.json 合併進正式題庫（1a/1b/1c.json）。

- 按 id 數字續號校驗（新題 id 必須從現有最大序號之後開始——已由 _check_new_q 保證不撞號）
- 合併後再次全量校驗（schema／point 引用／無 U+FFFD）
- 成功才刪除 _new_q_ 中間檔
"""
import glob, io, json, os, sys

sys.stdout.reconfigure(encoding="utf-8")
QDIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "quiz", "chem")

# data 全部 point id（最終校驗用）
DATA = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "chem")
pts = set()
for f in glob.glob(os.path.join(DATA, "*.json")):
    t = json.load(io.open(f, encoding="utf-8"))
    if not isinstance(t, dict):
        continue
    for s in t.get("sections", []):
        for p in s.get("points", []):
            pts.add(p["id"])

# 收集新題（依檔名排序保持 id 遞增）
new_by_topic = {}
for f in sorted(glob.glob(os.path.join(QDIR, "_new_q_*.json"))):
    for q in json.load(io.open(f, encoding="utf-8")):
        tid = q["id"].split("-")[0]
        new_by_topic.setdefault(tid, []).append(q)

merged_files = []
for tid, newqs in sorted(new_by_topic.items()):
    path = os.path.join(QDIR, tid + ".json")
    cur = json.load(io.open(path, encoding="utf-8"))
    old_ids = {q["id"] for q in cur["questions"]}
    clash = [q["id"] for q in newqs if q["id"] in old_ids]
    if clash:
        sys.exit("ID 衝突 %s: %s" % (tid, clash))
    cur["questions"].extend(newqs)
    merged_files.append((path, cur, len(newqs)))

# 先寫入（indent=1 與原檔一致）
for path, data, n in merged_files:
    with io.open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
        f.write("\n")
    print("merged %s: +%d -> %d 題" % (os.path.basename(path), n, len(data["questions"])))

# 全量複驗
ok = True
for path, data, _ in merged_files:
    ids = [q["id"] for q in data["questions"]]
    if len(ids) != len(set(ids)):
        print("FAIL dup id in", path); ok = False
    for q in data["questions"]:
        if q.get("point") not in pts:
            print("FAIL bad point", q["id"], q.get("point")); ok = False
        if "\ufffd" in json.dumps(q, ensure_ascii=False):
            print("FAIL fffd", q["id"]); ok = False
if not ok:
    sys.exit(1)
print("複驗通過")

# 清理中間檔
for f in glob.glob(os.path.join(QDIR, "_new_q_*.json")):
    os.remove(f)
    print("removed", os.path.basename(f))
