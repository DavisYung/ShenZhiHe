import json,sys,glob
sys.stdout.reconfigure(encoding="utf-8")
for p in sorted(glob.glob("extras/*/*.json")):
    d=json.load(open(p,encoding="utf-8"))
    print(f'{p:36} emoji={repr(d.get("emoji")):12} type={d.get("type")}')
