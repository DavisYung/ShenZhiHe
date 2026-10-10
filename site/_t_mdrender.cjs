// 从 template.html 精确抽取 mdLite + esc + inline，用真实核物理 body 验证渲染
const fs = require('fs');
const path = require('path');
const vm = require('vm');

const tpl = fs.readFileSync(path.join(__dirname, 'template.html'), 'utf8');

// 用括号配平抽出一个顶层 function 的完整文本
function extractFn(src, name) {
    const start = src.indexOf('function ' + name + '(');
    if (start < 0) throw new Error('找不到函数 ' + name);
    let i = src.indexOf('{', start), depth = 0;
    for (; i < src.length; i++) {
        const c = src[i];
        if (c === '{') depth++;
        else if (c === '}') { depth--; if (depth === 0) return src.slice(start, i + 1); }
    }
    throw new Error('函数 ' + name + ' 括号不配平');
}

const code = [
    extractFn(tpl, 'esc'),
    extractFn(tpl, 'inline'),
    extractFn(tpl, 'mdLite')
].join('\n');

const sandbox = {};
vm.createContext(sandbox);
vm.runInContext(code + '\n;globalThis.__mdLite = mdLite;', sandbox, { timeout: 5000 });
const mdLite = sandbox.__mdLite;
if (typeof mdLite !== 'function') { console.error('mdLite 不可用'); process.exit(1); }

let totalImgs = 0, totalPre = 0, checked = 0;
const fails = [];
for (const f of ['nuclear1.json', 'nuclear2.json', 'nuclear3.json']) {
    const d = JSON.parse(fs.readFileSync(path.join(__dirname, '..', 'data', 'phys', f), 'utf8').replace(/^\uFEFF/, ''));
    for (const sec of d.sections) {
        for (const pt of sec.points) {
            checked++;
            const body = pt.body || '';
            const out = mdLite(body);
            const imgs = (out.match(/<img /g) || []).length;
            const pres = (out.match(/<pre class="mdcodewrap"/g) || []).length;
            totalImgs += imgs; totalPre += pres;

            const srcImgLines = (body.match(/^\s*!\[/gm) || []).length;
            if (srcImgLines > 0 && imgs === 0) fails.push(`${pt.id}: 有 ${srcImgLines} 行图片但 0 张渲染`);

            const srcFences = (body.match(/^```/gm) || []).length;
            if (srcFences >= 2 && pres === 0) fails.push(`${pt.id}: 有 ${srcFences} 个围栏但 0 个代码块`);

            const stripped = out.replace(/<img[^>]*>/g, '').replace(/<pre[\s\S]*?<\/pre>/g, '');
            if (/!\[[^\]]*\]\(/.test(stripped)) fails.push(`${pt.id}: 输出残留未渲染的图片语法`);
            if (/```/.test(stripped)) fails.push(`${pt.id}: 输出残留裸围栏`);
        }
    }
}

console.log(`检查知识点: ${checked}`);
console.log(`渲染出 <img>: ${totalImgs} 张`);
console.log(`渲染出代码块: ${totalPre} 个`);
console.log('');
if (fails.length) {
    console.log(`[FAIL] ${fails.length} 项问题:`);
    fails.slice(0, 25).forEach(x => console.log('  ' + x));
    process.exit(1);
}
console.log('[OK] 全部知识点：图片与代码块均正确渲染，无残留语法');
