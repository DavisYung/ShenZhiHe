# -*- coding: utf-8 -*-
"""严格核验部署包：版本、img 引用完整性、关键文件、路径层级。"""
import io, json, os, re, sys

sys.stdout.reconfigure(encoding="utf-8")

WORK = r"D:\deepseek-harness\default-workspace"
PKG = os.path.join(WORK, "神智核-GitHub部署包")

html = io.open(os.path.join(PKG, "index.html"), encoding="utf-8").read()

# 1) 版本
meta = json.load(io.open(os.path.join(WORK, "f6chem", "site", "version.json"), encoding="utf-8"))
ver = meta["version"]
has_ver = ver in html
title = re.search(r"<title>(.*?)</title>", html, re.S)
title = title.group(1).strip() if title else ""

# 2) HTML 里引用的所有图片文件名（形如 img/xxx.webp）
refs = set(re.findall(r"img/([A-Za-z0-9_\-\.]+\.webp)", html))
img_dir = os.path.join(PKG, "img")
on_disk = set(f for f in os.listdir(img_dir) if f.endswith(".webp"))

missing = sorted(refs - on_disk)
unused = sorted(on_disk - refs)

# 3) 关键文件存在
must = [".nojekyll", "index.html", "404.html", "manifest.json", "service-worker.js",
        "apple-touch-icon.png", "apple-touch-icon-152.png", "apple-touch-icon-167.png",
        "favicon.ico", "favicon-32.png", "icon-192.png", "icon-512.png",
        "icon-maskable-512.png", "README.md", "部署指南.md"]
missing_files = [f for f in must if not os.path.exists(os.path.join(PKG, f))]

# 4) 层级：img 必须是一级子目录，且图片不能再嵌套
nested_img = [f for f in on_disk if os.sep in f]

# 5) 总大小 / 文件数
n, total = 0, 0
for root, _d, fs in os.walk(PKG):
    for f in fs:
        n += 1
        total += os.path.getsize(os.path.join(root, f))

out = []
out.append("版本            : %s  (index.html 内含: %s)" % (ver, "是" if has_ver else "否"))
out.append("页面标题        : %s" % title)
out.append("HTML 引用图片   : %d 张" % len(refs))
out.append("img/ 实际图片   : %d 张" % len(on_disk))
out.append("引用但缺图      : %d %s" % (len(missing), missing[:5]))
out.append("有图但未引用    : %d %s" % (len(unused), unused[:5]))
out.append("必需文件缺失    : %d %s" % (len(missing_files), missing_files))
out.append("图片嵌套错误    : %d" % len(nested_img))
out.append("elec 关键字     : %d 次" % len(re.findall(r"elec[1-6]", html)))
out.append("内嵌 base64     : %d 处" % html.count("data:image"))
out.append("总文件数        : %d" % n)
out.append("总大小          : %.1f MB" % (total / 1024.0 / 1024.0))
ok = (has_ver and not missing and not missing_files and not nested_img and len(on_disk) > 400)
out.append("")
out.append("结论            : %s" % ("全部通过 ✅" if ok else "有項目未通過 ❌"))

txt = "\n".join(out)
print(txt)
io.open(os.path.join(WORK, "_pkg_verify2.txt"), "w", encoding="utf-8").write(txt + "\n")