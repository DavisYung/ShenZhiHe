# -*- coding: utf-8 -*-
"""回歸測試（二）：V0.0.15 效能與穩定性改造，用 headless Chrome --dump-dom 驗。

V1 虛擬滾動：長課題只渲染視窗+緩衝卡片，離開視口的卡片被銷毀
V2 搜索進 Web Worker：blob worker 可用、主線程匹配規則、輸入防抖；
    worker 往返用「迷你 payload」驗證（4MB 全量種子在虛擬時間下測不到）
V3 記憶體／存儲管控：超長字串截斷、store 寫入有上限、告警元素可彈出
V4 PIP 關閉後徹底銷毀內部 DOM
V5 知識圖譜節點過濾：filterCoreNodes 只留核心節點、toggle 可切換
"""
import io
import os
import re
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8")
BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)
from _sitefile import built_html  # noqa: E402

CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
TMP = os.path.join(BASE, "_t_v015.html")

HARNESS = r"""
<script>
(function(){
  var log=[];
  function out(k,v){log.push(k+'='+v);}
  function dump(){
    if(document.getElementById('RESULT'))return;
    var pre=document.createElement('pre');
    pre.id='RESULT'; pre.textContent=log.join('\n');
    document.body.appendChild(pre);
  }
  window.onerror=function(m,src,ln){ log.push('JS_ERROR='+m+' @'+ln); dump(); };
  window.addEventListener('unhandledrejection',function(e){
    log.push('PROMISE_ERROR='+(e.reason&&e.reason.message||e.reason)); dump();
  });
  setTimeout(function(){
    try{ localStorage.clear(); }catch(e){}

    /* ---- V1 虛擬滾動：2a 有 88 個知識點，應走虛擬列表 ---- */
    location.hash='#/chem/t/2a';
    setTimeout(function(){
      try{
        var vc=document.getElementById('vcontent');
        out('V1_has_vcontent', !!vc);
        var items=document.querySelectorAll('#vlist .vitem');
        out('V1_rendered_lt_total', items.length>0 && items.length<88);
        out('V1_rendered_count', items.length);
        out('V1_has_placeholder', !!document.querySelector('#vlist .vplaceholder'));
        var pts2a=Object.keys(PMAP).filter(function(p){return p.indexOf('2a-')===0;});
        var lastPid=pts2a[pts2a.length-1];
        var before=vc.scrollTop;
        /* 跳轉動畫模式：off 時直接到位（scrollTop 立即變），才能做同步斷言；
           full/simple 下平滑捲動是非同步的，改驗「目標已被渲染」即可。 */
        setAnimMode('off');
        var ok=virtJumpPoint(lastPid);
        out('V1_jump_ok', !!ok);
        out('V1_jump_moved', vc.scrollTop>before);
        out('V1_target_in_dom', !!document.getElementById('pt-'+lastPid));
        out('V1_jump_sec_ok', !!virtJumpSection((TMAP['2a'].sections||[])[0].id));
        /* 平滑模式（full）下跳轉不應報錯，且目標同樣要渲染出來 */
        setAnimMode('full');
        out('V1_jump_smooth_ok', !!virtJumpPoint(lastPid));
        out('V1_smooth_target_rendered', !!document.getElementById('pt-'+lastPid));
        setAnimMode('off');

        /* ---- V2a 搜索：blob worker 可用 + 主線程匹配規則 + 防抖 ---- */
        out('V2_worker_url', (typeof __SEARCH_WORKER_URL__==='string' && __SEARCH_WORKER_URL__.indexOf('blob:')===0)?'blob':'MISSING');
        out('V2_used', ensureSearchWorker()?'worker':'fallback');
        var loc=searchLocal('氧化還原');
        out('V2_local_has_hits', loc.total>0);
        out('V2_local_title_rank', (function(){
          /* 標題命中(100)要排在正文命中(10)前面——用合成資料驗規則 */
          var oldT=TOPICS, oldQ=QUIZ;
          TOPICS=[{id:'x',title:'X',sections:[{id:'xs',title:'S',points:[
            {id:'xp1',title:'關鍵詞在標題',body:'內容A',tags:[]},
            {id:'xp2',title:'一般標題',body:'正文提到關鍵詞',tags:[]}]}]}];
          QUIZ={};
          var r=searchLocal('關鍵詞');
          TOPICS=oldT; QUIZ=oldQ;
          return r.hits.length===2 && r.hits[0].p.id==='xp1'
              && r.hits[0].score===100 && r.hits[1].score===10;
        })());
        var inp=document.getElementById('sq');
        inp.value='H2SO4'; doSearch();
        out('V2_debounce_scheduled', SW_DEBT?1:0);
        if(SW_DEBT){ clearTimeout(SW_DEBT); SW_DEBT=null; }
        inp.value='';
      }catch(e){ out('V1_V2_STEP_ERROR', e.message); }

      /* ---- V3 記憶體／存儲管控 ---- */
      setTimeout(function(){
        try{
          var cut=truncateDeep({a:new Array(30001).join('x')});
          out('V3_truncate_deep', cut.a.length===8006);
          out('V3_truncate_keep_small', truncateDeep({a:'short'}).a==='short');
          var s=STORE.get(); s.blob=new Array(600001).join('y'); STORE.set(s);
          var raw=localStorage.getItem(storeKey())||'';
          out('V3_store_capped', raw.length<500000);
          var s2=STORE.get(); delete s2.blob; STORE.set(s2);
          showMemWarn('測試提示 <b>99%</b>', true);
          var w=document.querySelector('.memwarn.show');
          out('V3_memwarn_el', !!w);
          if(w) w.remove();
          out('V3_storage_usage_gt0', getStorageUsage()>0);
          out('V3_check_runs', (function(){try{checkMemoryAndStorage();return 1;}catch(e){return 0;}})());

          /* ---- V4 PIP 銷毀 ---- */
          var pid=Object.keys(PMAP)[0];
          openPip(pid);
          var el=document.getElementById('pip');
          out('V4_pip_open', el.classList.contains('on') && el.innerHTML.length>100);
          /* 完全關閉動畫時：立即清空內部 DOM（不殘留節點） */
          setAnimMode('off');
          closePip();
          out('V4_pip_destroyed', el.innerHTML==='' && !el.classList.contains('on'));
          /* 有動畫時：先移除 .on 播過渡，延遲才清 DOM（Safari 閃現修復）；
             這裡驗「立刻不會殘留可見狀態」＋「延遲後會清空」 */
          setAnimMode('full');
          openPip(pid);
          closePip();
          out('V4_pip_hidden_now', !el.classList.contains('on'));
          out('V4_pip_kept_for_transition', el.innerHTML.length>100);
          /* 有動畫時：延遲才清 DOM。這裡不能用 setTimeout 記錄結果——
             headless 的 --virtual-time-budget 會讓虛擬時間跑得比真實計時器快，
             回呼常常還沒執行就結束採集，導致 V4_pip_cleared_after 變成 None（假失敗）。
             改成先標記「待驗」，由外層在採集前留足時間再檢查（見 _t_pip.mjs 的獨立驗證）。 */
          window.__pipClearPending = true;
          setTimeout(function(){
            window.__pipClearPending = false;
            window.__pipCleared = (el.innerHTML==='');
            setAnimMode('off');
          }, 700);
        }catch(e){ out('V3_V4_STEP_ERROR', e.message); }

        /* ---- V5 圖譜節點過濾 ---- */
        location.hash='#/chem/graph';
        setTimeout(function(){
          try{
            out('V5_graph_rendered', document.querySelectorAll('#graphsvg .gn').length>0);
            out('V5_threshold_type', typeof GRAPH_THRESHOLD);
            var nodes=[],edges=[];
            for(var i=0;i<40;i++)nodes.push({key:'n'+i,label:'N'+i,topic:TOPICS[0],r:10,sub:'',x:0,y:0,vx:0,vy:0});
            for(var j=0;j<39;j++)edges.push({s:j,t:j+1,n:1,labels:[],ka:'a',kb:'b'});
            var f=filterCoreNodes(nodes,edges,20);
            out('V5_filtered_count', f.nodes.length===20);
            out('V5_edges_valid', f.edges.every(function(e){return e.s<20&&e.t<20;}));
            out('V5_keeps_hub', f.nodes.some(function(n){return n.key==='n19';}));
            /* 在圖譜頁切換過濾狀態（走完整 drawGraph 路徑） */
            GRAPH_ALL_NODES=nodes; GRAPH_ALL_EDGES=edges;
            GRAPH_MAX_NODES=20; GRAPH_FILTERED=false; GRAPH_IS_ALL=true;
            toggleGraphFilter();
            out('V5_toggle_rendered', document.querySelectorAll('#graphsvg .gn').length===20);
            out('V5_toggle_filtered_flag', GRAPH_FILTERED===true);
          }catch(e){ out('V5_STEP_ERROR', e.message); }

          /* ---- V2b worker 往返（迷你 payload，最後一步：結果一到就 dump）---- */
          try{
            var sw=ensureSearchWorker();
            if(!sw){ out('V2_roundtrip', 'no-worker'); dump(); return; }
            var origRender=renderSearch;
            renderSearch=function(q,hits,total){
              origRender(q,hits,total);
              out('V2_roundtrip', 'ok');
              out('V2_worker_total', total);
              out('V2_worker_hits', document.querySelectorAll('#app .sres').length);
              dump();
            };
            SW_LAST='水';
            sw.postMessage({q:'水', kw:'水', sid:'mini',
              topics:[{id:'mt',title:'迷你課題',sections:[{id:'ms',title:'章',points:[
                {id:'mp1',title:'水的組成',body:'H2O 由氫與氧組成',tags:['水']},
                {id:'mp2',title:'硫酸',body:'H2SO4 是強酸',tags:[]}]}]}],
              quiz:{mt:[{id:'mq1',q:'水的化學式？',options:['H2O','CO2'],explanation:'H2O'}]}});
            /* 若 worker 沒回，最終也會由虛擬時間收尾報錯（拿不到 RESULT） */
          }catch(e){ out('V2_ROUNDTRIP_ERROR', e.message); dump(); }
        },500);
      },400);
    },500);
  },300);
})();
</script>
"""

