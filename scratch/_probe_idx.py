# -*- coding: utf-8 -*-
import io, re, sys
sys.stdout.reconfigure(encoding="utf-8")
h = io.open(r"D:\deepseek-harness\default-workspace\神智核-GitHub部署包\index.html", encoding="utf-8").read()
print("len:", len(h))
print("img/ count:", h.count("img/"))
print("data:image count:", h.count("data:image"))
print("--- src= 样本 ---")
for m in re.findall(r'src="[^"]{0,50}', h)[:10]:
    print(" ", m)
print("--- 版本字串 ---")
print("V0.3.0:", h.count("V0.3.0"), "| V0.2.0:", h.count("V0.2.0"))
for m in sorted(set(re.findall(r"V0\.\d+\.\d+", h)))[:10]:
    print(" ", m)
print("--- title ---")
m = re.search(r"<title>(.*?)</title>", h, re.S)
print(" ", m.group(1) if m else "none")