/* 線上真實瀏覽器驗收：數學分區 + 額外資訊程式碼（GitHub Pages） */
const fs = require('fs');
const path = require('path');
const { spawn } = require('child_process');

const URL_BASE = 'https://nzgjsmy.github.io/ShenZhiHe/';
const CHROME = 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe';
const OUT = __dirname;
const sleep = ms => new Promise(r => setTimeout(r, ms));

(async () => {
  const results = [];
  const ok = (n, c, e) => results.push({ n, pass: !!c, e: e || '' });

  const prof = path.join(OUT, '_t_profile_on_' + Date.now());
  const chrome = spawn(CHROME, ['--headless=new', '--remote-debugging-port=9333',
    '--user-data-dir=' + prof, '--no-first-run', '--no-default-browser-check',
    '--disable-gpu', '--window-size=1200,900', 'about:blank'], { stdio: 'ignore' });

  try {
    let list = null;
    for (let i = 0; i < 50; i++) {
      await sleep(300);
      try { const r = await fetch('http://127.0.0.1:9333/json/list'); list = await r.json(); if (list && list.length) break; } catch (e) {}
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
        if (!/Failed to load resource|404|net::/.test(t)) errs.push('LOG ' + t.slice(0, 160));
      }
    });

    const ev = async (expr) => {
      const r = await send('Runtime.evaluate', { expression: expr, returnByValue: true, awaitPromise: true });
      if (r.exceptionDetails) throw new Error('Eval ' + JSON.stringify(r.exceptionDetails).slice(0, 200));
      return r.result.value;
    };
    const nav = async (hash) => {
      await send('Page.navigate', { url: URL_BASE + hash });
      await sleep(3500);
    };

    await nav('');
    const home = await ev('document.body.innerText');
    ok('線上首頁載入', home.length > 500);
    ok('線上首頁有四科', /化學/.test(home) && /物理/.test(home) && /生物/.test(home) && /數學/.test(home));
    ok('線上版號 V0.13.0', /V0\.13\.0/.test(home), home.slice(0, 120));

    await nav('#/math/extras/programs');
    await sleep(2000);
    const d = await ev(`(function(){
      var cards=document.querySelectorAll('.progcard');
      var codes=document.querySelectorAll('.progcode');
      var areas=[].map.call(document.querySelectorAll('.progarea'),function(e){return e.textContent.trim();});
      return {cards:cards.length, codes:codes.length, areas:areas,
        first:(codes[0]?codes[0].textContent:'').slice(0,50),
        copy:document.querySelectorAll('.pcopy').length,
        quick:!!document.querySelector('.progquick'),
        bytes:!!document.querySelector('.htable')};
    })()`);
    ok('線上四張程式卡片', d.cards === 4, JSON.stringify(d));
    ok('線上四段程式碼', d.codes === 4);
    ok('線上區號 P1~P4', JSON.stringify(d.areas) === JSON.stringify(['P1','P2','P3','P4']), JSON.stringify(d.areas));
    ok('線上程式碼開頭正確', d.first.startsWith('?→A:?→B:?→C:?→D:?→X:?→Y:'), d.first);
    ok('線上複製按鈕', d.copy === 4);
    ok('線上速查條與字節表', d.quick && d.bytes);

    // 逐字比對四段程式碼
    const codes = await ev(`[].map.call(document.querySelectorAll('.progcode'),function(e){return e.textContent;})`);
    const expect = JSON.parse(fs.readFileSync(path.join(OUT, '..', 'extras', 'math', 'programs.json'), 'utf8'));
    let match = true; const bad = [];
    expect.groups.forEach((g, i) => { if (codes[i] !== g.code) { match = false; bad.push(g.area); } });
    ok('線上四段程式逐字還原', match, bad.join(','));

    await nav('#/math/t/calc');
    await sleep(2000);
    const t = await ev('document.body.innerText');
    ok('線上數學課題頁', /計算機程式|看題型選區|四段程式/.test(t), t.slice(0, 150));

    await nav('#/chem');
    await sleep(2500);
    const chem = await ev('document.body.innerText');
    ok('線上化學分區正常', chem.length > 300 && /課題|知識點/.test(chem));

    // 圖片是否真的載入（不是 404）
    const imgs = await ev(`(function(){
      var ns=document.querySelectorAll('img');
      var total=ns.length, broken=0, sample=[];
      for(var i=0;i<ns.length;i++){
        if(!ns[i].complete || ns[i].naturalWidth===0){ broken++; if(sample.length<3) sample.push(ns[i].getAttribute('src')); }
      }
      return {total:total, broken:broken, sample:sample};
    })()`);
    ok('線上圖片載入正常', imgs.broken === 0, JSON.stringify(imgs));

    const realErrs = errs.filter(e => !/Failed to load resource/.test(e));
    ok('線上無 JS 例外', realErrs.length === 0, realErrs.slice(0, 3).join(' | '));

    await nav('#/math/extras/programs');
    await sleep(1500);
    await send('Emulation.setDeviceMetricsOverride', { width: 390, height: 844, deviceScaleFactor: 2, mobile: true });
    await sleep(800);
    const m = await send('Page.getLayoutMetrics');
    const h = Math.min(Math.ceil(m.cssContentSize.height), 14000);
    await send('Emulation.setDeviceMetricsOverride', { width: 390, height: h, deviceScaleFactor: 2, mobile: true });
    await sleep(800);
    const shot = await send('Page.captureScreenshot', { format: 'png', captureBeyondViewport: true });
    fs.writeFileSync(path.join(OUT, 'shot_online_math_prog.png'), Buffer.from(shot.data, 'base64'));

    ws.close();
    const pass = results.filter(r => r.pass).length;
    console.log('\n===== 線上驗收 =====');
    results.forEach(r => console.log((r.pass ? 'PASS ' : 'FAIL ') + r.n + (r.pass ? '' : '  << ' + r.e)));
    console.log(`\n通過 ${pass}/${results.length}`);
    process.exitCode = pass === results.length ? 0 : 1;
  } catch (e) {
    console.error('ERR', e.message);
    process.exitCode = 2;
  } finally {
    try { chrome.kill(); } catch (e) {}
    setTimeout(() => process.exit(process.exitCode || 0), 800);
  }
})();
