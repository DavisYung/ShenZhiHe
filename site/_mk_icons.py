# -*- coding: utf-8 -*-
"""生成 PWA / App 图标：192 / 512 / maskable 512 / apple-touch 180 / favicon。

站点主色 #0f766e（teal），图标画一个「核」的意象：同心轨道 + 中心核点。
不依赖任何字体文件（用几何绘制），避免字体缺失导致豆腐块。

**为什么全部输出不透明 RGB、绝不留 alpha 通道**（重要，踩过坑）：
    iOS 把 apple-touch-icon 的透明／半透明像素合成到**黑色**背景上，图标边缘会发脏、
    发暗，看起来「不是设计的那个图标」。Pillow 的 ImageDraw 对 RGBA 是**直接替换像素**
    而不是 alpha 合成，所以哪怕背景铺满了，只要用带 alpha 的颜色画线条，线条边缘就会
    留下半透明像素（抗锯齿处尤其明显）。
    → 因此这里一律用 RGB 模式绘制，需要「淡」的效果就用颜色插值（和背景混色），
      绝不使用半透明颜色。最后存成 RGB PNG（无 alpha）。
"""
import math
import os
import sys
from PIL import Image, ImageDraw

sys.stdout.reconfigure(encoding="utf-8")

BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, "icons")
os.makedirs(OUT, exist_ok=True)

TEAL = (15, 118, 110)          # #0f766e 主色
TEAL_DARK = (13, 92, 86)
CREAM = (250, 247, 242)
GOLD = (214, 158, 46)


def blend(c1, c2, k):
    """把 c1 按比例 k 混到 c2 上，得到不透明的新颜色。

    用来替代「半透明」：想要线条看起来淡一点，就和背景色混，而不是调 alpha。
    """
    return tuple(int(round(c1[i] * k + c2[i] * (1 - k))) for i in range(3))


def draw_icon(size, maskable=False):
    """maskable 版本要把图形缩进安全区（中心约 80% 圆内），否则被系统裁切。"""
    SS = 4  # 超采样，边缘更干净
    S = size * SS
    # 关键：RGB 模式，没有 alpha 通道，从源头杜绝半透明像素
    img = Image.new("RGB", (S, S), TEAL)
    d = ImageDraw.Draw(img)

    # 内容安全区
    pad = S * (0.22 if maskable else 0.14)
    cx, cy = S / 2, S / 2
    r_out = (S - 2 * pad) / 2

    # 三条椭圆轨道，模拟电子轨道。
    # 第三条用「和背景混色」表现淡，而不是 alpha=150（那样会留下半透明像素）。
    faint = blend(CREAM, TEAL, 0.55)
    for i, (rx_k, ry_k) in enumerate([(1.0, 0.42), (0.42, 1.0), (0.78, 0.78)]):
        rx, ry = r_out * rx_k, r_out * ry_k
        w = max(2, int(S * 0.018))
        col = CREAM if i < 2 else faint
        d.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], outline=col, width=w)

    # 中心核
    r_core = r_out * 0.26
    d.ellipse([cx - r_core, cy - r_core, cx + r_core, cy + r_core], fill=GOLD)
    r_in = r_core * 0.45
    d.ellipse([cx - r_in, cy - r_in, cx + r_in, cy + r_in], fill=TEAL_DARK)

    # 轨道上的小电子点（maskable 下不画，避免裁切后显乱）
    if not maskable:
        r_dot = max(2, S * 0.022)
        for ang, rx_k, ry_k in [(0, 1.0, 0.42), (180, 1.0, 0.42),
                                (90, 0.42, 1.0), (270, 0.78, 0.78)]:
            a = math.radians(ang)
            x = cx + r_out * rx_k * math.cos(a)
            y = cy + r_out * ry_k * math.sin(a)
            d.ellipse([x - r_dot, y - r_dot, x + r_dot, y + r_dot], fill=CREAM)

    img = img.resize((size, size), Image.LANCZOS)
    # 双保险：显式转 RGB（丢弃任何可能的 alpha），并确认无 alpha 通道
    img = img.convert("RGB")
    return img


def verify_no_alpha(path):
    """确认存出来的 PNG 真的没有 alpha 通道、没有半透明像素。"""
    im = Image.open(path)
    has_alpha = im.mode in ("RGBA", "LA") or (im.mode == "P" and "transparency" in im.info)
    n_partial = 0
    if has_alpha:
        a = im.convert("RGBA").getchannel("A")
        n_partial = sum(a.histogram()[:255])
    return (not has_alpha), n_partial


def main():
    # 圖示一律輸出到網站根目錄（不放 icons/ 子資料夾）。
    # 原因：用 GitHub 網頁上傳時拖曳資料夾很容易漏掉整個資料夾，
    # 而 <link rel="apple-touch-icon"> 指向 404 時 iOS 不會回退到根目錄圖示，
    # 會用 theme-color + 標題首字生成佔位圖示。平鋪在根目錄就不會漏。
    made = []
    specs = [
        ("icon-192.png", 192, False),
        ("icon-512.png", 512, False),
        ("icon-maskable-512.png", 512, True),
        # iOS 各裝置會挑不同尺寸：iPhone 180、iPad Pro 167、iPad 152。
        # 只給 180 的話，部分 iPad 會拿不到而退回佔位圖示。
        ("apple-touch-icon.png", 180, False),
        ("apple-touch-icon-167.png", 167, False),
        ("apple-touch-icon-152.png", 152, False),
        ("favicon-32.png", 32, False),
    ]
    for name, size, maskable in specs:
        img = draw_icon(size, maskable=maskable)
        p = os.path.join(BASE, name)
        img.save(p, "PNG", optimize=True)
        made.append((name, size, os.path.getsize(p), p))

    # favicon.ico（多尺寸）
    ico_path = os.path.join(BASE, "favicon.ico")
    draw_icon(64, maskable=False).save(ico_path, sizes=[(16, 16), (32, 32), (48, 48), (64, 64)])
    made.append(("favicon.ico", 64, os.path.getsize(ico_path), ico_path))

    # 舊版曾把圖示放在 icons/ 子資料夾，該目錄已不再使用；
    # 若殘留會讓人誤以為還要上傳那個資料夾，這裡主動清掉。
    legacy = os.path.join(BASE, "icons")
    if os.path.isdir(legacy):
        import shutil
        shutil.rmtree(legacy, ignore_errors=True)
        print("已移除舊的 icons/ 子資料夾（圖示現在都放根目錄）\n")

    print("生成圖示（全部不透明 RGB，無 alpha，全部在網站根目錄）：")
    all_ok = True
    for n, s, b, p in made:
        if n.endswith(".ico"):
            print("  %-32s %4dpx  %6.1f KB" % (n, s, b / 1024.0))
            continue
        no_alpha, n_partial = verify_no_alpha(p)
        flag = "✓" if (no_alpha and n_partial == 0) else "✗"
        if not (no_alpha and n_partial == 0):
            all_ok = False
        print("  %-32s %4dpx  %6.1f KB  無alpha=%s 半透明像素=%d %s"
              % (n, s, b / 1024.0, "是" if no_alpha else "否", n_partial, flag))

    print("\n輸出位置：%s（網站根目錄）" % BASE)
    if not all_ok:
        print("❌ 仍有圖示帶 alpha／半透明像素，iOS 上會出問題")
        raise SystemExit(1)
    print("✓ 全部圖示均為不透明 RGB，iOS 不會出現黑邊")


if __name__ == "__main__":
    main()
