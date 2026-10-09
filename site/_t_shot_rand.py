# -*- coding: utf-8 -*-
"""截圖驗證：測驗頁的「🎲 隨機抽題」區塊。"""
import io, os, subprocess, sys

sys.stdout.reconfigure(encoding="utf-8")
BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)
from _sitefile import built_html  # noqa: E402

CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
TMP = os.path.join(BASE, "_t_shot_rand.html")
SHOT = os.path.join(BASE, "shots", "v0010_randquiz.png")

H = """
<style>*{animation:none!important;transition:none!important}</style>
<script>
window.addEventListener('load',function(){
  setTimeout(function(){
    location.hash='#/quiz';
    setTimeout(function(){
      document.querySelectorAll('.view').forEach(function(v){
        v.style.animation='none'; v.style.opacity='1'; v.style.transform='none';
      });
      var r=document.getElementById('rndfrom');
      if(r) r.value='1b';
    },400);
  },150);
});
</script>
"""
with io.open(built_html(), encoding="utf-8") as f:
    page = f.read()
with io.open(TMP, "w", encoding="utf-8") as f:
    f.write(page.replace("</body>", H + "</body>"))
cmd = [CHROME, "--headless", "--disable-gpu", "--no-sandbox",
       "--window-size=1000,1000", "--hide-scrollbars",
       "--virtual-time-budget=8000",
       "--screenshot=" + SHOT,
       "--user-data-dir=" + os.path.join(BASE, "_t_profile_shot5"),
       "file:///" + TMP.replace("\\", "/")]
r = subprocess.run(cmd, capture_output=True, timeout=120)
print("exit", r.returncode, "size", os.path.getsize(SHOT) if os.path.exists(SHOT) else 0)
