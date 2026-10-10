// 线上站点端到端：直接打开 GitHub Pages，验证图片真实加载 + 代码块渲染
const { chromium } = require('playwright-core');

const BASE = 'https://nzgjsmy.github.io/ShenZhiHe/index.html';

(async () => {
    const browser = await chromium.launch({
        executablePath: 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
        headless: true
    });
    const page = await browser.newPage({ viewport: { width: 390, height: 844 } });
    const bad = [];
    page.on('response', r => { if (r.status() >= 400) bad.push(r.status() + ' ' + r.url()); });

    console.log('打开: ' + BASE);
    await page.goto(BASE, { waitUntil: 'load', timeout: 90000 });
    await page.waitForTimeout(3000);

    const ver = await page.title();
    console.log('标题: ' + ver);

    const all = await page.evaluate(async () => {
        const phys = SUBJECTS.find(s => s.id === 'phys');
        const nuc = (phys.topics || []).filter(t => t.id.startsWith('nuclear'));
        const host = document.createElement('div');
        let html = '', pts = 0;
        for (const t of nuc) for (const s of t.sections) for (const p of s.points) { html += mdLite(p.body, null); pts++; }
        host.innerHTML = html;
        const imgTags = [...host.querySelectorAll('img')];
        const unique = [...new Set(imgTags.map(i => i.getAttribute('src')))];
        const pres = host.querySelectorAll('pre.mdcodewrap').length;
        const tables = host.querySelectorAll('table').length;
        const rawImg = /!\[[^\]]*\]\(/.test(host.textContent);
        const rawFence = /```/.test(host.textContent);
        const results = await Promise.all(unique.map(src => new Promise(res => {
            const i = new Image();
            const to = setTimeout(() => res({ src, ok: false, err: 'timeout' }), 30000);
            i.onload = () => { clearTimeout(to); res({ src, ok: true, w: i.naturalWidth }); };
            i.onerror = () => { clearTimeout(to); res({ src, ok: false, err: 'onerror' }); };
            i.src = src;
        })));
        return { pts, imgTags: imgTags.length, unique: unique.length, pres, tables, rawImg, rawFence,
                 ok: results.filter(r => r.ok).length, bad: results.filter(r => !r.ok) };
    });

    console.log('\n=== 线上核物理 ===');
    console.log(`知识点 ${all.pts} · img 标签 ${all.imgTags} · 唯一图片 ${all.unique} 张 · 加载成功 ${all.ok}`);
    console.log(`代码块 ${all.pres} 个 · 表格 ${all.tables} 个`);
    console.log('残留图片语法: ' + all.rawImg + ' · 残留裸围栏: ' + all.rawFence);
    all.bad.forEach(b => console.log('  FAIL ' + b.src + ' ' + b.err));
    if (bad.length) { console.log('\n资源错误:'); bad.slice(0, 10).forEach(x => console.log('  ' + x)); }

    const pass = all.ok === all.unique && all.bad.length === 0 && all.unique >= 36
              && !all.rawImg && !all.rawFence && all.pres > 0;
    console.log('\n' + (pass ? '[PASS] 线上端到端验证通过' : '[FAIL] 未通过'));

    await browser.close();
    process.exit(pass ? 0 : 1);
})().catch(e => { console.error('异常: ' + e.message); process.exit(1); });
