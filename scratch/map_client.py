# -*- coding: utf-8 -*-
"""把 client.js（minified）裡修復管線的幾個函數定位並 dump 出來。"""
import io, re, sys

sys.stdout.reconfigure(encoding="utf-8")
P = r"C:\Users\guomi\.dsh\profiles\desktop\node_modules\@changfenhuang\dsh-genui\lib\client.js"
t = io.open(P, encoding="utf-8").read()
print("client.js chars:", len(t))

# 1) tetris 函数（含 "columns" 正则）
i = t.find('function qp(')
print("\n=== qp (tetris) @", i, "===")
# dump 到下一个 function 边界（粗略：往后 3000 字符里找 \nfunction 或 ;function）
seg = t[i:i+4000]
print(seg[:3500])

# 2) 找包含 JSON.parse 且含 \\" 输出（tier-1 引号转义）的函数
print("\n=== candidates: occurrences of \\\" escaping idiom ===")
for m in re.finditer(r'function (\w+)\((\w+)\)\{', t):
    start = m.start()
    body = t[start:start+4000]
    # tier-1 特征：JSON.parse 在函数内 + repairs 语义（计数变量++）+ 输出 \"
    if 'JSON.parse' in body[:2000] and '\\"' in body[:2000] and body.count('JSON.parse') >= 1:
        fn = m.group(1)
        # 进一步区分：tier-1 只做引号/尾逗号；tier-2 有 stack.pop 或 qp 调用
        is_t2 = ('qp(' in body[:3500]) or ('.pop()' in body[:3000])
        print(f"  fn {fn}@{start} tier2-ish={is_t2} len>= {body[:60]!r}")
