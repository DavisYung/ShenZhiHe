# -*- coding: utf-8 -*-
import json, os

BASE = r"C:\Users\guomi\OneDrive\文件\deepseek-harness\default-workspace\f6chem"
DATA = os.path.join(BASE, "data", "3a.json")
OUT = os.path.join(BASE, "quiz", "3a.json")

questions = [
    # ---- s1 化石燃料與石油 ----
    {"id": "3a-q1", "type": "mc", "point": "3a-s1-p3",
     "q": "關於石油（原油）的成分，下列哪項正確？",
     "options": ["石油是單一化合物",
                 "石油主要是烴的混合物，並含小量硫、氧、氮",
                 "石油的主要成分是甲烷",
                 "石油是無色無味的液體"],
     "answer": 1,
     "explanation": "石油是由多種化合物組成的混合物，主要含烴（只由碳及氫組成），並含小量 S、O、N；外觀為粘滯惡臭的黑色液體。甲烷是天然氣的主要成分，不是石油。"},
    {"id": "3a-q2", "type": "tf", "point": "3a-s1-p1",
     "q": "煤是由海洋生物和植物遺骸經長時間的熱力、壓力和細菌作用而形成。",
     "answer": False,
     "explanation": "煤由植物遺骸形成；石油（原油）才是由海洋生物和植物遺骸形成。"},
    # ---- s2 石油分餾 ----
    {"id": "3a-q3", "type": "mc", "point": "3a-s2-p1",
     "q": "石油分餾（精煉）能把石油分成多個餾分，主要是利用各成分的什麼差異？",
     "options": ["密度", "沸點", "溶解度", "化學反應性"],
     "answer": 1,
     "explanation": "石油中各碳氫化合物有不同沸點，加熱後蒸氣在分餾塔不同溫度的塔盤冷凝成不同餾分。分餾屬物理變化，不是化學反應。"},
    {"id": "3a-q4", "type": "fill", "point": "3a-s2-p2",
     "q": "工業分餾石油時，石油以____°C 進入熔爐加熱後送入分餾塔。",
     "answer": ["400"],
     "explanation": "石油以 400°C 進入熔爐加熱，再送入分餾塔；塔內溫度由下而上遞減，蒸氣在不同塔盤冷凝成不同餾分。"},
    # ---- s3 燃燒與溫室氣體 ----
    {"id": "3a-q5", "type": "mc", "point": "3a-s3-p1",
     "q": "烴完全燃燒的通式為 CₓHᵧ(g) + (x + y/4)O₂(g) → xCO₂(g) + y/2H₂O(l)。下列哪個方程式符合此通式？",
     "options": ["C₄H₈(g) + 6O₂(g) → 4CO₂(g) + 4H₂O(l)",
                 "C₄H₈(g) + 4O₂(g) → 4CO₂(g) + 4H₂O(l)",
                 "C₄H₈(g) + 6O₂(g) → 4CO(g) + 4H₂O(l)",
                 "C₄H₈(g) + 8O₂(g) → 4CO₂(g) + 4H₂O(l)"],
     "answer": 0,
     "explanation": "代入 x=4、y=8：O₂ 係數 = 4 + 8/4 = 6，CO₂ = 4，H₂O = 8/2 = 4。B 氧氣不足，C 生成 CO 屬不完全燃燒，D 氧氣過多。"},
    {"id": "3a-q6", "type": "tf", "point": "3a-s3-p3",
     "q": "二氧化碳（CO₂）是一種空氣污染物。",
     "answer": False,
     "explanation": "CO₂ 不是空氣污染物，它只造成溫室效應；教師紅字特別強調這一點。"},
    # ---- s4 空氣污染物與酸雨 ----
    {"id": "3a-q7", "type": "mc", "point": "3a-s4-p2",
     "q": "關於酸雨的形成，下列哪項正確？",
     "options": ["CO₂ 溶於雨水是酸雨的主要成因",
                 "氮氧化物與二氧化硫溶於雨水形成酸雨",
                 "酸雨是由氧氣與水反應形成",
                 "酸雨與空氣污染物無關"],
     "answer": 1,
     "explanation": "2NO₂(g) + H₂O(l) → HNO₃(aq) + HNO₂(aq)；SO₂(g) + H₂O(l) ⇌ H₂SO₃(aq)。CO₂ 正常溶於水屬雨水本來的弱酸性，不算酸雨。"},
    {"id": "3a-q8", "type": "tf", "point": "3a-s4-p1",
     "q": "行雷也能導致氮氧化物（NOx）的形成。",
     "answer": True,
     "explanation": "高溫（如行雷）令空氣中的氮和氧反應：N₂(g) + O₂(g) → 2NO(g)，2NO(g) + O₂(g) → 2NO₂(g)。"},
    # ---- s5 分子表示與官能基 ----
    {"id": "3a-q9", "type": "mc", "point": "3a-s5-p3",
     "q": "下列哪個化合物不屬於有機化合物？",
     "options": ["辛烷 C₈H₁₈", "二氧化碳 CO₂", "乙醇 C₂H₅OH", "甲烷 CH₄"],
     "answer": 1,
     "explanation": "有機化合物指所有含碳的化合物，但不包括碳的氧化物（CO、CO₂）、碳酸（氫）鹽（CO₃²⁻、HCO₃⁻）和氰化物（CN⁻）三類例外。"},
    {"id": "3a-q10", "type": "fill", "point": "3a-s5-p2",
     "q": "乙醇（CH₃CH₂OH）的官能基為____。",
     "answer": ["-OH", "羥基"],
     "explanation": "乙醇的官能基是羥基（-OH）；官能基決定化合物大部份性質，帶 -OH 者可與水形成氫鍵，沸點較高。"},
    # ---- s6 常見塑膠 ----
    {"id": "3a-q11", "type": "mc", "point": "3a-s6-p3",
     "q": "關於熱塑性與熱固性塑膠的比較，下列哪項正確？",
     "options": ["熱固性塑膠受熱可反覆軟化",
                 "熱塑性塑膠分子間只有微弱的范德華引力，受熱軟化",
                 "熱塑性塑膠有強的共價交鍵",
                 "兩者受熱後的行為沒有分別"],
     "answer": 1,
     "explanation": "熱塑性塑膠分子間只有微弱的范德華引力，受熱軟化、冷後硬化，可反覆進行；熱固性塑膠有強的共價交鍵，第一次模塑即永久定型。"},
    {"id": "3a-q12", "type": "tf", "point": "3a-s6-p3",
     "q": "熱固性塑膠可加熱重新軟化並再次模塑。",
     "answer": False,
     "explanation": "熱固性塑膠第一次模塑時即永久定型，之後硬、不能再軟化；能反覆加熱軟化的是熱塑性塑膠。"},
    # ---- s7 命名 ----
    {"id": "3a-q13", "type": "mc", "point": "3a-s7-p2",
     "q": "根據 IUPAC 命名法則，下列哪項描述正確？",
     "options": ["選最短的碳鏈為主鏈",
                 "分支的編號取最大的數字",
                 "選最長連續碳鏈為主鏈，分支編號取最小數字",
                 "分支名稱放在主鏈名稱之後"],
     "answer": 2,
     "explanation": "IUPAC 法則：(i) 選最長連續碳鏈為主鏈；(ii) 分支編號取最小數字，數字後加「-」。例如 2-甲基丁烷即主鏈 4 個碳、甲基在 2 號位。"},
    {"id": "3a-q14", "type": "fill", "point": "3a-s7-p1",
     "q": "直鏈烷烴 CH₃CH₂CH₂CH₃ 的 IUPAC 名稱為____。",
     "answer": ["丁烷"],
     "explanation": "碳數目 4 對應中文字碼「丁」，直鏈飽和烷烴命名即為丁烷。"},
    # ---- s8 烷烴性質 ----
    {"id": "3a-q15", "type": "mc", "point": "3a-s8-p3",
     "q": "關於烷烴的化學性質，下列哪項正確？",
     "options": ["烷烴可與酸和氧化劑反應",
                 "烷烴化學性質不活潑，不與酸、氧化劑、還原劑反應",
                 "烷烴容易與溴水反應",
                 "烷烴可與高錳酸鉀反應"],
     "answer": 1,
     "explanation": "烷烴是飽和烴，化學性質不活潑（化學惰性），不會與酸、氧化劑、還原劑反應；這與烯烴（含 C=C）的活潑性質不同。"},
    {"id": "3a-q16", "type": "mc", "point": "3a-s8-p2",
     "q": "關於烷烴的物理性質，下列哪項正確？",
     "options": ["沸點隨碳原子數目增加而下降",
                 "C₁ 至 C₄ 的烷烴在常溫下為液體",
                 "烷烴密度高於空氣",
                 "烷烴不溶於水，但可溶於有機溶劑"],
     "answer": 3,
     "explanation": "烷烴沸點隨碳數增加而升高；C₁–C₄ 為氣體；密度低於空氣；不溶於水、溶於有機溶劑。"},
    # ---- s9 取代與裂解 ----
    {"id": "3a-q17", "type": "mc", "point": "3a-s9-p1",
     "q": "甲烷與氯氣發生取代反應生成氯甲烷，需要什麼條件？",
     "options": ["紫外光或 300°C", "黑暗常溫", "高壓", "濃硫酸催化"],
     "answer": 0,
     "explanation": "CH₄(g) + Cl₂(g) →[紫外光／300°C] CH₃Cl(g) + HCl(g)；自由基取代的引發步驟（Cl–Cl → 2Cl·）需要熱或紫外光，不能在常溫黑暗中進行。"},
    {"id": "3a-q18", "type": "mc", "point": "3a-s9-p3",
     "q": "關於裂解作用，下列哪項正確？",
     "options": ["裂解在無空氣環境下進行，把大烴分子分裂成小烴分子",
                 "裂解是放熱反應",
                 "裂解只生成烷烴",
                 "裂解不需要催化劑"],
     "answer": 0,
     "explanation": "裂解（ΔH > 0，吸熱）在無空氣環境下把大烴分子分裂成小烴分子，可生產額外汽油並製造烯烴；實驗以碎素瓷片／Al₂O₃ 作催化劑。"},
    # ---- s10 烯烴 ----
    {"id": "3a-q19", "type": "mc", "point": "3a-s10-p2",
     "q": "乙烯與溴溶液（在有機溶劑中）反應，觀察到什麼現象？",
     "options": ["橙色溴溶液變成無色",
                 "無色溶液變成橙色",
                 "產生白色沉澱",
                 "沒有變化"],
     "answer": 0,
     "explanation": "乙烯 + Br₂ → 1,2-二溴乙烷，溴（橙色）變成產物（無色）；這是加成反應，也是檢驗不飽和烴的方法。"},
    {"id": "3a-q20", "type": "mc", "point": "3a-s10-p3",
     "q": "乙烯與冷的酸化稀高錳酸鉀溶液反應，觀察到什麼現象？",
     "options": ["紫色溶液變成無色",
                 "無色溶液變成紫色",
                 "產生橙色沉澱",
                 "溶液變綠色"],
     "answer": 0,
     "explanation": "乙烯被氧化成 1,2-乙二醇，KMnO₄（紫色）變成無色；這是氧化反應，同樣用於檢驗烯烴。"},
    # ---- s11 烷醇 ----
    {"id": "3a-q21", "type": "mc", "point": "3a-s11-p4",
     "q": "用 K₂Cr₂O₇/H⁺ 氧化乙醇時，觀察到什麼顏色變化？",
     "options": ["橙色變成綠色", "綠色變成橙色", "紫色變成無色", "無色變成橙色"],
     "answer": 0,
     "explanation": "K₂Cr₂O₇（橙色，Cr⁶⁺）被還原成 Cr³⁺（綠色）；這顏色變化是酒精測試（呼氣分析儀）的原理。"},
    {"id": "3a-q22", "type": "fill", "point": "3a-s11-p1",
     "q": "烷醇的通式為____。",
     "answer": ["CₙH₂ₙ₊₁OH", "CnH2n+1OH", "ROH"],
     "explanation": "烷醇通式 CₙH₂ₙ₊₁OH（ROH，n = 1, 2, 3…），可看成烷烴的一個 H 被羥基（-OH）取代。"},
    # ---- s12 酯化 ----
    {"id": "3a-q23", "type": "mc", "point": "3a-s12-p1",
     "q": "關於酯化作用，下列哪項正確？",
     "options": ["酯化是不可逆反應",
                 "酯化需要濃硫酸作催化劑並回流加熱",
                 "酯化不需要催化劑",
                 "酯化反應中醇被氧化成酸"],
     "answer": 1,
     "explanation": "酸 + 醇 ⇌ 酯 + 水，濃 H₂SO₄ 作催化劑並回流加熱；酯化是可逆反應，濃硫酸同時起催化與吸水作用，有助平衡向生成酯的方向移動。"},
    {"id": "3a-q24", "type": "fill", "point": "3a-s12-p1",
     "q": "酯化反應中，濃硫酸的作用是____。",
     "answer": ["催化劑及吸水劑", "催化劑和吸水劑", "催化及吸水"],
     "explanation": "濃硫酸在酯化反應中同時起催化劑與吸水劑作用，吸收生成的水，有助平衡向生成酯的方向移動。"},
    # ---- s13 加成聚合 ----
    {"id": "3a-q25", "type": "mc", "point": "3a-s13-p1",
     "q": "關於加成聚合作用，下列哪項正確？",
     "options": ["單體必定是飽和的",
                 "加成聚合沒有細小分子產生",
                 "加成聚合有小分子（如 H₂O）消去",
                 "聚合物與單體的原子成分不同"],
     "answer": 1,
     "explanation": "加成聚合的單體必定不飽和（含 C=C）；反應中沒有細小分子產生，聚合物與單體分子的原子成分相同（原子經濟率 100%）。有小分子消去的是縮合聚合。"},
    {"id": "3a-q26", "type": "tf", "point": "3a-s13-p3",
     "q": "加成聚合作用沒有細小分子產生。",
     "answer": True,
     "explanation": "加成聚合中單體的原子全部進入聚合物，沒有小分子消去；有小分子（如 H₂O、HCl）消去的是縮合聚合。"},
    # ---- s14 縮合聚合 ----
    {"id": "3a-q27", "type": "mc", "point": "3a-s14-p2",
     "q": "聚對苯二甲酸乙二酯（PET）是由哪兩種單體縮合而成？",
     "options": ["對苯二甲酸 + 乙二醇",
                 "己二酸 + 己-1,6-二胺",
                 "乙烯 + 丙烯",
                 "氯乙烯 + 苯乙烯"],
     "answer": 0,
     "explanation": "PET 由對苯二甲酸與乙二醇縮合生成，鍵合方式為酯鍵合（酸 + 醇）；B 是尼龍-6,6 的單體。"},
    {"id": "3a-q28", "type": "fill", "point": "3a-s14-p3",
     "q": "尼龍-6,6 由己-1,6-二胺與____縮合而成。",
     "answer": ["己二酸"],
     "explanation": "尼龍-6,6 由己-1,6-二胺（6 個碳）與己二酸（6 個碳）縮合生成，鍵合方式為醯胺鍵合（酸 + 胺）；名字「6,6」代表二胺和二酸各有 6 個碳。"},
    # ---- s15 脲甲醛 ----
    {"id": "3a-q29", "type": "mc", "point": "3a-s15-p3",
     "q": "熱固性塑膠（如脲甲醛）不熔不軟化的根本原因是什麼？",
     "options": ["分子間只有范德華引力",
                 "長鏈之間有強的共價交鍵（交聯）形成三維網狀結構",
                 "分子間有氫鍵",
                 "分子鏈太短"],
     "answer": 1,
     "explanation": "熱固性塑膠的長鏈之間以共價交鍵（如 –CH₂– 橋鍵）交連成三維網狀結構，破壞共價鍵需高能量，故不熔不軟化；這與熱塑性（范德華引力）的分野。"},
    {"id": "3a-q30", "type": "tf", "point": "3a-s15-p1",
     "q": "脲甲醛是一種熱塑性塑膠。",
     "answer": False,
     "explanation": "脲甲醛（尿素 + 甲醛在酸性條件縮合）是典型的熱固性塑膠，第一次模塑即永久定型。"},
    # ---- s16 塑膠廢物與總結 ----
    {"id": "3a-q31", "type": "mc", "point": "3a-s16-p1",
     "q": "焚化聚氯乙烯（PVC）廢料會產生什麼有毒氣體？",
     "options": ["二噁英和 HCl", "CO₂ 和 H₂O", "O₂ 和 N₂", "CH₄ 和 NH₃"],
     "answer": 0,
     "explanation": "燒 PVC 會產生二噁英和 HCl；燒尼龍會產生 HCN、NO、NO₂。焚化的優點是可把廢料轉化成能量。"},
    {"id": "3a-q32", "type": "tf", "point": "3a-s16-p2",
     "q": "烷烴與氯氣在光照（hv）下發生加成反應。",
     "answer": False,
     "explanation": "烷烴與 Cl₂ 在光照下發生的是取代反應（生成氯化烷混合物）；加成反應是烯烴與 Br₂（CCl₄）的反應，用於檢驗烯。"},
]

