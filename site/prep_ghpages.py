# -*- coding: utf-8 -*-
"""準備 GitHub Pages 發布目錄。

做五件事：
1. 把離線單檔網站複製成 ASCII 檔名 index.html（GitHub Pages 對非 ASCII 檔名連結不友好）
2. 生成 .nojekyll（避免 Jekyll 處理 _ 開頭檔案）
3. 附一個精簡的 README 與 404 提示頁
4. 附上 PWA 資源（manifest.json、service-worker.js、icons/、favicon.ico），
   讓使用者可以「加到主畫面」——這同時是 iOS 不清空學習進度的前提
5. 把 service-worker.js 裡的 __SW_VERSION__ 換成站點版號（改版即換快取名）
"""
import io, json, os, re, shutil, sys
sys.stdout.reconfigure(encoding="utf-8")

SITE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(os.path.dirname(SITE), "gh-pages")

# 站名與版號（改版只動 version.json）
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _sitefile import site_meta, stable_html, versioned_html  # noqa: E402
META = site_meta()
SITE_NAME = META["name"]
SITE_VER = META["version"]
SITE_TITLE = "%s %s" % (SITE_NAME, SITE_VER)


README = """# {ST}


化學、物理、生物三科的離線整合版。化學與物理內容已完成；生物分區已建好，內容待補。

**分區互不干擾**：三科各有自己的課題、知識圖譜、測驗與學習進度，
連 localStorage 都是分開的鍵，切科目不會蓋掉彼此的紀錄。

## 建議先「加到主畫面」

用手機開這個網站時，請先加到主畫面（iOS：Safari 分享 → 加入主畫面；
Android：瀏覽器選單 → 安裝應用程式）。這不只是為了像 App，而是**關係到進度會不會消失**：

iOS Safari 會清掉「7 天以上沒打開」的網站的 localStorage，
學習進度、錯題、複習排程會無聲歸零。加到主畫面裝成 App 之後就不會再被清掉。
裝好之後也支援離線使用，斷網、地鐵上都能打開複習。

設定頁有「匯出備份／匯入備份」，換裝置前先匯出，新裝置匯入即可接著學。

## 化學區（已完成）

{NP} 份化學教師版筆記 PDF 的離線整合版。

- **{NPTS}** 個知識點（全部附原 PDF 頁碼）
- **{NQ}** 道測驗題（選擇 {NMC} / 是非 {NTF}，全部點選作答）
- **{NL}** 條跨課題知識串連，互動知識圖譜
- {NT} 個課題：{TOPLIST}

## 物理區（已完成）

牛津《新高中生活與物理（第二版）》課堂工作紙，分**熱學**與**力學**兩個分區：

- **熱學**：溫度與溫度計、內能與比熱容量、物態的改變、傳熱方式、氣體定律與分子運動論
- **力學**：長度時間與運動描述、直線運動線圖、牛頓三定律、力矩平衡、功與能量、動量、拋體、圓周運動、萬有引力

- **{PNPTS}** 個知識點（全部附原 PDF 頁碼與筆記原圖）
- **{PNQ}** 道測驗題（全部點選作答）
- **{PNL}** 條跨課題知識串連
- {PNT} 個課題：{PTOPLIST}

整站是**單一 HTML 檔**，無外部依賴，進度與錯題記錄存在瀏覽器 localStorage。

## 版權與免責聲明

> ⚠️ **本網站一切資源僅供學習用途，請勿商用。**

- 本網站為個人學習用途的筆記整理，非官方出版品，與任何出版社、考試機構均無隸屬或合作關係。
- 筆記內容、例題與圖表整理自公開教材及歷屆試題，版權歸原作者、出版方及香港考試及評核局所有。
- 所有資源僅供個人學習、複習與教學參考，請勿用於任何商業用途，亦請勿再行散布或用於營利。
- 整理過程雖力求準確，仍可能存在疏漏或錯誤，內容僅供參考，一切以官方教材及考試機構公布為準。
- 本站不對內容的準確性、完整性或適用性作任何保證，使用者須自行判斷並承擔使用後果。
- 學習進度與錯題紀錄僅儲存在使用者自己的瀏覽器中，本站不收集、不上傳任何個人資料。
- 如版權所有者認為本站內容不妥，請聯絡我們，我們會立即處理或移除。
""".replace("{ST}", SITE_TITLE)

NOJEKYLL = ""


