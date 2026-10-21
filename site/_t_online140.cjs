/* 線上驗收：V0.14.0 測驗頁課題卡片 + 勾選合成測驗 */
const fs = require("fs"); const PORT = 9333;
const sleep = ms => new Promise(r => setTimeout(r, ms));
(async () => {
  let list = null;
  for (let i = 0; i < 60; i++) { try { const r = await fetch(`http://127.0.0.1:${PORT}/json/list`); list = await r.json(); if (list && list.some(t => t.type === "page")) break; } catch (e) {} await sleep(300); }
  const ws = new WebSocket(list.find(t => t.type === "page").webSocketDebuggerUrl);
  let id = 0; const pending = new Map(); const logs = [];
  ws.onmessage = ev => { const m = JSON.parse(ev.data); if (m.id && pending.has(m.id)) { pending.get(m.id)(m); pending.delete(m.id); } if (m.method === "Runtime.exceptionThrown") logs.push("EX:" + (m.params.exceptionDetails.exception?.description || "").split("\n")[0]); };
  const send = (m, p = {}) => new Promise(res => { const i = ++id; pending.set(i, res); ws.send(JSON.stringify({ id: i, method: m, params: p })); });
  await new Promise(r => ws.onopen = r);
  await send("Page.enable"); await send("Runtime.enable"); await send("Network.enable");
  await send("Network.setCacheDisabled", { cacheDisabled: true });
  const ev = async e => { const r = await send("Runtime.evaluate", { expression: e, returnByValue: true, awaitPromise: true }); if (r.result?.exceptionDetails) return "EXC:" + (r.result.exceptionDetails.exception?.description || ""); return r.result?.result?.value; };
  const S = "https://nzgjsmy.github.io/ShenZhiHe/";
  let pass = 0, fail = 0; const ok = (c, m) => { if (c) { pass++; console.log("  PASS " + m); } else { fail++; console.log("  FAIL " + m); } };
  await send("Emulation.setDeviceMetricsOverride", { width: 390, height: 844, deviceScaleFactor: 2, mobile: true });
  await send("Page.navigate", { url: S + "#/phys/quiz" }); await sleep(12000);
  console.log("[线上 · V0.14.0 课题卡片 + 勾选]");
  ok(await ev("document.querySelector('.fver').textContent.trim()") === "V0.14.0", "页脚 V0.14.0");
  ok(await ev("document.querySelectorAll('.qpick').length") === 38, `38 张卡片（${await ev("document.querySelectorAll('.qpick').length")}）`);
  ok(await ev("!!document.querySelector('.qpick .qpick-go')") === true, "卡片有「單獨測驗」按钮");
  ok(await ev("!!document.querySelector('.qpick .qpick-pbar')") === true, "卡片有掌握度进度条");
  ok(await ev("document.querySelectorAll('.qpick input[type=checkbox]').length") === 38, "每卡一个勾选框");
  await ev(`(()=>{const b=[...document.querySelectorAll('.qpick input')];b[0].checked=true;b[1].checked=true;b[4].checked=true;quizPickChanged();})()`); await sleep(600);
  const st = await ev("document.getElementById('pickbar-t')?.textContent||''");
  console.log("  浮条:", st);
  ok(st.includes('已選 3 個課題'), "浮条显示已选 3 个");
  ok(await ev("document.querySelectorAll('.qpick.on').length") === 3, "3 张卡片选中态");
  await ev("document.getElementById('pickbar').querySelector('.pickbar-go').click()"); await sleep(5000);
  ok((await ev("location.hash")).includes('/run'), "进入答题页");
  const pt = await ev("JSON.stringify([...new Set(QZ.pool.map(q=>q.topic))])");
  ok(JSON.parse(pt).length === 3, `题库 3 个课题（${pt}）`);
  const s = await send("Page.captureScreenshot", { format: "png" });
  fs.writeFileSync("_t_online140.png", Buffer.from(s.result.data, "base64"));
  ok(logs.length === 0, `零异常（${logs.length}）`);
  console.log(`\n结果：通过 ${pass}，失败 ${fail}`);
  process.exit(fail ? 1 : 0);
})().catch(e => { console.log("FATAL", e.message); process.exit(1); });
