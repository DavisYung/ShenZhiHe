# -*- coding: utf-8 -*-
"""抽取 HTML 內所有 <script>（排除 type=application/json 的 payload）逐塊語法檢查。

用法：python _extract_js.py <html>   # 預設 template.html
輸出：_js_block_N.js，並自動用 node --check 驗每一塊。
"""
import io
import os
import re
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
BASE = os.path.dirname(os.path.abspath(__file__))
NODE = r"C:\Users\guomi\.dsh\dsh-runtimes\dsh-primary-runtime\dependencies\node\bin\node.exe"

PATH = sys.argv[1] if len(sys.argv) > 1 else "template.html"
src = io.open(PATH, encoding="utf-8").read()
# 抓所有不帶 type 的 <script>（payload 帶 type=application/json，會被排除）
blocks = re.findall(r"<script>(.*?)</script>", src, re.S)
print("%s: %d 個可執行 script 區塊" % (PATH, len(blocks)))
bad = 0
for i, b in enumerate(blocks):
    out = os.path.join(BASE, "_js_block_%d.js" % i)
    io.open(out, "w", encoding="utf-8", newline="\n").write(b)
    r = subprocess.run([NODE, "--check", out], capture_output=True)
    tag = "OK" if r.returncode == 0 else "FAIL"
    print("  block %d: %s (%d chars)" % (i, tag, len(b)))
    if r.returncode != 0:
        bad += 1
        print(r.stderr.decode("utf-8", "replace")[-900:])
    os.remove(out)
print("結果：", "全部通過 ✅" if bad == 0 else "%d 塊失敗 ❌" % bad)
sys.exit(1 if bad else 0)