def load(path, default=None):
    if not os.path.exists(path):
        return default
    with io.open(path, encoding="utf-8") as f:
        return json.load(f)


def chem_readme_stats():
    """從資料檔實時統計，避免課題增減後 README 過期。"""
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    subj = load(os.path.join(base, "data", "chem", "subject.json"), {}) or {}
    topics = subj.get("topics") or []
    n_pts = n_mc = n_tf = 0
    titles = []
    for tid in topics:
        t = load(os.path.join(base, "data", "chem", tid + ".json"), None)
        if t:
            titles.append("%s %s" % (tid.upper(), t.get("title", "")))
            n_pts += sum(len(s.get("points", [])) for s in t.get("sections", []))
        q = load(os.path.join(base, "quiz", "chem", tid + ".json"), None) or {}
        for x in q.get("questions", []):
            if x.get("type") == "mc":
                n_mc += 1
            elif x.get("type") == "tf":
                n_tf += 1
    links = load(os.path.join(base, "data", "chem", "links.json"), []) or []
    return dict(NP=len(topics), NT=len(topics), NPTS=n_pts, NQ=n_mc + n_tf,
                NMC=n_mc, NTF=n_tf, NL=len(links), TOPLIST="、".join(titles))


def phys_readme_stats():
    """物理區統計（同樣實時從資料檔算，避免 README 與內容脫節）。"""
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    subj = load(os.path.join(base, "data", "phys", "subject.json"), {}) or {}
    topics = subj.get("topics") or []
    n_pts = n_q = 0
    titles = []
    for tid in topics:
        t = load(os.path.join(base, "data", "phys", tid + ".json"), None)
        if t:
            titles.append(t.get("title", tid))
            n_pts += sum(len(s.get("points", [])) for s in t.get("sections", []))
        q = load(os.path.join(base, "quiz", "phys", tid + ".json"), None) or {}
        n_q += len(q.get("questions", []) or [])
    links = load(os.path.join(base, "data", "phys", "links.json"), []) or []
    return dict(PNPTS=n_pts, PNQ=n_q, PNL=len(links),
                PNT=len(topics), PTOPLIST="、".join(titles))

NOTFOUND = """<!doctype html>
<html lang="zh-Hant"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{ST}</title>
<style>
body{margin:0;min-height:100vh;display:flex;align-items:center;justify-content:center;
 background:linear-gradient(160deg,#0f766e,#134e4a);color:#fff;
 font-family:"PingFang TC","Microsoft JhengHei",system-ui,sans-serif;padding:20px;text-align:center}
.c{max-width:420px;width:100%}
h1{font-size:23px;margin:0 0 10px}
p{opacity:.85;font-size:14.5px;line-height:1.8}
a.btn{display:inline-block;background:#fff;color:#0f766e;text-decoration:none;font-weight:700;
 font-size:17px;padding:14px 28px;border-radius:13px;margin-top:20px;min-height:44px;line-height:1.2;box-sizing:border-box}
</style></head>
<body><div class="c">
<h1>🧪 {ST}</h1>
<p>你打開的這個頁面不存在。<br>回到首頁請點下面的按鈕。</p>
<a class="btn" id="home" href="./">回到首頁 →</a>
</div>
<script>
// 這個 404 頁面會被 GitHub Pages 用在任何不存在的路徑下，網址可能是
//   /倉庫名/打錯的頁面        或   /倉庫名/深/一層/打錯
// 所以不能用 "./"（它會相對「打錯的那一層」解析，還是 404），
// 也不能用 "/"（那是使用者主頁，不是筆記）。
// 專案網站的網址固定是 /倉庫名/...，取第一段就是倉庫根；使用者主頁只有一段，根就是 "/"。
(function () {
  var path = location.pathname;
  var seg = path.split("/").filter(Boolean);
  var base;
  if (seg.length >= 2) {
    base = "/" + seg[0] + "/";        // /倉庫名/任何東西
  } else if (seg.length === 1 && path.charAt(path.length - 1) === "/") {
    base = "/" + seg[0] + "/";        // /倉庫名/ 本身
  } else {
    base = "/";                       // 使用者主頁，或主頁下的 404
  }
  document.getElementById("home").setAttribute("href", base);
})();
</script>
</body></html>
""".replace("{ST}", SITE_TITLE)


