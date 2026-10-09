# -*- coding: utf-8 -*-
"""把 gh-pages/ 的发布内容打包成可直接部署的交付目录 + zip。

产物（工作区根目录）：
    神智核-GitHub部署包/       可直接拖到 GitHub 的目录
    神智核-GitHub部署包.zip    同上的压缩包

打包内容 = gh-pages/ 全部文件（含 PWA 資源） + 部署指南.md
部署指南的「檔案」表格由本脚本依實際檔案大小自動生成，避免文件與產物不同步。
"""
import io, os, shutil, sys, zipfile

sys.stdout.reconfigure(encoding="utf-8")

SITE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(SITE)                      # f6chem/
WORK = os.path.dirname(ROOT)                      # 工作區根
SRC = os.path.join(ROOT, "gh-pages")
PKG = os.path.join(WORK, "神智核-GitHub部署包")
ZIP = os.path.join(WORK, "神智核-GitHub部署包.zip")

sys.path.insert(0, SITE)
from _sitefile import site_meta  # noqa: E402
META = site_meta()
NAME, VER = META["name"], META["version"]

# 這些檔案屬於開發／測試產物，不進交付包
EXCLUDE = {"_t_dwell.png", "_t_v015.html", "_t_logic.html"}


def human(n):
    if n < 1024:
        return "%d B" % n
    if n < 1024 * 1024:
        return "%.1f KB" % (n / 1024.0)
    return "%.1f MB" % (n / 1024.0 / 1024.0)


def collect():
    """回傳 [(相對路徑, 絕對路徑)]，相對路徑用 / 分隔。"""
    out = []
    for root, dirs, files in os.walk(SRC):
        dirs[:] = [d for d in dirs if not d.startswith("_t_")]
        for n in sorted(files):
            if n in EXCLUDE or n.startswith("_t_"):
                continue
            ap = os.path.join(root, n)
            rp = os.path.relpath(ap, SRC).replace("\\", "/")
            out.append((rp, ap))
    return sorted(out)


