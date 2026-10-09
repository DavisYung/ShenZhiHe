# -*- coding: utf-8 -*-
"""生成引導頁 index.html：列出電腦所有可用網址，並自動探測到手機能否連上。

iOS 的「文件」App 不支援 .html（沒有「用瀏覽器打開」按鈕），
所以唯一可靠途徑是讓手機用 Safari 開 http://網址。
引導頁會即時 ping 各網址，顯示哪個通、哪個不通。
"""
import io, json, os, socket, sys
sys.stdout.reconfigure(encoding="utf-8")

SITE = os.path.dirname(os.path.abspath(__file__))
PORT = sys.argv[1] if len(sys.argv) > 1 else "8899"

# 站名與版號（改版只動 version.json）
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _sitefile import site_meta, stable_html, versioned_html  # noqa: E402
META = site_meta()
SITE_NAME = META["name"]
SITE_VER = META["version"]
SITE_TITLE = "%s %s" % (SITE_NAME, SITE_VER)

# 主站（穩定檔名優先；沒有就退回帶版號的主檔）
_html_name = os.path.basename(stable_html())


def lan_ips():
    """取得所有 IPv4，並標出哪些是私有網段（家/校園 WiFi 常見）。"""
    ips, seen = [], set()
    try:
        import subprocess
        out = subprocess.run(["ipconfig"], capture_output=True, timeout=15).stdout.decode("gbk", "replace")
    except Exception:
        out = ""
    cur = []
    for line in out.splitlines():
        if "adapter" in line:
            cur = [line.strip()]
        m = line.strip()
        if m.startswith("IPv4 Address"):
            parts = m.split(":", 1)
            if len(parts) == 2:
                raw = parts[1].strip().split("%")[0].strip()
                ip = raw if not raw.startswith("169.254") else None
                if ip and ip not in seen:
                    seen.add(ip)
                    ips.append({"ip": ip, "adapter": cur[0] if cur else "", "line": m})
    return ips


def classify(ip, adapter=""):
    a = adapter.lower()
    # 先看網卡名稱：虛擬網卡要排除，否則 172.28.x（ZeroTier）會被誤判成家用 WiFi
    if any(k in a for k in ("zerotier", "radmin", "vpn", "tap", "tun", "virtual", "loopback")):
        return "vpn", "虛擬網卡（非 WiFi）"
    if "wi-fi" in a or "wireless" in a or "無線" in a or "无线" in a:
        return "home", "WiFi ✅ 就是這個"
    if "ethernet" in a or "以太" in a:
        return "wired", "有線網路"

    p = [int(x) for x in ip.split(".")[:4]]
    if p[0] == 192 and p[1] == 168:
        return "home", "家用 WiFi ✅"
    if p[0] == 10:
        return "home", "家用 WiFi ✅"
    if p[0] == 172 and 16 <= p[1] <= 31:
        return "home", "家用 WiFi ✅"
    if 128 <= p[0] <= 191:
        return "campus", "校園網"
    return "other", "其他"


