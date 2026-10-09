# extras/ — 額外資訊（補充資料）

這裡放「不屬於任何課題、但查資料時想隨手翻」的補充內容。
放進 `extras/<科目>/` 的每個 .json 都會自動變成網站導覽列「額外資訊」裡的一張卡，
**不計入學習進度、不出題、不影響知識圖譜**。

## 檔案格式

每個 JSON 至少要這幾個欄位：

| 欄位 | 說明 |
|---|---|
| `id` | 唯一代號，同時是網址 `#/extras/<id>`（可加 `@原子序` 深連結到某元素） |
| `type` | 版面型別。目前支援 `ptable`（元素週期表）；其他值會先以原始 JSON 呈現 |
| `order` | 排序，數字小的在前面 |
| `emoji` `title` `subtitle` | 卡片標題列 |
| `source` | 資料來源，顯示在卡片底部 |

### type = "ptable" 的欄位

- `categories`：`[{id, name, color}]`，分類圖例與格子底色都吃這裡
- `elements`：每個元素一格
  - `z` 原子序、`sym` 符號、`cn` 中文名、`en` 英文名、`mass` 相對原子質量
  - `cat` 對應 categories 的 id、`row`/`col` 在 18 欄網格的位置（鑭系 row 8、錒系 row 9）
  - `period`/`group`/`state`（氣／液／固）

### type = "hot" 的欄位

由 `_mk_hot.py` 從各課題的 `exam` 標注重生，**不要手改**：

- `summary`：`{years, points, hits, lv3, lv2, lv1, topics}`
- `groups`：`[{id: lv3|lv2, name, color, items}]`；item = 知識點 + `years`/`hits`/`level`/`kw`/`samples`
- `topics`：`[{id, name, hits}]` 各課題命中數（篩選 chip 用）
- `years`：`[{year, topics, hits}]` 各年被考課題與題-點對數
- `keywords`：`[{text, count}]` 全站得分字眼詞頻（前 50 個顯示為字眼雲）

## 現有內容

- `chem/ptable.json` — 118 種元素週期表，中文名取自 Dave Lo《English-Chinese Periodic Table of Elements》(2006)，
  112–118 號補現代命名。重新產生：`python f6chem/_mk_ptable.py`
- `chem/hot.json` — 高頻考點報告（DSE 2012–2023 卷一甲部/乙部＋卷二逐題比對，含得分字眼）。
  **資料來源不是手工維護**：由各課題 `data/chem/*.json` 裡的 `exam` 標注重生。
  更新考標後重新產生：`python f6chem/_mk_hot.py`
  （考標本身的生產管線在 `scratch/`：`ocr_papers.py` OCR 試卷 → 子代理逐題映射 → `merge_exam.py` 合併 → `_mk_hot.py` 重生報告）

## 加完之後

在 `f6chem/` 底下執行：

```
python f6chem/site/build.py
```

網站會重建，額外資訊自動出現在導覽列。
