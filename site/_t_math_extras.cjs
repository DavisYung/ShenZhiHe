/* 驗收數學分區 + 額外資訊程式碼（Node + CDP 直連 Chrome，免 playwright） */
const http = require('http');
const fs = require('fs');
const path = require('path');
const { spawn } = require('child_process');

const ROOT = path.join(__dirname);
const PORT = 8731;
const CHROME = 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe';
const TARGET = '神智核.html';

const MIME = { '.html': 'text/html; charset=utf-8', '.js': 'application/javascript; charset=utf-8',
  '.json': 'application/json; charset=utf-8', '.svg': 'image/svg+xml', '.png': 'image/png',
  '.webp': 'image/webp', '.css': 'text/css; charset=utf-8' };

const srv = http.createServer((req, res) => {
  let p = decodeURIComponent(req.url.split('?')[0].split('#')[0]);
  if (p === '/') p = '/' + TARGET;
  const fp = path.join(ROOT, p);
  if (!fp.startsWith(ROOT) || !fs.existsSync(fp) || fs.statSync(fp).isDirectory()) {
    res.writeHead(404); res.end('404'); return;
  }
  res.writeHead(200, { 'Content-Type': MIME[path.extname(fp)] || 'application/octet-stream' });
  fs.createReadStream(fp).pipe(res);
});

const sleep = ms => new Promise(r => setTimeout(r, ms));

async function cdp(wsUrl) {
  const WS = globalThis.WebSocket;
  const ws = new WS(wsUrl);
  ws.addEventListener('error', e => console.error('WS error', e.message || ''));
  await new Promise((res, rej) => {
    ws.addEventListener('open', res, { once: true });
    ws.addEventListener('error', rej, { once: true });
  });
  let id = 0; const pending = new Map(); const events = [];
  const msgListeners = [];
  ws.addEventListener('message', ev => {
    const m = JSON.parse(typeof ev.data === 'string' ? ev.data : ev.data);
    if (m.id && pending.has(m.id)) { pending.get(m.id)(m); pending.delete(m.id); }
    else if (m.method) { events.push(m); msgListeners.forEach(fn => fn(m)); }
  });
  const send = (method, params) => new Promise((res, rej) => {
    const i = ++id; pending.set(i, m => m.error ? rej(new Error(method + ': ' + JSON.stringify(m.error))) : res(m.result));
    ws.send(JSON.stringify({ id: i, method, params: params || {} }));
  });
  return { ws, send, events, onMessage: fn => msgListeners.push(fn) };
}

