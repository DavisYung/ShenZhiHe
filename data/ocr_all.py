import sys, os, glob, time
sys.path.insert(0, r"C:\Users\guomi\OneDrive\文件\deepseek-harness\default-workspace\f6chem\pylibs3")
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from rapidocr_onnxruntime import RapidOCR

SRC = r"C:\Users\guomi\OneDrive\文件\deepseek-harness\default-workspace\f6chem\pages\2a"
OUT = r"C:\Users\guomi\OneDrive\文件\deepseek-harness\default-workspace\f6chem\data\ocr"
os.makedirs(OUT, exist_ok=True)

engine = RapidOCR()
pages = sorted(glob.glob(os.path.join(SRC, "p*.jpg")))
t0 = time.time()
for p in pages:
    name = os.path.basename(p).replace(".jpg", ".txt")
    dst = os.path.join(OUT, name)
    if os.path.exists(dst) and os.path.getsize(dst) > 0:
        continue
    res, _ = engine(p)
    items = []
    if res:
        for box, text, score in res:
            ys = [q[1] for q in box]
            xs = [q[0] for q in box]
            items.append((min(ys), min(xs), max(xs), text, score))
    items.sort(key=lambda t: (t[0], t[1]))
    lines = []
    for it in items:
        placed = False
        for ln in lines:
            if abs(ln["cy"] - it[0]) < 18:
                ln["items"].append(it)
                ln["cy"] = (ln["cy"] * (len(ln["items"]) - 1) + it[0]) / len(ln["items"])
                placed = True
                break
        if not placed:
            lines.append({"cy": it[0], "items": [it]})
    with open(dst, "w", encoding="utf-8") as f:
        for ln in sorted(lines, key=lambda l: l["cy"]):
            parts = sorted(ln["items"], key=lambda t: t[1])
            f.write(" | ".join(t[3] for t in parts) + "\n")
    print("%s done (%d lines) %.1fs" % (name, len(lines), time.time() - t0), flush=True)
print("ALL DONE %.1fs" % (time.time() - t0))
