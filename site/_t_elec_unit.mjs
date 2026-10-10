/* 定向验证电学单元：物理首页 → 電學单元 → 六课题 → 整个分区测验。

自建本地 HTTP 服务 + 真实 Chrome，与 _t_units.mjs 同一套做法
（file:// 协议下 hash 路由不可靠，必须走 HTTP）。
*/
import http from "node:http";
import fs from "node:fs";
import path from "node:path";
import { spawn } from "node:child_process";
import os from "node:os";

const PKG = path.resolve(process.argv[2] || ".");
const OUT = path.resolve(process.argv[3] || ".");
const FILE = ["神智核.html", "index.html"].find((n) => fs.existsSync(path.join(PKG, n))) || "神智核.html";
const PORT = 8897;
const CHROME = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe";
const MIME = { ".html": "text/html; charset=utf-8", ".json": "application/manifest+json",
  ".js": "application/javascript", ".png": "image/png", ".webp": "image/webp",
  ".ico": "image/x-icon" };

const srv = http.createServer((req, res) => {
  const p = decodeURIComponent(req.url.split("?")[0]);
  let rel = p.replace(/^\//, ""); if (rel === "") rel = FILE;
  const t = path.join(PKG, rel);
  if (fs.existsSync(t) && fs.statSync(t).isFile()) {
    const d = fs.readFileSync(t);
    res.writeHead(200, { "Content-Type": MIME[path.extname(t)] || "application/octet-stream" });
    res.end(d);
  } else { res.writeHead(404); res.end("nf"); }
});
await new Promise((r) => srv.listen(PORT, "127.0.0.1", r));
const base = `http://127.0.0.1:${PORT}/${encodeURIComponent(FILE)}`;

const prof = path.join(os.tmpdir(), "sz_elec_" + Date.now());
fs.mkdirSync(prof, { recursive: true });
const chrome = spawn(CHROME, ["--headless=new", "--disable-gpu", "--no-sandbox",
  "--user-data-dir=" + prof, "--remote-debugging-port=9459",
  "--window-size=1280,1400", base]);

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

async function cdp() {
  for (let i = 0; i < 60; i++) {
    try {
      const j = await (await fetch("http://127.0.0.1:9459/json/list")).json();
      const pg = j.find((x) => x.type === "page" && x.webSocketDebuggerUrl);
      if (pg) return pg.webSocketDebuggerUrl;
    } catch { }
    await sleep(250);
  }
  throw new Error("CDP not ready");
}

const ws = new (await import("node:worker_threads")) ? null : null; // 占位不用
const { WebSocket } = await import("node:http").then(() => globalThis.WebSocket ? { WebSocket: globalThis.WebSocket } : { WebSocket: null });

const results = [];
const ok = (n, c, d) => { results.push([n, !!c]); console.log((c ? "  PASS " : "  FAIL ") + n + (d ? "  " + d : "")); };

(async () => {
  const wsUrl = await cdp();
  const sock = new WebSocket(wsUrl);
  let mid = 0; const pending = new Map();
  sock.addEventListener("message", (ev) => {
    const m = JSON.parse(ev.data);
    if (m.id && pending.has(m.id)) { pending.get(m.id)(m); pending.delete(m.id); }
  });
  await new Promise((r) => sock.addEventListener("open", r));
  const send = (method, params = {}) => new Promise((res) => {
    const id = ++mid; pending.set(id, (m) => res(m.result));
    sock.send(JSON.stringify({ id, method, params }));
  });
  const evaluate = async (expr) => {
    const r = await send("Runtime.evaluate", { expression: expr, returnByValue: true, awaitPromise: true });
    return r.result ? r.result.value : undefined;
  };

  await sleep(1200);

  // 进物理区
  await evaluate("document.querySelector('a[href*=\"phys\"],button')&&0");
  const subj = await evaluate(`(()=>{const e=[...document.querySelectorAll('a,button')].find(x=>/物理/.test(x.textContent));if(e){e.click();return true}return false})()`);
  await sleep(700);
  ok('进入物理区', subj);

  // 首页单元卡片
  const cards = await evaluate(`(()=>{const e=[...document.querySelectorAll('[class*="unit"],[class*="card"]')].map(x=>x.textContent.trim()).filter(t=>/熱學|力學|波動學|電學/.test(t)&&t.length<80);return [...new Set(e)]})()`);
  ok('首页显示 4 个单元', cards.length >= 4, cards.length + ' 个');
  ok('其中含「電學」', cards.some(c => /電學/.test(c)),
     cards.filter(c => /電學/.test(c)).join(' ').slice(0, 40));

  // 点電學单元卡
  const go = await evaluate(`(()=>{
    const els=[...document.querySelectorAll('a,button,[class*="card"]')];
    const e=els.find(x=>/電學/.test(x.textContent)&&x.textContent.length<80);
    if(e){e.click();return e.tagName+'|'+e.className}return ''})()`);
  await sleep(900);
  const hash = await evaluate("location.hash");
  ok('点击電學卡片', !!go, go + ' hash=' + hash);

  const html = await evaluate("document.body.innerHTML.length");
  const bodyText = await evaluate("document.body.innerText");
  ok('进入电学单元页', /靜電學/.test(bodyText) && /交流電與變壓器/.test(bodyText),
     'len=' + html);

  // 六课题
  const titles = await evaluate(`(()=>{const e=[...document.querySelectorAll('h3,h4,[class*="title"]')].map(x=>x.textContent.trim());return [...new Set(e)].filter(t=>/靜電學|電路|家居電學|電磁學|電磁感應|交流電與變壓器/.test(t))})()`);
  ok('单元页列出电学 6 課', titles.length >= 6, titles.length + ' 个: ' + titles.slice(0, 6).join('/'));

  // 发起整分区测验
  const btn = await evaluate(`(()=>{const b=[...document.querySelectorAll('a,button')].find(x=>/整個分區|本分區|測驗本分區/.test(x.textContent));if(b){b.click();return b.textContent.trim()}return ''})()`);
  await sleep(900);
  const quizText = await evaluate("document.body.innerText");
  const qm = (quizText.match(/第\s*1\s*\/\s*(\d+)\s*題/) || [])[1];
  ok('点「整個分區」按钮', !!btn, btn);
  ok('进入电学整单元测验', !!qm, qm ? '共 ' + qm + ' 題' : '未见题号');
  ok('题数为 95（六课之和）', qm === '95', '实际 ' + qm);

  // 有题面
  const q = await evaluate(`document.body.innerText.slice(0,120)`);
  ok('测验有题面', q.length > 20, q.replace(/\\n/g, ' ').slice(0, 50));

  await sock.close();
  chrome.kill();
  await sleep(300);
  try { fs.rmSync(prof, { recursive: true, force: true }); } catch { }

  const pass = results.filter((r) => r[1]).length;
  console.log('\n结果: ' + pass + '/' + results.length + ' 通过');
  console.log(pass === results.length ? '电学单元导航验证通过' : '电学单元导航有问题');
  process.exit(pass === results.length ? 0 : 1);
})().catch((e) => { console.error('ERR', e.stack || e.message); chrome.kill(); process.exit(1); });
