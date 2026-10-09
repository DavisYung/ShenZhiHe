# -*- coding: utf-8 -*-
"""把化学 DSE past paper PDF 渲染成图再 OCR 成文字（本机 RapidOCR，无网络）。

用法：python ocr_papers.py <doc> [y0] [y1]
  doc = p1 | p2 | ms | all（默认 all）
  y0 y1 = 年份区间（含端点），用于并行分段
  p1 = 卷一（甲部选择 + 乙部长题）  p2 = 卷二（选修结构题）  ms = 参考答案
输出：f6chem/scratch/pp/<年>_<p1|p2|ms>.txt（带 === page N === 分页标记）
"""
import io
import os
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

SRC = os.path.join(os.environ["USERPROFILE"], "Downloads", "化学DSE Past Paper")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pp")
DPI = 250
ALL_YEARS = [2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023]

def jobs_for(doc, y0=None, y1=None):
    years = [y for y in ALL_YEARS if (y0 is None or y >= y0) and (y1 is None or y <= y1)]
    if doc == "p1":
        return [(y, "%d_卷一.pdf" % y, "%d_p1.txt" % y) for y in years]
    if doc == "p2":
        return [(y, "%d_卷二.pdf" % y, "%d_p2.txt" % y) for y in years]
    if doc == "ms":
        return [(y, "%d_参考答案.pdf" % y, "%d_ms.txt" % y) for y in years]
    raise SystemExit("unknown doc: " + doc)


def group_lines(items):
    """把 OCR 框按 y 聚成行（与 data/ocr_page.py 同款逻辑），行内按 x 排序。"""
    items = sorted(items, key=lambda t: (t[1], t[0]))
    lines = []
    for it in items:
        placed = False
        for ln in lines:
            if abs(it[1] - ln["cy"]) < 18:
                ln["items"].append(it)
                ln["cy"] = (ln["cy"] * (len(ln["items"]) - 1) + it[1]) / len(ln["items"])
                placed = True
                break
        if not placed:
            lines.append({"cy": it[1], "items": [it]})
    out = []
    for ln in sorted(lines, key=lambda l: l["cy"]):
        parts = sorted(ln["items"], key=lambda t: t[0])
        out.append(" ".join(t[4] for t in parts))
    return out


def main():
    doc = sys.argv[1] if len(sys.argv) > 1 else "all"
    y0 = int(sys.argv[2]) if len(sys.argv) > 2 else None
    y1 = int(sys.argv[3]) if len(sys.argv) > 3 else None
    if doc == "all":
        jobs = jobs_for("p1", y0, y1) + jobs_for("p2", y0, y1) + jobs_for("ms", y0, y1)
    else:
        jobs = jobs_for(doc, y0, y1)

    import pymupdf
    from rapidocr_onnxruntime import RapidOCR
    engine = RapidOCR()

    os.makedirs(OUT, exist_ok=True)
    for year, pdf_name, txt_name in jobs:
        pdf_path = os.path.join(SRC, str(year), pdf_name)
        txt_path = os.path.join(OUT, txt_name)
        if not os.path.exists(pdf_path):
            print("MISS PDF:", pdf_path)
            continue
        doc = pymupdf.open(pdf_path)
        chunks = []
        for i, page in enumerate(doc):
            pix = page.get_pixmap(dpi=DPI)
            # 直接把 PNG 字节喂给 OCR：不要落临时档——并行分段跑时
            # 多个进程共用同一个临时路径会互相踩踏（读到半写的图直接崩）
            result, _ = engine(pix.tobytes("png"))
            items = []
            if result:
                for box, text, score in result:
                    xs = [p[0] for p in box]
                    ys = [p[1] for p in box]
                    items.append((min(xs), min(ys), max(xs), max(ys), text))
            body = "\n".join(group_lines(items)) if items else "(NO TEXT)"
            chunks.append("=== page %d ===\n%s" % (i + 1, body))
            print("%s page %d: %d lines" % (txt_name, i + 1, len(group_lines(items)) if items else 0))
        doc.close()
        with io.open(txt_path, "w", encoding="utf-8") as f:
            f.write("\n".join(chunks))
        print("written:", txt_path)
    print("ALL DONE")


if __name__ == "__main__":
    main()
