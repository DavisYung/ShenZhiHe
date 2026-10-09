# -*- coding: utf-8 -*-
"""按 DeepSeek 官方定价精确估算花费（修正高峰时段定义）。

官方定价（元/百万 token，来源 api-docs.deepseek.com 定价页 2026-10 抓取）：
  deepseek-flash（= DeepSeek-V4.1-Flash）
    缓存命中输入：空闲 0.02 / 高峰 0.04
    缓存未命中输入：空闲 1 / 高峰 2
    输出：空闲 4 / 高峰 8
  高峰时段 = 北京时间**周一至周五**（不含法定节假日）09:00–12:00 与 14:00–18:00
  其余（12:00–14:00 午休、18:00–次日 09:00、周末全天）都是空闲时段（半价）

口径：stats.json 的 input 已是「缓存未命中」口径，cacheRead 单列，output 含思考。
"""
import io
import json
import os
import sys
from collections import defaultdict
from datetime import datetime, timedelta

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

PRICE = {
    "hit":  {"low": 0.02, "high": 0.04},
    "in":   {"low": 1.0,  "high": 2.0},
    "out":  {"low": 4.0,  "high": 8.0},
}
USD = 7.1


def is_peak(dt):
    """北京时间周一至周五 9-12、14-18 为高峰。"""
    if dt.weekday() >= 5:          # 周六日全天空闲
        return False
    m = dt.hour * 60 + dt.minute
    return (9 * 60 <= m < 12 * 60) or (14 * 60 <= m < 18 * 60)


def cost(tin, thit, tout, frac_peak):
    """frac_peak = 落在高峰时段的 token 比例"""
    lo = 1 - frac_peak
    return (
        tin / 1e6 * (PRICE["in"]["high"] * frac_peak + PRICE["in"]["low"] * lo)
        + thit / 1e6 * (PRICE["hit"]["high"] * frac_peak + PRICE["hit"]["low"] * lo)
        + tout / 1e6 * (PRICE["out"]["high"] * frac_peak + PRICE["out"]["low"] * lo)
    )


def fmt(x):
    return "{:,.2f}".format(x)


stats = json.load(io.open(os.path.join(os.environ["DSH_HOME"], "our-free-model",
                                       "stats.json"), encoding="utf-8"))

# 1) 全期总量
TOT = {"input": 0, "output": 0, "cacheRead": 0, "calls": 0}
for day, rec in stats["days"].items():
    for mid, r in (rec.get("models") or {}).items():
        TOT["input"] += r.get("input", 0)
        TOT["output"] += r.get("output", 0)
        TOT["cacheRead"] += r.get("cacheRead", 0)
        TOT["calls"] += r.get("calls", 0)

# 2) 用 samples 的精确时间戳估算高峰占比
s = stats.get("samples") or []
hi_tok = lo_tok = 0
hi_n = lo_n = 0
per_hour = defaultdict(int)
for x in s:
    ts = x.get("at")
    if not ts:
        continue
    dt = datetime.fromtimestamp(ts / 1000)
    tok = x.get("input", 0) + x.get("output", 0)
    per_hour[dt.hour] += 1
    if is_peak(dt):
        hi_tok += tok
        hi_n += 1
    else:
        lo_tok += tok
        lo_n += 1

frac_peak = (hi_tok / (hi_tok + lo_tok)) if (hi_tok + lo_tok) else 0.0

print("=" * 70)
print("DeepSeek V4.1 Flash（官方定价）估算")
print("=" * 70)
print("计费 token 全期累计：")
print("  缓存未命中输入 : %14s" % format(TOT["input"], ","))
print("  缓存命中输入   : %14s" % format(TOT["cacheRead"], ","))
print("  输出（含思考） : %14s" % format(TOT["output"], ","))
print("  总调用次数     : %14s" % format(TOT["calls"], ","))
print()

print("高峰时段占比（按最近 %d 次调用的真实时间戳）：" % len(s))
print("  高峰 %d 次 / 空闲 %d 次  →  高峰 token 占比 %.1f%%"
      % (hi_n, lo_n, 100 * frac_peak))
print("  样本时段分布：", ", ".join("%02d时×%d" % (h, c) for h, c in sorted(per_hour.items())))
print()

c_actual = cost(TOT["input"], TOT["cacheRead"], TOT["output"], frac_peak)
c_allhi = cost(TOT["input"], TOT["cacheRead"], TOT["output"], 1.0)
c_alllo = cost(TOT["input"], TOT["cacheRead"], TOT["output"], 0.0)

print("全期总花费（人民币）：")
print("  按实际时段分布 : ¥%9s   (≈ $%s)" % (fmt(c_actual), fmt(c_actual / USD)))
print("  若全在高峰     : ¥%9s   (≈ $%s)" % (fmt(c_allhi), fmt(c_allhi / USD)))
print("  若全在空闲     : ¥%9s   (≈ $%s)" % (fmt(c_alllo), fmt(c_alllo / USD)))
print()

print("--- 按实际分布分项 ---")
def part(unit, key):
    hi = PRICE[key]["high"] * frac_peak
    lo = PRICE[key]["low"] * (1 - frac_peak)
    return unit / 1e6 * (hi + lo)

p_in = part(TOT["input"], "in")
p_hit = part(TOT["cacheRead"], "hit")
p_out = part(TOT["output"], "out")
for name, v in (("未命中输入", p_in), ("缓存命中", p_hit), ("输出", p_out)):
    print("  %-10s ¥%9s  (%4.1f%%)" % (name, fmt(v), 100 * v / c_actual))
print()

# 3) 只看真正跑在 v4.1-flash 上的量
ds = None
for day, rec in stats["days"].items():
    r = (rec.get("models") or {}).get("deepseek-ai/deepseek-v4.1-flash")
    if r:
        if ds is None:
            ds = {"input": 0, "output": 0, "cacheRead": 0, "calls": 0}
        for k in ds:
            ds[k] += r.get(k, 0)
if ds:
    d = cost(ds["input"], ds["cacheRead"], ds["output"], frac_peak)
    print("--- 仅 deepseek-ai/deepseek-v4.1-flash 这一个模型 ---")
    print("  in=%s  cache=%s  out=%s  calls=%s"
          % (format(ds["input"], ","), format(ds["cacheRead"], ","),
             format(ds["output"], ","), ds["calls"]))
    print("  ¥%s  (≈ $%s)" % (fmt(d), fmt(d / USD)))
