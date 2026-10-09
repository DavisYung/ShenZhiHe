# -*- coding: utf-8 -*-
"""放大 2x 重新 OCR 指定頁，輸出更完整行序，用於校對。用法: python ocr2.py p016 p023 p024 p025"""
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
names = sys.argv[1:] or ['p016', 'p023', 'p024', 'p025']
out_all = []
for name in names:
    img = imread_cjk(os.path.join(ROOT, 'pages', '2b', name + '.jpg'))
    img = cv2.resize(img, None, fx=2.0, fy=2.0, interpolation=cv2.INTER_CUBIC)
    res, _ = ocr(img)
    items = []
    if res:
        for box, txt, score in res:
            ys = [p[1] for p in box]
            xs = [p[0] for p in box]
            items.append((sum(ys) / 4, sum(xs) / 4, txt))
    items.sort(key=lambda t: (int(t[0] // 60), t[1]))
    out_all.append('===== %s =====' % name)
    last = None
    for y, x, txt in items:
        band = int(y // 60)
        if band != last:
            out_all.append('')
            last = band
        out_all.append('%.0f|%.0f| %s' % (y, x, txt))
path = os.path.join(ROOT, 'data', 'view', 'ocr2-report.txt')
io.open(path, 'w', encoding='utf-8').write('\n'.join(out_all))
print('written', path)
