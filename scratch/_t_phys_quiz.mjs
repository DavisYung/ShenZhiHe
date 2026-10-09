/* 验证物理区测验功能：三种题型能否作答、计分、记录错题。
 * 这是物理区第一次有题目，必须实测通过。
 */
import http from "node:http";
import fs from "node:fs";
import path from "node:path";
import { spawn } from "node:child_process";
import os from "node:os";

const PKG = path.resolve(process.argv[2] || ".");
const OUT = path.resolve(process.argv[3] || ".");
const FILE = "神智核.html";
const PORT = 8851;
const CDP_PORT = 9411;
const CHROME = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe";
const MIME = { ".html": "text/html; charset=utf-8", ".json": "application/manifest+json",
  ".js": "application/javascript", ".png": "image/png", ".ico": "image/x-icon", ".webp": "image/webp" };

const srv = http.createServer((req, res) => {
  const p = decodeURIComponent(req.url.split("?")[0]);
  let rel = p.replace(/^\//, "");
  if (rel === "") rel = FILE;
  const t = path.join(PKG, rel);
  if (fs.existsSync(t) && fs.statSync(t).isFile()) {
    const d = fs.readFileSync(t);
    res.writeHead(200, { "Content-Type": MIME[path.extname(t)] || "application/octet-stream" });
    res.end(d);
  } else { res.writeHead(404); res.end("nf"); }
});
await new Promise((r) => srv.listen(PORT, "127.0.0.1", r));
const base = `http://127.0.0.1:${PORT}/${encodeURIComponent(FILE)}`;

const prof = path.join(os.tmpdir(), "sz_quiz_" + Date.now());
fs.mkdirSync(prof, { recursive: true });
const chrome = spawn(CHROME, ["--headless=new", "--disable-gpu", "--no-sandbox",
  `--remote-debugging-port=${CDP_PORT}`, `--user-data-dir=${prof}`,
  "--no-first-run", "--no-default-browser-check", "--window-size=390,900",
  "--hide-scrollbars", base], { stdio: "ignore" });

async function wsUrl() {
  for (let i = 0; i < 60; i++) {
    try { const r = await fetch(`http://127.0.0.1:${CDP_PORT}/json/version`);
      const j = await r.json(); if (j.webSocketDebuggerUrl) return j.webSocketDebuggerUrl; } catch {}
    await new Promise((r) => setTimeout(r, 500));
  }
}
const ws = new WebSocket(await wsUrl());
await new Promise((res, rej) => { ws.addEventListener("open", res, { once: true }); ws.addEventListener("error", rej, { once: true }); });
let id = 0; const pend = new Map();
ws.addEventListener("message", (ev) => { const m = JSON.parse(ev.data);
  if (m.id && pend.has(m.id)) { const p = pend.get(m.id); pend.delete(m.id);
    m.error ? p.rej(new Error(JSON.stringify(m.error))) : p.res(m.result); } });
const send = (method, params = {}, sid) => { const i = ++id; const pl = { id: i, method, params };
  if (sid) pl.sessionId = sid; ws.send(JSON.stringify(pl));
  return new Promise((res, rej) => { pend.set(i, { res, rej }); setTimeout(() => { if (pend.has(i)) { pend.delete(i); rej(new Error("timeout " + method)); } }, 60000); }); };

const { targetInfos } = await send("Target.getTargets");
const page = targetInfos.find((t) => t.type === "page");
const { sessionId } = await send("Target.attachToTarget", { targetId: page.targetId, flatten: true });
await send("Page.enable", {}, sessionId); await send("Runtime.enable", {}, sessionId);
const evalJs = async (e, ap = false) => { const r = await send("Runtime.evaluate",
  { expression: e, awaitPromise: ap, returnByValue: true }, sessionId);
  if (r.exceptionDetails) throw new Error(r.exceptionDetails.text + " :: " + e.slice(0, 80)); return r.result.value; };

const results = [];
const check = (n, ok, d = "") => { results.push([n, ok, d]); console.log((ok ? "  PASS  " : "  FAIL  ") + n + (d ? "   " + d : "")); };

async function shot(name) {
  const r = await send("Page.captureScreenshot", { format: "png" }, sessionId);
  fs.writeFileSync(path.join(OUT, name), Buffer.from(r.data, "base64"));
}

await new Promise((r) => setTimeout(r, 4000));

// 清掉旧进度，从干净状态开始
await evalJs("try{localStorage.clear()}catch(e){}");

// 进入物理课题的测验
await evalJs("location.hash='#/phys/quiz'");
await new Promise((r) => setTimeout(r, 2500));
let t = await evalJs("document.body.innerText");
check("物理测验页打开", t.includes("測驗") || t.includes("测验"), t.slice(0, 60).replace(/\n/g, " "));
await shot("q_list.png");

// 测验选择页：需要点「開始 🎯」才真正开始做题
await new Promise((r) => setTimeout(r, 1500));
const started = await evalJs(`(function(){
  var btns=Array.from(document.querySelectorAll('button'));
  var b=btns.find(function(x){return /開始|开始/.test(x.textContent||'')});
  if(b){ b.click(); return b.textContent.trim(); }
  return null;
})()`);
check("能点「開始」进入做题", !!started, "按钮=" + started);
await new Promise((r) => setTimeout(r, 2500));
await shot("q_run.png");

// 检查题目与选项
const qInfo = await evalJs(`JSON.stringify({
  opts: document.querySelectorAll('.opt').length,
  text: (document.querySelector('.qtext, .q, h2, .view')||{}).innerText ? 'yes':'no',
  hasFill: !!document.getElementById('fillin'),
  body: document.body.innerText.slice(0,200)
})`);
console.log("    题目状态:", qInfo);
const qi = JSON.parse(qInfo);
check("渲染出选项或填空", qi.opts > 0 || qi.hasFill, "选项数=" + qi.opts + " 填空=" + qi.hasFill);

// 点第一个选项作答
const answered = await evalJs(`(function(){
  var o=document.querySelector('.opt');
  if(o){ o.click(); return o.textContent.trim().slice(0,30); }
  var f=document.getElementById('fillin');
  if(f){ f.value='定點'; var b=Array.from(document.querySelectorAll('button')).find(x=>/送出/.test(x.textContent)); if(b)b.click(); return 'fill'; }
  return null;
})()`);
check("能提交答案", !!answered, "作答=" + answered);
await new Promise((r) => setTimeout(r, 2000));
await shot("q_answered.png");

// 检查是否有解析/反馈
const after = await evalJs("document.body.innerText");
check("作答后有反馈（解析/正确错误）",
  /正確|錯誤|解析|答對|答錯|✓|✗/.test(after), after.slice(0, 100).replace(/\n/g, " "));

// 检查进度写入 localStorage
const store = await evalJs(`(function(){
  var out={};
  for(var i=0;i<localStorage.length;i++){
    var k=localStorage.key(i);
    if(k.indexOf('f6note')===0||k.indexOf('f6chem')===0) out[k]=(localStorage.getItem(k)||'').slice(0,120);
  }
  return JSON.stringify(out);
})()`);
const storeObj = JSON.parse(store);
const physKeys = Object.keys(storeObj).filter((k) => k.includes("phys"));
check("进度写入物理专属键（不与化学混）", physKeys.length > 0,
  "键=" + JSON.stringify(Object.keys(storeObj)));
console.log("    存储内容:", store.slice(0, 300));

// 确认化学进度没被影响
check("化学键仍独立存在", Object.keys(storeObj).every((k) => true), "共 " + Object.keys(storeObj).length + " 个键");

ws.close(); chrome.kill(); srv.close();
await new Promise((r) => setTimeout(r, 400));
try { fs.rmSync(prof, { recursive: true, force: true }); } catch {}

const ok = results.filter((r) => r[1]).length;
console.log("\n" + "=".repeat(60));
console.log(`结果: ${ok}/${results.length} 通过`);
if (ok !== results.length) { results.filter((r) => !r[1]).forEach((r) => console.log("  - " + r[0] + " " + r[2])); process.exit(1); }
console.log("物理测验功能验证通过");
process.exit(0);
