# -*- coding: utf-8 -*-
"""截圖驗證：科目總覽頁的「資料管理」面板（含已填入的訊息）。"""
import io, os, subprocess, sys

sys.stdout.reconfigure(encoding="utf-8")
BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)
from _sitefile import built_html  # noqa: E402

CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
TMP = os.path.join(BASE, "_t_shot_backup.html")
SHOT = os.path.join(BASE, "shots", "v008_databox.png")

H = """
<style>*{animation:none!important;transition:none!important}</style>
<script>
window.addEventListener('load',function(){
  setTimeout(function(){
    location.hash='#/subjects';
    setTimeout(function(){
      // 模擬匯出成功後的提示，驗證訊息樣式
      try{ localStorage.setItem('f6chem.v1','{"ver":2}'); }catch(e){}
      bkMsg('已匯出 3 項紀錄 ✓（在瀏覽器的下載資料夾）','ok');
      window.scrollTo(0, document.body.scrollHeight);
      // 虛擬時間下 CSS 動畫不推進，會截在淡入首帧——直接釘死最終態
      document.querySelectorAll('.view').forEach(function(v){
        v.style.animation='none'; v.style.opacity='1'; v.style.transform='none';
      });
    },400);
  },150);
});
</script>
"""
with io.open(built_html(), encoding="utf-8") as f:
    page = f.read()
with io.open(TMP, "w", encoding="utf-8") as f:
    f.write(page.replace("</body>", H + "</body>"))
os.makedirs(os.path.dirname(SHOT), exist_ok=True)
cmd = [CHROME, "--headless", "--disable-gpu", "--no-sandbox",
       "--window-size=1000,1400", "--hide-scrollbars",
       "--force-prefers-reduced-motion",
       "--virtual-time-budget=8000",
       "--screenshot=" + SHOT,
       "--user-data-dir=" + os.path.join(BASE, "_t_profile_shot3"),
       "file:///" + TMP.replace("\\", "/")]
r = subprocess.run(cmd, capture_output=True, timeout=120)
print("exit", r.returncode, "size", os.path.getsize(SHOT) if os.path.exists(SHOT) else 0)
