# -*- coding: utf-8 -*-
"""Append final sections 1b-s16 ~ s18 (pages 41-43), then full validation.
p044/p045 are 0-byte blank pages -> skipped, never fabricated."""
import json, io, os, sys
sys.stdout.reconfigure(encoding="utf-8")

BASE = r"C:\Users\guomi\OneDrive\文件\deepseek-harness\default-workspace\f6chem"
DATA = os.path.join(BASE, "data", "1b.json")
OCR = os.path.join(BASE, "ocr", "1b")

def S(sid, title, points):
    return {"id": sid, "title": title, "points": points}

def P(pid, title, body, page, tags):
    return {"id": pid, "title": title, "body": body, "page": page, "tags": tags}

BATCH_C = [
S("1b-s16", "簡單分子結構", [
  P("1b-s16-p1", "簡單分子結構的特徵",
    "- 由**共價化合物**組成，例如 **H₂、O₂、CO₂、N₂**；由**獨立的分子**存在。\n- **低熔點及低沸點**，因為分子間只有**微弱的范德華引力**。\n- **大部分不溶於水**，一般可溶於非水溶劑。\n- **不導電**，因為沒有可自由流動的電子或離子。",
    41, ["簡單分子結構", "范德華引力", "溶解度", "導電性"]),
  P("1b-s16-p2", "簡單分子間的作用力示意",
    "- 分子**內部**原子之間由**強大的共價鍵**連結；**分子與分子之間**只有**微弱的范德華引力**。\n- 正是分子間微弱的吸引力，令簡單分子結構的物質熔點、沸點都低。\n- ⚠️ 教師重點：分辨「分子內的共價鍵」與「分子間的范德華力」兩種不同的作用力。",
    41, ["共價鍵", "范德華引力", "分子間作用力"]),
  P("1b-s16-p3", "氫與氧的沸點比較",
    "- **氫的沸點 −246 °C**（單原子分子）；**氧的沸點 −185.8 °C**（雙原子分子）。\n- 氧分子（O₂，相對分子質量 32）比氫分子（H₂，相對分子質量 2）大，故**氫分子間的范德華力較弱**，沸點較低。\n- 結論：**沸點 氫 < 氧**。\n- ⚠️ 教師重點：同類分子之間，相對分子質量越大 → 電子雲越有極性、范德華力越強 → 沸點越高。",
    41, ["氫", "氧", "沸點", "范德華引力", "相對分子質量"]),
]),
S("1b-s17", "物質的性質與結構、化學鍵類別的關係", [
  P("1b-s17-p1", "由物質類別判斷結構類別",
    "- **離子化合物 → 巨型離子結構**（微觀：宏觀結構 = 巨型離子結構）。\n- **共價化合物 → 巨型共價結構或簡單分子結構**。\n- **金屬／合金 → 巨型金屬結構**。\n- 對應的化學鍵：巨型離子靠**強大的離子鍵**、巨型共價靠**強大的共價鍵**、巨型金屬靠**強大的金屬鍵**、簡單分子靠**分子間微弱的范德華力**。\n- ⚠️ 教師重點：此頁為 essay 常出題目，須能由「物質類別 → 結構類別 → 化學鍵 → 物理性質」完整串連。",
    42, ["結構類別", "巨型金結構", "essay", "化學鍵"]),
]),
S("1b-s18", "四大結構類別總結比較", [
  P("1b-s18-p1", "結構類別、在哪裡形成與所含粒子",
    "- **巨型離子結構**：由**金屬和非金屬**化合生成的化合物，如**氯化鈉、氧化鎂**；所含粒子為**陽離子和陰離子**。\n- **巨型共價結構**：由**第 IV 族元素及部分非金元素**化合生成，如**金剛石、石墨、二氧化矽**；所含粒子為**原子**。\n- **簡單分子結構**：由**一些非金元素**化合生成，如**氫、碘、氨、乾冰**；所含粒子為**細小的分子**。\n- **巨型金屬結構**：由**金屬**生成，如**銅、鎳**；所含粒子為**帶正電荷的金屬離子**，被**離域電子海**包圍。",
    43, ["巨型離子", "巨型共價", "簡單分子", "巨型金屬", "離域電子海"]),
  P("1b-s18-p2", "化學鍵與常溫常壓下的狀態",
    "- **巨型離子**：由**強大的離子鍵**連結；常溫常壓下為**固體**。\n- **巨型共價**：原子藉**強大的共價鍵**連結成三維網狀結構；常溫常壓下為**固體**。\n- **簡單分子**：分子內為強大的共價鍵，**分子之間只有微弱的范德華力**；常溫常壓下可呈**固體、液體或氣體**（如乾冰為固體、水為液體、氧氣為氣體）。\n- **巨型金屬**：由**強大的金屬鍵**連結；常溫常壓下為**固體**。",
    43, ["離子鍵", "共價鍵", "范德華力", "金屬鍵", "物態"]),
  P("1b-s18-p3", "硬度、熔點與沸點",
    "- **巨型離子**：**堅硬而易碎**；熔點、沸點**高**。\n- **巨型共價**：**非常硬**（若具三維網狀結構）；熔點、沸點**非常高**。\n- **簡單分子**：固體通常**質軟**；熔點、沸點**低**。\n- **巨型金屬**：**硬，且具延展性**；熔點、沸點**高至高**。",
    43, ["硬度", "熔點", "沸點", "延展性"]),
  P("1b-s18-p4", "溶解度與導電性",
    "- **巨型離子**：一般都**溶於水，不溶於非水溶劑**；固態不導電，但**熔融或溶於水時能導電**。\n- **巨型共價**：**不溶於水及非水溶劑**；**不能導電**（石墨除外）。\n- **簡單分子**：一般**不溶於水**，但**易溶於非水溶劑**；**不能導電**。\n- **巨型金屬**：一般**不溶於水及非水溶劑**；**是優良的導電體**。",
    43, ["溶解度", "導電性", "石墨導電"]),
]),
]

