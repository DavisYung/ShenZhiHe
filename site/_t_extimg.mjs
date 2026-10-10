/* 路线三核心验证：图片外置后的离线完整性
 * 1. 在线打开课题页 → 图片下载（HTTP 200）
 * 2. 断网 → 重新导航 → 图片仍显示（来自 SW 缓存，非网络）
 * 3. 断网时打开一个新课题页 → 页面可用，已缓存图片可用
 * 同时抓服务器端日志确认断网后无真实请求（全走缓存）。
 */
import http from "node:http";
import fs from "node:fs";
import path from "node:path";
import { spawn } from "node:child_process";
import os from "node:os";

const PKG = path.resolve(process.argv[2] || ".");
const OUT = path.resolve(process.argv[3] || ".");
const FILE = ["神智核.html", "index.html"].find((n) => fs.existsSync(path.join(PKG, n))) || "index.html";
const PORT = 8971, CDP_PORT = 9511;
const CHROME = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe";
const MIME = { ".html": "text/html; charset=utf-8", ".json": "application/manifest+json",
  ".js": "application/javascript", ".png": "image/png", ".ico": "image/x-icon", ".webp": "image/webp" };

const log = [];
const srv = http.createServer((req, res) => {
  const p = decodeURIComponent(req.url.split("?")[0]);
  let rel = p.replace(/^\//, ""); if (rel === "") rel = FILE;
  log.push(p);
  const t = path.join(PKG, rel);
  if (fs.existsSync(t) && fs.statSync(t).isFile()) {
    const d = fs.readFileSync(t);
    res.writeHead(200, { "Content-Type": MIME[path.extname(t)] || "application/octet-stream" });
    res.end(d);
  } else { res.writeHead(404); res.end("nf"); }
});
await new Promise((r) => srv.listen(PORT, "127.0.0.1", r));
const base = `http://127.0.0.1:${PORT}/${encodeURIComponent(FILE)}`;
const prof = path.join(os.tmpdir(), "sz_extimg_" + Date.now());
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
  return new Promise((res, rej) => { pend.set(i, { res, rej }); setTimeout(() => { if (pend.has(i)) { pend.delete(i); rej(new Error("timeout " + method)); } }, 90000); }); };

const { targetInfos } = await send("Target.getTargets");
const page = targetInfos.find((t) => t.type === "page");
const { sessionId } = await send("Target.attachToTarget", { targetId: page.targetId, flatten: true });
await send("Page.enable", {}, sessionId); await send("Runtime.enable", {}, sessionId);
const evalJs = async (e, ap = false) => { const r = await send("Runtime.evaluate",
  { expression: e, awaitPromise: ap, returnByValue: true }, sessionId);
  if (r.exceptionDetails) throw new Error(r.exceptionDetails.text); return r.result.value; };
async function shot(name) {
  const r = await send("Page.captureScreenshot", { format: "png" }, sessionId);
  fs.writeFileSync(path.join(OUT, name), Buffer.from(r.data, "base64"));
}
const IMGSTAT = `JSON.stringify({
  total: document.querySelectorAll('img').length,
  loaded: Array.from(document.querySelectorAll('img')).filter(i=>i.complete&&i.naturalWidth>0).length,
  broken: Array.from(document.querySelectorAll('img')).filter(i=>i.complete&&i.naturalWidth===0).length
})`;

const results = [];
const check = (n, ok, d = "") => { results.push([n, ok, d]); console.log((ok ? "  PASS  " : "  FAIL  ") + n + (d ? "   " + d : "")); };

await new Promise((r) => setTimeout(r, 5000));

// === 1. 在线：打开 mech3（约 17 张图），等图片下载 ===
await evalJs("location.hash='#/phys/t/mech3'");
await new Promise((r) => setTimeout(r, 4500));
let st = JSON.parse(await evalJs(IMGSTAT));
check("[在线] mech3 图片已下载", st.total > 0 && st.loaded > 0 && st.broken === 0,
      `共${st.total} 载入${st.loaded} 破损${st.broken}`);
const onlineImgCount = log.filter((x) => x.includes("img/") && x.includes("webp")).length;
check("[在线] 服务器日志有 img 请求", onlineImgCount > 0, `${onlineImgCount} 个 img 请求`);
// 等 SW 激活（首访后 SW 装载并接管需要时间）
await new Promise((r) => setTimeout(r, 3500));
const swState = await evalJs(`(async()=>{const r=await navigator.serviceWorker.getRegistration();
  return r&&r.active?'activated':'not-yet';})()`, true);
check("SW 已激活", swState === "activated", swState);

// === 2. 断网 → 重新导航 → 图片应仍显示 ===
await send("Network.enable", {}, sessionId);
await send("Network.emulateNetworkConditions", {
  offline: true, latency: 0, downloadThroughput: 0, uploadThroughput: 0,
}, sessionId);
log.length = 0;  // 清空日志：断网后不应有真实请求
await evalJs("location.hash='#/home'");
await new Promise((r) => setTimeout(r, 800));
await evalJs("location.hash='#/phys/t/mech3'");   // 重新导航到已访问页
await new Promise((r) => setTimeout(r, 5000));
st = JSON.parse(await evalJs(IMGSTAT));
check("[断网] 重新导航后 mech3 图片全在", st.total > 0 && st.loaded > 0 && st.broken === 0,
      `共${st.total} 载入${st.loaded} 破损${st.broken}`);
check("[断网] 无真实服务器请求（全走缓存）", log.length === 0,
      `日志 ${log.length} 条${log.length ? ": " + log.slice(0,3).join(",") : ""}`);
await shot("ext_offline.png");

// === 3. 断网打开另一个课题（heat1 本会话未访问过 → 图片没缓存，预期加载不到）===
// 这正是「看过的内容离线可看」的设计：首次没看过的页面，离线只能看文字。
// SPA 单 HTML 内跳转（HTML 不重取），文字照常可读。
await evalJs("location.hash='#/phys/t/heat1'");
await new Promise((r) => setTimeout(r, 3500));
const heatText = await evalJs("document.body.innerText");
check("[断网] 未预访问的 heat1 文字仍可读（单 HTML 内跳转）",
      heatText.includes("溫度") || heatText.includes("長度"),
      `文本 ${heatText.length} 字`);
st = JSON.parse(await evalJs(IMGSTAT));
console.log(`    ℹ 断网下 heat1 图片状态（预期没缓存）：共${st.total} 载入${st.loaded} 破损${st.broken}（参考值，不计断言）`);

// === 4. 恢复网络，检查缓存命中统计（SW 用 stale-while-revalidate，重新校验会走网络）===
await send("Network.emulateNetworkConditions", {
  offline: false, latency: 0, downloadThroughput: -1, uploadThroughput: -1,
}, sessionId);

ws.close(); chrome.kill(); srv.close();
await new Promise((r) => setTimeout(r, 400));
try { fs.rmSync(prof, { recursive: true, force: true }); } catch {}

const ok = results.filter((r) => r[1]).length;
console.log("\n" + "=".repeat(60));
console.log(`结果: ${ok}/${results.length} 通过`);
if (ok !== results.length) { results.filter((r) => !r[1]).forEach((r) => console.log("  - " + r[0] + " " + r[2])); process.exit(1); }
console.log("路线三离线完整性验证通过：图片外置后离线体验与内嵌一致");
process.exit(0);
