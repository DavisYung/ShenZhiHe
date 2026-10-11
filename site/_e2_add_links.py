# -*- coding: utf-8 -*-
"""为 atomic1/2/3 追加跨区串连（incremental，保留现有全部 links）。

设计：按「from/to 的课题前缀 + 主题关键词」定义候选，只有两端知识点都真实存在才写入。
可重复执行（已存在的 from+to 对不会重复加）。
"""
import io, json, os, sys

sys.stdout.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data", "phys")
LINKS = os.path.join(DATA, "links.json")

with io.open(LINKS, encoding="utf-8-sig") as f:
    links = json.load(f)

# 收集所有已存在的知识点 id
exist = set()
for n in os.listdir(DATA):
    if not n.endswith(".json"):
        continue
    stem = n[:-5]
    if stem in ("subject", "links", "index"):
        continue
    try:
        with io.open(os.path.join(DATA, n), encoding="utf-8-sig") as f:
            d = json.load(f)
    except Exception:
        continue
    for sec in d.get("sections", []) or []:
        for pt in sec.get("points", []) or []:
            if pt.get("id"):
                exist.add(pt["id"])

print(f"已存在知识点: {len(exist)}")

# 候选串连：(from, to, label)
# 主题：卢瑟福/原子结构 ↔ 电学原子结构；光电效应/光子 ↔ 波动学电磁波；
#       德布罗意/波粒二象性 ↔ 波动学衍射干涉；纳米/显微镜 ↔ 波动学瑞利判据；玻尔能级 ↔ 电磁波谱
CANDIDATES = [
    # ── 原子结构与电学 ──
    ("atomic1-s1-p1", "elec1-s1-p1", "散射實驗揭示的原子結構：原子核與電子"),
    ("atomic1-s1-p1", "nuclear2-s1-p1", "α 粒子散射 vs 原子核由質子中子組成"),
    ("atomic1-s1-p2", "elec1-s1-p1", "盧瑟福模型的局限：加速電子會輻射能量"),
    # ── 光电效应与波动学 ──
    ("atomic1-s2-p1", "wave6-s3-p1", "光電效應所需的光屬電磁波譜的哪一段"),
    ("atomic1-s2-p3", "wave6-s1-p1", "波動理論與光電效應的矛盾"),
    ("atomic1-s3-p1", "wave6-s3-p3", "光子能量 hf 與可見光的頻率"),
    ("atomic1-s3-p2", "wave6-s3-p4", "紫外輻射的頻率高於臨界頻率才能引發光電效應"),
    # ── 光谱与电磁波谱 ──
    ("atomic2-s1-p1", "wave6-s3-p1", "光譜線對應的頻率落在電磁波譜的位置"),
    ("atomic2-s1-p2", "elec1-s5-p1", "玻爾模型中的能級與電勢能"),
    ("atomic2-s1-p3", "wave6-s3-p4", "氫原子光譜線與紫外／可見光"),
    # ── 波粒二象性与波动学 ──
    ("atomic2-s2-p1", "wave6-s1-p3", "德布羅意波長與雙縫干涉"),
    ("atomic2-s2-p1", "wave6-s1-p1", "電子的衍射實驗證明物質波"),
    ("atomic2-s2-p2", "atomic2-s1-p2", "玻爾模型的駐波解釋"),
    # ── 纳米与波动学 ──
    ("atomic3-s2-p1", "wave6-s1-p1", "瑞利判據源於光的衍射"),
    ("atomic3-s2-p2", "atomic2-s2-p2", "電子顯微鏡利用電子的德布羅意波長"),
    ("atomic3-s1-p1", "atomic3-s2-p1", "納米尺度需用電子顯微鏡觀察"),
]

added = 0
skipped_missing = []
existing_pairs = {(l["from"], l["to"]) for l in links}

for f, t, label in CANDIDATES:
    if f not in exist or t not in exist:
        skipped_missing.append((f, t))
        continue
    if (f, t) in existing_pairs:
        continue
    links.append({"from": f, "to": t, "label": label})
    existing_pairs.add((f, t))
    added += 1

if skipped_missing:
    print(f"\n跳過 {len(skipped_missing)} 條（端點知識點不存在，可能是子代理命名不同）：")
    for f, t in skipped_missing:
        print(f"  {f} -> {t}")

print(f"\n新增 {added} 條串連，總數 {len(links)}")

if added:
    with io.open(LINKS, "w", encoding="utf-8") as f:
        json.dump(links, f, ensure_ascii=False, indent=4)
    print("已寫入 links.json")
else:
    print("無新增，未改動檔案")
