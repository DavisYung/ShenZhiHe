# -*- coding: utf-8 -*-
"""模拟 iOS 对 apple-touch-icon 的处理，证明修复有效。

iOS 会把图标的透明/半透明像素合成到黑色背景上。做法：
  1. 把「修复前」的半透明图标和「修复后」的不透明图标，各自合成到黑底
  2. 逐像素比较差异，看修复前到底有多少像素被改变（会发黑）
  3. 输出对比图供人工核对
"""
import os, sys
from PIL import Image

sys.stdout.reconfigure(encoding="utf-8")
SITE = os.path.dirname(os.path.abspath(__file__))
IDIR = os.path.join(SITE, "icons")
OUT = os.environ.get("TEMP", ".")


def compose_on_black(img):
    """把带 alpha 的图合成到黑底；无 alpha 的图原样返回。"""
    if img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info):
        rgba = img.convert("RGBA")
        bg = Image.new("RGB", rgba.size, (0, 0, 0))
        bg.paste(rgba, mask=rgba.getchannel("A"))
        return bg
    return img.convert("RGB")


print("=== 当前图标：合成到黑底后是否与原始一致 ===")
all_ok = True
for n in sorted(os.listdir(IDIR)):
    if not n.lower().endswith(".png"):
        continue
    p = os.path.join(IDIR, n)
    im = Image.open(p)
    on_black = compose_on_black(im)
    orig = im.convert("RGB")
    if list(orig.getdata()) == list(on_black.getdata()):
        print("  OK   %-30s 合成黑底后完全一致（iOS 上不会变色）" % n)
    else:
        # 统计差异
        diff = 0
        for a, b in zip(orig.getdata(), on_black.getdata()):
            if a != b:
                diff += 1
        print("  FAIL %-30s 合成黑底后有 %d 个像素变色（iOS 上会发黑）" % (n, diff))
        all_ok = False

print("\n=== 对照实验：故意做一张半透明图标，看 iOS 会怎么糟蹋它 ===")
bad = Image.new("RGBA", (180, 180), (0, 0, 0, 0))
from PIL import ImageDraw
d = ImageDraw.Draw(bad)
d.rectangle([0, 0, 179, 179], fill=(15, 118, 110, 255))
d.ellipse([40, 40, 140, 140], outline=(250, 247, 242, 150), width=6)  # 半透明线条
bad_path = os.path.join(OUT, "icon_bad_demo.png")
bad.save(bad_path, "PNG")
composed = compose_on_black(bad)
demo_path = os.path.join(OUT, "icon_bad_on_black.png")
composed.save(demo_path, "PNG")
n_alpha = sum(1 for px in bad.getchannel("A").getdata() if px < 255)
print("  半透明图标：%d 个像素 alpha<255" % n_alpha)
print("  → 合成到黑底后，这些像素会变暗（这就是你看到的「图标不对」）")
print("  已输出对照图：%s" % demo_path)

print("\n" + "=" * 60)
print("当前图标全部无 alpha，iOS 合成黑底不会产生任何变色" if all_ok else "仍有图标存在 alpha 问题")
sys.exit(0 if all_ok else 1)
