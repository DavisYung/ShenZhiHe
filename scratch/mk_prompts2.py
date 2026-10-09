# -*- coding: utf-8 -*-
"""生成拆分版映射任务书 → f6chem/scratch/prompts2/<年>_<part>.txt

每年 3 个小任务（防子代理上下文爆掉，上一轮整年任务 8/8 全灭）：
  p1a = 卷一甲部选择题映射（无 kw——选择题评分只有答案字母）
  p1b = 卷一乙部结构题映射 + 得分字眼（读 ms 的卷一部分）
  p2  = 卷二选修结构题映射 + 得分字眼（读 ms 的卷二部分）
用法：python f6chem/scratch/mk_prompts2.py
"""
import io
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # f6chem
PP = os.path.join(BASE, "scratch", "pp")
OUT = os.path.join(BASE, "scratch", "prompts2")
MAP = os.path.join(BASE, "scratch", "map")
ALL_YEARS = [2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023]

qnums = json.load(io.open(os.path.join(PP, "existing_qnums.json"), encoding="utf-8"))

TOPIC_LINE = ("课题 id 对照：1a 地球 / 1b 微觀世界 / 1c 金屬 / 2a 酸和鹽基 / 2b 氧化還原 / "
              "3a 有機化合物 / 3b 碳化合物的化學反應 / 3c 焓變 / 4a 反應速率 / 4b 化學平衡 / "
              "6 工業化學 / 8 分析化學")
DISC = ("纪律：只读任务书列出的文件；不在回复里复述题目或目录原文（省上下文）；"
        "自查脚本先用 write 落 .py 再运行（PowerShell 无 heredoc，管道传中文会乱码），"
        "python 路径 C:\\Users\\guomi\\.dsh\\dsh-runtimes\\dsh-primary-runtime\\dependencies\\python\\python.exe；"
        "产出只写 map 目录里的一个 json。")

TPL_P1A = """# 任务：DSE 化学 {Y} 年卷一甲部选择题 → 知识点映射（神智核项目 · 无得分字眼）

## 输入（只读这两个文件，别的都不要读）
- 知识点目录（653 行，列=point_id \\t 课题id \\t 章节标题 \\t 知识点标题 \\t 标签）：
  {PP}\\catalog.tsv
- {Y} 年卷一甲部 OCR：{PP}\\{Y}_p1_mc.txt（=== page N === 分页，末尾有「甲部完」）

## 已有覆盖（跳过清单）
{SKIP}

## {TOPIC}

## 做法
1. 逐题映射：每道选择题 → 1–3 个最贴切 point_id；没有真正对应的写 []（旧纲要题对不上很正常）。
   只依据题目内容与目录标题/标签判断，别脑补；OCR 错字自行还原（雨→兩、NHs→NH3、Nz→N2 等）。
2. focus ≤30 字、繁体中文，一句话说清考什么（例：「布朗運動與溫度的關係」）。
3. 选择题没有得分字眼，kw 不用做。

## 输出（分三段累积写，防上下文爆掉）
产出：{MAP}\\{Y}_p1a.json
- 做完 Q1–12 就 write 该文件（只含前 12 条）；做完 13–24、25–36 各再整体重写一次（累积全部）。
格式：
{
  "year": {Y},
  "mappings": [
    {"ref": "{Y}-P1A-Q1", "points": ["1c-s2-p1"], "focus": "...."}
  ]
}
ref 一律 {Y}-P1A-Q{n}，n 用卷子实际题号。

## 自查与汇报
写完用 python 验证：json.load 通过、全文无 \\ufffd、points id 都能在 catalog.tsv 找到。
汇报一行：单元数 / 空映射数 / 覆盖题号范围。
{DISC}
"""

