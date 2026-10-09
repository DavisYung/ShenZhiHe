/* ---------------- 額外資訊（元素週期表等補充資料） ---------------- */
let PT_ST = null;
function extrasOf(){ return (SUB && SUB.extras) || []; }
function extraById(id){ var xs=extrasOf(); for(var i=0;i<xs.length;i++) if(xs[i].id===id) return xs[i]; return null; }

function viewExtras(){
  navOn("extras");
  if(needsContent())return;
  var xs=extrasOf();
  if(!xs.length){
    app.innerHTML="<div class=\"view\"><div class=\"thead\"><button class=\"back\" onclick=\"go(\'#/home\')\">← 返回首頁</button><h2>📎 額外資訊</h2></div>"
      +"<div class=\"emptybox\"><div class=\"e1\">📎</div><h3>這一科還沒有額外資訊</h3>"
      +"<p>把 JSON 放進 <code>f6chem/extras/"+esc(SUB.id)+"/*.json</code>，重新產生網站就會出現在這裡。</p></div></div>";
    return;
  }
  var cards=xs.map(function(x){
    return "<div class=\"extracard\" onclick=\"go(\'#/extras/"+encodeURIComponent(x.id)+"\')\">"
      +"<div class=\"exemoji\">"+(x.emoji||"📎")+"</div>"
      +"<h3>"+esc(x.title||x.id)+"</h3>"
      +"<p>"+esc(x.subtitle||x.intro||"")+"</p>"
      +"<div style=\"margin-top:12px;border-top:1px dashed var(--line);padding-top:9px;font-size:12.5px;color:var(--muted)\">"+esc(x.source||"")+"</div>"
      +"</div>";
  }).join("");
  app.innerHTML="<div class=\"view\"><div class=\"thead\"><button class=\"back\" onclick=\"go(\'#/home\')\">← 返回首頁</button><h2>📎 額外資訊</h2></div>"
    +"<div class=\"tmeta\">本科的補充資料：表格、速查、圖鑑。不計入學習進度，純查閱用。</div>"
    +"<div class=\"extras-grid\">"+cards+"</div></div>";
}

function viewExtra(id, sel){
  navOn("extras");
  if(needsContent())return;
  var x=extraById(id);
  if(!x){ go("#/extras"); return; }
  if(x.type==="ptable"){ viewPtable(x, sel); return; }
  if(x.type==="hot"){ viewHot(x); return; }
  app.innerHTML="<div class=\"view\"><div class=\"thead\"><button class=\"back\" onclick=\"go(\'#/extras\')\">← 額外資訊</button><h2>"+esc(x.emoji||"📎")+" "+esc(x.title||x.id)+"</h2></div>"
    +"<div class=\"tmeta\">"+esc(x.subtitle||"")+"</div>"
    +"<div class=\"note\">這個額外資訊的型別（"+esc(x.type||"未指定")+"）還沒有專屬版面，先在下方看原始內容。</div>"
    +"<pre style=\"overflow:auto;background:#fff;border:1px solid var(--line);border-radius:12px;padding:14px;font-size:13px\">"+esc(JSON.stringify(x,null,1).slice(0,20000))+"</pre></div>";
}

