/* 查证：物理首页「準備中」到底出现在哪个元素里。 */
import http from "node:http";
import fs from "node:fs";
import path from "node:path";
import { spawn } from "node:child_process";
import os from "node:os";

const PKG = path.resolve(process.argv[2] || ".");
const FILE = "神智核.html";
const PORT = 8881, CDP_PORT = 9441;
const CHROME = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe";
const MIME = { ".html": "text/html; charset=utf-8", ".json": "application/manifest+json",
  ".js": "application/javascript", ".png": "image/png", ".ico": "image/x-icon", ".webp": "image/webp" };
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
const prof = path.join(os.tmpdir(), "sz_prep_" + Date.now());
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
  return new Promise((res, rej) => { pend.set(i, { res, rej }); setTimeout(() => { if (pend.has(i)) { pend.delete(i); rej(new Error("timeout")); } }, 60000); }); };
const { targetInfos } = await send("Target.getTargets");
const page = targetInfos.find((t) => t.type === "page");
const { sessionId } = await send("Target.attachToTarget", { targetId: page.targetId, flatten: true });
await send("Page.enable", {}, sessionId); await send("Runtime.enable", {}, sessionId);
const evalJs = async (e, ap = false) => { const r = await send("Runtime.evaluate",
  { expression: e, awaitPromise: ap, returnByValue: true }, sessionId);
  if (r.exceptionDetails) throw new Error(r.exceptionDetails.text); return r.result.value; };

await new Promise((r) => setTimeout(r, 5000));
await evalJs("location.hash='#/phys/home'");
await new Promise((r) => setTimeout(r, 3000));

// 找出所有含「準備中」的元素及其完整文字
const info = await evalJs(`(function(){
  var out=[];
  document.querySelectorAll('*').forEach(function(el){
    if(el.children.length===0 && /準備中/.test(el.textContent||'')){
      out.push({tag:el.tagName, cls:el.className||'', text:(el.textContent||'').trim().slice(0,80),
                parentCls:(el.parentElement&&el.parentElement.className)||''});
    }
  });
  return JSON.stringify(out.slice(0,10));
})()`);
console.log("=== 含「準備中」的叶子元素 ===");
console.log(info);

// 列出物理首页的课题卡片
const cards = await evalJs(`(function(){
  var out=[];
  document.querySelectorAll('.tcard, .subcard, .card, [class*="tcard"]').forEach(function(el){
    out.push({cls:el.className, text:(el.textContent||'').trim().replace(/\\s+/g,' ').slice(0,90)});
  });
  return JSON.stringify(out.slice(0,12));
})()`);
console.log("\n=== 课题卡片 ===");
console.log(cards);

// 完整 innerText 前 900 字
const body = await evalJs("document.body.innerText.slice(0,900)");
console.log("\n=== 页面文本 ===");
console.log(body);

ws.close(); chrome.kill(); srv.close();
await new Promise((r) => setTimeout(r, 400));
try { fs.rmSync(prof, { recursive: true, force: true }); } catch {}
process.exit(0);