GUIDE = """# 部署到 GitHub Pages

做完之后你会得到一个網址，像 `https://你的用戶名.github.io/神智核/`，手機、電腦、平板隨時都能開，不用電腦一直開著。

要準備的東西只有一個 GitHub 帳號，沒有的話去 <https://github.com/signup> 免費註冊，再準備一個瀏覽器就夠了。

---

## 方式一：網頁上傳（最簡單，第一次建議用這個）

### 1. 建一個新倉庫

打開 <https://github.com/new>

| 欄位 | 填什麼 |
|---|---|
| Repository name | `神智核`（想用英文就填 `shenzhine` 或你喜歡的名字） |
| Description | 隨便寫，例如 `F6 三科筆記整合網` |
| Public / Private | 選 **Public**，免費版的 Pages 只支援公開倉庫 |
| 勾選 | `Add a README file` |
| License | 隨便選或不選 |

點 **Create repository**。

### 2. 上傳檔案

在倉庫頁面點 **Add file** → **Upload files**，把這個資料夾裡的**所有檔案**一起拖進去。

> ✅ **圖示都平鋪在根目錄，沒有子資料夾，全選拖進去就對了。**
> 以前圖示放在 `icons/` 子資料夾，用網頁拖曳時整個資料夾容易漏掉，
> 而圖示連結一旦 404，iPhone 不會用根目錄的圖示，會自己生成一個
> 「主題色底 + 標題第一個字」的佔位圖示（看起來完全不是你設計的那個）。
> 現在改成平鋪，就沒有這個風險了。

拖完點 **Commit changes**。

> ⚠️ 兩個小坑：
> 1. `.nojekyll` 以點開頭，網頁上傳時可能傳不上去。傳不上也沒關係，網站照樣能用（我們的檔名沒有以 `_` 開頭）。
> 2. `index.html` 有 4.7 MB，上傳要等十幾秒，進度條不動是正常的。

### 3. 開啟 Pages

1. 倉庫頂部點 **Settings**
2. 左邊選單點 **Pages**
3. **Source** 下拉選 **Deploy from a branch**
4. **Branch** 選 **main**，右邊的資料夾選 **/ (root)**
5. 點 **Save**

### 4. 等一到三分鐘

重新整理頁面，上面會出現一行：

```
Your site is live at https://你的用戶名.github.io/神智核/
```

點開那個網址，看到筆記網站就成了。

> 倉庫名是中文的話，GitHub 會把它轉成 `%E7%A5%9E...` 這種編碼塞進網址，能用但不好看也不好記。
> 想讓網址乾淨一點，倉庫名用英文（例如 `shenzhine`），網址就是 `https://你的用戶名.github.io/shenzhine/`。

---

## 方式二：Git 命令行

適合之後要經常更新的人。差別是不用每次手動拖檔案，改完推一下就好。

### 1. 建倉庫

同方式一的第 1 步，但**不要勾** `Add a README file`。

### 2. 在本機執行

把這個資料夾當成倉庫根目錄：

```powershell
cd "這裡填這個資料夾的路徑"

git init
git add .
git commit -m "神智核 {VER}"
git branch -M main
git remote add origin https://github.com/你的用戶名/神智核.git
git push -u origin main
```

`git add .` 會把 `.nojekyll` 和 `icons/` 一起加進去，這點比網頁上傳方便。

推送時會要你輸入帳號密碼。**密碼那欄要填 Personal Access Token，不是你的 GitHub 登入密碼**，現在 GitHub 已經不接受密碼推送了。取得方式：

1. 點 GitHub 頭像 → **Settings**
2. 左側拉到最下面 → **Developer settings**
3. **Personal access tokens** → **Tokens (classic)** → **Generate new token (classic)**
4. 勾選 `repo`，Expiration 選個到期日
5. 產生後把那串 token 複製起來，它只顯示一次
6. 貼進終端機時畫面不會顯示任何字元，這是正常的，貼完直接按 Enter

### 3. 開啟 Pages

同方式一的第 3、4 步。

---

## 一定要做：加到主畫面

網站開起來之後，請**先在手機上把它加到主畫面**：

- **iPhone / iPad**：用 Safari 開 → 底部「分享」按鈕 → 「加入主畫面」→ 新增
- **Android**：用 Chrome 開 → 右上角選單 → 「安裝應用程式」或「加到主畫面」

這不只是為了像 App。**iOS Safari 會清掉「7 天以上沒打開」的網站的 localStorage**，
你的學習進度、錯題、複習排程會無聲歸零，而且不會有任何提示。
裝成 App 之後就不會再被清掉，另外也支援斷網使用。

網站偵測到你在 iOS 上還沒安裝時，會自己跳一個提示告訴你怎麼做，設定頁也有說明。

---

## 之後要更新內容

```powershell
cd "這個資料夾的路徑"
git add .
git commit -m "更新筆記內容"
git push
```

推上去之後等一到兩分鐘，網址上的內容就換新了。GitHub Pages 有快取，如果還是舊的，按 Ctrl+F5 強制重新整理，或者在網址後面加個 `?v=2` 試試。

> 更新後如果手機上還是舊版，把 App 完全關掉再開一次。
> 網站有做版本化快取，偵測到新版會提示「有新版本，重新載入即可更新」。

---

## 手機上怎麼用

1. 用 Safari 開你的網址
2. 底部「分享」→「加入主畫面」
3. 桌面出現圖示，之後點它就能用

好處是不用電腦開著，出門在外也能複習，沒網路也能打開。

有一點要留意：**學習進度存在每台裝置自己的瀏覽器裡**。手機上做的題，iPad 上看不到，反過來也一樣。
換裝置前到「設定 → 資料管理」按「匯出備份」，在新裝置按「匯入備份」就能接著學。

---

## 常見問題

**網址打開是 404？**
Pages 還沒部署完，等一到三分鐘。超過五分鐘還是 404，回去 Settings → Pages 檢查 Source 和 Branch 有沒有選對。

**上傳時說檔案太大？**
GitHub 單檔上限 100 MB，我們最大的是 4.7 MB，不會超。

**加到主畫面後圖示是「主題色底 + 一個字」？**
那是 iPhone 自己生成的佔位圖示，說明它沒載入到你上傳的圖示。通常是圖示檔案沒傳上去。
檢查方法：在手機瀏覽器直接開
`https://你的用戶名.github.io/倉庫名/apple-touch-icon.png`
如果顯示 404，就是漏傳了，重新上傳一次全部檔案。

**圖示換了但主畫面上還是舊的？**
iOS／Android 會快取 App 圖示，換圖後不會馬上更新。這樣處理：
1. 長按主畫面那個圖示 → 刪除 App（學習進度不會跟著刪，它在瀏覽器儲存裡）
2. Safari 設定 → 進階 → 網站資料 → 找到本站 → 刪除
3. 重新開網站 → 分享 → 加入主畫面

還有一個細節：`index.html` 的檔名如果沒變，瀏覽器可能沿用快取的 HTML，
所以「重新加入主畫面」前建議先按 Ctrl+F5 強制重新整理一次。

**網址太長不好記？**
倉庫名用英文就好，或者買個網域。想用自己的網域：Settings → Pages → Custom domain 填進去，然後去網域服務商那邊加一筆 CNAME 記錄指向 `你的用戶名.github.io`。

**內容會被公開嗎？**
會。Public 倉庫的東西誰都看得到。這是自己的學習筆記，一般沒什麼問題。真的不想公開，可以改用私有倉庫加 Cloudflare Pages，免費方案也支援。

**以後換電腦了怎麼辦？**
用方式二的話，新電腦 `git clone` 下來就行。用方式一的話，把這個資料夾留著，之後照著「之後要更新內容」那節做。

---

## 這個資料夾裡有什麼

| 檔案 | 大小 | 作用 |
|---|---|---|
{TABLE}

網站本身零外部依賴，所有筆記圖片都已經內嵌在 HTML 裡，不連任何外部網址。
`manifest.json`、`service-worker.js` 和 `icons/` 是讓它能「加到主畫面」與離線使用的必要檔案。
"""

