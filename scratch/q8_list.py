import json, io

BASE = r"D:\deepseek-harness\default-workspace\f6chem"
d = json.load(io.open(BASE + r"\data\8.json", encoding="utf-8"))
out = io.open(BASE + r"\scratch\q8_points.txt", "w", encoding="utf-8")

secs = d["sections"]
tot = 0
ocr = []
for s in secs:
    pts = s.get("points") or []
    tot += len(pts)
    out.write(f"== {s['id']} | {s['title']} | points={len(pts)}\n")
    for p in pts:
        body = p.get("body") or ""
        bad = ("OCR 不清" in body)
        if bad:
            ocr.append(p["id"])
        out.write(f"   {p['id']} | {p['title']}{'  [OCR-UNCLEAR]' if bad else ''}\n")
out.write(f"\nTOTAL sections={len(secs)} points={tot}\n")
out.write(f"OCR-UNCLEAR points: {ocr}\n")
out.write("TOP: id=%s title=%s\n" % (d.get("id"), d.get("title")))
out.close()
print("ok", tot, len(ocr))