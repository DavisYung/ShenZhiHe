# -*- coding: utf-8 -*-
"""把 3C 焓變 PDF 渲染成頁面圖（對齊既有 pages/<tid>/pNNN.jpg 規格）。

pymupdf 不入正式環境：wheel 下載解包到臨時目錄 pytmp，用完即棄。
"""
import io, json, os, re, sys, urllib.request, zipfile

sys.stdout.reconfigure(encoding="utf-8")
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # f6chem
PDF = r"G:\我的云端硬盘\生物\3C 化學筆記～～焓變 TeacherVer.pdf"
TMP_LIB = os.path.join(BASE, "pytmp")
OUT_DIR = os.path.join(BASE, "pages", "3c")

WHEEL = ("https://files.pythonhosted.org/packages/py3/p/pymupdf/"
         "pymupdf-1.28.2-cp310-abi3-win_amd64.whl")
# PyPI 實際直鏈需要走 API 查，避免寫死哈希路徑
API = "https://pypi.org/pypi/pymupdf/1.28.2/json"

os.makedirs(TMP_LIB, exist_ok=True)

# 1) 拿 win_amd64 wheel 直鏈
if not any(n.startswith("fitz") or n == "pymupdf" for n in os.listdir(TMP_LIB)):
    print("fetching wheel metadata ...")
    with urllib.request.urlopen(API, timeout=60) as r:
        meta = json.load(r)
    url = None
    for f in meta["urls"]:
        if f["filename"].endswith("cp310-abi3-win_amd64.whl"):
            url = f["url"]
            break
    if not url:
        sys.exit("no win_amd64 wheel")
    whl = os.path.join(TMP_LIB, "pymupdf.whl")
    print("downloading", url)
    urllib.request.urlretrieve(url, whl)
    with zipfile.ZipFile(whl) as z:
        z.extractall(TMP_LIB)
    os.remove(whl)
    print("extracted")

sys.path.insert(0, TMP_LIB)
import fitz  # noqa: E402

doc = fitz.open(PDF)
print("pages in pdf:", doc.page_count)
os.makedirs(OUT_DIR, exist_ok=True)

# 既有規格 1071x1521 ≈ A4(595x842pt) × 1.8
ZOOM = 1.8
mat = fitz.Matrix(ZOOM, ZOOM)
for i, page in enumerate(doc, start=1):
    pix = page.get_pixmap(matrix=mat)
    if pix.n > 3:
        pix = fitz.Pixmap(fitz.csRGB, pix)
    out = os.path.join(OUT_DIR, "p%03d.jpg" % i)
    pix.save(out, jpg_quality=85)
print("rendered ->", OUT_DIR, len(os.listdir(OUT_DIR)), "files")

# 2) 更新 pages/meta.json
meta_path = os.path.join(BASE, "pages", "meta.json")
meta = json.load(io.open(meta_path, encoding="utf-8"))
meta["3c"] = {"file": os.path.basename(PDF), "pages": doc.page_count}
# 按課題序保持整潔
meta = dict(sorted(meta.items()))
with io.open(meta_path, "w", encoding="utf-8") as f:
    json.dump(meta, f, ensure_ascii=False, indent=1)
    f.write("\n")
print("meta.json updated:", list(meta.keys()))

# 3) 對一張圖的尺寸確認
import struct
def jpg_size(path):
    with open(path, "rb") as f:
        f.read(2)
        while True:
            b = f.read(1)
            if not b:
                return None
            while b != b"\xff":
                b = f.read(1)
            m = f.read(1)
            while m == b"\xff":
                m = f.read(1)
            if m[0] in (0xc0, 0xc1, 0xc2, 0xc3):
                f.read(3)
                h, w = struct.unpack(">HH", f.read(4))
                return w, h
            else:
                ln = struct.unpack(">H", f.read(2))[0]
                f.read(ln - 2)

print("sample size:", jpg_size(os.path.join(OUT_DIR, "p001.jpg")))
