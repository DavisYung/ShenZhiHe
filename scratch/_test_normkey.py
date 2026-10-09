# -*- coding: utf-8 -*-
"""norm_key 单元测试：新旧 ref 风格的归一化与去重语义。"""
import os
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from merge_exam import norm_key  # noqa: E402

CASES = [
    # (ref, expected_key 去掉 year 部分)
    ("卷一 甲部 Q1", ("P1", "A", 1, "")),
    ("2014-P1-甲部-23", ("P1", "A", 23, "")),
    ("2020-P1-A-14", ("P1", "A", 14, "")),
    ("2021 P1 Q1", ("P1", "A", 1, "")),
    ("2015-P1-Q22", ("P1", "A", 22, "")),
    ("2020-p1-Q23", ("P1", "A", 23, "")),
    ("2016-P1A-Q36", ("P1", "A", 36, "")),
    ("2016-P1B-Q1(a)", ("P1", "B", 1, "a")),
    ("2012-P1B-Q13(a)(i)", ("P1", "B", 13, "a-i")),
    ("2012-P2A-Q1(a)(iii)", ("P2", "A", 1, "a-iii")),
    ("2012-P2C-Q2", ("P2", "C", 2, "")),
    ("2012-P2B-Q1(b)(ii)", ("P2", "B", 1, "b-ii")),
]
bad = 0
for ref, exp in CASES:
    y = int(ref[:4]) if ref[:2] == "20" else 2012
    k = norm_key(y, ref)
    got = k[1:]
    ok = got == exp
    if not ok:
        bad += 1
    print("%-22s -> %-24s %s" % (ref, str(got), "OK" if ok else "FAIL exp=%s" % (exp,)))

# 去重语义：同题不同小问不撞、甲/乙部不撞
a = norm_key(2012, "2012-P1B-Q1(a)")
b = norm_key(2012, "2012-P1B-Q1(b)")
c = norm_key(2012, "2012-P1A-Q1")
print("different parts distinct:", a != b)
print("section distinct:", a != c)
print("RESULT:", "ALL OK" if bad == 0 else "%d FAILED" % bad)
sys.exit(1 if bad else 0)
