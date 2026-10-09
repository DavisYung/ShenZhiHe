import sys, json, os, collections
sys.stdout.reconfigure(encoding="utf-8")
BASE = r"C:\Users\guomi\OneDrive\文件\deepseek-harness\default-workspace\f6chem"
DST = os.path.join(BASE, "quiz", "2b.json")
doc = json.load(open(DST, encoding="utf-8"))
qs = doc["questions"]
byp = {q["point"]: q for q in qs}

# ---------- 1) rebalance tf: convert 3 True statements into False ones ----------
byq = {q["point"]: q for q in qs}

q = byq["2b-s1-p2"]            # was True
q["q"] = "在六種常用電池中，鉛酸蓄電池的最高電壓與鋅碳電池相同，都是 1.5 V。"
q["answer"] = False
q["explanation"] = ("鉛酸蓄電池的最高電壓是 2 V，比鋅碳、鹼性錳和氧化銀的 1.5 V 高，"
                    "但遠低於鋰離子電池的 3.7 V，也高於鎳金屬氫化物的 1.2 V，故陳述錯誤。")

q = byq["2b-s13-p3"]
q["q"] = "在 Mg/Cu 化學電池中，電子由正電極（Cu）經外電路流向負電極（Mg）。"
q["answer"] = False
q["explanation"] = ("Mg 失電子成為陽極（負電極），電子是由負電極（Mg）經外電路流向正電極（Cu）；"
                    "鹽橋中 NO₃⁻ 移向陽極室、K⁺ 移向陰極室以維持兩邊電中性。電子流向剛好相反，故陳述錯誤。")

q = byq["2b-s15-p2"]
q["q"] = "在含惰性電極的電池中，判斷陰陽極的第一步是觀察兩片電極所用的物料。"
q["answer"] = False
q["explanation"] = ("惰性電極（碳或鉑）本身不參與反應，所以第一步應先列出每個燒杯所含的離子"
                    "（Fe²⁺、SO₄²⁻／K⁺、MnO₄⁻、H⁺），再據此判斷哪個離子被氧化（Fe²⁺→Fe³⁺，陽極）"
                    "哪個被還原（MnO₄⁻→Mn²⁺，陰極），故陳述錯誤。")

q = byq["2b-s17-p1"]
q["q"] = "電解是自發的放電反應，其能量轉換與化學電池相同，都是化學能轉為電能。"
q["answer"] = False
q["explanation"] = ("電解必須外加電源強迫進行非自發反應，把電能轉換為化學能（把化學能儲存在產物中）；"
                    "化學電池才是自發的放電反應，把化學能轉為電能。兩者剛好相反，故陳述錯誤。")

# fill answer tidy-up (avoid ungrammatical alt)
byq["2b-s18-p3"]["answer"] = ["高"]

# ---------- 2) rebalance mc answer positions by rotating the options array ONLY ----------
ROT = {                       # point -> rotation (old index -> new index)
    "2b-s8-p1":  1,          # ans 1 -> 2
    "2b-s10-p1": 1,          # ans 1 -> 2
    "2b-s18-p2": 1,          # ans 1 -> 2
    "2b-s14-p2": 2,          # ans 1 -> 3
    "2b-s17-p2": 2,          # ans 1 -> 3
    "2b-s21-p2": 3,          # ans 0 -> 3
}
for pid, k in ROT.items():
    q = byq[pid]
    n = len(q["options"])
    k %= n
    new_ans = (q["answer"] + k) % n
    # rotate RIGHT by k:  new_options[(i+k) % n] = options[i]
    q["options"] = [q["options"][(i - k) % n] for i in range(n)]
    q["answer"] = new_ans
    # q / explanation text is NOT touched

# ---------- 3) sort by section then renumber ----------
qs.sort(key=lambda q: (int(q["point"].split("-s")[1].split("-p")[0]),
                        int(q["point"].split("-p")[1])))
for i, q in enumerate(qs, 1):
    q["id"] = "2b-q%d" % i
doc["questions"] = qs

with open(DST, "w", encoding="utf-8") as fh:
    json.dump(doc, fh, ensure_ascii=False, indent=1)

# ================= validation =================
errs = []
raw = open(DST, encoding="utf-8").read()
doc2 = json.load(open(DST, encoding="utf-8"))
assert doc2["topic"] == "2b"
qs = doc2["questions"]
data = json.load(open(os.path.join(BASE, "data", "2b.json"), encoding="utf-8"))
allp = {p["id"] for s in data["sections"] for p in s["points"]}
secs = {s["id"] for s in data["sections"]}
if len(qs) != 42: errs.append("count")

seen = set()
for i, q in enumerate(qs, 1):
    if q["id"] != "2b-q%d" % i: errs.append("seq @%d %s" % (i, q["id"]))
    if q["id"] in seen: errs.append("dup " + q["id"])
    seen.add(q["id"])
    if q["point"] not in allp: errs.append("bad point " + q["point"])
    blob = json.dumps(q, ensure_ascii=False)
    if "\ufffd" in blob: errs.append("U+FFFD " + q["id"])
    if not q["q"] or not q["explanation"]: errs.append("empty " + q["id"])
    t = q["type"]
    if t == "mc":
        if len(q["options"]) != 4: errs.append("opts " + q["id"])
        if not isinstance(q["answer"], int) or not 0 <= q["answer"] <= 3: errs.append("mc ans " + q["id"])
        if len(set(q["options"])) != 4: errs.append("dup opt " + q["id"])
    elif t == "tf":
        if not isinstance(q["answer"], bool): errs.append("tf ans " + q["id"])
    elif t == "fill":
        a = q["answer"] if isinstance(q["answer"], list) else [q["answer"]]
        if not a or not all(isinstance(x, str) and x.strip() for x in a): errs.append("fill ans " + q["id"])
        if "____" not in q["q"]: errs.append("fill blank " + q["id"])
    else: errs.append("type " + q["id"])
    if "OCR 不清" in q["q"]: errs.append("OCR " + q["id"])
if "\ufffd" in raw: errs.append("U+FFFD in file")

cnt = collections.Counter(q["type"] for q in qs)
tff = sum(1 for q in qs if q["type"]=="tf" and q["answer"] is False)
cov = {q["point"].rsplit("-p",1)[0] for q in qs}
mc_ans = collections.Counter(q["answer"] for q in qs if q["type"]=="mc")
print("VALIDATION:", "PASS - no errors" if not errs else errs)
print("n:", len(qs), dict(cnt), "| mc=%.1f%% tf=%.1f%% fill=%.1f%%" % (
    100*cnt["mc"]/len(qs), 100*cnt["tf"]/len(qs), 100*cnt["fill"]/len(qs)))
print("tf: false=%d true=%d" % (tff, cnt["tf"]-tff))
print("sections %d/%d | points %d/%d" % (len(cov), len(secs), len({q["point"] for q in qs}), len(allp)))
print("mc answer dist:", dict(sorted(mc_ans.items())))
print("U+FFFD:", raw.count("\ufffd"), "| bytes:", len(raw.encode("utf-8")))