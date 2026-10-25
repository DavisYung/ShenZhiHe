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

---

## 回答「别人要如何协助我建设神智核」

### 发现的文档谎言

`AGENTS.md` 第 76 行写着 `python scripts/guard_data.py`，
但 `scripts/` 下**根本没有这个文件**。朋友照着文档跑，第一步就报「找不到文件」。
这类「文档说有、实际没有」比没有文档更伤人。

### 补的三样东西

1. **`docs/贡献指南.md`** — 给人看的。按门槛分三档：
   报问题（0 门槛）/ 补内容（只需编辑 JSON）/ 改代码。
   含五分钟上手、三种 JSON 结构、可认领任务清单（带实测数字）、提交与防冲突规则、红线表。

2. **`scripts/guard_data.py`** — 题库守门员。结构校验 + 与 git HEAD 逐字段比对，
   只放行 `explanation`/`explSource`。确需改受保护字段时用 `--allow` 白名单显式声明。
   **它是「保护校对成果」这条铁律的执行者**，此前只有文字约定，没有工具。

3. **`scripts/check_quiz.py`** — 2528 道测验题的结构校验。
   查选项数、答案索引、`point` 是否指向真实知识点、题解是否为空、id 是否重复。

### 守门员上线 5 分钟就抓出 6 处真错

| 题号 | 症状 | 根因 |
|---|---|---|
| `pp_2019_q34` | **48 个选项** | 吞了后面 11 题的选项 |
| `pp_2021_q24` | 8 个选项 | 题干吞 Q25，选项吞 Q25 的 4 个 |
| `pp_2017_q12` | 8 个选项 | 题干吞 Q32 题头，选项吞 Q32 的 4 个 |
| `pp_2013_q11` | 两个 `A` | 选项 A 被 OCR 断成两条 |
| `pp_2016_q35` | 5 个选项 | 混进一条图注碎片 |
| `nuclear1-q9` | 5 个选项 | 出了 5 个安全措施 |

**为什么这些一直没被发现**：前端不截断。`ppCard()` 直接 `opts.map(...)`，
48 个选项就渲染 48 个按钮；`viewQuiz()` 用 `String.fromCharCode(65+idx)`，
第 5 个选项显示成「E」。用户看到的是坏界面，但没人会想到去数选项。

修复方式全部是**最小改动**：截断到 4 项 / 合并断行 / 图注移入题干，
每题改前都 `cp` 了备份，改完 `guard_data.py --allow` 逐项确认。

### 顺带的整理

- `quiz/zz.json`（3 道示例题，挂在不存在的话题上）→ 移到 `docs/examples/quiz-example.json`，
  变成写题模板，不再是错误源。
- CI 加两步：`guard_data.py --no-git` + `check_quiz.py`。
  **注意**：CI 检出的是本次提交本身，工作区与 HEAD 必然一致，
  逐字段比对永远通过，所以 CI 只能做结构校验；字段保护靠本地提交前跑。
- `SHARED-MEMORY.md` 新增 §4.8「吞并邻题」陷阱表，把判定方法写成表格。

### 验证

```
build.py        3,870,691 bytes / V0.18.17 / 2528 题
verify_build    11/11 全绿
guard_data      0 错误（8 项白名单改动已确认）
check_quiz      0 错误 / 5 警告（都是已知的短题解）
```

体积比修前小了 2.5 KB —— 因为删掉了 44 个错误选项和重复选项。
