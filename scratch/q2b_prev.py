import sys, json, os, collections
sys.stdout.reconfigure(encoding="utf-8")
BASE = r"D:\deepseek-harness\default-workspace\f6chem"
for tid in ["1a","1c","2a","3a","3b","4a","4b","6","8"]:
    q = json.load(open(os.path.join(BASE,"quiz",tid+".json"), encoding="utf-8"))
    d = json.load(open(os.path.join(BASE,"data",tid+".json"), encoding="utf-8"))
    secs = d["sections"]; allp = {p["id"] for s in secs for p in s["points"]}
    qs = q["questions"]
    c = collections.Counter(x["type"] for x in qs)
    covered = {x["point"].rsplit("-p",1)[0] for x in qs}
    print(tid, "| n_sec=%d n_point=%d" % (len(secs), len(allp)),
          "| n_q=%d" % len(qs), dict(c),
          "| sec_covered=%d/%d" % (len(covered), len(secs)),
          "| bad_point=%d" % sum(1 for x in qs if x["point"] not in allp))