HTML = """<!doctype html>
<html lang="zh-Hant">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{ST} · 開啟方式</title>
<style>
 *{box-sizing:border-box}
 html,body{margin:0;padding:0;width:100%;max-width:100%;overflow-x:hidden}
 body{background:linear-gradient(160deg,#0f766e,#134e4a 55%,#0b3d38);color:#fff;
      font-family:"PingFang TC","Microsoft JhengHei",system-ui,sans-serif;padding:18px 14px 40px}
 .wrap{max-width:520px;margin:0 auto}
 h1{font-size:22px;margin:0 0 4px;text-align:center}
 .sub{text-align:center;opacity:.82;font-size:13.5px;margin:0 0 20px}
 .card{background:rgba(255,255,255,.09);border:1px solid rgba(255,255,255,.16);
       border-radius:18px;padding:18px 16px;margin-bottom:14px}
 .ct{font-size:14px;font-weight:700;margin:0 0 10px;opacity:.95}
 a.url{display:flex;align-items:center;justify-content:space-between;gap:10px;
       background:#fff;color:#0f766e;text-decoration:none;border-radius:13px;
       padding:14px 15px;margin-bottom:9px;font-weight:700;font-size:16px;
       touch-action:manipulation;-webkit-tap-highlight-color:transparent}
 a.url:active{transform:scale(.985)}
 a.url .tag{font-size:11.5px;font-weight:600;background:#e6f3f1;color:#0f766e;
            border-radius:999px;padding:3px 9px;white-space:nowrap}
 a.url.dim{opacity:.5}
 .st{font-size:12px;margin:-5px 0 12px;padding-left:3px;opacity:.8}
 .st.ok{color:#bbf7d0}
 .st.bad{color:#fecaca}
 .st.wait{color:#fde68a}
 .note{font-size:13px;line-height:1.85;opacity:.85}
 .note b{color:#fde68a}
 .steps{counter-reset:s;margin:10px 0 0;padding:0;list-style:none}
 .steps li{counter-increment:s;margin:7px 0;font-size:13.5px;line-height:1.7;padding-left:26px;position:relative}
 .steps li:before{content:counter(s);position:absolute;left:0;top:1px;width:19px;height:19px;
   background:rgba(255,255,255,.2);border-radius:50%;text-align:center;line-height:19px;font-size:11.5px}
 .why{font-size:12.5px;opacity:.72;margin-top:12px;line-height:1.75;border-top:1px dashed rgba(255,255,255,.2);padding-top:12px}
</style>
</head>
<body>
<div class="wrap">
  <h1>🧪 {ST}</h1>
  <p class="sub">化學 __SUBSTATS__</p>

  <div class="card">
    <p class="ct">👆 點下面能通的網址（已自動幫你測試）</p>
    <div id="list"></div>
  </div>

  <div class="card">
    <p class="ct">📱 變成 App 的樣子</p>
    <ol class="steps">
      <li>用手機<b>瀏覽器</b>（Safari／Chrome）打開上面的網址</li>
      <li>點瀏覽器的<b>分享</b>按鈕（Safari 是方框向上箭頭 □↑）</li>
      <li>選「<b>添加到主屏幕</b>」／「<b>加到主畫面</b>」</li>
      <li>桌面會出現圖示，以後點它就能直接開</li>
    </ol>
    <div class="why">
      為什麼不能直接點 HTML 檔？<br>
      iPhone 的「檔案」App <b>不支援 .html</b>，只會當普通檔案預覽，
      不會跳出「用瀏覽器打開」的按鈕。所以必須給它一個 http 網址。
    </div>
  </div>
</div>

<script>
var TARGET = "__TARGET__";
var PORT = "__PORT__";
var CANDIDATES = __CANDIDATES__;

var list = document.getElementById('list');
list.innerHTML = CANDIDATES.map(function(c,i){
  return '<a class="url" id="u'+i+'" href="http://'+c.ip+':'+PORT+'/'+TARGET+'">'+
         '<span>http://'+c.ip+':'+PORT+'/</span>'+
         '<span class="tag">'+c.kindLabel+'</span></a>'+
         '<div class="st wait" id="s'+i+'">測試中…</div>';
}).join('');

// 逐一探測：能載入並拿到本站頁面才算通
CANDIDATES.forEach(function(c,i){
  var url='http://'+c.ip+':'+PORT+'/index.html?t='+Date.now();
  var done=false;
  function ok(){ if(done)return; done=true;
    var el=document.getElementById('s'+i);
    el.className='st ok'; el.textContent='✅ 這個可以用！點上面的連結';
  }
  function bad(){ if(done)return; done=true;
    var el=document.getElementById('s'+i);
    el.className='st bad';
    el.textContent='❌ 連不上（這個網址不適合你的手機，或電腦沒開著這個服務）';
  }
  setTimeout(bad, 4000);
  var img=new Image();
  img.onload=ok; img.onerror=bad; img.src=url+'&px='+i;
});
</script>
</body>
</html>
"""


def main():
    cands = []
    for info in lan_ips():
        adapter = info["adapter"]
        # 去掉編碼亂碼的網卡名前綴，只留可辨識部分
        kind, label = classify(info["ip"], adapter)
        cands.append({
            "ip": info["ip"],
            "kind": kind,
            "kindLabel": label,
            "adapter": adapter,
        })
    # 排序：WiFi → 有線 → 校園網 → 虛擬網卡
    order = {"home": 0, "wired": 1, "campus": 2, "vpn": 3, "other": 4}
    cands.sort(key=lambda c: (order.get(c.get("kind"), 9), c["ip"]))
    if not cands:
        cands = [{"ip": "127.0.0.1", "kind": "other",
                  "kindLabel": "本機", "adapter": ""}]

    from urllib.parse import quote
    # 副標題統計從資料檔實時算，課題增減後不用再手改
    base = os.path.dirname(SITE)
    subj = {}
    sp = os.path.join(base, "data", "chem", "subject.json")
    if os.path.exists(sp):
        with io.open(sp, encoding="utf-8") as f:
            subj = json.load(f)
    topics = subj.get("topics") or []
    n_pts = n_q = 0
    for tid in topics:
        tp = os.path.join(base, "data", "chem", tid + ".json")
        if os.path.exists(tp):
            with io.open(tp, encoding="utf-8") as f:
                n_pts += sum(len(s.get("points", [])) for s in json.load(f).get("sections", []))
        qp = os.path.join(base, "quiz", "chem", tid + ".json")
        if os.path.exists(qp):
            with io.open(qp, encoding="utf-8") as f:
                n_q += len(json.load(f).get("questions", []))
    lp = os.path.join(base, "data", "chem", "links.json")
    n_links = 0
    if os.path.exists(lp):
        with io.open(lp, encoding="utf-8") as f:
            n_links = len(json.load(f))
    substats = ("%d 課題 · %d 知識點 · %d 測驗題 · %d 條串連"
                % (len(topics), n_pts, n_q, n_links))
    html = (HTML
            .replace("{ST}", SITE_TITLE)
            .replace("__SUBSTATS__", substats)
            .replace("__TARGET__", quote(_html_name))
            .replace("__PORT__", PORT)
            .replace("__CANDIDATES__", json.dumps(cands, ensure_ascii=False)))
    dst = os.path.join(SITE, "index.html")
    with io.open(dst, "w", encoding="utf-8") as f:
        f.write(html)
    print("index.html 已生成（%d 個候選網址）" % len(cands))
    for c in cands:
        print("  %-16s %s" % (c["ip"], c["kindLabel"]))


if __name__ == "__main__":
    main()
