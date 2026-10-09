# -*- coding: utf-8 -*-
"""截一張指定 hash 的頁面圖（完全比照 _t_dwell 的 headless 參數）。

用法：python _shot.py [hash] [檔名] [寬] [高] [scroll]
  scroll = 注入腳本把 #vcontent 捲到中段（檢查占位塊／卡片重疊）
"""
import io
import os
import shutil
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8")
BASE = os.path.dirname(os.path.abspath(__file__))
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

hash_ = sys.argv[1] if len(sys.argv) > 1 else "#/chem/t/2a"
name = sys.argv[2] if len(sys.argv) > 2 else "_shot.png"
w = sys.argv[3] if len(sys.argv) > 3 else "900"
h = sys.argv[4] if len(sys.argv) > 4 else "1400"
mode = sys.argv[5] if len(sys.argv) > 5 else ""

SRC = os.path.join(BASE, "_shotsrc.html")
shutil.copyfile(os.path.join(BASE, "神智核.html"), SRC)
if mode == "scroll":
    with io.open(SRC, encoding="utf-8") as f:
        page = f.read()
    inject = ("<script>setTimeout(function(){"
              "var vc=document.getElementById('vcontent');"
              "if(vc){vc.scrollTop=Math.round(vc.scrollHeight*0.45);}"
              "},600);</script>")
    with io.open(SRC, "w", encoding="utf-8") as f:
        f.write(page.replace("</body>", inject + "</body>"))

SHOT = os.path.join(BASE, name)
url = "file:///" + SRC.replace("\\", "/") + hash_
cmd = [CHROME, "--headless=new", "--disable-gpu", "--no-sandbox",
       "--window-size=%s,%s" % (w, h), "--hide-scrollbars",
       "--virtual-time-budget=6000",
       "--screenshot=" + SHOT, "--dump-dom",
       "--user-data-dir=" + os.path.join(BASE, "_t_profile_shot"),
       url]
r = subprocess.run(cmd, capture_output=True, timeout=180)
print("exit", r.returncode, "shot", os.path.exists(SHOT),
      os.path.getsize(SHOT) if os.path.exists(SHOT) else 0)
if not os.path.exists(SHOT):
    print(r.stderr.decode("utf-8", "replace")[-800:])
