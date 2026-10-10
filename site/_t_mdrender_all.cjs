// 全科目回归：所有 subject 的所有知识点，图片/代码块渲染 + 残留语法检查
const fs = require('fs');
const path = require('path');
const vm = require('vm');

const tpl = fs.readFileSync(path.join(__dirname, 'template.html'), 'utf8');
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
const sandbox = {};
vm.createContext(sandbox);
vm.runInContext([extractFn(tpl,'esc'),extractFn(tpl,'inline'),extractFn(tpl,'mdLite')].join('\n') + '\n;globalThis.__mdLite=mdLite;', sandbox, {timeout:5000});
const mdLite = sandbox.__mdLite;

const dataRoot = path.join(__dirname, '..', 'data');
let grand = { pts:0, imgs:0, pres:0 };
const allFails = [];
const perSubject = {};

for (const sid of fs.readdirSync(dataRoot)) {
    const sdir = path.join(dataRoot, sid);
    if (!fs.statSync(sdir).isDirectory()) continue;
    if (!fs.existsSync(path.join(sdir, 'subject.json'))) continue;
    let pts=0, imgs=0, pres=0;
    const RESERVED = new Set(['subject','links','index']);
    for (const n of fs.readdirSync(sdir)) {
        if (!n.endsWith('.json')) continue;
        const stem = n.slice(0,-5);
        if (RESERVED.has(stem) || stem.startsWith('_') || stem.startsWith('payload') || stem.startsWith('tmp')) continue;
        const d = JSON.parse(fs.readFileSync(path.join(sdir, n), 'utf8').replace(/^\uFEFF/,''));
        for (const sec of (d.sections||[])) {
            for (const pt of (sec.points||[])) {
                pts++;
                const body = pt.body || '';
                const out = mdLite(body);
                const ni = (out.match(/<img /g)||[]).length;
                const np = (out.match(/<pre class="mdcodewrap"/g)||[]).length;
                imgs += ni; pres += np;
                const srcImgLines = (body.match(/^\s*!\[/gm)||[]).length;
                if (srcImgLines>0 && ni===0) allFails.push(`${sid}/${pt.id}: ${srcImgLines} 行图片未渲染`);
                const fences = (body.match(/^```/gm)||[]).length;
                if (fences>=2 && np===0) allFails.push(`${sid}/${pt.id}: ${fences} 围栏未渲染`);
                const stripped = out.replace(/<img[^>]*>/g,'').replace(/<pre[\s\S]*?<\/pre>/g,'');
                if (/!\[[^\]]*\]\(/.test(stripped)) allFails.push(`${sid}/${pt.id}: 残留图片语法`);
                if (/```/.test(stripped)) allFails.push(`${sid}/${pt.id}: 残留裸围栏`);
            }
        }
    }
    perSubject[sid] = {pts, imgs, pres};
    grand.pts += pts; grand.imgs += imgs; grand.pres += pres;
}

for (const [sid,v] of Object.entries(perSubject)) {
    console.log(`${sid}: 知识点 ${v.pts} · 图片 ${v.imgs} · 代码块 ${v.pres}`);
}
console.log(`\n合计: 知识点 ${grand.pts} · 图片 ${grand.imgs} · 代码块 ${grand.pres}`);
if (allFails.length) {
    console.log(`\n[FAIL] ${allFails.length} 项:`);
    allFails.slice(0,30).forEach(x=>console.log('  '+x));
    process.exit(1);
}
console.log('[OK] 全科目回归通过');
