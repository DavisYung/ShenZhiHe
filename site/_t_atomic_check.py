# -*- coding: utf-8 -*-
"""E2 原子世界知识点/测验校验器。

用法：
    python _t_atomic_check.py            # 校验已存在的 atomic*.json
    python _t_atomic_check.py --one 1    # 只校验 atomic1
"""
import io, json, os, re, sys

sys.stdout.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data", "phys")
QUIZ = os.path.join(ROOT, "quiz", "phys")
IMG = os.path.join(ROOT, "site", "img")
PAGES = os.path.join(ROOT, "pages", "atomic")

TARGETS = sys.argv[2].split(",") if len(sys.argv) > 2 and sys.argv[1] == "--one" else ["1", "2", "3"]

fails = []
warns = []
stats = {}


def load(p):
    with io.open(p, encoding="utf-8-sig") as f:
        return json.load(f)


def check_topic(tid):
    dp = os.path.join(DATA, tid + ".json")
    if not os.path.exists(dp):
        fails.append(f"{tid}: 数据档不存在")
        return None
    d = load(dp)
    npts = 0
    pages_used = set()

    for sec in d.get("sections", []):
        for pt in sec.get("points", []):
            npts += 1
            pid = pt.get("id", "?")
            body = pt.get("body") or ""

            # 1) 残留填空
            if re.search(r"_{3,}", body):
                fails.append(f"{pid}: 残留填空下划线")
            # 2) 乱码
            if "\ufffd" in body or "\ufffd" in pt.get("title", ""):
                fails.append(f"{pid}: 含乱码 U+FFFD")
            # 3) 我是谁 / 未替换占位
            if "TODO" in body or "???" in body:
                fails.append(f"{pid}: 含 TODO/???")
            # 4) 必需字段
            for k in ("id", "title", "page", "body"):
                if k not in pt:
                    fails.append(f"{pid}: 缺字段 {k}")
            # 5) tags
            if not pt.get("tags"):
                warns.append(f"{pid}: tags 为空")
            # 6) 页图引用：必须存在对应 webp，且页码与 page 字段一致
            imgs = re.findall(r"!\[[^\]]*\]\(([^)]+)\)", body)
            if not imgs:
                fails.append(f"{pid}: 没有页图引用")
            for src in imgs:
                for one in [x.strip() for x in src.split(",")]:
                    if not one:
                        continue
                    if not one.startswith("img/"):
                        fails.append(f"{pid}: 图片路径不是 img/ 开头 -> {one}")
                        continue
                    fp = os.path.join(ROOT, "site", one)
                    if not os.path.exists(fp):
                        fails.append(f"{pid}: 图片文件不存在 -> {one}")
                    m = re.search(r"phys_atomic_p(\d+)\.webp$", one)
                    if m:
                        pages_used.add(int(m.group(1)))
                    else:
                        fails.append(f"{pid}: 图片命名不符 phys_atomic_pNN.webp -> {one}")
            # 7) 图片行必须是整行独占（mdLite 的 IMG_LINE_RE 要求 ^...$）
            for line in body.split("\n"):
                if "![" in line:
                    if not re.match(r"^\s*!\[[^\]]*\]\([^)]*\)\s*$", line):
                        fails.append(f"{pid}: 图片行不是独占整行 -> {line[:60]}")
            # 8) 异体字检查
            if "温" in body and "溫" not in body:
                pass  # 「温和」等正确用法，不报

    # 页覆盖检查（单课题级只记页集，整门课级在下面统一比对）
    stats[tid] = {"points": npts, "pages": sorted(pages_used)}
    return d


