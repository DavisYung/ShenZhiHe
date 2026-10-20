# -*- coding: utf-8 -*-
"""用 jsonschema 校验 data/ 与 quiz/ 的数据结构。

取代手写的一堆 if 判断：schema 集中定义「什么是合法数据」，
新增科目（力学、波动学）时自动适用。

用法:
    python _t_schema.py            # 校验全部科目
    python _t_schema.py phys       # 只校验物理
"""
import io
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")
try:
    from jsonschema import Draft7Validator
except ImportError:
    print("缺少 jsonschema，请先：python -m pip install jsonschema")
    sys.exit(2)

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # f6chem/
DATA = os.path.join(BASE, "data")
QUIZ = os.path.join(BASE, "quiz")

# ---------------- Schema 定义 ----------------

TOPIC_SCHEMA = {
    "type": "object",
    "required": ["id", "title", "sections"],
    "properties": {
        "id": {"type": "string", "minLength": 1},
        "title": {"type": "string", "minLength": 1},
        "pdf": {"type": "string"},
        "description": {"type": "string"},
        "sections": {
            "type": "array",
            "minItems": 1,
            "items": {
                "type": "object",
                "required": ["id", "title", "points"],
                "properties": {
                    "id": {"type": "string", "minLength": 1},
                    "title": {"type": "string", "minLength": 1},
                    "points": {
                        "type": "array",
                        "minItems": 1,
                        "items": {
                            "type": "object",
                            "required": ["id", "title", "body"],
                            "properties": {
                                "id": {"type": "string", "minLength": 1},
                                "title": {"type": "string", "minLength": 1},
                                # page：PDF 頁碼。數學分區（計算機程式）沒有 PDF，
                                # 因此改為選填；有 page 的前端才顯示「第 N 頁」。
                                "page": {"type": "integer", "minimum": 1},
                                "tags": {"type": "array", "items": {"type": "string"}},
                                "body": {"type": "string", "minLength": 1},
                                # 考试标注（化学用）
                                "exam": {"type": "object"},
                            },
                        },
                    },
                },
            },
        },
    },
}

QUIZ_SCHEMA = {
    "type": "object",
    "required": ["topic", "questions"],
    "properties": {
        "topic": {"type": "string", "minLength": 1},
        "questions": {
            "type": "array",
            "minItems": 1,
            "items": {
                "type": "object",
                "required": ["id", "type", "q", "explanation"],
                "properties": {
                    "id": {"type": "string", "minLength": 1},
                    "type": {"enum": ["mc", "tf", "fill"]},
                    "point": {"type": "string"},
                    "q": {"type": "string", "minLength": 1},
                    "explanation": {"type": "string", "minLength": 1},
                    "options": {"type": "array", "minItems": 2, "items": {"type": "string"}},
                    "answer": {},
                },
                # 分题型约束：mc 需要 options 与整数 answer；tf 需要布尔 answer
                "allOf": [
                    {
                        "if": {"properties": {"type": {"const": "mc"}}, "required": ["type"]},
                        "then": {
                            "required": ["options", "answer"],
                            "properties": {"answer": {"type": "integer", "minimum": 0}},
                        },
                    },
                    {
                        "if": {"properties": {"type": {"const": "tf"}}, "required": ["type"]},
                        "then": {
                            "required": ["answer"],
                            "properties": {"answer": {"type": "boolean"}},
                        },
                    },
                    {
                        "if": {"properties": {"type": {"const": "fill"}}, "required": ["type"]},
                        "then": {
                            "required": ["answer"],
                            "properties": {
                                "answer": {"type": "array", "minItems": 1,
                                           "items": {"type": "string"}},
                            },
                        },
                    },
                ],
            },
        },
    },
}

LINKS_SCHEMA = {
    "type": "array",
    "items": {
        "type": "object",
        "required": ["from", "to"],
        "properties": {
            "from": {"type": "string", "minLength": 1},
            "to": {"type": "string", "minLength": 1},
            "label": {"type": "string"},
        },
    },
}


def load(p):
    with io.open(p, encoding="utf-8") as f:
        return json.load(f)


def validate_file(path, schema, label):
    """校验单个文件，回传 (ok, errors)。"""
    try:
        data = load(path)
    except json.JSONDecodeError as e:
        return False, ["JSON 解析失败：%s" % e]
    v = Draft7Validator(schema)
    errs = []
    for e in sorted(v.iter_errors(data), key=lambda x: list(x.path)):
        loc = "/".join(str(x) for x in e.path) or "(根)"
        errs.append("%s: %s" % (loc, e.message))
    return (not errs), errs


def main():
    only = sys.argv[1] if len(sys.argv) > 1 else None
    total = bad = 0
    print("=" * 70)
    print("Schema 校验（jsonschema %s）" % __import__("importlib.metadata", fromlist=["x"])
          .metadata("jsonschema").get("Version", "?"))
    print("=" * 70)

    for sid in sorted(os.listdir(DATA)):
        sdir = os.path.join(DATA, sid)
        if not os.path.isdir(sdir) or not os.path.exists(os.path.join(sdir, "subject.json")):
            continue
        if only and sid != only:
            continue
        print("\n[%s]" % sid)
        subj = load(os.path.join(sdir, "subject.json"))
        topics = subj.get("topics") or []
        # 课题文件
        for tid in topics:
            p = os.path.join(sdir, tid + ".json")
            if not os.path.exists(p):
                print("  ✗ %s.json 不存在" % tid); bad += 1; total += 1
                continue
            ok, errs = validate_file(p, TOPIC_SCHEMA, tid)
            total += 1
            if ok:
                print("  ✓ %s.json" % tid)
            else:
                bad += 1
                print("  ✗ %s.json" % tid)
                for e in errs[:5]:
                    print("      %s" % e)
        # links
        lp = os.path.join(sdir, "links.json")
        if os.path.exists(lp):
            ok, errs = validate_file(lp, LINKS_SCHEMA, "links")
            total += 1
            if ok:
                n = len(load(lp))
                print("  ✓ links.json（%d 條）" % n)
            else:
                bad += 1
                print("  ✗ links.json")
                for e in errs[:5]:
                    print("      %s" % e)
        # 测验
        qdir = os.path.join(QUIZ, sid)
        if os.path.isdir(qdir):
            for tid in topics:
                p = os.path.join(qdir, tid + ".json")
                if not os.path.exists(p):
                    continue
                ok, errs = validate_file(p, QUIZ_SCHEMA, tid)
                total += 1
                if ok:
                    n = len(load(p)["questions"])
                    print("  ✓ quiz/%s.json（%d 題）" % (tid, n))
                else:
                    bad += 1
                    print("  ✗ quiz/%s.json" % tid)
                    for e in errs[:5]:
                        print("      %s" % e)

    print("\n" + "=" * 70)
    print("檢查 %d 個檔案，通過 %d，失敗 %d" % (total, total - bad, bad))
    if bad:
        sys.exit(1)
    print("Schema 校验全部通过")
    sys.exit(0)


if __name__ == "__main__":
    main()
