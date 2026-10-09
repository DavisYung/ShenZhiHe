// build.mjs —— build.py 的 Node 等價實作（不修改原 Python 檔）
// 用法: node build.mjs
// 產出與 build.py 完全相同：site/<站名>-<版號>.html 與 site/<站名>.html
import fs from 'fs'
import path from 'path'
import url from 'url'

const BASE = path.dirname(url.fileURLToPath(import.meta.url))
const ROOT = path.dirname(BASE)
const DATA = path.join(ROOT, 'data')
const QUIZ = path.join(ROOT, 'quiz')
const EXTRAS = path.join(ROOT, 'extras')
const IMG_DIR = path.join(BASE, 'img')
const VER_PATH = path.join(BASE, 'version.json')
const LEGACY_NAMES = ['F6筆記整合網.html', 'F6化學筆記整合網.html']
const RESERVED = new Set(['subject', 'links', 'index'])

const load = (p, dflt = null) => {
  if (!fs.existsSync(p)) return dflt
  try { return JSON.parse(fs.readFileSync(p, 'utf8').replace(/^﻿/, '')) } catch (e) {
    console.error('  ! JSON 解析失敗: ' + p + ' → ' + e.message)
    return dflt
  }
}

function siteMeta() {
  const v = load(VER_PATH, {}) || {}
  const name = (v.name || '神智核').trim()
  const version = (v.version || 'V0.1.0').trim()
  return {
    name, version,
    subtitle: v.subtitle || '',
    tagline: v.tagline || '',
    out_name: `${name}-${version}.html`,
    stable_name: `${name}.html`,
    note: v.note || ''
  }
}

function isTopicName(name) {
  if (!name.endsWith('.json')) return false
  const stem = name.slice(0, -5)
  if (RESERVED.has(stem)) return false
  if (/^(payload|batch|tmp|_)/.test(stem) || stem.endsWith('-batch')) return false
  return true
}

function inlineBodyImages(payload) {
  const pat = /\]\(img\/([^)\s]+)\)/g
  let n = 0
  const miss = []
  for (const s of payload.subjects || []) {
    for (const t of s.topics || []) {
      for (const sec of t.sections || []) {
        for (const p of sec.points || []) {
          const body = p.body || ''
          if (!body.includes('](img/')) continue
          p.body = body.replace(pat, (m0, file) => {
            const fp = path.join(IMG_DIR, file)
            if (!fs.existsSync(fp)) { miss.push(file); return m0 }
            n++
            return '](data:image/webp;base64,' + fs.readFileSync(fp).toString('base64') + ')'
          })
        }
      }
    }
  }
  if (miss.length) {
    console.log(`  warning: ${miss.length} 個圖片缺失（引用保留）: ${[...new Set(miss)].slice(0, 5).join(', ')}`)
  }
  return { n, miss }
}

