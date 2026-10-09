# -*- coding: utf-8 -*-
"""在 app.asar（二進位包）裡搜尋 genui 圍欄修復相關字串，找出檔案偏移。"""
import io, os, re, sys
sys.stdout.reconfigure(encoding="utf-8")

ASAR = r"D:\deepseek\resources\app.asar"
PAT = [b"genui-fence-repair", b"invalid_json", b"resend_corrected_fence_only",
       b"validate_dsh_ui", b"render_failed", b"block_markdown"]

with open(ASAR, "rb") as f:
    blob = f.read()
print("asar size", len(blob))
for p in PAT:
    idxs = []
    start = 0
    while True:
        i = blob.find(p, start)
        if i < 0:
            break
        idxs.append(i)
        start = i + 1
        if len(idxs) >= 8:
            break
    print("\n%-32s hits=%d" % (p.decode(), len(idxs)))
    for i in idxs[:4]:
        a = max(0, i - 200)
        b = min(len(blob), i + 300)
        seg = blob[a:b].decode("utf-8", "replace").replace("\n", "\\n")
        print("   @%d ... %s ..." % (i, seg))
