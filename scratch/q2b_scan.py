import sys, json, os, re
sys.stdout.reconfigure(encoding="utf-8")
BASE = r"D:\deepseek-harness\default-workspace\f6chem"
qs = json.load(open(os.path.join(BASE,"quiz","2b.json"), encoding="utf-8"))["questions"]
pat = re.compile(r"(選項|答案|所以|故)[^\n]{0,40}?[一二三四ABCD](項|、|，|,|。| 是)|[ABCD]\s*項")
for q in qs:
    for fld in ("q","explanation"):
        t = q.get(fld,"")
        m = pat.search(t)
        if m:
            print(q["id"], q["point"], q["type"], fld, "::", t[max(0,m.start()-45):m.end()+45])
print("scan done")