// 原子世界区本地端到端：图片加载 + 渲染 + 单元导航
const { chromium } = require('playwright-core');
const path = require('path'); const http = require('http'); const fs = require('fs');

const GH = path.join(__dirname, '..', 'gh-pages');
const MIME = { '.html':'text/html;charset=utf-8','.webp':'image/webp','.png':'image/png','.json':'application/json;charset=utf-8','.js':'application/javascript','.ico':'image/x-icon' };
const server = http.createServer((req, res) => {
    let p = decodeURIComponent(req.url.split('?')[0]); if (p === '/') p = '/index.html';
    const fp = path.join(GH, p);
    if (!fs.existsSync(fp) || fs.statSync(fp).isDirectory()) { res.writeHead(404); return res.end('404'); }
    res.writeHead(200, { 'Content-Type': MIME[path.extname(fp).toLowerCase()] || 'application/octet-stream' });
    fs.createReadStream(fp).pipe(res);
});

(async () => {
    await new Promise(r => server.listen(0, '127.0.0.1', r));
    const browser = await chromium.launch({ executablePath: 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe', headless: true });
    const page = await browser.newPage({ viewport: { width: 390, height: 844 } });
    const bad = [];
    page.on('response', r => { if (r.status() >= 400) bad.push(r.status() + ' ' + r.url()); });

    await page.goto(`http://127.0.0.1:${server.address().port}/index.html`, { waitUntil: 'load', timeout: 60000 });
    await page.waitForTimeout(2200);

    const info = await page.evaluate(() => {
        const phys = SUBJECTS.find(s => s.id === 'phys');
        const u = (phys.units || []).find(x => x.id === 'atomic');
        return {
            units: (phys.units || []).map(x => x.id + ':' + x.title),
            atomicUnit: u ? { title: u.title, emoji: u.emoji, topics: u.topics, stats: u.stats } : null,
            topics: (phys.topics || []).filter(t => t.id.startsWith('atomic')).map(t => ({ id: t.id, title: t.title, sects: t.sections.length, pts: t.sections.reduce((a, s) => a + s.points.length, 0) }))
        };
    });
    console.log('物理区单元: ' + JSON.stringify(info.units));
    console.log('原子世界单元: ' + JSON.stringify(info.atomicUnit));
    console.log('课题: ' + JSON.stringify(info.topics, null, 1));

    // 渲染全部 atomic 知识点，验证图片真实加载
    const all = await page.evaluate(async () => {
        const phys = SUBJECTS.find(s => s.id === 'phys');
        const ato = (phys.topics || []).filter(t => t.id.startsWith('atomic'));
        const host = document.createElement('div');
        let html = '', pts = 0;
        for (const t of ato) for (const s of t.sections) for (const p of s.points) { html += mdLite(p.body, null); pts++; }
        host.innerHTML = html;
        const imgTags = [...host.querySelectorAll('img')];
        const unique = [...new Set(imgTags.map(i => i.getAttribute('src')))];
        const pres = host.querySelectorAll('pre.mdcodewrap').length;
        const tables = host.querySelectorAll('table').length;
        const rawImg = /!\[[^\]]*\]\(/.test(host.textContent);
        const rawFence = /```/.test(host.textContent);
        const results = await Promise.all(unique.map(src => new Promise(res => {
            const i = new Image();
            const to = setTimeout(() => res({ src, ok: false, err: 'timeout' }), 20000);
            i.onload = () => { clearTimeout(to); res({ src, ok: true, w: i.naturalWidth }); };
            i.onerror = () => { clearTimeout(to); res({ src, ok: false, err: 'onerror' }); };
            i.src = src;
        })));
        // 题目统计
        let qTotal = 0, pointsWithQ = new Set();
        for (const t of ato) {
            const qz = (SUBJECTS.find(s=>s.id==='phys').quiz || {})[t.id] || [];
            qTotal += qz.length;
            qz.forEach(x => pointsWithQ.add(x.point));
        }
        return { pts, imgTags: imgTags.length, unique: unique.length, pres, tables, rawImg, rawFence,
                 ok: results.filter(r => r.ok).length, bad: results.filter(r => !r.ok), qTotal, pointsWithQ: pointsWithQ.size };
    });

    console.log('\n=== 原子世界全量 ===');
    console.log(`知识点 ${all.pts} · img 标签 ${all.imgTags} · 唯一图片 ${all.unique} 张 · 加载成功 ${all.ok}/${all.unique}`);
    console.log(`代码块 ${all.pres} · 表格 ${all.tables} · 题 ${all.qTotal} · 有题知识点 ${all.pointsWithQ}`);
    console.log('残留图片语法: ' + all.rawImg + ' · 残留裸围栏: ' + all.rawFence);
    all.bad.forEach(b => console.log('  FAIL ' + b.src + ' ' + b.err));
    if (bad.length) { console.log('\n资源错误:'); bad.slice(0, 10).forEach(x => console.log('  ' + x)); }

    const pass = all.ok === all.unique && all.bad.length === 0 && all.unique === 39
              && !all.rawImg && !all.rawFence && all.pres > 0
              && info.atomicUnit && info.atomicUnit.topics.length === 3
              && all.pts === 57 && all.qTotal === 86;
    console.log('\n' + (pass ? '[PASS] 原子世界本地端到端验证通过' : '[FAIL] 未通过'));

    await browser.close(); server.close();
    process.exit(pass ? 0 : 1);
})().catch(e => { console.error('异常: ' + e.message); process.exit(1); });
