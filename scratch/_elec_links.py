# -*- coding: utf-8 -*-
"""把电学六课的跨课题串连追加进 data/phys/links.json。

电学内部：按「静电场→电路→功率→磁→电磁感应→交流电」的知识链条串起。
跨科：接到力学的功/能量/力矩、热学的内能与热效应。
"""
import io
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LINKS = os.path.join(BASE, "data", "phys", "links.json")

with io.open(LINKS, encoding="utf-8") as f:
    links = json.load(f)

old = len(links)
existing = {(l.get("from"), l.get("to")) for l in links}

new_links = [
  # ---------- 电学内部 ----------
  {"from": "elec1-s1-p1", "to": "elec1-s1-p4", "label": "电子是起电时转移的粒子"},
  {"from": "elec1-s1-p4", "to": "elec1-s1-p5", "label": "电荷守恒是三种起电方式的共同基础"},
  {"from": "elec1-s1-p3", "to": "elec1-s1-p5", "label": "感生电荷与感应起电是同一机制"},
  {"from": "elec1-s1-p2", "to": "elec2-s1-p1", "label": "金属的自由电子就是电路里的载流子"},
  {"from": "elec1-s1-p5", "to": "elec1-s3-p1", "label": "起电量多少由库伦定律决定"},
  {"from": "elec1-s2-p1", "to": "elec1-s4-p1", "label": "电场力线的疏密正是电场强度的几何意义"},
  {"from": "elec1-s3-p1", "to": "elec1-s4-p1", "label": "由库伦力推出点电荷的电场强度"},
  {"from": "elec1-s4-p1", "to": "elec1-s5-p1", "label": "电荷在电场中移动就有电势能变化"},
  {"from": "elec1-s4-p3", "to": "elec1-s5-p1", "label": "匀强电场中静电力平衡重力"},
  {"from": "elec1-s4-p1", "to": "elec2-s2-p1", "label": "E = V/d 把电场与电路电压连起来"},
  {"from": "elec1-s1-p1", "to": "elec1-s4-p2", "label": "电子的电量与质量用于电场计算"},

  {"from": "elec2-s1-p1", "to": "elec2-s2-p1", "label": "电流是电荷流率，电压是每单位电荷的能量"},
  {"from": "elec2-s1-p2", "to": "elec2-s4-p1", "label": "串联电流相等是串联合并电阻的前提"},
  {"from": "elec2-s2-p2", "to": "elec2-s3-p1", "label": "由 V 和 I 的定义直接得 R = V/I"},
  {"from": "elec2-s3-p2", "to": "elec2-s3-p3", "label": "欧姆定律的定值前提与电阻率公式都是定值电阻"},
  {"from": "elec2-s3-p3", "to": "elec2-s4-p1", "label": "R = ρl/A 解释了为何串联等效电阻变长变大"},
  {"from": "elec2-s3-p3", "to": "elec2-s4-p2", "label": "R = ρl/A 解释了为何并联等效电阻变粗变小"},
  {"from": "elec2-s4-p1", "to": "elec2-s4-p3", "label": "串联与并联公式是解混合电路的积木"},
  {"from": "elec2-s4-p2", "to": "elec2-s4-p4", "label": "并联电阻愈小电流愈大正是短路的原因"},
  {"from": "elec2-s5-p2", "to": "elec2-s3-p1", "label": "内电阻让 R = V/I 量到的不是定值"},
  {"from": "elec2-s5-p1", "to": "elec2-s5-p2", "label": "仪表与电源的内电阻是同一类系统误差"},

  {"from": "elec3-s1-p1", "to": "elec3-s1-p2", "label": "P = VI 代入 V = IR 得另两个功率公式"},
  {"from": "elec3-s1-p2", "to": "elec3-s1-p4", "label": "功率乘以时间就是电能"},
  {"from": "elec3-s1-p3", "to": "elec3-s2-p2", "label": "由额定功率算额定电流才能选保险丝"},
  {"from": "elec3-s1-p3", "to": "elec6-s1-p2", "label": "市电功率用方均根电压与电流计算"},
  {"from": "elec3-s1-p4", "to": "elec6-s2-p3", "label": "千瓦时计量的电能正是高压输电要减少损耗的那部分"},
  {"from": "elec3-s2-p1", "to": "elec6-s1-p1", "label": "市电就是220V、50Hz的正弦交流电"},
  {"from": "elec3-s2-p3", "to": "elec3-s2-p4", "label": "地线与环形干线都是家居安全布置"},
  {"from": "elec3-s1-p1", "to": "elec4-s4-p3", "label": "电流的热效应与磁力计算都从电流出发"},

  {"from": "elec4-s1-p1", "to": "elec4-s1-p2", "label": "磁力线是描述磁场方向与强弱的工具"},
  {"from": "elec4-s1-p2", "to": "elec4-s2-p1", "label": "磁力线与电力线的画法与性质完全平行"},
  {"from": "elec4-s2-p1", "to": "elec4-s2-p2", "label": "由长直导线的右手定则推广到螺线管"},
  {"from": "elec4-s2-p2", "to": "elec4-s3-p1", "label": "螺线管结构与 B = μ₀NI/l 一一对应"},
  {"from": "elec4-s3-p1", "to": "elec4-s4-p4", "label": "两条导线的磁力由 B = μ₀I/2πr 算出"},
  {"from": "elec4-s4-p1", "to": "elec4-s4-p3", "label": "左手定则定方向，F = BIl sin θ 定量值"},
  {"from": "elec4-s4-p3", "to": "elec4-s5-p1", "label": "BIl 与 BQv 是同一力的宏观与微观表述"},
  {"from": "elec4-s5-p1", "to": "elec4-s5-p2", "label": "磁力提供向心力使电荷作圆周运动"},
  {"from": "elec4-s4-p5", "to": "elec4-s5-p2", "label": "电动机的力偶与移动电荷的圆周运动都源于同一磁力"},
  {"from": "elec4-s1-p2", "to": "elec4-s4-p2", "label": "平板形磁铁间的匀强磁场是电流天平的标准装置"},

  {"from": "elec5-s1-p1", "to": "elec5-s1-p2", "label": "磁通量变化是现象，法拉第定律是它的量度"},
  {"from": "elec5-s1-p2", "to": "elec5-s1-p3", "label": "法拉第定大小，楞次定方向"},
  {"from": "elec5-s1-p2", "to": "elec5-s2-p1", "label": "变化率快慢要用磁通量来表述"},
  {"from": "elec5-s2-p1", "to": "elec5-s2-p2", "label": "磁通匝链数 NΦ 正是法拉第公式里的量"},
  {"from": "elec5-s2-p2", "to": "elec5-s3-p1", "label": "感应电动势抵不过恒定磁场，故探察线圈只能测变化磁场"},
  {"from": "elec5-s3-p1", "to": "elec5-s3-p2", "label": "探察线圈测频率，发电机正是产生交流电的装置"},
  {"from": "elec4-s4-p5", "to": "elec5-s3-p2", "label": "电动机与发电机结构相同、原理相反"},
  {"from": "elec5-s3-p2", "to": "elec6-s1-p1", "label": "发电机产生的正是方向周期性改变的交流电"},
  {"from": "elec4-s1-p2", "to": "elec4-s5-p2", "label": "粒子走半圆的磁场来自匀强磁场"},
  {"from": "elec5-s2-p1", "to": "elec5-s2-p2", "label": "磁通匝链数变化产生感应电动势"},
  {"from": "elec5-s2-p1", "to": "elec4-s5-p1", "label": "磁通量与磁力都是 B 的两种表现"},
  {"from": "elec5-s2-p1", "to": "elec4-s3-p1", "label": "磁通量与 B 通过 Φ = BA 换算"},
  {"from": "elec5-s2-p2", "to": "elec5-s3-p2", "label": "法拉第定律是发电机产生电动势的原理"},
  {"from": "elec2-s4-p2", "to": "elec5-s2-p1", "label": "并联电阻愈小电流愈大正是短路的原因"},

  # ---------- 跨科：电学 → 力学 / 热学 ----------
  {"from": "elec2-s5-p2", "to": "mech6-s1-p1", "label": "ε = V + Ir 与端电压都是电压的分配"},
  {"from": "elec1-s5-p1", "to": "mech6-s1-p1", "label": "电势能变化 = 外力所作的功，与功的定义一致"},
  {"from": "elec1-s5-p1", "to": "mech6-s1-p2", "label": "電勢能變化 = 外力所作的功，與功的定義一致"},
  {"from": "elec3-s1-p1", "to": "mech6-s1-p1", "label": "功率 = 能量/时间，与力学功率同一定义"},
  {"from": "elec3-s1-p1", "to": "heat2-s2-p1", "label": "电流的热效应使导体获得内能"},
  {"from": "elec3-s1-p4", "to": "heat2-s1-p2", "label": "电能以焦耳或千瓦小时计量"},
  {"from": "elec3-s2-p4", "to": "mech5-s1-p1", "label": "断路口与力矩平衡都涉及自动切断机制"},
  {"from": "elec4-s4-p2", "to": "mech5-s1-p1", "label": "電流量度裝置是運用電磁感應原理"},
  {"from": "elec4-s4-p5", "to": "mech5-s1-p3", "label": "電動機的力偶是力矩與力偶的應用"},
  {"from": "elec4-s5-p2", "to": "mech4-s1-p1", "label": "磁力提供向心力，与圆周运动同学"},
  {"from": "elec5-s2-p2", "to": "mech6-s1-p2", "label": "電磁阻尼把動能轉為電能再轉為熱"},

  # ---------- 跨科：电学 → 热学 ----------
  {"from": "elec2-s3-p2", "to": "heat2-s1-p2", "label": "金属电阻随温度升高而增大（温度影响电阻）"},
  {"from": "elec2-s3-p3", "to": "heat3-s1-p2", "label": "电流的热效应令导体温度上升"},
  {"from": "elec3-s1-p2", "to": "heat3-s1-p2", "label": "电功率通过 I²R 转为内能（热效应）"},
  {"from": "elec3-s1-p4", "to": "heat2-s1-p2", "label": "电热水器用电能增加水的内能"},
  {"from": "elec5-s3-p2", "to": "heat3-s1-p2", "label": "涡电流的热效应用于电磁炉加热"},
  {"from": "elec6-s2-p2", "to": "heat4-s3-p1", "label": "变压器铁心发热就是能量以热形式散失"},
]

