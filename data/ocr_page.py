import sys, os
sys.path.insert(0, r"C:\Users\guomi\OneDrive\文件\deepseek-harness\default-workspace\f6chem\pylibs3")
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from rapidocr_onnxruntime import RapidOCR

img = sys.argv[1]
engine = RapidOCR()
result, elapse = engine(img)
if not result:
    print("NO TEXT")
    sys.exit(0)

items = []
for box, text, score in result:
    xs = [p[0] for p in box]
    ys = [p[1] for p in box]
    items.append((min(ys), min(xs), max(xs), text, score))

# group into lines: sort by y, merge boxes with overlapping y-bands
items.sort(key=lambda t: (t[0], t[1]))
lines = []
for it in items:
    placed = False
    for ln in lines:
        # same line if vertical overlap > 50%
        iy0, iy1 = it[0], it[0] + 1
        h = 20
        cy = it[0]
        lcy = ln["cy"]
        if abs(cy - lcy) < 18:
            ln["items"].append(it)
            ln["cy"] = (lcy * (len(ln["items"]) - 1) + cy) / len(ln["items"])
            placed = True
            break
    if not placed:
        lines.append({"cy": it[0], "items": [it]})

for ln in sorted(lines, key=lambda l: l["cy"]):
    parts = sorted(ln["items"], key=lambda t: t[1])
    print(" | ".join("%s(%.2f)" % (t[3], t[4]) for t in parts))