/* ---- 高頻考點報告 ---- */
var HOT_ST={topic:"",q:""};
var CUR_HOT=null;
function hotTopicColor(tid){
  var C={"1a":"#7c3aed","1b":"#0ea5e9","1c":"#f59e0b","2a":"#0f766e","2b":"#ef4444","3a":"#22c55e","3b":"#14b8a6","3c":"#f97316","4a":"#8b5cf6","4b":"#ec4899","6":"#64748b","8":"#a855f7"};
  return C[tid]||"#64748b";
}
function hotLvTag(lv){
  if(lv>=3) return '<span class="hlv3">🔥 必考</span>';
  if(lv===2) return '<span class="hlv2">⭐ 常考</span>';
  return '<span class="hlv1">· 考過</span>';
}
function hotItemRow(it){
  var kws=(it.kw||[]).slice(0,6).map(function(k){return '<span class="hkw">'+esc(k)+'</span>';}).join("");
  var yr=(it.years||[]).join(" / ");
  var samp="";
  if(it.samples&&it.samples.length){
    samp='<details class="hsamp"><summary>看 '+it.samples.length+' 條題目實例</summary><ul>'
      +it.samples.map(function(s){return '<li><b>'+esc(s.ref||"")+'</b>：'+esc(s.focus||"")+'</li>';}).join("")
      +'</ul></details>';
  }
  return '<tr>'
    +'<td>'+hotLvTag(it.level)+'</td>'
    +'<td><span class="htag" style="background:'+hotTopicColor(it.topic)+'">'+esc(it.topic)+'</span> '+esc(it.tname||"")+'<div class="hsec">'+esc(it.sec||"")+'</div></td>'
    +'<td><a href="#/t/'+esc(it.topic)+'">'+esc(it.title)+'</a>'+(it.page?'<span class="hpg">P'+esc(it.page)+'</span>':"")+'</td>'
    +'<td class="hyr">'+esc(yr)+'</td>'
    +'<td>'+(kws||'<span class="hdim">—</span>')+samp+'</td>'
    +'</tr>';
}
function hotFiltered(x){
  var rows=[];
  (x.groups||[]).forEach(function(g){ (g.items||[]).forEach(function(it){ rows.push(it); }); });
  var t=HOT_ST.topic, q=(HOT_ST.q||"").trim().toLowerCase();
  return rows.filter(function(it){
    if(t && it.topic!==t) return false;
    if(!q) return true;
    if(String(it.title).toLowerCase().indexOf(q)>=0) return true;
    if(String(it.tname||"").toLowerCase().indexOf(q)>=0) return true;
    if(String(it.sec||"").toLowerCase().indexOf(q)>=0) return true;
    return (it.kw||[]).some(function(k){return String(k).toLowerCase().indexOf(q)>=0;});
  });
}
function hotSetTopic(t){ HOT_ST.topic=(HOT_ST.topic===t)?"":t; viewHot(CUR_HOT); }
function hotSetQ(v){ HOT_ST.q=v; viewHot(CUR_HOT); }
function viewHot(x){
  navOn("extras");
  if(needsContent())return;
  CUR_HOT=x;
  var s=x.summary||{};
  var shown=hotFiltered(x);
  var chips='<button class="hchip'+(HOT_ST.topic?"":" on")+'" onclick="hotSetTopic(\'\')">全部</button>'
    +(x.topics||[]).map(function(t){
      return '<button class="hchip'+(HOT_ST.topic===t.id?" on":"")+'" style="--hc:'+hotTopicColor(t.id)+'" onclick="hotSetTopic(\''+esc(t.id)+'\')">'
        +esc(t.id)+' '+esc(t.name)+' <b>'+t.hits+'</b></button>';
    }).join("");
  var cards=[
    '<div class="hcard"><div class="n">'+(s.points||0)+'</div><div class="l">被考的知識點</div></div>',
    '<div class="hcard"><div class="n">'+(s.hits||0)+'</div><div class="l">命中次數</div></div>',
    '<div class="hcard"><div class="n" style="color:#dc2626">'+(s.lv3||0)+'</div><div class="l">🔥 必考（5年+）</div></div>',
    '<div class="hcard"><div class="n" style="color:#ea580c">'+(s.lv2||0)+'</div><div class="l">⭐ 常考（2-4年）</div></div>',
    '<div class="hcard"><div class="n">'+(s.years?s.years.length:0)+'</div><div class="l">參考年份</div></div>'
  ].join("");
  var yrTbl='<table class="htable"><thead><tr><th>年份</th><th>命中</th><th>涉及課題</th></tr></thead><tbody>'
    +(x.years||[]).map(function(y){
      return '<tr><td><b>'+y.year+'</b></td><td>'+y.hits+'</td><td>'
        +(y.topics||[]).map(function(t){return '<span class="htag" style="background:'+hotTopicColor(t)+'">'+esc(t)+'</span>';}).join("")
        +'</td></tr>';
    }).join("")+'</tbody></table>';
  var kwTbl='<div class="hkwcloud">'+(x.keywords||[]).slice(0,50).map(function(k){
    return '<span class="hkw" style="font-size:'+(12+Math.min(4,k.count))+'px">'+esc(k.text)+' <small>'+k.count+'</small></span>';
  }).join("")+'</div>';
  app.innerHTML="<div class=\"view\">"
    +"<div class=\"thead\"><button class=\"back\" onclick=\"go(\'#/extras\')\">← 額外資訊</button>"
    +"<h2>"+(x.emoji||"🔥")+" "+esc(x.title||"高頻考點")+"</h2></div>"
    +"<div class=\"tmeta\">"+esc(x.subtitle||"")+(x.source?" ｜ 來源："+esc(x.source):"")+"</div>"
    +(x.intro?'<div class="note">'+esc(x.intro)+'</div>':"")
    +'<div class="hcards">'+cards+'</div>'
    +'<div class="hfilter"><input type="search" placeholder="搜尋知識點或得分字眼…" value="'+esc(HOT_ST.q||"")+'" oninput="hotSetQ(this.value)"></div>'
    +'<div class="hchips">'+chips+'</div>'
    +'<div class="hcount">目前顯示 <b>'+shown.length+'</b> 個知識點'+(HOT_ST.topic?'（課題 '+esc(HOT_ST.topic)+'）':'')+'</div>'
    +'<table class="htable"><thead><tr><th>熱度</th><th>課題</th><th>知識點</th><th>考過年份</th><th>得分字眼</th></tr></thead><tbody>'
    +(shown.length?shown.map(hotItemRow).join("")
      :'<tr><td colspan="5" class="hdim">沒有符合的知識點</td></tr>')
    +'</tbody></table>'
    +'<h3 class="hsec-h">各年被考課題覆蓋</h3>'+yrTbl
    +'<h3 class="hsec-h">得分字眼總覽</h3><p class="hdim" style="font-size:13px;margin:4px 0 8px">評卷參考常見的採分表述，答題時務必寫出來；括號是它出現在幾個知識點裡。</p>'+kwTbl
    +(x.note?'<div class="note" style="margin-top:18px">'+esc(x.note)+'</div>':"")
    +"</div>";
}

