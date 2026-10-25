import io, json, sys

OUT = r"D:\deepseek-harness\default-workspace\f6chem\scratch\map\2019_p1a.json"
CAT = r"D:\deepseek-harness\default-workspace\f6chem\scratch\pp\catalog.tsv"

raw = io.open(OUT, "r", encoding="utf-8").read()
data = json.loads(raw)  # json.load 通过
ids = set()
for line in io.open(CAT, "r", encoding="utf-8"):
    line = line.rstrip("\n")
    if line.strip():
        ids.add(line.split("\t")[0])

bad_ref = [m["ref"] for m in data["mappings"] if not m["ref"].startswith("2019-P1A-Q")]
empty = [m["ref"] for m in data["mappings"] if not m["points"]]
unknown = [(m["ref"], p) for m in data["mappings"] for p in m["points"] if p not in ids]
long_focus = [(m["ref"], len(m["focus"])) for m in data["mappings"] if len(m["focus"]) > 30]
nums = [int(m["ref"].split("Q")[-1]) for m in data["mappings"]]

print("has_bom_or_fffd:", "\\ufffd" in raw)
print("units:", len(data["mappings"]))
print("empty_mappings:", len(empty), empty)
print("range:", min(nums), "-", max(nums), "sequential:", nums == list(range(25, 37)))
print("bad_ref:", bad_ref)
print("unknown_points:", unknown)
print("focus_too_long:", long_focus)
