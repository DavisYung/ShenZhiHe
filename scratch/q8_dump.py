import json, io, sys

BASE = r"D:\deepseek-harness\default-workspace\f6chem"
d = json.load(io.open(BASE + r"\data\8.json", encoding="utf-8"))
idx = {}
for s in d["sections"]:
    for p in s["points"]:
        idx[p["id"]] = p

BATCH = [
    ["8-s2-p1","8-s2-p2","8-s2-p3","8-s2-p4","8-s3-p1","8-s3-p2","8-s3-p3"],
    ["8-s4-p1","8-s4-p2","8-s4-p3","8-s5-p1","8-s5-p2","8-s5-p3","8-s5-p4"],
    ["8-s6-p1","8-s6-p2","8-s6-p3","8-s6-p4","8-s6-p5","8-s7-p1","8-s7-p2","8-s7-p3"],
    ["8-s8-p1","8-s8-p2","8-s8-p3","8-s9-p1","8-s9-p2","8-s9-p3","8-s9-p4"],
    ["8-s10-p1","8-s10-p2","8-s10-p3","8-s10-p4","8-s11-p1","8-s11-p2","8-s11-p3"],
    ["8-s12-p1","8-s12-p2","8-s12-p3","8-s12-p6","8-s13-p1","8-s13-p2","8-s13-p3","8-s13-p4","8-s13-p5"],
    ["8-s14-p1","8-s14-p2","8-s14-p3","8-s14-p4","8-s1-p1","8-s1-p2","8-s1-p3"],
]
which = sys.argv[1]
out = io.open(BASE + r"\scratch\q8_dump_%s.txt" % which, "w", encoding="utf-8")
for bid in BATCH[int(which) - 1]:
    p = idx[bid]
    out.write("\n########## %s | %s\n" % (p["id"], p["title"]))
    out.write((p.get("body") or "") + "\n")
out.close()
print("ok", which)