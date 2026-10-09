# -*- coding: utf-8 -*-
"""裁切+放大 OCR：python ocr3.py p021 full / python ocr3.py p025 1050:1516"""
import os, sys, io
ROOT = r'C:\Users\guomi\OneDrive\文件\deepseek-harness\default-workspace\f6chem'
sys.path.insert(0, os.path.join(ROOT, 'pylibs'))
import cv2
import numpy as np
from rapidocr_onnxruntime import RapidOCR

def imread_cjk(path):
    data = np.frombuffer(open(path, 'rb').read(), dtype=np.uint8)
    return cv2.imdecode(data, cv2.IMREAD_COLOR)

ocr = RapidOCR()
name = sys.argv[1]
region = sys.argv[2] if len(sys.argv) > 2 else 'full'
scale = float(sys.argv[3]) if len(sys.argv) > 3 else 3.0
img = imread_cjk(os.path.join(ROOT, 'pages', '2b', name + '.jpg'))
if region != 'full':
    y1, y2 = [int(v) for v in region.split(':')]
    img = img[y1:y2, :]
img = cv2.resize(img, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
res, _ = ocr(img)
items = []
if res:
    for box, txt, score in res:
        ys = [p[1] for p in box]
        xs = [p[0] for p in box]
        items.append((sum(ys) / 4, sum(xs) / 4, txt))
items.sort(key=lambda t: (int(t[0] // 40), t[1]))
out = ['===== %s region=%s scale=%s =====' % (name, region, scale)]
last = None
for y, x, txt in items:
    band = int(y // 40)
    if band != last:
        out.append('')
        last = band
    out.append('%.0f|%.0f| %s' % (y, x, txt))
path = os.path.join(ROOT, 'data', 'view', 'ocr3-report.txt')
io.open(path, 'w', encoding='utf-8').write('\n'.join(out))
print('written', path)
