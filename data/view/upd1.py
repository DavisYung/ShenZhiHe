# -*- coding: utf-8 -*-
import json, io, os
path = r'C:\Users\guomi\OneDrive\文件\deepseek-harness\default-workspace\f6chem\data\2b.json'
d = json.load(io.open(path, encoding='utf-8'))

# 修正 p001-p007 各點的 page（OCR 已確立：p002=頁1 intro, p003=頁2 蓄電池, p004=頁3 基本結構,
# p005=頁4 電化序, p006=頁5 鹽橋, p007=頁6 丹聶爾）
fix = {
    '2b-s1-p1': 2, '2b-s1-p2': 2, '2b-s1-p3': 3,
    '2b-s2-p1': 4, '2b-s2-p2': 4, '2b-s2-p3': 6, '2b-s2-p4': 7,
    '2b-s3-p1': 5, '2b-s3-p2': 5,
}
for s in d['sections']:
    for p in s['points']:
        if p['id'] in fix:
            p['page'] = fix[p['id']]

# 微幅校正：OCR 顯示鉛酸缺點為「防漏（密封類型）」「笨重」
for s in d['sections']:
    for p in s['points']:
        if p['id'] == '2b-s1-p2':
            p['body'] = p['body'].replace('防濕(密封類型)', '防漏（密封類型）').replace('苯重', '笨重')

# 新增 p008、p009 知識點
for s in d['sections']:
    if s['id'] == '2b-s3':
        s['points'].append({
            'id': '2b-s3-p3',
            'title': '電化次序的兩大用途與氧化劑/還原劑強弱',
            'body': '同一電化序表可從兩個方向判斷強弱：\n\n'
                    '- **氧化劑**（金屬離子一方）：由上而下**越來越強**（圖左側箭頭：弱→強）。\n'
                    '- **還原劑**（金屬一方）：由上而下**越來越弱**（圖右側箭頭：強→弱），即越上的金屬還原性越強。\n\n'
                    '**可利用電化次序來**：\n'
                    '- 推測元素的**化學活性**\n'
                    '- 推測**化學電池中的反應及電子流的方向**',
            'page': 9,
            'tags': ['電化序', '氧化劑', '還原劑'],
        })

d['sections'].append({
    'id': '2b-s4',
    'title': '氧化還原反應（CH20）',
    'points': [
        {
            'id': '2b-s4-p1',
            'title': '氧化還原反應的定義與氧化/還原作用',
            'body': '- 氧化還原反應：物質經過**氧化數的變化**，**同時進行氧化作用及還原作用**。\n'
                    '- **氧化作用 (Oxidation)**：獲得氧（**失去電子**）。\n'
                    '- **還原作用 (Reduction)**：失去氧（**獲得電子**）。\n'
                    '- 例子：2PbO(s) + C(s) → 2Pb(s) + CO₂(g)\n'
                    '  - C 獲得氧 [+O] 變成 CO₂（被氧化）\n'
                    '  - PbO 失去氧 [−O] 變成 Pb（被還原）\n'
                    '- **氧化劑**：令人哋氧化（即使別人被氧化）→ **PbO**（本身被還原）。\n'
                    '- **還原劑**：令人哋還原 → **C**（本身被氧化）。\n\n'
                    '⚠️ 記：氧化劑/還原劑是「使別人怎樣」——氧化劑使別人氧化、自己被還原。',
            'page': 8,
            'tags': ['氧化還原', '氧化劑', '還原劑'],
        },
    ],
})

os.makedirs(os.path.dirname(path), exist_ok=True)
with io.open(path, 'w', encoding='utf-8') as f:
    json.dump(d, f, ensure_ascii=False, indent=1)
n_pts = sum(len(s['points']) for s in d['sections'])
print('sections=%d points=%d' % (len(d['sections']), n_pts))
