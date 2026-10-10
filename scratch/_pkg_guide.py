# -*- coding: utf-8 -*-
"""为部署包生成「部署指南.md」，并核验包内关键文件。"""
import io, json, os, re, sys

sys.stdout.reconfigure(encoding="utf-8")

WORK = r"C:\Users\guomi\OneDrive\文件\deepseek-harness\default-workspace"
PKG = os.path.join(WORK, "神智核-GitHub部署包")
SITE = os.path.join(WORK, "f6chem", "site")

meta = json.load(io.open(os.path.join(SITE, "version.json"), encoding="utf-8"))
NAME, VER = meta["name"], meta["version"]

# --- 核验 index.html ---
idx = os.path.join(PKG, "index.html")
html = io.open(idx, encoding="utf-8").read()
checks = {}
checks["版本字串"] = VER in html
checks["電學单元"] = ("elec1" in html and "elec6" in html)
checks["外置图片引用"] = ('src="img/' in html or "src='img/" in html)
checks["无内嵌 base64 残留"] = ("data:image/" not in html)
checks["热学/力学/波动学"] = all(k in html for k in ("heat1", "mech1", "wave1"))
n_elec = len(re.findall(r"elec[1-6]", html))

GUIDE = """# {NAME} 部署指南（{VER}）

這份資料夾裡的內容，就是要**直接放在倉庫根目錄**的網站檔案。
放上去之後，GitHub Pages 就能打開，手機、電腦、平板隨時可用。

---

## 一、這包裡有什麼

| 檔案／目錄 | 說明 |
|---|---|
| `index.html` | 網站本體（單檔，含全部筆記、題庫、知識圖譜） |
| `img/` | 筆記原圖 428 張（HTML 以相對路徑引用，**必須整個目錄一起上傳**） |
| `404.html` | 找不到頁面時的導回頁 |
| `manifest.json`、`service-worker.js` | PWA：可「加到主畫面」變成 App，離線也能開 |
| `apple-touch-icon*.png`、`icon-*.png`、`favicon.ico` | 圖示（必須**平鋪在根目錄**，不能放子資料夾） |
| `.nojekyll` | 告訴 GitHub Pages 不要用 Jekyll 處理（少了它底線開頭的檔案會 404） |

⚠️ 關鍵：`index.html`、`img/`、圖示檔必須**同層**。若把 index.html 單獨丟進子目錄，網站不會生效。

---

## 二、上傳方式

### 方式 A：git 命令（推薦，最快且不會漏檔）

把這個資料夾的路徑複製起來，開 PowerShell：

```powershell
cd "這個資料夾的路徑"
git init -b main
git remote add origin https://github.com/nzgjsmy/ShenZhiHe.git
git add .
git commit -m "部署 {VER}"
git push -u -f origin main
```

`-f` 是必要的：遠端倉庫已有舊內容（舊的 master 分支），這裡是**全量替換**部署語意。

以後更新只要：重新產生部署包 → 進資料夾 → `git add . && git commit -m "更新" && git push -f`。

### 方式 B：GitHub 網頁上傳

1. 打開 `https://github.com/nzgjsmy/ShenZhiHe`
2. 左側分支選單 → **View all branches** → 新建 `main` 分支（或先切到你要用的分支）
3. 刪掉舊檔案：倉庫根目錄若有 `f6chem/` 等舊資料夾，先全部刪除（否則根目錄會混著舊內容）
4. **Add file → Upload files**，把本資料夾的**全部內容**拖進去
5. Commit

⚠️ **GitHub 網頁一次最多上傳 100 個檔案**，本包共 442 個，所以要分批：

| 批次 | 上傳內容 |
|---|---|
| 第 1 批 | 根目錄全部 14 個檔案（含 `.nojekyll`） |
| 第 2～5 批 | `img/` 裡的 428 張圖，每次約 100 張 |

分批上傳時**每批都要 commit**，且 `img/` 的路徑要維持在 `img/` 底下。

---

## 三、開啟 GitHub Pages

1. 倉庫 → **Settings** → 左側 **Pages**
2. Source 選 **Deploy from a branch**
3. Branch 選 **main**、資料夾選 **/ (root)** → Save
4. 等 1～2 分鐘，網址會是：

```
https://nzgjsmy.github.io/ShenZhiHe/
```

---

## 四、上線後檢查（30 秒）

| 檢查項 | 預期 |
|---|---|
| 首頁打開 | 看到「{NAME} {VER}」，有化學／物理／生物科目卡 |
| 物理 → 電學 | 看到「⚡ 電學」分區，點進去 6 個課題 |
| 電學測驗 | 「整個分區」能出題（95 題） |
| 任意一張圖 | 點開筆記頁圖能正常顯示（`img/` 有傳對） |
| 加到主畫面 | Safari／Chrome 可安裝成 App，離線仍能開 |

---

## 五、常見問題

**打開是 404？**
Pages 的 branch 沒選 `main`，或資料夾沒選 `/ (root)`。

**頁面能開但圖全破？**
`img/` 沒傳上去，或層級錯了（必須是 `img/xxx.webp`，不是 `子目錄/img/xxx.webp`）。

**主畫面的 App 圖示不對？**
圖示檔必須平鋪在根目錄。改完後要「刪掉主畫面圖示 → 清 Safari 網站資料 → 重新加到主畫面」才會更新。

**進度會不見嗎？**
學習進度存在你自己的瀏覽器（localStorage）。iOS Safari 若 7 天未互動會清除，
**「加到主畫面」安裝成 App 就能豁免**，建議一定要裝。
"""

guide = GUIDE.replace("{NAME}", NAME).replace("{VER}", VER)
with io.open(os.path.join(PKG, "部署指南.md"), "w", encoding="utf-8", newline="\n") as f:
    f.write(guide)

lines = []
lines.append("站点版本: %s %s" % (NAME, VER))
for k, v in checks.items():
    lines.append("  %-20s %s" % (k, "PASS" if v else "FAIL"))
lines.append("  elec 关键字出现  %d 次" % n_elec)
lines.append("")

n = 0
total = 0
for root, _d, fs in os.walk(PKG):
    for f in fs:
        n += 1
        total += os.path.getsize(os.path.join(root, f))
lines.append("部署包: %d 个文件, %.1f MB" % (n, total / 1024.0 / 1024.0))
lines.append("指南已写入: 部署指南.md")

txt = "\n".join(lines)
print(txt)
io.open(os.path.join(WORK, "_pkg_verify.txt"), "w", encoding="utf-8").write(txt + "\n")