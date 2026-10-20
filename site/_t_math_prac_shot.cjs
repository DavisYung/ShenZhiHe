/* 分段截圖：數學課題頁的練習區塊（手機 390px，只截視窗，避免超長圖） */
const http = require('http');
const fs = require('fs');
const path = require('path');
const { spawn } = require('child_process');

const ROOT = __dirname;
const PORT = 8735;
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
  const prof = path.join(ROOT, '_t_profile_seg_' + Date.now());
  const chrome = spawn(CHROME, ['--headless=new', '--remote-debugging-port=9335',
    '--user-data-dir=' + prof, '--no-first-run', '--no-default-browser-check',
    '--disable-gpu', 'about:blank'], { stdio: 'ignore' });
  try {
    let list = null;
    for (let i = 0; i < 40; i++) {
      await sleep(300);
      try { const r = await fetch('http://127.0.0.1:9335/json/list'); list = await r.json(); if (list && list.length) break; } catch (e) {}
    }
    const page = list.find(t => t.type === 'page') || list[0];
    const ws = new WebSocket(page.webSocketDebuggerUrl);
    await new Promise((res, rej) => { ws.addEventListener('open', res, { once: true }); ws.addEventListener('error', rej, { once: true }); });
    let id = 0; const pending = new Map();
    ws.addEventListener('message', ev => { const m = JSON.parse(ev.data);
      if (m.id && pending.has(m.id)) { pending.get(m.id)(m); pending.delete(m.id); } });
    const send = (method, params) => new Promise((res, rej) => { const i = ++id;
      pending.set(i, m => m.error ? rej(new Error(method + ':' + JSON.stringify(m.error))) : res(m.result));
      ws.send(JSON.stringify({ id: i, method, params: params || {} })); });

    await send('Page.enable'); await send('Runtime.enable');
    await send('Emulation.setDeviceMetricsOverride', { width: 390, height: 844, deviceScaleFactor: 2, mobile: true });

    await send('Page.navigate', { url: `http://127.0.0.1:${PORT}/${encodeURIComponent(TARGET)}#/math/t/calc` });
    await sleep(3000);

    // 找出各練習章節的 y 座標
    const r = await send('Runtime.evaluate', {
      expression: `(function(){
        var out=[];
        var els=document.querySelectorAll('h3,h4,.sech,.sh');
        for(var i=0;i<els.length;i++){
          var tx=els[i].textContent||'';
          if(tx.indexOf('練習')>=0){
            var rect=els[i].getBoundingClientRect();
            out.push({t:tx.trim().slice(0,20), y:Math.round(rect.top+window.scrollY)});
          }
        }
        return out;
      })()`, returnByValue: true });
    const marks = r.result.value;
    console.log('練習章節位置：', JSON.stringify(marks));

    // 逐段截圖
    const targets = marks.length ? marks : [{ t: 'fallback', y: 0 }];
    let n = 0;
    for (const mk of targets) {
      n++;
      await send('Runtime.evaluate', { expression: `window.scrollTo(0, ${Math.max(0, mk.y - 20)})` });
      await sleep(900);
      const shot = await send('Page.captureScreenshot', { format: 'png' });
      const name = `shot_prac_${n}.png`;
      fs.writeFileSync(path.join(ROOT, name), Buffer.from(shot.data, 'base64'));
      console.log(`  ${name}  ← ${mk.t} (y=${mk.y})`);
    }
    ws.close();
  } catch (e) { console.error('ERR', e.message); }
  finally { try { chrome.kill(); } catch (e) {} srv.close(); setTimeout(() => process.exit(0), 600); }
})();
