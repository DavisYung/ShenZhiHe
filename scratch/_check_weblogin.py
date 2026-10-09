# -*- coding: utf-8 -*-
"""检查 dsh-deepseek-web-login 的实际使用情况：调用记录、账号、诊断。"""
import io
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")
WL = os.path.join(os.environ["USERPROFILE"], ".dsh", "web-login")

print("=" * 70)
print("dsh-deepseek-web-login 使用情况")
print("=" * 70)

# 1. 账号
ap = os.path.join(WL, "accounts.json")
if os.path.exists(ap):
    with io.open(ap, encoding="utf-8") as f:
        acc = json.load(f)
    print("\n[账号] 当前 activeId = %s" % acc.get("activeId"))
    adir = os.path.join(WL, "accounts")
    if os.path.isdir(adir):
        for n in sorted(os.listdir(adir)):
            p = os.path.join(adir, n)
            try:
                with io.open(p, encoding="utf-8") as f:
                    a = json.load(f)
                # 只显示非敏感字段
                keys = [k for k in a.keys() if k not in ("token", "cookie", "authorization", "password")]
                info = {k: a[k] for k in keys if not isinstance(a[k], (dict, list))}
                print("   %s  %s" % (n, json.dumps(info, ensure_ascii=False)[:150]))
            except Exception as e:
                print("   %s  (读取失败: %s)" % (n, e))

# 2. 调用记录
udir = os.path.join(WL, "usage")
if os.path.isdir(udir):
    files = sorted(f for f in os.listdir(udir) if f.endswith(".jsonl"))
    print("\n[调用记录] 共 %d 天" % len(files))
    for fn in files:
        p = os.path.join(udir, fn)
        lines = io.open(p, encoding="utf-8").read().splitlines()
        print("   %s  %d 条" % (fn, len([l for l in lines if l.strip()])))
    # 看最后一条的字段结构
    if files:
        last = os.path.join(udir, files[-1])
        lines = [l for l in io.open(last, encoding="utf-8").read().splitlines() if l.strip()]
        if lines:
            try:
                j = json.loads(lines[-1])
                print("\n[最后一条记录的字段]")
                for k, v in j.items():
                    vs = str(v)
                    if len(vs) > 70:
                        vs = vs[:70] + "…"
                    print("   %-22s %s" % (k, vs))
            except Exception as e:
                print("   解析失败: %s" % e)

# 3. 诊断
ddir = os.path.join(WL, "diagnostics")
if os.path.isdir(ddir):
    print("\n[诊断文件]")
    for n in sorted(os.listdir(ddir)):
        p = os.path.join(ddir, n)
        print("   %-28s %d bytes" % (n, os.path.getsize(p)))
    rj = os.path.join(ddir, "rejected-meta.jsonl")
    if os.path.exists(rj):
        lines = [l for l in io.open(rj, encoding="utf-8").read().splitlines() if l.strip()]
        print("   rejected-meta 共 %d 条" % len(lines))
        if lines:
            print("   最后一条: %s" % lines[-1][:200])

# 4. gate 配置
gp = os.path.join(WL, "gate.json")
if os.path.exists(gp):
    with io.open(gp, encoding="utf-8") as f:
        g = json.load(f)
    print("\n[节流配置]")
    for k in ("minRequestIntervalMs", "maxRequestIntervalMs", "maxPromptChars",
              "contextWindow", "autoSwitchMinutes", "sessionCleanup"):
        if k in g:
            print("   %-24s %s" % (k, g[k]))
