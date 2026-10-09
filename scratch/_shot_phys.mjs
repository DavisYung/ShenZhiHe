/* 截图物理分区，确认内容渲染正常（公式、表格、原图、用字） */
import http from "node:http";
import fs from "node:fs";
import path from "node:path";
import { spawn } from "node:child_process";
import os from "node:os";

const PKG = path.resolve(process.argv[2] || ".");
const OUT = path.resolve(process.argv[3] || ".");
const REPO = "shenzhine";
const PORT = 8831;
const CDP_PORT = 9391;
const CHROME = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe";
const MIME = { ".html": "text/html; charset=utf-8", ".json": "application/manifest+json",
  ".js": "application/javascript", ".png": "image/png", ".ico": "image/x-icon", ".webp": "image/webp" };

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

const prof = path.join(os.tmpdir(), "sz_phys_" + Date.now());
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

await new Promise((r) => setTimeout(r, 3500));

// 1. 科目总览（应能看到物理分区）
await evalJs("location.hash='#/subjects'");
await new Promise((r) => setTimeout(r, 2000));
await shot("phys_subjects.png");
const subjText = await evalJs("document.body.innerText");
console.log("\n--- 科目页是否含物理 ---");
console.log("  含「物理」:", subjText.includes("物理"));
console.log("  含「熱學」或課名:", subjText.includes("溫度") || subjText.includes("熱"));

// 2. 物理课题列表
await evalJs("location.hash='#/phys/home'");
await new Promise((r) => setTimeout(r, 2500));
await shot("phys_home.png");
const homeText = await evalJs("document.body.innerText");
console.log("\n--- 物理首页 ---");
console.log("  含 heat1 标题:", homeText.includes("溫度與溫度計"));
console.log("  含「內容準備中」:", homeText.includes("準備中") || homeText.includes("准备中"));

// 3. 打开知识点，检查原图与公式
await evalJs("location.hash='#/phys/t/heat1'");
await new Promise((r) => setTimeout(r, 3000));
await shot("phys_topic.png");
const topicText = await evalJs("document.body.innerText");
console.log("\n--- heat1 课题页 ---");
console.log("  含「溫度」:", topicText.includes("溫度"));
console.log("  残留异体「温」(U+6E29):", topicText.includes("\u6e29"));
const imgInfo = await evalJs(`JSON.stringify({
  total: document.querySelectorAll('img').length,
  loaded: Array.from(document.querySelectorAll('img')).filter(i=>i.complete&&i.naturalWidth>0).length,
  broken: Array.from(document.querySelectorAll('img')).filter(i=>i.complete&&i.naturalWidth===0).length
})`);
console.log("  图片:", imgInfo);

ws.close(); chrome.kill(); srv.close();
await new Promise((r) => setTimeout(r, 400));
try { fs.rmSync(prof, { recursive: true, force: true }); } catch {}
process.exit(0);
