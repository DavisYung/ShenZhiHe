import json,io,sys
sys.stdout.reconfigure(encoding="utf-8")
p="site/version.json"
with io.open(p,encoding="utf-8-sig") as f: d=json.load(f)
d["version"]="V0.13.6"
# note 精简：把 V0.14~V0.20 那串「新增功能」叙述收掉，改成 V0.13.x 的修复叙述
d["note"]=("版號規則：V0.0.x = Demo／開發中，每次結構性改動加 x；V0.1.0 = 內容大致定型、可正式分享；"
 "V0.2.0 = 新增物理電學分區（六課，靜電學至輸電）；V0.5.0 = 新增物理第六分區「原子世界」（選修二 E2，三課 57 知識點）；"
 "V0.12.0 = 新增生物分區（10 單元 34 章）；V0.13.0 = 新增數學分區（計算機程式：fx-50FH II 四段萬能程式）；"
 "V0.13.6 = 修復一批顯示與功能回退問題：額外資訊的物理公式表／有機命名規則補專屬版面（不再印原始 JSON）、"
 "下角標顯示為字面下劃線（c_rms／N_A／V_s 等 446 處）、公式表同課題聚組並用課題專屬配色、"
 "補上遺失的 tsub()（修復生物「體內平衡與調節」單元與測驗按鈕白屏）、單元頁測驗按鈕被壓扁、"
 "公式表圖標顯示回形針、測驗範圍改為直接在課題列表勾選（勾多個即合成一份測驗）、"
 "Service Worker 導航超時 3.5s→10s（修復弱網下總回退舊版）。只改這個檔，build.py 會自動套用到檔名、頁面標題與頁尾。")
with io.open(p,"w",encoding="utf-8",newline="\n") as f:
    json.dump(d,f,ensure_ascii=False,indent=2); f.write("\n")
print("version:",d["version"])
print("BOM:",open(p,"rb").read(3).hex())
