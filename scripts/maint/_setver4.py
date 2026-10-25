import json,io,sys
sys.stdout.reconfigure(encoding="utf-8")
p="site/version.json"
with io.open(p,encoding="utf-8-sig") as f: d=json.load(f)
d["version"]="V0.20.0"
d["note"]=d["note"].replace("V0.19.0 = 測驗頁新增","V0.20.0 = 測驗範圍改為直接在課題列表勾選（去掉獨立的「自由組合」區塊），勾多個即合成一份測驗，底部浮動條顯示已選數與總題數；V0.19.0 = 測驗頁新增")
with io.open(p,"w",encoding="utf-8",newline="\n") as f:
    json.dump(d,f,ensure_ascii=False,indent=2); f.write("\n")
print("version:",d["version"])
