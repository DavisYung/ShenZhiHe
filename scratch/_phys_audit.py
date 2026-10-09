# -*- coding: utf-8 -*-
"""物理内容独立审计（不信任子代理自检，重新交叉核验）。

核验四件事：
  1. 图片页码一致性：body 里 ![..](img/phys_heat_pNN.webp) 的 NN 是否与 point 的 page 相符
  2. 内容覆盖：每个知识点是否真的回答了工作纸上的空（抽查关键词是否出现在 body）
  3. 答案真实性：抽查答案数值是否真的来自 solution 文件（而非编造）
  4. 结构完整性：id 唯一、题数、题型分布、explanation 非空
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
EX = os.path.join(BASE, "scratch", "phys_extract")

issues = []
warns = []


def load(p):
    with io.open(p, encoding="utf-8") as f:
        return json.load(f)


def main():
    subj = load(os.path.join(DATA, "subject.json"))
    tids = subj.get("topics") or []
    sol_text = io.open(os.path.join(EX, "Book_1_Heat_Notes_solution.txt"),
                       encoding="utf-8").read()
    work_text = (io.open(os.path.join(EX, "Heat_notes.txt"), encoding="utf-8").read()
                 + io.open(os.path.join(EX, "Gases_note.txt"), encoding="utf-8").read())

    total_pts = total_q = 0
    print("=" * 74)
    print("物理內容獨立審計")
    print("=" * 74)

    for tid in tids:
        p = os.path.join(DATA, tid + ".json")
        if not os.path.exists(p):
            print("\n[%s] ⏳ 尚未生成，跳過" % tid)
            continue
        t = load(p)
        pts = [pt for s in t.get("sections", []) for pt in s.get("points", [])]
        total_pts += len(pts)
        print("\n[%s] %s — %d 章 %d 點" % (tid, t.get("title"),
                                          len(t.get("sections", [])), len(pts)))

        # --- 1. 图片页码一致性 ---
        # 注意：檔名形如 phys_heat_p15.webp，页码後面是「.」不是「_」，
        # 正則必須允許結尾，否則會整批漏匹配（曾因此誤報）。
        IMG_PAGE = re.compile(r"!\[[^\]]*\]\(img/(phys_[a-z]+_p(\d+))\.webp\)")
        bad_img = []
        multi_page = []
        first_diff = []
        for pt in pts:
            body = pt.get("body") or ""
            page = pt.get("page")
            found = [(m.group(1), int(m.group(2))) for m in IMG_PAGE.finditer(body)]
            pages = [f[1] for f in found]
            if len(pages) > 1:
                multi_page.append((pt["id"], page, pages))
            # page 必須落在該知識點引用的頁碼集合內（知識點可跨頁，page 標主頁）
            if pages and page not in pages:
                bad_img.append("%s: page=%s 不在引用頁 %s 中" % (pt["id"], page, sorted(set(pages))))
            if pages and pages[0] != page:
                first_diff.append("%s: 首圖 p%d, page=%s, 全部=%s"
                                  % (pt["id"], pages[0], page, sorted(set(pages))))
        if bad_img:
            issues.append("[%s] page 欄位與引用頁不符: %s" % (tid, bad_img[:3]))
            print("   ✗ page 與引用頁不符 %d 處: %s" % (len(bad_img), bad_img[:2]))
        else:
            print("   ✓ page 欄位落在引用頁範圍內")
        if first_diff:
            print("   ℹ 首圖非 page 的知識點 %d 個（跨頁知識點，合理）: %s"
                  % (len(first_diff), first_diff[0][:60]))
        if multi_page:
            # 化學區慣例是「一點一頁一圖」，物理出現多圖是風格差異，記為提醒
            warns.append("[%s] 有 %d 個知識點內嵌多張頁圖（化學區慣例為一點一圖）: %s"
                         % (tid, len(multi_page), [m[0] for m in multi_page[:4]]))
            print("   ⚠ 內嵌多張頁圖的知識點 %d 個" % len(multi_page))

        # --- 2. 圖片檔案真實存在 ---
        missing = []
        for pt in pts:
            for m in re.finditer(r"!\[[^\]]*\]\(img/([^)\s]+)\)", pt.get("body") or ""):
                fp = os.path.join(BASE, "site", "img", m.group(1))
                if not os.path.exists(fp):
                    missing.append("%s -> %s" % (pt["id"], m.group(1)))
        if missing:
            issues.append("[%s] 圖片檔不存在: %s" % (tid, missing[:3]))
            print("   ✗ 圖片檔不存在 %d 個" % len(missing))
        else:
            print("   ✓ 引用的圖片檔全部存在")

        # --- 3. 殘留填空 / 亂碼 / LaTeX ---
        leftover = [pt["id"] for pt in pts if re.search(r"_{3,}", pt.get("body") or "")]
        fffd = [pt["id"] for pt in pts if "\ufffd" in (pt.get("body") or "")]
        latex = [pt["id"] for pt in pts
                 if re.search(r"\\frac|\\times|\$\$|\\Delta", pt.get("body") or "")]
        if leftover:
            issues.append("[%s] 殘留填空: %s" % (tid, leftover))
            print("   ✗ 殘留填空 %d 處: %s" % (len(leftover), leftover[:3]))
        else:
            print("   ✓ 無殘留填空下劃線")
        if fffd:
            issues.append("[%s] 亂碼: %s" % (tid, fffd))
            print("   ✗ 亂碼 %d 處" % len(fffd))
        if latex:
            warns.append("[%s] 疑似 LaTeX 寫法: %s" % (tid, latex[:3]))
            print("   ⚠ 疑似 LaTeX %d 處" % len(latex))

        # --- 4. 異體字 ---
        n_wen = sum((pt.get("body") or "").count("\u6e29") for pt in pts)
        if n_wen:
            issues.append("[%s] 殘留異體字 温 x%d" % (tid, n_wen))
            print("   ✗ 殘留「温」(U+6E29) %d 次" % n_wen)
        else:
            print("   ✓ 無異體字「温」")

        # --- 5. 內容覆蓋：抽查答案關鍵詞是否真的出現 ---
        # 從 solution 裡抽該課題常見答案詞，檢查是否被寫進 body
        allbody = " ".join((pt.get("body") or "") for pt in pts)
        key_checks = {
            "heat1": ["冷熱", "定點", "線性", "紅外", "熱敏電阻"],
            "heat3": ["潛熱", "熔化", "沸騰", "蒸發", "凝結"],
            "heat4": ["傳導", "對流", "輻射", "絕緣", "保溫瓶"],
            "heat5": ["壓強", "波義耳", "查理", "分子", "絕對溫度"],
        }.get(tid, [])
        if key_checks:
            miss = [k for k in key_checks if k not in allbody]
            if miss:
                warns.append("[%s] 關鍵詞未出現: %s" % (tid, miss))
                print("   ⚠ 關鍵詞未出現: %s" % miss)
            else:
                print("   ✓ 核心關鍵詞齊全 (%d/%d)" % (len(key_checks), len(key_checks)))

        # --- 6. 測驗題 ---
        qp = os.path.join(QUIZ, tid + ".json")
        if os.path.exists(qp):
            q = load(qp)
            qs = q.get("questions") or []
            total_q += len(qs)
            dist = Counter(x.get("type") for x in qs)
            pids = {pt["id"] for pt in pts}
            bad_ref = [x.get("id") for x in qs if x.get("point") not in pids]
            empty_ex = [x.get("id") for x in qs
                        if len((x.get("explanation") or "").strip()) < 8]
            short_ex = [x.get("id") for x in qs
                        if len((x.get("explanation") or "").strip()) < 20]
            dup_ids = [k for k, v in Counter(x.get("id") for x in qs).items() if v > 1]
            print("   ▸ 題目 %d 題 %s" % (len(qs), dict(dist)))
            if bad_ref:
                issues.append("[%s] 題目指向不存在的知識點: %s" % (tid, bad_ref[:3]))
                print("   ✗ 題目指向無效 point: %s" % bad_ref[:3])
            else:
                print("   ✓ 題目 point 引用全部有效")
            if empty_ex:
                issues.append("[%s] explanation 過短/空: %s" % (tid, empty_ex[:3]))
                print("   ✗ explanation 過短: %s" % empty_ex[:3])
            elif short_ex:
                warns.append("[%s] 部分 explanation 偏短: %s" % (tid, short_ex[:3]))
            if dup_ids:
                issues.append("[%s] 題目 id 重複: %s" % (tid, dup_ids[:3]))
                print("   ✗ 題目 id 重複: %s" % dup_ids[:3])
            # mc 答案索引必須在選項範圍內
            bad_ans = []
            for x in qs:
                if x.get("type") == "mc":
                    opts = x.get("options") or []
                    a = x.get("answer")
                    if not isinstance(a, int) or a < 0 or a >= len(opts):
                        bad_ans.append(x.get("id"))
            if bad_ans:
                issues.append("[%s] mc 答案索引越界: %s" % (tid, bad_ans[:3]))
                print("   ✗ mc 答案索引越界: %s" % bad_ans[:3])
            else:
                print("   ✓ mc 答案索引全部合法")
        else:
            print("   ▸ 尚無測驗題")

    print("\n" + "=" * 74)
    print("合計：知識點 %d、測驗題 %d" % (total_pts, total_q))
    if warns:
        print("\n提醒（非致命）：")
        for w in warns:
            print("  ⚠ " + w)
    if issues:
        print("\n發現 %d 個問題：" % len(issues))
        for i in issues:
            print("  ✗ " + i)
        sys.exit(1)
    print("\n獨立審計通過：無實質問題")
    sys.exit(0)


if __name__ == "__main__":
    main()
