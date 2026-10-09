# -*- coding: utf-8 -*-
"""回歸測試（三）：資料管理——匯出備份 / 匯入備份 / 刪除本機紀錄。

headless Chrome 實測：
  T1 站點鍵盤點：只抓 f6note.* / f6chem*，不碰其他來源的 localStorage 鍵
  T2 backupPayload 帶 app/version/exportedAt/data 四欄，資料完整
  T3 parseBackup 驗證：合法備份→回 keys；垃圾/他人資料→null（不誤收）
  T4 匯入流程：寫回鍵值 + 觸發重新載入（confirm 拦截，不真重載）
  T5 刪除流程：本站鍵全清、他人鍵保留
"""
import io, os, re, subprocess, sys

sys.stdout.reconfigure(encoding="utf-8")
BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)
from _sitefile import built_html  # noqa: E402

CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
TMP = os.path.join(BASE, "_t_backup.html")

HARNESS = r"""
<script>
(function(){
  var log=[];
  function out(k,v){log.push(k+'='+v);}
  function publish(){ document.title='RESULT|'+log.join('|'); }
  window.onerror=function(m,src,ln){ log.push('JS_ERROR='+m+'@'+ln); publish(); };

  setTimeout(function(){
    try{ localStorage.clear(); }catch(e){}

    /* 模擬：本站三鍵 + 一個別站的鍵 */
    localStorage.setItem('f6chem.v1','{"ver":2,"seen":{"1a-s1-p1":123}}');
    localStorage.setItem('f6note.subject','chem');
    localStorage.setItem('f6note.pip.pos','{"left":10,"top":20}');
    localStorage.setItem('otherapp.cart','{"x":1}');

    /* T1 站點鍵盤點 */
    var keys=siteDataKeys().slice().sort();
    out('T1_keys', JSON.stringify(keys));
    out('T1_excludes_other', keys.indexOf('otherapp.cart')<0);

    /* T2 匯出 payload */
    var p=backupPayload();
    out('T2_fields', [!!p.app,!!p.version,!!p.exportedAt,!!p.data].join(','));
    out('T2_data_n', Object.keys(p.data).length);
    out('T2_roundtrip', p.data['f6chem.v1']==='{"ver":2,"seen":{"1a-s1-p1":123}}');

    /* T3 parseBackup 驗證 */
    var good=parseBackup(JSON.stringify(p));
    out('T3_valid_ok', !!good && good.keys.length===3);
    out('T3_garbage_null', parseBackup('not json at all')===null);
    out('T3_foreign_null', parseBackup(JSON.stringify({data:{'otherapp.cart':'{}'}}))===null);
    out('T3_emptyobj_null', parseBackup('{}')===null);
    var bare=parseBackup(JSON.stringify({'f6note.subject':'phys'}));
    out('T3_bare_ok', !!bare && bare.keys.length===1);

    /* T4 匯入核心：改一鍵 + 新鍵（applyBackup 純邏輯，不含 confirm/重載） */
    var before=localStorage.getItem('f6note.subject');
    var inc=parseBackup(JSON.stringify({data:{'f6note.subject':'phys','f6note.phys.v1':'{"ver":2}'}}));
    var n=applyBackup(inc);
    out('T4_apply_n', n===2 ? '2' : ('?'+n));
    out('T4_overwritten', before==='chem' && localStorage.getItem('f6note.subject')==='phys');
    out('T4_added', localStorage.getItem('f6note.phys.v1')==='{"ver":2}');

    /* T5 刪除核心：本站鍵全清、他人鍵保留（core 不觸發 reload，測試可安全收尾） */
    var removed=clearSiteDataCore();
    out('T5_removed_n', removed===4 ? '4' : ('?'+removed));
    out('T5_ours_gone', localStorage.getItem('f6chem.v1')===null && localStorage.getItem('f6note.subject')===null);
    out('T5_other_kept', localStorage.getItem('otherapp.cart')==='{"x":1}');

    publish();
  },300);
})();
</script>
"""

EXPECT = {
    "T1_keys": '["f6chem.v1","f6note.pip.pos","f6note.subject"]',
    "T1_excludes_other": "true",
    "T2_fields": "true,true,true,true",
    "T2_data_n": "3",
    "T2_roundtrip": "true",
    "T3_valid_ok": "true",
    "T3_garbage_null": "true",
    "T3_foreign_null": "true",
    "T3_emptyobj_null": "true",
    "T3_bare_ok": "true",
    "T4_apply_n": "2",
    "T4_overwritten": "true",
    "T4_added": "true",
    "T5_removed_n": "4",
    "T5_ours_gone": "true",
    "T5_other_kept": "true",
}


def main():
    with io.open(built_html(), encoding="utf-8") as f:
        page = f.read()
    with io.open(TMP, "w", encoding="utf-8") as f:
        f.write(page.replace("</body>", HARNESS + "</body>"))
    cmd = [CHROME, "--headless", "--disable-gpu", "--no-sandbox",
           "--virtual-time-budget=15000", "--dump-dom",
           "--user-data-dir=" + os.path.join(BASE, "_t_profile_bk"),
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
    print("=== 資料管理回歸測試 ===")
    for k in EXPECT:
        print("  %-22s %s" % (k, got.get(k)))
    print("\n檢查 %d 項，通過 %d 項" % (len(EXPECT), len(EXPECT) - len(fails)))
    for f in fails:
        print("  ✗", f)
    print("\n結果：", "全部通過 ✅" if not fails else "有 %d 項失敗 ❌" % len(fails))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
