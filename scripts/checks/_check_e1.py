import re
html = open('gh-pages/index.html', encoding='utf-8').read()
print('E1 span 次数:', len(re.findall(r'<span class="tag">E1</span>', html)))
print('t.tags 渲染代码:', 't.tags&&t.tags.length' in html)
print('版本:', re.findall(r'V0\.\d+\.\d+', html)[:3])
