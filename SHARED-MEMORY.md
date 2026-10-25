# 共享记忆 · WorkBuddy AI ⇄ DSH

> **这是本项目所有协作者（人 + AI 代理）共用的唯一事实来源。**
> 本文件**随 git 同步**：改完 commit & push，别人 `git pull` 就能看到。
> 工作区里 `default-workspace/SHARED-MEMORY.md` 只是指向本文件的存根。
> 改动前先读，改完必须追加记录。
> 建立时间：2026-10-25 22:30 ｜ 最后更新：2026-10-25 22:30 ｜ 当前站点版本：**V0.18.12**

---

## 0. 使用约定（两个代理都必须遵守）

1. **读**：每次动这个项目之前，先读本文件的「§2 现状」与「§4 已知陷阱」。
2. **写**：只追加到「§5 变更日志」，格式固定：
   ```
   ### [YYYY-MM-DD HH:MM] 作者（WorkBuddy / DSH）· 一句话标题
   - 改了什么（文件级）
   - 为什么
   - 验证结果（线上/本地）
   ```
   **不要改写别人写的条目**；要更正就追加一条「更正」。
3. **不要同时构建**。动工前在「§3 占用」写一行 `占用中：<作者> <时间>`，做完删掉。看到别人占用就等。
4. 本文件放在工作区根目录，两个代理都能读写：
   `D:\deepseek-harness\default-workspace\SHARED-MEMORY.md`

---

## 1. 项目一句话

把 DSE 生物卷一 MC（2012–2022）做成可练习的网页题库：按话题/年份浏览、点选项作答、错题自动进错题本、可写笔记、可归档。
线上：<https://nzgjsmy.github.io/ShenZhiHe/>

**仓库结构（2026-10-25 23:45 起）**：同一个仓库两个分支
- `main` = **部署产物**（index.html + img/ + files/ + sw），GitHub Pages 从这里发布，**不要提交源码**
- `source` = **源码**（data/ + site/ + scripts/ + AGENTS.md），所有开发在这里
- 协作者上手：`git clone … && git checkout source`，然后读 `AGENTS.md`
- CI：`.github/workflows/verify.yml` 在 source 分支 push/PR 时跑 `build.py + verify_build.py`，不过不能合并

---

## 2. 现状（每次交付后更新这块）

| 项目 | 值 |
|---|---|
| 站点版本 | V0.18.17 |
| 题库 | 374 / 396 题（2012–2022，缺 22 道多為選項為圖者） |
| 课题分类 | 27 个（bio02–bio29，bio99 已归零） |
| 题解 | **195 / 374**（缺 179） |
| 配图 | 121 张题目图 + 21 张选项图 + 14 张整题原卷图 |
| 数据主档 | `f6chem/data/bio/_pastpaper.json`（≈284 KB） |
| 线上体积 | index.html 3.66 MB（图片外置） |
| 部署包 | `default-workspace/神智核-GitHub部署包`（独立 git 仓库，remote `nzgjsmy/ShenZhiHe`） |

---

## 3. 占用状态

```
（空 = 当前没有人在改）
```

---

## 4. 已知陷阱（血泪，务必先看）

### ⚠️ 4.1 构建脚本：**只用 `build.py`，`build.mjs` 已废弃（转发桩）**

| 脚本 | 语言 | 状态 |
|---|---|---|
| `f6chem/site/build.py` | Python | ✅ **唯一官方构建脚本（canonical）** |
| `f6chem/site/build.mjs` | Node | ⚠️ **已废弃**，现在只把调用转发给 `python build.py` |

**为什么要废弃 build.mjs**：它是 Node 重写版，功能面一直落后，造成过两次线上事故——
① 缺 `_pastpaper` → 真题页整页空白（线上出现过 3.42 MB 无题目版本）；
② 缺 `copyright`/`disclaimer` → 页脚黄条无文字；
③ 仍缺 `__SEARCH_WORKER_URL__`（搜索后台 worker 注入）→ 站内搜索失效。

①② 已于 10-25 22:42 补齐，③ 未补。**与其维护两份实现，不如统一到 build.py。**
`node build.mjs` 现在会打印弃用提示并自动转发，产出与官方完全一致（3,832,031 bytes）。
旧实现备份：`build.mjs.bak-2242`（不要再用，会丢搜索功能）。

### ⚠️ 4.2 图片必须外置

- `build.py` 支持 `EMBED_IMG=1` 把图片转 base64 内嵌 → HTML 从 **3.66 MB 涨到 63 MB**。**默认不要设这个环境变量。**
- 部署目录必须有完整 `img/`（1000+ 张），否则只能内嵌。

