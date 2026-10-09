# -*- coding: utf-8 -*-
"""物理内容生产：第 2 步「产出每课题的转录素材包」。

背景（本项目的关键发现）：
    Heat notes.pdf / Gases note.pdf 是**填空工作纸**（大量 ____ 空格），
    Book 1 Heat Notes solution.pdf 是**配套答案**，按同一「第N課 / N.M 章節 / 題號」骨架编排，
    且答案里直接标了对应工作纸页码（如 "A 蒸發 (p.28)"）。
    单看工作纸是残缺的，必须两份合并才能得到完整知识点。

本脚本按**课题**切分，把「工作纸原文 + 配套答案 + 可用页图清单」合成一份素材包。

产出：f6chem/scratch/phys_bundles/<tid>.md
"""
import io
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

SCRATCH = os.path.dirname(os.path.abspath(__file__))
EX = os.path.join(SCRATCH, "phys_extract")
IMGDIR = os.path.join(os.path.dirname(SCRATCH), "site", "img")
OUT = os.path.join(SCRATCH, "phys_bundles")
os.makedirs(OUT, exist_ok=True)

# 课题划分：忠实对应 PDF 的「第N課」。第1-4課出自 Heat notes，第5課出自 Gases note。
TOPICS = [
    {
        "tid": "heat1", "lesson": 1, "title": "温度與温度計",
        "pdf": "Heat notes.pdf",
        "sections": [
            {"sid": "heat1-s1", "num": "1.1", "title": "温度與温標"},
            {"sid": "heat1-s2", "num": "1.2", "title": "温度計"},
        ],
    },
    {
        "tid": "heat2", "lesson": 2, "title": "內能與比熱容量",
        "pdf": "Heat notes.pdf",
        "sections": [
            {"sid": "heat2-s1", "num": "2.1", "title": "內能"},
            {"sid": "heat2-s2", "num": "2.2", "title": "比熱容量"},
        ],
    },
    {
        "tid": "heat3", "lesson": 3, "title": "物態的改變",
        "pdf": "Heat notes.pdf",
        "sections": [
            {"sid": "heat3-s1", "num": "3.1", "title": "潛熱"},
            {"sid": "heat3-s2", "num": "3.2", "title": "蒸發"},
        ],
    },
    {
        "tid": "heat4", "lesson": 4, "title": "傳熱方式",
        "pdf": "Heat notes.pdf",
        "sections": [
            {"sid": "heat4-s1", "num": "4.1", "title": "傳導"},
            {"sid": "heat4-s2", "num": "4.2", "title": "對流"},
            {"sid": "heat4-s3", "num": "4.3", "title": "輻射"},
        ],
    },
    {
        "tid": "heat5", "lesson": 5, "title": "氣體",
        "pdf": "Gases note.pdf",
        "sections": [
            {"sid": "heat5-s1", "num": "5.1", "title": "氣體定律"},
            {"sid": "heat5-s2", "num": "5.2", "title": "氣體分子運動論"},
        ],
    },
]

# 工作纸页归属（由 phys_pagemap.txt 核定）
WORKSHEET = {
    "heat1": (1, 4),
    "heat2": (5, 13),
    "heat3": (14, 32),
    "heat4": (33, 45),
    "heat5": (1, 31),
}

# 答案页归属（由 phys_pagemap.txt 核定；第1課答案跨 p1-2）
SOLUTION = {
    "heat1": (1, 2),
    "heat2": (2, 3),
    "heat3": (4, 6),
    "heat4": (7, 8),
    "heat5": (9, 12),
}

# 工作纸里夹带的 DSE 真题页（图片形式，文字层为空）——单独标注，避免被误当正文转录
DSE_PAGES = {
    "heat5": list(range(17, 32)),
}


def load(name):
    with io.open(os.path.join(EX, name + ".txt"), encoding="utf-8") as f:
        return f.read()


def page_slice(text, lo, hi):
    parts = re.split(r"<<<PAGE (\d+)>>>", text)
    out = []
    for i in range(1, len(parts), 2):
        n = int(parts[i])
        if lo <= n <= hi:
            out.append("### 原 PDF 第 %d 頁\n%s" % (n, parts[i + 1].strip()))
    return "\n\n".join(out)


