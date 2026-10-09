# -*- coding: utf-8 -*-
"""生成「修复前 vs 修复后」图标对比图，判断半透明 bug 是否足以解释用户看到的现象。

修复前的版本：用 alpha=150 画第三条轨道 + RGBA 输出 → 半透明像素
修复后的版本：RGB 输出 + 用颜色混色表现「淡」 → 无 alpha
两者都按 iOS 的方式合成到黑底上，并排输出。
"""
import math
import os
import sys
from PIL import Image, ImageDraw

sys.stdout.reconfigure(encoding="utf-8")
BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.environ.get("TEMP", ".")

TEAL = (15, 118, 110)
TEAL_DARK = (13, 92, 86)
CREAM = (250, 247, 242)
GOLD = (214, 158, 46)


def draw_old(size=180, SS=4):
    """修复前的画法：RGBA + alpha=150 的轨道。"""
    S = size * SS
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, S, S], fill=TEAL)
    pad = S * 0.14
    cx, cy = S / 2, S / 2
    r_out = (S - 2 * pad) / 2
    for i, (rx_k, ry_k) in enumerate([(1.0, 0.42), (0.42, 1.0), (0.78, 0.78)]):
        rx, ry = r_out * rx_k, r_out * ry_k
        w = max(2, int(S * 0.018))
        col = CREAM if i < 2 else (CREAM[0], CREAM[1], CREAM[2], 150)
        d.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], outline=col, width=w)
    r_core = r_out * 0.26
    d.ellipse([cx - r_core, cy - r_core, cx + r_core, cy + r_core], fill=GOLD)
    r_in = r_core * 0.45
    d.ellipse([cx - r_in, cy - r_in, cx + r_in, cy + r_in], fill=TEAL_DARK)
    r_dot = max(2, S * 0.022)
    for ang, rx_k, ry_k in [(0, 1.0, 0.42), (180, 1.0, 0.42), (90, 0.42, 1.0), (270, 0.78, 0.78)]:
        a = math.radians(ang)
        x = cx + r_out * rx_k * math.cos(a)
        y = cy + r_out * ry_k * math.sin(a)
        d.ellipse([x - r_dot, y - r_dot, x + r_dot, y + r_dot], fill=CREAM)
    return img.resize((size, size), Image.LANCZOS)


def on_black(img):
    if img.mode in ("RGBA", "LA"):
        rgba = img.convert("RGBA")
        bg = Image.new("RGB", rgba.size, (0, 0, 0))
        bg.paste(rgba, mask=rgba.getchannel("A"))
        return bg
    return img.convert("RGB")


old = draw_old()
new = Image.open(os.path.join(BASE, "icons", "apple-touch-icon.png")).convert("RGB")

old_black = on_black(old)
new_black = on_black(new)

# 统计半透明像素
a = old.convert("RGBA").getchannel("A")
n_partial = sum(a.histogram()[:255])
print("修复前图标：%d 个半透明像素（alpha<255）" % n_partial)

# 找出修复前被 iOS 改色的像素
o_rgb = old.convert("RGB")
diff_px = sum(1 for p, q in zip(o_rgb.getdata(), old_black.getdata()) if p != q)
print("合成黑底后有 %d 个像素变色（占 %.1f%%）" % (diff_px, diff_px / (180 * 180) * 100))

# 并排对比：修复前原图 | 修复前@黑底 | 修复后@黑底
gap = 20
W = 180 * 3 + gap * 4
H = 180 + gap * 2 + 40
canvas = Image.new("RGB", (W, H), (245, 245, 245))
canvas.paste(o_rgb, (gap, gap + 40))
canvas.paste(old_black, (gap * 2 + 180, gap + 40))
canvas.paste(new_black, (gap * 3 + 360, gap + 40))

from PIL import ImageDraw as ID
d = ID.Draw(canvas)
try:
    from PIL import ImageFont
    font = ImageFont.load_default()
except Exception:
    font = None
labels = ["BEFORE (as designed)", "BEFORE on black (iOS)", "AFTER on black (iOS)"]
for i, t in enumerate(labels):
    d.text((gap + i * (180 + gap), 14), t, fill=(30, 30, 30), font=font)

p = os.path.join(OUT, "icon_compare.png")
canvas.save(p)
print("\n对比图已输出：%s" % p)
