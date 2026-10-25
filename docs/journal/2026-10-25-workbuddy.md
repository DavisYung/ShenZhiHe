# 2026-10-25 · WorkBuddy AI

## 做了共享记忆的同步基建

### 起因

用户问：「那他们（朋友的 AI）做完的东西，记忆该怎么同步到我这里」。

排查后发现一个根本漏洞：`SHARED-MEMORY.md` 当时放在
`D:\deepseek-harness\default-workspace\`（本地工作区），**不在 git 仓库里**。
朋友 clone 仓库根本看不到这个文件，等于「共享记忆」只在本地两台程序之间共享，
一旦涉及远程协作者就断了。

### 处理

1. **搬进仓库**：`cp SHARED-MEMORY.md f6chem/SHARED-MEMORY.md`
2. **顶部加同步说明**：明确本文件随 git 同步，工作区那份只是存根
3. **§5 变更日志改成「一行摘要 + journal 文件名」**，避免多人追加同一段造成冲突
4. **建 `docs/journal/README.md`**：按人分文件写日志，一人一个文件，天然不冲突
5. **工作区那份改成存根**：写明正式位置、拉取命令、写回流程
6. **`AGENTS.md`**：
   - `../SHARED-MEMORY.md` → 同目录 `SHARED-MEMORY.md`
   - 新增「记忆怎么同步」整节（开工前 pull / 收工后 push 的具体命令）
   - 注明**没有 master 分支**

### 顺手修的仓库卫生

发现协作者 clone 下来会缺数据：`quiz/bio/*.json`（34 个）和
`quiz/phys/energy1-4.json` **从未提交过**，而 `site/build.py` 第 195–305 行
直接读取 `quiz/<sid>/<tid>.json` 作为课题测验题。缺了这些文件，
别人构建出来的站会少 34 个生物课题的测验题，且不会有任何报错。

- 已 `git add` 全部 quiz 数据（1.0 MB）
- `.gitignore` 补忽略：`site/_*.py`、`site/_*.cjs`、`site/_*.png`、
  `site/_screenshot_check/`、`site/archive/`（14 MB 旧版本产物）、
  `e3_src/`（OCR 中间文本）、`scratch/_*.py`、`scratch/ocr_*.txt` 等
- 删掉残留的本地 `master` 分支（之前就是因为它，两个提交错进了 master）

### 验证

```
python site/build.py            → 3,873,179 bytes · V0.18.17 · 2528 题
python scripts/verify_build.py  → 11/11 全绿
git push origin source          → 2ad8b57..334d1c3
```

### 结论 / 经验

- **共享记忆必须在版本库里**，放工作区目录等于没共享。
- **记忆分两层写**：`SHARED-MEMORY.md` 放「结论」，`docs/journal/` 放「过程」。
  只放一个文件的话，要么太短没用，要么太长冲突且没人读。
- **未追踪的数据文件是隐性炸弹**：构建不报错，但产出缺内容。
  以后加 `data/` 或 `quiz/` 下的新文件，记得 `git status` 看一眼有没有漏。