function loadSubject(sid) {
  const sdir = path.join(DATA, sid)
  const qdir = path.join(QUIZ, sid)
  const meta = load(path.join(sdir, 'subject.json'), {}) || {}
  const listed = (meta.topics || []).filter(Boolean)
  const found = fs.existsSync(sdir)
    ? fs.readdirSync(sdir).filter(isTopicName).map((x) => x.slice(0, -5)).sort()
    : []
  let topicsIds = listed
  if (listed) {
    const extra = found.filter((t) => !listed.includes(t))
    if (extra.length) console.log(`  note: ${sid} 有未列在 subject.json 的課題檔，已忽略：${extra.join(', ')}`)
  } else {
    topicsIds = found
  }

  const topics = []
  for (const tid of topicsIds) {
    const p = path.join(sdir, tid + '.json')
    if (!fs.existsSync(p)) { console.log(`  warning: ${sid} 缺少課題檔 ${tid}.json`); continue }
    const t = load(p)
    if (t && typeof t === 'object' && !Array.isArray(t)) {
      if (t.id === undefined) t.id = tid
      topics.push(t)
    } else {
      console.log(`  warning: ${sid}/${tid}.json 格式不是物件，已跳過`)
    }
  }
  topics.sort((a, b) => String(a.id || '').localeCompare(String(b.id || '')))

  const pointIds = new Set()
  for (const t of topics) for (const s of t.sections || []) for (const p of s.points || []) pointIds.add(p.id)
  const links = []
  let dropped = 0
  for (const l of load(path.join(sdir, 'links.json'), []) || []) {
    if (!l || typeof l !== 'object') continue
    if (pointIds.has(l.from) && pointIds.has(l.to)) links.push(l)
    else dropped++
  }
  if (dropped) console.log(`  note: ${sid} links.json 有 ${dropped} 條指向不存在的知識點，已忽略`)

  const quiz = {}
  for (const tid of topicsIds) {
    const p = path.join(qdir, tid + '.json')
    if (!fs.existsSync(p)) continue
    const q = load(p, { questions: [] })
    if (q && typeof q === 'object' && Array.isArray(q.questions)) {
      const qs = q.questions.filter((x) => x && typeof x === 'object')
      if (qs.length) quiz[tid] = qs
    } else {
      console.log(`  warning: ${sid}/${tid}.json 測驗題格式不對，已跳過`)
    }
  }

  const extras = []
  const edir = path.join(EXTRAS, sid)
  if (fs.existsSync(edir)) {
    for (const n of fs.readdirSync(edir).sort()) {
      if (!n.endsWith('.json')) continue
      const x = load(path.join(edir, n))
      if (x && typeof x === 'object' && !Array.isArray(x)) {
        if (x.id === undefined) x.id = n.slice(0, -5)
        extras.push(x)
      }
    }
    extras.sort((a, b) => ((a.order ?? 99) - (b.order ?? 99)) || String(a.id).localeCompare(String(b.id)))
  }

  const nPts = topics.reduce((a, t) => a + (t.sections || []).reduce((b, s) => b + (s.points || []).length, 0), 0)
  const nQ = Object.values(quiz).reduce((a, v) => a + v.length, 0)

  return {
    id: sid,
    title: meta.title || sid,
    full: meta.full || meta.title || sid,
    emoji: meta.emoji || '📘',
    color: meta.color || '#0f766e',
    order: meta.order ?? 99,
    description: meta.description || '',
    source: meta.source || '',
    ready: nPts > 0,
    topics, links, quiz, extras,
    stats: {
      topics: topics.length,
      sections: topics.reduce((a, t) => a + (t.sections || []).length, 0),
      points: nPts,
      links: links.length,
      questions: nQ
    }
  }
}

function discoverSubjects() {
  if (!fs.existsSync(DATA)) { console.error('找不到 data 目錄：' + DATA); process.exit(1) }
  const ids = fs.readdirSync(DATA)
    .filter((name) => fs.existsSync(path.join(DATA, name, 'subject.json')))
    .sort()
  if (!ids.length) { console.error('data/ 底下沒有任何科目資料夾（需要 <科目>/subject.json）'); process.exit(1) }
  return ids
}

function writeLegacyRedirect(dstOld, site) {
  const name = path.basename(site.stable_name)
  const msg = `已更名為《${site.name} ${site.version}》`
  const html =
`<!doctype html>
<html lang="zh-Hant"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta http-equiv="refresh" content="0;url=${encodeURIComponent(name)}">
<title>${site.name} ${site.version}</title>
<style>body{margin:0;min-height:100vh;display:flex;align-items:center;
justify-content:center;background:#faf7f2;color:#2b2a26;text-align:center;
font-family:"Microsoft JhengHei","PingFang TC",system-ui,sans-serif;padding:20px}
a{color:#0f766e;font-weight:700}</style></head><body><div>
<p>網站${msg}。</p>
<p><a href="${encodeURIComponent(name)}">如果沒有自動跳轉，點這裡 →</a></p>
</div><script>location.replace(${JSON.stringify(name)});</script></body></html>
`
  fs.writeFileSync(dstOld, html, 'utf8')
}

