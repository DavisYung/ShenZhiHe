# -*- coding: utf-8 -*-
"""物理内容校验：结构、字段、图片引用、用字一致性。

用法: python _phys_check.py            # 校验全部 phys 课题
      python _phys_check.py heat1      # 只校验指定课题
"""
import io
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _phys_norm import check_variants  # noqa: E402

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # f6chem/
DATA = os.path.join(BASE, "data", "phys")
QUIZ = os.path.join(BASE, "quiz", "phys")
IMG = os.path.join(BASE, "site", "img")

results = []


def check(name, ok, detail=""):
    results.append((name, ok, detail))
    print(("  PASS  " if ok else "  FAIL  ") + name + (("   " + detail) if detail else ""))


def load(p):
    with io.open(p, encoding="utf-8") as f:
        return json.load(f)


def main():
    only = sys.argv[1] if len(sys.argv) > 1 else None
    subj = load(os.path.join(DATA, "subject.json"))
    tids = list(subj.get("topics") or [])
    # 支援校驗「尚未登記進 subject.json」的課題：
    #   python _phys_check.py heat3        → 即使 subject.json 沒列也能校驗
    # 這樣多個並行任務就不必同時改 subject.json（避免寫衝突）。
    if only:
        tids = [only]
    elif not tids:
        # 沒有任何登記時，掃描資料夾
        tids = sorted(n[:-5] for n in os.listdir(DATA)
                      if n.endswith(".json") and n not in ("subject.json", "links.json"))

    if not tids:
        print("沒有要檢查的課題（subject.json 的 topics 為空？）")
        return

    all_pids = set()
    for tid in tids:
        p = os.path.join(DATA, tid + ".json")
        print("\n[%s] %s" % (tid, os.path.basename(p)))
        if not os.path.exists(p):
            check("%s.json 存在" % tid, False)
            continue
        t = load(p)
        check("id 正確", t.get("id") == tid, "id=%s" % t.get("id"))
        check("有 title", bool(t.get("title")))
        check("有 pdf 來源", bool(t.get("pdf")))
        secs = t.get("sections") or []
        check("有章節", len(secs) > 0, "%d 章" % len(secs))

        for s in secs:
            sid = s.get("id", "?")
            check("%s 章節 id/title" % sid, bool(sid) and bool(s.get("title")))
            pts = s.get("points") or []
            if not pts:
                check("%s 有知識點" % sid, False)
            for pt in pts:
                pid = pt.get("id", "?")
                # 逐點檢查：把該點的所有問題收集起來，最後只報一行結論。
                # （先前寫法只在失敗時打印，成功時看不到 PASS，
                #   導致「通過 N 項」可能掩蓋逐點問題——現改為每點都出結論。）
                probs = []
                if pid in all_pids:
                    probs.append("id 重複")
                all_pids.add(pid)
                if not pt.get("title"):
                    probs.append("缺 title")
                if not isinstance(pt.get("page"), int):
                    probs.append("page 非整數(%r)" % pt.get("page"))
                body = pt.get("body") or ""
                if not body.strip():
                    probs.append("缺 body")
                bad = check_variants(body) or check_variants(pt.get("title") or "")
                if bad:
                    probs.append("殘留異體字 %s" % bad)
                for m in re.finditer(r"!\[[^\]]*\]\((img/[^)\s]+)\)", body):
                    rel = m.group(1)[4:]
                    if not os.path.exists(os.path.join(IMG, rel)):
                        probs.append("圖片缺失 %s" % rel)
                if re.search(r"_{3,}", body):
                    probs.append("殘留填空 ____")
                if "\ufffd" in body:
                    probs.append("含亂碼 U+FFFD")
                n_img = len(re.findall(r"!\[[^\]]*\]\(img/", body))
                check("  %-16s p%-3s 圖%d" % (pid, pt.get("page"), n_img),
                      not probs, "；".join(probs))

        # 測驗題
        qp = os.path.join(QUIZ, tid + ".json")
        if os.path.exists(qp):
            q = load(qp)
            qs = q.get("questions") or []
            pids = {pt["id"] for s in secs for pt in (s.get("points") or []) if pt.get("id")}
            for x in qs:
                qid = x.get("id", "?")
                if x.get("point") and x["point"] not in pids:
                    check("%s 指向存在的知識點" % qid, False, "point=%s" % x["point"])
                if x.get("type") == "mc":
                    if not isinstance(x.get("options"), list) or len(x.get("options") or []) < 2:
                        check("%s 選項完整" % qid, False)
                    if not isinstance(x.get("answer"), int):
                        check("%s answer 是索引" % qid, False)
                elif x.get("type") == "tf":
                    if not isinstance(x.get("answer"), bool):
                        check("%s answer 是布林" % qid, False)
                if "\ufffd" in (x.get("q") or "") or "\ufffd" in (x.get("explanation") or ""):
                    check("%s 無亂碼" % qid, False)

    print("\n" + "=" * 62)
    ok = sum(1 for _, o, _ in results if o)
    print("檢查 %d 項，通過 %d 項" % (len(results), ok))
    if ok != len(results):
        print("\n失敗項：")
        for n, o, d in results:
            if not o:
                print("  - %s  %s" % (n, d))
        sys.exit(1)
    print("全部通過")
    sys.exit(0)


if __name__ == "__main__":
    main()
