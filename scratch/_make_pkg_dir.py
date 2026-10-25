# -*- coding: utf-8 -*-
"""手工生成部署包文件夹（不依赖 _mk_pkg.py，避免旧目录残留导致 FileExistsError）。"""
import io, os, shutil, stat, sys

sys.stdout.reconfigure(encoding="utf-8")

WORK = r"D:\deepseek-harness\default-workspace"
SRC = os.path.join(WORK, "f6chem", "gh-pages")
PKG = os.path.join(WORK, "神智核-GitHub部署包")

EXCLUDE = {"_t_dwell.png", "_t_v015.html", "_t_logic.html"}


def on_rm_error(func, path, exc_info):
    try:
        os.chmod(path, stat.S_IWRITE)
        func(path)
    except Exception:
        pass


# 1) 清空旧部署包（含旧的 .git，让用户自己 init）
if os.path.isdir(PKG):
    shutil.rmtree(PKG, onerror=on_rm_error)
    if os.path.isdir(PKG):
        shutil.rmtree(PKG, ignore_errors=True)
    if os.path.isdir(PKG):
        print("!! 旧目录未能完全删除，请关闭占用该目录的程序后重试")
        sys.exit(1)
os.makedirs(PKG, exist_ok=True)

# 2) 收集 gh-pages 内容
files = []
for root, dirs, fs in os.walk(SRC):
    dirs[:] = [d for d in dirs if not d.startswith("_t_")]
    for n in sorted(fs):
        if n in EXCLUDE or n.startswith("_t_"):
            continue
        ap = os.path.join(root, n)
        rp = os.path.relpath(ap, SRC)
        files.append((rp, ap))

# 3) 拷贝
for rp, ap in files:
    dst = os.path.join(PKG, rp)
    d = os.path.dirname(dst)
    if d and not os.path.isdir(d):
        os.makedirs(d)
    shutil.copy2(ap, dst)

# 4) 统计
n = 0
total = 0
for root, _dirs, fs in os.walk(PKG):
    for f in fs:
        n += 1
        total += os.path.getsize(os.path.join(root, f))

root_files = sorted(f for f in os.listdir(PKG) if os.path.isfile(os.path.join(PKG, f)))
sub_dirs = sorted(d for d in os.listdir(PKG) if os.path.isdir(os.path.join(PKG, d)))

report = []
report.append("部署包目录: %s" % PKG)
report.append("总文件数: %d" % n)
report.append("总大小: %.1f MB" % (total / 1024.0 / 1024.0))
report.append("根目录文件 (%d): %s" % (len(root_files), ", ".join(root_files)))
report.append("子目录 (%d): %s" % (len(sub_dirs), ", ".join(sub_dirs)))
for d in sub_dirs:
    dp = os.path.join(PKG, d)
    cnt = sum(len(fs) for _r, _dd, fs in os.walk(dp))
    sz = sum(os.path.getsize(os.path.join(r, f)) for r, _dd, fs in os.walk(dp) for f in fs)
    report.append("  %s/ : %d 个文件, %.1f MB" % (d, cnt, sz / 1024.0 / 1024.0))

txt = "\n".join(report)
io.open(os.path.join(WORK, "_pkg_report.txt"), "w", encoding="utf-8").write(txt + "\n")
print(txt)
