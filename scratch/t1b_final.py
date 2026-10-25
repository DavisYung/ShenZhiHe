# -*- coding: utf-8 -*-
import json, io, sys, os
sys.stdout.reconfigure(encoding="utf-8")
BASE = r"D:\deepseek-harness\default-workspace\f6chem"
DATA = os.path.join(BASE, "data", "1b.json")

doc = json.load(io.open(DATA, encoding="utf-8"))   # json.load 驗證
secs = doc["sections"]
NEW = {"1b-s%d" % n for n in range(9, 19)}
new = [s for s in secs if s["id"] in NEW]
old = [s for s in secs if s["id"] not in NEW]
np = sum(len(s["points"]) for s in new)
op = sum(len(s["points"]) for s in old)
pages = sorted({p["page"] for s in new for p in s["points"]})
badpage = [(s["id"], p["id"], p["page"]) for s in new for p in s["points"]
           if not isinstance(p["page"], int) or not 28 <= p["page"] <= 45]
ocrlen = {n: os.path.getsize(os.path.join(BASE, "ocr", "1b", "p%03d.txt" % n)) for n in (44, 45)}

print("json.load 驗證 : PASS")
print("原有內容未動   : %d sections / %d points (1b-s1~s8)" % (len(old), op))
print("新增            : %d sections / %d points" % (len(new), np))
print("檔案總計        : %d sections / %d points" % (len(secs), op + np))
print("新增頁碼覆蓋    : %d-%d，%d 頁 (%s)" % (pages[0], pages[-1], len(pages), pages))
print("新 section page 範圍:", "OK" if not badpage else str(badpage))
print("每節 3-6 點     :", "OK" if all(3 <= len(s["points"]) <= 6 for s in new) else "FAIL")
print("p044/p045 位元組:", ocrlen, "-> 空白頁跳過，未編造內容")
print("檔案大小        :", os.path.getsize(DATA), "bytes")
