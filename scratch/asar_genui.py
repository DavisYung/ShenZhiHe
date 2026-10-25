# -*- coding: utf-8 -*-
"""把 asar 內含關鍵字的檔案抽出來，並 dump 出關鍵字周邊片段。"""
import bisect, json, struct, sys

sys.stdout.reconfigure(encoding="utf-8")
ASAR = r"D:\deepseek\resources\app.asar"
OUT = r"D:\deepseek-harness\default-workspace\f6chem\scratch"

with open(ASAR, "rb") as f:
    f.read(4)
    hp = struct.unpack("<I", f.read(4))[0]
    f.read(4)
    hl = struct.unpack("<I", f.read(4))[0]
    header = f.read(hl).decode("utf-8")
    data_off = 4 + hp
    f.seek(data_off)
    blob = f.read()

h = json.loads(header)
files = []

def walk(node, path):
    if node.get("files"):
        for name, child in node["files"].items():
            walk(child, path + "/" + name)
    else:
        files.append((path, int(node.get("offset", 0)), int(node.get("size", 0))))

walk(h, "")
files.sort(key=lambda x: x[1])
offsets = [x[1] for x in files]

def which_file(off):
    rel = off - data_off
    i = bisect.bisect_right(offsets, rel) - 1
    if i < 0:
        return None
    p, o, s = files[i]
    return p if rel < o + s else None

lower = blob.lower()

KEYS = [b"genui-fence", b"fence-repair", b"render_failed", b"invalid_json",
        b"corrected_fence", b"repair", b"fence"]
# 找出裝有 'genui' 的檔案 → 直接 dump 檔內所有含 repair/fence/genui 的片段
targets = set()
for i in range(len(lower)):
    pass
# 更快：逐檔掃（檔案數 12967，但只要掃 node_modules/@deepseek-ai 與主程式）
import time
t0 = time.time()
fragments = []
for p, o, s in files:
    if s == 0 or s > 40_000_000:
        continue
    low = p.lower()
    if not (low.endswith(".js") or low.endswith(".mjs") or low.endswith(".cjs")
            or low.endswith(".json") or low.endswith(".md") or low.endswith(".ts")):
        continue
    data = blob[o:o + s]
    dl = data.lower()
    for key in (b"genui", b"render_failed", b"resend_corrected"):
        idx = dl.find(key)
        while idx >= 0:
            a = max(0, idx - 400)
            b = min(s, idx + 700)
            fragments.append((p, data[a:b].decode("utf-8", "replace")))
            idx = dl.find(key, idx + 1)
        if len(fragments) > 400:
            break
    if len(fragments) > 400:
        break
print("scan time %.1fs fragments=%d" % (time.time() - t0, len(fragments)))

seen_files = {}
for p, frag in fragments:
    seen_files.setdefault(p, []).append(frag)
print("\n承載檔案：")
for p in seen_files:
    print("  ", p)

with open(OUT + r"\genui_frag.txt", "w", encoding="utf-8") as f:
    for p, frags in seen_files.items():
        f.write("\n\n######## %s ########\n" % p)
        for fr in frags[:6]:
            f.write("\n--- fragment ---\n" + fr + "\n")
print("dumped -> scratch/genui_frag.txt")
