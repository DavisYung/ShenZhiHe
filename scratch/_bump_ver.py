# -*- coding: utf-8 -*-
import io, json, re, sys
sys.stdout.reconfigure(encoding="utf-8")

p = r"f6chem\site\version.json"
# 用原始字节读，避免任何编码猜测
raw = io.open(p, "rb").read()
txt = raw.decode("utf-8")

# 只替换 version 字段的值
new = re.sub(r'("version"\s*:\s*")V0\.2\.0(")', r'\g<1>V0.3.0\g<2>', txt)
assert new != txt, "version 字段未被替换（可能已是 V0.3.0）"

with io.open(p, "w", encoding="utf-8", newline="\n") as f:
    f.write(new)

# 读回验证
t = json.load(io.open(p, encoding="utf-8"))
print("version =", t["version"])
print("tagline =", t["tagline"][:60])
print("note    =", t["note"][:70])
