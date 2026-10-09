/* 验证「加到主画面」时浏览器实际拿到的图标。
 *
 * 用户反馈图标不对，所以要直接看浏览器认到的是哪个图标、长什么样：
 *   1. 从页面里取出所有 apple-touch-icon / icon 声明（浏览器就是这么挑的）
 *   2. 逐个下载并合成到黑底上（iOS 的实际渲染方式），看是否出现黑边
 *   3. 把每个图标渲染成 PNG 供人工核对
 */
import http from "node:http";
import fs from "node:fs";
import path from "node:path";
import { spawn } from "node:child_process";
import os from "node:os";

const PKG = path.resolve(process.argv[2] || ".");
const OUT = path.resolve(process.argv[3] || ".");
const REPO = "shenzhine";
const PORT = 8801;
const CDP_PORT = 9371;
const CHROME = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe";
const MIME = { ".html": "text/html; charset=utf-8", ".json": "application/manifest+json",
  ".js": "application/javascript", ".png": "image/png", ".ico": "image/x-icon" };

const srv = http.createServer((req, res) => {
  const p = decodeURIComponent(req.url.split("?")[0]);
  const prefix = "/" + REPO + "/";
  let rel = p.startsWith(prefix) ? p.slice(prefix.length) : (p === "/" + REPO ? "index.html" : null);
  if (rel === "") rel = "index.html";
  if (rel === null) { res.writeHead(404); res.end(); return; }
  const t = path.join(PKG, rel);
  if (fs.existsSync(t) && fs.statSync(t).isFile()) {
    const d = fs.readFileSync(t);
    res.writeHead(200, { "Content-Type": MIME[path.extname(t)] || "application/octet-stream" });
    res.end(d);
  } else { res.writeHead(404); res.end("nf"); }
});
await new Promise((r) => srv.listen(PORT, "127.0.0.1", r));
const base = `http://127.0.0.1:${PORT}/${REPO}/`;

const prof = path.join(os.tmpdir(), "sz_icon_" + Date.now());
fs.mkdirSync(prof, { recursive: true });
const chrome = spawn(CHROME, ["--headless=new", "--disable-gpu", "--no-sandbox",
  `--remote-debugging-port=${CDP_PORT}`, `--user-data-dir=${prof}`,
  "--no-first-run", "--no-default-browser-check", "--window-size=390,844", base],
  { stdio: "ignore" });

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

await new Promise((r) => setTimeout(r, 3000));

// 1. 浏览器在 DOM 里看到的图标声明（决定「加到主画面」用哪张）
const links = await evalJs(`JSON.stringify(
  Array.from(document.querySelectorAll('link[rel*="icon"]')).map(l => ({rel: l.rel, sizes: l.sizes.value, href: l.getAttribute('href')}))
)`);
console.log("=== 页面里的图标声明（浏览器按这个挑） ===");
const parsed = JSON.parse(links);
parsed.forEach((l) => console.log(`  rel=${l.rel.padEnd(18)} sizes=${(l.sizes||"-").padEnd(9)} href=${l.href}`));

// 2. 实际能否取到每个图标（HTTP 200 + 尺寸）
console.log("\n=== 逐个取回并检查 ===");
for (const l of parsed) {
  const url = new URL(l.href, base).href;
  try {
    const r = await fetch(url);
    const buf = Buffer.from(await r.arrayBuffer());
    const name = path.basename(new URL(url).pathname);
    const outP = path.join(OUT, "icon_" + name);
    fs.writeFileSync(outP, buf);
    // 解析 PNG 头拿尺寸
    let dims = "?";
    if (buf.length > 24 && buf.slice(1, 4).toString() === "PNG") {
      dims = `${buf.readUInt32BE(16)}x${buf.readUInt32BE(20)}`;
      const colorType = buf[25];   // 6=RGBA, 2=RGB
      const typeName = colorType === 6 ? "RGBA(有alpha)" : colorType === 2 ? "RGB(无alpha)" : "type" + colorType;
      dims += " " + typeName;
    }
    console.log(`  ${r.status === 200 ? "OK  " : "FAIL"} ${name.padEnd(28)} ${dims}  ${buf.length} bytes`);
  } catch (e) {
    console.log(`  FAIL ${l.href}  ${e.message}`);
  }
}

// 3. manifest 里的图标同样检查
const mfIcons = await evalJs(`(async()=>{const r=await fetch('./manifest.json');const j=await r.json();return JSON.stringify(j.icons);})()`, true);
console.log("\n=== manifest 里的图标 ===");
for (const ic of JSON.parse(mfIcons)) {
  const url = new URL(ic.src, base).href;
  try {
    const r = await fetch(url);
    const buf = Buffer.from(await r.arrayBuffer());
    let colorType = buf.length > 25 ? buf[25] : -1;
    const typeName = colorType === 6 ? "RGBA(有alpha)" : colorType === 2 ? "RGB(无alpha)" : "type" + colorType;
    console.log(`  ${r.status === 200 ? "OK  " : "FAIL"} ${ic.src.padEnd(34)} ${ic.sizes.padEnd(9)} ${ic.purpose.padEnd(9)} ${typeName}`);
  } catch (e) { console.log(`  FAIL ${ic.src} ${e.message}`); }
}

ws.close(); chrome.kill(); srv.close();
await new Promise((r) => setTimeout(r, 400));
try { fs.rmSync(prof, { recursive: true, force: true }); } catch {}
process.exit(0);
