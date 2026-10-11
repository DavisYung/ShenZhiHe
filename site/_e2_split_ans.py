# -*- coding: utf-8 -*-
"""把答案本按「第N課」边界切成 3 份，与 course1/2/3.txt 配对。"""
import io, os, re, sys
sys.stdout.reconfigure(encoding="utf-8")

D = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "atomic_src")
D = os.path.abspath(D)

with io.open(os.path.join(D, "ans_all.txt"), encoding="utf-8") as f:
    txt = f.read()

# 定位「第N 課」标题（跳过开头的目次性文字）
idxs = []
for m in re.finditer(r"第\s*(\d)\s*課", txt):
    n = int(m.group(1))
    if not idxs or idxs[-1][0] != n:
        idxs.append((n, m.start()))

print("找到的课边界:")
for n, i in idxs:
    print(f"  第{n}課 @ {i}")

# 切成 3 段
marks = [i for _n, i in idxs]
names = {1: "ans_course1.txt", 2: "ans_course2.txt", 3: "ans_course3.txt"}
for k, (n, start) in enumerate(idxs):
    end = idxs[k + 1][1] if k + 1 < len(idxs) else len(txt)
    seg = txt[start:end]
    out = os.path.join(D, names.get(n, f"ans_course{n}.txt"))
    with io.open(out, "w", encoding="utf-8") as f:
        f.write(seg)
    print(f"  {os.path.basename(out)}  {len(seg)} 字元")

print("\n配对材料:")
for c in (1, 2, 3):
    a = os.path.join(D, f"ans_course{c}.txt")
    b = os.path.join(D, f"course{c}.txt")
    print(f"  course{c}.txt ({os.path.getsize(b)}B)  +  ans_course{c}.txt ({os.path.getsize(a)}B)")
