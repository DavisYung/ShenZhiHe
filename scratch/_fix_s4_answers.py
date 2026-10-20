# -*- coding: utf-8 -*-
"""一次性修补 calc-s4 答案：补上第 7、8 题的坐标行。"""
import io
import json

P = "data/math/calc.json"
with io.open(P, encoding="utf-8") as f:
    d = json.load(f)

OLD = "| 6 | (4.333, 1) | (4.394, 0.394) | (5, 2) | (3, −1) |"
NEW = ("| 6 | (4.333, 1) | (4.394, 0.394) | (5, 2) | (3, −1) |\n"
       "| 7 | (1, 1.333) | (1, 1) | (1.5, 2) | (0, 0) |\n"
       "| 8 | (1.667, 4) | (2, 2) | (2.5, 6) | (0, 0) |")

OLD2 = ("**第 7 題**：三邊是 3、4、5（直角），內切圓半徑 `r = (3+4−5)/2 = 1`，所以內心是 (1, 1)。\n\n"
        "**第 8 題**：斜邊 = √(25+144) = 13，外接圓半徑 `R = 13/2 = 6.5`。程式第 5、6 個輸出應為 (2.5, 6)，到 (0,0) 的距離正好 6.5。")
NEW2 = ("**第 7 題**：三邊是 3、4、5（直角），內切圓半徑 `r = (a+b−c)/2 = (3+4−5)/2 = 1`，所以內心是 (1, 1)。"
        "反過來驗證：內心 (1,1) 到三條邊的距離都是 1。\n\n"
        "**第 8 題**：斜邊 = √(5²+12²) = 13，外接圓半徑 `R = 13/2 = 6.5`。程式第 5、6 個輸出是 (2.5, 6)，"
        "到 (0,0) 的距離 √(2.5²+6²) = 6.5，完全吻合。")

hit = 0
for sec in d["sections"]:
    for p in sec["points"]:
        if OLD in p["body"]:
            p["body"] = p["body"].replace(OLD, NEW)
            hit += 1
        if OLD2 in p["body"]:
            p["body"] = p["body"].replace(OLD2, NEW2)
            hit += 1

assert hit == 2, "只命中 %d 处，预期 2 处" % hit

with io.open(P, "w", encoding="utf-8", newline="\n") as f:
    json.dump(d, f, ensure_ascii=False, indent=2)
    f.write("\n")

with io.open(P, encoding="utf-8") as f:
    back = json.load(f)
assert "\ufffd" not in json.dumps(back, ensure_ascii=False)
print("OK 已修补 %d 处" % hit)
