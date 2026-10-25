import json,glob,re,sys,collections
sys.stdout.reconfigure(encoding="utf-8")
# Unicode 下标字符
subs="₀₁₂₃₄₅₆₇₈₉ₐₑₒₓₕₖₗₘₙₚₛₜᵢᵣᵤᵥᵦᵧᵨᵩᵪ"
supers="⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻⁼⁽⁾ⁿⁱˣ"
c=collections.Counter(); samples=[]
for f in glob.glob("data/*/*.json"):
    if "links" in f or "subject" in f: continue
    try: d=json.load(open(f,encoding="utf-8"))
    except: continue
    for s in d.get("sections",[]):
        for p in s.get("points",[]):
            b=p.get("body","")
            for ch in b:
                if ch in subs: c["unicode_sub"]+=1
                if ch in supers: c["unicode_sup"]+=1
            if re.search(r"[A-Za-z]_[A-Za-z0-9]", b):
                c["underscore"]+=1
                if len(samples)<5: samples.append((p["id"], re.findall(r"[A-Za-z]_[A-Za-z0-9]+", b)[:4]))
print("统计:",dict(c))
for s in samples: print("  ",s)
