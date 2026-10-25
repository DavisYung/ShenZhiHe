# -*- coding: utf-8 -*-
import json, io, os
from collections import Counter

BASE = r"D:\deepseek-harness\default-workspace\f6chem"
out = io.open(BASE + r"\scratch\q8_report.txt", "w", encoding="utf-8")

data = json.load(io.open(BASE + r"\quiz\8.json", encoding="utf-8"))
src = json.load(io.open(BASE + r"\data\8.json", encoding="utf-8"))
points = {p["id"]: p for s in src["sections"] for p in s["points"]}

err = []
if data.get("topic") != "8":
    err.append("topic != 8")
qs = data["questions"]
out.write("total = %d\n" % len(qs))

# id 連續無重複
ids = [q["id"] for q in qs]
expect = ["8-q%d" % i for i in range(1, len(qs) + 1)]
if ids != expect:
    err.append("id not continuous: %s" % ids[:5])
if len(set(ids)) != len(ids):
    err.append("duplicate ids")

tc = Counter(q["type"] for q in qs)
out.write("types: %s\n" % dict(tc))
n = len(qs)
out.write("ratios: mc=%.1f%% tf=%.1f%% fill=%.1f%%\n" % (
    100.0 * tc["mc"] / n, 100.0 * tc["tf"] / n, 100.0 * tc["fill"] / n))

for q in qs:
    t, pid = q["type"], q.get("point")
    if pid not in points:
        err.append("%s bad point %s" % (q["id"], pid))
    body = points.get(pid, {}).get("body") or ""
    title = points.get(pid, {}).get("title", "")
    if "OCR 不清" in body:
        err.append("%s point marked OCR-unclear" % q["id"])
    if not q.get("q", "").strip():
        err.append("%s empty q" % q["id"])
    if not q.get("explanation", "").strip():
        err.append("%s empty explanation" % q["id"])
    if t == "mc":
        o = q.get("options")
        if not isinstance(o, list) or len(o) != 4:
            err.append("%s options != 4" % q["id"])
        elif len(set(o)) != 4:
            err.append("%s duplicate options" % q["id"])
        a = q.get("answer")
        if not isinstance(a, int) or isinstance(a, bool) or not (0 <= a <= 3):
            err.append("%s bad mc answer %r" % (q["id"], a))
        else:
            out.write("  %s mc  ans=%d -> %r | %s | %s\n" % (
                q["id"], a, o[a], pid, title))
    elif t == "tf":
        if not isinstance(q.get("answer"), bool):
            err.append("%s tf answer not bool" % q["id"])
        else:
            out.write("  %s tf  ans=%s | %s | %s\n" % (
                q["id"], q["answer"], pid, title))
    elif t == "fill":
        a = q.get("answer")
        arr = a if isinstance(a, list) else [a]
        if not isinstance(a, (str, list)) or not arr or any(
                not isinstance(x, str) or not x.strip() for x in arr):
            err.append("%s bad fill answer %r" % (q["id"], a))
        if "____" not in q["q"]:
            err.append("%s fill missing ____" % q["id"])
        out.write("  %s fill ans=%s | %s | %s\n" % (q["id"], arr, pid, title))
    else:
        err.append("%s unknown type %s" % (q["id"], t))

# section 覆蓋
sec = {s["id"]: s for s in src["sections"]}
cover = {}
for q in qs:
    sid = q["point"].rsplit("-", 1)[0]
    cover.setdefault(sid, []).append(q["id"])
out.write("\n-- section coverage (%d sections) --\n" % len(sec))
for sid in sec:
    got = cover.get(sid, [])
    if len(got) < 2:
        err.append("section %s only %d questions" % (sid, len(got)))
    out.write("  %s %-22s %d  %s\n" % (sid, sec[sid]["title"][:22], len(got),
                                      ",".join(x.split("-")[1] for x in got)))

tfs = [q for q in qs if q["type"] == "tf"]
nf = sum(1 for q in tfs if q["answer"] is False)
out.write("\ntf: %d total, %d false (%.0f%%)\n" % (len(tfs), nf, 100.0 * nf / len(tfs)))

out.write("\nERRORS: %d\n" % len(err))
for e in err:
    out.write("  ! %s\n" % e)
out.write("RESULT: %s\n" % ("PASS" if not err else "FAIL"))
out.close()
print("errors=%d" % len(err))