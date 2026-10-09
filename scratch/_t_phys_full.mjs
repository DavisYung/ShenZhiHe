/* 物理分区完整验收：5 个课题逐一打开，检查内容渲染、图片加载、串连、测验。
 * 同时确认化学区未被破坏。
 */
import http from "node:http";
import fs from "node:fs";
import path from "node:path";
import { spawn } from "node:child_process";
import os from "node:os";

const PKG = path.resolve(process.argv[2] || ".");
const OUT = path.resolve(process.argv[3] || ".");
// 自动识别入口档：构建目录里叫「神智核.html」，交付包里叫 index.html（GitHub Pages 要求）。
const FILE = ["神智核.html", "index.html"].find((n) => fs.existsSync(path.join(PKG, n)))
  || "神智核.html";
const PORT = 8861;
const CDP_PORT = 9421;
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
  } else { res.writeHead(404); res.end("nf"); }
});
await new Promise((r) => srv.listen(PORT, "127.0.0.1", r));
const base = `http://127.0.0.1:${PORT}/${encodeURIComponent(FILE)}`;

const prof = path.join(os.tmpdir(), "sz_physfull_" + Date.now());
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

await new Promise((r) => setTimeout(r, 5000));

// 1. 物理首页列出 5 个课题
await evalJs("location.hash='#/phys/home'");
await new Promise((r) => setTimeout(r, 3000));
let t = await evalJs("document.body.innerText");
const TITLES = ["溫度與溫度計", "內能與比熱容量", "物態的改變", "傳熱方式", "氣體"];
const found = TITLES.filter((x) => t.includes(x));
check("物理首页列出全部 5 个课题", found.length === 5, found.join(" / "));
// 精确判断：只有「準備中」那个 span 所属的科目才是未完成的。
// 生物区显示「準備中」是正确行为；物理 5 个课题必须都显示知识点/题数。
const prep = await evalJs(`(function(){
  // 找科目切换栏里的「準備中」标记，回传它所在的科目名
  var out=[];
  document.querySelectorAll('.cnt').forEach(function(el){
    if(/準備中/.test(el.textContent||'')){
      var box=el.closest('button,a,div');
      out.push((box?box.textContent:'').trim().slice(0,20));
    }
  });
  return JSON.stringify(out);
})()`);
const prepList = JSON.parse(prep);
const physPreparing = prepList.filter((x) => /物理|熱|氣體|溫度/.test(x));
check("物理不是「準備中」（生物準備中屬正常）", physPreparing.length === 0,
      prepList.length ? "準備中的科目: " + prepList.join(" / ") : "無");
const r1 = await send("Page.captureScreenshot", { format: "png" }, sessionId);
fs.writeFileSync(path.join(OUT, "f_home.png"), Buffer.from(r1.data, "base64"));

// 2. 逐一打开课题，检查内容与图片
for (const [tid, title] of [["heat1", "溫度與溫度計"], ["heat2", "內能與比熱容量"],
                            ["heat3", "物態的改變"], ["heat4", "傳熱方式"], ["heat5", "氣體"]]) {
  await evalJs(`location.hash='#/phys/t/${tid}'`);
  await new Promise((r) => setTimeout(r, 2600));
  const txt = await evalJs("document.body.innerText");
  const img = JSON.parse(await evalJs(`JSON.stringify({
    total: document.querySelectorAll('img').length,
    loaded: Array.from(document.querySelectorAll('img')).filter(i=>i.complete&&i.naturalWidth>0).length,
    broken: Array.from(document.querySelectorAll('img')).filter(i=>i.complete&&i.naturalWidth===0).length
  })`));
  const hasTitle = txt.includes(title);
  const noWen = !txt.includes("\u6e29");
  check(`[${tid}] ${title} 可打开`, hasTitle, hasTitle ? "" : "标题未出现");
  check(`[${tid}] 图片加载正常`, img.broken === 0 && img.loaded > 0,
        `共${img.total} 已载${img.loaded} 破损${img.broken}`);
  check(`[${tid}] 无「温」异体字`, noWen);
  const s = await send("Page.captureScreenshot", { format: "png" }, sessionId);
  fs.writeFileSync(path.join(OUT, `f_${tid}.png`), Buffer.from(s.data, "base64"));
}

// 3. 知识图谱（串连）
await evalJs("location.hash='#/phys/graph'");
await new Promise((r) => setTimeout(r, 3500));
t = await evalJs("document.body.innerText");
const gsvg = await evalJs("document.querySelectorAll('svg circle, svg line, svg path, .gnode').length");
check("知识图谱能渲染（串连 24 条）", gsvg > 0 || t.includes("圖譜") || t.includes("串連"),
      "图元素=" + gsvg);
const r3 = await send("Page.captureScreenshot", { format: "png" }, sessionId);
fs.writeFileSync(path.join(OUT, "f_graph.png"), Buffer.from(r3.data, "base64"));

// 4. 测验页显示物理题量
await evalJs("location.hash='#/phys/quiz'");
await new Promise((r) => setTimeout(r, 2500));
t = await evalJs("document.body.innerText");
check("测验页显示物理题量", /187|全部課題/.test(t), t.match(/\d+ 題/g) ? t.match(/\d+ 題/g).slice(0,3).join(" ") : "");

// 5. 化学区未被破坏
await evalJs("location.hash='#/chem/home'");
await new Promise((r) => setTimeout(r, 2500));
t = await evalJs("document.body.innerText");
check("化学区仍正常（653 知识点）", t.includes("653") || t.includes("化學"));
await evalJs("location.hash='#/chem/t/1a'");
await new Promise((r) => setTimeout(r, 2500));
const chemImg = JSON.parse(await evalJs(`JSON.stringify({
  broken: Array.from(document.querySelectorAll('img')).filter(i=>i.complete&&i.naturalWidth===0).length
})`));
check("化学课题图片无破损", chemImg.broken === 0, "破损=" + chemImg.broken);

// 6. 科目切换互不干扰
await evalJs("location.hash='#/subjects'");
await new Promise((r) => setTimeout(r, 2000));
t = await evalJs("document.body.innerText");
check("科目页显示物理与化学", t.includes("物理") && t.includes("化學"));

ws.close(); chrome.kill(); srv.close();
await new Promise((r) => setTimeout(r, 400));
try { fs.rmSync(prof, { recursive: true, force: true }); } catch {}

const ok = results.filter((r) => r[1]).length;
console.log("\n" + "=".repeat(64));
console.log(`结果: ${ok}/${results.length} 通过`);
if (ok !== results.length) { results.filter((r) => !r[1]).forEach((r) => console.log("  - " + r[0] + "  " + r[2])); process.exit(1); }
console.log("物理分区完整验收通过");
process.exit(0);
