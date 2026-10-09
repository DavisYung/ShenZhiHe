# -*- coding: utf-8 -*-
"""擴大搜尋：genui / fence / dsh-ui 相關字串（不分大小寫），列出所有承載檔案。"""
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
files.sort(key=lambda x: x[1])
offsets = [x[1] for x in files]

def which_file(off):
    rel = off - data_off
    i = bisect.bisect_right(offsets, rel) - 1
    if i < 0:
        return "?"
    p, o, s = files[i]
    return p if rel < o + s else "?"

lower = blob.lower()

def scan(pat):
    out, start = {}, 0
    while True:
        i = lower.find(pat, start)
        if i < 0:
            break
        n = which_file(i + data_off)
        out[n] = out.get(n, 0) + 1
        start = i + 1
    return out

for pat in [b"genui", b"dsh-ui", b"fence", b"validate_dsh", b"repair_failed",
            b"repair"]:
    res = scan(pat)
    print("=== %s : %d 檔" % (pat.decode(), len(res)))
    for n, c in sorted(res.items(), key=lambda x: -x[1])[:12]:
        print("   %5d  %s" % (c, n))
    print()
