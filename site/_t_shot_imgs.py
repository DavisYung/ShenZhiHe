# -*- coding: utf-8 -*-
"""截圖驗證：掛了筆記原圖的知識點卡片。"""
import io, os, subprocess, sys

sys.stdout.reconfigure(encoding="utf-8")
BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)
from _sitefile import built_html  # noqa: E402

CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
TMP = os.path.join(BASE, "_t_shot_imgs.html")
SHOT = os.path.join(BASE, "shots", "v0012_imgs.png")

H = """
<style>*{animation:none!important;transition:none!important}</style>
<script>
window.addEventListener('load',function(){
  setTimeout(function(){
    /* 找第一个挂图的知识点并跳过去 */
    var pid=null;
    TOPICS.forEach(function(t){(t.sections||[]).forEach(function(s){
      (s.points||[]).forEach(function(p){
        if(!pid && /^\\s*!\\[[^\\]]*\\]\\([^)]+\\)/.test(p.body||'')) pid=p.id;
      });
    });});
    if(pid) jumpPoint(pid); else location.hash='#/chem/t/4a';
    setTimeout(function(){
      document.querySelectorAll('.view').forEach(function(v){
        v.style.animation='none'; v.style.opacity='1'; v.style.transform='none';
      });
      window.scrollTo(0,0);
    },700);
  },150);
});
</script>
"""
with io.open(built_html(), encoding="utf-8") as f:
    page = f.read()
with io.open(TMP, "w", encoding="utf-8") as f:
    f.write(page.replace("</body>", H + "</body>"))
cmd = [CHROME, "--headless", "--disable-gpu", "--no-sandbox",
       "--window-size=1000,1300", "--hide-scrollbars",
       "--virtual-time-budget=9000",
       "--screenshot=" + SHOT,
       "--user-data-dir=" + os.path.join(BASE, "_t_profile_shot12"),
       "file:///" + TMP.replace("\\", "/")]
r = subprocess.run(cmd, capture_output=True, timeout=120)
print("exit", r.returncode, "size", os.path.getsize(SHOT) if os.path.exists(SHOT) else 0)
