# -*- coding: utf-8 -*-
import json, re, io, sys

BASE = r"C:\Users\guomi\OneDrive\文件\deepseek-harness\default-workspace\f6chem\scratch"
MAP = BASE + r"\map\2012_p1b.json"
CAT = BASE + r"\pp\catalog.tsv"

raw = io.open(MAP, encoding="utf-8").read()
errs = []
if "\ufffd" in raw:
    errs.append("contains U+FFFD")

data = json.loads(raw)

ids = set()
for line in io.open(CAT, encoding="utf-8"):
    parts = line.rstrip("\n").split("\t")
    if parts and parts[0]:
        ids.add(parts[0])

mapped = set()
refs = []
for m in data["mappings"]:
    refs.append(m["ref"])
    if not re.fullmatch(r"2012-P1B-Q\d+(\([a-z]\)(\([iv]+\))?)*", m["ref"]):
        errs.append("bad ref format: " + m["ref"])
    han = len(re.findall(r"[一-鿿]", m["focus"]))
    if han > 40 or len(m["focus"]) > 60:
        errs.append("focus too long: " + m["ref"])
    for p in m["points"]:
        if p not in ids:
            errs.append("unknown point: " + p + " in " + m["ref"])
        mapped.add(p)

if len(refs) != len(set(refs)):
    errs.append("duplicate refs")

terms = 0
for k in sorted(data["kw"]):
    if k not in mapped:
        errs.append("kw key not in mappings: " + k)
    if not data["kw"][k]:
        errs.append("kw empty list: " + k)
    for w in data["kw"][k]:
        terms += 1
        if "\ufffd" in w:
            errs.append("kw U+FFFD: " + k)
        is_expr = ("→" in w) or ("=" in w) or ("=" in w)
        han = len(re.findall(r"[一-鿿]", w))
        if is_expr:
            continue
        if han:
            if han > 8 or len(w) > 16:
                errs.append("kw too long: %s / %s" % (k, w))
        elif not (2 <= len(w) <= 16):
            errs.append("kw len odd: %s / %s" % (k, w))

qn = sorted(set(int(re.search(r"Q(\d+)", r).group(1)) for r in refs))
kw_pts = sum(1 for k in data["kw"] if data["kw"][k])
out = "units=%d refs=%d covered_Q=%s kw_points=%d kw_terms=%d\n" % (
    len(data["mappings"]), len(set(refs)), ",".join(str(x) for x in qn), kw_pts, terms)
if errs:
    out += "ERRORS:\n" + "\n".join(" - " + e for e in errs) + "\n"
io.open(BASE + r"\_chk_2012_p1b.out.txt", "w", encoding="utf-8").write(out)
print(out.encode("unicode_escape").decode("ascii"))
sys.exit(1 if errs else 0)
