# -*- coding: utf-8 -*-
"""在 asar 裡搜尋圍欄修復相關字串所在的檔案（沿用已驗證可用的 header 解析）。"""
import bisect, json, struct, sys

sys.stdout.reconfigure(encoding="utf-8")
ASAR = r"D:\deepseek\resources\app.asar"

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
print("files:", len(files), "data_off:", data_off, "blob bytes:", len(blob))
files.sort(key=lambda x: x[1])
offsets = [x[1] for x in files]

def which_file(off):
    rel = off - data_off
    if rel < 0:
        return "?"
    i = bisect.bisect_right(offsets, rel) - 1
    if i < 0:
        return "?"
    p, o, s = files[i]
    return p if rel < o + s else "?"

def find_all(pat, limit=800):
    out, start = [], 0
    while len(out) < limit:
        i = blob.find(pat, start)
        if i < 0:
            break
        out.append(i + data_off)
        start = i + 1
    return out

PATS = [b"genui-fence-repair", b"resend_corrected_fence_only", b"dsh-ui",
        b"validate_dsh_ui", b"render_failed", b"fingerprint",
        b"block_markdown", b"invalid_json", b"repair=failed"]
for p in PATS:
    hits = find_all(p)
    names = {}
    for off in hits:
        names.setdefault(which_file(off), []).append(off)
    print("%-34s total=%d" % (p.decode(), len(hits)))
    for n, offs in sorted(names.items(), key=lambda x: -len(x[1]))[:6]:
        print("     %4d  %s" % (len(offs), n))
    print()
