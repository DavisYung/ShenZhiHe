# -*- coding: utf-8 -*-
"""对「解压后的交付包」做最终验收：模拟 GitHub Pages 子路径 + 静态检查。

用法: python _t_deliver.py <解压后的包目录>
"""
import io, json, os, re, sys

sys.stdout.reconfigure(encoding="utf-8")
PKG = os.path.abspath(sys.argv[1])

# 版本号从 version.json 动态读取——避免写死版本号，改版后测试不会过期
_HERE = os.path.dirname(os.path.abspath(__file__))
try:
    with io.open(os.path.join(_HERE, "version.json"), encoding="utf-8") as _f:
        SITE_VER = json.load(_f).get("version", "")
except Exception:
    SITE_VER = ""

results = []
def check(name, ok, detail=""):
    results.append((name, ok, detail))
    print(("  PASS  " if ok else "  FAIL  ") + name + (("   " + detail) if detail else ""))

def read(p):
    with io.open(p, encoding="utf-8") as f:
        return f.read()

print("交付包: %s\n" % PKG)

print("[1] 文件齐全（含 PWA 资源）")
need = ["index.html", "404.html", "manifest.json", "service-worker.js", "favicon.ico",
        ".nojekyll", "README.md", "部署指南.md",
        "icon-192.png", "icon-512.png", "icon-maskable-512.png",
        "apple-touch-icon.png", "apple-touch-icon-167.png", "apple-touch-icon-152.png",
        "favicon-32.png"]
for n in need:
    check("存在 %s" % n, os.path.isfile(os.path.join(PKG, n.replace("/", os.sep))))

check("沒有 icons/ 子資料夾（圖示平鋪根目錄）", not os.path.isdir(os.path.join(PKG, "icons")))

print("\n[1.5] 图标必须无 alpha（iOS 会把 alpha 合成到黑底）")
try:
    from PIL import Image
    for n in [x for x in need if x.endswith(".png")]:
        p = os.path.join(PKG, n.replace("/", os.sep))
        if not os.path.isfile(p):
            continue
        im = Image.open(p)
        has_alpha = im.mode in ("RGBA", "LA") or (im.mode == "P" and "transparency" in im.info)
        n_partial = 0
        if has_alpha:
            a = im.convert("RGBA").getchannel("A")
            n_partial = sum(a.histogram()[:255])
        check("%s 无 alpha/半透明" % n, (not has_alpha) and n_partial == 0,
              "mode=%s 半透明=%d" % (im.mode, n_partial))
except ImportError:
    print("  note: 无 Pillow，跳过")

print("\n[2] 无开发产物泄漏")
allf = []
for root, _d, fs in os.walk(PKG):
    for n in fs:
        allf.append(os.path.relpath(os.path.join(root, n), PKG).replace("\\", "/"))
bad = [f for f in allf if f.startswith("_t_") or f.endswith(".py") or f.startswith("__pycache__")]
check("无测试/脚本文件", not bad, "泄漏=%s" % bad if bad else "")
check("无 headless 截图", not any("shot" in f for f in allf))
check("文件数合理", 10 <= len(allf) <= 320, "共 %d 个" % len(allf))

print("\n[2b] 图片外置完整性（路线三核心）")
idx0 = read(os.path.join(PKG, "index.html"))
refs = sorted(set(re.findall(r"img/([A-Za-z0-9_]+\.webp)", idx0)))
check("HTML 引用图片", len(refs) >= 250, "引用 %d 张" % len(refs))
check("HTML 无 data:image 残留", "data:image" not in idx0)
img_dir = os.path.join(PKG, "img")
missing = [r for r in refs if not os.path.isfile(os.path.join(img_dir, r))]
check("引用的图片全部存在", not missing,
      "缺 %d 张: %s" % (len(missing), missing[:3]) if missing else "全部 %d 张就位" % len(refs))

print("\n[3] 404 子路径跳转（源头已修）")
h = read(os.path.join(PKG, "404.html"))
check("不再用绝对根", 'href="/"' not in h)
check("含路径判断", "location.pathname" in h)
check("无双花括号残留", "{{" not in h)

print("\n[4] manifest 与 SW")
m = json.loads(read(os.path.join(PKG, "manifest.json")))
check("start_url 相对", m.get("start_url") == "./")
check("图标路径相对", all(i["src"].startswith("./") for i in m.get("icons", [])))
sw = read(os.path.join(PKG, "service-worker.js"))
check("SW 版本已替换", "__SW_VERSION__" not in sw and (not SITE_VER or SITE_VER in sw),
      "SW_VERSION=%s" % SITE_VER)
check("SW 用相对路径", "./index.html" in sw)

print("\n[5] 站点自包含")
idx = read(os.path.join(PKG, "index.html"))
check("无外部 http 链接", not re.search(r"https?://", idx))
check("无本机路径", "file:///" not in idx and not re.search(r"[A-Za-z]:\\\\", idx))
check("含 PWA 接入", 'rel="manifest"' in idx and "serviceWorker.register" in idx)
check("含导出/导入备份", "exportBackup" in idx and "importBackup" in idx)
check("script 成对", idx.count("<script") == idx.count("</script>"))
check("收尾完整", idx.rstrip().endswith("</html>"))

print("\n[6] 部署指南数字与实际一致")
g = read(os.path.join(PKG, "部署指南.md"))
sz = os.path.getsize(os.path.join(PKG, "index.html")) / 1024.0 / 1024.0
check("指南提到加到主画面", "加到主畫面" in g or "加到主画面" in g)
check("指南提到 iOS 7 天清缓存", "7 天" in g)
check("指南含当前版本号 %s" % SITE_VER, (not SITE_VER) or (SITE_VER in g),
      "指南未含 %s" % SITE_VER if SITE_VER and SITE_VER not in g else "")
check("指南含版權聲明", "請勿商用" in g or "勿商用" in g)
# 指南表格里声明的 index.html 大小要与实际相符（允许 0.2MB 误差）
m_sz = re.search(r"`index\.html`\s*\|\s*([\d.]+)\s*MB", g)
if m_sz:
    declared = float(m_sz.group(1))
    check("指南中 index.html 大小正确", abs(declared - sz) < 0.25,
          "指南=%s MB 实际=%.2f MB" % (m_sz.group(1), sz))
else:
    check("指南有 index.html 大小欄位", False)
# 表格里声明的图标/配置大小要与实际一致（值动态计算，不写死）
for fn in ("icon-192.png", "manifest.json"):
    real = os.path.getsize(os.path.join(PKG, fn.replace("/", os.sep)))
    human = ("%d B" % real) if real < 1024 else ("%.1f KB" % (real / 1024.0))
    check("指南中 %s 大小正确" % fn, human in g, "实际=%s" % human)

ok = sum(1 for _, o, _ in results if o)
print("\n" + "=" * 60)
print("结果: %d/%d 通过" % (ok, len(results)))
if ok != len(results):
    for n, o, d in results:
        if not o:
            print("  - %s  %s" % (n, d))
    sys.exit(1)
print("交付包验收通过")
sys.exit(0)
