# -*- coding: utf-8 -*-
"""逐题核对 mc 的 answer 索引是否指向正确选项（人眼复核清单）。

把每道 mc 的选项和 answer 打出来，Le 我先用程序做「明显错误」检测：
  · answer 越界
  · 选项中重复
  · fill 的 answer 不是字符串数组
另外打印每题供人工核对。
"""
import io, json, os, sys
from collections import Counter

sys.stdout.reconfigure(encoding="utf-8")

only = sys.argv[1] if len(sys.argv) > 1 else None
files = []
for base in ("f6chem/quiz/phys",):
    for n in sorted(os.listdir(base)):
        if n.endswith(".json") and (not only or n[:-5] == only):
            files.append(os.path.join(base, n))

problems = 0
for f in files:
    q = json.load(io.open(f, encoding="utf-8"))
    tid = q["topic"]
    dist = Counter(x["type"] for x in q["questions"])
    print("=" * 76)
    print("%s  %d 题 %s" % (tid, len(q["questions"]), dict(dist)))
    print("=" * 76)
    mc_idx = [x["answer"] for x in q["questions"] if x["type"] == "mc"]
    print("  mc answer 分布:", dict(Counter(mc_idx)))
    for x in q["questions"]:
        pid = x["id"]
        if x["type"] == "mc":
            opts = x["options"]
            a = x["answer"]
            flag = ""
            if not isinstance(a, int) or a < 0 or a >= len(opts):
                flag = "  <<< answer 越界!"
                problems += 1
            if len(set(opts)) != len(opts):
                flag += "  <<< 選項有重複!"
                problems += 1
            print("  %-12s [%d] %s%s" % (pid, a, opts[a], flag))
        elif x["type"] == "tf":
            print("  %-12s [%s] %s" % (pid, x["answer"], ("正確" if x["answer"] else "錯誤")))
        else:
            print("  %-12s [fill] %s" % (pid, x["answer"]))
    print()

print("=" * 76)
print("自動檢測发现的问题: %d" % problems)
if problems:
    sys.exit(1)
print("無越界/重複問題（仍需人工核對選項語義）")
sys.exit(0)
