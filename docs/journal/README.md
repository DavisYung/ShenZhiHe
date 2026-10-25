# 协作日志（docs/journal/）

**为什么按人分文件**：多人/多 AI 同时往 `SHARED-MEMORY.md §5` 追加会 git 冲突。
这里每人每天一个文件，**只追加、永不冲突**，合并时最多是新增文件。

## 怎么用

新建 `docs/journal/<YYYY-MM-DD>-<你的名字或代理名>.md`，每次做完一件事追加：

```markdown
## 14:30 修好了真题页图片 404
- 改了什么：`site/prep_ghpages.py` 增加 img/pp 收集
- 为什么：新增配图没被复制到部署目录
- 验证：`python scripts/verify_build.py` 全绿；线上 img/pp/2019/f27.webp 200
```

然后在 `SHARED-MEMORY.md` **§2 现状**里更新数字（版本号、题数、题解数），
在 **§5** 留一行摘要（`- 2026-10-25 14:30 <名字>：一句话 + 本文件名`）。

## 我这边怎么同步

```bash
git checkout source && git pull
```

就这样。`SHARED-MEMORY.md` 和 `docs/journal/` 都是普通文件，pull 下来就是最新的。
