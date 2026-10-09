# -*- coding: utf-8 -*-
"""解析目前的產物檔名。

build.py 產出三種檔案：
  神智核-V0.1.6.html   帶版號的主檔（歸檔、辨識版本用）
  神智核.html          穩定檔名（分享連結用，內容與帶版號那份相同）
  F6筆記整合網.html     舊檔名轉址頁（書籤相容）

輔助腳本一律用 built_html() 拿穩定檔，不要寫死檔名。
"""
import io
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
VER_PATH = os.path.join(BASE, "version.json")


def site_meta():
    if not os.path.exists(VER_PATH):
        return {"name": "神智核", "version": "V0.1.0"}
    with io.open(VER_PATH, encoding="utf-8") as f:
        v = json.load(f)
    return {
        "name": (v.get("name") or "神智核").strip(),
        "version": (v.get("version") or "V0.1.0").strip(),
    }


def stable_html():
    """不帶版號的穩定檔名（若不存在則退回最新一份帶版號的主檔）。"""
    m = site_meta()
    p = os.path.join(BASE, m["name"] + ".html")
    if os.path.exists(p):
        return p
    return versioned_html()


def versioned_html():
    m = site_meta()
    return os.path.join(BASE, "%s-%s.html" % (m["name"], m["version"]))


def built_html():
    """目前該讀哪一份：優先穩定檔，其次帶版號的主檔。"""
    p = stable_html()
    if os.path.exists(p):
        return p
    return versioned_html()


if __name__ == "__main__":
    print("name    :", site_meta()["name"])
    print("version :", site_meta()["version"])
    print("stable  :", stable_html())
    print("built   :", built_html(), os.path.exists(built_html()))
