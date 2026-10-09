/* ============================================================
   神智核 · 搜索后台 Worker
   ------------------------------------------------------------
   把「全量遍历 payload 匹配关键词」的 CPU 密集工作从主线程移走，
   让输入搜索时界面不再冻结。主线程只负责渲染结果。
   匹配规则与主线程 searchLocal 完全一致：
     · 知识点：标题 / 正文 / 标签 拼接后做子串匹配（化学式、标签、标题都在内）
     · 题目：题干 / 解析 / 选项 拼接后做子串匹配
     · 标题命中权重（100）高于正文（10）；题干命中（90）高于选项（5）
     · 结果按得分降序，最多返回前 60 条
   数据（topics/quiz）只在首次或换科目时由主线程推送一次，
   之后每次搜索只传关键词，避免反复克隆整份 payload。
   ============================================================ */
var SEED = { sid: null, topics: [], quiz: {} };

self.onmessage = function (e) {
  var d = e.data || {};

  // 收到资料（首次或换科目）就先存起来
  if (d.topics) {
    SEED.sid = d.sid || '';
    SEED.topics = d.topics || [];
    SEED.quiz = d.quiz || {};
  }

  var kw = (d.kw || String(d.q || '')).toLowerCase();
  var hits = [];

  if (kw) {
    SEED.topics.forEach(function (t) {
      (t.sections || []).forEach(function (s) {
        (s.points || []).forEach(function (p) {
          var hay = ((p.title || '') + '\n' + (p.body || '') + '\n' + ((p.tags || []).join(' '))).toLowerCase();
          if (hay.indexOf(kw) >= 0) {
            var inTitle = (p.title || '').toLowerCase().indexOf(kw) >= 0;
            hits.push({ t: t, s: s, p: p, score: inTitle ? 100 : 10, hay: hay });
          }
        });
      });
    });
    Object.keys(SEED.quiz).forEach(function (tid) {
      (SEED.quiz[tid] || []).forEach(function (qq) {
        var hay = ((qq.q || '') + '\n' + (qq.explanation || '') + '\n' + ((qq.options || []).join(' '))).toLowerCase();
        if (hay.indexOf(kw) >= 0) {
          hits.push({ q: qq, topic: tid, score: (qq.q || '').toLowerCase().indexOf(kw) >= 0 ? 90 : 5, hay: hay });
        }
      });
    });
    hits.sort(function (a, b) { return b.score - a.score; });
  }

  self.postMessage({ q: d.q, kw: kw, hits: hits.slice(0, 60), total: hits.length });
};
