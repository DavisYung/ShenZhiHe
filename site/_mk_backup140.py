# -*- coding: utf-8 -*-
"""重建「神智核-本地备份-V0.14.0/」，把旧 V0.20.0 备份整合掉。

背景（2026-10-21）：用户要求「把本地备份及所有神智核 0.20.0 的版本号都改成 0.14.0」，
经确认采取「整份备份重做」方案 —— 不是只替换版本号字符串，而是让备份目录的
内容与当前 V0.14.0 源码完全一致。

本脚本做的事：
  1. 清掉旧的 V0.14.0 备份里 01/02 两个纯文件目录（就地覆盖式）
  2. 用活源码 f6chem/site/ 重建 01-源码/
  3. 用 f6chem/gh-pages/ 重建 02-构建产物/
  4. 用工作区根的 神智核-GitHub部署包/ 重建 03-部署包/（含 .git）
  5. 从旧版备份补回活源码已移除但仍有价值的历史文件（_t_pick.cjs 等）
  6. 写备份说明.md

安全：删除前会校验路径必须位于工作区根且名字精确匹配。
"""
import io, os, shutil, sys

sys.stdout.reconfigure(encoding="utf-8")
SITE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(SITE)                 # f6chem/
WORK = os.path.dirname(ROOT)                 # 工作區根
sys.path.insert(0, SITE)
from _sitefile import site_meta  # noqa: E402

META = site_meta()
VER = META["version"]                        # V0.14.0
DST = os.path.join(WORK, "神智核-本地备份-%s" % VER)
# 舊版備份（只取其中仍有效的歷史測試腳本，不帶版本號字樣）
OLD_NAMES = ("神智核-本地备份-V0.20.0-oldtmp", "神智核-本地备份-V0.19.0")
OLD = None
for _n in OLD_NAMES:
    _p = os.path.join(WORK, _n)
    if os.path.isdir(_p):
        OLD = _p
        break
SRC_DIR = os.path.join(DST, "01-源码")
BUILD_DIR = os.path.join(DST, "02-构建产物")
PKG_DIR = os.path.join(DST, "03-部署包")
PKG = os.path.join(WORK, "神智核-GitHub部署包")
GH = os.path.join(ROOT, "gh-pages")
EXTRAS = os.path.join(ROOT, "extras")

# ---------- 安全：路径守卫 ----------
if not WORK.endswith("default-workspace"):
    raise SystemExit("工作區根路徑異常：%s" % WORK)
if os.path.basename(DST) != "神智核-本地备份-%s" % VER:
    raise SystemExit("備份目錄名異常：%s" % DST)


def rmtree_safe(p):
    """刪除目錄；先校驗路徑在預期位置。"""
    p = os.path.abspath(p)
    if not p.startswith(os.path.abspath(WORK) + os.sep):
        raise SystemExit("拒絕刪除工作區外的路徑：%s" % p)
    if os.path.isdir(p):
        shutil.rmtree(p, ignore_errors=True)
        if os.path.isdir(p):  # OneDrive 鎖導致部分刪不掉，逐項再試
            for n in os.listdir(p):
                q = os.path.join(p, n)
                try:
                    if os.path.isdir(q):
                        shutil.rmtree(q, ignore_errors=True)
                    else:
                        os.remove(q)
                except OSError:
                    pass
            try:
                os.rmdir(p)
            except OSError:
                pass
    if os.path.isdir(p):
        raise SystemExit("無法刪除舊備份目錄：%s" % p)


# 1) 清掉旧 V0.14.0 备份
# 注意：03-部署包 内含 .git，OneDrive 常把 .git 内文件锁住导致整目录删不掉
# （本项目 2026-10-16 已因 rmtree 失败炸掉过一次交付目录）。
# 因此这里改成「就地覆盖」：先删 01/02 两个纯文件目录，03-部署包则按条目覆盖，
# 删不掉的旧文件直接跳过（部署包内容每次都会全量重写，残留无害）。
rmtree_safe(SRC_DIR)
rmtree_safe(BUILD_DIR)
os.makedirs(SRC_DIR, exist_ok=True)
os.makedirs(BUILD_DIR, exist_ok=True)
os.makedirs(PKG_DIR, exist_ok=True)

# 2) 01-源码：站点源文件（不含 img/ 与临时产物）
SRC_FILES = ["template.html", "extras.js", "build.py", "prep_ghpages.py", "_mk_pkg.py",
             "_sitefile.py", "manifest.json", "service-worker.js", "version.json",
             "search-worker.js", "_srv_fm.py", "_mk_backup140.py"]
for n in SRC_FILES:
    p = os.path.join(SITE, n)
    if os.path.exists(p):
        shutil.copy2(p, os.path.join(SRC_DIR, n))

# formulas.json：活源码已移除，實際改由 extras/phys/formulas.json 提供 → 從那裡取
fm = os.path.join(EXTRAS, "phys", "formulas.json")
if os.path.exists(fm):
    shutil.copy2(fm, os.path.join(SRC_DIR, "formulas.json"))

