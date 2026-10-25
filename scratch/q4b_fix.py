# -*- coding: utf-8 -*-
import json
OUT = r'D:\deepseek-harness\default-workspace\f6chem\quiz\4b.json'
doc = json.load(open(OUT, encoding='utf-8'))
qs = {x['id']: x for x in doc['questions']}

# 1) q9: mc -> fill（保留 s3-p2 的平衡濃度計算，降低 mc 比例、提高 fill 比例）
q9 = qs['4b-q9']
q9.clear()
q9.update({
 "id": "4b-q9", "type": "fill", "point": "4b-s3-p2",
 "q": "把 2.00 mol CH₃OH(g) 通入 400℃ 的 3.00 dm³ 密閉容器中進行 2CH₃OH(g) ⇌ CH₃OCH₃(g) + H₂O(g)，平衡時有 60% 的 CH₃OH 轉換成 CH₃OCH₃ 和 H₂O。則平衡時 [CH₃OH] = ____ mol dm⁻³。",
 "answer": ["0.2667", "0.267", "0.27"],
 "explanation": "消耗的 CH₃OH = 2.00 × 60% = 1.20 mol，剩餘 0.80 mol，所以 [CH₃OH] = 0.80/3.00 = 0.2667 mol dm⁻³。由 2CH₃OH → CH₃OCH₃ 的 2:1 比例，生成的 CH₃OCH₃ 與 H₂O 各為 0.60 mol，即各 0.2 mol dm⁻³；代入 Kc = (0.2)(0.2)/(0.2667)² = 0.562。若忘記先扣除已消耗的 CH₃OH（誤得 0.4 mol dm⁻³），或忽略 2:1 的係數比，都是常見錯誤。"
})

# 2) q13: tf True -> False（同一 point，改為與課本相反的陳述，使 tf 約一半 false）
q13 = qs['4b-q13']
q13['q'] = "Kc << 1 的平衡體系中，反應混合物主要以生成物為主，代表反應幾乎完全進行。"
q13['answer'] = False
q13['explanation'] = ("錯誤，說反了。Kc << 1 表示生成物相對極少，平衡位置靠近反應物，"
 "反應混合物主要為反應物，代表反應幾乎不進行；只有 Kc >> 1 才表示反應混合物主要為生成物、反應幾乎完全。"
 "Kc ≈ 1 時反應物與生成物的分量相若。")

doc['questions'] = list(qs.values())
json.dump(doc, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print('adjusted:', len(doc['questions']))