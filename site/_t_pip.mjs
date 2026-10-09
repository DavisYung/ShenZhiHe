/* 独立验证 PIP 关闭后是否真的清空 DOM —— 不依赖 _t_v015.py 的时序假设。
 * 给足等待时间（3 秒），确认站点行为本身正确。
 */
import http from "node:http";
import fs from "node:fs";
import path from "node:path";
import { spawn } from "node:child_process";
import os from "node:os";

const PKG = path.resolve(process.argv[2] || ".");
const FILE = ["神智核.html", "index.html"].find((n) => fs.existsSync(path.join(PKG, n))) || "神智核.html";
const PORT = 8951, CDP_PORT = 9491;
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
const prof = path.join(os.tmpdir(), "sz_pip_" + Date.now());
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

await new Promise((r) => setTimeout(r, 4500));

const results = [];
const check = (n, ok, d = "") => { results.push([n, ok, d]); console.log((ok ? "  PASS  " : "  FAIL  ") + n + (d ? "   " + d : "")); };

// 进入化学区并打开 PIP
await evalJs("location.hash='#/chem/t/1a'");
await new Promise((r) => setTimeout(r, 2500));

const opened = await evalJs(`(function(){
  var pid=Object.keys(PMAP)[0];
  if(!pid) return 'no-pid';
  openPip(pid);
  var el=document.getElementById('pip');
  return el.innerHTML.length;
})()`);
check("PIP 能打开且有内容", typeof opened === "number" && opened > 100, "innerHTML 长度=" + opened);

// 动画全开下关闭 → 立即隐藏、延迟后清空
await evalJs("setAnimMode('full')");
await evalJs("closePip()");
const hiddenNow = await evalJs("!document.getElementById('pip').classList.contains('on')");
check("關閉後立即移除 .on（不再可見）", hiddenNow === true);

// 给足时间（3 秒，远大于实现里的 700ms）
await new Promise((r) => setTimeout(r, 3000));
const cleared = await evalJs("document.getElementById('pip').innerHTML === ''");
check("延遲後 DOM 確實清空（等 3 秒）", cleared === true,
      "innerHTML 長度=" + (await evalJs("document.getElementById('pip').innerHTML.length")));

// 动画关闭模式下关闭 → 立即清空
await evalJs("setAnimMode('off')");
await evalJs("openPip(Object.keys(PMAP)[0])");
await evalJs("closePip()");
await new Promise((r) => setTimeout(r, 600));
const clearedOff = await evalJs("document.getElementById('pip').innerHTML === ''");
check("關閉動畫時立即清空 DOM", clearedOff === true);

ws.close(); chrome.kill(); srv.close();
await new Promise((r) => setTimeout(r, 400));
try { fs.rmSync(prof, { recursive: true, force: true }); } catch {}

const ok = results.filter((r) => r[1]).length;
console.log("\n" + "=".repeat(56));
console.log(`结果: ${ok}/${results.length} 通过`);
if (ok !== results.length) { results.filter((r) => !r[1]).forEach((r) => console.log("  - " + r[0] + " " + r[2])); process.exit(1); }
console.log("PIP 行為正確：站點無 bug，_t_v015.py 的失敗是測試時序問題");
process.exit(0);
