# -*- coding: utf-8 -*-
import io, json

# 核物理链接文件
# 实际路径：f6chem\nuclear\links.json
# 数据已在 f6chem\nuclear\data\nuclear1/2/3.json 中生成

links = [
    # 核物理内部串连
    {"from": "nuclear1-s1-p1", "to": "nuclear2-s1-p1", "label": "由輻射過渡到核素構成"},
    {"from": "nuclear2-s1-p2", "to": "nuclear3-s1-p1", "label": "由衰變過渡到核反應"},
    
    # 跨科串连：核物理→力学（能量守恆、动量）
    {"from": "nuclear3-s1-p1", "to": "mech6-s1-p1", "label": "能量守恆定律：核分裂釋放的能量可轉化為機械能與熱能"},
    
    # 跨科串连：核物理→化学（核变与化学变化）
    {"from": "nuclear1-s1-p1", "to": "chem1-s1-p1", "label": "電離輻射會破壞分子結構，屬核物理範疇，非化學變化"},
]

with io.open("f6chem/nuclear/links.json", "w", encoding="utf-8") as f:
    json.dump(links, f, ensure_ascii=False, indent=1)
    f.write("\n")

print("串連 %d 條" % len(links))
print("已寫出 f6chem/nuclear/links.json")