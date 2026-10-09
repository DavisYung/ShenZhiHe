# -*- coding: utf-8 -*-
"""回歸測試（五）：題庫擴充 + 隨機抽題。

  T1 題庫規模：1a=49 / 1b=120 / 1c=94 / 3c=89，全站 623 題，ID 全站唯一
  T2 新題 schema：point 引用全部存在於 data，無 U+FFFD，answer 合法
  T3 三個課題原本未覆蓋的 69 個知識點現在全部至少有 1 題
  T4 random 模式（headless）：抽 n 題恰好 n、無重複、全部來自源池
  T5 random 範圍：指定課題只抽該課題；錯題源只抽錯題；n 超過源長度取全部
  T6 隨機抽題 UI：rndfrom/rndn/startRandomQuiz 存在
"""
import glob, io, json, os, re, subprocess, sys

sys.stdout.reconfigure(encoding="utf-8")
ROOT = "f6chem"

def load(pid):
    return json.load(io.open("%s/data/chem/%s.json" % (ROOT, pid), encoding="utf-8"))

def quiz(tid):
    return json.load(io.open("%s/quiz/chem/%s.json" % (ROOT, tid), encoding="utf-8"))

fails = []

# ---------- T1 統計 ----------
counts = {t: len(quiz(t)["questions"]) for t in ("1a", "1b", "1c", "3c")}
expect = {"1a": 49, "1b": 120, "1c": 94, "3c": 89}
print("T1 counts:", counts)
if counts != expect:
    fails.append("T1 counts: %r" % counts)
all_ids = []
for f in glob.glob(ROOT + "/quiz/chem/*.json"):
    for q in json.load(io.open(f, encoding="utf-8"))["questions"]:
        all_ids.append(q["id"])
uniq = len(all_ids) == len(set(all_ids))
print("T1 total=%d unique=%s" % (len(all_ids), uniq))
if len(all_ids) != 623 or not uniq:
    fails.append("T1 total/unique: %d/%s" % (len(all_ids), uniq))

# ---------- T2 schema ----------
pts = set()
for f in glob.glob(ROOT + "/data/chem/*.json"):
    t = json.load(io.open(f, encoding="utf-8"))
    if not isinstance(t, dict):
        continue
    for s in t.get("sections", []):
        for p in s.get("points", []):
            pts.add(p["id"])
schema_bad = []
for f in glob.glob(ROOT + "/quiz/chem/*.json"):
    for q in json.load(io.open(f, encoding="utf-8"))["questions"]:
        if q.get("point") not in pts:
            schema_bad.append(q["id"] + ":point")
        if "\ufffd" in json.dumps(q, ensure_ascii=False):
            schema_bad.append(q["id"] + ":fffd")
        if q["type"] == "mc" and not (0 <= q.get("answer", -1) < len(q.get("options", []))):
            schema_bad.append(q["id"] + ":answer")
        if q["type"] == "tf" and not isinstance(q.get("answer"), bool):
            schema_bad.append(q["id"] + ":tfanswer")
print("T2 schema_bad:", schema_bad or "none")
if schema_bad:
    fails.append("T2 %s" % schema_bad)

# ---------- T3 覆蓋率（原 69 個未覆蓋點全數有題）----------
UNCOVERED = {
    "1a": ["1a-s1-p1","1a-s2-p2","1a-s4-p2","1a-s4-p4","1a-s5-p4","1a-s6-p3","1a-s7-p1","1a-s8-p5","1a-s9-p2"],
    "1b": ["1b-s1-p1","1b-s1-p2","1b-s1-p4","1b-s1-p5","1b-s2-p1","1b-s2-p2","1b-s2-p6","1b-s3-p3","1b-s4-p1",
           "1b-s5-p1","1b-s5-p2","1b-s5-p3","1b-s5-p6","1b-s6-p1","1b-s6-p3","1b-s6-p4","1b-s7-p2","1b-s8-p1",
           "1b-s8-p2","1b-s8-p3","1b-s9-p1","1b-s9-p4","1b-s11-p1","1b-s11-p3","1b-s12-p1","1b-s13-p1","1b-s13-p4",
           "1b-s14-p1","1b-s15-p1","1b-s15-p4","1b-s16-p1","1b-s17-p1","1b-s18-p1","1b-s18-p2"],
    "1c": ["1c-s1-p1","1c-s2-p2","1c-s2-p4","1c-s3-p3","1c-s4-p2","1c-s4-p5","1c-s4-p6","1c-s6-p1","1c-s6-p2",
           "1c-s7-p1","1c-s7-p4","1c-s8-p1","1c-s8-p2","1c-s8-p3","1c-s8-p5","1c-s8b-p1","1c-s8b-p3","1c-s9-p3",
           "1c-s10-p3","1c-s11-p2","1c-s11-p4","1c-s12-p3","1c-s13-p1","1c-s13-p3","1c-s13-p4","1c-s13-p7"],
}
missing = []
for tid, plist in UNCOVERED.items():
    covered = {q.get("point") for q in quiz(tid)["questions"]}
    missing += [p for p in plist if p not in covered]
print("T3 uncovered now missing:", missing or "none (%d checked)" % sum(len(v) for v in UNCOVERED.values()))
if missing:
    fails.append("T3 %s" % missing)

