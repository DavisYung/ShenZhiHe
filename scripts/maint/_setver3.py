import json,io,sys
sys.stdout.reconfigure(encoding="utf-8")
p="site/version.json"
with io.open(p,encoding="utf-8-sig") as f: d=json.load(f)
d["version"]="V0.19.0"
d["note"]=d["note"].replace("V0.18.0 = 修復單元頁","V0.19.0 = 測驗頁新增「自由組合測驗」：可勾選任意幾個課題組成一份測驗（分區歸組、全選/清除、只考錯題、指定抽題數），科目之間仍嚴格隔離；V0.18.0 = 修復單元頁")
with io.open(p,"w",encoding="utf-8",newline="\n") as f:
    json.dump(d,f,ensure_ascii=False,indent=2); f.write("\n")
print("version:",d["version"])
