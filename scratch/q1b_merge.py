import json, sys, os, collections
sys.stdout.reconfigure(encoding="utf-8")

BASE = r"D:\deepseek-harness\default-workspace\f6chem"
DATA = os.path.join(BASE, "data", "1b.json")
OUTDIR = os.path.join(BASE, "quiz")
OUT = os.path.join(OUTDIR, "1b.json")

raw = []
for f in ("part_a.json", "part_b.json"):
    raw += json.load(open(os.path.join(BASE, "scratch", f), encoding="utf-8"))
raw.sort(key=lambda x: x["n"])

L = "ABCD"
def build(r):
    q = {"id": "1b-q%d" % r["n"], "type": r["type"], "point": r["point"], "q": r["q"]}
    if r["type"] == "mc":
        n4 = len(r["options"])
        k = r["n"] % n4                       # rotate options right by k
        new_opts = [r["options"][(j - k) % n4] for j in range(n4)]
        q["options"] = new_opts
        q["answer"] = (r["answer"] + k) % n4
    elif r["type"] == "tf":
        q["answer"] = r["answer"]
    else:
        q["answer"] = r["answer"]
    q["explanation"] = r["explanation"]
    return q

questions = [build(r) for r in raw]

os.makedirs(OUTDIR, exist_ok=True)
payload = {"topic": "1b", "questions": questions}
with open(OUT, "w", encoding="utf-8") as fh:
    json.dump(payload, fh, ensure_ascii=False, indent=1)

# ---------------- validation ----------------
errs = []
data = json.load(open(DATA, encoding="utf-8"))
pids = {p["id"] for s in data["sections"] for p in s["points"]}
p2sec = {p["id"]: s["id"] for s in data["sections"] for p in s["points"]}

check = json.load(open(OUT, encoding="utf-8"))          # re-load from disk
qs = check["questions"]

ids = [q["id"] for q in qs]
if ids != ["1b-q%d" % i for i in range(1, len(qs) + 1)]:
    errs.append("id not continuous")
if len(set(ids)) != len(ids):
    errs.append("duplicate id")

cnt = collections.Counter(q["type"] for q in qs)
for q in qs:
    if q["point"] not in pids:
        errs.append("%s bad point %s" % (q["id"], q["point"]))
    if q["type"] == "mc":
        if not isinstance(q["answer"], int) or not 0 <= q["answer"] <= 3:
            errs.append("%s mc answer index" % q["id"])
        if len(q["options"]) != 4:
            errs.append("%s options != 4" % q["id"])
        if len(set(q["options"])) != len(q["options"]):
            errs.append("%s duplicate options" % q["id"])
    elif q["type"] == "tf":
        if not isinstance(q["answer"], bool):
            errs.append("%s tf answer not bool" % q["id"])
    elif q["type"] == "fill":
        a = q["answer"]
        if not a or not isinstance(a, (str, list)) or (isinstance(a, list) and not all(isinstance(x, str) and x for x in a)):
            errs.append("%s fill answer empty" % q["id"])
        if "____" not in q["q"]:
            errs.append("%s fill missing ____" % q["id"])
    else:
        errs.append("%s unknown type" % q["id"])
    for k, v in q.items():
        if isinstance(v, str) and "\ufffd" in v:
            errs.append("%s replacement char in %s" % (q["id"], k))
    for o in q.get("options", []):
        if "\ufffd" in o:
            errs.append("%s replacement char in option" % q["id"])

secs = collections.Counter(p2sec[q["point"]] for q in qs)
short = [s for s, c in secs.items() if c < 2]
missing = sorted({p2sec[p] for p in pids} - set(secs))
if short:
    errs.append("sections with <2 questions: %s" % short)
if missing:
    errs.append("sections with 0 questions: %s" % missing)

ansdist = collections.Counter(q["answer"] for q in qs if q["type"] == "mc")
tfans = collections.Counter(q["answer"] for q in qs if q["type"] == "tf")
n = len(qs)

print("questions:", n, dict(cnt))
print("ratio:", {k: round(v / n * 100) for k, v in cnt.items()})
print("sections covered:", len(secs), "/", len({p2sec[p] for p in pids}))
print("mc answer distribution:", dict(sorted(ansdist.items())))
print("tf answer distribution:", dict(tfans))
print("per-section counts:", dict(sorted(secs.items())))
print("VALIDATION:", "PASS" if not errs else "FAIL " + "; ".join(errs))

print("\n===== FULL QUIZ (for manual review) =====")
for q in qs:
    print(q["id"], q["type"], q["point"])
    print("  Q:", q["q"])
    for i, o in enumerate(q.get("options", [])):
        print("     %s. %s" % (L[i], o))
    if q["type"] == "mc":
        print("  A:", L[q["answer"]])
    elif q["type"] == "tf":
        print("  A:", q["answer"])
    else:
        print("  A:", q["answer"])
    print("  E:", q["explanation"])
    print()