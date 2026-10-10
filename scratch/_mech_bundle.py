# -*- coding: utf-8 -*-
"""力學素材包生成：按課題切分「工作紙原文 + 配套答案 + 頁圖清單」。

與熱學 (_phys_bundle.py) 同構，差異在於：
  · 工作紙分兩冊（mecha = 第1–7課 72頁、mechb = 第8–10課 28頁）
  · 答案本單一檔案（29 頁），按課題切對應頁段

產出：scratch/phys_bundles/<tid>.md（與熱學同目錄，已忽略於 git）
"""
import io
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

SCRATCH = os.path.dirname(os.path.abspath(__file__))
EX = os.path.join(SCRATCH, "mech_extract")
OUT = os.path.join(SCRATCH, "phys_bundles")
os.makedirs(OUT, exist_ok=True)
IMGDIR = os.path.join(os.path.dirname(SCRATCH), "site", "img")

# 課題劃分：忠實對應 PDF 的「第N課」，id 採 mechN（不與 heatN 衝突）
TOPICS = [
    {"tid": "mech1", "lesson": 1, "title": "長度、時間與運動描述",
     "src": "mecha", "ws": (1, 7), "ans": (1, 2),
     "sections": [("mech1-s1", "1.1 長度與時間"), ("mech1-s2", "1.2 距離與位移"),
                  ("mech1-s3", "1.3 速率、速度與加速度"), ("mech1-s4", "1.4 直線上的運動")]},
    {"tid": "mech2", "lesson": 2, "title": "直線運動的線圖與運動方程",
     "src": "mecha", "ws": (8, 19), "ans": (3, 5),
     "sections": [("mech2-s1", "2.1 直線運動的線圖"), ("mech2-s2", "2.2 勻加速運動方程"),
                  ("mech2-s3", "2.3 自由落體的運動")]},
    {"tid": "mech3", "lesson": 3, "title": "力與牛頓運動定律",
     "src": "mecha", "ws": (20, 33), "ans": (6, 9),
     "sections": [("mech3-s1", "3.1 力的簡介"), ("mech3-s2", "3.2 慣性與牛頓第一定律"),
                  ("mech3-s3", "3.3 淨力與牛頓第二定律"), ("mech3-s4", "3.4 重量、摩擦力與流體阻力"),
                  ("mech3-s5", "3.5 作用力與反作用力：牛頓第三定律")]},
    {"tid": "mech4", "lesson": 4, "title": "力的合成與分解",
     "src": "mecha", "ws": (34, 41), "ans": (10, 13),
     "sections": [("mech4-s1", "4.1 力的合成與分解"), ("mech4-s2", "4.2 共面力與牛頓運動定律")]},
    {"tid": "mech5", "lesson": 5, "title": "力矩與剛體平衡",
     "src": "mecha", "ws": (42, 51), "ans": (14, 16),
     "sections": [("mech5-s1", "5.1 力的轉動效應（力矩）"), ("mech5-s2", "5.2 剛體的平衡")]},
    {"tid": "mech6", "lesson": 6, "title": "功、能量與功率",
     "src": "mecha", "ws": (52, 63), "ans": (17, 19),
     "sections": [("mech6-s1", "6.1 功與能量轉移"), ("mech6-s2", "6.2 動能與勢能"),
                  ("mech6-s3", "6.3 能量轉換與能量守恆"), ("mech6-s4", "6.4 功率")]},
    {"tid": "mech7", "lesson": 7, "title": "動量",
     "src": "mecha", "ws": (64, 72), "ans": (20, 21),
     "sections": [("mech7-s1", "7.1 動量守恆"), ("mech7-s2", "7.2 動量變化")]},
    {"tid": "mech8", "lesson": 8, "title": "拋體運動",
     "src": "mechb", "ws": (1, 12), "ans": (22, 24),
     "sections": [("mech8-s1", "8.1 平拋運動"), ("mech8-s2", "8.2 一般拋體運動")]},
    {"tid": "mech9", "lesson": 9, "title": "圓周運動與向心力",
     "src": "mechb", "ws": (13, 22), "ans": (25, 27),
     "sections": [("mech9-s1", "9.1 圓周運動的簡介"), ("mech9-s2", "9.2 向心力")]},
    {"tid": "mech10", "lesson": 10, "title": "萬有引力",
     "src": "mechb", "ws": (23, 28), "ans": (28, 29),
     "sections": [("mech10-s1", "10.1 牛頓萬有引力定律"),
                  ("mech10-s2", "10.2 引力作用下的圓周運動")]},
]

SRC_PDF = {"mecha": "ws_book 2 mechanic notes version 2.pdf",
           "mechb": "ws_book 2 mechanic notes 2.pdf"}
ANS_PDF = "ws_2_ans_ce.pdf"


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
        "mecha": load("ws_book_2_mechanic_notes_version_2"),
        "mechb": load("ws_book_2_mechanic_notes_2"),
    }
    ans = load("ws_2_ans_ce")

    print("產出素材包：\n")
    for t in TOPICS:
        tid = t["tid"]
        wlo, whi = t["ws"]
        alo, ahi = t["ans"]
        wtext = texts[t["src"]]
        tag = t["src"]

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
        L.append("| 來源 PDF | `%s` |" % SRC_PDF[tag])
        L.append("| 工作紙頁範圍 | 第 %d–%d 頁 |" % (wlo, whi))
        L.append("| 答案頁範圍 | `%s` 第 %d–%d 頁 |" % (ANS_PDF, alo, ahi))
        L.append("")
        L.append("## 章節規劃")
        for s in t["sections"]:
            L.append("- `%s` = %s" % (s[0], s[1]))
        L.append("")
        L.append("## 頁圖清單（轉錄時用 `![](img/<檔名>)` 內嵌）")
        L.append("> **圖示前綴注意**：本課題頁圖前綴是 `phys_%s_`，不是 heat。" % tag)
        for fn in imgs:
            L.append("- `%s`" % fn)
        L.append("")
        if sparse:
            L.append("> ⚠️ 以下頁面文字層很薄（<150 字元），內容主要在**圖片／圖表**裡，")
            L.append("> 必須看頁圖才能轉錄，不能只靠文字：")
            L.append("> " + ", ".join("p%d(%d字)" % (n, stats[n]) for n in sorted(sparse)))
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
        L.append(page_slice(ans, alo, ahi))
        L.append("```")

        op = os.path.join(OUT, tid + ".md")
        with io.open(op, "w", encoding="utf-8") as f:
            f.write("\n".join(L))
        print("  %-8s %-14s ws p%-2d–%-2d  圖%2d  稀疏頁%2d  %5.1f KB"
              % (tid, t["title"], wlo, whi, len(imgs), len(sparse),
                 os.path.getsize(op) / 1024.0))

    print("\n輸出目錄：%s" % OUT)


if __name__ == "__main__":
    main()