TPL_P1B = """# 任务：DSE 化学 {Y} 年卷一乙部（结构题）→ 知识点映射 + 得分字眼（神智核项目）

## 输入（只读这三个文件）
- 知识点目录（653 行，列=point_id \\t 课题id \\t 章节标题 \\t 知识点标题 \\t 标签）：
  {PP}\\catalog.tsv
- {Y} 年卷一乙部 OCR：{PP}\\{Y}_p1_b.txt
- {Y} 年卷一评分标准 OCR：{PP}\\{Y}_ms_p1.txt（开头的甲部答案表可跳过；重点是乙部各题评分）

## 说明
- 乙部所有题都要标（网站旧数据从未覆盖乙部）。
- 单元粒度 = 小问 (a)(b)…；(i)(ii) 若考点明显不同再细分。
- 每单元 1–3 个最贴切 point_id，没有对应的写 []；focus ≤40 字繁体中文。
- kw 从评分标准提：评分要求写出的词/式/概念/结论（2–8 字词组），跳过「學生」类通用词；
  评分标准稀疏的题就少提或不提，绝不编造。

## {TOPIC}

## 输出（每做完 3–4 题就整体重写一次，防上下文爆掉）
产出：{MAP}\\{Y}_p1b.json
{
  "year": {Y},
  "mappings": [
    {"ref": "{Y}-P1B-Q1(a)", "points": ["..."], "focus": "..."}
  ],
  "kw": {"<point_id>": ["字眼1", "字眼2"]}
}
ref 一律 {Y}-P1B-Q{n}(小问链)，n 用卷子实际题号；小问链括号连写如 (a)(i)。
kw 的 key 必须是本任务 mappings 出现过的 point_id。

## 自查与汇报
写完用 python 验证：json.load 通过、无 \\ufffd、points id 在 catalog.tsv 里。
汇报一行：单元数 / 覆盖题号 / kw 点数。
{DISC}
"""

TPL_P2 = """# 任务：DSE 化学 {Y} 年卷二（选修结构题）→ 知识点映射 + 得分字眼（神智核项目）

## 输入（只读这三个文件）
- 知识点目录（653 行，列=point_id \\t 课题id \\t 章节标题 \\t 知识点标题 \\t 标签）：
  {PP}\\catalog.tsv
- {Y} 年卷二 OCR：{PP}\\{Y}_p2.txt
- {Y} 年卷二评分标准 OCR：{PP}\\{Y}_ms_p2.txt

## 说明
- 卷二 = 甲/乙/丙三部各一大题，题号实测是 1/2/3 连续（以卷子实际编号为准，别假设分部重启）。
- 单元 = 小问 (a)(b)(i)…（考点明显不同才细分到 (i) 级）；每单元 1–3 个 point_id；
  focus ≤40 字繁体中文。
- 内容多为工业化学/分析化学（课题 6/8），也有反应速率(4a)、平衡(4b)、有机(3a/3b)、焓變(3c)——按内容定。
- kw 从评分标准提（2–8 字词组，跳过通用词，稀疏就少提，不编造）。

## {TOPIC}

## 输出（每做完一题就整体重写一次，防上下文爆掉）
产出：{MAP}\\{Y}_p2.json
{
  "year": {Y},
  "mappings": [
    {"ref": "{Y}-P2A-Q1(a)(i)", "points": ["..."], "focus": "..."}
  ],
  "kw": {"<point_id>": ["字眼1"]}
}
ref 一律 {Y}-P2{A|B|C}-Q{n}(小问链)：节号看部标题（甲=A 乙=B 丙=C），题号用实际数字。
kw 的 key 必须是本任务 mappings 出现过的 point_id。

## 自查与汇报
写完用 python 验证：json.load 通过、无 \\ufffd、points id 在 catalog.tsv 里。
汇报一行：单元数 / 覆盖题号 / kw 点数。
{DISC}
"""

SKIP_ALL = "该年无任何既有标注：全部题号都要输出。"
SKIP_EXIST = ("已有标注覆盖甲部题号 {nums}：清单内的题号跳过、不输出；"
              "清单外的题号（如 25–36）必须输出。卷一乙部与卷二属于本系列其他任务，本任务别管。")


def main():
    os.makedirs(OUT, exist_ok=True)
    n = 0
    for y in ALL_YEARS:
        ys = str(y)
        skip = SKIP_EXIST.format(nums=qnums[ys]) if ys in qnums else SKIP_ALL
        common = {"{Y}": ys, "{PP}": PP, "{MAP}": MAP, "{TOPIC}": TOPIC_LINE,
                  "{DISC}": DISC, "{SKIP}": skip}
        for part, tpl in (("p1a", TPL_P1A), ("p1b", TPL_P1B), ("p2", TPL_P2)):
            text = tpl
            for k, v in common.items():
                text = text.replace(k, v)
            with io.open(os.path.join(OUT, "%d_%s.txt" % (y, part)), "w",
                         encoding="utf-8") as f:
                f.write(text)
            n += 1
    print("written %d prompts -> %s" % (n, OUT))


if __name__ == "__main__":
    main()
