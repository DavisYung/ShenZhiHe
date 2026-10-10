/* 力學分區端到端驗收：力學單元卡 → 10 個課題 → 逐課內容/圖片 → 測驗 → 圖譜串連 */
import http from "node:http";
import fs from "node:fs";
import path from "node:path";
import { spawn } from "node:child_process";
import os from "node:os";

const PKG = path.resolve(process.argv[2] || ".");
const OUT = path.resolve(process.argv[3] || ".");
const FILE = ["神智核.html", "index.html"].find((n) => fs.existsSync(path.join(PKG, n))) || "神智核.html";
const PORT = 8961, CDP_PORT = 9501;
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
const prof = path.join(os.tmpdir(), "sz_mech_" + Date.now());
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

const results = [];
const check = (n, ok, d = "") => { results.push([n, ok, d]); console.log((ok ? "  PASS  " : "  FAIL  ") + n + (d ? "   " + d : "")); };
async function shot(name) {
  const r = await send("Page.captureScreenshot", { format: "png" }, sessionId);
  fs.writeFileSync(path.join(OUT, name), Buffer.from(r.data, "base64"));
}

await new Promise((r) => setTimeout(r, 5000));

// 1. 物理首页应有「熱學」「力學」两张单元卡
await evalJs("location.hash='#/phys/home'");
await new Promise((r) => setTimeout(r, 2800));
let t = await evalJs("document.body.innerText");
const cards = JSON.parse(await evalJs(`JSON.stringify({
  n: document.querySelectorAll('.tcard').length,
  titles: Array.from(document.querySelectorAll('.tcard h3')).map(h=>h.textContent.trim().slice(0,20))
})`));
check("物理首页显示 2 张单元卡", cards.n === 2, JSON.stringify(cards.titles));
check("含「熱學」", t.includes("熱學"));
check("含「力學」", t.includes("力學"));
const mechCard = await evalJs(`(function(){
  var card=Array.from(document.querySelectorAll('.tcard')).find(h=>h.textContent.includes('力學'));
  return card ? card.textContent.replace(/\\s+/g,' ').trim().slice(0,120) : null;
})()`);
check("力學卡显示統計（10 課題）", mechCard && /10\s*課題/.test(mechCard), mechCard);
await shot("m_home.png");

// 2. 力學单元页列出 10 个课题
await evalJs("location.hash='#/phys/unit/mechanics'");
await new Promise((r) => setTimeout(r, 2800));
t = await evalJs("document.body.innerText");
const TOPICS = ["長度、時間與運動描述", "直線運動的線圖與運動方程", "力與牛頓運動定律", "力的合成與分解",
  "力矩與剛體平衡", "功、能量與功率", "動量", "拋體運動", "圓周運動與向心力", "萬有引力"];
const found = TOPICS.filter((x) => t.includes(x));
check("力學单元页列出 10 個課題", found.length === 10, "命中 " + found.length + " 個");
const topicCards = await evalJs("document.querySelectorAll('.tcard').length");
check("10 张课题卡片", topicCards === 10, "卡片=" + topicCards);
await shot("m_unit.png");

// 3. 逐课打开：内容 + 图片无破损
for (const [tid, title] of [["mech1","長度、時間"], ["mech3","力與牛頓"], ["mech6","功、能量"], ["mech10","萬有引力"]]) {
  await evalJs(`location.hash='#/phys/t/${tid}'`);
  await new Promise((r) => setTimeout(r, 2400));
  const txt = await evalJs("document.body.innerText");
  const img = JSON.parse(await evalJs(`JSON.stringify({
    total: document.querySelectorAll('img').length,
    broken: Array.from(document.querySelectorAll('img')).filter(i=>i.complete&&i.naturalWidth===0).length
  })`));
  check(`[${tid}] ${title} 可打开`, txt.includes(title));
  check(`[${tid}] 圖片無破損`, img.broken === 0, `共${img.total} 破損${img.broken}`);
  check(`[${tid}] 無「温」異體字`, !txt.includes("\u6e29"));
}
await shot("m_topic.png");

// 4. 力学单元测验（整分區聚合）
await evalJs("location.hash='#/phys/quiz'");
await new Promise((r) => setTimeout(r, 2400));
t = await evalJs("document.body.innerText");
check("測驗頁含「力學全部」", t.includes("力學全部"));
const started = await evalJs(`(function(){
  var el=Array.from(document.querySelectorAll('.scope')).find(x=>/力學全部/.test(x.textContent));
  if(el){ el.click(); return el.textContent.trim().slice(0,24); } return null;
})()`);
check("能開始力學整區測驗", !!started, started);
await new Promise((r) => setTimeout(r, 2600));
t = await evalJs("document.body.innerText");
const m = t.match(/第 \d+ \/ (\d+) 題/);
check("測驗進入做題", !!m, m ? "共 " + m[1] + " 題" : "");
check("題量為力學 244", m && m[1] === "244", m ? "第1/共" + m[1] : "");

// 5. 化学不受影响 + 进度键隔离
await evalJs("location.hash='#/chem/home'");
await new Promise((r) => setTimeout(r, 2400));
const chemCards = await evalJs("document.querySelectorAll('.tcard').length");
check("化学区仍 12 课题平铺", chemCards === 12, "卡片=" + chemCards);
const keys = await evalJs(`(function(){var o=[];for(var i=0;i<localStorage.length;i++)o.push(localStorage.key(i));return JSON.stringify(o);})()`);
console.log("    localStorage:", keys);

ws.close(); chrome.kill(); srv.close();
await new Promise((r) => setTimeout(r, 400));
try { fs.rmSync(prof, { recursive: true, force: true }); } catch {}

const ok = results.filter((r) => r[1]).length;
console.log("\n" + "=".repeat(60));
console.log(`结果: ${ok}/${results.length} 通过`);
if (ok !== results.length) { results.filter((r) => !r[1]).forEach((r) => console.log("  - " + r[0] + " " + r[2])); process.exit(1); }
console.log("力學分區端到端驗收通過");
process.exit(0);