### ⚠️ 4.3 部署必须走 `prep_ghpages.py`，且必须同步 `img/`

手工 `cp index.html + service-worker.js` 会漏图片 → 线上新增图全部 404（已发生两次）。
正确流程见 §6。

### ⚠️ 4.4 `SW_VERSION` 必须跟着版本 bump

`service-worker.js` 的 `SW_VERSION` 决定 cache key（`shenzhine-<ver>`）。不 bump → 客户端一直吃旧缓存。
注意：文件注释里也有 `__SW_VERSION__` 字样，判断要精确匹配 `var SW_VERSION = '...'` 那一行。

### ⚠️ 4.5 渲染函数抛异常 = 页面静默卡住

本站是 hash 路由 + `app.innerHTML` 全量重绘。任何渲染函数抛 `ReferenceError`（例如 `escJs` 未定义）都会导致 **`innerHTML` 那行没跑到，画面停在上一帧**，表现为「按钮点了没反应」。
排查顺序：① 目标函数是否存在 ② 依赖函数是否齐全 ③ 再怀疑路径/iframe。

### ⚠️ 4.6 「跳回同一 hash」的按钮会静默失效

`normalizeHash()` 会把 `#/extras/x` 补成 `#/<科目>/extras/x`；如果当前 hash 已经是这个值，浏览器不派发 `hashchange` → 不重绘。要么加子路径，要么直接调渲染函数。

### ⚠️ 4.7 构建后必做语法检查

`build.py` 会把 `template.html` + `extras.js` + 数据注入成单文件，**任何一个 js 语法错都会整站白屏**。每次构建后用 Node 逐块解析：

```js
const blocks=[...html.matchAll(/<script(?![^>]*application\/json)[^>]*>([\s\S]*?)<\/script>/g)];
blocks.forEach(b=>new vm.Script(b[1]));   // 抛错即语法错
```

---

## 5. 变更日志（只追加）

> **多人协作时**：不要都往这一节追加（会 git 冲突）。
> 每人/每个 AI 在 `docs/journal/<日期>-<名字>.md` 写自己的详细日志，
> 只在这里留**一行摘要 + 文件名**。单人时可直接写在这里。



### [2026-10-25 22:30] WorkBuddy · 建立共享记忆文件
- 新建本文件，整合双方各自的导出文档（`神智核-工作记忆-20261025.md` / `...-DSH.md`）。
- 记录 §4.1 的重大发现：`build.mjs` 缺 `_pastpaper`，解释了 17:44 那次「真题全没了」。

### [2026-10-25 17:44] DSH · 部署（事后记录）
- 用 `node build.mjs` 构建并推送，index.html 3.42 MB。
- **后果**：payload 里没有 `bio._pastpaper`，线上真题页空白；`site.copyright` / `disclaimer` 也缺失，页脚黄条无文字。
- 原因见 §4.1。

### [2026-10-25 18:00–22:25] WorkBuddy · V0.17.1 → V0.18.12 连续迭代
- 修体积（63 MB → 3.66 MB）、修页脚、修 extras 档名繁简、修 `escJs` 未定义、修返回按钮 hash 死锁。
- 真题练习化：话题筛选、ABCD 可点作答、错题本（已整理 + 笔记）。
- 数据治理：OCR 补齐 42 题、翻译 2022 英文卷 8 题、校对 23 题错字、13 题改原卷图、分类复查改 63 道。
- 详见 `神智核-DSE真题-工作记忆-20261025.md`（12.4 KB）。

### [2026-10-25 22:42] WorkBuddy · 给 build.mjs 补齐 `_pastpaper` 与版权字段
- 改 `f6chem/site/build.mjs`（备份 `build.mjs.bak-2242`）：
  ① `loadSubject()` 增加读取 `_pastpaper.json` 并挂到 `subject._pastpaper`；
  ② `siteMeta()` 增加 `copyright` / `disclaimer` 两个字段。
- 为什么：build.mjs 缺这两块 → 用它构建会丢全部真题、页脚版权空白（线上曾发生）。
- 验证：`node build.mjs` 产物 374 题、copyright ✓、免责 7 条、脚本 3/3；再用 `python build.py` 恢复 canonical 产物（3.65 MB）。
- 按 §7 分工，build.mjs 属 DSH 区域，本次为「防回归」跨区修改，已在此登记。

