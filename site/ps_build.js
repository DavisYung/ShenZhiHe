// 用 Node.js 模拟 build.py 的构建逻辑
const fs = require('fs');
const path = require('path');

const root = 'f6chem';
const siteDir = path.join(root, 'site');
const dataDir = path.join(root, 'data');
const quizDir = path.join(root, 'quiz');
const extrasDir = path.join(root, 'extras');

// 读取 version.json
const version = JSON.parse(fs.readFileSync(path.join(siteDir, 'version.json'), 'utf8').replace(/^\uFEFF/, ''));
const siteName = version.name;
const siteVer = version.version;

console.log(`站名: ${siteName} ${siteVer}`);

// 发现科目
const subjectIds = [];
for (const name of fs.readdirSync(dataDir)) {
    const dir = path.join(dataDir, name);
    if (fs.statSync(dir).isDirectory() && fs.existsSync(path.join(dir, 'subject.json'))) {
        subjectIds.push(name);
    }
}
console.log(`科目: ${subjectIds.join(', ')}`);

const RESERVED = new Set(['subject', 'links', 'index']);

function loadJSON(p) {
    if (!fs.existsSync(p)) return null;
    const content = fs.readFileSync(p, 'utf8').replace(/^\uFEFF/, '');
    return JSON.parse(content);
}

const payload = {
    site: {
        name: siteName,
        version: siteVer,
        subtitle: version.subtitle || '',
        tagline: version.tagline || '',
        note: version.note || '',
        copyright: version.copyright || '',
        disclaimer: version.disclaimer || []
    },
    subjects: []
};

for (const sid of subjectIds) {
    const sdir = path.join(dataDir, sid);
    const qdir = path.join(quizDir, sid);
    const meta = loadJSON(path.join(sdir, 'subject.json')) || {};

    // 列出课题
    const listed = (meta.topics || []).filter(t => t && !RESERVED.has(t));

    // 扫描 data 目录
    const found = [];
    for (const n of fs.readdirSync(sdir)) {
        if (!n.endsWith('.json')) continue;
        const stem = n.slice(0, -5);
        if (RESERVED.has(stem)) continue;
        if (stem.startsWith('payload') || stem.startsWith('batch') || stem.startsWith('tmp') || stem.startsWith('_') || stem.endsWith('-batch')) continue;
        found.push(stem);
    }
    found.sort();

    const topicsIds = listed.length > 0 ? listed : found;

    // 读取课题数据
    const topics = [];
    for (const tid of topicsIds) {
        const p = path.join(sdir, tid + '.json');
        if (!fs.existsSync(p)) {
            console.log(`  warning: ${sid} 缺少课题档 ${tid}.json`);
            continue;
        }
        const t = JSON.parse(fs.readFileSync(p, 'utf8'));
        if (!t.id) t.id = tid;
        topics.push(t);
    }
    topics.sort((a, b) => String(a.id).localeCompare(String(b.id)));

    // 读取 links
    const linksPath = path.join(sdir, 'links.json');
    let links = loadJSON(linksPath) || [];
    // 过滤无效链接
    const pointIds = new Set();
    for (const t of topics) {
        for (const s of (t.sections || [])) {
            for (const p of (s.points || [])) {
                pointIds.add(p.id);
            }
        }
    }
    const validLinks = [];
    let dropped = 0;
    for (const l of links) {
        if (pointIds.has(l.from) && pointIds.has(l.to)) {
            validLinks.push(l);
        } else {
            dropped++;
        }
    }
    if (dropped > 0) {
        console.log(`  note: ${sid} links.json 有 ${dropped} 条指向不存在的知识点，已忽略`);
    }
    links = validLinks;

    // 读取 quiz
    const quiz = {};
    for (const tid of topicsIds) {
        const qp = path.join(qdir, tid + '.json');
        if (!fs.existsSync(qp)) continue;
        const q = JSON.parse(fs.readFileSync(qp, 'utf8'));
        if (q.questions && Array.isArray(q.questions) && q.questions.length > 0) {
            quiz[tid] = q.questions;
        }
    }

    // 统计
    let nPts = 0;
    let nSec = 0;
    for (const t of topics) {
        nSec += (t.sections || []).length;
        for (const s of (t.sections || [])) {
            nPts += (s.points || []).length;
        }
    }
    let nQ = 0;
    for (const k of Object.keys(quiz)) {
        nQ += quiz[k].length;
    }
    const ready = nPts > 0;

    // units
    const units = [];
    const rawUnits = meta.units || [];
    const tidSet = new Set(topics.map(t => t.id));
    for (const u of rawUnits) {
        const uTids = (u.topics || []).filter(x => tidSet.has(x));
        if (uTids.length === 0) {
            console.log(`  warning: ${sid} 的单元 ${u.id} 没有对应课题，已略过`);
            continue;
        }
        const uTopics = topics.filter(t => uTids.includes(t.id));
        let uPts = 0;
        let uSec = 0;
        for (const t of uTopics) {
            uSec += (t.sections || []).length;
            for (const s of (t.sections || [])) {
                uPts += (s.points || []).length;
            }
        }
        let uQ = 0;
        for (const t of uTopics) {
            if (quiz[t.id]) uQ += quiz[t.id].length;
        }
        units.push({
            id: u.id,
            title: u.title || u.id,
            emoji: u.emoji || '',
            description: u.description || '',
            topics: uTids,
            stats: {
                topics: uTids.length,
                sections: uSec,
                points: uPts,
                questions: uQ
            }
        });
    }

    const subject = {
        id: sid,
        title: meta.title || sid,
        full: meta.full || meta.title || sid,
        emoji: meta.emoji || '📘',
        color: meta.color || '#0f766e',
        order: meta.order !== undefined ? meta.order : 99,
        description: meta.description || '',
        source: meta.source || '',
        ready: ready,
        topics: topics,
        units: units,
        links: links,
        quiz: quiz,
        extras: [],
        stats: {
            topics: topics.length,
            sections: nSec,
            points: nPts,
            links: links.length,
            questions: nQ,
            units: units.length
        }
    };

    console.log(`  ${sid}: 课题 ${topics.length} · 章节 ${nSec} · 知识点 ${nPts} · 串连 ${links.length} · 题目 ${nQ}`);
    payload.subjects.push(subject);
}

