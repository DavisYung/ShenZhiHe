import json,io,sys
sys.stdout.reconfigure(encoding="utf-8")
p="site/version.json"
with io.open(p,encoding="utf-8-sig") as f: d=json.load(f)
d["version"]="V0.18.0"
d["note"]=d["note"].replace("V0.17.0 = 補上遺失的 tsub()","V0.18.0 = 修復單元頁「測驗本分區」按鈕被壓成 23px 標籤（.go 樣式原本只寫在 .rrow 下）、公式表補 emoji（原本顯示回形針）、測驗頁把「分區總測」組合測驗提到最上方；V0.17.0 = 補上遺失的 tsub()")
with io.open(p,"w",encoding="utf-8",newline="\n") as f:
    json.dump(d,f,ensure_ascii=False,indent=2); f.write("\n")
print("version:",d["version"])