### [2026-10-25 22:48] WorkBuddy · 废弃 build.mjs，改为转发到 build.py
- 功能比对结论：`build.py` 是超集（含 `__SEARCH_WORKER_URL__` 搜索 worker、`LEGACY_NAMES` 旧档名转址、图片外置、extras、quiz）；
  `build.mjs` 仍缺搜索 worker 注入。
- 处理：`build.mjs` 改写为转发桩（打印弃用原因 → `spawnSync` 调 `python build.py` → 透传退出码；找不到 Python 则报错退出 1）。
- 验证：`node build.mjs` 输出 3,832,031 bytes，与 `python build.py` 完全一致；`_pastpaper` 374 题、copyright ✓、免责 7 条、搜索 worker ✓、脚本 3/3。
- 用户与 DSH 双方同意此方案。


### [2026-10-25 22:52] 双方 · 记忆互通验证通过
- 用户实测：DSH 能读到本文件并正确转述 §4.1（构建脚本）、§7（分工）、§3（并发占用）。
- DSH 已把本文件指针写入其长期记忆 `~/.dsh/memories/projects/05c95bcf1d81/KEY.md`；WorkBuddy 写在 `.workbuddy-ai/memory/MEMORY.md`。
- 另补：DSH 的 KEY.md 增加了一条「使用规约」（§3/§5/分工），确保后续会话知道操作规则而不只是「文件存在」。

### [2026-10-25 23:00] WorkBuddy · V0.18.13 题解第二批（酶和新陳代謝）
- 写 16 道逐选项题解（`expl_bio04.py`），涵盖温度/pH、代谢类型配对、活性部位、酶是蛋白质、对照实验设计、自变量与控制变量、分泌途径。
- 顺带修正 2013 Q5 误归：膜蛋白功能题 bio04 → bio03（并补题解）。
- 全站题解 114 → 131。线上验证：V0.18.13、脚本 3/3、374 题、搜索 worker ✓、copyright ✓。
- 仍缺：243 题（含 2018 Q3 题干空、2019 Q9 缺陈述，需先补数据）。

### [2026-10-25 23:05] WorkBuddy · 新增 §9 题解写作规范 + 覆盖率脚本（交接准备）
- 新增 `f6chem/site/_expl_coverage.py`：`--topic` 看单课题缺哪些、`--check` 校验（过短/缺 explSource/整题图无提示）。
- SHARED-MEMORY 新增 §9：字段规范、写作模板、质量红线（有图不许编、答案冲突以官方为准、无信息就跳过）、改完五步。
- 目的：WorkBuddy 额度用完后，DSH 可无缝接手写题解，不用重新摸索写法。


### [2026-10-25 23:20] WorkBuddy · V0.18.14 题解第三、四批（25 题）
- 物质穿越细胞膜 5、生命的基本单位 2、人体气体交换 8、植物营养 5、体内平衡 4、生物工程 1。
- 修 2015 Q15 题干误并 2020 Q11 整题（又一个「年份+题号」标题未识别的串题）。
- 全站题解 131 → 156。**注意**：依赖图表才能判断的题（如 2019 Q5、2022 Q30/Q32/Q33、2012 Q12）暂缓，需读原卷图再写。

### [2026-10-25 23:30] WorkBuddy · V0.18.15 题解第五批（读图后撰写 6 题）
- 2012 Q8/Q9 眼球构造（P=巩膜、U/S=睫状体、T=晶状体、Q=视网膜、R=视神经）、2012 Q10 水下切枝防气泡、2012 Q16 碳循环流向、2013 Q27 视锥/视杆、2014 Q31 捕食者判定。
- 全站题解 156 → 162。
- **经验**：读一张图可写 1–2 题，但很多「有图」题其实靠原理就能写（如图中只是装置示意图），不必读图。

### [2026-10-25 23:40] WorkBuddy · V0.18.16 修正眼球标注
- 2012 Q8/Q9 题解里把 **U 误认为睫状体**，用户校对指出 U＝**虹膜**；经确认 S＝睫状体、T＝晶状体。
- 已改正并部署。**教训：读原卷图认标注容易出错（线条指向相邻结构），写完最好让用户抽查一两条认图题。**

### [2026-10-25 23:55] WorkBuddy · V0.18.17 题解第六、七批（33 题）
- 植物蒸腾 10、生长和发育 6、环境状况的探测 5、人体的协调 10。
- 全站题解 162 → 195。
- 经验：**「有图」不等于「必须读图」**——装置示意图类的题靠原理即可作答；真正要读图的是「从图上读数/认标注/比曲线」那类。

