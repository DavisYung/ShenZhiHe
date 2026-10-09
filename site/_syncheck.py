# -*- coding: utf-8 -*-
"""從產出的單檔網站抽出應用腳本，交給 node --check 做語法檢查。"""
import io, os, re, subprocess, sys

sys.stdout.reconfigure(encoding="utf-8")
BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _sitefile import built_html  # noqa: E402
SRC = built_html()
OUT = os.path.join(BASE, "_appcheck.js")

h = io.open(SRC, encoding="utf-8").read()
# 抓最後一段 <script> ... </script>（應用邏輯），排除 payload 資料段
blocks = re.findall(r"<script(?:\s[^>]*)?>(.*?)</script>", h, re.S)
app = None
for b in blocks:
    if '"use strict"' in b or "'use strict'" in b:
        app = b
if app is None:
    sys.exit("找不到應用腳本")
io.open(OUT, "w", encoding="utf-8").write(app)
print("script chars:", len(app))

node = r"D:\node.exe"
r = subprocess.run([node, "--check", OUT], capture_output=True)
print("node --check exit:", r.returncode)
if r.stdout:
    print(r.stdout.decode("utf-8", "replace"))
if r.stderr:
    print(r.stderr.decode("utf-8", "replace"))

# 掃描 U+FFFD
bad = h.count("\ufffd")
print("U+FFFD count:", bad)

# 檢查科目資料確實分開注入
import json
m = re.search(r'<script id="payload" type="application/json">(.*?)</script>', h, re.S)
payload = json.loads(m.group(1).replace("<\\/", "</"))
for s in payload["subjects"]:
    st = s["stats"]
    print("  subject %-5s %-4s ready=%-5s topics=%2d points=%3d links=%2d quiz=%3d"
          % (s["id"], s["title"], s["ready"], st["topics"], st["points"],
             st["links"], st["questions"]))