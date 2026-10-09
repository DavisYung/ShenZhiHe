# -*- coding: utf-8 -*-
"""验证 PWA 改动是否正确落地（在发布目录 gh-pages/ 上检查）。"""
import io, json, os, re, subprocess, sys

sys.stdout.reconfigure(encoding="utf-8")
BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(os.path.dirname(BASE), "gh-pages")

results = []
def check(name, ok, detail=""):
    results.append((name, ok, detail))
    print(("  PASS  " if ok else "  FAIL  ") + name + (("   " + detail) if detail else ""))

def read(p):
    with io.open(p, encoding="utf-8") as f:
        return f.read()

print("发布目录: %s\n" % OUT)

# ---------- 1. 必需文件 ----------
print("[1] 文件齐全")
need = ["index.html", "404.html", "manifest.json", "service-worker.js",
        "favicon.ico", ".nojekyll", "README.md",
        "icon-192.png", "icon-512.png", "icon-maskable-512.png",
        "apple-touch-icon.png", "apple-touch-icon-167.png", "apple-touch-icon-152.png",
        "favicon-32.png"]
for n in need:
    p = os.path.join(OUT, n.replace("/", os.sep))
    check("存在 %s" % n, os.path.isfile(p))

# 圖示必須平鋪在根目錄。曾把圖示放 icons/ 子資料夾，結果用 GitHub 網頁上傳時
# 整個資料夾漏掉 → <link> 指向 404 → iOS 生成「theme-color + 標題首字」佔位圖示。
check("沒有 icons/ 子資料夾（圖示平鋪根目錄）",
      not os.path.isdir(os.path.join(OUT, "icons")))
_head = read(os.path.join(OUT, "index.html"))[:8000]
check("圖示連結不含 icons/ 前綴", 'href="./icons/' not in _head)

# ---------- 2. 404 页（上轮 bug 的源头修复） ----------
print("\n[2] 404.html 子路径跳转（源码层面已修）")
h404 = read(os.path.join(OUT, "404.html"))
check("不再用绝对根 href=\"/\"", 'href="/"' not in h404)
check("无双花括号残留", "{{" not in h404)
check("含 location.pathname 路径判断", "location.pathname" in h404)
check("含回到首頁按钮", "回到首頁" in h404)

# ---------- 3. manifest ----------
print("\n[3] manifest.json")
m = json.loads(read(os.path.join(OUT, "manifest.json")))
check("name 含神智核", "神智核" in m.get("name", ""))
check("start_url 用相对路径", m.get("start_url") == "./", "start_url=%s" % m.get("start_url"))
check("scope 用相对路径", m.get("scope") == "./", "scope=%s" % m.get("scope"))
check("display=standalone", m.get("display") == "standalone")
check("theme_color=#0f766e", m.get("theme_color") == "#0f766e")
check("有 192 图标", any(i.get("sizes") == "192x192" for i in m.get("icons", [])))
check("有 512 图标", any(i.get("sizes") == "512x512" for i in m.get("icons", [])))
check("有 maskable 图标", any("maskable" in (i.get("purpose") or "") for i in m.get("icons", [])))
# 图标路径必须是相对的
bad = [i["src"] for i in m.get("icons", []) if not i["src"].startswith("./")]
check("图标路径均为相对路径", not bad, "问题项=%s" % bad if bad else "")

# ---------- 4. service worker ----------
print("\n[4] service-worker.js")
sw = read(os.path.join(OUT, "service-worker.js"))
check("版本占位符已替换", "__SW_VERSION__" not in sw)
vm = re.search(r"var SW_VERSION = '([^']+)'", sw)
check("版本号正确", bool(vm) and vm.group(1) == "V0.0.16",
      "SW_VERSION=%s" % (vm.group(1) if vm else "?"))
check("含 install 事件", "addEventListener('install'" in sw)
check("含 fetch 事件", "addEventListener('fetch'" in sw)
check("含 activate 事件", "addEventListener('activate'" in sw)
check("导航请求网络优先", "navigate" in sw)
check("离线回退到缓存首页", "caches.match('./index.html')" in sw)
# 只检查「实际使用」的路径参数是否相对；注释里提到 "/index.html" 是说明为何不用它，不算违规
uses_abs = re.findall(r"(?:cache\.add|caches\.match)\(\s*['\"]/", sw)
check("预缓存/匹配用相对路径", not uses_abs, "绝对路径调用=%s" % uses_abs if uses_abs else "")
# 语法检查
r = subprocess.run(["node", "--check", os.path.join(OUT, "service-worker.js")],
                   capture_output=True)
