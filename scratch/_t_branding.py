# -*- coding: utf-8 -*-
"""验证本轮三项改动：版本号、F6 清除、免责声明。"""
import io
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(BASE, "site")

results = []
def check(name, ok, detail=""):
    results.append((name, ok, detail))
    print(("  PASS  " if ok else "  FAIL  ") + name + (("   " + detail) if detail else ""))

# 读构建产物
p = os.path.join(SITE, "神智核.html")
if not os.path.exists(p):
    print("找不到构建产物")
    sys.exit(1)
html = io.open(p, encoding="utf-8").read()
# 版本号动态读取（改版后测试不会过期）
vj = json.loads(io.open(os.path.join(SITE, "version.json"), encoding="utf-8").read())

print("=" * 72)
print("[1] 版本号 %s" % vj["version"])
print("=" * 72)
check("页面标题含当前版本号 %s" % vj["version"], "神智核 %s" % vj["version"] in html)
_old = [v for v in ("V0.0.16", "V0.0.15") if v in html]
check("不含旧版本号", not _old, "仍有 %s" % _old if _old else "")
check("产物文件名为 神智核-%s.html" % vj["version"],
      os.path.exists(os.path.join(SITE, "神智核-%s.html" % vj["version"])))
check("version.json 的 version", vj["version"] == "V0.1.0", vj["version"])

print("\n" + "=" * 72)
print("[2] 用户可见处的 F6 已清除")
print("=" * 72)
# 提取所有文本节点（粗略：去标签后找 F6）
text_only = re.sub(r"<script[^>]*>.*?</script>", " ", html, flags=re.S)
text_only = re.sub(r"<style[^>]*>.*?</style>", " ", text_only, flags=re.S)
text_only = re.sub(r"<[^>]+>", " ", text_only)
n_f6_text = len(re.findall(r"F6", text_only))
check("頁面可見文字不含 F6", n_f6_text == 0, "發現 %d 處" % n_f6_text)
if n_f6_text:
    for m in list(re.finditer(r"F6", text_only))[:5]:
        print("      ...%s..." % text_only[max(0, m.start()-40):m.start()+40].replace("\n", " "))

# 标题相关字段
check("version.json subtitle 无 F6", "F6" not in vj["subtitle"], vj["subtitle"])
mf = json.loads(io.open(os.path.join(SITE, "manifest.json"), encoding="utf-8").read())
check("manifest name 无 F6", "F6" not in mf["name"], mf["name"])
check("manifest description 无 F6", "F6" not in mf["description"])
for sid in ("chem", "phys", "bio"):
    fp = os.path.join(BASE, "data", sid, "subject.json")
    if os.path.exists(fp):
        d = json.loads(io.open(fp, encoding="utf-8").read())
        check("data/%s subject.full 无 F6" % sid, "F6" not in (d.get("full") or ""), d.get("full"))
        check("data/%s subject.source 无 F6" % sid, "F6" not in (d.get("source") or ""))

print("\n" + "=" * 72)
print("[3] 免责声明")
print("=" * 72)
check("頁尾含版權聲明", "僅供學習用途" in html and "請勿商用" in html)
check("頁尾有可展開的完整聲明", "版權與免責聲明" in html and "<details" in html)
check("設定頁含免責聲明區", "legalbox" in html and "legallist" in html)
for kw in ("非官方出版品", "版權歸原作者", "不收集", "立即處理或移除"):
    check("聲明含「%s」" % kw, kw in html)
check("version.json 有 copyright", bool(vj.get("copyright")))
check("version.json 有 disclaimer 陣列", isinstance(vj.get("disclaimer"), list),
      "%d 條" % len(vj.get("disclaimer") or []))

print("\n" + "=" * 72)
print("[4] 技术标识未被误改（进度数据安全）")
print("=" * 72)
check("localStorage 键 f6note. 保留", "f6note." in html)
check("localStorage 键 f6chem.v1 保留", "f6chem.v1" in html)
check("旧档名转址保留", os.path.exists(os.path.join(SITE, "F6筆記整合網.html")))

print("\n" + "=" * 72)
ok = sum(1 for _, o, _ in results if o)
print("結果: %d/%d 通過" % (ok, len(results)))
if ok != len(results):
    print("失敗項：")
    for n, o, d in results:
        if not o:
            print("  - %s  %s" % (n, d))
    sys.exit(1)
print("三項改動全部生效")
sys.exit(0)