# ---------- headless: T4/T5/T6 ----------
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
sys.path.insert(0, ROOT + "/site")
from _sitefile import built_html  # noqa: E402

HARNESS = r"""
<script>
(function(){
  var log=[];
  function out(k,v){log.push(k+'='+v);}
  function publish(){ document.title='RESULT|'+log.join('|'); }
  window.onerror=function(m,s,l){ log.push('JS_ERROR='+m+'@'+l); publish(); };
  setTimeout(function(){
    try{ localStorage.clear(); }catch(e){}
    /* T6 UI 存在 */
    location.hash='#/quiz';
    setTimeout(function(){
      out('T6_select', !!document.getElementById('rndfrom'));
      out('T6_input', !!document.getElementById('rndn'));
      out('T6_btn', typeof startRandomQuiz==='function');

      /* T4 抽 12 題：恰好 12、無重複、來自源池 */
      var all=allQuestions();
      var allIds={}; all.forEach(function(q){allIds[q.id]=1;});
      startQuiz({mode:'random',from:'all',n:12});
      out('T4_n', QZ.pool.length);
      var seen={}, dup=0, foreign=0;
      QZ.pool.forEach(function(q){ if(seen[q.id])dup++; seen[q.id]=1; if(!allIds[q.id])foreign++; });
      out('T4_dup', dup);
      out('T4_foreign', foreign);
      out('T4_hash', location.hash);

      /* T5a 指定課題 1b 抽 20 題 */
      startQuiz({mode:'random',from:'1b',n:20});
      out('T5a_n', QZ.pool.length);
      out('T5a_all1b', QZ.pool.every(function(q){return q.topic==='1b';}));

      /* T5b n 超過源長度 → 取全部（1c 共 94 題，要 999） */
      startQuiz({mode:'random',from:'1c',n:999});
      out('T5b_n', QZ.pool.length);
      out('T5b_all1c', QZ.pool.every(function(q){return q.topic==='1c';}));

      /* T5c 錯題源：先造 3 個錯題 */
      var s=STORE.get(); s.wrong=all.slice(0,3).map(function(q){return q.id;}); STORE.set(s);
      startQuiz({mode:'random',from:'wrong',n:10});
      out('T5c_n', QZ.pool.length);
      out('T5c_allwrong', QZ.pool.every(function(q){return s.wrong.indexOf(q.id)>=0;}));

      /* T5d n=0/非法 → 回退預設 10 題（parseInt(0)||10，與 UI 輸入框預設一致） */
      startQuiz({mode:'random',from:'all',n:0});
      out('T5d_n', QZ.pool.length);

      /* 抽題實際可作答：答一題後狀態更新 */
      answerMc(0);
      out('T_answered', QZ.answered);
      // hashchange→route→renderSubbar 會改寫 document.title，延後 publish 等路由消化完
      setTimeout(publish,300);
      publish();
    },500);
  },300);
})();
</script>
"""

EXPECT = {
    "T6_select": "true",
    "T6_input": "true",
    "T6_btn": "true",
    "T4_n": "12",
    "T4_dup": "0",
    "T4_foreign": "0",
    "T4_hash": "#/chem/run",
    "T5a_n": "20",
    "T5a_all1b": "true",
    "T5b_n": "94",
    "T5b_all1c": "true",
    "T5c_n": "3",
    "T5c_allwrong": "true",
    "T5d_n": "10",
    "T_answered": "true",
}


def run_headless():
    page = io.open(built_html(), encoding="utf-8").read()
    tmp = os.path.abspath(os.path.join(ROOT, "site", "_t_randquiz.html"))
    io.open(tmp, "w", encoding="utf-8").write(page.replace("</body>", HARNESS + "</body>"))
    cmd = [CHROME, "--headless", "--disable-gpu", "--no-sandbox",
           "--virtual-time-budget=20000", "--dump-dom",
           "--user-data-dir=" + os.path.abspath(os.path.join(ROOT, "site", "_t_profile_rand")),
           "file:///" + tmp.replace("\\", "/")]
    r = None
    try:
        r = subprocess.run(cmd, capture_output=True, timeout=120)
    except subprocess.TimeoutExpired:
        fails.append("headless: Chrome 超時 (120s)")
        return False
    dom = r.stdout.decode("utf-8", "replace")
    tm = re.search(r"<title>(.*?)</title>", dom, re.S)
    print("actual <title> =", (tm.group(1)[:300] if tm else "NO TITLE TAG"))
    m = re.search(r"<title>RESULT\|(.*?)</title>", dom, re.S)
    if not m:
        print("headless 無結果, dom len=", len(dom))
        print("stderr:", r.stderr.decode("utf-8", "replace")[-800:])
        # 無結果 = 整段 headless 測試失敗，不可靜默通過
        fails.append("headless: 沒有拿到任何結果 (dom len=%d)" % len(dom))
        return False
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
    print("\n--- headless ---")
    for k in EXPECT:
        print("  %-18s %s" % (k, got.get(k)))
    return True


run_headless()
total_checks = len(EXPECT) + 3 + 1  # +1 為 headless 有無結果本身
print("\n檢查 %d 項，通過 %d 項" % (total_checks, total_checks - len(fails)))
for f in fails:
    print("  ✗", f)
print("\n結果：", "全部通過 ✅" if not fails else "有 %d 項失敗 ❌" % len(fails))
sys.exit(1 if fails else 0)
