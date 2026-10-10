// 验证核物理 36 页 PDF 是否全部被知识点引用
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const BASE = path.join(__dirname, '..', 'data', 'phys');

const refd = new Set();
const perPoint = new Map();

for (const f of ['nuclear1.json', 'nuclear2.json', 'nuclear3.json']) {
    const d = JSON.parse(fs.readFileSync(path.join(BASE, f), 'utf8').replace(/^\uFEFF/, ''));
    for (const sec of d.sections) {
        for (const pt of sec.points) {
            const m = (pt.body || '').match(/img\/phys_nuclear_p(\d+)\.webp/g) || [];
            const pages = m.map(x => parseInt(x.match(/p(\d+)\.webp/)[1], 10));
            perPoint.set(pt.id, pages);
            pages.forEach(p => refd.add(p));
        }
    }
}

const TOTAL = 36;
const missing = [];
for (let i = 1; i <= TOTAL; i++) if (!refd.has(i)) missing.push(i);

console.log('已引用页数: ' + refd.size + '/' + TOTAL);
console.log('引用到的页: ' + [...refd].sort((a, b) => a - b).join(', '));
if (missing.length) {
    console.log('\n[缺失] ' + TOTAL + ' 页中未引用: ' + missing.join(', '));
} else {
    console.log('\n[OK] 36 页全覆盖 ✓');
}

// 统计每个知识点的引用
console.log('\n各知识点引用：');
let noImg = [];
for (const [pid, pages] of perPoint) {
    if (pages.length === 0) noImg.push(pid);
    console.log('  ' + pid.padEnd(20) + (pages.length ? 'p' + pages.join(', p') : '[无图]'));
}
console.log('\n无图知识点: ' + (noImg.length ? noImg.join(', ') : '无 ✓'));
console.log('知识点总数: ' + perPoint.size);
