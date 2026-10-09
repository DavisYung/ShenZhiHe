# -*- coding: utf-8 -*-
"""生成每年一份的映射子代理任务书 → f6chem/scratch/prompts/<year>.txt

任务书包含：输入文件路径、该年已有覆盖情况（跳过规则）、ref 约定、输出 schema、
OCR 纠错与自查纪律。子代理只需 read 对应任务书并照做。
用法：python f6chem/scratch/mk_prompts.py
"""
import io
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # f6chem
PP = os.path.join(BASE, "scratch", "pp")
OUT = os.path.join(BASE, "scratch", "prompts")
ALL_YEARS = [2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023]

qnums = json.load(io.open(os.path.join(PP, "existing_qnums.json"), encoding="utf-8"))

TPL = """# 任务：DSE 化学 {Y} 年试题 → 神智核知识点映射（含得分字眼）

你在为离线学习网站「神智核」重建高频考点数据。全站共 653 个知识点，每个有稳定 id。

## 输入文件（用 read 工具直接读；路径含中文可原样传）
- 卷一试题 OCR：{PP}/{Y}_p1.txt（=== page N === 分页；卷一 = 甲部选择题 + 乙部长题）
- 卷二试题 OCR：{PP}/{Y}_p2.txt（卷二 = 选修结构题，分甲/乙/丙三部，题号分部重启）
- 参考答案 OCR：{PP}/{Y}_ms.txt（提取得分字眼用；含卷一、卷二评分标准）
- 知识点总目录：{PP}/catalog.tsv（653 行；列 = point_id \\t 课题id \\t 章节标题 \\t 知识点标题 \\t 标签）
- 已有标注：{PP}/existing.json（point_id → {years, samples:[{y,ref}]}）
- 已有题号清单：{PP}/existing_qnums.json（年份 → 已标注过的题号）

## {Y} 年覆盖情况
{SKIP}

## 课题 id 对照
1a 地球 / 1b 微觀世界 / 1c 金屬 / 2a 酸和鹽基 / 2b 氧化還原 / 3a 有機化合物 /
3b 碳化合物的化學反應 / 3c 焓變 / 4a 反應速率 / 4b 化學平衡 / 6 工業化學 / 8 分析化學

## 要做的事
1. 读卷一、卷二 OCR，按题切分。单元粒度：选择题=整题；结构题=小问 (a)(b)…，
   若 (i)(ii) 小问考的知识点明显不同则再细分成 (i) 级。
2. 每个单元映射 1–3 个最贴切的 point_id。宁缺勿滥：没有真正对应的写 points: []，
   不许硬凑。只依据题目实际内容与目录标题/标签判断，别脑补。
3. 从 {Y}_ms.txt 找该题评分标准，提取「得分字眼」（评分要求写出的词/式/概念/结论，
   2–8 字词组；跳过「學生」「答案」这类通用词），按命中的 point_id 归进 kw。
   同一知识点已有字眼不必重复（合并端会去重）。
4. OCR 噪声自行纠正：雨→兩、什→什麼、须→須、NHs→NH3、Nz→N2、下标丢失、
   錯別字等，按化学常识还原题意后再判断考点。

## 输出
用 write 工具写 {MAP}/{Y}.json（UTF-8；不要经 PowerShell 管道传中文，防乱码）：

{
  "year": {Y},
  "mappings": [
    {"ref": "{Y}-P1A-Q12", "points": ["1c-s3-p2"], "focus": "實驗式與百分組成計算"},
    {"ref": "{Y}-P1B-Q1(a)", "points": ["4b-s2-p1"], "focus": "..."},
    {"ref": "{Y}-P2A-Q1(a)(iii)", "points": ["6-s3-p1", "4b-s4-p2"], "focus": "..."}
  ],
  "kw": {"1c-s3-p2": ["實驗式", "百分組成"]}
}

ref 约定：甲部选择 = {Y}-P1A-Q{n}；卷一乙部 = {Y}-P1B-Q{n}(小问链)；
卷二 = {Y}-P2{A|B|C}-Q{n}(小问链)。小问链把括号连写，如 (a)(i)。
focus 一到两句、约 20–60 字、繁体中文，说清考了什么
（风格参考既有标注，如「布朗運動與溫度的關係：液體溫度越高，動能越大，擴散越快」）。
kw 的 key 必须是本文件 mappings 里出现过的 point_id（或该年确实考过、目录里存在的 id）。

## 自查（写完必须做）
用 python（写成 .py 再执行，别走管道）验证：
1) json.load({MAP}/{Y}.json) 通过；
2) 全文无 \\ufffd；
3) mappings 里每个 point_id 都能在 catalog.tsv 找到；
4) 输出统计：mappings 条数、覆盖的题号范围、kw 涉及多少个 point_id。
把统计写进你的汇报。

## 纪律
- 只写 scratch/map/{Y}.json 这一个文件，不改 data/ 与其他任何文件。
- 精确 > 数量：错标比漏标更糟。
"""

SKIP_EXISTING = ("已有标注覆盖该年卷一甲部题号：{nums}。规则：\n"
                 "- 这些甲部题号**不要**重复输出（已标过，合并会去重但避免噪音）；\n"
                 "- 甲部里**不在**该清单的题号要补标（可能旧数据漏了）；\n"
                 "- 卷一乙部、卷二**全部**题都要标（旧口径从未覆盖）。")
SKIP_MISSING = ("该年**没有任何**已有标注：卷一甲部、卷一乙部、卷二全部题都要标。")


def main():
    os.makedirs(OUT, exist_ok=True)
    for y in ALL_YEARS:
        if str(y) in qnums:
            skip = SKIP_EXISTING.format(nums=qnums[str(y)])
        else:
            skip = SKIP_MISSING
        text = TPL.replace("{Y}", str(y)).replace("{PP}", PP).replace("{MAP}", os.path.join(BASE, "scratch", "map")).replace("{SKIP}", skip)
        with io.open(os.path.join(OUT, "%d.txt" % y), "w", encoding="utf-8") as f:
            f.write(text)
    print("written prompts for", len(ALL_YEARS), "years ->", OUT)


if __name__ == "__main__":
    main()
