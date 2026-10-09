# -*- coding: utf-8 -*-
"""把 scratch/map/<year>.json 的逐题映射合并进 data/chem/*.json 的 exam 字段。

map 文件 schema（由映射子代理产出）：
{
 "year": 2016,
 "mappings": [{"ref": "2016-P1A-Q12", "points": ["2a-s3-p1"], "focus": "一句話說考了什麼"}],
 "kw": {"<point_id>": ["字眼1", "字眼2"]}      # 该年参考答案提取，按知识点归并
}

规则（只增不改，保护既有标注）：
- years 累加；hits = len(years)；level 重算（>=5=3 / 2-4=2 / 1=1）
- samples 按归一化 (年, 卷, 节, 题号, 小问) 去重追加 {y, ref, focus}；撞车保留旧条目
- keywords 并入新词，旧词保持原顺序在前
- 每个被改的档写回前 json.load 验证 + 扫描 U+FFFD；改动前先备份到 scratch/backup_exam/

用法：python f6chem/scratch/merge_exam.py [年份.json ...]   # 缺省合并 scratch/map/ 全部
"""
import glob
import io
import json
import os
import re
import shutil
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # f6chem
DATA = os.path.join(BASE, "data", "chem")
MAPD = os.path.join(BASE, "scratch", "map")
BAK = os.path.join(BASE, "scratch", "backup_exam")


def level_of(n):
    return 3 if n >= 5 else (2 if n >= 2 else 1)


def norm_key(year, ref):
    """把各种风格的 ref 归一成 (year, paper, section, qnum, part)。

    旧 ref（卷一甲部口径）缺节号一律视为 A；新 ref 按约定
    {y}-P1A-Q{n} / {y}-P1B-Q{n}({part}) / {y}-P2{A|B|C}-Q{n}({part})。
    """
    r = str(ref)
    low = r.lower()
    paper = "P2" if ("p2" in low or "卷二" in r) else "P1"
    if "p1b" in low or "p2b" in low or "乙部" in r:
        sec = "B"
    elif "p1c" in low or "p2c" in low or "丙部" in r:
        sec = "C"
    else:
        sec = "A"
    s = re.sub(r"20\d{2}", "", r)
    s = re.sub(r"[Pp]\d", "", s)
    m = re.search(r"(\d+)", s)
    qnum = int(m.group(1)) if m else 0
    # 小问链：'Q1(a)(i)' → 'a-i'（多层括号全收，保证 (a)(i) 与 (a)(iii) 不撞）
    groups = re.findall(r"\(([a-z0-9]+)\)", low)
    part = "-".join(groups)
    return (year, paper, sec, qnum, part)


def load_all():
    """一次读入所有 data 档；point_id -> (file, 该档内 point 对象引用)。
    合并必须改这份对象树，写回时也写它——避免读两份导致改动丢失。"""
    objs, pid2pt = {}, {}
    for f in sorted(glob.glob(os.path.join(DATA, "*.json"))):
        stem = os.path.basename(f)[:-5]
        if stem in ("subject", "links", "index"):
            continue
        obj = json.load(io.open(f, encoding="utf-8"))
        if not isinstance(obj, dict):
            continue
        objs[f] = obj
        for s in obj.get("sections") or []:
            for p in s.get("points") or []:
                pid2pt[p["id"]] = (f, p)
    return objs, pid2pt


def write_back(path, obj):
    text = json.dumps(obj, ensure_ascii=False, indent=2)   # 与既有格式一致（无尾换行）
    if "\ufffd" in text:
        raise SystemExit("U+FFFD in " + path)
    with io.open(path, "w", encoding="utf-8", newline="") as f:
        f.write(text)
    back = json.load(io.open(path, encoding="utf-8"))      # 回读验证
    assert back.get("id") == obj.get("id")


def main():
    args = sys.argv[1:]
    files = [os.path.join(MAPD, a) for a in args] if args else \
        sorted(glob.glob(os.path.join(MAPD, "*.json")))
    if not files:
        raise SystemExit("no map files in " + MAPD)
    objs, pid2pt = load_all()
    os.makedirs(BAK, exist_ok=True)

    touched = set()
    stats = {"pairs": 0, "samples": 0, "kw": 0, "unknown": []}
    for mf in files:
        d = json.load(io.open(mf, encoding="utf-8"))
        year = int(d["year"])
        kws = d.get("kw") or {}
        for m in d.get("mappings") or []:
            focus = (m.get("focus") or "").strip()
            for pid in m.get("points") or []:
                hit = pid2pt.get(pid)
                if not hit:
                    stats["unknown"].append(pid)
                    continue
                f, p = hit
                touched.add(f)
                e = p.setdefault("exam", {"years": [], "hits": 0, "level": 1,
                                          "samples": [], "keywords": []})
                for k in ("years", "samples", "keywords"):
                    e.setdefault(k, [])
                if year not in e["years"]:
                    e["years"].append(year)
                    e["years"].sort()
                    stats["pairs"] += 1
                key = norm_key(year, m.get("ref", ""))
                have = {norm_key(sm.get("y"), sm.get("ref")) for sm in e["samples"]}
                if key not in have:
                    entry = {"y": year, "ref": m.get("ref")}
                    if focus:
                        entry["focus"] = focus
                    e["samples"].append(entry)
                    e["samples"].sort(key=lambda s: (s.get("y") or 0, str(s.get("ref"))))
                    stats["samples"] += 1
                for kw in kws.get(pid) or []:
                    if kw and kw not in e["keywords"]:
                        e["keywords"].append(kw)
                        stats["kw"] += 1
                e["hits"] = len(e["years"])
                e["level"] = level_of(e["hits"])

    for f in sorted(touched):
        shutil.copy2(f, os.path.join(BAK, os.path.basename(f)))
        write_back(f, objs[f])

    print("merged %d map files -> %d data files" % (len(files), len(touched)))
    print("added year-pairs: %d, samples: %d, keywords: %d"
          % (stats["pairs"], stats["samples"], stats["kw"]))
    if stats["unknown"]:
        print("UNKNOWN point ids:", sorted(set(stats["unknown"])))


if __name__ == "__main__":
    main()