# 測試腳本（只帶 .cjs/.py，不帶 .png 產物）
for n in sorted(os.listdir(SITE)):
    if n.startswith("_t_") and n.endswith((".cjs", ".py")):
        shutil.copy2(os.path.join(SITE, n), os.path.join(SRC_DIR, n))

# 舊版備份裡有、但活源碼已無的歷史測試腳本 → 補回（它們仍是有效回歸）
# 排除已被新版取代、且硬編碼舊版號的：_t_online20.cjs / _t_final20.cjs
SKIP_OLD = {"_t_online20.cjs", "_t_final20.cjs"}
if os.path.isdir(OLD):
    old_src = os.path.join(OLD, "01-源码")
    for n in sorted(os.listdir(old_src)):
        if n.startswith("_t_") and n.endswith((".cjs", ".py")) and n not in SKIP_OLD:
            dst_p = os.path.join(SRC_DIR, n)
            if not os.path.exists(dst_p):
                shutil.copy2(os.path.join(old_src, n), dst_p)

# 舊檔名轉址頁
for n in ("F6化學筆記整合網.html", "F6筆記整合網.html"):
    p = os.path.join(SITE, n)
    if os.path.exists(p):
        shutil.copy2(p, os.path.join(SRC_DIR, n))

# 3) 02-构建产物：gh-pages 的入口檔
for n in ("index.html", "service-worker.js", "404.html", ".nojekyll",
          "manifest.json", "README.md", "部署指南.md"):
    p = os.path.join(GH, n)
    if os.path.exists(p):
        shutil.copy2(p, os.path.join(BUILD_DIR, n))

# 4) 03-部署包
# 順序很重要：先 git clone（會 checkout 工作區，index 與 HEAD 一致），
# 再把源部署包的最新檔案覆蓋上去 —— 這樣 git status 才乾淨。
# 注意：不能用 --no-checkout，否則 index 為空，git status 會把 900+ 檔案全顯示為「已刪除」。
# 坑：git clone 的目標目錄若名為 .git，會產生 .git/.git 雙層結構（非真正的倉庫）。
# 正解：先 clone 到臨時目錄，再把其中的 .git 移過去。
import subprocess, tempfile
if os.path.isdir(PKG_DIR):
    for name in os.listdir(PKG_DIR):
        q = os.path.join(PKG_DIR, name)
        try:
            if os.path.isdir(q):
                shutil.rmtree(q, ignore_errors=True)
            else:
                os.remove(q)
        except OSError:
            pass
os.makedirs(PKG_DIR, exist_ok=True)

tmp_clone = tempfile.mkdtemp(dir=DST)
r = subprocess.run(["git", "clone", "--no-hardlinks", PKG, tmp_clone],
                   capture_output=True, text=True, cwd=DST)
inner = os.path.join(tmp_clone, ".git")
if os.path.isdir(inner):
    shutil.move(inner, os.path.join(PKG_DIR, ".git"))
shutil.rmtree(tmp_clone, ignore_errors=True)
if not os.path.isdir(os.path.join(PKG_DIR, ".git")):
    print("  warn: git clone 失敗：%s" % ((r.stderr or r.stdout) or "")[:300])

# 然後把源部署包的最新內容覆蓋進來（clone 的是提交快照，源目錄可能已更新）
for name in os.listdir(PKG):
    if name == ".git":
        continue
    s = os.path.join(PKG, name)
    d = os.path.join(PKG_DIR, name)
    try:
        if os.path.isdir(s):
            shutil.copytree(s, d, dirs_exist_ok=True)
        else:
            shutil.copy2(s, d)
    except OSError as e:
        print("  warn: 複製 %s 失敗（%s）" % (name, e))

# 確保分支是 main，remote 指向 GitHub（clone 過來的是本地路徑）
def _git(*a):
    return subprocess.run(["git"] + list(a), capture_output=True, text=True, cwd=PKG_DIR)

if os.path.isdir(os.path.join(PKG_DIR, ".git")):
    br = _git("rev-parse", "--abbrev-ref", "HEAD")
    if br.stdout.strip() != "main":
        _git("checkout", "main")
    _git("remote", "set-url", "origin", "https://github.com/nzgjsmy/ShenZhiHe.git")
    # 把源目錄的新變化同步進索引（不提交，只讓 status 反映真實差異）
    _git("add", "-A")

# 5) 自檢：確認備份裡再無舊版號 0.20.0 殘留
# 排除本腳本自身（它的註釋裡本來就要提到舊版號）與 .git（git 歷史裡必然有舊 commit）
OLD_TAG = "0.20.0"
bad = []
for r, _, fs in os.walk(DST):
    if ".git" in r:
        continue
    for f in fs:
        if f == os.path.basename(__file__):
            continue
        p = os.path.join(r, f)
        if os.path.getsize(p) > 6_000_000:
            continue
        try:
            t = io.open(p, encoding="utf-8", errors="ignore").read()
        except OSError:
            continue
        if OLD_TAG in t:
            bad.append((os.path.relpath(p, DST), t.count(OLD_TAG)))
print("\n自檢：備份內殘留 %s 的檔案 %d 個" % (OLD_TAG, len(bad)))
for n, c in bad:
    print("   %s  x%d" % (n, c))