// 排序
payload.subjects.sort((a, b) => {
    if (a.order !== b.order) return a.order - b.order;
    return String(a.id).localeCompare(String(b.id));
});

// 读取模板并替换
let tpl = fs.readFileSync(path.join(siteDir, 'template.html'), 'utf8');
tpl = tpl.replace('/*__SITE_NAME__*/', siteName);
tpl = tpl.replace('/*__SITE_VERSION__*/', siteVer);
tpl = tpl.replace('/*__SITE_SUBTITLE__*/', version.subtitle || '');
tpl = tpl.replace('/*__SITE_COPYRIGHT__*/', version.copyright || '');

const discList = version.disclaimer || [];
const discHtml = discList.map(d => `<li>${d}</li>`).join('');
tpl = tpl.replace('/*__SITE_DISCLAIMER__*/', discHtml);

// extras.js
const exPath = path.join(siteDir, 'extras.js');
if (fs.existsSync(exPath)) {
    const exJs = fs.readFileSync(exPath, 'utf8');
    tpl = tpl.replace('/*__EXTRAS_JS__*/', exJs);
} else {
    tpl = tpl.replace('/*__EXTRAS_JS__*/', '');
}

// search-worker.js 注入
const swPath = path.join(siteDir, 'search-worker.js');
if (fs.existsSync(swPath)) {
    const swB64 = fs.readFileSync(swPath).toString('base64');
    const swSrc = `var __SEARCH_WORKER_URL__ = URL.createObjectURL(new Blob([atob('${swB64}')], {type:'application/javascript'}));`;
    tpl = tpl.replace('/*__SEARCH_WORKER__*/', swSrc);
} else {
    tpl = tpl.replace('/*__SEARCH_WORKER__*/', 'var __SEARCH_WORKER_URL__ = null;');
}

// 序列化 payload
const blob = JSON.stringify(payload);
const out = tpl.replace('/*__DATA__*/', blob);

// 输出
const stablePath = path.join(siteDir, `${siteName}.html`);
const versionedPath = path.join(siteDir, `${siteName}-${siteVer}.html`);

fs.writeFileSync(stablePath, out, 'utf8');
fs.writeFileSync(versionedPath, out, 'utf8');

console.log(`written: ${stablePath} (${fs.statSync(stablePath).size} bytes)`);
console.log(`written: ${versionedPath} (${fs.statSync(versionedPath).size} bytes)`);
