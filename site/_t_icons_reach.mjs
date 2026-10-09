/* 验证「图标 404」是导致 iOS 生成占位图标的根因，并证明新布局不会再 404。
 *
 * 背景：用户线上站点 icons/ 整个目录 404，而 <link rel="apple-touch-icon"> 指向
 * ./icons/apple-touch-icon.png。iOS 在这种情况下不会回退到根目录图标，而是用
 * theme-color 底色 + 标题首字生成占位图标（teal 底 + 白色「神」字）。
 *
 * 本脚本：
 *   1. 逐个请求 HTML 里声明的每个图标 URL，断言全部 200（不能有 404）
 *   2. 读取 PNG 头确认 colorType=2（RGB，无 alpha）
 *   3. 打印每个图标的实际尺寸，与 sizes 属性比对
 */
import http from "node:http";
import fs from "node:fs";
import path from "node:path";
import { spawn } from "node:child_process";
import os from "node:os";

const PKG = path.resolve(process.argv[2] || ".");
const REPO = "ShenZhiHe";              // 用用户真实的仓库名
const PORT = 8821;
const CDP_PORT = 9381;
const CHROME = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe";
const MIME = { ".html": "text/html; charset=utf-8", ".json": "application/manifest+json",
  ".js": "application/javascript", ".png": "image/png", ".ico": "image/x-icon" };

/* 记录每个请求的路径，用于发现 404 */
const requested = [];
const srv = http.createServer((req, res) => {
  const p = decodeURIComponent(req.url.split("?")[0]);
  const prefix = "/" + REPO + "/";
  let rel = p.startsWith(prefix) ? p.slice(prefix.length) : (p === "/" + REPO ? "index.html" : null);
  if (rel === "") rel = "index.html";
  if (rel === null) { requested.push([p, 404]); res.writeHead(404); res.end(); return; }
  const t = path.join(PKG, rel);
  if (fs.existsSync(t) && fs.statSync(t).isFile()) {
    const d = fs.readFileSync(t);
    requested.push([p, 200]);
    res.writeHead(200, { "Content-Type": MIME[path.extname(t)] || "application/octet-stream" });
    res.end(d);
  } else {
    requested.push([p, 404]);
    res.writeHead(404); res.end("nf");
  }
});
await new Promise((r) => srv.listen(PORT, "127.0.0.1", r));
const base = `http://127.0.0.1:${PORT}/${REPO}/`;

const prof = path.join(os.tmpdir(), "sz_icontest_" + Date.now());
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

await new Promise((r) => setTimeout(r, 3500));

const links = JSON.parse(await evalJs(`JSON.stringify(
  Array.from(document.querySelectorAll('link[rel*="icon"]')).map(l => ({rel: l.rel, sizes: l.sizes.value, href: l.getAttribute('href')}))
)`));

let fail = 0;
console.log("=== 1. HTML 声明的图标全部可达（404 会让 iOS 生成占位图标）===");
for (const l of links) {
  const url = new URL(l.href, base).href;
  const resp = await fetch(url);
  const buf = Buffer.from(await resp.arrayBuffer());
  let dims = "?", type = "?";
  if (buf.slice(1, 4).toString() === "PNG") {
    dims = `${buf.readUInt32BE(16)}x${buf.readUInt32BE(20)}`;
    const ct = buf[25];
    type = ct === 2 ? "RGB(无alpha)" : ct === 6 ? "RGBA(有alpha!)" : "type" + ct;
  }
  const ok = resp.status === 200 && (type.includes("无alpha") || dims === "?");
  if (!ok) fail++;
  console.log(`  ${ok ? "PASS" : "FAIL"}  ${l.rel.padEnd(18)} sizes=${(l.sizes||"-").padEnd(9)} ${dims.padEnd(9)} ${type.padEnd(14)} ${l.href}`);
}

console.log("\n=== 2. manifest 图标全部可达 ===");
const mf = JSON.parse(await evalJs(`(async()=>{const r=await fetch('./manifest.json');const j=await r.json();return JSON.stringify(j.icons);})()`, true));
for (const ic of mf) {
  const resp = await fetch(new URL(ic.src, base).href);
  const buf = Buffer.from(await resp.arrayBuffer());
  const ct = buf.length > 25 ? buf[25] : -1;
  const type = ct === 2 ? "RGB(无alpha)" : ct === 6 ? "RGBA(有alpha!)" : "type" + ct;
  const ok = resp.status === 200 && ct === 2;
  if (!ok) fail++;
  console.log(`  ${ok ? "PASS" : "FAIL"}  ${ic.src.padEnd(28)} ${ic.sizes.padEnd(9)} ${ic.purpose.padEnd(9)} ${type}`);
}

console.log("\n=== 3. 服务器端是否有任何 404（页面加载期间）===");
const bad = requested.filter(([, c]) => c === 404);
if (bad.length) {
  fail++;
  console.log("  发现 404：");
  bad.forEach(([u, c]) => console.log("    " + c + "  " + u));
} else {
  console.log("  PASS  无任何 404（共 " + requested.length + " 个请求）");
}

ws.close(); chrome.kill(); srv.close();
await new Promise((r) => setTimeout(r, 400));
try { fs.rmSync(prof, { recursive: true, force: true }); } catch {}

console.log("\n" + "=".repeat(60));
if (fail === 0) {
  console.log("全部通过：图标均可达且为不透明 RGB，iOS 不会再生成占位图标");
  process.exit(0);
} else {
  console.log(`有 ${fail} 项失败`);
  process.exit(1);
}
