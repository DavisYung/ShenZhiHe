/* 直接截「神智核.html」（构建产物），验证物理分区渲染 */
import http from "node:http";
import fs from "node:fs";
import path from "node:path";
import { spawn } from "node:child_process";
import os from "node:os";

const PKG = path.resolve(process.argv[2] || ".");
const OUT = path.resolve(process.argv[3] || ".");
const FILE = process.argv[4] || "神智核.html";
const PORT = 8841;
const CDP_PORT = 9401;
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
  } else { res.writeHead(404); res.end("nf: " + rel); }
});
await new Promise((r) => srv.listen(PORT, "127.0.0.1", r));
const base = `http://127.0.0.1:${PORT}/${encodeURIComponent(FILE)}`;

const prof = path.join(os.tmpdir(), "sz_phys2_" + Date.now());
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
  if (r.exceptionDetails) throw new Error(r.exceptionDetails.text); return r.result.value; };

async function shot(name) {
  const r = await send("Page.captureScreenshot", { format: "png" }, sessionId);
  fs.writeFileSync(path.join(OUT, name), Buffer.from(r.data, "base64"));
  console.log("  截图 " + name);
}

await new Promise((r) => setTimeout(r, 4000));
const title = await evalJs("document.title");
console.log("页面标题:", title);

// 科目总览
await evalJs("location.hash='#/subjects'");
await new Promise((r) => setTimeout(r, 2200));
await shot("p_subjects.png");
let t = await evalJs("document.body.innerText");
console.log("\n--- 科目页 ---");
console.log("  含「物理」:", t.includes("物理"));
console.log("  含「化學」:", t.includes("化學"));

// 物理课题列表
await evalJs("location.hash='#/phys/home'");
await new Promise((r) => setTimeout(r, 2500));
await shot("p_home.png");
t = await evalJs("document.body.innerText");
console.log("\n--- 物理首页 ---");
console.log("  含「溫度與溫度計」:", t.includes("溫度與溫度計"));
console.log("  含「內容準備中」:", t.includes("準備中"));
console.log("  残留异体「温」:", t.includes("\u6e29"));

// 课题内容
await evalJs("location.hash='#/phys/t/heat1'");
await new Promise((r) => setTimeout(r, 3500));
await shot("p_topic.png");
t = await evalJs("document.body.innerText");
console.log("\n--- heat1 课题页 ---");
console.log("  含「溫度與溫標」:", t.includes("溫度與溫標"));
console.log("  含「冷熱程度」:", t.includes("冷熱程度"));
console.log("  残留异体「温」:", t.includes("\u6e29"));
const img = await evalJs(`JSON.stringify({
  total: document.querySelectorAll('img').length,
  loaded: Array.from(document.querySelectorAll('img')).filter(i=>i.complete&&i.naturalWidth>0).length,
  broken: Array.from(document.querySelectorAll('img')).filter(i=>i.complete&&i.naturalWidth===0).length
})`);
console.log("  图片:", img);

ws.close(); chrome.kill(); srv.close();
await new Promise((r) => setTimeout(r, 400));
try { fs.rmSync(prof, { recursive: true, force: true }); } catch {}
process.exit(0);
