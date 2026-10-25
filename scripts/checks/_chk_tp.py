import json,sys,collections
sys.stdout.reconfigure(encoding="utf-8")
d=json.load(open("extras/phys/formulas.json",encoding="utf-8"))
# 统计每个分组内涉及哪些课题
for g in d["toback"]:
    tps=collections.Counter(it.get("tp") for it in g["items"])
    print(f'[{g["group"]}] {len(g["items"])} 条 -> 课题: {dict(tps)}')