with io.open(DATA, encoding="utf-8") as f:
    doc = json.load(f)

before_s, before_p = len(doc["sections"]), sum(len(s["points"]) for s in doc["sections"])
existing = {s["id"] for s in doc["sections"]}
added = [s for s in BATCH_C if s["id"] not in existing]
doc["sections"].extend(added)
with io.open(DATA, "w", encoding="utf-8") as f:
    json.dump(doc, f, ensure_ascii=False, indent=2)

# ---- full validation ----
chk = json.load(io.open(DATA, encoding="utf-8"))
secs = chk["sections"]
ids = [s["id"] for s in secs]
pids = [p["id"] for s in secs for p in s["points"]]
pages = sorted({p["page"] for s in secs for p in s["points"]})
new_pages = sorted({p["page"] for s in secs if s["id"] >= "1b-s9" for p in s["points"]})
print("BATCH C OK | 本批新增 %d sections / %d points" % (len(added), sum(len(s["points"]) for s in added)))
print("=" * 62)
print("總計 sections: %d (原 %d → +%d)" % (len(secs), before_s, len(secs) - before_s))
print("總計 points  : %d (原 %d → +%d)" % (len(secs) and sum(len(s["points"]) for s in secs),
                                            before_p, sum(len(s["points"]) for s in secs) - before_p))
print("section id 唯一:", len(ids) == len(set(ids)), "| point id 唯一:", len(pids) == len(set(pids)))
print("新 section id :", [i for i in ids if i >= "1b-s9"])
bad = [s["id"] for s in secs if not 3 <= len(s["points"]) <= 6]
print("每節 3-6 點 :", "OK" if not bad else "越界 " + str(bad))
missing = [(s["id"], p["id"]) for s in secs for p in s["points"]
           if not all(k in p for k in ("id", "title", "body", "page", "tags"))]
print("point 欄位完整:", "OK" if not missing else str(missing[:5]))
print("新增涵蓋頁碼:", new_pages)
blank = [44, 45]
print("跳過空白頁   :", blank, "(p044.txt/p045.txt 均為 0 位元組)")
