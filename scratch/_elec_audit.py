# -*- coding: utf-8 -*-
"""電學內容獨立審計：不信任自檢，重新交叉核驗。

核驗項目：
  1. 圖片頁碼一致性：body 引用的頁圖編號是否落在該知識點的 page 內
  2. 圖片檔真實存在
  3. 殘留填空 / 亂碼 / 異體字 / LaTeX
  4. 內容覆蓋：核心關鍵詞是否都寫進 body
  5. 測驗題：point 引用有效、explanation 夠長、mc 答案索引合法、id 不重複
  6. 知識點 id 全域唯一、與串連 links.json 互相引用有效
"""
import io
import json
import os
import re
import sys
from collections import Counter

sys.stdout.reconfigure(encoding="utf-8")
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, "data", "phys")
QUIZ = os.path.join(BASE, "quiz", "phys")
IMG = os.path.join(BASE, "site", "img")

issues = []
warns = []

TIDS = ["elec1", "elec2", "elec3", "elec4", "elec5", "elec6"]

KEY_CHECKS = {
 "elec1": ["質子", "中子", "電子", "起電", "電場力線", "庫倫", "電場強度", "電勢能", "接地"],
 "elec2": ["安培計", "伏特計", "電動勢", "電勢差", "電阻", "歐姆定律", "等效電阻", "分壓器", "內電阻", "端電壓"],
 "elec3": ["功率", "額定", "保險絲", "活線", "中線", "地線", "環形幹線", "斷路器", "千瓦小時"],
 "elec4": ["北極", "南極", "磁力線", "螺線管", "弗林明左手定則", "忒斯拉", "磁導率", "換向器", "力偶"],
 "elec5": ["感生電動勢", "法拉第", "楞次", "弗林明右手定則", "磁通量", "韋伯", "發電機", "渦電流"], "elec6": ["交流電", "方均根", "變壓器", "原線圈", "副線圈", "匝數比", "疊片式", "高壓輸電"],
}

IMG_PAGE = re.compile(r"!\[[^\]]*\]\(img/(phys_elec[a-z]*_p(\d+))\.webp\)")

all_ids = {}
all_pid = []

print("=" * 74)
print("電學內容獨立審計")
print("=" * 74)

for tid in TIDS:
    p = os.path.join(DATA, tid + ".json")
    if not os.path.exists(p):
        issues.append("[%s] data 檔不存在" % tid)
        continue
    t = json.load(io.open(p, encoding="utf-8"))
    pts = [pt for s in t.get("sections", []) for pt in s.get("points", [])]
    all_ids[tid] = {pt["id"] for pt in pts}
    all_pid.extend(pt["id"] for pt in pts)
    print("\n[%s] %s — %d 章 %d 點" % (tid, t.get("title"),
                                      len(t.get("sections", [])), len(pts)))

    # 1. 圖片頁碼一致性
    bad_img, multi = [], []
    for pt in pts:
        pages = [int(m.group(2)) for m in IMG_PAGE.finditer(pt.get("body") or "")]
        if len(pages) > 1:
            multi.append(pt["id"])
        if pages and pt.get("page") not in pages:
            bad_img.append("%s: page=%s 引用頁 %s" % (pt["id"], pt.get("page"), pages))
    if bad_img:
        issues.append("[%s] page 與引用頁不符 %d 處: %s" % (tid, len(bad_img), bad_img[:3]))
        print("   ✗ page 與引用頁不符 %d 處: %s" % (len(bad_img), bad_img[:2]))
    else:
        print("   ✓ page 欄位落在引用頁範圍內")
    if multi:
        print("   ℹ 跨頁知識點 %d 個（一點多圖，合理）" % len(multi))

    # 2. 圖片檔存在
    missing = []
    for pt in pts:
        for m in re.finditer(r"!\[[^\]]*\]\(img/([^)\s]+)\)", pt.get("body") or ""):
            if not os.path.exists(os.path.join(IMG, m.group(1))):
                missing.append("%s -> %s" % (pt["id"], m.group(1)))
    if missing:
        issues.append("[%s] 圖片檔不存在: %s" % (tid, missing[:3]))
        print("   ✗ 圖片檔不存在 %d 個" % len(missing))
    else:
        print("   ✓ 引用的圖片檔全部存在")

    # 3. 殘留填空 / 亂碼 / 異體字 / LaTeX
    leftover = [pt["id"] for pt in pts if re.search(r"_{3,}", pt.get("body") or "")]
    fffd = [pt["id"] for pt in pts if "\ufffd" in (pt.get("body") or "")]
    latex = [pt["id"] for pt in pts
             if re.search(r"\\frac|\\times|\$\$|\\Delta|\\mu", pt.get("body") or "")]
    ellip = [pt["id"] for pt in pts if "..." in (pt.get("body") or "")]
    wen = sum((pt.get("body") or "").count("\u6e29") for pt in pts)
    if leftover:
        issues.append("[%s] 殘留填空: %s" % (tid, leftover))
        print("   ✗ 殘留填空: %s" % leftover[:3])
    else:
        print("   ✓ 無殘留填空下劃線")
    if fffd:
        issues.append("[%s] 亂碼: %s" % (tid, fffd))
        print("   ✗ 亂碼 %d 處" % len(fffd))
    if latex:
        issues.append("[%s] 殘留 LaTeX 語法: %s" % (tid, latex))
        print("   ✗ 殘留 LaTeX %d 處" % len(latex))
    if ellip:
        issues.append("[%s] 殘留省略號佔位（可能內容不全）: %s" % (tid, ellip))
        print("   ✗ 殘留省略號佔位 %d 處" % len(ellip))
    if wen:
        issues.append("[%s] 殘留異體字「温」%d 次" % (tid, wen))
        print("   ✗ 殘留「温」%d 次" % wen)

    # 4. 內容覆蓋
    allbody = " ".join((pt.get("body") or "") for pt in pts)
    miss = [k for k in KEY_CHECKS.get(tid, []) if k not in allbody]
    if miss:
        issues.append("[%s] 核心關鍵詞缺失: %s" % (tid, miss))
        print("   ✗ 核心關鍵詞缺失: %s" % miss)
    else:
        print("   ✓ 核心關鍵詞齊全 (%d/%d)"
              % (len(KEY_CHECKS.get(tid, [])), len(KEY_CHECKS.get(tid, []))))

    # 5. 測驗題
    qp = os.path.join(QUIZ, tid + ".json")
    if not os.path.exists(qp):
        issues.append("[%s] quiz 檔不存在" % tid)
        continue
    q = json.load(io.open(qp, encoding="utf-8"))
    qs = q.get("questions") or []
    dist = Counter(x.get("type") for x in qs)
    pids = {pt["id"] for pt in pts}
    bad_ref = [x.get("id") for x in qs if x.get("point") not in pids]
    empty_ex = [x.get("id") for x in qs if len((x.get("explanation") or "").strip()) < 10]
    dup_ids = [k for k, v in Counter(x.get("id") for x in qs).items() if v > 1]
    bad_ans = []
    for x in qs:
        if x.get("type") == "mc":
            opts = x.get("options") or []
            a = x.get("answer")
            if not isinstance(a, int) or a < 0 or a >= len(opts):
                bad_ans.append(x.get("id"))
    tf_bad = [x.get("id") for x in qs
              if x.get("type") == "tf" and not isinstance(x.get("answer"), bool)]
    print("   ▸ 題目 %d 題 %s" % (len(qs), dict(dist)))
    if bad_ref:
        issues.append("[%s] 題目指向無效 point: %s" % (tid, bad_ref[:3]))
        print("   ✗ 無效 point 引用: %s" % bad_ref[:3])
    else:
        print("   ✓ point 引用全部有效")
    if empty_ex:
        issues.append("[%s] explanation 過短: %s" % (tid, empty_ex[:3]))
        print("   ✗ explanation 過短: %s" % empty_ex[:3])
    if dup_ids:
        issues.append("[%s] 題目 id 重複: %s" % (tid, dup_ids))
    if bad_ans:
        issues.append("[%s] mc 答案索引越界: %s" % (tid, bad_ans))
        print("   ✗ mc 答案索引越界: %s" % bad_ans)
    else:
        print("   ✓ mc 答案索引全部合法")
    if tf_bad:
        issues.append("[%s] tf 答案非布林: %s" % (tid, tf_bad))

