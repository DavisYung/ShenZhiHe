import json, io, os
ROOT = r"D:\deepseek-harness\default-workspace\f6chem"
TIDS = ["1a","1b","1c","2a","2b","3a","3b","4a","4b","6","8"]
tot=0
for tid in TIDS:
    p = os.path.join(ROOT,"quiz",tid+".json")
    if not os.path.exists(p):
        print("%-4s MISSING" % tid); continue
    with io.open(p,encoding="utf-8") as f: q=json.load(f)
    qs=q.get("questions",[]); tot+=len(qs)
    d=os.path.join(ROOT,"data",tid+".json")
    with io.open(d,encoding="utf-8") as f: dd=json.load(f)
    npts=sum(len(s.get("points",[])) for s in dd.get("sections",[]))
    nsec=len(dd.get("sections",[]))
    cover=len(set(x.get("point") for x in qs))
    print("%-4s %3d q | %2d sec %3d pts | cover %d pts" % (tid,len(qs),nsec,npts,cover))
print("TOTAL questions:",tot)
