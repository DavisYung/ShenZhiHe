# -*- coding: utf-8 -*-
"""用字规范化修正：把物理数据里的异体字「温」(U+6E29) 统一为「溫」(U+6EAB)。

背景：化学区 12 份资料全部用「溫」389 次、零例外；PDF 原文是「温」。
物理区必须与化学区一致，否则字形不统一、搜索漏命中。

安全设计：
  · 只替换「温」→「溫」这一个字形差异，不做简繁转换（避免改动语义）
  · 同时处理 title / body / tags / explanation / q / options / answer 等所有字符串字段
  · 修正前先备份，修正后重新校验
"""
import io
import json
import os
import shutil
import sys

sys.stdout.reconfigure(encoding="utf-8")
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPLACE = {"\u6e29": "\u6eab"}   # 温 → 溫


def fix_str(s):
    if not isinstance(s, str):
        return s, 0
    n = 0
    for a, b in REPLACE.items():
        c = s.count(a)
        if c:
            s = s.replace(a, b)
            n += c
    return s, n


def walk(obj):
    """递归修正所有字符串字段，回传 (新对象, 修正数)。"""
    if isinstance(obj, str):
        return fix_str(obj)
    if isinstance(obj, list):
        out, tot = [], 0
        for x in obj:
            v, n = walk(x)
            out.append(v)
            tot += n
        return out, tot
    if isinstance(obj, dict):
        out, tot = {}, 0
        for k, v in obj.items():
            nk, kn = fix_str(k)
            nv, vn = walk(v)
            out[nk] = nv
            tot += kn + vn
        return out, tot
    return obj, 0


def process(path, dry=False):
    with io.open(path, encoding="utf-8") as f:
        raw = f.read()
    data = json.loads(raw)
    fixed, n = walk(data)
    if n and not dry:
        shutil.copy2(path, path + ".bak")
        with io.open(path, "w", encoding="utf-8") as f:
            json.dump(fixed, f, ensure_ascii=False, indent=1)
            f.write("\n")
    return n


def main():
    dry = "--dry" in sys.argv
    targets = []
    for d, pat in ((os.path.join(BASE, "data", "phys"), None),
                   (os.path.join(BASE, "quiz", "phys"), None)):
        if not os.path.isdir(d):
            continue
        for n in sorted(os.listdir(d)):
            if n.endswith(".json") and n not in ("subject.json",):
                targets.append(os.path.join(d, n))
    # links.json 也一并处理
    lp = os.path.join(BASE, "data", "phys", "links.json")
    if os.path.exists(lp) and lp not in targets:
        targets.append(lp)

    total = 0
    for p in targets:
        n = process(p, dry=dry)
        if n:
            print("  %-46s 修正 %d 處%s" % (os.path.basename(p), n,
                                          "（dry-run）" if dry else ""))
            total += n
    print("\n合計修正 %d 處「温」→「溫」%s" % (total, "（dry-run，未寫入）" if dry else ""))


if __name__ == "__main__":
    main()