def rmtree_soft(path):
    """刪掉舊的發布目錄。裡面可能殘留 headless Chrome 的臨時 profile（檔案被鎖住），
    這種情況下逐項刪、刪不掉的先跳過，不要讓整個發布流程失敗。"""
    if not os.path.isdir(path):
        return
    for root, dirs, files in os.walk(path, topdown=False):
        for n in files:
            try:
                os.unlink(os.path.join(root, n))
            except OSError:
                pass
        for n in dirs:
            try:
                os.rmdir(os.path.join(root, n))
            except OSError:
                pass
    try:
        os.rmdir(path)
    except OSError:
        print("  note: 舊發布目錄有檔案被占用，殘留部分已略過")


def copy_pwa():
    """複製 PWA 資源到發布目錄，並把 SW 版號換成當前站點版號。

    這些檔案是「加到主畫面」與「離線可用」的必要條件，也讓 iOS 給予
    durable storage（否則 7 天沒開就清空學習進度）。
    缺檔不致命：網站本體仍可正常使用，只是少了安裝與離線能力。
    """
    copied = []
    # PWA 核心檔案 + 圖示，全部平鋪在網站根目錄。
    # 刻意不放 icons/ 子資料夾：用 GitHub 網頁上傳時，拖曳資料夾很容易只傳到檔案、
    # 整個資料夾沒上去；而 <link rel="apple-touch-icon"> 一旦指向 404，iOS 不會回退到
    # 根目錄圖示，會直接用 theme-color 底色 + 標題首字生成佔位圖示。
    # 平鋪在根目錄後，上傳時「全選檔案一起拖」就不可能漏。
    flat = ["manifest.json", "service-worker.js", "favicon.ico",
            "apple-touch-icon.png", "apple-touch-icon-167.png", "apple-touch-icon-152.png",
            "favicon-32.png", "icon-192.png", "icon-512.png", "icon-maskable-512.png"]
    for name in flat:
        src = os.path.join(SITE, name)
        if not os.path.exists(src):
            print("  note: 缺少 %s（略過；網站本體不受影響）" % name)
            continue
        dst = os.path.join(OUT, name)
        if name == "service-worker.js":
            with io.open(src, encoding="utf-8") as f:
                js = f.read()
            js = js.replace("__SW_VERSION__", SITE_VER)
            with io.open(dst, "w", encoding="utf-8") as f:
                f.write(js)
        else:
            shutil.copy2(src, dst)
        copied.append(name)
    return copied


def main():
    rmtree_soft(OUT)
    if not os.path.isdir(OUT):
        os.makedirs(OUT)

    # 主站 = 穩定檔名的單檔網站（舊檔名的轉址頁只有幾百 bytes，會自然被排除）
    src = stable_html()
    if not os.path.exists(src):
        cands = []
        for n in os.listdir(SITE):
            if (n.endswith(".html") and "verify" not in n and "shot" not in n
                    and n != "index.html"):
                p = os.path.join(SITE, n)
                cands.append((os.path.getsize(p), p))
        cands.sort(reverse=True)
        if not cands:
            raise SystemExit("找不到網站 HTML")
        src = cands[0][1]

    shutil.copy2(src, os.path.join(OUT, "index.html"))
    _stats = chem_readme_stats()
    _stats.update(phys_readme_stats())
    with io.open(os.path.join(OUT, "README.md"), "w", encoding="utf-8") as f:
        f.write(README.format(**_stats))
    with io.open(os.path.join(OUT, ".nojekyll"), "w", encoding="utf-8") as f:
        f.write(NOJEKYLL)
    with io.open(os.path.join(OUT, "404.html"), "w", encoding="utf-8") as f:
        f.write(NOTFOUND)
    pwa = copy_pwa()

    print("站名：%s" % SITE_TITLE)
    print("來源：%s" % os.path.basename(src))
    print("發布目錄已準備好：%s" % OUT)
    for n in sorted(os.listdir(OUT)):
        p = os.path.join(OUT, n)
        if os.path.isfile(p):
            print("  %-18s %8.1f KB" % (n, os.path.getsize(p) / 1024.0))
    print("  PWA 資源：%d 個（%s）" % (len(pwa), "、".join(pwa[:3]) + ("…" if len(pwa) > 3 else "")))

    total = 0
    for root, _dirs, files in os.walk(OUT):
        for n in files:
            total += os.path.getsize(os.path.join(root, n))
    print("\n合計 %.1f KB" % (total / 1024.0))


if __name__ == "__main__":
    main()
