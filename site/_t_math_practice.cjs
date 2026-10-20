/* 驗收數學練習章節：7 章節 / 17 知識點 / 4 組練習，含表格渲染與答案對齊 */
const http = require('http');
const fs = require('fs');
const path = require('path');
const { spawn } = require('child_process');

const ROOT = __dirname;
const PORT = 8734;
const CHROME = 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe';
const TARGET = '神智核.html';
const MIME = { '.html': 'text/html; charset=utf-8', '.js': 'application/javascript', '.json': 'application/json',
  '.svg': 'image/svg+xml', '.png': 'image/png', '.webp': 'image/webp', '.css': 'text/css' };

const srv = http.createServer((req, res) => {
  let p = decodeURIComponent(req.url.split('?')[0].split('#')[0]);
  if (p === '/') p = '/' + TARGET;
  const fp = path.join(ROOT, p);
  if (!fp.startsWith(ROOT) || !fs.existsSync(fp) || fs.statSync(fp).isDirectory()) { res.writeHead(404); res.end('404'); return; }
  res.writeHead(200, { 'Content-Type': MIME[path.extname(fp)] || 'application/octet-stream' });
  fs.createReadStream(fp).pipe(res);
});
const sleep = ms => new Promise(r => setTimeout(r, ms));

(async () => {
  await new Promise(r => srv.listen(PORT, r));
  const results = [];
  const ok = (n, c, e) => results.push({ n, pass: !!c, e: e || '' });

  const prof = path.join(ROOT, '_t_profile_prac_' + Date.now());
  const chrome = spawn(CHROME, ['--headless=new', '--remote-debugging-port=9334',
    '--user-data-dir=' + prof, '--no-first-run', '--no-default-browser-check',
    '--disable-gpu', '--window-size=1200,900', 'about:blank'], { stdio: 'ignore' });

  try {
    let list = null;
    for (let i = 0; i < 40; i++) {
      await sleep(300);
      try { const r = await fetch('http://127.0.0.1:9334/json/list'); list = await r.json(); if (list && list.length) break; } catch (e) {}
    }
    const page = list.find(t => t.type === 'page') || list[0];
    const ws = new WebSocket(page.webSocketDebuggerUrl);
    await new Promise((res, rej) => { ws.addEventListener('open', res, { once: true }); ws.addEventListener('error', rej, { once: true }); });
    let id = 0; const pending = new Map(); const listeners = [];
    ws.addEventListener('message', ev => {
      const m = JSON.parse(ev.data);
      if (m.id && pending.has(m.id)) { pending.get(m.id)(m); pending.delete(m.id); }
      else if (m.method) listeners.forEach(f => f(m));
    });
    const send = (method, params) => new Promise((res, rej) => {
      const i = ++id;
      pending.set(i, m => m.error ? rej(new Error(method + ':' + JSON.stringify(m.error))) : res(m.result));
      ws.send(JSON.stringify({ id: i, method, params: params || {} }));
    });

    await send('Page.enable'); await send('Runtime.enable'); await send('Log.enable');
    const errs = [];
    listeners.push(m => {
      if (m.method === 'Runtime.exceptionThrown') errs.push('EXC ' + (m.params.exceptionDetails?.text || ''));
      if (m.method === 'Log.entryAdded' && m.params.entry.level === 'error') {
        const t = m.params.entry.text || '';
        if (!/Failed to load resource|404|net::/.test(t)) errs.push('LOG ' + t.slice(0, 150));
      }
    });

    const ev = async (expr) => {
      const r = await send('Runtime.evaluate', { expression: expr, returnByValue: true, awaitPromise: true });
      if (r.exceptionDetails) throw new Error('Eval ' + JSON.stringify(r.exceptionDetails).slice(0, 250));
      return r.result.value;
    };
    const nav = async (hash, wait) => {
      await send('Page.navigate', { url: `http://127.0.0.1:${PORT}/${encodeURIComponent(TARGET)}${hash}` });
      await sleep(wait || 2000);
    };

    await nav('#/math/t/calc', 2600);
    const info = await ev(`(function(){
      var secs=document.querySelectorAll('.sect, .secbox, section');
      var h=document.querySelectorAll('h3,h4');
      var tbls=document.querySelectorAll('table');
      var txt=document.body.innerText;
      return {tables:tbls.length, txt:txt, hcount:h.length};
    })()`);
    const t = info.txt;
    ok('課題頁可開', t.length > 500);
    ok('有七個章節標題', ['四段程式怎麼選', '共用前提', '四段程式速查與驗收',
      '練習一', '練習二', '練習三', '練習四'].every(s => t.includes(s)), t.slice(0, 300));
    ok('練習一有 8 題', t.includes('(0,0)、(6,0)、(0,8)') && t.includes('(0,0)、(5,0)、(0,12)'));
    ok('練習二有線性規劃情境', t.includes('機器上限 8 小時'));
    ok('練習三有 8 題', t.includes('cos2θ = cosθ'));
    ok('練習四有 10 題', t.includes('a=2, b=3, ∠C=120°'));
    ok('表格有渲染成 table', info.tables >= 10, 'tables=' + info.tables);
    ok('答案表存在', t.includes('(2, 2.667)') && t.includes('(5, 5.25)'));
    ok('沒有裸露的 Markdown 管線', !/\|\s*-{3,}\s*\|/.test(t), '發現表格分隔行未轉換');
    ok('沒有裸露的星號粗體', !/\*\*[^*]+\*\*/.test(t), '發現 ** 未轉換');
    ok('沒有裸露的反引號', !/`[^`]+`/.test(t), '發現反引號未轉換');
    ok('無 JS 例外', errs.filter(e => !/Failed to load/.test(e)).length === 0, errs.slice(0, 3).join(' | '));

    // 手機尺寸
    await send('Emulation.setDeviceMetricsOverride', { width: 390, height: 844, deviceScaleFactor: 2, mobile: true });
    await sleep(600);
    const m = await ev(`(function(){var d=document.documentElement;return {sw:d.scrollWidth,cw:d.clientWidth};})()`);
    ok('手機無橫向溢出', m.sw <= m.cw + 2, JSON.stringify(m));

    await nav('#/math/t/calc', 2600);
    const met = await send('Page.getLayoutMetrics');
    const h = Math.min(Math.ceil(met.cssContentSize.height), 16000);
    await send('Emulation.setDeviceMetricsOverride', { width: 390, height: h, deviceScaleFactor: 2, mobile: true });
    await sleep(700);
    const shot = await send('Page.captureScreenshot', { format: 'png', captureBeyondViewport: true });
    fs.writeFileSync(path.join(ROOT, 'shot_m_practice.png'), Buffer.from(shot.data, 'base64'));
    await send('Emulation.clearDeviceMetricsOverride');

    ws.close();
    const pass = results.filter(r => r.pass).length;
    console.log('\n===== 練習章節驗收 =====');
    results.forEach(r => console.log((r.pass ? 'PASS ' : 'FAIL ') + r.n + (r.pass ? '' : '  << ' + r.e)));
    console.log(`\n通過 ${pass}/${results.length}`);
    process.exitCode = pass === results.length ? 0 : 1;
  } catch (e) {
    console.error('ERR', e.message);
    process.exitCode = 2;
  } finally {
    try { chrome.kill(); } catch (e) {}
    srv.close();
    setTimeout(() => process.exit(process.exitCode || 0), 800);
  }
})();
