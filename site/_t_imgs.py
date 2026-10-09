# -*- coding: utf-8 -*-
"""回歸測試（六）：筆記原圖內嵌。

  T1 構建產物：data URI >= 90 個、無殘留 ](img/ 引用、無缺圖警告
  T2 mdLite 渲染（headless）：掛圖的知識點 body 渲出 <figure class="mdfig"><img
  T3 圖片寬高：img 標籤 lazy 屬性存在；figure 有 figcaption
  T4 未掛圖的知識點照常渲染（無回退）
"""
import io, os, re, subprocess, sys

sys.stdout.reconfigure(encoding="utf-8")
BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)
from _sitefile import built_html  # noqa: E402

fails = []
page = io.open(built_html(), encoding="utf-8").read()

# ---------- T1 構建產物 ----------
n_datauri = page.count("data:image/webp;base64,")
n_ref = len(re.findall(r"\]\(img/", page))
print("T1 dataURI=%d residual_img_ref=%d size=%.1fMB" % (n_datauri, n_ref, len(page) / 1048576))
if n_datauri < 90:
    fails.append("T1 dataURI 只有 %d 個" % n_datauri)
if n_ref != 0:
    fails.append("T1 殘留 img 引用 %d 個" % n_ref)
if len(page) > 6 * 1048576:
    fails.append("T1 超過 6MB 預算: %.1fMB" % (len(page) / 1048576))

# ---------- headless: T2/T3/T4 ----------
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
HARNESS = r"""
<script>
(function(){
  var log=[];
  function out(k,v){log.push(k+'='+v);}
  function publish(){ document.title='RESULT|'+log.join('|'); }
  window.onerror=function(m,s,l){ log.push('JS_ERROR='+m+'@'+l); publish(); };
  setTimeout(function(){
    try{ localStorage.clear(); }catch(e){}
    /* 找一个挂了图的知识点（body 首行是 ![...]） */
    var imgPid=null;
    TOPICS.forEach(function(t){(t.sections||[]).forEach(function(s){
      (s.points||[]).forEach(function(p){
        if(!imgPid && /^\s*!\[[^\]]*\]\([^)]+\)/.test(p.body||'')) imgPid=p.id;
      });
    });});
    out('imgPid', imgPid||'none');
    if(imgPid){
      jumpPoint(imgPid);
      setTimeout(function(){
        var fig=document.querySelector('#app figure.mdfig');
        out('figure', !!fig);
        var img=fig&&fig.querySelector('img');
        out('img_src_datauri', !!(img&&img.src.indexOf('data:image/webp;base64,')===0));
        out('img_lazy', !!(img&&img.getAttribute('loading')==='lazy'));
        out('figcaption', !!(fig&&fig.querySelector('figcaption')));
        out('img_natural_w', img?img.naturalWidth:0);
        /* T4: 沒掛圖的點照常渲染 */
        var plainPid=null;
        TOPICS.forEach(function(t){(t.sections||[]).forEach(function(s){
          (s.points||[]).forEach(function(p){
            if(!plainPid && !/\!\[[^\]]*\]\([^)]+\)/.test(p.body||'')) plainPid=p.id;
          });
        });});
        if(plainPid){
          jumpPoint(plainPid);
          setTimeout(function(){
            var card=document.getElementById('pt-'+plainPid);
            out('plain_renders', !!(card&&card.querySelector('.md')));
            out('plain_no_fig', !(card&&card.querySelector('figure.mdfig')));
            publish();
          },400);
        } else publish();
      },600);
    } else publish();
  },400);
})();
</script>
"""

EXPECT = {
    "figure": "true",
    "img_src_datauri": "true",
    "img_lazy": "true",
    "figcaption": "true",
    "plain_renders": "true",
    "plain_no_fig": "true",
}


def run_headless():
    tmp = os.path.abspath(os.path.join(BASE, "_t_imgs.html"))
    io.open(tmp, "w", encoding="utf-8").write(page.replace("</body>", HARNESS + "</body>"))
    cmd = [CHROME, "--headless", "--disable-gpu", "--no-sandbox",
           "--virtual-time-budget=20000", "--dump-dom",
           "--user-data-dir=" + os.path.abspath(os.path.join(BASE, "_t_profile_imgs")),
           "file:///" + tmp.replace("\\", "/")]
    try:
        r = subprocess.run(cmd, capture_output=True, timeout=120)
    except subprocess.TimeoutExpired:
        fails.append("headless 超時")
        return
    dom = r.stdout.decode("utf-8", "replace")
    m = re.search(r"<title>RESULT\|(.*?)</title>", dom, re.S)
    if not m:
        print("actual title:", (re.search(r"<title>(.*?)</title>", dom, re.S) or ["", "?"])[1][:200])
        fails.append("headless 無結果 (len=%d)" % len(dom))
        return
    txt = (m.group(1).replace("&gt;", ">").replace("&lt;", "<")
           .replace("&amp;", "&").replace("&quot;", '"'))
    got = {}
    for part in txt.split("|"):
        if "=" in part:
            k, v = part.split("=", 1)
            got[k.strip()] = v.strip()
    for k, v in EXPECT.items():
        if got.get(k) != v:
            fails.append("%s: 期待 %r 實際 %r" % (k, v, got.get(k)))
    print("--- headless ---")
    for k in ["imgPid"] + list(EXPECT):
        print("  %-18s %s" % (k, got.get(k)))


run_headless()
print("\n檢查 %d 項，通過 %d 項" % (len(EXPECT) + 3, len(EXPECT) + 3 - len(fails)))
for f in fails:
    print("  ✗", f)
print("\n結果：", "全部通過 ✅" if not fails else "有 %d 項失敗 ❌" % len(fails))
sys.exit(1 if fails else 0)
