# -*- coding: utf-8 -*-
"""題解覆蓋率報告 / 校驗器。

用法：
    python _expl_coverage.py            # 各課題覆蓋率 + 缺題清單
    python _expl_coverage.py --topic bio10   # 只看某課題缺哪幾題
    python _expl_coverage.py --check    # 校驗：JSON 合法性、必要欄位、題解過短/未標來源

寫題解的同學（人或代理）改完 _pastpaper.json 後，先跑這個確認沒漏、沒寫壞。
"""
import json, os, sys, collections

sys.stdout.reconfigure(encoding="utf-8")
BASE = os.path.dirname(os.path.abspath(__file__))
PP = os.path.join(os.path.dirname(BASE), "data", "bio", "_pastpaper.json")

# 課題名稱（與 data/bio/bioNN.json 的 title 對應）
TOPIC_NAME = {
    "bio02": "生命的基本單位", "bio03": "物質穿越細胞膜的活動", "bio04": "酶和新陳代謝",
    "bio05": "食物和人類", "bio06": "人的營養", "bio07": "人體的氣體交換",
    "bio08": "人體內物質的轉運", "bio09": "植物的營養和氣體交換",
    "bio10": "植物的蒸騰、轉運和支持", "bio11": "細胞週期和分裂",
    "bio12": "有花植物的生殖", "bio13": "人的生殖", "bio14": "生長和發育",
    "bio15": "環境狀況的探測", "bio16": "人體的協調", "bio17": "人體的運動",
    "bio18": "體內平衡", "bio19": "生態系", "bio20": "光合作用", "bio21": "呼吸作用",
    "bio22": "非傳染病", "bio23": "傳染病和疾病的預防", "bio24": "身體的防禦機制",
    "bio25": "基礎遺傳學", "bio26": "分子遺傳學", "bio27": "生物工程",
    "bio28": "生物多樣性", "bio29": "進化I", "bio30": "進化II",
    "bio32": "體溫調節", "bio33": "水份調節", "bio34": "血液內氣體成分的調節",
    "bio35": "生殖週期的激素控制", "bio36": "人類對環境的影響",
}

def load():
    return json.load(open(PP, encoding="utf-8"))

def main():
    args = sys.argv[1:]
    d = load()
    qs = [q for y in d["years"].values() for q in y]

    if "--check" in args:
        bad = []
        for q in qs:
            e = (q.get("explanation") or "").strip()
            if not e:
                continue
            if len(e) < 30:
                bad.append((q, "題解過短（<30 字）"))
            if not q.get("explSource"):
                bad.append((q, "缺 explSource 標記"))
            if q.get("qImg") and "見下圖" not in (q.get("q") or ""):
                bad.append((q, "整題圖但題幹無提示"))
        print(f"題解校驗：{len(qs)} 題，有題解 {sum(1 for q in qs if (q.get('explanation') or '').strip())} 題")
        if bad:
            print(f"\n⚠️ {len(bad)} 條可疑：")
            for q, why in bad[:40]:
                print(f"  {q['year']} Q{q['qnum']:<2} {why}")
        else:
            print("✅ 未發現問題")
        return

    topic = None
    if "--topic" in args:
        topic = args[args.index("--topic") + 1]

    by = collections.defaultdict(lambda: [0, 0])
    for q in qs:
        t = q.get("topic") or "?"
        by[t][1] += 1
        if (q.get("explanation") or "").strip():
            by[t][0] += 1

    total_done = sum(v[0] for v in by.values())
    total_all = sum(v[1] for v in by.values())
    print(f"全站題解：{total_done}/{total_all}（缺 {total_all - total_done}）\n")
    print(f"{'課題':<8}{'名稱':<22}{'有題解/總數':>12}   進度")
    for t in sorted(by):
        done, allq = by[t]
        if topic and t != topic:
            continue
        bar = "█" * int(done / allq * 10) if allq else ""
        mark = " ✅" if done == allq else ""
        print(f"{t:<8}{TOPIC_NAME.get(t, t):<22}{done:>4}/{allq:<4}   {bar:<10}{mark}")

    if topic:
        miss = [q for q in qs if q.get("topic") == topic and not (q.get("explanation") or "").strip()]
        print(f"\n{topic} 缺題解 {len(miss)} 題：")
        for q in sorted(miss, key=lambda x: (x["year"], x["qnum"])):
            flag = " [圖]" if (q.get("img") or q.get("optImg") or q.get("qImg")) else ""
            print(f"  {q['year']} Q{q['qnum']}{flag}  答案 {q['answer']}  答對率 {q['pct']}%")

if __name__ == "__main__":
    main()
