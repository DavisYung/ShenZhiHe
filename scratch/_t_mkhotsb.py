# -*- coding: utf-8 -*-
"""在沙盒数据上预演 _mk_hot.py（hot.json 重生器），确认指标与结构无异常。"""
import io
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))          # f6chem/scratch
F6 = os.path.dirname(HERE)
sys.path.insert(0, F6)
import _mk_hot  # noqa: E402

_mk_hot.DATA = os.path.join(HERE, "_t_data_real")
_mk_hot.DST = os.path.join(HERE, "_t_hot_sandbox.json")
_mk_hot.main()

h = json.load(io.open(_mk_hot.DST, encoding="utf-8"))
s = h["summary"]
print("\nsandbox hot.json:")
print("  years:", s["years"])
print("  points/hits/lv:", s["points"], s["hits"], "lv3=%d lv2=%d lv1=%d" % (s["lv3"], s["lv2"], s["lv1"]))
print("  groups: lv3=%d lv2=%d" % (len(h["groups"][0]["items"]), len(h["groups"][1]["items"])))
print("  years[]:", [(y["year"], y["hits"]) for y in h["years"]])
print("  top topics:", [(t["id"], t["hits"]) for t in h["topics"][:6]])
print("  keywords cloud:", len(h["keywords"]), "top5:", [(k["text"], k["count"]) for k in h["keywords"][:5]])
print("  subtitle:", h["subtitle"])
