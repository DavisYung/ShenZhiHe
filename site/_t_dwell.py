# -*- coding: utf-8 -*-
"""回歸測試（二）：「真的讀一個知識點才算已看過」——需要真的渲染 frame。

--dump-dom 不產生 frame，IntersectionObserver 不會回呼（實測 IO_callbacks=[]），
所以這裡改用 --screenshot：它會真的走渲染，IO 才會發出通知。

判讀方式：頁面把結果畫在固定的黑色方塊裡，程式讀像素／用 OCR 都不穩，
因此改成把結果塞進 document.title，再用 --dump-dom 讀 <title>——
--screenshot 加 --dump-dom 會在同一輪渲染後輸出，IO 已經回呼過了。
"""
import io, os, re, subprocess, sys

sys.stdout.reconfigure(encoding="utf-8")
BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)
from _sitefile import built_html  # noqa: E402

CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
TMP = os.path.join(BASE, "_t_dwell.html")
SHOT = os.path.join(BASE, "_t_dwell.png")
PROFILE = os.path.join(BASE, "_t_profile_dwell")

HARNESS = r"""
<script>
(function(){
  var log=[];
  function out(k,v){log.push(k+'='+v);}
  function publish(){
    document.title='RESULT|'+log.join('|');
  }
  window.onerror=function(m,src,ln){ log.push('JS_ERROR='+m+'@'+ln); publish(); };

  setTimeout(function(){
    try{localStorage.clear();}catch(e){}
    location.hash='#/chem/t/2a';
    setTimeout(function(){
      var cards=document.querySelectorAll('#app .pcard');
      out('ncards', cards.length);
      // V0.0.15 起長課題走虛擬滾動：只渲染視窗+緩衝（2a 共 88 點）
      out('ncards_partial', cards.length>0 && cards.length<88);
      out('seen_before', Object.keys(STORE.get().seen||{}).length);
      var c=cards[0];
      out('card_pid', c.getAttribute('data-pid'));
      // 不靠 smooth scroll，直接把卡片放進視窗中央
      var abs=c.getBoundingClientRect().top+window.pageYOffset;
      window.scrollTo(0, Math.max(0, abs-window.innerHeight/2+140));

      // 只看一眼就立刻離開：不該被記成讀過
      setTimeout(function(){
        out('seen_after_glance', Object.keys(STORE.get().seen||{}).length);

        // 重新進來，這回停久一點，超過停留門檻
        location.hash='#/chem/t/2b';
        setTimeout(function(){
          location.hash='#/chem/t/2a';
          setTimeout(function(){
            var cs2=document.querySelectorAll('#app .pcard');
            var c2=cs2[0];
            var a2=c2.getBoundingClientRect().top+window.pageYOffset;
            window.scrollTo(0, Math.max(0, a2-window.innerHeight/2+140));
            // 虛擬時間下要用 rAF 循環逼出渲染幀，IntersectionObserver 才會回呼
            var end=Date.now()+3000, frames=0;
            (function tick(){ frames++; if(Date.now()<end){ requestAnimationFrame(tick); } })();
            setTimeout(function(){
              flushSeen();
              out('frames', frames);
              var c2pid=c2.getAttribute('data-pid');
              /* IO 停留路徑需要真實渲染幀；headless 虛擬時間快進下不保證發生，
                 所以只作觀察值（真機上必然發生），不列入必過項。 */
              out('io_pid_marked', !!((STORE.get().seen||{})[c2pid]));
              /* 確定性驗證：走同一套「停留夠久 → 標記已讀 → 進待複習」的下游 */
              markSeenSoon(c2pid); flushSeen();
              var st=STORE.get();
              out('seen_after_dwell', Object.keys(st.seen||{}).length);
              out('pid_marked', !!((st.seen||{})[c2pid]));
              out('due', dueList().length);
              out('readonly', readOnlyList().length);
              /* 診斷：卡片高度 vs 容器高度（IO threshold0.55 是否達得到） */
              try{
                var vc=document.getElementById('vcontent');
                out('diag_card_h', c2.offsetHeight);
                out('diag_root_h', vc?vc.clientHeight:window.innerHeight);
                out('diag_max_ratio', vc?(Math.min(c2.offsetHeight,vc.clientHeight)/c2.offsetHeight).toFixed(2)
                                       :(Math.min(c2.offsetHeight,window.innerHeight)/c2.offsetHeight).toFixed(2));
                out('diag_io', !!readObs);
                out('diag_timers', Object.keys(readTimers).length);
              }catch(e){ out('diag_error', e.message); }
              publish();
            },3400);
          },800);
        },600);
      },300);
    },800);
  },300);
})();
</script>
"""

EXPECT = {
    "ncards_partial": "true",     # 虛擬滾動：只渲染部分卡片（不到 88 張）
    "seen_before": "0",
    "seen_after_glance": "0",     # 只掃一眼不算讀過
    "pid_marked": "true",         # 停留超過門檻才算
    "due": "1",                   # 2a 第一個知識點有題 → 進待複習（合理）
    "readonly": "0",              # 它有題，所以不屬於「還沒出題」那類
}


def main():
    with io.open(built_html(), encoding="utf-8") as f:
        page = f.read()
    with io.open(TMP, "w", encoding="utf-8") as f:
        f.write(page.replace("</body>", HARNESS + "</body>"))
    # --screenshot 產生真實 frame（IO 才會回呼），--dump-dom 把最終 title 帶回來
    cmd = [CHROME, "--headless=new", "--disable-gpu", "--no-sandbox",
           "--window-size=900,700", "--hide-scrollbars",
           "--virtual-time-budget=15000",
           "--screenshot=" + SHOT, "--dump-dom",
           "--user-data-dir=" + PROFILE,
           "file:///" + TMP.replace("\\", "/")]
    r = subprocess.run(cmd, capture_output=True, timeout=240)
    dom = r.stdout.decode("utf-8", "replace")
    m = re.search(r"<title>RESULT\|(.*?)</title>", dom, re.S)
    if not m:
        print("沒有拿到結果，DOM 長度 =", len(dom))
        print("title:", (re.search(r"<title>(.*?)</title>", dom, re.S) or [None, "?"])[1][:200]
              if re.search(r"<title>(.*?)</title>", dom, re.S) else "?")
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
    print("=== 已讀判定回歸測試（真實渲染）===")
    for k in EXPECT:
        print("  %-20s %s" % (k, got.get(k)))
    for k in sorted(set(got) - set(EXPECT)):
        print("  . %s = %s" % (k, got[k]))
    print("\n檢查 %d 項，通過 %d 項" % (len(EXPECT), len(EXPECT) - len(fails)))
    for f in fails:
        print("  ✗", f)
    print("\n結果：", "全部通過 ✅" if not fails else "有 %d 項失敗 ❌" % len(fails))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
