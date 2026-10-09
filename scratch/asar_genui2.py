# -*- coding: utf-8 -*-
"""精準搜尋組合字串與跨檔搜尋 'fence-repair' / 'render_failed'。"""
import bisect, json, struct, sys, time

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
        return None
    p, o, s = files[i]
    return p if rel < o + s else None

def find(pat, limit=50):
    out, start = [], 0
    dl = blob.lower()
    while len(out) < limit:
        i = dl.find(pat, start)
        if i < 0:
            break
        out.append(i + data_off)
        start = i + 1
    return out

for pat in [b"fence-repair", b"render_failed", b"resend_corrected",
            b"block_markdown", b"next=resend", b"status=render",
            b"fingerprint=", b"genui_action", b"[genui"]:
    hits = find(pat)
    print("=== %s : %d" % (pat.decode(), len(hits)))
    for off in hits[:5]:
        n = which_file(off)
        rel = off - data_off
        seg = blob[rel - 300:rel + 500].decode("utf-8", "replace")
        print("  [%s]" % n)
        print("   ..." + seg.replace("\n", "\\n") + "...")
    print()
