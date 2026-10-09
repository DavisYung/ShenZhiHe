# -*- coding: utf-8 -*-
"""截圖驗證：複習頁在修好之後長什麼樣（有題的待複習 vs 沒題的只讀清單）。"""
import io, os, subprocess, sys

sys.stdout.reconfigure(encoding="utf-8")
BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)
from _sitefile import built_html  # noqa: E402

CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
TMP = os.path.join(BASE, "_t_shot_review.html")
SHOT = os.path.join(BASE, "shots", "fix_review.png")

H = r"""
<script>
(function(){
  setTimeout(function(){
    try{localStorage.clear();}catch(e){}
    var now=Date.now(), DAY=86400000;
    var qp=quizPoints();
    var all=Object.keys(PMAP);
    var withQ=all.filter(function(p){return qp[p];});
    var noQ=all.filter(function(p){return !qp[p];});
    var seen={},review={},attempts={};
    // 5 個有題、且已到期 → 應該出現在「該複習了」
    withQ.slice(0,5).forEach(function(p,i){
      seen[p]=now-(i+2)*DAY;
      review[p]={box:2,due:now-(i+1)*DAY,last:now-4*DAY};
      attempts[p]={r:2,n:3};
    });
    // 3 個沒題、已讀 → 應該只出現在「讀過、但還沒出題」
    noQ.slice(0,3).forEach(function(p,i){ seen[p]=now-(i+1)*DAY; });
    localStorage.setItem('f6chem.v1',JSON.stringify({
      ver:2,wrong:[],days:{},seen:seen,review:review,attempts:attempts}));
    location.hash='#/chem/review';
  },200);
})();
</script>
"""
with io.open(built_html(), encoding="utf-8") as f:
    page = f.read()
with io.open(TMP, "w", encoding="utf-8") as f:
    f.write(page.replace("</body>", H + "</body>"))
os.makedirs(os.path.dirname(SHOT), exist_ok=True)
cmd = [CHROME, "--headless", "--disable-gpu", "--no-sandbox",
       "--window-size=1000,1400", "--hide-scrollbars",
       "--virtual-time-budget=8000",
       "--screenshot=" + SHOT,
       "--user-data-dir=" + os.path.join(BASE, "_t_profile_shot2"),
       "file:///" + TMP.replace("\\", "/")]
r = subprocess.run(cmd, capture_output=True, timeout=180)
print("exit", r.returncode, "size", os.path.getsize(SHOT) if os.path.exists(SHOT) else 0)
