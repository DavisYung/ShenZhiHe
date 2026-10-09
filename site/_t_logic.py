# -*- coding: utf-8 -*-
"""回歸測試（一）：純邏輯，用 headless Chrome --dump-dom 驗。

涵蓋 4 件事：
  T1 打開課題頁（什麼都不點）不該產生任何待複習
  T3 沒出題的知識點不進「待複習」；有出題的才進
  T4 舊的髒資料（v1 留下的整頁 seen）載入時會被清理
  T5 三科各自獨立，切科目不互相汙染

「真的讀一個知識點才算已看過」需要真的渲染 frame，由 _t_read_dwell.py 用
截圖驗（--dump-dom 不產生 frame，IntersectionObserver 不會回呼）。
"""
import io, os, re, subprocess, sys

sys.stdout.reconfigure(encoding="utf-8")
BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)
from _sitefile import built_html  # noqa: E402

CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
TMP = os.path.join(BASE, "_t_logic.html")

HARNESS = r"""
<script>
(function(){
  var log=[];
  function out(k,v){log.push(k+'='+v);}
  function dump(){
    var pre=document.createElement('pre');
    pre.id='RESULT'; pre.textContent=log.join('\n');
    document.body.appendChild(pre);
  }
  window.onerror=function(m,src,ln){ log.push('JS_ERROR='+m+' @'+ln); dump(); };
  function step(fn,next){
    try{ fn(); }catch(e){ log.push('STEP_ERROR='+e.message); dump(); return; }
    if(next)setTimeout(next,400);
  }
  function pids(prefix){
    return Object.keys(PMAP).filter(function(p){return p.indexOf(prefix)===0;});
  }
  setTimeout(function(){
    try{ localStorage.clear(); }catch(e){}

    /* T1：打開課題頁，不點任何東西 */
    location.hash='#/chem/t/2a';
    setTimeout(function(){
      var st=STORE.get();
      out('T1_seen_after_open_2a', Object.keys(st.seen||{}).length);
      out('T1_due_after_open_2a', dueList().length);
      updateNavBadge();
      out('T1_badge_after_open_2a', document.getElementById('rbadge').textContent);

      /* T1b：連開三課也不該有任何待複習 */
      location.hash='#/chem/t/1b';
      setTimeout(function(){
        location.hash='#/chem/t/2b';
        setTimeout(function(){
          out('T1b_seen_after_open_3_topics', Object.keys(STORE.get().seen||{}).length);
          out('T1b_due_after_open_3_topics', dueList().length);

          /* T3：due / readOnly 的分類是否正確 */
          var qp=quizPoints();
          // 手動塞幾個「已看過」：一個有題、一個沒題
          var s=STORE.get(); s.seen=s.seen||{};
          var withQuiz=Object.keys(qp)[0];
          var noQuiz=Object.keys(PMAP).filter(function(p){return !qp[p];})[0];
          s.seen[withQuiz]=Date.now(); s.seen[noQuiz]=Date.now();
          STORE.set(s);
          var d=dueList(), ro=readOnlyList();
          out('T3_due_count', d.length);
          out('T3_due_all_with_quiz', d.every(function(x){return !!qp[x.pid];}));
          out('T3_withquiz_in_due', d.some(function(x){return x.pid===withQuiz;}));
          out('T3_noquiz_not_in_due', !d.some(function(x){return x.pid===noQuiz;}));
          out('T3_noquiz_in_readonly', ro.indexOf(noQuiz)>=0);
          out('T3_readonly_all_quizless', ro.every(function(p){return !qp[p];}));
          out('T3_count_matches_dueCountFor', d.length===dueCountFor('chem'));

          /* T4：髒資料清理 */
          var dirty={ver:1,wrong:[],days:{},seen:{},review:{},attempts:{}};
          pids('1c').forEach(function(p){ dirty.seen[p]=Date.now(); });
          dirty.attempts[pids('1c')[0]]={r:1,n:2};
          dirty.review[pids('1c')[1]]={box:1,due:Date.now()+86400000,last:Date.now()};
          localStorage.setItem('f6chem.v1',JSON.stringify(dirty));
          useSubject('chem');
          var st4=STORE.get();
          out('T4_ver_after_migrate', st4.ver);
          out('T4_seen_kept_only_real', Object.keys(st4.seen||{}).length);
          out('T4_kept_attempt_pid', !!((st4.seen||{})[pids('1c')[0]]));
          out('T4_kept_review_pid', !!((st4.seen||{})[pids('1c')[1]]));
          out('T4_due_after_migrate', dueList().length);

          /* T5：科目獨立 */
          out('T5_phys_key', storeKey('phys'));
          out('T5_phys_store', JSON.stringify(STORE.get('phys')));
          out('T5_chem_key', storeKey('chem'));
          dump();
        },400);
      },400);
    },400);
  },300);
})();
</script>
"""

EXPECT = {
    "T1_seen_after_open_2a": "0",
    "T1_due_after_open_2a": "0",
    "T1_badge_after_open_2a": "0",
    "T1b_seen_after_open_3_topics": "0",
    "T1b_due_after_open_3_topics": "0",
    "T3_due_count": "1",
    "T3_due_all_with_quiz": "true",
    "T3_withquiz_in_due": "true",
    "T3_noquiz_not_in_due": "true",
    "T3_noquiz_in_readonly": "true",
    "T3_readonly_all_quizless": "true",
    "T3_count_matches_dueCountFor": "true",
    "T4_ver_after_migrate": "2",
    "T4_seen_kept_only_real": "2",
    "T4_kept_attempt_pid": "true",
    "T4_kept_review_pid": "true",
    "T4_due_after_migrate": "0",
    "T5_phys_key": "f6note.phys.v1",
    "T5_phys_store": "{}",
    "T5_chem_key": "f6chem.v1",
}


def main():
    with io.open(built_html(), encoding="utf-8") as f:
        page = f.read()
    with io.open(TMP, "w", encoding="utf-8") as f:
        f.write(page.replace("</body>", HARNESS + "</body>"))
    cmd = [CHROME, "--headless", "--disable-gpu", "--no-sandbox",
           "--virtual-time-budget=20000", "--dump-dom",
           "--user-data-dir=" + os.path.join(BASE, "_t_profile"),
           "file:///" + TMP.replace("\\", "/")]
    r = subprocess.run(cmd, capture_output=True, timeout=240)
    dom = r.stdout.decode("utf-8", "replace")
    m = re.search(r'<pre id="RESULT">(.*?)</pre>', dom, re.S)
    if not m:
        print("沒有拿到結果，DOM 長度 =", len(dom))
        print(r.stderr.decode("utf-8", "replace")[-1500:])
        return 1
    txt = (m.group(1).replace("&gt;", ">").replace("&lt;", "<")
           .replace("&amp;", "&").replace("&quot;", '"'))
    got = {}
    for line in txt.splitlines():
        if "=" in line:
            k, v = line.split("=", 1)
            got[k.strip()] = v.strip()
    fails = []
    for k, v in EXPECT.items():
        if got.get(k) != v:
            fails.append("%s: 期待 %r，實際 %r" % (k, v, got.get(k)))
    print("=== 複習邏輯回歸測試 ===")
    for k in EXPECT:
        print("  %-34s %s" % (k, got.get(k)))
    print("\n檢查 %d 項，通過 %d 項" % (len(EXPECT), len(EXPECT) - len(fails)))
    for f in fails:
        print("  ✗", f)
    print("\n結果：", "全部通過 ✅" if not fails else "有 %d 項失敗 ❌" % len(fails))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
