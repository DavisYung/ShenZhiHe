// build.mjs —— ⚠️ 已废弃（2026-10-25），本文件现在只做「转发」。
//
// 为什么废弃：本文件是 build.py 的 Node 重写版，但功能面一直落后，曾造成线上事故：
//   ① 缺 `_pastpaper`（真题数据）→ 用它构建，DSE 真题页整页空白（线上出现过 3.42MB 无题目版本）
//   ② 缺 `copyright` / `disclaimer` → 页脚「版權與免責聲明」黄条无文字
//   ③ 缺 `__SEARCH_WORKER_URL__`（搜索后台 worker 注入）→ 站内搜索失效
// ① ② 已于 2026-10-25 22:42 补齐，③ 仍未补；与其维护两份实现，不如统一到 build.py。
//
// 现在的行为：直接调用 `python build.py`，产出与官方构建完全一致。
// 想强制用旧实现请改回 build.mjs.bak-2242，但那会丢失搜索功能。
//
// 详见 ../SHARED-MEMORY.md §4.1
import { spawnSync } from 'child_process'
import path from 'path'
import url from 'url'

const BASE = path.dirname(url.fileURLToPath(import.meta.url))

console.warn('')
console.warn('⚠️  build.mjs 已废弃 → 正在转发到 python build.py')
console.warn('    原因：本文件缺少搜索后台 worker 注入（__SEARCH_WORKER_URL__），')
console.warn('          且曾因缺 _pastpaper / copyright 造成真题页空白与页脚无字。')
console.warn('    请改用：cd f6chem/site && python build.py')
console.warn('    说明：../SHARED-MEMORY.md §4.1')
console.warn('')

const candidates = [
  process.env.PYTHON,
  'python',
  'python3',
  'py',
].filter(Boolean)

let lastErr = null
for (const bin of candidates) {
  const r = spawnSync(bin, ['build.py'], { cwd: BASE, stdio: 'inherit' })
  if (r.error) { lastErr = r.error; continue }
  process.exit(r.status === null ? 1 : r.status)
}

console.error('✖ 找不到 Python 解释器，无法转发。请手动执行：')
console.error('    cd f6chem/site && python build.py')
if (lastErr) console.error('  （最后错误：' + lastErr.message + '）')
process.exit(1)
