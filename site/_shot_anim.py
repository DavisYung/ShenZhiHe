# -*- coding: utf-8 -*-
"""截图：注入指定动画模式后截设置页/课题页，肉眼比对三档差异。

用法：python _shot_anim.py <mode> <out.png> [hash] [w] [h]
  mode = full | simple | off
"""
import io
import os
import shutil
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
BASE = os.path.dirname(os.path.abspath(__file__))
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

mode = sys.argv[1] if len(sys.argv) > 1 else "full"
name = sys.argv[2] if len(sys.argv) > 2 else "_shot_anim.png"
hash_ = sys.argv[3] if len(sys.argv) > 3 else "#/chem/t/2a"
w = sys.argv[4] if len(sys.argv) > 4 else "900"
h = sys.argv[5] if len(sys.argv) > 5 else "1200"

SRC = os.path.join(BASE, "_shotsrc.html")
shutil.copyfile(os.path.join(BASE, "神智核.html"), SRC)
with io.open(SRC, encoding="utf-8") as f:
    page = f.read()
# 在載入前就寫好 localStorage，確保首屏即為指定模式（避免先全開再切換）
inject = ("<script>try{localStorage.setItem('f6note.anim','%s');"
          "localStorage.setItem('f6note.animk','1');"
          "localStorage.setItem('f6note.animforce','1');}catch(e){}</script>" % mode)
with io.open(SRC, "w", encoding="utf-8") as f:
    f.write(page.replace("<head>", "<head>" + inject, 1))

SHOT = os.path.join(BASE, name)
url = "file:///" + SRC.replace("\\", "/") + hash_
cmd = [CHROME, "--headless=new", "--disable-gpu", "--no-sandbox",
       "--window-size=%s,%s" % (w, h), "--hide-scrollbars",
       "--virtual-time-budget=6000",
       "--screenshot=" + SHOT, "--dump-dom",
       "--user-data-dir=" + os.path.join(BASE, "_t_profile_shota"),
       url]
r = subprocess.run(cmd, capture_output=True, timeout=180)
print("mode=%s exit=%d shot=%s size=%s" % (mode, r.returncode, os.path.exists(SHOT),
      os.path.getsize(SHOT) if os.path.exists(SHOT) else 0))