# 6. 知識點 id 全域唯一 + 串連有效
dup = [k for k, v in Counter(all_pid).items() if v > 1]
if dup:
    issues.append("知識點 id 全域重複: %s" % dup)
    print("\n✗ 知識點 id 全域重複: %s" % dup)
else:
    print("\n✓ 電學 %d 個知識點 id 全域唯一" % len(all_pid))

lp = os.path.join(DATA, "links.json")
links = json.load(io.open(lp, encoding="utf-8"))
elinks = [l for l in links if (l.get("from") or "").startswith("elec")
          or (l.get("to") or "").startswith("elec")]
allphys = set(all_pid)
for sub in os.listdir(DATA):
    if sub.endswith(".json") and sub not in ("subject.json", "links.json"):
        try:
            tt = json.load(io.open(os.path.join(DATA, sub), encoding="utf-8"))
        except Exception:
            continue
        if isinstance(tt, dict):
            for s in tt.get("sections") or []:
                for pt in s.get("points") or []:
                    allphys.add(pt.get("id"))
bad_links = [l for l in elinks
             if l.get("from") not in allphys or l.get("to") not in allphys]
if bad_links:
    issues.append("串連引用不存在的 id %d 條: %s" % (len(bad_links), bad_links[:2]))
    print("✗ 串連引用無效 %d 條" % len(bad_links))
else:
    print("✓ 電學相關串連 %d 條全部有效" % len(elinks))

# 統計
tot_pt = len(all_pid)
tot_q = sum(len(json.load(io.open(os.path.join(QUIZ, t + ".json"), encoding="utf-8")).get("questions") or [])
            for t in TIDS if os.path.exists(os.path.join(QUIZ, t + ".json")))
img_ref = sum(len(IMG_PAGE.findall((pt.get("body") or "")))
              for tid in TIDS
              for pt in [q for s in json.load(io.open(os.path.join(DATA, tid + ".json"), encoding="utf-8")).get("sections", []) for q in s.get("points", [])])
print("\n合計：%d 課、%d 知識點、%d 測驗題、%d 張頁圖引用" % (len(TIDS), tot_pt, tot_q, img_ref))

print("\n" + "=" * 74)
if warns:
    print("\n提醒（非致命）：")
    for w in warns:
        print("  ⚠ " + w)
if issues:
    print("\n發現 %d 個問題：" % len(issues))
    for i in issues:
        print("  ✗ " + i)
    sys.exit(1)
print("\n電學獨立審計通過：無實質問題")
sys.exit(0)
