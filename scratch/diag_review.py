# -*- coding: utf-8 -*-
"""診斷神智核複習數量異常：統計知識點數、測驗覆蓋率、以及『只是看筆記』會標記多少 seen。"""
import io, json, os, glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data", "chem")
QUIZ = os.path.join(ROOT, "quiz", "chem")

sub = json.load(io.open(os.path.join(DATA, "subject.json"), encoding="utf-8"))
topics = sub.get("topics") or sorted(n[:-5] for n in os.listdir(DATA) if n.endswith(".json") and n[:-5] not in ("subject", "links"))

pts = {}          # pid -> title
per_topic = {}    # tid -> [pids]
for tid in topics:
    p = os.path.join(DATA, tid + ".json")
    if not os.path.exists(p):
        print("缺少", tid)
        continue
    t = json.load(io.open(p, encoding="utf-8"))
    ids = []
    for s in t.get("sections", []):
        for pt in s.get("points", []):
            pts[pt["id"]] = pt.get("title", "")
            ids.append(pt["id"])
    per_topic[tid] = ids

print("課題數 %d，知識點總數 %d" % (len(per_topic), len(pts)))

qpts = set()
qn = 0
noquiz_topics = []
for f in glob.glob(os.path.join(QUIZ, "*.json")):
    q = json.load(io.open(f, encoding="utf-8"))
    qs = q.get("questions", []) if isinstance(q, dict) else q
    tid = os.path.basename(f)[:-5]
    has = False
    for x in qs:
        qn += 1
        if x.get("point"):
            qpts.add(x["point"])
            has = True
    if not has:
        noquiz_topics.append(tid)

covered = sorted(qpts & set(pts))
uncovered = sorted(set(pts) - qpts)
print("測驗題總數 %d，有題目的知識點 %d，沒有題目的知識點 %d" % (qn, len(covered), len(uncovered)))
print("完全沒有 quiz 的課題:", noquiz_topics)

print("\n各課題：知識點數 / 有題目數 / 沒題目數")
for tid in sorted(per_topic):
    ids = per_topic[tid]
    c = len([x for x in ids if x in qpts])
    print("  %-4s 共 %3d 點，有題 %3d，沒題 %3d" % (tid, len(ids), c, len(ids) - c))

print("\n沒題目的知識點（會被永久算進『今日待複習』）：")
for pid in uncovered[:60]:
    print("   ", pid, pts[pid])
if len(uncovered) > 60:
    print("    ... 其餘 %d 個" % (len(uncovered) - 60))