added = 0
for l in new_links:
    key = (l.get("from"), l.get("to"))
    if key in existing:
        continue
    links.append(l)
    existing.add(key)
    added += 1

with io.open(LINKS, "w", encoding="utf-8") as f:
    json.dump(links, f, ensure_ascii=False, indent=1)
    f.write("\n")

print("原有 %d 条，新增 %d 条，现有 %d 条" % (old, added, len(links)))

# 自检：引用的知识点 id 必须存在
ids = set()
for sub in ("data/phys",):
    d = os.path.join(BASE, sub)
    for n in sorted(os.listdir(d)):
        if n.startswith("elec") and n.endswith(".json"):
            t = json.load(io.open(os.path.join(d, n), encoding="utf-8"))
            for s in t.get("sections") or []:
                for pt in s.get("points") or []:
                    ids.add(pt.get("id"))
missing = set()
for l in links:
    for k in ("from", "to"):
        if l[k] not in ids and l[k].startswith("elec"):
            missing.add(l[k])
# 也允许跨科指向其它课题，这里只查电学的
allids = set()
for sub in ("data/phys",):
    d = os.path.join(BASE, sub)
    for n in sorted(os.listdir(d)):
        if n.endswith(".json") and n not in ("subject.json",):
            try:
                t = json.load(io.open(os.path.join(d, n), encoding="utf-8"))
            except Exception:
                continue
            if not isinstance(t, dict):
                continue
            for s in t.get("sections") or []:
                for pt in s.get("points") or []:
                    allids.add(pt.get("id"))
bad = set()
for l in links:
    for k in ("from", "to"):
        if l[k].startswith("elec") and l[k] not in allids:
            bad.add(l[k])
print("电学知识点 id %d 个" % len(ids))
if bad:
    print("引用了不存在的电学 id: %s" % ", ".join(sorted(bad)))
    sys.exit(1)
print("自检通过")