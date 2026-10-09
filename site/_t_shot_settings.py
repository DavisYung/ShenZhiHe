# -*- coding: utf-8 -*-
"""同一次 Chrome 運行裡同時拿：截圖 + 計算樣式（寫進 title 再 dump-dom）。
避免『探針一次、截圖又一次』兩次運行結果互相矛盾無法對表。"""
import io, os, re, subprocess, sys

sys.stdout.reconfigure(encoding="utf-8")
BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)
from _sitefile import built_html  # noqa: E402

CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
TMP = os.path.join(BASE, "_t_shot_settings.html")
SHOT = os.path.join(BASE, "shots", "v009_settings.png")

H = """
<style>*{animation:none!important;transition:none!important}</style>
<script>
window.addEventListener('load',function(){
  setTimeout(function(){
    location.hash='#/settings';
    setTimeout(function(){
      try{ localStorage.setItem('f6chem.v1','{"ver":2}'); }catch(e){}
      bkMsg('本機有 1 項紀錄，匯出後即可遷移到新裝置','ok');
      document.querySelectorAll('.view').forEach(function(v){
        v.style.animation='none'; v.style.opacity='1'; v.style.transform='none';
      });
      var g=document.getElementById('gearbtn'), cs=getComputedStyle(g), r=g.getBoundingClientRect();
      var wrap=g.parentElement, wcs=getComputedStyle(wrap);
      var info='pos='+cs.position
        +'|gearRect='+Math.round(r.left)+','+Math.round(r.top)+','+Math.round(r.width)
        +'|hwrapPad='+wcs.paddingRight+'|hwrapPos='+wcs.position
        +'|vw='+window.innerWidth
        +'|mediaMobile='+window.matchMedia('(max-width:768px)').matches;
      document.title='PROBE|'+info;
      // 調試浮層只在帶 overlay 參數時顯示，交付截圖保持乾淨
      if(location.search.indexOf('overlay')>=0){
        var d=document.createElement('div');
        d.style.cssText='position:fixed;left:6px;top:6px;z-index:99999;background:#000;color:#0f0;font:13px monospace;padding:6px;white-space:pre';
        d.textContent=info;
        document.body.appendChild(d);
      }
    },500);
  },150);
});
</script>
"""

with io.open(built_html(), encoding="utf-8") as f:
    page = f.read()
with io.open(TMP, "w", encoding="utf-8") as f:
    f.write(page.replace("</body>", H + "</body>"))

cmd = [CHROME, "--headless", "--disable-gpu", "--no-sandbox",
       "--window-size=1000,900", "--hide-scrollbars",
       "--virtual-time-budget=8000",
       "--screenshot=" + SHOT,
       "--dump-dom",
       "--user-data-dir=" + os.path.join(BASE, "_t_profile_shot4"),
       "file:///" + TMP.replace("\\", "/")]
r = subprocess.run(cmd, capture_output=True, timeout=120)
dom = r.stdout.decode("utf-8", "replace")
m = re.search(r"<title>PROBE\|(.*?)</title>", dom, re.S)
print("PROBE:", m.group(1) if m else "NO PROBE")
print("shot:", os.path.getsize(SHOT) if os.path.exists(SHOT) else 0)