(async () => {
  await new Promise(r => srv.listen(PORT, r));
  const results = [];
  const ok = (name, cond, extra) => { results.push({ name, pass: !!cond, extra: extra || '' }); };

  const prof = path.join(ROOT, '_t_profile_math_' + Date.now());
  const chrome = spawn(CHROME, ['--headless=new', '--remote-debugging-port=9331',
    '--user-data-dir=' + prof, '--no-first-run', '--no-default-browser-check',
    '--disable-gpu', '--window-size=1200,900', 'about:blank'], { stdio: 'ignore' });

  try {
    let list = null;
    for (let i = 0; i < 40; i++) {
      await sleep(300);
      try {
        const r = await fetch('http://127.0.0.1:9331/json/list');
        list = await r.json();
        if (list && list.length) break;
      } catch (e) {}
    }
    if (!list || !list.length) throw new Error('Chrome CDP 未就緒');
    const page = list.find(t => t.type === 'page') || list[0];
    const { ws, send, events, onMessage } = await cdp(page.webSocketDebuggerUrl);

    await send('Page.enable');
    await send('Runtime.enable');
    await send('Log.enable');
    const consoleErrs = [];
    onMessage(m => {
      if (m.method === 'Runtime.exceptionThrown') {
        consoleErrs.push('EXC: ' + (m.params.exceptionDetails?.text || '') + ' ' +
          (m.params.exceptionDetails?.exception?.description || '').slice(0, 200));
      }
      if (m.method === 'Log.entryAdded' && m.params.entry.level === 'error') {
        const t = m.params.entry.text || '';
        if (!/Failed to load resource|404/.test(t)) consoleErrs.push('LOG: ' + t.slice(0, 200));
      }
    });

    const evalJS = async (expr) => {
      const r = await send('Runtime.evaluate', { expression: expr, returnByValue: true, awaitPromise: true });
      if (r.exceptionDetails) throw new Error('Eval: ' + JSON.stringify(r.exceptionDetails).slice(0, 300));
      return r.result.value;
    };
    const nav = async (hash) => {
      await send('Page.navigate', { url: `http://127.0.0.1:${PORT}/${encodeURIComponent(TARGET)}${hash}` });
      await sleep(1800);
    };

    // 1) 首頁：數學科目存在
    await nav('');
    const homeTxt = await evalJS('document.body.innerText');
    ok('首頁出現數學科目', /數學/.test(homeTxt), homeTxt.includes('數學') ? '' : homeTxt.slice(0, 200));
    ok('首頁科目數含四科', /化學/.test(homeTxt) && /物理/.test(homeTxt) && /生物/.test(homeTxt) && /數學/.test(homeTxt));

    // 2) 進數學科目
    await nav('#/math');
    await sleep(1500);
    const mathTxt = await evalJS('document.body.innerText');
    ok('數學分區可進入', /計算機程式/.test(mathTxt), mathTxt.slice(0, 300));

    // 3) 額外資訊列表
    await nav('#/math/extras');
    await sleep(1200);
    const exTxt = await evalJS('document.body.innerText');
    ok('額外資訊有程式卡片', /fx-50FH II 四段萬能程式碼/.test(exTxt), exTxt.slice(0, 300));
    ok('額外資訊標題正確', /額外資訊/.test(exTxt));

    // 4) 進程式碼頁
    await nav('#/math/extras/programs');
    await sleep(1500);
    const detail = await evalJS(`(function(){
      var cards=document.querySelectorAll('.progcard');
      var codes=document.querySelectorAll('.progcode');
      var areas=[].map.call(document.querySelectorAll('.progarea'),function(e){return e.textContent.trim();});
      var firstCode=codes[0]?codes[0].textContent:'';
      return {nCards:cards.length, nCodes:codes.length, areas:areas,
        firstLen:firstCode.length, firstHead:firstCode.slice(0,40),
        hasP1:firstCode.indexOf('?→A')===0,
        hasCopy:document.querySelectorAll('.pcopy').length,
        hasQuick:!!document.querySelector('.progquick'),
        hasBytes:!!document.querySelector('.htable')};
    })()`);
    ok('四張程式卡片', detail.nCards === 4, JSON.stringify(detail));
    ok('四段程式碼都在', detail.nCodes === 4);
    ok('區號 P1~P4 正確', JSON.stringify(detail.areas) === JSON.stringify(['P1','P2','P3','P4']), JSON.stringify(detail.areas));
    ok('程式碼開頭正確', detail.hasP1, detail.firstHead);
    ok('複製按鈕存在', detail.hasCopy === 4);
    ok('速查條存在', detail.hasQuick);
    ok('字節表存在', detail.hasBytes);

    // 5) 四段程式碼內容逐字比對（防止 esc 變形）
    const codeCheck = await evalJS(`(function(){
      return [].map.call(document.querySelectorAll('.progcode'),function(e){return e.textContent;});
    })()`);
    const expect = JSON.parse(fs.readFileSync(path.join(ROOT, '..', 'extras', 'math', 'programs.json'), 'utf8'));
    let allMatch = true; const mismatch = [];
    expect.groups.forEach((g, i) => {
      if (codeCheck[i] !== g.code) { allMatch = false; mismatch.push(g.area + ' 不一致'); }
    });
    ok('四段程式碼逐字還原', allMatch, mismatch.join(','));
    ok('程式碼含中文全形符號', /→|◢|⇒/.test(codeCheck[0] || ''), (codeCheck[0] || '').slice(0, 60));

    // 6) 複製功能（headless 下 clipboard 可能不可用，只驗按鈕不拋錯）
    await evalJS(`document.getElementById('pcopy0').click(); 'clicked'`);
    await sleep(400);
    const btnTxt = await evalJS(`document.getElementById('pcopy0').textContent`);
    ok('複製按鈕有回饋', /已複製|長按/.test(btnTxt), btnTxt);

    // 7) 數學課題頁可開
    await nav('#/math/t/calc');
    await sleep(1500);
    const topicTxt = await evalJS('document.body.innerText');
    ok('計算機程式課題頁可開', /P1|四段程式|看題型選區/.test(topicTxt), topicTxt.slice(0, 300));

    // 8) 其他科目未受影響
    await nav('#/chem');
    await sleep(1500);
    const chemTxt = await evalJS('document.body.innerText');
    ok('化學分區正常', /課題|知識點|化學/.test(chemTxt) && chemTxt.length > 200);

    // 9) console 錯誤
    const realErrs = consoleErrs.filter(e => !/Failed to load resource/.test(e));
    ok('無 JS 例外', realErrs.length === 0, realErrs.slice(0, 3).join(' | '));

    // 截圖
    await nav('#/math/extras/programs');
    await sleep(1200);
    const metrics = await send('Page.getLayoutMetrics');
    const h = Math.min(Math.ceil(metrics.cssContentSize.height), 12000);
    await send('Emulation.setDeviceMetricsOverride', { width: 1200, height: h, deviceScaleFactor: 1, mobile: false });
    await sleep(600);
    const shot = await send('Page.captureScreenshot', { format: 'png', captureBeyondViewport: true });
    fs.writeFileSync(path.join(ROOT, 'shots_math_programs.png'), Buffer.from(shot.data, 'base64'));
    await send('Emulation.clearDeviceMetricsOverride');

    ws.close();

    const pass = results.filter(r => r.pass).length;
    console.log('\n===== 驗收結果 =====');
    results.forEach(r => console.log((r.pass ? 'PASS ' : 'FAIL ') + r.name + (r.pass ? '' : '  << ' + r.extra)));
    console.log(`\n通過 ${pass}/${results.length}`);
    const failed = results.filter(r => !r.pass);
    process.exitCode = failed.length ? 1 : 0;
  } catch (e) {
    console.error('ERR', e.message);
    process.exitCode = 2;
  } finally {
    try { chrome.kill(); } catch (e) {}
    srv.close();
    setTimeout(() => process.exit(process.exitCode || 0), 800);
  }
})();