check("node --check 语法通过", r.returncode == 0, r.stderr.decode("utf-8", "replace")[:200])

# ---------- 4.5 圖示必須是不透明 RGB（iOS 黑邊坑，本次修的就是這個） ----------
print("\n[4.5] 圖示不透明（iOS 會把 alpha 合成到黑底，導致圖示發黑）")
try:
    from PIL import Image
    icon_files = ["icon-192.png", "icon-512.png",
                  "icon-maskable-512.png", "apple-touch-icon.png",
                  "apple-touch-icon-167.png", "apple-touch-icon-152.png",
                  "favicon-32.png"]
    for rel in icon_files:
        p = os.path.join(OUT, rel.replace("/", os.sep))
        if not os.path.isfile(p):
            check("存在 %s" % rel, False)
            continue
        im = Image.open(p)
        has_alpha = im.mode in ("RGBA", "LA") or (im.mode == "P" and "transparency" in im.info)
        n_partial = 0
        if has_alpha:
            a = im.convert("RGBA").getchannel("A")
            n_partial = sum(a.histogram()[:255])
        check("%s 無 alpha 且無半透明像素" % rel, (not has_alpha) and n_partial == 0,
              "mode=%s 半透明=%d" % (im.mode, n_partial))
except ImportError:
    print("  note: 沒有 Pillow，跳過圖示透明度檢查")

# ---------- 4.6 根目錄兜底圖示（iOS 找不到 link 時會來這裡找） ----------
print("\n[4.6] iOS 圖示聲明與兜底")
idx0 = read(os.path.join(OUT, "index.html"))
check("apple-touch-icon 帶 sizes", 'rel="apple-touch-icon" sizes="180x180"' in idx0)
check("含 iPad 尺寸 167", "apple-touch-icon-167.png" in idx0)
check("含 iPad 尺寸 152", "apple-touch-icon-152.png" in idx0)
check("根目錄有 apple-touch-icon.png（兜底）",
      os.path.isfile(os.path.join(OUT, "apple-touch-icon.png")))

# ---------- 5. index.html 的 PWA 接入 ----------
print("\n[5] index.html PWA 接入")
idx = read(os.path.join(OUT, "index.html"))
check("引用 manifest", 'rel="manifest"' in idx)
check("manifest 用相对路径", 'href="./manifest.json"' in idx)
check("apple-touch-icon", "apple-touch-icon" in idx)
check("theme-color meta", 'name="theme-color"' in idx)
check("apple-mobile-web-app-capable", "apple-mobile-web-app-capable" in idx)
check("注册 service worker", "serviceWorker.register" in idx)
check("SW 路径为相对", "'./service-worker.js'" in idx)
check("file:// 下跳过 SW 注册", "location.protocol" in idx)
check("含加到主屏引导", "pwaHintHTML" in idx)
check("含 iOS 判断", "isIOS" in idx)
check("含 standalone 检测", "isStandalone" in idx)
check("设置页含 PWA 区块", "pwa-set-hint" in idx)
check("调用了 maybeShowPwaHint", "maybeShowPwaHint()" in idx)
check("站点仍是单文件自包含（无外链）", not re.search(r'https?://', idx.replace("https://github.com", "")))

# ---------- 6. 不破坏原有能力 ----------
print("\n[6] 原有功能未被破坏")
check("汇出備份仍在", "function exportBackup" in idx)
check("匯入備份仍在", "function importBackup" in idx)
check("删除本机纪录仍在", "function clearSiteData" in idx)
check("虚拟滚动仍在", "VIRT" in idx)
check("搜索 worker 仍在", "__SEARCH_WORKER_URL__" in idx)
check("script 标签成对", idx.count("<script") == idx.count("</script>"),
      "%d/%d" % (idx.count("<script"), idx.count("</script>")))
check("含 </html> 收尾", idx.rstrip().endswith("</html>"))
check("无 file:/// 本机路径", "file:///" not in idx)

ok = sum(1 for _, o, _ in results if o)
print("\n" + "=" * 60)
print("结果: %d/%d 通过" % (ok, len(results)))
if ok != len(results):
    print("失败项:")
    for n, o, d in results:
        if not o:
            print("  - %s  %s" % (n, d))
    sys.exit(1)
print("PWA 改动验证通过")
sys.exit(0)