def check_quiz(tid, topic):
    qp = os.path.join(QUIZ, tid + ".json")
    if not os.path.exists(qp):
        fails.append(f"{tid}: quiz 不存在")
        return
    q = load(qp)
    qs = q.get("questions", [])
    if not qs:
        fails.append(f"{tid}: quiz 没有题目")
        return
    # 收集所有知识点 id
    ptids = set()
    if topic:
        for sec in topic.get("sections", []):
            for pt in sec.get("points", []):
                ptids.add(pt["id"])
    for item in qs:
        qid = item.get("id", "?")
        t = item.get("type")
        # 题点引用必须有效
        pt = item.get("point")
        if not pt:
            fails.append(f"{tid}/{qid}: 缺 point 字段")
        elif pt not in ptids:
            fails.append(f"{tid}/{qid}: point 指向不存在的知识点 {pt}")
        if t == "mc":
            opts = item.get("options") or []
            if len(opts) < 2:
                fails.append(f"{tid}/{qid}: mc 选项少于 2 个")
            a = item.get("answer")
            if not isinstance(a, int) or a < 0 or a >= len(opts):
                fails.append(f"{tid}/{qid}: mc answer 索引越界 ({a} / {len(opts)})")
        elif t == "tf":
            if not isinstance(item.get("answer"), bool):
                fails.append(f"{tid}/{qid}: tf answer 不是布林值")
        else:
            fails.append(f"{tid}/{qid}: 未知题型 {t}")
        if not item.get("q"):
            fails.append(f"{tid}/{qid}: 缺题干 q")
        if not item.get("explanation"):
            warns.append(f"{tid}/{qid}: 缺 explanation")
        # 乱码
        blob = json.dumps(item, ensure_ascii=False)
        if "\ufffd" in blob:
            fails.append(f"{tid}/{qid}: 含乱码")
    stats[tid]["quiz"] = {
        "total": len(qs),
        "mc": sum(1 for x in qs if x.get("type") == "mc"),
        "tf": sum(1 for x in qs if x.get("type") == "tf"),
    }


print("=" * 62)
print("E2 原子世界 校验")
print("=" * 62)

for n in TARGETS:
    tid = "atomic" + n
    topic = check_topic(tid)
    if topic:
        check_quiz(tid, topic)

print()
for tid, s in sorted(stats.items()):
    q = s.get("quiz", {})
    print(f"{tid}: 知识点 {s['points']} · 页 {len(s['pages'])} 页 "
          f"({s['pages'][0] if s['pages'] else '-'}-{s['pages'][-1] if s['pages'] else '-'}) · "
          f"题 {q.get('total', 0)} (MC{q.get('mc', 0)}/TF{q.get('tf', 0)})")

# 整门课页覆盖（跨课题合并）
# 边界以工作纸实际印的页码为准，不是答案本的标注：
#   第1课 p1-14；第2课 p15-27（含 2.2 B 的 p27）；第3课 p28-39
RANGES = {"atomic1": (1, 14), "atomic2": (15, 27), "atomic3": (28, 39)}
print()
for tid in sorted(stats):
    lo, hi = RANGES.get(tid, (0, 0))
    if not lo:
        continue
    have = set(stats[tid]["pages"])
    miss = [p for p in range(lo, hi + 1) if p not in have]
    total = hi - lo + 1
    got = total - len(miss)
    flag = "OK " if not miss else "!! "
    print(f"[{flag}] {tid} 页覆盖 {got}/{total} ({lo}-{hi})" +
          (f"  缺 {miss}" if miss else ""))
    if miss:
        warns.append(f"{tid}: 整门课缺页 {miss}")

print()
if warns:
    print(f"[WARN] {len(warns)} 项：")
    for w in warns[:40]:
        print("  " + w)
    if len(warns) > 40:
        print(f"  ... 其余 {len(warns)-40} 项略")
print()
if fails:
    print(f"[FAIL] {len(fails)} 项：")
    for x in fails[:60]:
        print("  " + x)
    if len(fails) > 60:
        print(f"  ... 其余 {len(fails)-60} 项略")
    sys.exit(1)
print(f"[OK] 全部通过（{sum(s['points'] for s in stats.values())} 知识点，"
      f"{sum(s.get('quiz',{}).get('total',0) for s in stats.values())} 题）")
