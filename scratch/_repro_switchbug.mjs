/* 复现并定位「非科目页无法切换科目」的 bug。
 * 逐页点击科目切换按钮，看 SUB 与 hash 是否一致。
 */
import http from "node:http";
import fs from "node:fs";
import path from "node:path";
import { spawn } from "node:child_process";
import os from "node:os";

const PKG = path.resolve(process.argv[2] || ".");
const FILE = ["神智核.html", "index.html"].find((n) => fs.existsSync(path.join(PKG, n))) || "神智核.html";
const PORT = 8911, CDP_PORT = 9471;
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
const prof = path.join(os.tmpdir(), "sz_bug_" + Date.now());
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

// 各页面的 hash 形态
const PAGES = [
  ["#/phys/home", "物理首页"],
  ["#/phys/quiz", "物理测验页"],
  ["#/phys/review", "物理复习页"],
  ["#/phys/graph", "物理知识图谱"],
  ["#/phys/wrong", "物理错题本"],
  ["#/phys/extras", "物理额外资讯"],
  ["#/phys/t/heat1", "物理课题页"],
  ["#/phys/unit/thermal", "物理单元页"],
  ["#/settings", "设置页"],
  ["#/subjects", "科目总览页"],
];

console.log("=== 从各页面点「化學」按钮，看是否真的切过去 ===");
for (const [hash, label] of PAGES) {
  await evalJs(`location.hash='${hash}'`);
  await new Promise((r) => setTimeout(r, 1600));
  const before = await evalJs("(SUB&&SUB.id)||'?'");
  // 点科目栏里的「化學」按钮
  const clicked = await evalJs(`(function(){
    var btns=Array.from(document.querySelectorAll('#subbar button'));
    var b=btns.find(x=>/化學/.test(x.textContent));
    if(b){ b.click(); return true; } return false;
  })()`);
  await new Promise((r) => setTimeout(r, 1800));
  const after = await evalJs("(SUB&&SUB.id)||'?'");
  const h = await evalJs("location.hash");
  const ok = after === "chem";
  console.log(`  ${ok ? "OK  " : "BUG "} ${label.padEnd(12)} hash=${h.padEnd(22)} SUB ${before} -> ${after}${clicked ? "" : " (找不到按鈕!)"}`);
}

ws.close(); chrome.kill(); srv.close();
await new Promise((r) => setTimeout(r, 400));
try { fs.rmSync(prof, { recursive: true, force: true }); } catch {}
process.exit(0);