EXPECT = {
    "V1_has_vcontent": "true",
    "V1_rendered_lt_total": "true",
    "V1_has_placeholder": "true",
    "V1_jump_ok": "true",
    "V1_jump_moved": "true",
    "V1_target_in_dom": "true",
    "V1_jump_sec_ok": "true",
    "V1_jump_smooth_ok": "true",
    "V1_smooth_target_rendered": "true",
    "V2_worker_url": "blob",
    "V2_used": "worker",
    "V2_local_has_hits": "true",
    "V2_local_title_rank": "true",
    "V2_debounce_scheduled": "1",
    "V3_truncate_deep": "true",
    "V3_truncate_keep_small": "true",
    "V3_store_capped": "true",
    "V3_memwarn_el": "true",
    "V3_storage_usage_gt0": "true",
    "V3_check_runs": "1",
    "V4_pip_open": "true",
    "V4_pip_destroyed": "true",
    "V4_pip_hidden_now": "true",
    "V4_pip_kept_for_transition": "true",
    # 註：原本還有 "V4_pip_cleared_after"（動畫模式下延遲清空 DOM）。
    # 它靠 700ms 的 setTimeout 寫結果，但 headless 的 --virtual-time-budget
    # 會讓虛擬時間跑得比真實計時器快，回呼常常還沒跑就結束採集 →
    # 值變成 None 造成假失敗（實測站點行為正確，DOM 確實清空）。
    # 該行為改由獨立測試 _t_pip.mjs 驗證（等足 3 秒，4/4 通過）。
    "V5_graph_rendered": "true",
    "V5_threshold_type": "number",
    "V5_filtered_count": "true",
    "V5_edges_valid": "true",
    "V5_keeps_hub": "true",
    "V5_toggle_rendered": "true",
    "V5_toggle_filtered_flag": "true",
    "V2_roundtrip": "ok",
    "V2_worker_total": "2",   # 「水」命中 mp1 標題+正文與 mq1 題幹
    "V2_worker_hits": "2",
}


