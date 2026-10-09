// 用 src/*.ts 直接跑修复管线（Node 24 原生类型剥离）
import { createHash } from 'node:crypto'
import { readFileSync } from 'node:fs'
import { pathToFileURL } from 'node:url'

const PLUGIN = 'C:/Users/guomi/OneDrive/文件/deepseek-harness/default-workspace/f6chem/scratch/genui-src'
const repair = await import(pathToFileURL(PLUGIN + '/shared/fence-repair.ts').href)
const { repairFenceJson, completeFenceJson, isCompleteJson, describeJsonFailure } = repair
console.log('fence-repair.ts loaded:', Object.keys(repair).join(', '))

let resolve = null
try {
  resolve = await import(pathToFileURL(PLUGIN + '/shared/fence-resolve.ts').href)
  console.log('fence-resolve.ts loaded:', Object.keys(resolve).join(', '))
} catch (e) {
  console.log('fence-resolve.ts load failed:', e.message)
}

const raw = readFileSync('C:/Users/guomi/OneDrive/文件/deepseek-harness/default-workspace/f6chem/scratch/failing_fence.json', 'utf8')
console.log('\nfingerprint(session recorded) = 39337636e5b8')
console.log('fingerprint(reconstruction)   =', createHash('sha256').update(raw.trim()).digest('hex').slice(0, 12))

console.log('\n[case A] 本会话失败围栏（"gap 键缺左引号）')
console.log('  isCompleteJson:', isCompleteJson(raw))
console.log('  describeJsonFailure:', describeJsonFailure(raw))
const t1 = repairFenceJson(raw)
console.log('  tier-1:', t1 ? `repaired=${t1.repairs}` : 'null ❌ 无法修复')
const t2 = completeFenceJson(raw)
console.log('  tier-2:', t2 ? `repaired=${t2.repairs}` : 'null ❌ 无法修复')

console.log('\n[case B] 最小复现 {"title":"x", gap":16, "items":[]}')
const min = '{"title":"x", gap":16, "items":[]}'
console.log('  tier-1:', JSON.stringify(repairFenceJson(min)))
console.log('  tier-2:', JSON.stringify(completeFenceJson(min)))

console.log('\n[case C] 各类常见错法扫描')
const cases = {
  'trailing comma': '{"title":"x", "items":[],}',
  'quote inside value': '{"title":"对"别名"失败", "items":[]}',
  'missing closing brace': '{"title":"x", "items":[{"type":"list"}]',
  'key missing LEFT quote': '{"title":"x", gap":16}',
  'key missing both quotes': '{"title":"x", gap:16}',
  'wrong closer ]→}': '{"title":"x", "items":[{"type":"stat","label":"a","value":1}}',
  'key quote on wrong side': '{"title":"x, "gap":16}',
  'chinese quote key': '{"title":"x", 「gap」:16}',
  'single quotes': "{'title':'x','items':[]}",
  'unquoted key (js)': '{title:"x", items:[]}',
}
for (const [name, body] of Object.entries(cases)) {
  const r1 = repairFenceJson(body)
  const r2 = completeFenceJson(body)
  console.log(`  ${name.padEnd(24)} tier1=${r1 ? 'OK' : 'fail'}  tier2=${r2 ? 'OK' : 'fail'}`)
}

if (resolve) {
  console.log('\n[case A] resolveFence(settled=true):')
  const r = resolve.resolveFence(raw, { settled: true })
  console.log('  spec:', r.spec === null ? 'null → render_failed' : 'renderable ✅')
}
