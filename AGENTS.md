# AGENTS.md — 给 AI 协作者的项目约定

> 你（AI 代理）在这个仓库工作前，**必须先读**本文件和 `SHARED-MEMORY.md`。
> 本文件是硬约束，不是建议。违反会导致线上故障（已经发生过多次）。


## 如何开始（协作者 / AI 代理）

```bash
git clone https://github.com/nzgjsmy/ShenZhiHe.git
cd ShenZhiHe
git checkout source          # ★ 必须切到 source，main 只有部署产物
python site/build.py         # 首次构建
python scripts/verify_build.py   # 应全绿
```

> **main 分支 = 已构建的网站**（GitHub Pages 从这里发布），**不要往 main 提交源码**。
> **source 分支 = 源码**，所有开发都在这里。

提交前：

```bash
python site/build.py && python scripts/verify_build.py   # 全绿
git add -A && git commit -m "说明" && git push
```

CI（`.github/workflows/verify.yml`）会在 source 分支的每次 push / PR 上自动跑
`build.py + verify_build.py`，**不通过就无法合并**。

## 这是什么项目

DSE 生物/化学/物理/数学笔记整合站「神智核」。单文件离线网站，由 `site/build.py` 把
`data/**/*.json` + `site/template.html` + `site/extras.js` 注入成一个 HTML。

```
f6chem/
├─ data/<sid>/*.json      ← 内容数据（bio/chem/phys/math）
├─ data/bio/_pastpaper.json ← DSE 真题题库（下划线开头，不被当作课题加载）
├─ site/template.html     ← 前端模板（含 DSE 真题视图、错题本）
├─ site/extras.js         ← 额外资讯页逻辑
├─ site/build.py          ← ★ 唯一构建入口
├─ site/prep_ghpages.py   ← 生成部署目录 gh-pages/
├─ site/img/              ← 所有图片（外置，不内嵌）
└─ 神智核.html            ← 构建产物，**不要手改**
```

## 铁律（违反会直接出事）

1. **构建只用 `python site/build.py`**
   `site/build.mjs` 已废弃，现在只是转发桩（会打印提示后调用 build.py）。
   **不要恢复它的实现**——它缺 `_pastpaper`（真题数据）和 `__SEARCH_WORKER_URL__`（搜索 worker）。

2. **绝不手改 `site/神智核.html`**
   它是产物。改内容 → 改 `data/` 或 `site/template.html` → 重新构建。

3. **不要设 `EMBED_IMG=1`**
   那会把图片转成 base64 内嵌，HTML 从 3.8 MB 涨到 63 MB，线上加载会崩。

4. **部署必须带图片**
   只复制 `index.html` + `service-worker.js` 会漏图 → 新增图片全部 404（已发生两次）。

5. **改版必须 bump `site/version.json` 的 version**
   `service-worker.js` 的缓存键是 `shenzhine-<version>`，不 bump 客户端会一直用旧缓存。

6. **`data/bio/_pastpaper.json` 只允许改 `explanation` 和 `explSource`**
   其余字段（`q`/`options`/`answer`/`topic`/`pct`/`img`/`optImg`/`qImg`/`ocr*`）已人工校对过，
   **任何"顺手优化"都会破坏已校对的内容**。写完题解跑 `scripts/guard_data.py` 自检。

## 常用命令

```bash
python site/build.py                      # 构建
python scripts/verify_build.py            # ★ 构建后自检（必须全绿）
NO_WIPE=1 python site/prep_ghpages.py     # 生成部署目录
python site/_expl_coverage.py             # 题解覆盖率（--topic bioNN / --check）
python scripts/guard_data.py              # 检查题库只改了允许的字段
```

## 改完必须做

1. `python site/build.py` → `python scripts/verify_build.py`（全绿才算完成）
2. 部署按 `SHARED-MEMORY.md` §6 六步（**别忘 `cp -rn gh-pages/img/. 部署包/img/`**）
3. 往 `SHARED-MEMORY.md` **§5 变更日志**追加一条（带作者、时间、验证结果）
4. 更新 §2 现状（版本号、题数、题解数）

## 已知陷阱（详细版见 SHARED-MEMORY.md §4）

| 陷阱 | 后果 |
|---|---|
| 用 build.mjs 构建 | 真题页整页空白（缺 `_pastpaper`） |
| 内嵌图片 | HTML 63 MB |
| 部署漏 `img/` | 新增图 404 |
| SW_VERSION 没 bump | 客户端吃旧缓存，用户看不到更新 |
| 渲染函数抛异常 | 页面**静默停在上一帧**，表现为「按钮没反应」 |
| 用 `go()` 跳到当前相同 hash | 不触发 hashchange，不重绘 |

## 协作

- 多人/多 AI 同时改时，先读 `SHARED-MEMORY.md` **§3 占用**，动工前登记，做完删掉。
- 分工：题库与真题视图归 WorkBuddy；`extras/*`、`_mk_pkg.py` 归 DSH。
- 有疑问先看 §4 陷阱表，90% 的坑都记在那里。
