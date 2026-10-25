import io, sys
p = r"D:\deepseek-harness\default-workspace\f6chem\scratch\pp\catalog.tsv"
raw = open(p, "rb").read()
out = []
for enc in ["utf-8", "cp950", "big5hkscs", "gbk", "utf-16"]:
    try:
        t = raw.decode(enc)
        out.append(enc + " OK | " + t.splitlines()[0][:80])
    except Exception as e:
        out.append(enc + " FAIL " + str(e)[:60])
sys.stdout.buffer.write(("\n".join(out) + "\n").encode("utf-8"))
