# -*- coding: utf-8 -*-
"""版面分析：把页图切成内容块，標記疑似圖塊（供後續裁剪+語義掛載）。

算法（PIL+numpy，無需 CV 庫）：
1. 灰度→二值化（自適應閾值：頁面中位亮度-40）
2. 水平墨跡投影，空白帶（連續 >=22px 幾乎無墨）切塊
3. 块分类：
   - 行结构检测：块内 rowsig 局部峰（>=4 个峰、峰高>基线2倍、间距均匀）
   - 长横线检测：二值行 run-length > 150px 的像素对数（表格线/框/坐标轴）
   - 满足「>=4 个规整行 且 无长横线」→ text_like；否则 → fig_like
4. 过滤：高 <70px（页眉/标题条）、墨占比 <0.4%（脏点）的块丢弃
输出：pages/<tid>/blocks.json = [{page, y1, y2, kind, score, ink}]
"""
import io, json, os, sys

import numpy as np
from PIL import Image

sys.stdout.reconfigure(encoding="utf-8")
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGES = os.path.join(BASE, "pages")

BAND = 22          # 空白带最小高度（px）
MIN_H = 70         # 块最小高度
MIN_INK = 0.004    # 墨占比下限
LONG_RUN = 150     # 长横线 run 长度


def page_blocks(path):
    im = Image.open(path).convert("L")
    w, h = im.size
    a = np.asarray(im)
    thr = float(np.median(a)) - 40
    binimg = a < thr                      # True = 墨
    rowsig = binimg.sum(axis=1)

    # 空白带切块
    blank = rowsig < (w * 0.004)
    blocks, y = [], None
    for i, b in enumerate(blank):
        if not b and y is None:
            y = i
        elif b and y is not None:
            if i - y >= 10:
                blocks.append((y, i))
            y = None
    if y is not None:
        blocks.append((y, h))
    # 相邻块如果间隙 < BAND（噪声空隙）就合并
    merged = []
    for b in blocks:
        if merged and b[0] - merged[-1][1] < BAND:
            merged[-1] = (merged[-1][0], b[1])
        else:
            merged.append(list(b) if False else (b[0], b[1]))

    out = []
    for (y1, y2) in merged:
        hh = y2 - y1
        if hh < MIN_H:
            continue
        seg = binimg[y1:y2]
        ink = float(seg.mean())
        if ink < MIN_INK:
            continue
        rs = rowsig[y1:y2]
        # 行结构：局部峰
        base = rs.mean()
        peaks = []
        i = 1
        while i < len(rs) - 1:
            if rs[i] > base * 2 and rs[i] >= rs[i - 1] and rs[i] >= rs[i + 1]:
                # 找峰宽
                j = i
                while j < len(rs) - 1 and rs[j] > base * 1.2:
                    j += 1
                peaks.append((i + j) // 2)
                i = j + 3
            else:
                i += 1
        # 峰间距均匀度（文字行特征）
        regular = False
        if len(peaks) >= 4:
            gaps = np.diff(peaks)
            if len(gaps) >= 2 and gaps.mean() > 8:
                regular = float(gaps.std() / gaps.mean()) < 0.45
        # 长横线（表格/框/坐标轴）
        row_runs = 0
        for yy in range(0, hh, 3):
            row = seg[yy]
            run = mx = 0
            for v in row:
                if v:
                    run += 1
                    mx = max(mx, run)
                else:
                    run = 0
            if mx >= LONG_RUN:
                row_runs += 1
        kind = "text" if (regular and row_runs < 2) else "fig"
        out.append({"y1": y1, "y2": y2, "kind": kind,
                    "rows": len(peaks), "lines": row_runs,
                    "ink": round(ink, 4), "h": hh})
    return out, (w, h)


def main():
    import glob
    meta = json.load(io.open(os.path.join(PAGES, "meta.json"), encoding="utf-8"))
    summary = {}
    for tid in sorted(meta):                      # 只处理正式课题，跳过 3bL/6t 等旧实验目录
        d = os.path.join(PAGES, tid)
        if not os.path.isdir(d):
            continue
        res = {}
        for f in sorted(glob.glob(os.path.join(d, "p*.jpg"))):
            pg = int(os.path.basename(f)[1:4])    # p001.jpg -> 1（修正原 [1:3] 坍缩 bug）
            blocks, size = page_blocks(f)
            res[str(pg)] = {"size": size, "blocks": blocks}
        summary[tid] = res
        n_all = sum(len(v["blocks"]) for v in res.values())
        n_fig = sum(1 for v in res.values() for b in v["blocks"] if b["kind"] == "fig")
        print("%-4s pages=%d blocks=%d fig=%d" % (tid, len(res), n_all, n_fig))
    with io.open(os.path.join(PAGES, "blocks.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f)
    print("written pages/blocks.json")


if __name__ == "__main__":
    main()
