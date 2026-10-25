import json,sys,io
p="site/version.json"
# 用 utf-8-sig 读入（容忍 BOM），再以无 BOM 的 utf-8 写回
with io.open(p,encoding="utf-8-sig") as f:
    d=json.load(f)
print("version:",d["version"])
with io.open(p,"w",encoding="utf-8",newline="\n") as f:
    json.dump(d,f,ensure_ascii=False,indent=2)
    f.write("\n")
# 验证无 BOM
raw=open(p,"rb").read(3)
print("BOM 前3字节:",raw.hex(),"(efbbbf 表示有 BOM)")
