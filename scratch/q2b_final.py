import sys, json, os, collections
sys.stdout.reconfigure(encoding="utf-8")
BASE = r"C:\Users\guomi\OneDrive\文件\deepseek-harness\default-workspace\f6chem"
SCR = os.path.join(BASE, "scratch")

pool = []
for f in ["q2b_part_a.json", "q2b_part_b.json", "q2b_part_c.json"]:
    pool.extend(json.load(open(os.path.join(SCR, f), encoding="utf-8")))

# 21 sections x 2 questions; mc 25 / tf 9 / fill 8 -> mc 59.5%, tf 21.4%, fill 19.0%
KEEP = ["2b-q1","2b-q2","2b-q3","2b-q4","2b-q5","2b-q6","2b-q7","2b-q8",
        "2b-q9","2b-q10","2b-q12","2b-q13","2b-q14","2b-q16","2b-q17","2b-q18",
        "2b-q19","2b-q21","2b-q22","2b-q23","2b-q25","2b-q26","2b-q27","2b-q29",
        "2b-q30","2b-q31","2b-q32","2b-q33","2b-q36","2b-q38","2b-q39","2b-q40",
        "2b-q43","2b-q44","2b-q46","2b-q48","2b-q50","2b-q51","2b-q53","2b-q55",
        "2b-q56","2b-q57"]
bymap = {x["id"]: x for x in pool}
missing = [k for k in KEEP if k not in bymap]
assert not missing, missing

# Section-ordered so ids follow the notes; re-number only the id field.
def skey(qid):
    pid = bymap[qid]["point"]
    s, p = int(pid.split("-s")[1].split("-p")[0]), int(pid.split("-p")[1])
    return (s, p)
ordered = sorted(KEEP, key=skey)

out = []
for i, qid in enumerate(ordered, 1):
    q = dict(bymap[qid])          # shallow copy; body text never modified
    q["id"] = "2b-q%d" % i
    out.append(q)

doc = {"topic": "2b", "questions": out}
dst = os.path.join(BASE, "quiz", "2b.json")
with open(dst, "w", encoding="utf-8") as fh:
    json.dump(doc, fh, ensure_ascii=False, indent=1)

# ================= validation =================
errs = []
raw = open(dst, encoding="utf-8").read()
doc2 = json.load(open(dst, encoding="utf-8"))           # json.load must succeed
if doc2["topic"] != "2b": errs.append("topic")
qs = doc2["questions"]
if len(qs) != 42: errs.append("count=%d" % len(qs))

data = json.load(open(os.path.join(BASE, "data", "2b.json"), encoding="utf-8"))
allp = {p["id"]: p for s in data["sections"] for p in s["points"]}
secs = {s["id"] for s in data["sections"]}

ids, seen = [], set()
for i, q in enumerate(qs, 1):
    if q["id"] != "2b-q%d" % i: errs.append("id seq @%d %s" % (i, q["id"]))
    if q["id"] in seen: errs.append("dup id " + q["id"])
    seen.add(q["id"]); ids.append(q["id"])
    if q["point"] not in allp: errs.append("bad point %s" % q["point"])
    body = json.dumps(q, ensure_ascii=False)
    if "\ufffd" in body: errs.append("U+FFFD in " + q["id"])
    if "\ufffd" in raw: errs.append("U+FFFD in file")
    if not q.get("q") or not q.get("explanation"): errs.append("empty " + q["id"])
    t = q["type"]
    if t == "mc":
        if len(q.get("options", [])) != 4: errs.append("opts " + q["id"])
        if not isinstance(q["answer"], int) or not 0 <= q["answer"] <= 3:
            errs.append("mc ans " + q["id"])
        if len(set(q["options"])) != 4: errs.append("dup opts " + q["id"])
    elif t == "tf":
        if not isinstance(q["answer"], bool): errs.append("tf ans " + q["id"])
    elif t == "fill":
        a = q["answer"]
        if isinstance(a, str): a = [a]
        if not isinstance(a, list) or not a or not all(isinstance(x, str) and x.strip() for x in a):
            errs.append("fill ans " + q["id"])
        if "____" not in q["q"]: errs.append("fill no blank " + q["id"])
    else:
        errs.append("type " + q["id"])
    if "OCR 不清" in q["q"]: errs.append("OCR in q " + q["id"])

cnt = collections.Counter(q["type"] for q in qs)
tf_false = sum(1 for q in qs if q["type"] == "tf" and q["answer"] is False)
covered = {q["point"].rsplit("-p", 1)[0] for q in qs}
mc_ans = collections.Counter(q["answer"] for q in qs if q["type"] == "mc")
pts = {q["point"] for q in qs}

print("VALIDATION:", "PASS - no errors" if not errs else errs)
print("n_questions:", len(qs), dict(cnt))
print("pct mc=%.1f%% tf=%.1f%% fill=%.1f%%" % (
    100*cnt["mc"]/len(qs), 100*cnt["tf"]/len(qs), 100*cnt["fill"]/len(qs)))
print("tf false:", tf_false, "/ true:", cnt["tf"]-tf_false)
print("sections covered: %d/%d" % (len(covered), len(secs)))
print("distinct points used: %d/%d" % (len(pts), len(allp)))
print("mc answer distribution:", dict(sorted(mc_ans.items())))
print("U+FFFD count:", raw.count("\ufffd"))
print("bytes:", len(raw.encode("utf-8")))