### [2026-10-25 23:45] WorkBuddy · 建立 source 分支 + CI + AGENTS.md（多人/多 AI 协作基建）
- 新增 `f6chem/AGENTS.md`：给 AI 协作者自动读取的硬约束（只用 build.py、不手改产物、禁内嵌图片、部署带 img、_pastpaper 只改两个字段）。
- 新增 `f6chem/scripts/verify_build.py`：11 项构建自检（体积/真题数/版权/搜索 worker/脚本语法/图片引用/SW 版本/build.mjs 桩），退出码可直接当 CI 门禁。**写完立刻抓到 2 个问题**（1 个是我自己的检查写错、1 个是真错）。
- 新增 `.github/workflows/verify.yml`：source 分支 push/PR 自动 build + verify。
- 补齐 632 张此前未纳入版本控制的笔记图片（clone 后可直接构建）；.gitignore 排除内嵌 Python 运行时与备份档。
- 推送 `source` 分支（2ad8b57），`main` 保持 aec21d7 未动，线上 200。
- **踩坑**：`git branch -f source master` 后仍停留在 master，后续提交进了 master → 远程 source 落后一版。教训：建分支后要 `git checkout`，或直接用 `git push origin master:source`。

### [2026-10-26 00:05] WorkBuddy · 共享记忆入仓 + 补齐 quiz 数据（记忆同步闭环）
- **修复根本漏洞**：`SHARED-MEMORY.md` 原在 `default-workspace/`（本地），**不在仓库里**，协作者 clone 看不到 → 已搬进仓库根目录，随 git 同步；工作区那份改为存根。
- 建 `docs/journal/` 按人分文件写日志，§5 从此只留「一行摘要 + journal 文件名」，避免多人冲突。
- **补齐隐性缺失数据**：`quiz/bio/*.json`（34 个）与 `quiz/phys/energy1-4.json` 从未提交，而 `build.py` 直接读取 → 别人构建会静默少 34 个生物课题测验题。已全部入库（1.0 MB）。
- `.gitignore` 补忽略 `site/_*.py`、`site/archive/`（14 MB 旧产物）、`e3_src/`、`scratch/_*.py` 等中间物，未追踪文件从 160+ 降到 0。
- 删除残留本地 `master` 分支（之前错提交的根源）；`AGENTS.md` 注明「没有 master 分支」并新增「记忆怎么同步」整节。
- 验证：`build.py` → 3,873,179 bytes / V0.18.17 / 2528 题；`verify_build.py` → 11/11 全绿；推送 `334d1c3`。
- 详见 `docs/journal/2026-10-25-workbuddy.md`。

---

## 6. 标准流程（照抄即可）

```bash
# 0) 备份数据
cd f6chem/data/bio && cp _pastpaper.json "_pastpaper.json.bak-$(date +%H%M)"

# 1) 改源码：data/*.json + site/template.html（不要手改 神智核.html）
# 2) 构建（★ 用 build.py，不要用 build.mjs）
cd f6chem/site && python build.py
#    构建后做语法检查（见 §4.7）

# 3) 准备部署目录（沙箱不允许批量删除时加 NO_WIPE=1）
NO_WIPE=1 python prep_ghpages.py

# 4) 同步到 git 部署包（★ 一定要带 img/）
cd /d/deepseek-harness/default-workspace
cp f6chem/gh-pages/index.html        "神智核-GitHub部署包/index.html"
cp f6chem/gh-pages/service-worker.js "神智核-GitHub部署包/service-worker.js"
cp -rn f6chem/gh-pages/img/.         "神智核-GitHub部署包/img/"

# 5) 推送
cd "神智核-GitHub部署包"
git add -A && git commit -m "V0.xx.x：说明" && git push origin main

# 6) 验收（60–90 秒后）
curl -s https://nzgjsmy.github.io/ShenZhiHe/service-worker.js | grep SW_VERSION
```

---

## 7. 分工建议（减少冲突）

| 区域 | 建议归属 | 说明 |
|---|---|---|
| `data/bio/_pastpaper.json`（题库内容） | **WorkBuddy** | 题库解析、题解、分类 |
| `site/template.html` 的 DSE 真題区 | **WorkBuddy** | `viewPastPaper` / `ppCard` / 错题本 |
| `site/extras.js`、`extras/*` | **DSH** | 额外资讯、公式表等 |
| `_mk_pkg.py` | **DSH** | 打包工具链（build.mjs 已废弃为转发桩） |
| `site/build.py`、`prep_ghpages.py` | **共同，改动需在此登记** | 影响面最大；build.py 为唯一构建入口 |

> 谁要动别人的区域，先在本文件 §3 登记占用，并在 §5 说明原因。

