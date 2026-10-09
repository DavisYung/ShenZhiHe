# -*- coding: utf-8 -*-
"""校验新增題目 JSON：schema、ID 唯一、point 引用存在、無 U+FFFD。"""
import glob, io, json, sys

sys.stdout.reconfigure(encoding="utf-8")
ROOT = "f6chem"

# data 全部 point id
pts = set()
for f in glob.glob(ROOT + "/data/chem/*.json"):
    t = json.load(io.open(f, encoding="utf-8"))
    if not isinstance(t, dict):
        continue
    for s in t.get("sections", []):
        for p in s.get("points", []):
            pts.add(p["id"])

# 既有題目 id
exist = set()
for f in glob.glob(ROOT + "/quiz/chem/*.json"):
    if "_new_q_" in f:
        continue
    d = json.load(io.open(f, encoding="utf-8"))
    for q in d["questions"]:
        exist.add(q["id"])

ok = True
for f in sorted(glob.glob(ROOT + "/quiz/chem/_new_q_*.json")):
    d = json.load(io.open(f, encoding="utf-8"))
    ids = [q["id"] for q in d]
    dup_local = [i for i in set(ids) if ids.count(i) > 1]
    clash = [i for i in ids if i in exist]
    bad_point = [q["id"] for q in d if q.get("point") not in pts]
    bad_schema = []
    for q in d:
        t = q.get("type")
        if t == "mc":
            if not (isinstance(q.get("options"), list) and len(q["options"]) >= 2
                    and isinstance(q.get("answer"), int)
                    and 0 <= q["answer"] < len(q["options"])):
                bad_schema.append(q["id"])
        elif t == "tf":
            if not isinstance(q.get("answer"), bool):
                bad_schema.append(q["id"])
        else:
            bad_schema.append(q["id"])
        for k in ("id", "point", "q", "explanation"):
            if not q.get(k):
                bad_schema.append(q["id"])
    fffd = [q["id"] for q in d if "\ufffd" in json.dumps(q, ensure_ascii=False)]
    status = "OK" if not (dup_local or clash or bad_point or bad_schema or fffd) else "FAIL"
    if status == "FAIL":
        ok = False
    print("%-40s n=%-3d %s" % (f.split("/")[-1], len(d), status))
    for label, bad in (("dup_local", dup_local), ("clash_existing", clash),
                       ("bad_point", bad_point), ("bad_schema", bad_schema),
                       ("ufffd", fffd)):
        if bad:
            print("    %s: %s" % (label, bad))

print("\n總計新增:", end=" ")
tot = 0
for f in sorted(glob.glob(ROOT + "/quiz/chem/_new_q_*.json")):
    tot += len(json.load(io.open(f, encoding="utf-8")))
print(tot)
sys.exit(0 if ok else 1)
