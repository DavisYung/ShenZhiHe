# -*- coding: utf-8 -*-
"""回歸測試（四）：設定分區——右上角齒輪 + #/settings 路由 + 面板遷移。

  T1 header 右上角有齒輪按鈕（gearbtn），且在 nav 之後（DOM 順序最右）
  T2 normalizeHash('#/settings') 不會被補科目前綴（仍是 #/settings）
  T3 #/settings 路由進設定頁：有「設定」標題、三個資料管理按鈕、bkmsg
  T4 齒輪在設定頁高亮（.on），在首頁不高亮
  T5 科目總覽頁已不含資料管理面板（遷移後不重複），但留了指引
"""
import io, os, re, subprocess, sys

sys.stdout.reconfigure(encoding="utf-8")
BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)
from _sitefile import built_html  # noqa: E402

CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
TMP = os.path.join(BASE, "_t_settings.html")

HARNESS = r"""
<script>
(function(){
  var log=[];
  function out(k,v){log.push(k+'='+v);}
  function publish(){ document.title='RESULT|'+log.join('|'); }
  window.onerror=function(m,src,ln){ log.push('JS_ERROR='+m+'@'+ln); publish(); };

  setTimeout(function(){
    try{ localStorage.clear(); }catch(e){}

    /* T1 齒輪在 header、且 DOM 順序在 nav 之後（視覺最右） */
    var gear=document.getElementById('gearbtn');
    out('T1_gear_exists', !!gear);
    var nav=document.getElementById('nav');
    out('T1_gear_after_nav', !!(gear&&nav&&(gear.compareDocumentPosition(nav)&Node.DOCUMENT_POSITION_PRECEDING)));
    out('T1_gear_title', gear?gear.getAttribute('title'):'');

    /* T2 normalizeHash 不補前綴 */
    out('T2_hash', normalizeHash('#/settings'));
    out('T2_subjects_still_ok', normalizeHash('#/subjects'));

    /* T3 進設定頁 */
    location.hash='#/settings';
    setTimeout(function(){
      var body=document.getElementById('app').textContent;
      out('T3_is_settings', body.indexOf('設定')>=0);
      out('T3_export_btn', body.indexOf('匯出備份')>=0);
      out('T3_import_btn', body.indexOf('匯入備份')>=0);
      out('T3_clear_btn', body.indexOf('刪除本機紀錄')>=0);
      out('T3_bkmsg', !!document.getElementById('bkmsg'));
      out('T3_bkn', !!document.getElementById('bkn'));

      /* T4 齒輪高亮 */
      out('T4_gear_on', gear.classList.contains('on'));
      location.hash='#/home';
      setTimeout(function(){
        out('T4_gear_off_home', !gear.classList.contains('on'));
        /* T5 科目頁：面板已遷走、指引還在 */
        location.hash='#/subjects';
        setTimeout(function(){
          var sb=document.getElementById('app').innerHTML;
          out('T5_no_databox', sb.indexOf('id="bkmsg"')<0);
          out('T5_hint_kept', sb.indexOf('設定')>=0);
          publish();
        },350);
      },350);
    },400);
  },300);
})();
</script>
"""

EXPECT = {
    "T1_gear_exists": "true",
    "T1_gear_after_nav": "true",
    "T1_gear_title": "設定",
    "T2_hash": "#/settings",
    "T2_subjects_still_ok": "#/subjects",
    "T3_is_settings": "true",
    "T3_export_btn": "true",
    "T3_import_btn": "true",
    "T3_clear_btn": "true",
    "T3_bkmsg": "true",
    "T3_bkn": "true",
    "T4_gear_on": "true",
    "T4_gear_off_home": "true",
    "T5_no_databox": "true",
    "T5_hint_kept": "true",
}


def main():
    with io.open(built_html(), encoding="utf-8") as f:
        page = f.read()
    with io.open(TMP, "w", encoding="utf-8") as f:
        f.write(page.replace("</body>", HARNESS + "</body>"))
    cmd = [CHROME, "--headless", "--disable-gpu", "--no-sandbox",
           "--virtual-time-budget=20000", "--dump-dom",
           "--user-data-dir=" + os.path.join(BASE, "_t_profile_set"),
           "file:///" + TMP.replace("\\", "/")]
    r = subprocess.run(cmd, capture_output=True, timeout=180)
    dom = r.stdout.decode("utf-8", "replace")
    m = re.search(r"<title>RESULT\|(.*?)</title>", dom, re.S)
    if not m:
        print("沒有拿到結果，DOM 長度 =", len(dom))
        print(r.stderr.decode("utf-8", "replace")[-1200:])
        return 1
    txt = (m.group(1).replace("&gt;", ">").replace("&lt;", "<")
           .replace("&amp;", "&").replace("&quot;", '"'))
    got = {}
    for part in txt.split("|"):
        if "=" in part:
            k, v = part.split("=", 1)
            got[k.strip()] = v.strip()
    fails = []
    for k, v in EXPECT.items():
        if got.get(k) != v:
            fails.append("%s: 期待 %r，實際 %r" % (k, v, got.get(k)))
    print("=== 設定分區回歸測試 ===")
    for k in EXPECT:
        print("  %-22s %s" % (k, got.get(k)))
    print("\n檢查 %d 項，通過 %d 項" % (len(EXPECT), len(EXPECT) - len(fails)))
    for f in fails:
        print("  ✗", f)
    print("\n結果：", "全部通過 ✅" if not fails else "有 %d 項失敗 ❌" % len(fails))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
