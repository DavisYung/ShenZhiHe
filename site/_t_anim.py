# -*- coding: utf-8 -*-
"""回歸測試：動畫三檔模式 / 時長係數 / 降級 / 按壓回饋 / 平滑捲動 / PIP 過渡。

用 headless Chrome --dump-dom 驗（無需真實 frame 的項目）。
A1 三檔模式：setAnimMode 寫入 localStorage 且 html[data-anim] 同步
A2 時長係數：setAnimK 夾在 0.5–2.0、寫入 --anim-k
A3 降級偵測：detectAnimBroken 可呼叫、ANIM_BROKEN 是布林；off 模式時 animDisabled()=true
A4 按壓樣式：CSS 內有 button:active / -webkit-tap-highlight-color / touch-action
A5 平滑捲動：smoothScrollTo 在 off 模式回傳 false（直接到位）
A6 PIP：CSS 用 visibility 過渡（非 display 切換）、dragging 有 transition:none
A7 PIP 關閉：closePip 後 .on 移除；off 模式下 innerHTML 立即清空
A8 設定頁：有 animseg 三顆按鈕、range 滑桿、note 區塊
"""
import io
import os
import re
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)
from _sitefile import built_html  # noqa: E402

CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
TMP = os.path.join(BASE, "_t_anim.html")

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
  setTimeout(function(){
    try{ localStorage.clear(); }catch(e){}
    try{
      /* A1 三檔模式 */
      setAnimMode('simple');
      out('A1_stored_simple', localStorage.getItem('f6note.anim'));
      out('A1_dom_simple', document.documentElement.getAttribute('data-anim'));
      setAnimMode('full');
      out('A1_dom_full', document.documentElement.getAttribute('data-anim'));
      setAnimMode('off');
      out('A1_dom_off', document.documentElement.getAttribute('data-anim'));
      out('A1_disabled_true', animDisabled());
      setAnimMode('bogus');
      out('A1_ignores_bogus', localStorage.getItem('f6note.anim')==='off');

      /* A2 時長係數 */
      out('A2_k_clamp_low', setAnimK(0.1)===0.5);
      out('A2_k_clamp_high', setAnimK(9)===2);
      var k=setAnimK(1.5);
      out('A2_k_set', k===1.5);
      out('A2_css_var', document.documentElement.style.getPropertyValue('--anim-k'));
      out('A2_stored', localStorage.getItem('f6note.animk'));

      /* A3 降級偵測 */
      out('A3_broken_is_bool', typeof ANIM_BROKEN==='boolean');
      out('A3_detect_callable', typeof detectAnimBroken()==='boolean');
      out('A3_modes', ANIM_MODES.join(','));

      /* A4 按壓樣式（從 stylesheet 讀） */
      var css='';
      for(var i=0;i<document.styleSheets.length;i++){
        try{
          var rs=document.styleSheets[i].cssRules||[];
          for(var j=0;j<rs.length;j++){ css+=rs[j].cssText+'\n'; }
        }catch(e){}
      }
      out('A4_has_button_active', css.indexOf('button:active')>=0);
      out('A4_has_tap_highlight', css.indexOf('-webkit-tap-highlight-color')>=0);
      out('A4_has_touch_action', css.indexOf('touch-action')>=0);
      out('A4_has_card_active', css.indexOf('.tcard:active')>=0);
      out('A4_has_anim_vars', css.indexOf('--dur-base')>=0 && css.indexOf('--anim-k')>=0);
      out('A4_off_kills_anim', css.indexOf('data-anim="off"')>=0);
      out('A4_simple_mode_css', css.indexOf('data-anim="simple"')>=0);
      out('A4_reduced_motion', css.indexOf('prefers-reduced-motion')>=0);

      /* A5 平滑捲動：off 模式要直接到位 */
      setAnimMode('off');
      out('A5_off_no_smooth', smoothScrollTo(0)===false);
      setAnimMode('full');
      out('A5_full_smooth', smoothScrollTo(0)===true || prefersReducedMotion());

      /* A6 PIP 樣式：visibility 過渡、dragging 關過渡 */
      var pipcss='';
      for(var i2=0;i2<document.styleSheets.length;i2++){
        try{
          var rs2=document.styleSheets[i2].cssRules||[];
          for(var j2=0;j2<rs2.length;j2++){ pipcss+=rs2[j2].cssText+'\n'; }
        }catch(e){}
      }
      out('A6_pip_visibility', /visibility:\s*hidden/.test(pipcss));
      out('A6_pip_no_display_toggle', pipcss.indexOf('display:flex;animation:pipin')<0);
      out('A6_pip_drag_no_transition', /\.pip\.dragging\s*\{[^}]*transition:\s*none/.test(pipcss));

      /* A7 PIP 開關 */
      var pid=Object.keys(PMAP)[0];
      setAnimMode('off');
      openPip(pid);
      var el=document.getElementById('pip');
      out('A7_open', el.classList.contains('on'));
      closePip();
      out('A7_closed', !el.classList.contains('on'));
      out('A7_off_immediate_clear', el.innerHTML==='');

      /* A8 設定頁 UI */
      setAnimMode('full');
      location.hash='#/settings';
      setTimeout(function(){
        try{
          out('A8_seg_buttons', document.querySelectorAll('#animseg button').length===3);
          out('A8_range', !!document.getElementById('animk'));
          out('A8_note', !!document.getElementById('animnote'));
          out('A8_active_marked', document.querySelectorAll('#animseg button.on').length===1);
          out('A8_kv_text', (document.getElementById('animkv')||{}).textContent||'');
          /* 點簡約看是否即時生效 */
          pickAnim('simple');
          out('A8_pick_works', document.documentElement.getAttribute('data-anim')==='simple');
        }catch(e){ out('A8_ERROR', e.message); }
        dump();
      },400);
    }catch(e){ out('STEP_ERROR', e.message); dump(); }
  },400);
})();
</script>
"""

EXPECT = {
    "A1_stored_simple": "simple",
    "A1_dom_simple": "simple",
    "A1_dom_full": "full",
    "A1_dom_off": "off",
    "A1_disabled_true": "true",
    "A1_ignores_bogus": "true",
    "A2_k_clamp_low": "true",
    "A2_k_clamp_high": "true",
    "A2_k_set": "true",
    "A2_css_var": "1.5",
    "A2_stored": "1.5",
    "A3_broken_is_bool": "true",
    "A3_detect_callable": "true",
    "A3_modes": "full,simple,off",
    "A4_has_button_active": "true",
    "A4_has_tap_highlight": "true",
    "A4_has_touch_action": "true",
    "A4_has_card_active": "true",
    "A4_has_anim_vars": "true",
    "A4_off_kills_anim": "true",
    "A4_simple_mode_css": "true",
    "A4_reduced_motion": "true",
    "A5_off_no_smooth": "true",
    "A5_full_smooth": "true",
    "A6_pip_visibility": "true",
    "A6_pip_no_display_toggle": "true",
    "A6_pip_drag_no_transition": "true",
    "A7_open": "true",
    "A7_closed": "true",
    "A7_off_immediate_clear": "true",
    "A8_seg_buttons": "true",
    "A8_range": "true",
    "A8_note": "true",
    "A8_active_marked": "true",
    "A8_pick_works": "true",
}


def main():
    with io.open(built_html(), encoding="utf-8") as f:
        page = f.read()
    with io.open(TMP, "w", encoding="utf-8") as f:
        f.write(page.replace("</body>", HARNESS + "</body>"))
    cmd = [CHROME, "--headless=new", "--disable-gpu", "--no-sandbox",
           "--virtual-time-budget=20000", "--dump-dom",
           "--user-data-dir=" + os.path.join(BASE, "_t_profile_anim"),
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
    print("=== 動畫三檔／降級／PIP 回歸測試 ===")
    for k in EXPECT:
        print("  %-28s %s" % (k, got.get(k)))
    for k in sorted(set(got) - set(EXPECT)):
        if k.endswith("_ERROR") or k.startswith("JS_ERROR"):
            fails.append("執行期錯誤: %s=%s" % (k, got[k]))
            print("  ! %s = %s" % (k, got[k]))
    print("\n檢查 %d 項，通過 %d 項" % (len(EXPECT), len(EXPECT) - len(fails)))
    for f in fails:
        print("  ✗", f)
    print("\n結果：", "全部通過 ✅" if not fails else "有 %d 項失敗 ❌" % len(fails))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
