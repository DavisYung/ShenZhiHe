/* 诊断：渲染后的页面里「温」(U+6E29) 到底出现在哪个元素/字段。
 * 不猜，直接遍历 DOM 定位。
 */
import http from "node:http";
import fs from "node:fs";
import path from "node:path";
import { spawn } from "node:child_process";
import os from "node:os";

const PKG = path.resolve(process.argv[2] || ".");
const FILE = "神智核.html";
const PORT = 8871;
const CDP_PORT = 9431;
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
const prof = path.join(os.tmpdir(), "sz_diag_" + Date.now());
fs.mkdirSync(prof, { recursive: true });
const chrome = spawn(CHROME, ["--headless=new", "--disable-gpu", "--no-sandbox",
  `--remote-debugging-port=${CDP_PORT}`, `--user-data-dir=${prof}`,
  "--no-first-run", "--no-default-browser-check", "--window-size=390,900", base], { stdio: "ignore" });

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
  if (r.exceptionDetails) throw new Error(r.exceptionDetails.text); return r.result.value; };

await new Promise((r) => setTimeout(r, 5000));

for (const tid of ["heat1", "heat2", "heat3", "heat4", "heat5"]) {
  await evalJs(`location.hash='#/phys/t/${tid}'`);
  await new Promise((r) => setTimeout(r, 2500));
  // 找出所有含 U+6E29 的元素及其上下文
  const info = await evalJs(`(function(){
    var out=[];
    var walker=document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
    var n;
    while((n=walker.nextNode())){
      var v=n.nodeValue||'';
      if(v.indexOf('\\u6e29')>=0){
        out.push({
          tag:(n.parentElement&&n.parentElement.tagName)||'?',
          cls:(n.parentElement&&n.parentElement.className)||'',
          ctx:v.slice(Math.max(0,v.indexOf('\\u6e29')-30), v.indexOf('\\u6e29')+30)
        });
      }
    }
    // 也检查输入框/属性
    return JSON.stringify({count:out.length, items:out.slice(0,4)});
  })()`);
  console.log(`\n=== ${tid} ===`);
  console.log(info);
}

// 检查数据源里是否还有残留（通过 payload script 标签）
const payloadInfo = await evalJs(`(function(){
  var el=document.getElementById('payload');
  if(!el) return 'no payload';
  var s=el.textContent;
  var n=(s.match(/\\u6e29/g)||[]).length;
  var i=s.indexOf('\\u6e29');
  return JSON.stringify({count:n, ctx: i>=0 ? s.slice(i-60,i+60) : ''});
})()`);
console.log("\n=== 内嵌数据 payload 里的「温」 ===");
console.log(payloadInfo);

ws.close(); chrome.kill(); srv.close();
await new Promise((r) => setTimeout(r, 400));
try { fs.rmSync(prof, { recursive: true, force: true }); } catch {}
process.exit(0);
