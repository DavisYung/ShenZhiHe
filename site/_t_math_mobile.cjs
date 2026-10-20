/* 手機尺寸截圖：數學分區首頁 + 額外資訊程式頁 */
const http = require('http');
const fs = require('fs');
const path = require('path');
const { spawn } = require('child_process');

const ROOT = __dirname;
const PORT = 8732;
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
  const prof = path.join(ROOT, '_t_profile_m_' + Date.now());
  const chrome = spawn(CHROME, ['--headless=new', '--remote-debugging-port=9332', '--user-data-dir=' + prof,
    '--no-first-run', '--no-default-browser-check', '--disable-gpu', 'about:blank'], { stdio: 'ignore' });
  try {
    let list = null;
    for (let i = 0; i < 40; i++) { await sleep(300);
      try { const r = await fetch('http://127.0.0.1:9332/json/list'); list = await r.json(); if (list && list.length) break; } catch (e) {} }
    const page = list.find(t => t.type === 'page') || list[0];
    const ws = new WebSocket(page.webSocketDebuggerUrl);
    await new Promise((res, rej) => { ws.addEventListener('open', res, { once: true }); ws.addEventListener('error', rej, { once: true }); });
    let id = 0; const pending = new Map();
    ws.addEventListener('message', ev => { const m = JSON.parse(ev.data);
      if (m.id && pending.has(m.id)) { pending.get(m.id)(m); pending.delete(m.id); } });
    const send = (method, params) => new Promise((res, rej) => { const i = ++id;
      pending.set(i, m => m.error ? rej(new Error(method + ':' + JSON.stringify(m.error))) : res(m.result));
      ws.send(JSON.stringify({ id: i, method, params: params || {} })); });

    await send('Page.enable');
    await send('Runtime.enable');
    await send('Emulation.setDeviceMetricsOverride', { width: 390, height: 844, deviceScaleFactor: 2, mobile: true });

    const shots = [
      ['#/math', 'shot_m_home.png', 1600],
      ['#/math/extras', 'shot_m_extras.png', 1400],
      ['#/math/extras/programs', 'shot_m_prog.png', 2000],
      ['#/math/t/calc', 'shot_m_topic.png', 1800]
    ];
    for (const [hash, name, wait] of shots) {
      await send('Page.navigate', { url: `http://127.0.0.1:${PORT}/${encodeURIComponent(TARGET)}${hash}` });
      await sleep(wait);
      const r = await send('Runtime.evaluate', {
        expression: `(function(){var d=document.documentElement;return {sw:d.scrollWidth,cw:d.clientWidth,sh:document.body.scrollHeight};})()`,
        returnByValue: true });
      const info = r.result.value;
      const tooWide = info.sw > info.cw + 2;
      const m = await send('Page.getLayoutMetrics');
      const h = Math.min(Math.ceil(m.cssContentSize.height), 14000);
      await send('Emulation.setDeviceMetricsOverride', { width: 390, height: h, deviceScaleFactor: 2, mobile: true });
      await sleep(500);
      const shot = await send('Page.captureScreenshot', { format: 'png', captureBeyondViewport: true });
      fs.writeFileSync(path.join(ROOT, name), Buffer.from(shot.data, 'base64'));
      console.log(`${name}  scrollW=${info.sw} clientW=${info.cw} 高度=${h}  ${tooWide ? '❌ 橫向溢出' : '✅ 無溢出'}`);
      await send('Emulation.setDeviceMetricsOverride', { width: 390, height: 844, deviceScaleFactor: 2, mobile: true });
    }
    ws.close();
  } catch (e) { console.error('ERR', e.message); }
  finally { try { chrome.kill(); } catch (e) {} srv.close(); setTimeout(() => process.exit(0), 600); }
})();
