import json,io,sys
sys.stdout.reconfigure(encoding="utf-8")
p="site/version.json"
with io.open(p,encoding="utf-8-sig") as f: d=json.load(f)
d["version"]="V0.17.0"
d["note"]=d["note"].replace(
 "V0.15.0 = 上述兩個版面改為柔和卡通风",
 "V0.16.0 = 修復下角標顯示為字面下劃線（全站 446 處），公式表改回每課題專屬配色，SW 導航超時 3.5s→10s；V0.17.0 = 補上遺失的 tsub()（修復生物「體內平衡與調節」單元與課題測驗按鈕白屏）、公式表同課題聚組並加課題小標、按鈕改實心課題色（邊界明確）；V0.15.0 = 上述兩個版面改為柔和卡通风")
with io.open(p,"w",encoding="utf-8",newline="\n") as f:
    json.dump(d,f,ensure_ascii=False,indent=2); f.write("\n")
print("version:",d["version"])
print("BOM:",open(p,"rb").read(3).hex())
