import json,sys,os,glob
sys.stdout.reconfigure(encoding="utf-8")
d=json.load(open("data/bio/subject.json",encoding="utf-8"))
registered=set(d.get("topics",[]))
print("subject.json 登记的 topics:",len(registered))
print(sorted(registered))
print("\n=== data/bio/ 下实际存在的文件 ===")
files=set()
for p in glob.glob("data/bio/bio*.json"):
    if p.endswith(".bak") or ".bak" in p: continue
    files.add(os.path.basename(p).replace(".json",""))
print("实际文件:",len(files))
print(sorted(files))
print("\n=== 差异 ===")
print("文件存在但未登记:",sorted(files-registered))
print("登记但文件不存在:",sorted(registered-files))
