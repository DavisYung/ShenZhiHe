# -*- coding: utf-8 -*-
"""用字规范化：把 PDF 抽取出来的异体字统一成香港繁体标准字形。

背景（实测数据）：
    PDF 原文用「温」(U+6E29, 日韩字形) 131 次、「溫」(U+6EAB) 0 次；
    而化学区 12 份资料全部用「溫」(U+6EAB) 389 次、零例外。
    若不统一，物理区会与化学区字形不一致，搜索也会漏命中。

只处理「同一字的不同字形」这类安全问题，不做简繁转换（那会改动语义）。
本模块被转录与校验脚本共用。
"""
import re

# 实测需要替换的异体字（左：PDF 常见，右：香港标准）
REPLACE = {
    "\u6e29": "\u6eab",   # 温 → 溫
    "\u8aa4": "\u8aa4",   # 誤（占位，保持）
    "\u9ad4": "\u9ad4",   # 體（占位，保持）
}

# 只保留真正有差異的
REPLACE = {a: b for a, b in REPLACE.items() if a != b}

# PDF 抽取的頁眉頁腳等噪音行
NOISE_PATTERNS = [
    re.compile(r"^新高中生活與物理（第二版）\s*$"),
    re.compile(r"^課堂工作紙\s*\d*\s*$"),
    re.compile(r"^牛津大學出版社\s*\d{4}\s*$"),
    re.compile(r"^\s*\d{1,3}\s*$"),          # 單獨的頁碼
    re.compile(r"^Name\s*:.*$"),
    re.compile(r"^Class\s*:.*$"),
    re.compile(r"^\s*©.*$"),
]


def normalize_text(s):
    """把異體字統一為香港繁體標準字形。"""
    if not s:
        return s
    for a, b in REPLACE.items():
        s = s.replace(a, b)
    return s


def is_noise(line):
    """判斷是否為頁眉頁腳等噪音行。"""
    s = line.strip()
    if not s:
        return True
    return any(p.match(s) for p in NOISE_PATTERNS)


def check_variants(s):
    """回報殘留的異體字，供驗證腳本使用。"""
    return {a: s.count(a) for a in REPLACE if s.count(a)}


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8")
    t = "温度與温度計"
    print("原文  :", t)
    print("規範後:", normalize_text(t))
    print("殘留  :", check_variants(normalize_text(t)) or "無")
