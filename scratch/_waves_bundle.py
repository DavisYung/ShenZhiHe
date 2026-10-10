# -*- coding: utf-8 -*-
"""波動學素材包：按課題切分「工作紙原文 + 配套答案 + 頁圖清單」。

與熱學/力學同構，差異：
  · 工作紙單冊（ws_3A3B notes.pdf，85 頁，第 1–7 課）
  · 答案兩份：ws_3A_ans_ce（第1–3課）+ ws_3B_ans_ce（第4–7課）
  · 3B 答案括號頁碼是「分冊局部編號」（= 總頁碼 − 36），素材包統一用總頁碼

產出：scratch/phys_bundles/<tid>.md（與熱學/力學同目錄）
"""
import io
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

SCRATCH = os.path.dirname(os.path.abspath(__file__))
EX = os.path.join(SCRATCH, "waves_extract")
OUT = os.path.join(SCRATCH, "phys_bundles")
os.makedirs(OUT, exist_ok=True)
IMGDIR = os.path.join(os.path.dirname(SCRATCH), "site", "img")

TOPICS = [
    {"tid": "wave1", "lesson": 1, "title": "光線與反射",
     "ws": (1, 9), "ans": ("ws_3A_ans_ce", 1, 3),
     "sections": [("wave1-s1", "1.1 光線"), ("wave1-s2", "1.2 反射定律"),
                  ("wave1-s3", "1.3 平面鏡成像")]},
    {"tid": "wave2", "lesson": 2, "title": "折射與全內反射",
     "ws": (10, 20), "ans": ("ws_3A_ans_ce", 4, 6),
     "sections": [("wave2-s1", "2.1 折射定律"), ("wave2-s2", "2.2 光的全內反射")]},
    {"tid": "wave3", "lesson": 3, "title": "透鏡成像",
     "ws": (21, 36), "ans": ("ws_3A_ans_ce", 7, 12),
     "sections": [("wave3-s1", "3.1 凸透鏡與凹透鏡"), ("wave3-s2", "3.2 凸透鏡成像"),
                  ("wave3-s3", "3.3 凹透鏡成像")]},
    {"tid": "wave4", "lesson": 4, "title": "波動基礎",
     "ws": (37, 44), "ans": ("ws_3B_ans_ce", 1, 2),
     "sections": [("wave4-s1", "4.1 波動"), ("wave4-s2", "4.2 粒子運動與波動"),
                  ("wave4-s3", "4.3 以線圖描述橫波")]},
    {"tid": "wave5", "lesson": 5, "title": "水波與波的現象",
     "ws": (45, 58), "ans": ("ws_3B_ans_ce", 3, 5),
     "sections": [("wave5-s1", "5.1 利用水波研究波的現象"), ("wave5-s2", "5.2 波的反射與折射"),
                  ("wave5-s3", "5.3 波的衍射"), ("wave5-s4", "5.4 波的干涉"),
                  ("wave5-s5", "5.5 駐波")]},
    {"tid": "wave6", "lesson": 6, "title": "光的波動本質與電磁波",
     "ws": (59, 72), "ans": ("ws_3B_ans_ce", 6, 8),
     "sections": [("wave6-s1", "6.1 光的波動本質"), ("wave6-s2", "6.2 楊氏雙縫實驗與平面透射光柵"),
                  ("wave6-s3", "6.3 電磁波")]},
    {"tid": "wave7", "lesson": 7, "title": "縱波與聲音",
     "ws": (73, 85), "ans": ("ws_3B_ans_ce", 9, 12),
     "sections": [("wave7-s1", "7.1 縱波"), ("wave7-s2", "7.2 聲音的波動本質"),
                  ("wave7-s3", "7.3 聲音的特性"), ("wave7-s4", "7.4 樂音與噪音")]},
]

WS_PDF = "ws_3A3B notes.pdf"


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


def img_names(lo, hi):
    out = []
    for n in range(lo, hi + 1):
        fn = "phys_wav_p%02d.webp" % n
        if os.path.exists(os.path.join(IMGDIR, fn)):
            out.append(fn)
    return out


def main():
    ws = load("ws_3A3B_notes")
    ans_cache = {}

    print("產出素材包：\n")
    for t in TOPICS:
        tid = t["tid"]
        wlo, whi = t["ws"]
        ans_name, alo, ahi = t["ans"]
        if ans_name not in ans_cache:
            ans_cache[ans_name] = load(ans_name)

        stats = page_stats(ws, wlo, whi)
        sparse = [n for n, c in stats.items() if c < 150]
        imgs = img_names(wlo, whi)

        L = []
        L.append("# 轉錄素材包 · %s（第%d課 %s）\n" % (tid, t["lesson"], t["title"]))
        L.append("## 課題信息")
        L.append("| 項目 | 值 |")
        L.append("|---|---|")
        L.append("| 課題 id | `%s` |" % tid)
        L.append("| 課題標題 | %s |" % t["title"])
        L.append("| 來源 PDF | `%s` |" % WS_PDF)
        L.append("| 工作紙頁範圍 | 第 %d–%d 頁（85 頁總表的總頁碼） |" % (wlo, whi))
        L.append("| 答案頁範圍 | `%s.pdf` 第 %d–%d 頁 |" % (ans_name, alo, ahi))
        L.append("")
        L.append("> 注意：答案裡括號標的頁碼是**分冊局部編號**（3B 冊 = 總頁碼 − 36），")
        L.append("> 本素材包與轉錄用的 page 欄位一律用 **85 頁總表的總頁碼**。")
        L.append("")
        L.append("## 章節規劃")
        for s in t["sections"]:
            L.append("- `%s` = %s" % (s[0], s[1]))
        L.append("")
        L.append("## 頁圖清單（轉錄時用 `![](img/<檔名>)` 內嵌）")
        L.append("> **圖示前綴**：本課題是 `phys_wav_`（不是 heat 也不是 mecha）。")
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
        L.append(page_slice(ws, wlo, whi))
        L.append("```")
        L.append("")
        L.append("---\n")
        L.append("## 二、配套答案（按同一題號順序）\n")
        L.append("```")
        L.append(page_slice(ans_cache[ans_name], alo, ahi))
        L.append("```")

        op = os.path.join(OUT, tid + ".md")
        with io.open(op, "w", encoding="utf-8") as f:
            f.write("\n".join(L))
        print("  %-7s %-16s ws p%-2d–%-2d  圖%2d  稀疏頁%2d  %5.1f KB"
              % (tid, t["title"], wlo, whi, len(imgs), len(sparse),
                 os.path.getsize(op) / 1024.0))

    print("\n輸出目錄：%s" % OUT)


if __name__ == "__main__":
    main()
