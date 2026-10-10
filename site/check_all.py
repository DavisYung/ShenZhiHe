# -*- coding: utf-8 -*-
"""一键跑完全部检查（质量门）。

把散落的各个测试串成一个入口，改完代码跑这一条就够：

    python check_all.py            # 全部检查
    python check_all.py --quick    # 只跑快速项（跳过浏览器测试）

包含：
  1. 数据 schema 校验（jsonschema）        —— 快
  2. 数据深度审计（图片/用字/题点引用）      —— 快
  3. 单元与物理功能静态校验                —— 快
  4. 构建站点                              —— 中
  5. 化学回归 _t_v015.py                  —— 中（浏览器）
  6. PWA 静态 _t_pwa.py                    —— 快
  7. 科目切换（Playwright）                —— 中（浏览器）
  8. 单元导航（Playwright/CDP）            —— 中（浏览器）
  9. ESLint / HTML Validate               —— 快
"""
import io
import os
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PY = sys.executable
NODE = "node"

QUICK = "--quick" in sys.argv


def run(label, cmd, cwd=HERE, allow_fail=False):
    print("\n" + "=" * 74)
    print("▶ %s" % label)
    print("=" * 74)
    try:
        p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=900)
    except subprocess.TimeoutExpired:
        print("  ⏱ 逾时（900s）")
        return False
    out = (p.stdout or "") + (p.stderr or "")
    # 只印尾段，避免刷屏
    lines = [l for l in out.splitlines() if l.strip()]
    for l in lines[-8:]:
        print("  " + l)
    ok = p.returncode == 0
    print("  → %s (exit=%d)" % ("通過 ✓" if ok else "失敗 ✗", p.returncode))
    return ok


def main():
    results = []

    # ---- 快速项 ----
    results.append(("Schema 校验", run("1/9 資料 Schema 校驗",
                                       [PY, "_t_schema.py"])))
    results.append(("Schema 校验器自检", run("2/9 Schema 校驗器反向測試",
                                             [PY, "_t_schema_probe.py"])))
    results.append(("物理內容審計", run("3/9 物理內容獨立審計",
                                       [PY, os.path.join(ROOT, "scratch", "_phys_audit.py")])))
    results.append(("物理內容校驗", run("3b/9 物理內容逐點校驗",
                                       [PY, os.path.join(ROOT, "scratch", "_phys_check.py")])))
    results.append(("電學獨立審計", run("3c/9 電學獨立審計",
                                       [PY, os.path.join(ROOT, "scratch", "_elec_audit.py")])))
    results.append(("PWA 静态", run("4/9 PWA 靜態檢查", [PY, "_t_pwa.py"])))

    # ---- 构建 ----
    # build 后必须接 prep：gh-pages/（index.html + img/ + PWA 资源）是浏览器
    # 与交付测试的被测对象，不重跑 prep 会测到上一次的旧产物。
    results.append(("构建站点", run("5/9 構建站點", [PY, "build.py"])))
    results.append(("准备发布目录", run("5b/9 準備 gh-pages（含 img/ 外置圖）",
                                        [PY, "prep_ghpages.py"])))

    # ---- 浏览器项 ----
    if QUICK:
        print("\n（--quick：跳过浏览器测试）")
    else:
        results.append(("化学回归", run("6/9 化學回歸（headless Chrome）",
                                       [PY, "_t_v015.py"])))
        results.append(("PIP 行为", run("6b/9 PIP 開關行為（獨立驗證）",
                                       [NODE, "_t_pip.mjs", "."])))
        results.append(("科目切换", run("7/9 科目切換（Playwright）",
                                       [NODE, "_t_switch_pw.cjs", ".", os.environ.get("TEMP", ".")])))
        results.append(("单元导航", run("8/9 單元導航（真實 Chrome）",
                                       [NODE, os.path.join(ROOT, "scratch", "_t_units.mjs"),
                                        ".", os.environ.get("TEMP", ".")])))
        results.append(("圖片外置離線", run("8b/9 圖片外置後離線完整性（真實 Chrome）",
                                          [NODE, "_t_extimg.mjs", os.path.join("..", "gh-pages"),
                                           os.environ.get("TEMP", ".")])))

    # ---- 静态代码检查 ----
    results.append(("ESLint", run("9/9a ESLint",
                                  [NODE, os.path.join("node_modules", "eslint", "bin", "eslint.js"), "."])))
    results.append(("HTML Validate", run("9/9b HTML Validate",
                                         [NODE, os.path.join("node_modules", "html-validate", "bin",
                                                             "html-validate.mjs"), "神智核.html"])))

    print("\n" + "=" * 74)
    print("總結")
    print("=" * 74)
    bad = 0
    for name, ok in results:
        print("  %-22s %s" % (name, "✓ 通過" if ok else "✗ 失敗"))
        if not ok:
            bad += 1
    print("\n共 %d 項，通過 %d，失敗 %d" % (len(results), len(results) - bad, bad))
    if bad:
        print("\n有失敗項，請看上面輸出。")
        sys.exit(1)
    print("\n全部通過 🎉")
    sys.exit(0)


if __name__ == "__main__":
    main()
