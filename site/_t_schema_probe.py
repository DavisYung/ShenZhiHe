# -*- coding: utf-8 -*-
"""反向测试：故意造坏数据，确认 schema 校验真的能抓到问题。
（一个只会说「通过」的校验器等于没有校验器。）
"""
import io
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from _t_schema import validate_file, TOPIC_SCHEMA, QUIZ_SCHEMA, LINKS_SCHEMA  # noqa: E402

TMP = os.path.join(HERE, "_schema_probe.json")

CASES = [
    ("缺 body 与 page", TOPIC_SCHEMA, {
        "id": "t", "title": "t",
        "sections": [{"id": "s1", "title": "s", "points": [{"id": "p1", "title": "x"}]}],
    }),
    ("page 是字符串而非整数", TOPIC_SCHEMA, {
        "id": "t", "title": "t",
        "sections": [{"id": "s1", "title": "s",
                      "points": [{"id": "p1", "title": "x", "page": "三", "body": "b"}]}],
    }),
    ("sections 为空数组", TOPIC_SCHEMA, {"id": "t", "title": "t", "sections": []}),
    ("缺 sections 字段", TOPIC_SCHEMA, {"id": "t", "title": "t"}),
    ("mc 缺 options", QUIZ_SCHEMA, {
        "topic": "t", "questions": [
            {"id": "q1", "type": "mc", "q": "?", "answer": 0, "explanation": "e"}],
    }),
    ("mc answer 越界为负数", QUIZ_SCHEMA, {
        "topic": "t", "questions": [
            {"id": "q1", "type": "mc", "q": "?", "options": ["a", "b"],
             "answer": -1, "explanation": "e"}],
    }),
    ("tf 的 answer 用字符串", QUIZ_SCHEMA, {
        "topic": "t", "questions": [
            {"id": "q1", "type": "tf", "q": "?", "answer": "true", "explanation": "e"}],
    }),
    ("fill 的 answer 不是数组", QUIZ_SCHEMA, {
        "topic": "t", "questions": [
            {"id": "q1", "type": "fill", "q": "?", "answer": "答案", "explanation": "e"}],
    }),
    ("题型不在 mc/tf/fill 之内", QUIZ_SCHEMA, {
        "topic": "t", "questions": [
            {"id": "q1", "type": "essay", "q": "?", "answer": 1, "explanation": "e"}],
    }),
    ("explanation 为空字符串", QUIZ_SCHEMA, {
        "topic": "t", "questions": [
            {"id": "q1", "type": "tf", "q": "?", "answer": True, "explanation": ""}],
    }),
    ("links 缺 to 字段", LINKS_SCHEMA, [{"from": "a"}]),
]

# 合法样本（必须通过）
GOOD = [
    ("合法课题", TOPIC_SCHEMA, {
        "id": "t", "title": "t", "pdf": "p.pdf",
        "sections": [{"id": "s1", "title": "s",
                      "points": [{"id": "p1", "title": "x", "page": 1, "body": "b"}]}],
    }),
    ("合法 mc", QUIZ_SCHEMA, {
        "topic": "t", "questions": [
            {"id": "q1", "type": "mc", "q": "?", "options": ["a", "b"],
             "answer": 1, "explanation": "e"}],
    }),
    ("合法 tf", QUIZ_SCHEMA, {
        "topic": "t", "questions": [
            {"id": "q1", "type": "tf", "q": "?", "answer": False, "explanation": "e"}],
    }),
    ("合法 fill", QUIZ_SCHEMA, {
        "topic": "t", "questions": [
            {"id": "q1", "type": "fill", "q": "?", "answer": ["a"], "explanation": "e"}],
    }),
]

fail = 0
print("=== 反向测试：坏数据必须被抓到 ===")
for name, schema, data in CASES:
    with io.open(TMP, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)
    ok, errs = validate_file(TMP, schema, "probe")
    if ok:
        print("  ✗ 漏报：%s（校验器没抓到！）" % name)
        fail += 1
    else:
        print("  ✓ 抓到：%-24s → %s" % (name, errs[0][:56]))

print("\n=== 正向测试：合法数据必须通过 ===")
for name, schema, data in GOOD:
    with io.open(TMP, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)
    ok, errs = validate_file(TMP, schema, "probe")
    if ok:
        print("  ✓ 通过：%s" % name)
    else:
        print("  ✗ 误报：%s → %s" % (name, errs[:2]))
        fail += 1

if os.path.exists(TMP):
    os.remove(TMP)

print("\n" + "=" * 60)
if fail:
    print("有 %d 项不符合预期" % fail)
    sys.exit(1)
print("Schema 校验器行为正确：%d 个坏数据全抓到，%d 个合法数据全通过" % (len(CASES), len(GOOD)))
sys.exit(0)
