# -*- coding: utf-8 -*-
"""验证「工作纸 ↔ 答案」的对应关系，判断能否自动合并。

策略：两份文件都是按「第N課 / N.M 章節 / 題號」的固定骨架编排。
本脚本抽出两侧的骨架序列，比对结构与数量是否吻合。
"""
import io
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")
D = "f6chem/scratch/phys_extract/"


def load(name):
    return io.open(D + name + ".txt", encoding="utf-8").read()


def skeleton(t):
    """抽出 第N課 / N.M 標題 的结构骨架。"""
    out = []
    for line in t.split("\n"):
        s = line.strip()
        m1 = re.match(r"^(第\d+)\s*課\s*(.*)$", s)
        m2 = re.match(r"^(\d+\.\d+)\s+(.*)$", s)
        if m1:
            out.append(("lesson", m1.group(1), m1.group(2).strip()))
        elif m2:
            # 過濾算式誤判（如 "1.5  500  (150 T)"）
            title = m2.group(2)
            if re.search(r"[\u4e00-\u9fff]", title):
                out.append(("section", m2.group(1), title))
    return out


def pages_of(t):
    return len(re.findall(r"<<<PAGE \d+>>>", t))


work_heat = load("Heat_notes")
work_gas = load("Gases_note")
sol = load("Book_1_Heat_Notes_solution")

print("=== 工作纸骨架（Heat notes，第1-4課）===")
for k, a, b in skeleton(work_heat):
    print("  %-8s %-6s %s" % (k, a, b))

print("\n=== 工作纸骨架（Gases note，第5課）===")
for k, a, b in skeleton(work_gas):
    print("  %-8s %-6s %s" % (k, a, b))

print("\n=== 答案骨架（solution）===")
for k, a, b in skeleton(sol):
    print("  %-8s %-6s %s" % (k, a, b))

print("\n=== 结构比对 ===")
sw = skeleton(work_heat) + skeleton(work_gas)
ss = skeleton(sol)
print("  工作纸条目数: %d" % len(sw))
print("  答案条目数  : %d" % len(ss))

w_sec = [a for k, a, b in sw if k == "section"]
s_sec = [a for k, a, b in ss if k == "section"]
print("\n  工作纸章節: %s" % w_sec)
print("  答案章節  : %s" % s_sec)
print("\n  章節集合是否一致: %s" % (set(w_sec) == set(s_sec)))

print("\n=== 答案里能覆盖多少題號（以章節為界）===")
# 檢查每個章節在答案裡是否都有對應段落
for sec in w_sec:
    in_sol = sec in sol
    print("  %-8s 答案中有此章節: %s" % (sec, "是" if in_sol else "否"))

print("\n=== 頁數 ===")
print("  Heat notes : %d 頁" % pages_of(work_heat))
print("  Gases note : %d 頁" % pages_of(work_gas))
print("  solution   : %d 頁" % pages_of(sol))
