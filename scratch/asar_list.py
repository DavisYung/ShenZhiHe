# -*- coding: utf-8 -*-
"""列出 app.asar 內的檔案，並找出 genui 圍欄修復相關的模組路徑。"""
import io, json, os, struct, sys

sys.stdout.reconfigure(encoding="utf-8")
ASAR = r"D:\deepseek\resources\app.asar"

with open(ASAR, "rb") as f:
    # asar: 4B pickle大小 + 4B header pickle大小 + 4B header大小 + 4B header字串長 + JSON
    f.read(4)
    hp = struct.unpack("<I", f.read(4))[0]
    hs = struct.unpack("<I", f.read(4))[0]
    hl = struct.unpack("<I", f.read(4))[0]
    header = f.read(hl).decode("utf-8")
    data_off = 8 + hp  # 4+4 header pickle + hp(header pickle 內含 hs+hl)
    # 更穩：data offset = 4(pickle size) + hp
    data_off = 4 + hp
    h = json.loads(header)

hits = []

def walk(node, path):
    if node.get("files"):
        for name, child in node["files"].items():
            walk(child, path + "/" + name)
    else:
        p = path
        low = p.lower()
        if ("genui" in low or "fence" in low or "dsh-ui" in low
                or "validate_dsh" in low or "repair" in low):
            hits.append((p, node.get("size", 0)))

walk(h, "")

print("找到 %d 個候選檔：" % len(hits))
for p, s in sorted(hits):
    print("  %9d  %s" % (s, p))
