# -*- coding: utf-8 -*-
import json, io, sys
try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except Exception:
    pass

BASE = r"C:\Users\guomi\OneDrive\文件\deepseek-harness\default-workspace\f6chem\scratch"
MAP = BASE + r"\map\2013_p1b.json"
CAT = BASE + r"\pp\catalog.tsv"

raw = io.open(MAP, 'rb').read()
if b'\xef\xbf\xbd' in raw:
    print("FAIL: output contains U+FFFD bytes")
    sys.exit(1)

data = json.loads(raw.decode('utf-8'))
print("json.load OK")

cat_ids = set()
for line in io.open(CAT, encoding='utf-8'):
    parts = line.rstrip('\n').split('\t')
    if parts and parts[0]:
        cat_ids.add(parts[0])
print("catalog ids:", len(cat_ids))

errs = []
used_points = set()
refs = set()
for m in data['mappings']:
    ref = m['ref']
    if ref in refs:
        errs.append("dup ref " + ref)
    refs.add(ref)
    if not ref.startswith("2013-P1B-Q"):
        errs.append("bad ref prefix " + ref)
    fo = m['focus']
    if len(fo) > 40:
        errs.append("focus>40: " + ref + " " + str(len(fo)))
    if '\ufffd' in fo:
        errs.append("ufffd in focus " + ref)
    for p in m['points']:
        if p not in cat_ids:
            errs.append("point not in catalog: " + p + " @ " + ref)
        used_points.add(p)

for p, kws in data['kw'].items():
    if p not in used_points:
        errs.append("kw key not in mappings: " + p)
    if not isinstance(kws, list) or len(kws) > 8:
        errs.append("kw bad size: " + p)
    for k in kws:
        if '\ufffd' in k:
            errs.append("ufffd in kw " + p)
        if not (2 <= len(k) <= 14):
            errs.append("kw len odd: %s / %s" % (p, k))

# coverage check: expected refs
expected = set()
qs = {
 1: ["(a)","(b)(i)","(b)(ii)","(c)"],
 2: ["(a)","(b)","(c)"],
 3: ["(a)","(b)"],
 4: ["(a)","(b)","(c)","(d)(i)","(d)(ii)","(e)(i)","(e)(ii)"],
 5: ["(a)(i)","(a)(ii)","(b)"],
 6: [""],
 7: ["(a)(i)","(a)(ii)","(b)","(c)(i)","(c)(ii)"],
 8: ["(a)","(b)(i)","(b)(ii)","(c)"],
 9: ["(a)","(b)(i)","(b)(ii)"],
 10: ["(a)","(b)","(c)(i)","(c)(ii)"],
 11: ["(a)","(b)","(c)","(d)(i)","(d)(ii)"],
 12: ["(a)","(b)","(c)"],
 13: [""],
 14: ["(a)","(b)(i)","(b)(ii)","(c)"],
 15: ["(a)","(b)","(c)","(d)"],
}
for n, subs in qs.items():
    for s in subs:
        expected.add("2013-P1B-Q%d%s" % (n, s))
missing = expected - refs
extra = refs - expected
if missing: errs.append("missing refs: " + ",".join(sorted(missing)))
if extra: errs.append("extra refs: " + ",".join(sorted(extra)))

kw_pts = set(data['kw'].keys())
n_units = len(data['mappings'])
covered_q = sorted({int(r.split('-Q')[1].split('(')[0]) for r in refs})
print("units=%d / questions covered=%s / kw points=%d" % (n_units, covered_q, len(kw_pts)))
if errs:
    print("FAIL:")
    for e in errs:
        print("  -", e)
    sys.exit(1)
print("ALL PASS")
