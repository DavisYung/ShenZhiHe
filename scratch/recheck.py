import json, io, os, sys
sys.stdout.reconfigure(encoding="utf-8")
ROOT = r"D:\deepseek-harness\default-workspace\f6chem"
TIDS = ["1a","1b","1c","2a","2b","3a","3b","4a","4b","6","8"]
bad=0
for tid in TIDS:
    p = os.path.join(ROOT,"quiz",tid+".json")
    with io.open(p,encoding="utf-8") as f: raw=f.read()
    q=json.loads(raw); qs=q.get("questions",[])
    # U+FFFD / surrogate / lone replacement
    fffd = raw.count("\ufffd")
    ids=[x["id"] for x in qs]
    dup=len(ids)-len(set(ids))
    # point existence
    dp=os.path.join(ROOT,"data",tid+".json")
    with io.open(dp,encoding="utf-8") as f: dd=json.load(f)
    valid=set()
    for s in dd.get("sections",[]):
        for pt in s.get("points",[]): valid.add(pt["id"])
    orphan=[x["id"] for x in qs if x.get("point") not in valid]
    probs=[]
    if fffd: probs.append("FFFD=%d"%fffd)
    if dup: probs.append("dup=%d"%dup)
    if orphan: probs.append("orphan=%d:%s"%(len(orphan),orphan[:3]))
    if probs:
        bad+=1
        print("%-4s PROBLEM %s" % (tid,"; ".join(probs)))
    else:
        print("%-4s clean  %d q" % (tid,len(qs)))
print("topics with problems:",bad)
