import json, io, sys, os

base = r"C:\Users\guomi\OneDrive\文件\deepseek-harness\default-workspace\f6chem\scratch"
jp = os.path.join(base, "map", "2021_p1b_b.json")
cp = os.path.join(base, "pp", "catalog.tsv")

errs = []
raw = open(jp, "rb").read()
if b"\xef\xbf\xbd" in raw:
    errs.append("JSON 含 U+FFFD")
d = json.loads(raw.decode("utf-8"))

cat = open(cp, "rb").read().decode("utf-8")
ids = set()
for ln in cat.splitlines():
    if ln.strip():
        ids.add(ln.split("\t")[0].strip())

refs = [m["ref"] for m in d["mappings"]]
bad = []
for m in d["mappings"]:
    for p in m["points"]:
        if p not in ids:
            bad.append((m["ref"], p))
    if len(m["focus"]) > 40:
        errs.append("focus 超 40 字: " + m["ref"] + " len=" + str(len(m["focus"])))
    if not (1 <= len(m["points"]) <= 3) and m["points"] != []:
        errs.append("points 數量異常: " + m["ref"])

kws = d.get("kw", {})
kwbad = [k for k in kws if k not in ids]
kwempty = [k for k, v in kws.items() if not v or len(v) > 8]
kwlen = [(k, len(w)) for k, v in kws.items() for w in v if not (2 <= len(w) <= 8)]

used = set(p for m in d["mappings"] for p in m["points"])
kworphan = sorted(used - set(kws))
kwunused = sorted(set(kws) - used)

sys.stdout.buffer.write((
    "refs=%d unique=%d\n" % (len(refs), len(set(refs))) +
    "kw_points=%d\n" % len(kws) +
    "unknown_point_ids=%s\n" % bad +
    "kw_unknown=%s\n" % kwbad +
    "kw_empty_or_too_many=%s\n" % kwempty +
    "kw_word_len_out_of_2_8=%s\n" % kwlen +
    "points_without_kw=%s\n" % kworphan +
    "kw_not_used_by_any_point=%s\n" % kwunused +
    "errors=%s\n" % errs +
    "refs_list=%s\n" % refs
).encode("utf-8"))
