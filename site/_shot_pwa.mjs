/* 截图：PWA 引导在设置页与首次进站的呈现效果 */
import http from "node:http";
import fs from "node:fs";
import path from "node:path";
import { spawn } from "node:child_process";
import os from "node:os";

const PKG = path.resolve(process.argv[2] || ".");
const OUT = path.resolve(process.argv[3] || ".");
const REPO = "shenzhine";
const PORT = 8781;
const CDP_PORT = 9351;
const CHROME = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe";

const MIME = { ".html": "text/html; charset=utf-8", ".json": "application/manifest+json",
  ".js": "application/javascript", ".png": "image/png", ".ico": "image/x-icon" };

const srv = http.createServer((req, res) => {
  const p = decodeURIComponent(req.url.split("?")[0]);
  const prefix = "/" + REPO + "/";
  let rel = p.startsWith(prefix) ? p.slice(prefix.length) : (p === "/" + REPO ? "index.html" : null);
  if (rel === "" || rel === null) rel = rel === null ? null : "index.html";
  if (rel === null) { res.writeHead(404); res.end(); return; }
  const t = path.join(PKG, rel);
  if (fs.existsSync(t) && fs.statSync(t).isFile()) {
    const d = fs.readFileSync(t);
    res.writeHead(200, { "Content-Type": MIME[path.extname(t)] || "application/octet-stream" });
    res.end(d);
  } else { res.writeHead(404); res.end(); }
});
await new Promise((r) => srv.listen(PORT, "127.0.0.1", r));

const base = `http://127.0.0.1:${PORT}/${REPO}/`;
const prof = path.join(os.tmpdir(), "sz_shot_" + Date.now());
fs.mkdirSync(prof, { recursive: true });

const chrome = spawn(CHROME, [
  "--headless=new", "--disable-gpu", "--no-sandbox",
  `--remote-debugging-port=${CDP_PORT}`, `--user-data-dir=${prof}`,
  "--no-first-run", "--no-default-browser-check", "--window-size=390,844",
  "--hide-scrollbars", base,
], { stdio: "ignore" });

async function wsUrl() {
  for (let i = 0; i < 60; i++) {
    try { const r = await fetch(`http://127.0.0.1:${CDP_PORT}/json/version`);
      const j = await r.json(); if (j.webSocketDebuggerUrl) return j.webSocketDebuggerUrl; } catch {}
    await new Promise((r) => setTimeout(r, 500));
  }
  return null;
}

const u = await wsUrl();
const ws = new WebSocket(u);
await new Promise((res, rej) => { ws.addEventListener("open", res, { once: true }); ws.addEventListener("error", rej, { once: true }); });

let id = 0; const pend = new Map();
ws.addEventListener("message", (ev) => {
  const m = JSON.parse(ev.data);
  if (m.id && pend.has(m.id)) { const p = pend.get(m.id); pend.delete(m.id);
    m.error ? p.rej(new Error(JSON.stringify(m.error))) : p.res(m.result); }
});
const send = (method, params = {}, sid) => {
  const i = ++id; const pl = { id: i, method, params }; if (sid) pl.sessionId = sid;
  ws.send(JSON.stringify(pl));
  return new Promise((res, rej) => { pend.set(i, { res, rej }); setTimeout(() => { if (pend.has(i)) { pend.delete(i); rej(new Error("timeout " + method)); } }, 60000); });
};

const { targetInfos } = await send("Target.getTargets");
const page = targetInfos.find((t) => t.type === "page");
const { sessionId } = await send("Target.attachToTarget", { targetId: page.targetId, flatten: true });
await send("Page.enable", {}, sessionId);
await send("Runtime.enable", {}, sessionId);

const evalJs = async (expr, awaitPromise = false) => {
  const r = await send("Runtime.evaluate", { expression: expr, awaitPromise, returnByValue: true }, sessionId);
  if (r.exceptionDetails) throw new Error(r.exceptionDetails.text);
  return r.result.value;
};

async function shot(name) {
  const r = await send("Page.captureScreenshot", { format: "png", captureBeyondViewport: false }, sessionId);
  fs.writeFileSync(path.join(OUT, name), Buffer.from(r.data, "base64"));
  console.log("  已截图 " + name);
}

// 1. 首次进站（等温和提示出现，4 秒延时）
await new Promise((r) => setTimeout(r, 7000));
await shot("shot_hint.png");

// 2. 设置页的 PWA 引导
await evalJs("location.hash='#/settings'");
await new Promise((r) => setTimeout(r, 2500));
await shot("shot_settings.png");

ws.close(); chrome.kill(); srv.close();
await new Promise((r) => setTimeout(r, 400));
try { fs.rmSync(prof, { recursive: true, force: true }); } catch {}
console.log("完成");
process.exit(0);
