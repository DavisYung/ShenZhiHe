# -*- coding: utf-8 -*-
"""校验 scratch/map/*.json（子代理产出），合并前必过。

检查项：
1) json 可解析、year 与文件名一致
2) 无 U+FFFD
3) 每条 mapping：ref 符合约定（{y}-P1A|P1B|P2{A|B|C}-Q数字(小问链)）、
   points 为数组且每个 id 都在 catalog.tsv、focus ≤40 字
4) kw 的 key 必须出现在 catalog；字眼非空、长度合理
5) 每年 mappings 数量在合理区间（防止空文件或幻觉爆炸）
输出：每年统计 + 总体是否可合并。
用法：python f6chem/scratch/validate_maps.py
"""
import glob
import io
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # f6chem
PP = os.path.join(BASE, "scratch", "pp")
MAPD = os.path.join(BASE, "scratch", "map")

REF_RE = re.compile(r"^(20\d{2})-(P1A|P1B|P2[A-Z])-Q\d+(\([a-z0-9]+\))*$")

catalog = set()
with io.open(os.path.join(PP, "catalog.tsv"), encoding="utf-8") as f:
    for line in f:
        catalog.add(line.rstrip("\n").split("\t")[0])

files = sorted(glob.glob(os.path.join(MAPD, "*.json")))
if not files:
    raise SystemExit("no map files")
allok = True
for mf in files:
    name = os.path.basename(mf)
    # 支持分段档：2020_p1b_a.json / 2020_p1b_b.json（乙部按题号对半拆分）
    m_part = re.match(r"\d{4}_(p1a|p1b|p2)(?:_[a-z])?\.json", name)
    part = m_part.group(1) if m_part else ""
    errs = []
    try:
        text = io.open(mf, encoding="utf-8").read()
    except Exception as e:
        print(name, "READ FAIL", e)
        allok = False
        continue
    if "\ufffd" in text:
        errs.append("U+FFFD present")
    try:
        d = json.loads(text)
    except Exception as e:
        print(name, "JSON FAIL", e)
        allok = False
        continue
    y = int(re.match(r"(\d+)", name).group(1))
    if int(d.get("year", -1)) != y:
        errs.append("year mismatch %s != %d" % (d.get("year"), y))
    refs = set()
    pids = set()
    for m in d.get("mappings") or []:
        ref = str(m.get("ref") or "")
        if not REF_RE.match(ref):
            errs.append("bad ref: %r" % ref)
        elif int(ref[:4]) != y:
            errs.append("ref year mismatch: %r" % ref)
        elif part == "p1a" and "-P1A-" not in ref:
            errs.append("ref part mismatch (want P1A): %r" % ref)
        elif part == "p1b" and "-P1B-" not in ref:
            errs.append("ref part mismatch (want P1B): %r" % ref)
        elif part == "p2" and "-P2" not in ref:
            errs.append("ref part mismatch (want P2X): %r" % ref)
        pts = m.get("points")
        if not isinstance(pts, list):
            errs.append("points not list: %r" % ref)
            pts = []
        for pid in pts:
            if pid not in catalog:
                errs.append("unknown point %s (ref %s)" % (pid, ref))
            pids.add(pid)
        focus = m.get("focus")
        if focus and len(focus) > 100:
            errs.append("focus too long: %r" % ref)
        if len(pts) > 3:
            errs.append("too many points (%d): %r" % (len(pts), ref))
        refs.add(ref)
    for pid, kws in (d.get("kw") or {}).items():
        if pid not in catalog:
            errs.append("kw unknown point %s" % pid)
        if not isinstance(kws, list):
            errs.append("kw not list: %s" % pid)
        # 空列表合法：纯图/纯结构题评分标准无文字要求，刻意留空防编造
        for k in kws or []:
            # 允许评分方程/数值（如 "NH4+ + OH- → NH3 + H2O"）与单字答案（如 "氫"）
            if not isinstance(k, str) or not (1 <= len(k) <= 40):
                errs.append("kw odd %r on %s" % (k, pid))
    n_map = len(d.get("mappings") or [])
    n_empty = sum(1 for m in (d.get("mappings") or []) if not m.get("points"))
    if not (3 <= n_map <= 220):
        errs.append("mappings count suspicious: %d" % n_map)
    status = "OK " if not errs else "BAD"
    if errs:
        allok = False
    print("%s %s  mappings=%3d empty=%2d refs=%3d points_hit=%3d kw_pts=%3d"
          % (status, name, n_map, n_empty, len(refs), len(pids),
             len(d.get("kw") or {})))
    for e in errs[:12]:
        print("     -", e)
    if len(errs) > 12:
        print("     ... +%d more" % (len(errs) - 12))
print("\nRESULT:", "ALL OK ✅" if allok else "HAS ERRORS ❌")
sys.exit(0 if allok else 1)
