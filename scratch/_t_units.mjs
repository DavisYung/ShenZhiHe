/* 验证子分区（单元）导航：物理首页 → 热学单元 → 课题；并确认化学不受影响、进度不丢。 */
import http from "node:http";
import fs from "node:fs";
import path from "node:path";
import { spawn } from "node:child_process";
import os from "node:os";

const PKG = path.resolve(process.argv[2] || ".");
const OUT = path.resolve(process.argv[3] || ".");
const FILE = ["神智核.html", "index.html"].find((n) => fs.existsSync(path.join(PKG, n))) || "神智核.html";
const PORT = 8891, CDP_PORT = 9451;
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
const prof = path.join(os.tmpdir(), "sz_unit_" + Date.now());
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

const results = [];
const check = (n, ok, d = "") => { results.push([n, ok, d]); console.log((ok ? "  PASS  " : "  FAIL  ") + n + (d ? "   " + d : "")); };
async function shot(name) {
  const r = await send("Page.captureScreenshot", { format: "png" }, sessionId);
  fs.writeFileSync(path.join(OUT, name), Buffer.from(r.data, "base64"));
}

await new Promise((r) => setTimeout(r, 5000));

// 1. 物理首页应显示「单元卡片」而不是 5 个课题平铺
await evalJs("location.hash='#/phys/home'");
await new Promise((r) => setTimeout(r, 3000));
let t = await evalJs("document.body.innerText");
check("物理首页显示「熱學」单元卡片", t.includes("熱學"), "");
const cardInfo = JSON.parse(await evalJs(`JSON.stringify({
  cards: document.querySelectorAll('.tcard').length,
  texts: Array.from(document.querySelectorAll('.tcard h3')).map(h=>h.textContent.trim())
})`));
// 单元数动态读取（热学 + 力学 + 未来的分區），断言「卡片数 = 单元数」而非写死 1
const unitCount = await evalJs("((SUB&&SUB.units&&SUB.units.length)||0)");
check("首页只显示单元卡片（卡片数=单元数）",
  cardInfo.cards === unitCount,
  "卡片数=" + cardInfo.cards + " 单元数=" + unitCount + " " + JSON.stringify(cardInfo.texts));
check("单元卡片含统计（5/10 課題、50/80 知識點）",
  /5 課題/.test(t) && /50 知識點/.test(t) && /10 課題/.test(t) && /80 知識點/.test(t), "");
await shot("u_home.png");

// 2. 点单元卡片 → 进入热学页，列出 5 个课题
await evalJs("location.hash='#/phys/unit/thermal'");
await new Promise((r) => setTimeout(r, 2800));
t = await evalJs("document.body.innerText");
const TITLES = ["溫度與溫度計", "內能與比熱容量", "物態的改變", "傳熱方式", "氣體"];
const found = TITLES.filter((x) => t.includes(x));
check("热学单元页列出全部 5 个课题", found.length === 5, found.join(" / "));
check("单元页显示返回首页", t.includes("返回首頁"));
check("单元页有「測驗本分區」", t.includes("測驗本分區"));
const unitCards = JSON.parse(await evalJs("document.querySelectorAll('.tcard').length"));
check("单元页显示 5 张课题卡片", unitCards === 5, "卡片数=" + unitCards);
await shot("u_unit.png");

// 3. 从单元页进课题，再返回
await evalJs("location.hash='#/phys/t/heat3'");
await new Promise((r) => setTimeout(r, 2600));
t = await evalJs("document.body.innerText");
check("从单元进入课题正常（heat3）", t.includes("物態的改變"));
check("课题页返回键可用", t.includes("返回"));

// 4. 测验页按分区分组
await evalJs("location.hash='#/phys/quiz'");
await new Promise((r) => setTimeout(r, 2500));
t = await evalJs("document.body.innerText");
// V0.14.0 起测验页改为「课题卡片 + 勾选」：单元入口是分组头部的 .qgwhole
// 「整區 N 題 →」按钮（旧版的 .scope「熱學全部」已下线）
const unitHead = await evalJs("document.querySelector('.qgroup[data-uid=thermal] .qgt') ? document.querySelector('.qgroup[data-uid=thermal] .qgt').textContent.trim() : ''");
check("测验页有热学分组标题", /熱學/.test(unitHead), unitHead);
check("测验页仍列出各课题", TITLES.filter((x) => t.includes(x)).length === 5);
await shot("u_quiz.png");

// 5. 单元测验真的能开始并抽到题
const started = await evalJs(`(function(){
  var el=document.querySelector('.qgroup[data-uid=thermal] .qgwhole');
  if(el){ el.click(); return el.textContent.trim().slice(0,30); }
  return null;
})()`);
check("能开始热学整区测验", !!started, "点击=" + started);
await new Promise((r) => setTimeout(r, 2500));
t = await evalJs("document.body.innerText");
check("单元测验进入做题（有题号）", /第 \d+ \/ \d+ 題/.test(t), (t.match(/第 \d+ \/ \d+ 題/) || [""])[0]);

// 6. 化学区不受影响（无单元，仍平铺 12 课题）
await evalJs("location.hash='#/chem/home'");
await new Promise((r) => setTimeout(r, 2800));
const chemCards = JSON.parse(await evalJs("document.querySelectorAll('.tcard').length"));
check("化学区仍平铺 12 个课题（不受单元影响）", chemCards === 12, "卡片数=" + chemCards);
t = await evalJs("document.body.innerText");
check("化学首页无单元分组提示", !t.includes("個分區 ·"), "");

// 7. 进度键隔离仍成立
const keys = await evalJs(`(function(){
  var out=[]; for(var i=0;i<localStorage.length;i++){out.push(localStorage.key(i));} return JSON.stringify(out);
})()`);
console.log("    localStorage 键:", keys);

ws.close(); chrome.kill(); srv.close();
await new Promise((r) => setTimeout(r, 400));
try { fs.rmSync(prof, { recursive: true, force: true }); } catch {}

const ok = results.filter((r) => r[1]).length;
console.log("\n" + "=".repeat(62));
console.log(`结果: ${ok}/${results.length} 通过`);
if (ok !== results.length) { results.filter((r) => !r[1]).forEach((r) => console.log("  - " + r[0] + "  " + r[2])); process.exit(1); }
console.log("子分区（单元）功能验证通过");
process.exit(0);
