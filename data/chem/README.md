# 化學（chem）資料夾說明

這個資料夾放**化學科**的內容，和化學科完全分開，互不干擾。

## 檔案放法

| 位置 | 放什麼 | 檔名 |
|---|---|---|
| `data/chem/subject.json` | 科目設定（名稱、顏色、課題清單） | 固定 |
| `data/chem/<課題id>.json` | 每個課題的章節與知識點 | 例如 `1a.json` |
| `data/chem/links.json` | 本課題之間的知識串連 | 固定 |
| `quiz/chem/<課題id>.json` | 每個課題的測驗題 | 例如 `1a.json` |

## 課題資料格式（data/chem/<tid>.json）

```json
{
  "id": "1a",
  "title": "課題名稱",
  "pdf": "來源 PDF 檔名",
  "sections": [
    {
      "id": "1a-s1",
      "title": "章節名稱",
      "points": [
        {
          "id": "1a-s1-p1",
          "title": "知識點標題",
          "page": 2,
          "tags": ["標籤"],
          "body": "內容，支援 **粗體**、`程式碼`、- 清單、| 表格 |"
        }
      ]
    }
  ]
}
```

## 測驗題格式（quiz/chem/<tid>.json）

```json
{
  "topic": "1a",
  "questions": [
    {"id": "1a-q1", "type": "mc", "point": "1a-s1-p1",
      "q": "題目", "options": ["A", "B", "C", "D"], "answer": 1,
      "explanation": "解析"},
    {"id": "1a-q2", "type": "tf", "point": "1a-s1-p1",
      "q": "題目", "answer": true, "explanation": "解析"},
    {"id": "1a-q3", "type": "fill", "point": "1a-s1-p1",
      "q": "題目", "answer": ["答案", "別名"], "explanation": "解析"}
  ]
}
```

## 知識串連格式（data/chem/links.json）

```json
[{"from": "1a-s1-p1", "to": "1b-s2-p1", "label": "為什麼相關"}]
```

`from` / `to` 必須是存在於本科課題裡的知識點 id。跨科串連目前**不支援**，兩科的資料是分開載入的。

## 加完內容之後

新增課題要在 `subject.json` 的 `topics` 陣列裡補上課題 id，然後重新產生網站：

```
python f6chem/site/build.py
```

`ready` 欄位：內容還沒開始放就設 `false`，網站會顯示「內容準備中」，不會出現空白的頁面。