# ---- validation ----
data = json.load(open(DATA, encoding="utf-8"))
valid_points = set()
for s in data["sections"]:
    for pt in s["points"]:
        valid_points.add(pt["id"])

errors = []
ids = [q["id"] for q in questions]
if len(ids) != len(set(ids)):
    errors.append("duplicate ids")
for i, q in enumerate(questions, 1):
    if q["id"] != f"3a-q{i}":
        errors.append(f"id sequence break at {i}: {q['id']}")
    if q["point"] not in valid_points:
        errors.append(f"{q['id']}: point {q['point']} not found")
    if q["type"] == "mc":
        if not (isinstance(q["answer"], int) and 0 <= q["answer"] < len(q["options"])):
            errors.append(f"{q['id']}: bad mc answer index")
        if len(q["options"]) != 4:
            errors.append(f"{q['id']}: mc options != 4")
    elif q["type"] == "tf":
        if not isinstance(q["answer"], bool):
            errors.append(f"{q['id']}: tf answer not bool")
    elif q["type"] == "fill":
        if not (isinstance(q["answer"], (str, list)) and len(q["answer"]) > 0):
            errors.append(f"{q['id']}: fill answer empty")
        if "____" not in q["q"]:
            errors.append(f"{q['id']}: fill question missing ____")

sections_covered = set()
for q in questions:
    sections_covered.add(q["point"].rsplit("-p", 1)[0])
all_sections = {s["id"] for s in data["sections"]}
missing_secs = all_sections - sections_covered
if missing_secs:
    errors.append(f"sections not covered: {missing_secs}")

from collections import Counter
tc = Counter(q["type"] for q in questions)
tf_false = sum(1 for q in questions if q["type"] == "tf" and q["answer"] is False)
tf_true = sum(1 for q in questions if q["type"] == "tf" and q["answer"] is True)

print("TOTAL:", len(questions))
print("TYPE COUNTS:", dict(tc))
print("TF true/false:", tf_true, "/", tf_false)
print("SECTIONS COVERED:", len(sections_covered), "/", len(all_sections))
print("ERRORS:", errors if errors else "NONE")

if not errors:
    out = {"topic": "3a", "questions": questions}
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    # re-load to verify
    chk = json.load(open(OUT, encoding="utf-8"))
    assert chk["topic"] == "3a" and len(chk["questions"]) == len(questions)
    print("WROTE:", OUT, os.path.getsize(OUT), "bytes")
else:
    print("NOT WRITTEN due to errors")
