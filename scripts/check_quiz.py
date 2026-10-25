# -*- coding: utf-8 -*-
"""課題測驗題自檢：新增／修改 `quiz/<科目>/<課題>.json` 後跑一遍。

为什么需要它：
  测验题是**手写 JSON**，写错了不会有任何报错，只会静默变成：
    * 界面上选项少一个、答案对不上题号
    * 题目挂在不存在的话题上，学生永远看不到
    * 两个题目共用同一个 id，错题本会记错

用法：
  python scripts/check_quiz.py                 # 检查全部
  python scripts/check_quiz.py quiz/phys       # 只查某个科目
  python scripts/check_quiz.py --quiet         # 只输出问题

退出码：0 = 无错误；1 = 有错误。
"""
import io
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # f6chem/
TYPES = {"mc", "tf", "fill"}

errors = []
warns = []
stats = {}


def err(m):
    errors.append(m)


def warn(m):
    warns.append(m)


def load(p):
    with io.open(p, encoding="utf-8") as f:
        return json.load(f)


def point_index():
    """收集 data/<sid>/<tid>.json 里所有知识点 id → {point_id: topic_id}。"""
    idx = {}
    d = os.path.join(BASE, "data")
    for sid in os.listdir(d):
        sd = os.path.join(d, sid)
        if not os.path.isdir(sd):
            continue
        for fn in os.listdir(sd):
            if not fn.endswith(".json") or fn.startswith("_") or ".bak" in fn:
                continue
            if fn in ("subject.json", "links.json"):
                continue
            try:
                doc = load(os.path.join(sd, fn))
            except Exception:
                continue
            if not isinstance(doc, dict):
                continue
            tid = doc.get("id") or fn[:-5]
            for sec in doc.get("sections") or []:
                for p in sec.get("points") or []:
                    if p.get("id"):
                        idx[p["id"]] = tid
    return idx


def check_file(path, points):
    sid = os.path.basename(os.path.dirname(path))
    tid = os.path.basename(path)[:-5]
    rel = os.path.relpath(path, BASE).replace(os.sep, "/")
    try:
        doc = load(path)
    except Exception as e:
        err("%s 解析失败：%s" % (rel, e))
        return 0
    if not isinstance(doc, dict):
        err("%s 顶层应为对象" % rel)
        return 0
    if doc.get("topic") != tid:
        warn("%s 的 topic=%r 与文件名 %r 不一致" % (rel, doc.get("topic"), tid))
    qs = doc.get("questions")
    if not isinstance(qs, list) or not qs:
        err("%s 没有 questions 数组" % rel)
        return 0

    seen = set()
    for i, q in enumerate(qs):
        qid = q.get("id") or "<第%d题无id>" % (i + 1)
        tag = "%s %s" % (rel, qid)

        for k in ("id", "type", "q", "answer"):
            if k not in q:
                err("%s 缺字段 `%s`" % (tag, k))

        if qid in seen:
            err("%s id 重复" % tag)
        seen.add(qid)

        # id 建议格式 <topic>-q<N>
        if q.get("id") and not re.fullmatch(re.escape(tid) + r"-q\d+", str(q["id"])):
            warn("%s id 格式建议为 `%s-q<N>`" % (tag, tid))

        t = q.get("type")
        if t not in TYPES:
            err("%s type=%r 不是 %s 之一" % (tag, t, "/".join(sorted(TYPES))))
            continue

        # 题干
        if not str(q.get("q") or "").strip():
            err("%s 题干为空" % tag)

        # 题解
        ex = str(q.get("explanation") or "").strip()
        if not ex:
            err("%s 没有题解（学生点开是空的）" % tag)
        elif len(ex) < 15:
            warn("%s 题解只有 %d 字，疑似没写完" % (tag, len(ex)))

        # 知识点归属
        pt = q.get("point")
        if not pt:
            warn("%s 没有 point，无法从笔记跳转" % tag)
        elif points and pt not in points:
            err("%s 的 point=%r 在 data/ 里找不到对应知识点" % (tag, pt))
        elif points and points[pt] != tid:
            warn("%s 的 point 属于课题 %s，但本题在 %s" % (tag, points[pt], tid))

        # 分类型校验
        opts = q.get("options")
        if t == "mc":
            if not isinstance(opts, list) or len(opts) != 4:
                err("%s 选择题应有 4 个选项，实际 %s（界面会显示成 E 选项）"
                    % (tag, len(opts) if isinstance(opts, list) else "无"))
            if not isinstance(q.get("answer"), int):
                err("%s 选择题 answer 应为索引整数 0–3，实际 %r" % (tag, q.get("answer")))
            elif isinstance(opts, list) and not (0 <= q["answer"] < len(opts)):
                err("%s 的 answer=%d 超出选项范围" % (tag, q["answer"]))
            if isinstance(opts, list):
                for j, o in enumerate(opts):
                    if not str(o or "").strip():
                        err("%s 第 %d 个选项为空" % (tag, j + 1))
                if len(set(str(o) for o in opts)) != len(opts):
                    err("%s 有重复选项" % tag)
        elif t == "tf":
            if not isinstance(q.get("answer"), bool):
                err("%s 判断题 answer 应为 true/false，实际 %r" % (tag, q.get("answer")))
        elif t == "fill":
            a = q.get("answer")
            if not isinstance(a, list) or not a:
                err("%s 填空题 answer 应为非空数组，实际 %r" % (tag, a))

    stats[sid] = stats.get(sid, 0) + len(qs)
    return len(qs)


def main():
    argv = [a for a in sys.argv[1:] if not a.startswith("--")]
    quiet = "--quiet" in sys.argv
    root = os.path.join(BASE, argv[0].replace("/", os.sep)) if argv else os.path.join(BASE, "quiz")
    if not os.path.isdir(root):
        print("✖ 找不到目录：%s" % root)
        return 1

    points = point_index()
    files = []
    for dirpath, _dirnames, filenames in os.walk(root):
        if "backup" in dirpath:
            continue
        for fn in sorted(filenames):
            if fn.endswith(".json") and not fn.startswith("_"):
                files.append(os.path.join(dirpath, fn))

    total = 0
    for p in files:
        total += check_file(p, points)

    if not quiet:
        print()
        for sid, n in sorted(stats.items()):
            print("  ✓ %-6s %d 题" % (sid, n))
        for m in warns:
            print("  ⚠ %s" % m)
        for m in errors:
            print("  ✖ %s" % m)
        print()

    if errors:
        print("✖ %d 个错误 / %d 个警告（共 %d 题，%d 个文件）—— 修完再提交。"
              % (len(errors), len(warns), total, len(files)))
        return 1
    if warns:
        print("✅ 无错误，%d 个警告（共 %d 题，%d 个文件）。" % (len(warns), total, len(files)))
        return 0
    print("✅ 全部通过（%d 题，%d 个文件）。" % (total, len(files)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