def page_stats(text, lo, hi):
    """逐页字数，用于识别「图片页」（文字层为空、内容在图里）。"""
    parts = re.split(r"<<<PAGE (\d+)>>>", text)
    st = {}
    for i in range(1, len(parts), 2):
        n = int(parts[i])
        if lo <= n <= hi:
            st[n] = len(parts[i + 1].strip())
    return st


def img_names(tag, lo, hi):
    out = []
    for n in range(lo, hi + 1):
        fn = "phys_%s_p%02d.webp" % (tag, n)
        if os.path.exists(os.path.join(IMGDIR, fn)):
            out.append(fn)
    return out


def main():
    texts = {
        "Heat notes.pdf": load("Heat_notes"),
        "Gases note.pdf": load("Gases_note"),
    }
    sol = load("Book_1_Heat_Notes_solution")

    print("產出素材包：\n")
    for t in TOPICS:
        tid = t["tid"]
        wlo, whi = WORKSHEET[tid]
        slo, shi = SOLUTION[tid]
        wtext = texts[t["pdf"]]
        tag = "heat" if t["pdf"].startswith("Heat") else "gas"

        stats = page_stats(wtext, wlo, whi)
        sparse = [n for n, c in stats.items() if c < 150]
        imgs = img_names(tag, wlo, whi)

        L = []
        L.append("# 轉錄素材包 · %s（第%d課 %s）\n" % (tid, t["lesson"], t["title"]))
        L.append("## 課題信息")
        L.append("| 項目 | 值 |")
        L.append("|---|---|")
        L.append("| 課題 id | `%s` |" % tid)
        L.append("| 課題標題 | %s |" % t["title"])
        L.append("| 來源 PDF | `%s` |" % t["pdf"])
        L.append("| 工作紙頁範圍 | 第 %d–%d 頁 |" % (wlo, whi))
        L.append("| 答案頁範圍 | solution 第 %d–%d 頁 |" % (slo, shi))
        L.append("")
        L.append("## 章節規劃")
        for s in t["sections"]:
            L.append("- `%s` = %s %s" % (s["sid"], s["num"], s["title"]))
        L.append("")
        L.append("## 頁圖清單（轉錄時用 `![](img/<檔名>)` 內嵌）")
        for fn in imgs:
            L.append("- `%s`" % fn)
        L.append("")
        if sparse:
            L.append("> ⚠️ 以下頁面的文字層很薄（<150 字元），內容主要在**圖片／圖表**裡，")
            L.append("> 必須看頁圖才能轉錄，不能只靠文字：")
            L.append("> " + ", ".join("p%d(%d字)" % (n, stats[n]) for n in sorted(sparse)))
            L.append("")
        if tid in DSE_PAGES:
            L.append("> 📝 本課題第 %d–%d 頁是**歷屆 DSE 公開試題**（題目為圖片形式，含作答空行），"
                     % (min(DSE_PAGES[tid]), max(DSE_PAGES[tid])))
            L.append("> 這部分不轉成一般知識點，應作為「歷年試題」整頁保留。")
            L.append("")

        L.append("---\n")
        L.append("## 一、工作紙原文（`____` = 待填答案）\n")
        L.append("```")
        L.append(page_slice(wtext, wlo, whi))
        L.append("```")
        L.append("")
        L.append("---\n")
        L.append("## 二、配套答案（按同一題號順序）\n")
        L.append("```")
        L.append(page_slice(sol, slo, shi))
        L.append("```")

        op = os.path.join(OUT, tid + ".md")
        with io.open(op, "w", encoding="utf-8") as f:
            f.write("\n".join(L))
        print("  %-7s %-14s %6.1f KB  頁圖 %2d 張  文字稀疏頁 %2d"
              % (tid, t["title"], os.path.getsize(op) / 1024.0, len(imgs), len(sparse)))

    print("\n輸出目錄：%s" % OUT)


if __name__ == "__main__":
    main()
