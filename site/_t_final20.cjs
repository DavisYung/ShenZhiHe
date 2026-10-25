const fs=require("fs");const PORT=9333;
const VER=JSON.parse(fs.readFileSync(__dirname+"/version.json","utf8")).version;
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
(async()=>{
 let list=null;
 for(let i=0;i<60;i++){try{const r=await fetch(`http://127.0.0.1:${PORT}/json/list`);list=await r.json();if(list&&list.some(t=>t.type==="page"))break;}catch(e){}await sleep(300);}
 const ws=new WebSocket(list.find(t=>t.type==="page").webSocketDebuggerUrl);
 let id=0;const pending=new Map();const logs=[];
 ws.onmessage=ev=>{const m=JSON.parse(ev.data);if(m.id&&pending.has(m.id)){pending.get(m.id)(m);pending.delete(m.id);}
  if(m.method==="Runtime.exceptionThrown")logs.push("EX:"+(m.params.exceptionDetails.exception?.description||"").split("\n")[0]);};
 const send=(m,p={})=>new Promise(res=>{const i=++id;pending.set(i,res);ws.send(JSON.stringify({id:i,method:m,params:p}));});
 await new Promise(r=>ws.onopen=r);
 await send("Page.enable");await send("Runtime.enable");await send("Network.enable");
 await send("Network.setCacheDisabled",{cacheDisabled:true});
 const ev=async e=>{const r=await send("Runtime.evaluate",{expression:e,returnByValue:true,awaitPromise:true});if(r.result?.exceptionDetails)return "EXC:"+(r.result.exceptionDetails.exception?.description||"");return r.result?.result?.value;};
 const S="https://nzgjsmy.github.io/ShenZhiHe/";
 let pass=0,fail=0;const ok=(c,m)=>{if(c){pass++;console.log("  PASS "+m);}else{fail++;console.log("  FAIL "+m);}};
 await send("Emulation.setDeviceMetricsOverride",{width:390,height:844,deviceScaleFactor:2,mobile:true});
 await send("Page.navigate",{url:S+"#/phys/quiz"});await sleep(10000);
 console.log("[线上 · "+VER+" 课题勾选]");
 ok(await ev("!!document.querySelector('.qpickwrap')")===true,"课题列表可勾选");
 ok(await ev("document.querySelectorAll('.qpick').length")===38,"38 个课题");
 ok(await ev("document.querySelector('.fver').textContent.trim()")===VER,"页脚 "+VER);
 ok(await ev("!document.getElementById('pickbar')")===true,"未选无浮条");
 await ev(`(()=>{const bs=[...document.querySelectorAll('.qpickwrap input')];bs[0].checked=true;bs[1].checked=true;bs[4].checked=true;quizPickChanged();})()`);await sleep(500);
 const st=await ev("document.getElementById('pickbar-t').textContent");
 console.log("  浮条:",st);
 ok(st.includes('已選 3 個課題'),"显示已选 3 个");
 ok(await ev("document.getElementById('pickbar').querySelector('.pickbar-go').disabled")===false,"按钮启用");
 await ev("document.getElementById('pickbar').querySelector('.pickbar-go').click()");await sleep(4000);
 ok((await ev("location.hash")).includes('/run'),"进入答题");
 const q=await ev("document.querySelector('.qtype').textContent.trim()");
 console.log("  题型:",q);
 const poolTopics=await ev("JSON.stringify([...new Set(QZ.pool.map(q=>q.topic))])");
 ok(JSON.parse(poolTopics).length===3,`题库 3 个课题（${poolTopics}）`);
 ok(logs.length===0,`零异常（${logs.length}）`);
 console.log(`\n结果：通过 ${pass}，失败 ${fail}`);
 process.exit(fail?1:0);
})().catch(e=>{console.log("FATAL",e.message);process.exit(1);});
