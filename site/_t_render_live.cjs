// 真实浏览器端到端：打开本地站点，检查核物理图片是否真的加载成功 + 代码块渲染
// 注意：.mdfig img 带 loading="lazy"，若把容器放在屏幕外，图片永不加载 → 必须用独立 Image() 主动加载
const { chromium } = require('playwright-core');
const path = require('path');
const http = require('http');
const fs = require('fs');

const GH = path.join(__dirname, '..', 'gh-pages');
const MIME = { '.html':'text/html;charset=utf-8', '.webp':'image/webp', '.png':'image/png',
               '.json':'application/json;charset=utf-8', '.js':'application/javascript', '.ico':'image/x-icon' };

const server = http.createServer((req, res) => {
    let p = decodeURIComponent(req.url.split('?')[0]);
    if (p === '/') p = '/index.html';
    const fp = path.join(GH, p);
    if (!fs.existsSync(fp) || fs.statSync(fp).isDirectory()) { res.writeHead(404); return res.end('404'); }
    res.writeHead(200, { 'Content-Type': MIME[path.extname(fp).toLowerCase()] || 'application/octet-stream' });
    fs.createReadStream(fp).pipe(res);
});

(async () => {
    await new Promise(r => server.listen(0, '127.0.0.1', r));
    const port = server.address().port;
    const url = `http://127.0.0.1:${port}/index.html`;
    console.log('本地站点: ' + url);

    const browser = await chromium.launch({
        executablePath: 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
        headless: true
    });
    const page = await browser.newPage({ viewport: { width: 390, height: 844 } });

    const failed = [];
    page.on('response', r => { if (r.status() >= 400) failed.push(`${r.status()} ${r.url()}`); });

    await page.goto(url, { waitUntil: 'load', timeout: 60000 });
    await page.waitForTimeout(2000);

    const env = await page.evaluate(() => ({
        hasSUBJECTS: typeof SUBJECTS !== 'undefined',
        hasMdLite: typeof mdLite === 'function',
        subjects: (typeof SUBJECTS !== 'undefined' ? SUBJECTS : []).map(s => ({ id: s.id, pts: s.stats && s.stats.points }))
    }));
    console.log('环境: SUBJECTS=' + env.hasSUBJECTS + ' mdLite=' + env.hasMdLite);
    console.log('科目: ' + JSON.stringify(env.subjects));
    if (!env.hasMdLite) { console.log('[FAIL] 页面里找不到 mdLite 函数'); await browser.close(); server.close(); process.exit(1); }

    // 渲染一个核物理知识点：检查图片语法是否变成 <img>、围栏是否变成代码块
    const one = await page.evaluate(() => {
        const phys = SUBJECTS.find(s => s.id === 'phys');
        const t = (phys.topics || []).find(x => x.id === 'nuclear1');
        const pt = t.sections[0].points[0];
        const host = document.createElement('div');
        host.innerHTML = mdLite(pt.body, null);
        const imgs = [...host.querySelectorAll('img')].map(i => i.getAttribute('src'));
        const pres = [...host.querySelectorAll('pre.mdcodewrap')];
        const txt = host.textContent;
        return {
            pointId: pt.id, title: pt.title,
            imgSrcs: imgs, preCount: pres.length,
            preTexts: pres.map(p => p.textContent.slice(0, 70)),
            rawImgSyntax: /!\[[^\]]*\]\(/.test(txt),
            rawFence: /```/.test(txt),
            // 表格也顺带确认没被破坏
            tableCount: host.querySelectorAll('table').length
        };
    });
    console.log('\n=== nuclear1 首个知识点渲染 ===');
    console.log(`[${one.pointId}] ${one.title}`);
    console.log(`图片 ${one.imgSrcs.length} 张 · 代码块 ${one.preCount} 个 · 表格 ${one.tableCount} 个`);
    console.log('残留图片语法: ' + one.rawImgSyntax + ' · 残留裸围栏: ' + one.rawFence);
    one.imgSrcs.forEach(s => console.log('  img src: ' + s));
    one.preTexts.forEach(t => console.log('  pre: ' + JSON.stringify(t)));

    // 全量：渲染所有核物理知识点，收集全部唯一图片并逐个真实加载
    const all = await page.evaluate(async () => {
        const phys = SUBJECTS.find(s => s.id === 'phys');
        const nucTopics = (phys.topics || []).filter(t => t.id.startsWith('nuclear'));
        const host = document.createElement('div');
        let html = '', pts = 0;
        for (const t of nucTopics) for (const s of t.sections) for (const p of s.points) { html += mdLite(p.body, null); pts++; }
        host.innerHTML = html;
        const imgTags = [...host.querySelectorAll('img')];
        const unique = [...new Set(imgTags.map(i => i.getAttribute('src')))];
        const pres = host.querySelectorAll('pre.mdcodewrap').length;
        const rawImg = /!\[[^\]]*\]\(/.test(host.textContent);
        const rawFence = /```/.test(host.textContent);
        // 用独立 Image() 主动加载（不受 loading=lazy 与屏幕外影响）
        const results = await Promise.all(unique.map(src => new Promise(res => {
            const i = new Image();
            const to = setTimeout(() => res({ src, ok: false, err: 'timeout' }), 15000);
            i.onload = () => { clearTimeout(to); res({ src, ok: true, w: i.naturalWidth, h: i.naturalHeight }); };
            i.onerror = () => { clearTimeout(to); res({ src, ok: false, err: 'onerror' }); };
            i.src = src;
        })));
        return { pts, imgTags: imgTags.length, unique: unique.length, pres, rawImg, rawFence,
                 ok: results.filter(r => r.ok).length, bad: results.filter(r => !r.ok) };
    });
    console.log('\n=== 核物理全量 ===');
    console.log(`知识点 ${all.pts} 个 · img 标签 ${all.imgTags} 个 · 唯一图片 ${all.unique} 张`);
    console.log(`加载成功 ${all.ok}/${all.unique} · 代码块 ${all.pres} 个`);
    console.log('残留图片语法: ' + all.rawImg + ' · 残留裸围栏: ' + all.rawFence);
    all.bad.forEach(b => console.log('  FAIL ' + b.src + ' (' + b.err + ')'));

    if (failed.length) { console.log('\n=== 资源错误 ==='); failed.slice(0, 15).forEach(f => console.log('  ' + f)); }

    const pass = all.ok === all.unique && all.bad.length === 0 && all.unique >= 36
              && !one.rawImgSyntax && !one.rawFence && !all.rawImg && !all.rawFence
              && all.pres > 0;
    console.log('\n' + (pass ? '[PASS] 浏览器端到端验证通过' : '[FAIL] 存在未通过项'));

    await browser.close();
    server.close();
    process.exit(pass ? 0 : 1);
})().catch(e => { console.error('异常: ' + e.message); process.exit(1); });
