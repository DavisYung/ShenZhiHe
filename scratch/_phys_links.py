# -*- coding: utf-8 -*-
"""生成物理科跨课题知识串连 links.json。

串连的价值：让学习者从「热学」的任一概念跳到相关概念。
只连真实存在的知识点 id，且每条都写清楚「为什么相关」。
本脚本会校验两端 id 是否存在，避免死链接。

用字：串连标签会显示在知识图谱上，必须与全站一致——香港繁体。
"""
import io
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # f6chem/
DATA = os.path.join(BASE, "data", "phys")

# 手工编写的串连（语义相关，非机械）。标签用香港繁体，与全站一致。
LINKS = [
    # 溫度與內能
    ("heat1-s1-p1", "heat2-s1-p2", "溫度的微觀意義：分子平均動能"),
    ("heat1-s1-p2", "heat2-s1-p2", "溫度計測的是溫度，內能是另一回事"),
    # 溫標與物態
    ("heat1-s2-p2", "heat3-s1-p1", "0 °C 與 100 °C 正是水的熔點和沸點"),
    ("heat1-s1-p1", "heat3-s1-p2", "加熱曲線的平台對應物態變化"),
    # 內能與比熱容量
    ("heat2-s1-p2", "heat2-s2-p1", "內能變化用比熱容量計算"),
    ("heat2-s2-p1", "heat3-s1-p3", "潛熱與比熱容量都是能量的計算方式"),
    # 比熱容量與蒸發
    ("heat2-s2-p1", "heat3-s2-p3", "水的比熱容量大，蒸發冷卻效應才顯著"),
    ("heat2-s2-p1", "heat4-s2-p1", "對流靠流體受熱膨脹，與水的高比熱容量有關"),
    ("heat2-s2-p5", "heat4-s3-p4", "水的高比熱容量影響氣候與溫室效應"),
    # 物態與傳熱
    ("heat3-s1-p2", "heat4-s1-p1", "熔化和沸騰都需要持續供熱"),
    ("heat3-s1-p3", "heat4-s1-p4", "潛熱與傳導都涉及分子能量的傳遞"),
    ("heat3-s2-p3", "heat4-s3-p1", "蒸發冷卻與輻射都是能量散失方式"),
    # 傳熱三種方式互相關聯
    ("heat4-s1-p1", "heat4-s2-p1", "傳導靠粒子振動，對流靠流體整體移動"),
    ("heat4-s2-p1", "heat4-s3-p1", "對流需要介質，輻射不需要"),
    ("heat4-s1-p3", "heat4-s3-p3", "保溫瓶同時抑制傳導、對流和輻射"),
    ("heat4-s1-p4", "heat2-s1-p2", "傳導的微觀圖像就是分子動能的傳遞"),
    # 溫度計與傳熱
    ("heat1-s1-p2", "heat4-s1-p2", "溫度計和導熱都依賴物質的物性"),
    # 氣體與溫度／內能
    ("heat5-s1-p4", "heat1-s1-p1", "氣體定律裡的溫度必須用絕對溫度"),
    ("heat5-s2-p3", "heat2-s1-p2", "分子運動論正是內能的微觀基礎"),
    ("heat5-s2-p3", "heat1-s1-p1", "溫度的本質：分子平均動能的量度"),
    ("heat5-s2-p5", "heat5-s1-p3", "用分子運動論解釋波義耳定律"),
    ("heat5-s1-p6", "heat5-s1-p3", "理想氣體方程統合三個氣體定律"),
    ("heat5-s1-p4", "heat5-s1-p5", "氣壓定律與查理定律都用絕對溫度"),
    # 氣體與物態
    ("heat5-s1-p3", "heat3-s2-p1", "蒸發是分子逸出液面，與氣體壓強有關"),
    ("heat5-s2-p4", "heat2-s2-p1", "方均根速率與溫度的平方根成正比"),
    # ================= 力學（mech）=================
    # 力學內部：由淺入深的依賴鏈
    ("mech1-s1-p1", "mech2-s1-p1", "線圖的斜率就是 mech1 學的加速度與速度"),
    ("mech1-s1-p1", "mech2-s3-p1", "自由落體是勻加速運動的特例（a = g）"),
    ("mech2-s3-p1", "mech8-s1-p1", "平拋的豎直分量就是自由落體"),
    ("mech1-s1-p1", "mech8-s1-p1", "拋體分解：水平勻速 × 豎直落體"),
    ("mech3-s3-p1", "mech4-s2-p1", "牛二 F = ma 在平衡時退化為 ΣF = 0"),
    ("mech3-s4-p1", "mech4-s1-p1", "摩擦力的方向判斷要先畫隔離體圖"),
    ("mech3-s1-p1", "mech4-s1-p1", "隔離體圖是力的合成與分解的起點"),
    ("mech3-s3-p1", "mech5-s1-p1", "力的轉動效應（力矩）是牛二在轉動上的對應"),
    ("mech5-s2-p4", "mech4-s2-p1", "剛體平衡 = 平移平衡 + 轉動平衡，缺一不可"),
    ("mech6-s1-p1", "mech7-s1-p1", "功與能量 vs 動量：兩種守恆量的分工"),
    ("mech7-s1-p1", "mech6-s3-p5", "彈性碰撞：動量必守恆，動能也守恆"),
    ("mech7-s2-p3", "mech6-s4-p8", "衝力 F = Δp/Δt 本身就是動量定義的變形"),
    ("mech7-s2-p3", "mech6-s1-p1", "緩衝（安全帶）= 用更長的力程換更小的衝力"),
    ("mech6-s2-p3", "mech10-s1-p1", "重力勢能 E_p = mgh 是萬有引力勢能的近似"),
    ("mech9-s2-p1", "mech10-s2-p1", "引力圓周運動：萬有引力提供向心力"),
    ("mech9-s2-p1", "mech8-s2-p1", "斜拋最高點之後是曲線運動，可對照圓周思考"),
    ("mech6-s2-p3", "mech6-s3-p5", "動能與勢能互相轉換是能量守恆的具體形式"),
    # 力學 ↔ 熱學（跨分區串連）
    ("mech6-s1-p1", "heat2-s2-p1", "能量是兩區共用的概念：J 是功也是熱的單位"),
    ("mech1-s1-p1", "heat1-s1-p3", "測量與校準：長度時間和溫度計都靠定點與刻度"),
    ("mech3-s4-p1", "heat4-s1-p2", "摩擦生熱：摩擦力做功最終變為內能"),
]


