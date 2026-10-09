# -*- coding: utf-8 -*-
"""dump client.js 的 Kp(tier-1)/Jp(tier-2)/em(resolveFence) 精确源码与调用点。"""
import io, sys
sys.stdout.reconfigure(encoding="utf-8")
P = r"C:\Users\guomi\.dsh\profiles\desktop\node_modules\@changfenhuang\dsh-genui\lib\client.js"
t = io.open(P, encoding="utf-8").read()

def dump_fn(name):
    i = t.find("function %s(" % name)
    if i < 0:
        print("fn %s not found" % name)
        return
    # 括号配平找函数结束
    depth = 0
    started = False
    for j in range(i, len(t)):
        c = t[j]
        if c == "{":
            depth += 1
            started = True
        elif c == "}":
            depth -= 1
            if started and depth == 0:
                print("\n=== function %s [%d..%d] ===" % (name, i, j + 1))
                print(t[i:j + 1])
                return
    print("unbalanced for", name)

dump_fn("Kp")
dump_fn("em")

# 调用点
import re
for name in ["Kp", "Jp", "em", "tm"]:
    sites = []
    for m in re.finditer(r"(?<![\w$])%s\(" % name, t):
        sites.append(m.start())
    print("\n%s call sites (%d): %s" % (name, len(sites), sites[:20]))
    for s in sites[:12]:
        print("   ...%s..." % t[max(0, s - 60):s + 40].replace("\n", "\\n"))
