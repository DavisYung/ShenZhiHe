# -*- coding: utf-8 -*-
"""检查 README 模板里的所有 {占位符} 是否都在 _stats 里注册。
避免 KeyError 或漏统计导致的构建失败（V0.4.3 曾因 NUC 前缀撞名踩过）。"""
import io, os, re, sys
sys.stdout.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

src = io.open(os.path.join(HERE, "prep_ghpages.py"), encoding="utf-8").read()

# 抽出 README 三引号内容
m = re.search(r'README = """(.*?)"""', src, re.S)
if not m:
    sys.exit("找不到 README 模板")
readme = m.group(1)

# README 里用到的占位符（排除 .replace 已处理的 ST）
used = set(re.findall(r"\{([A-Z][A-Z0-9_]*)\}", readme))
used.discard("ST")
print(f"README 占用占位符 {len(used)} 个：")
print("  " + ", ".join(sorted(used)))

# 从各 stats 函数收集键名（两种写法：return dict(...) 与 return {...}）
keys = set()
for fn in re.finditer(r"return\s+(?:dict\(|\{)(.*?)(?:\)|\})\s*$", src, re.S | re.M):
    for kv in re.findall(r"([A-Z][A-Z0-9_]*)\s*[=:]", fn.group(1)):
        keys.add(kv)
# 兜底：直接抓所有 UPDATE_KEYS 式的赋值与字典字面量中的大写键
for kv in re.findall(r"\b([A-Z][A-Z0-9_]{2,})\s*[=:]", src):
    keys.add(kv)
print(f"\n_stats 已注册 {len(keys)} 个键：")
print("  " + ", ".join(sorted(keys)))

missing = sorted(used - keys)
unused = sorted(keys - used)
print()
if missing:
    print(f"[FAIL] README 用到但未注册（会 KeyError）：{missing}")
    sys.exit(1)
print("[OK] README 所有占位符都已注册")
if unused:
    print(f"[INFO] 已注册但 README 未用：{unused}")
