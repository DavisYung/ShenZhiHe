import json,io,sys
sys.stdout.reconfigure(encoding="utf-8")
p="extras/phys/formulas.json"
with io.open(p,encoding="utf-8-sig") as f: d=json.load(f)
# 補上 emoji（原本缺這個欄位，前端 fallback 成回形針 📎）
d["emoji"]="🧮"
with io.open(p,"w",encoding="utf-8",newline="\n") as f:
    json.dump(d,f,ensure_ascii=False,indent=2); f.write("\n")
print("emoji 已设为:",d["emoji"])
print("BOM:",open(p,"rb").read(3).hex())
