# -*- coding: utf-8 -*-
"""列出 1a/1b/1c 三個課題裡【還沒有任何題目】的知識點，含全文，供出題用。"""
import io, json, os, sys

sys.stdout.reconfigure(encoding="utf-8")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data", "chem")
QUIZ = os.path.join(ROOT, "quiz", "chem")

out_path = os.path.join(ROOT, "scratch", "uncovered_1x.txt")
lines = []
for tid in ["1a", "1b", "1c"]:
    topic = json.load(io.open(os.path.join(DATA, tid + ".json"), encoding="utf-8"))
    quiz = json.load(io.open(os.path.join(QUIZ, tid + ".json"), encoding="utf-8"))
    covered = set(q.get("point") for q in quiz["questions"])
    lines.append("=" * 70)
    lines.append("課題 %s（已有 %d 題，涵蓋 %d 點）" % (tid, len(quiz["questions"]), len(covered)))
    lines.append("=" * 70)
    n = 0
    for sec in topic.get("sections", []):
        for p in sec.get("points", []):
            if p["id"] in covered:
                continue
            n += 1
            lines.append("")
            lines.append("[%s] %s / %s / p%s" % (p["id"], tid, p.get("title"), p.get("page")))
            lines.append((p.get("body") or "").strip())
    lines.append("\n>>> %s 未覆蓋 %d 個知識點" % (tid, n))

io.open(out_path, "w", encoding="utf-8").write("\n".join(lines))
print("written", out_path, os.path.getsize(out_path), "bytes")