---

## 8. 待办

- [ ] 题解：补 260 题（19 个课题）。写法：先讲正确答案理由 → 再逐项说错在哪 → 计算/图表题补关键判据。
- [ ] 缺 22 道题（多為選項為圖片、OCR 取不到文字），目前用原卷图代替。
- [x] ~~build.mjs 补齐 `_pastpaper`~~（10-25 22:42）
- [x] ~~比对两者功能面~~（10-25 22:48：build.py 为超集）→ **build.mjs 已废弃为转发桩**
- [ ] 年份排序：现为升序，可考虑加「↑↓」切换。

---

## 9. 題解寫作規範（誰接手都照這個來）

> 本節是給「繼續補題解」的人或代理看的。照做就不會走彎路。

### 9.1 只看兩個欄位

在 `data/bio/_pastpaper.json` 的每道題裡，**只改這兩個欄位**，其餘（`q`/`options`/`answer`/`img`/`optImg`/`qImg`/`topic`/`pct`）**一律不要動**：

```jsonc
"explanation": "題解正文（markdown）",
"explSource": "notes"        // 固定寫 "notes"，UI 會顯示「依筆記整理」標籤
```

### 9.2 寫作模板

```
先講【為什麼答案是 X】→ 再逐項說明【其餘選項錯在哪】→（計算/圖表題）補一句關鍵判據
```

實際樣例（2016 Q27，問「哪項不正確」）：

```
本題問「不正確」的一項。
- **A 對**：酶由細胞（核糖體）製造。
- **B 不正確（答案）**：「極端溫度」包含低溫與高溫；低溫只令酶不活躍、結構未破壞，
  升溫後可恢復，不算變性。變性只發生在高溫、強酸、強鹼。
- **C 對**：不同酶若活性部位形狀相似，可催化同一反應。
- **D 對**：酶具專一性，相同底物經同一酶催化，產物相同。
```

要點：
- 用 `**粗體**` 標出關鍵詞（站內 `mdLite` 支援粗體、清單、表格）
- 選項多時逐項列，選項少（如「只有 (1) 和 (2)」型）就解釋**每個陳述為何對/錯**
- 計算題把算式寫出來（例：脂肪 3.5×9＝31.5 千卡）

### 9.3 質量紅線

| 情況 | 正確做法 |
|---|---|
| 題目有圖、你看不到圖 | 寫「依圖示判斷」，**不要編造圖中的具體數字/形狀** |
| 題幹是 OCR 還原、可能有錯字 | 只在你能確定時解釋；不確定就寫「此題文字可能有誤，請對照原卷」 |
| 答案與你的推理衝突 | **以官方答案為準**，然後在題解裡說明為什麼（不要改 answer） |
| 完全沒有資訊（如 2018 Q3 題幹空） | 跳過，不要硬寫 |

### 9.4 進度自查

```bash
cd f6chem/site
python _expl_coverage.py              # 全站 + 各課題覆蓋率
python _expl_coverage.py --topic bio10   # 某課題還缺哪幾題（含答案與答對率）
python _expl_coverage.py --check      # 校驗：過短、缺 explSource、整題圖無提示
```

當前進度（2026-10-25 23:00）：**131 / 374**。

| 已做完 | 課題 |
|---|---|
| ✅ 100% | 細胞週期和分裂 27、人的生殖 3、呼吸作用 11、非傳染病 9、傳染病和疾病的預防 3、身體的防禦機制 4 |
| 🔶 大半 | 人的營養 29/30、酶和新陳代謝 18/20、人體的運動 10/11、有花植物的生殖 6/7 |
| ⬜ 待做 | 生態系 27、基礎遺傳學 29、植物的蒸騰 27、人體內物質的轉運 26、光合作用 19、環境狀況的探測 16、人體的協調 16、生長和發育 15、分子遺傳學 14、人體的氣體交換 12、植物的營養 11、生物多樣性 10、進化I 6、生命的基本單位 5、體內平衡 5、物質穿越細胞膜 10（已 4）、生物工程 1 |

### 9.5 改完必做

1. 備份：`cd data/bio && cp _pastpaper.json _pastpaper.json.bak-$(date +%H%M)`
2. 校驗：`python _expl_coverage.py --check`
3. 構建：`cd site && python build.py`（**不要用 build.mjs**），再按 §4.7 逐塊檢查腳本語法
4. 部署：按 §6 六步（**別忘了 `cp -rn .../img/.`**）
5. 回寫：更新本文件 **§2 現狀**（題解數字）與 **§5 變更日誌**
