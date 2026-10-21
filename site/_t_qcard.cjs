/* 測驗頁課題卡片 + 勾選合成測驗 回歸測試
   對應改版：課題列表由「一行小標籤」改為「卡片」，並加勾選功能。
   用法：先起本地 HTTP（_srv_fm.py :8791），Chrome 帶 --remote-debugging-port=9333，再 node _t_qcard.cjs */
const fs = require("fs");
const PORT = 9333;
const sleep = ms => new Promise(r => setTimeout(r, ms));
(async () => {
  let list = null;
  for (let i = 0; i < 60; i++) {
    try { const r = await fetch(`http://127.0.0.1:${PORT}/json/list`); list = await r.json(); if (list && list.some(t => t.type === "page")) break; } catch (e) {}
    await sleep(300);
  }
  const ws = new WebSocket(list.find(t => t.type === "page").webSocketDebuggerUrl);
  let id = 0; const pending = new Map(); const logs = [];
  ws.onmessage = ev => {
    const m = JSON.parse(ev.data);
    if (m.id && pending.has(m.id)) { pending.get(m.id)(m); pending.delete(m.id); }
    if (m.method === "Runtime.exceptionThrown") logs.push("EX:" + (m.params.exceptionDetails.exception?.description || "").split("\n")[0]);
  };
  const send = (m, p = {}) => new Promise(res => { const i = ++id; pending.set(i, res); ws.send(JSON.stringify({ id: i, method: m, params: p })); });
  await new Promise(r => ws.onopen = r);
  await send("Page.enable"); await send("Runtime.enable"); await send("Network.enable");
  await send("Network.setCacheDisabled", { cacheDisabled: true });
  const ev = async e => {
    const r = await send("Runtime.evaluate", { expression: e, returnByValue: true, awaitPromise: true });
    if (r.result?.exceptionDetails) return "EXC:" + (r.result.exceptionDetails.exception?.description || "");
    return r.result?.result?.value;
  };
  const B = "http://127.0.0.1:8791/%E7%A5%9E%E6%99%BA%E6%A0%B8.html";
  await send("Page.navigate", { url: B }); await sleep(3000);
  await ev("navigator.serviceWorker.getRegistrations().then(rs=>Promise.all(rs.map(r=>r.unregister())))");
  await ev("caches.keys().then(ks=>Promise.all(ks.map(k=>caches.delete(k))))");
  await sleep(600);
  let pass = 0, fail = 0;
  const ok = (c, m) => { if (c) { pass++; console.log("  PASS " + m); } else { fail++; console.log("  FAIL " + m); } };
  await send("Emulation.setDeviceMetricsOverride", { width: 390, height: 844, deviceScaleFactor: 2, mobile: true });

  console.log("[1] 卡片化渲染");
  await ev("go('#/phys/quiz')"); await sleep(3000);
  const nCards = await ev("document.querySelectorAll('.qpick').length");
  ok(nCards === 38, `物理 38 张课题卡片（${nCards}）`);
  ok(await ev("!!document.querySelector('.qpickwrap .qpick .qpick-t')") === true, "卡片含课题标题");
  ok(await ev("!!document.querySelector('.qpick .qpick-d')") === true, "卡片含课题简介");
  ok(await ev("!!document.querySelector('.qpick .qpick-pbar')") === true, "卡片含掌握度进度条");
  ok(await ev("!!document.querySelector('.qpick .qpick-go')") === true, "卡片含「單獨測驗」按钮");
  ok(await ev("document.querySelectorAll('.qpick input[type=checkbox]').length") === 38, "每卡一个勾选框");
  // 卡片不能是 label 包裹 button 的非法嵌套
  ok(await ev("document.querySelectorAll('label.qpick').length") === 0, "卡片用 div 而非 label（避免非法嵌套）");
  // 卡片要有课题色条
  ok(await ev("!!document.querySelector('.qpick .bar')") === true, "卡片含课题色条");
  // 网格布局
  const grid = await ev("getComputedStyle(document.querySelector('.qplist')).gridTemplateColumns");
  ok(grid && grid.split(" ").length >= 1, `卡片网格布局（${grid}）`);

  console.log("\n[2] 勾选功能");
  ok(await ev("!document.getElementById('pickbar')") === true, "未选无底部浮条");
  await ev(`(()=>{const b=[...document.querySelectorAll('.qpick input[type=checkbox]')];b[0].checked=true;b[1].checked=true;b[4].checked=true;quizPickChanged();})()`);
  await sleep(500);
  const st = await ev("document.getElementById('pickbar-t')?.textContent||''");
  console.log("  浮条:", st);
  ok(st.includes('已選 3 個課題'), "浮条显示已选 3 个");
  ok(await ev("document.querySelectorAll('.qpick.on').length") === 3, "3 张卡片进入选中态");
  ok(await ev("document.getElementById('pickbar').querySelector('.pickbar-go').disabled") === false, "开始按钮启用");

  console.log("\n[3] 点卡片空白处也能勾选");
  await ev("quizPickAll(false)"); await sleep(300);
  await ev(`(()=>{const c=document.querySelectorAll('.qpick')[2];c.querySelector('.qpick-d').click();})()`);
  await sleep(400);
  ok(await ev("document.querySelectorAll('.qpick input:checked').length") === 1, "点简介即勾选");
  ok(await ev("document.querySelectorAll('.qpick.on').length") === 1, "选中态同步");

  console.log("\n[4] 全部勾选 / 全部清除");
  await ev("quizPickAll(true)"); await sleep(500);
  ok(await ev("document.querySelectorAll('.qpick input:checked').length") === 38, "全部勾选 38 个");
  await ev("quizPickAll(false)"); await sleep(400);
  ok(await ev("document.querySelectorAll('.qpick input:checked').length") === 0, "全部清除");
  ok(await ev("!document.getElementById('pickbar')") === true, "清空后浮条消失");

  console.log("\n[5] 分区全选");
  await ev("quizPickUnit('thermal',true)"); await sleep(500);
  const unitN = await ev("document.querySelectorAll('.qgroup[data-uid=\"thermal\"] .qpick input:checked').length");
  ok(unitN === 5, `热学分区全选 5 个（${unitN}）`);
  await ev("quizPickUnit('thermal',false)"); await sleep(300);

  console.log("\n[6] 合成测验");
  await ev(`(()=>{const b=[...document.querySelectorAll('.qpick input[type=checkbox]')];b[0].checked=true;b[1].checked=true;b[4].checked=true;quizPickChanged();})()`);
  await sleep(500);
  await ev("document.getElementById('pickbar').querySelector('.pickbar-go').click()"); await sleep(4000);
  ok((await ev("location.hash")).includes('/run'), "进入答题页");
  const poolTopics = await ev("JSON.stringify([...new Set(QZ.pool.map(q=>q.topic))])");
  ok(JSON.parse(poolTopics).length === 3, `题库来自 3 个课题（${poolTopics}）`);
  ok(await ev("QZ.pool.length>0") === true, `共 ${await ev("QZ.pool.length")} 道题`);

  console.log("\n[7] 單獨測驗按钮");
  await ev("go('#/phys/quiz')"); await sleep(2500);
  await ev("document.querySelectorAll('.qpick-go')[0].click()"); await sleep(3500);
  ok((await ev("location.hash")).includes('/run'), "单课题测验可进入");
  const one = await ev("JSON.stringify([...new Set(QZ.pool.map(q=>q.topic))])");
  ok(JSON.parse(one).length === 1, `只考 1 个课题（${one}）`);

  console.log("\n[8] 科目隔离");
  await ev("go('#/chem/quiz')"); await sleep(3000);
  const chemN = await ev("document.querySelectorAll('.qpick').length");
  ok(chemN === 12, `化学 12 张卡片（${chemN}）`);
  const chemIds = await ev("JSON.stringify([...document.querySelectorAll('.qpick input')].map(b=>b.value))");
  ok(!chemIds.includes("heat1"), "化学页不含物理课题 id");
  await ev("go('#/phys/quiz')"); await sleep(2500);
  const physIds = await ev("JSON.stringify([...document.querySelectorAll('.qpick input')].map(b=>b.value))");
  ok(!physIds.includes("chem1"), "物理页不含化学课题 id");

  console.log("\n[9] 移动端不溢出");
  await ev("go('#/phys/quiz')"); await sleep(2500);
  const ov = await ev("({sw:document.documentElement.scrollWidth,cw:document.documentElement.clientWidth})");
  ok(ov.sw <= ov.cw + 2, `无横向溢出（${ov.sw} / ${ov.cw}）`);

  const s = await send("Page.captureScreenshot", { format: "png" });
  fs.writeFileSync("_t_qcard.png", Buffer.from(s.result.data, "base64"));
  ok(logs.length === 0, `零异常（${logs.length}）`);
  if (logs.length) logs.slice(0, 5).forEach(l => console.log("   " + l));
  console.log(`\n结果：通过 ${pass}，失败 ${fail}`);
  process.exit(fail ? 1 : 0);
})().catch(e => { console.log("FATAL", e.message); process.exit(1); });