/* ---- 元素週期表 ---- */
function ptInit(x){
  if(!PT_ST || PT_ST.id!==x.id) PT_ST={id:x.id,cats:{},q:"",sel:null};
  (x.categories||[]).forEach(function(c){ if(PT_ST.cats[c.id]===undefined) PT_ST.cats[c.id]=true; });
}
function viewPtable(x, sel){
  ptInit(x);
  if(sel) PT_ST.sel=parseInt(sel,10)||null;
  app.innerHTML="<div class=\"view\">"
    +"<div class=\"thead\"><button class=\"back\" onclick=\"go(\'#/extras\')\">← 額外資訊</button>"
    +"<h2>"+(x.emoji||"⚛️")+" "+esc(x.title||"元素週期表")+"</h2></div>"
    +"<div class=\"tmeta\">"+esc(x.subtitle||"")+(x.source?" ｜ 來源："+esc(x.source):"")+"</div>"
    +"<div class=\"ptwrap\">"
    +"<div class=\"ptsearch\"><input id=\"ptq\" type=\"search\" placeholder=\"搜尋：氫 / H / hydrogen / 1\" autocomplete=\"off\" value=\""+esc(PT_ST.q)+"\" oninput=\"ptSearch(this.value)\"><button class=\"back\" onclick=\"ptClear()\">清除</button></div>"
    +"<div class=\"ptlegend\" id=\"ptlegend\"></div>"
    +"<div class=\"ptscroll\"><div class=\"ptgrid\" id=\"ptgrid\"></div></div>"
    +"<div style=\"font-size:12.5px;color:var(--muted);margin-top:8px\">手機上表格可左右滑動；點格子看詳細資料。"+(x.massNote?" "+esc(x.massNote):"")+"</div>"
    +"</div>"
    +"<div id=\"ptdetail\"></div>"
    +"</div>";
  renderLegend(x); renderGrid(x); renderDetail(x);
}
function ptMatch(e){
  if(!PT_ST.cats[e.cat]) return false;
  var q=(PT_ST.q||"").trim().toLowerCase();
  if(!q) return true;
  return e.sym.toLowerCase().indexOf(q)>=0 || e.cn.indexOf(q)>=0 || e.en.toLowerCase().indexOf(q)>=0 || String(e.z)===q;
}
function ptCell(e,CATCOL){
  var on=(PT_ST.sel===e.z)?" on":"";
  var dim=ptMatch(e)?"":" dim";
  var bg=CATCOL[e.cat]||"#eeeeee";
  var nonh=(e.hkeaa===false)?" nonh":"";
  return "<div class=\"ptcell"+on+dim+nonh+"\" data-z=\""+e.z+"\" style=\"background:"+bg+"\" onclick=\"ptPick("+e.z+")\">"
    +"<div class=\"z\">"+e.z+"</div>"
    +"<div class=\"sym\">"+esc(e.sym)+"</div>"
    +"<div class=\"cn\">"+esc(e.cn)+"</div>"
    +"<div class=\"ms\">"+esc(e.mass)+"</div>"
    +"<div class=\"st\">"+esc(e.state)+"</div>"
    +"</div>";
}
function renderGrid(x){
  var el=document.getElementById("ptgrid"); if(!el)return;
  var map={}; (x.elements||[]).forEach(function(e){ map[e.row+"-"+e.col]=e; });
  var CATCOL={}; (x.categories||[]).forEach(function(c){ CATCOL[c.id]=c.color; });
  var s="";
  for(var r=1;r<=7;r++){
    for(var c=1;c<=18;c++){
      var e=map[r+"-"+c];
      s += e ? ptCell(e,CATCOL) : "<div></div>";
    }
  }
  s+="<div class=\"ptgap\"></div>";
  for(var r2=8;r2<=9;r2++){
    s+="<div class=\"ptrowlabel\" style=\"grid-column:1/3\">"+(r2===8?"鑭系":"錒系")+"</div>";
    for(var c2=3;c2<=17;c2++){
      var e2=map[r2+"-"+c2];
      s += e2 ? ptCell(e2,CATCOL) : "<div></div>";
    }
    s+="<div></div>";
  }
  el.innerHTML=s;
}
function renderLegend(x){
  var el=document.getElementById("ptlegend"); if(!el)return;
  el.innerHTML=(x.categories||[]).map(function(c){
    return "<span class=\""+((PT_ST.cats[c.id]||false)?"":"off")+"\" onclick=\"ptToggle(\'"+c.id+"\')\"><i style=\"background:"+c.color+"\"></i>"+esc(c.name)+"</span>";
  }).join("")+"<span style=\"border-style:dashed\" onclick=\"ptAllCats()\">全部顯示</span>";
}
function renderDetail(x){
  var el=document.getElementById("ptdetail"); if(!el)return;
  var cats={}; (x.categories||[]).forEach(function(c){ cats[c.id]=c; });
  var e=null;
  (x.elements||[]).forEach(function(v){ if(v.z===PT_ST.sel) e=v; });
  if(!e){ el.innerHTML="<div class=\"ptempty\">"+(x.intro||"點表格裡的元素看詳細資料。")+"</div>"; return; }
  var c=cats[e.cat]||{name:e.cat,color:"#eeeeee"};
  var posTxt = e.row<=7 ? ("第 "+e.period+" 週期"+(e.group?(" · 第 "+e.group+" 族"):"")) : (e.row===8?"鑭系元素":"錒系元素");
  el.innerHTML="<div class=\"ptdetail\"><div class=\"pth\">"
    +"<div class=\"box\" style=\"background:"+c.color+"\"><span>"+e.z+"</span><b>"+esc(e.sym)+"</b></div>"
    +"<div><h3>"+esc(e.cn)+" <span style=\"font-size:15px;color:var(--muted);font-weight:400\">"+esc(e.en)+"</span></h3>"
    +"<div style=\"font-size:13.5px;color:var(--muted)\">"+esc(c.name)+" · "+esc(posTxt)+"</div></div>"
    +"<button class=\"qbtn\" style=\"margin-left:auto\" onclick=\"ptFindNotes("+e.z+")\">🔍 在筆記裡找這個元素</button>"
    +"</div>"
    +"<div class=\"kv\">"
    +"<div><b>原子序</b><span>"+e.z+"</span></div>"
    +"<div><b>相對原子質量</b><span>"+esc(e.mass)+"</span></div>"
    +"<div><b>常溫狀態</b><span>"+esc(e.state==="氣"?"氣體":(e.state==="液"?"液體":"固體"))+"</span></div>"
    +"<div><b>類別</b><span>"+esc(c.name)+"</span></div>"
    +"</div>"
    +((e.hkeaa===false)?"<div style=\"font-size:12.5px;color:var(--amber);margin-top:8px\">⚠️ 這個元素不在香港考評局週期表內，相對原子質量為現代公認值，僅供參考。</div>":"")
    +(x.note?"<div style=\"font-size:13px;color:var(--muted);margin-top:10px\">"+esc(x.note)+"</div>":"")+"</div>";
}
function ptPick(z){
  PT_ST.sel=(PT_ST.sel===z?null:z);
  var x=extraById(PT_ST.id); renderGrid(x); renderDetail(x);
  if(PT_ST.sel) go("#/extras/"+PT_ST.id+"@"+PT_ST.sel);
}
function ptSearch(v){ PT_ST.q=v||""; var x=extraById(PT_ST.id); renderGrid(x); renderDetail(x); }
function ptClear(){ PT_ST.q=""; var i=document.getElementById("ptq"); if(i)i.value=""; var x=extraById(PT_ST.id); renderGrid(x); renderDetail(x); }
function ptToggle(cid){ PT_ST.cats[cid]=!PT_ST.cats[cid]; var x=extraById(PT_ST.id); renderLegend(x); renderGrid(x); }
function ptAllCats(){ var x=extraById(PT_ST.id); (x.categories||[]).forEach(function(c){ PT_ST.cats[c.id]=true; }); renderLegend(x); renderGrid(x); }
function ptFindNotes(z){
  var x=extraById(PT_ST.id); var e=null;
  (x.elements||[]).forEach(function(v){ if(v.z===z) e=v; });
  if(!e)return;
  go("#/search@"+encodeURIComponent(e.cn));
}