// ---------------- main ----------------
const site = siteMeta()
const subjects = discoverSubjects().map(loadSubject)
subjects.sort((a, b) => ((a.order ?? 99) - (b.order ?? 99)) || String(a.id).localeCompare(String(b.id)))

const payload = { site, subjects }

// ⚠️ 必須用 split/join 而非 String.replace(字串)：後者只換第一處。
// template.html 裡 /*__SITE_NAME__*/ 有 3 處、/*__SITE_VERSION__*/ 有 3 處，
// 用 replace 會漏掉後面的，頁頭頁尾就直接露出佔位符（畫面整片空白）。
const repAll = (s, from, to) => s.split(from).join(to)

let tpl = fs.readFileSync(path.join(BASE, 'template.html'), 'utf8')
for (const [from, to] of [
  ['/*__SITE_NAME__*/', site.name],
  ['/*__SITE_VERSION__*/', site.version],
  ['/*__SITE_SUBTITLE__*/', site.subtitle]
]) {
  if (!tpl.includes(from)) { console.error(`template.html 缺少佔位符 ${from}`); process.exit(1) }
  tpl = repAll(tpl, from, to)
}
if (/__SITE_(NAME|VERSION|SUBTITLE)__/.test(tpl)) {
  console.error('template.html 仍有未替換的站名佔位符（檢查是否有巢狀 /* 註解把佔位符吃掉）')
  process.exit(1)
}

const exPath = path.join(BASE, 'extras.js')
const exJs = fs.existsSync(exPath) ? fs.readFileSync(exPath, 'utf8') : ''
if (!tpl.includes('/*__EXTRAS_JS__*/')) { console.error('template.html 缺少 /*__EXTRAS_JS__*/ 佔位符'); process.exit(1) }
tpl = repAll(tpl, '/*__EXTRAS_JS__*/', exJs)

const { n: nImg } = inlineBodyImages(payload)

let blob = JSON.stringify(payload)
// 防止 </script> 破壞注入
blob = blob.replace(/<\//g, '<\\/')
if (!tpl.includes('/*__DATA__*/')) { console.error('template.html 缺少 /*__DATA__*/ 佔位符'); process.exit(1) }
const out = repAll(tpl, '/*__DATA__*/', blob)

console.log('科目：')
for (const s of subjects) {
  const st = s.stats
  const flag = s.ready ? '' : '  (內容準備中)'
  console.log(`  ${s.id.padEnd(5)} ${s.title.padEnd(4)} 課題 ${String(st.topics).padStart(2)} · 章節 ${String(st.sections).padStart(3)} · 知識點 ${String(st.points).padStart(3)} · 串連 ${String(st.links).padStart(2)} · 題目 ${String(st.questions).padStart(3)}${flag}`)
}

const dst = path.join(BASE, site.out_name)
fs.writeFileSync(dst, out, 'utf8')
const dstStable = path.join(BASE, site.stable_name)
if (path.resolve(dstStable) !== path.resolve(dst)) fs.writeFileSync(dstStable, out, 'utf8')

const writtenAbs = new Set([path.resolve(dst), path.resolve(dstStable)])
for (const legacy of LEGACY_NAMES) {
  const p = path.join(BASE, legacy)
  if (writtenAbs.has(path.resolve(p))) continue
  writeLegacyRedirect(p, site)
}

const tot = {}
for (const k of ['topics', 'sections', 'points', 'links', 'questions']) tot[k] = subjects.reduce((a, s) => a + s.stats[k], 0)
console.log(`\n合計 課題 ${tot.topics} · 章節 ${tot.sections} · 知識點 ${tot.points} · 串連 ${tot.links} · 題目 ${tot.questions}`)
console.log(`筆記原圖：內嵌 ${nImg} 張`)
console.log(`站名：${site.name} ${site.version}`)
console.log('written:', dst, fs.statSync(dst).size, 'bytes')
console.log('stable :', dstStable, fs.statSync(dstStable).size, 'bytes')
