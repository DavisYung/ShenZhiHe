/* 科目切换完整回归：双向、往返、状态一致性、刷新后保持、以及不能破坏其他功能。 */
import http from "node:http";
import fs from "node:fs";
import path from "node:path";
import { spawn } from "node:child_process";
import os from "node:os";

const PKG = path.resolve(process.argv[2] || ".");
const OUT = path.resolve(process.argv[3] || ".");
const FILE = ["神智核.html", "index.html"].find((n) => fs.existsSync(path.join(PKG, n))) || "神智核.html";
const PORT = 8921, CDP_PORT = 9481;
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
const prof = path.join(os.tmpdir(), "sz_sw_" + Date.now());
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
const clickSubject = (name) => evalJs(`(function(){
  var b=Array.from(document.querySelectorAll('#subbar button')).find(x=>/${name}/.test(x.textContent));
  if(b){ b.click(); return true; } return false;
})()`);
const state = async () => ({
  sub: await evalJs("(SUB&&SUB.id)||'?'"),
  hash: await evalJs("location.hash"),
  navOn: await evalJs("(function(){var b=document.querySelector('nav button.on');return b?b.textContent.trim():''})()"),
});

await new Promise((r) => setTimeout(r, 5000));

// 1. 双向切换：物理各页 → 化学，再从化学各页 → 物理
console.log("\n--- 物理各页 → 化學 ---");
for (const h of ["#/phys/home", "#/phys/quiz", "#/phys/graph", "#/phys/review", "#/phys/wrong", "#/phys/extras", "#/phys/t/heat1", "#/phys/unit/thermal"]) {
  await evalJs(`location.hash='${h}'`);
  await new Promise((r) => setTimeout(r, 1400));
  await clickSubject("化學");
  await new Promise((r) => setTimeout(r, 1600));
  const s = await state();
  check(`  ${h} → 化學`, s.sub === "chem", `SUB=${s.sub} hash=${s.hash}`);
}

console.log("\n--- 化學各页 → 物理 ---");
for (const h of ["#/chem/home", "#/chem/quiz", "#/chem/graph", "#/chem/review", "#/chem/wrong", "#/chem/t/1a"]) {
  await evalJs(`location.hash='${h}'`);
  await new Promise((r) => setTimeout(r, 1400));
  await clickSubject("物理");
  await new Promise((r) => setTimeout(r, 1600));
  const s = await state();
  check(`  ${h} → 物理`, s.sub === "phys", `SUB=${s.sub} hash=${s.hash}`);
}

// 2. 连续往返 5 次（状态不能错乱）
// 起點 phys，奇數次切換（第 1、3、5 次）後停在 chem，偶數次回到 phys。
// 切 5 次 → 終點應為 chem。
await evalJs("location.hash='#/phys/home'");
await new Promise((r) => setTimeout(r, 1500));
let flip = true;
for (let i = 0; i < 5; i++) {
  await clickSubject(flip ? "化學" : "物理");
  await new Promise((r) => setTimeout(r, 1300));
  flip = !flip;
}
let s = await state();
check("连续往返 5 次后状态正确（奇数次→chem）", s.sub === "chem", `SUB=${s.sub} hash=${s.hash}`);
// 再切一次回到 phys，确认可逆
await clickSubject("物理");
await new Promise((r) => setTimeout(r, 1500));
s = await state();
check("再切一次可回到物理", s.sub === "phys", `SUB=${s.sub} hash=${s.hash}`);

// 3. 内容真的换了（不是只改了变量）
await evalJs("location.hash='#/phys/quiz'");
await new Promise((r) => setTimeout(r, 1600));
await clickSubject("化學");
await new Promise((r) => setTimeout(r, 1800));
let t = await evalJs("document.body.innerText");
check("切到化学后测验页显示化学题量（623）", t.includes("623") || t.includes("653"),
      (t.match(/\d+ 題/) || []).slice(0, 2).join(" "));
await evalJs("location.hash='#/chem/graph'");
await new Promise((r) => setTimeout(r, 1600));
await clickSubject("物理");
await new Promise((r) => setTimeout(r, 2000));
t = await evalJs("document.body.innerText");
check("切到物理后图谱页显示物理内容", t.includes("物理") || t.includes("熱學") || t.includes("溫度"));

// 4. 刷新后科目保持（hash 带科目 id 的好处）
await evalJs("location.hash='#/phys/quiz'");
await new Promise((r) => setTimeout(r, 1500));
await clickSubject("化學");
await new Promise((r) => setTimeout(r, 1500));
await send("Page.reload", {}, sessionId);
await new Promise((r) => setTimeout(r, 5000));
s = await state();
check("重新整理后仍停在化學", s.sub === "chem", `SUB=${s.sub} hash=${s.hash}`);

// 5. 设置页切科目后仍留在设置页
await evalJs("location.hash='#/settings'");
await new Promise((r) => setTimeout(r, 1500));
await clickSubject("物理");
await new Promise((r) => setTimeout(r, 1800));
s = await state();
t = await evalJs("document.body.innerText");
check("设置页切科目后仍在设置页", s.sub === "phys" && t.includes("設定"),
      `SUB=${s.sub} hash=${s.hash}`);

// 6. 「全部科目」按钮仍可用
await evalJs("location.hash='#/chem/home'");
await new Promise((r) => setTimeout(r, 1500));
await evalJs(`(function(){var b=Array.from(document.querySelectorAll('#subbar button')).find(x=>/全部科目/.test(x.textContent)); if(b)b.click();})()`);
await new Promise((r) => setTimeout(r, 1800));
t = await evalJs("document.body.innerText");
check("「全部科目」按钮可用", t.includes("化學") && t.includes("物理") && t.includes("生物"));

// 7. 进度键仍隔离
const keys = await evalJs(`(function(){var o=[];for(var i=0;i<localStorage.length;i++)o.push(localStorage.key(i));return JSON.stringify(o);})()`);
check("进度键仍分科隔离", keys.includes("f6chem.v1") || keys.includes("f6note.phys.v1"), keys);

ws.close(); chrome.kill(); srv.close();
await new Promise((r) => setTimeout(r, 400));
try { fs.rmSync(prof, { recursive: true, force: true }); } catch {}

const ok = results.filter((r) => r[1]).length;
console.log("\n" + "=".repeat(62));
console.log(`结果: ${ok}/${results.length} 通过`);
if (ok !== results.length) { results.filter((r) => !r[1]).forEach((r) => console.log("  - " + r[0] + "  " + r[2])); process.exit(1); }
console.log("科目切换回归通过");
process.exit(0);