def load(p):
    with io.open(p, encoding="utf-8") as f:
        return json.load(f)


def main():
    subj = load(os.path.join(DATA, "subject.json"))
    tids = subj.get("topics") or []

    all_ids = set()
    for tid in tids:
        p = os.path.join(DATA, tid + ".json")
        if not os.path.exists(p):
            continue
        t = load(p)
        for s in t.get("sections", []):
            for pt in s.get("points", []):
                if pt.get("id"):
                    all_ids.add(pt["id"])

    print("已存在的知識點 id 共 %d 個" % len(all_ids))

    ok, dropped = [], []
    for a, b, label in LINKS:
        if a in all_ids and b in all_ids:
            ok.append({"from": a, "to": b, "label": label})
        else:
            missing = [x for x in (a, b) if x not in all_ids]
            dropped.append((a, b, label, missing))

    op = os.path.join(DATA, "links.json")
    with io.open(op, "w", encoding="utf-8") as f:
        json.dump(ok, f, ensure_ascii=False, indent=1)
        f.write("\n")

    print("寫入串連 %d 條 → %s" % (len(ok), op))
    # 用字檢查：不得殘留異體字
    raw = io.open(op, encoding="utf-8").read()
    n_wen = raw.count("\u6e29")
    print("串連標籤「温」殘留：%d %s" % (n_wen, "✓" if n_wen == 0 else "✗"))
    if dropped:
        print("\n略過 %d 條（端點不存在）：" % len(dropped))
        for a, b, label, miss in dropped:
            print("  %s → %s  缺 %s  (%s)" % (a, b, miss, label))


if __name__ == "__main__":
    main()