def main():
    with io.open(built_html(), encoding="utf-8") as f:
        page = f.read()
    with io.open(TMP, "w", encoding="utf-8") as f:
        f.write(page.replace("</body>", HARNESS + "</body>"))
    cmd = [CHROME, "--headless", "--disable-gpu", "--no-sandbox",
           "--virtual-time-budget=30000", "--dump-dom",
           "--user-data-dir=" + os.path.join(BASE, "_t_profile"),
           "file:///" + TMP.replace("\\", "/")]
    r = subprocess.run(cmd, capture_output=True, timeout=240)
    dom = r.stdout.decode("utf-8", "replace")
    m = re.search(r'<pre id="RESULT">(.*?)</pre>', dom, re.S)
    if not m:
        print("沒有拿到結果（worker 往返可能沒在虛擬時間內回來），DOM 長度 =", len(dom))
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
    print("=== V0.0.15 虛擬滾動／Worker／記憶體／圖譜 測試 ===")
    for k in EXPECT:
        print("  %-30s %s" % (k, got.get(k)))
    for k in sorted(set(got) - set(EXPECT)):
        if k.endswith("_ERROR") or k.startswith(("JS_ERROR", "PROMISE_ERROR")):
            fails.append("執行期錯誤: %s=%s" % (k, got[k]))
            print("  ! %s = %s" % (k, got[k]))
    print("\n檢查 %d 項，通過 %d 項" % (len(EXPECT), len(EXPECT) - len(fails)))
    for f in fails:
        print("  ✗", f)
    print("\n結果：", "全部通過 ✅" if not fails else "有 %d 項失敗 ❌" % len(fails))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
