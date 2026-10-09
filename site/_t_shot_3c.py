# -*- coding: utf-8 -*-
"""截圖驗證：3c 焓變課題頁 + 首頁課題卡。"""
import io, os, subprocess, sys

sys.stdout.reconfigure(encoding="utf-8")
BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)
from _sitefile import built_html  # noqa: E402

CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
TMP = os.path.join(BASE, "_t_shot_3c.html")
SHOT = os.path.join(BASE, "shots", "v0011_topic3c.png")

H = """
<style>*{animation:none!important;transition:none!important}</style>
<script>
window.addEventListener('load',function(){
  setTimeout(function(){
    location.hash='#/chem/t/3c';
    setTimeout(function(){
      document.querySelectorAll('.view').forEach(function(v){
        v.style.animation='none'; v.style.opacity='1'; v.style.transform='none';
      });
    },500);
  },150);
});
</script>
"""
with io.open(built_html(), encoding="utf-8") as f:
    page = f.read()
assert "3c" in page, "3c not in payload"
with io.open(TMP, "w", encoding="utf-8") as f:
    f.write(page.replace("</body>", H + "</body>"))
cmd = [CHROME, "--headless", "--disable-gpu", "--no-sandbox",
       "--window-size=1000,1200", "--hide-scrollbars",
       "--virtual-time-budget=8000",
       "--screenshot=" + SHOT,
       "--user-data-dir=" + os.path.join(BASE, "_t_profile_shot3c"),
       "file:///" + TMP.replace("\\", "/")]
r = subprocess.run(cmd, capture_output=True, timeout=120)
print("exit", r.returncode, "size", os.path.getsize(SHOT) if os.path.exists(SHOT) else 0)