DESC = {
    "index.html": "整個網站，{pts} 個知識點、{q} 道題、{links} 條串連",
    "404.html": "開到不存在的頁面時的提示，會自動判斷倉庫路徑",
    "manifest.json": "PWA 設定（App 名稱、圖示、啟動方式）",
    "service-worker.js": "離線快取，也是 iOS 不清空進度的前提",
    "favicon.ico": "瀏覽器分頁圖示",
    "README.md": "倉庫首頁的說明",
    ".nojekyll": "讓 GitHub 原樣發布",
    "部署指南.md": "你正在看的這份",
    "icon-192.png": "App 圖示 192px（Android／PWA 用）",
    "icon-512.png": "App 圖示 512px（Android／PWA 用）",
    "icon-maskable-512.png": "Android 自適應圖示（圓形裁切用）",
    "apple-touch-icon.png": "iOS 加到主畫面用的圖示 180px",
    "apple-touch-icon-167.png": "iPad Pro 用圖示 167px",
    "apple-touch-icon-152.png": "iPad 用圖示 152px",
    "favicon-32.png": "瀏覽器分頁小圖示",
}


def main():
    if not os.path.isdir(SRC):
        sys.exit("找不到發布目錄：%s（請先跑 prep_ghpages.py）" % SRC)

    files = collect()
    if not files:
        sys.exit("發布目錄是空的")

    # 統計資料，用於指南表格說明
    try:
        import json
        import glob
        n_pts = n_q = n_links = 0
        base = os.path.join(ROOT, "data", "chem")
        subj = {}
        p = os.path.join(base, "subject.json")
        if os.path.exists(p):
            with io.open(p, encoding="utf-8") as f:
                subj = json.load(f)
        for tid in subj.get("topics", []):
            tp = os.path.join(base, tid + ".json")
            if os.path.exists(tp):
                with io.open(tp, encoding="utf-8") as f:
                    t = json.load(f)
                n_pts += sum(len(s.get("points", [])) for s in t.get("sections", []))
            qp = os.path.join(ROOT, "quiz", "chem", tid + ".json")
            if os.path.exists(qp):
                with io.open(qp, encoding="utf-8") as f:
                    q = json.load(f)
                n_q += len(q.get("questions", []))
        lp = os.path.join(base, "links.json")
        if os.path.exists(lp):
            with io.open(lp, encoding="utf-8") as f:
                n_links = len(json.load(f))
    except Exception:
        n_pts = n_q = n_links = 0

    # 重建交付目錄
    if os.path.isdir(PKG):
        shutil.rmtree(PKG, ignore_errors=True)
    os.makedirs(PKG)

    for rp, ap in files:
        dst = os.path.join(PKG, rp.replace("/", os.sep))
        d = os.path.dirname(dst)
        if d and not os.path.isdir(d):
            os.makedirs(d)
        shutil.copy2(ap, dst)

    # 部署指南（表格依實際檔案大小生成）
    rows = []
    for rp, ap in files:
        desc = DESC.get(rp)
        if desc is None:
            continue
        desc = desc.format(pts=n_pts, q=n_q, links=n_links)
        rows.append("| `%s` | %s | %s |" % (rp, human(os.path.getsize(ap)), desc))
    rows.append("| `部署指南.md` | 這份 | 你正在看的 |")
    guide = GUIDE.replace("{VER}", VER).replace("{TABLE}", "\n".join(rows))
    with io.open(os.path.join(PKG, "部署指南.md"), "w", encoding="utf-8") as f:
        f.write(guide)

    # zip
    if os.path.exists(ZIP):
        os.remove(ZIP)
    with zipfile.ZipFile(ZIP, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for root, _dirs, fs in os.walk(PKG):
            for n in sorted(fs):
                ap = os.path.join(root, n)
                rp = os.path.relpath(ap, PKG).replace("\\", "/")
                z.write(ap, rp)

    print("交付目錄：%s" % PKG)
    total = 0
    for root, _dirs, fs in os.walk(PKG):
        for n in sorted(fs):
            ap = os.path.join(root, n)
            rp = os.path.relpath(ap, PKG).replace("\\", "/")
            total += os.path.getsize(ap)
            print("  %-30s %9s" % (rp, human(os.path.getsize(ap))))
    print("\n合計 %.1f MB" % (total / 1024.0 / 1024.0))
    print("壓縮包：%s（%.2f MB）" % (ZIP, os.path.getsize(ZIP) / 1024.0 / 1024.0))

    # 驗證 zip 內含必要檔案（.nojekyll 是 0 字節，最容易漏）
    with zipfile.ZipFile(ZIP) as z:
        names = z.namelist()
    for must in (".nojekyll", "index.html", "manifest.json", "service-worker.js",
                 "apple-touch-icon.png", "icon-192.png", "icon-512.png",
                 "icon-maskable-512.png", "favicon.ico", "404.html"):
        if must not in names:
            sys.exit("zip 缺少必要檔案：%s" % must)
    if any(n.startswith("icons/") for n in names):
        sys.exit("zip 內不應有 icons/ 子資料夾（圖示已改為平鋪根目錄）")
    print("zip 內容檢查通過（%d 個檔案，含 .nojekyll，圖示平鋪根目錄）" % len(names))


if __name__ == "__main__":
    main()
