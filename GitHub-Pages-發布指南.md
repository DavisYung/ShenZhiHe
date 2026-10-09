# 發布到 GitHub Pages · 完整步驟

发布后你会得到一个网址，像 `https://你的用户名.github.io/f6chem/`，
**手机电脑平板随时开，不用电脑开着，进度各设备独立保存**。

我已经把要发布的东西全部准备好了，你只需要上传。

---

## 你要准备的

- 一个 GitHub 账号（没有就去 <https://github.com/signup> 免费注册）
- 一个浏览器

---

## 方式一：网页上传（最简单，推荐第一次用）

### 第 1 步 · 建一个新仓库

打开 <https://github.com/new>

| 填什么 | 填什么 |
|---|---|
| Repository name | `f6chem` |
| Description | 随便写，比如 `F6 化學筆記整合網` |
| Public / Private | 选 **Public**（Pages 免费版只支持公开仓库） |
| 勾选 | `Add a README file` ✅ |
| License | 随便选或不选 |

点 **Create repository**

### 第 2 步 · 上传文件

在仓库页面点 **Add file** → **Upload files**

> ⚠️ 这里有个小坑：`gh-pages\.nojekyll` 以点开头，在网页上传时可能传不上去。
> 没关系，**没有它也照样能用**（我们的文件没有 `_` 开头的名字）。

把这两个文件拖进去：

```
f6chem\gh-pages\index.html
f6chem\gh-pages\README.md
```

（`404.html` 可选，不传也行）

上传完点 **Commit changes**

### 第 3 步 · 开启 Pages

1. 仓库顶栏点 **Settings**（Settings）
2. 左边菜单点 **Pages**
3. **Source** 下拉选 **Deploy from a branch**
4. **Branch** 选 **main**，目录选 **/ (root)**
5. 点 **Save**

### 第 4 步 · 等 1-3 分钟

页面会刷新，然后显示：

```
Your site is live at https://你的用户名.github.io/f6chem/
```

**打开这个网址，能看到笔记网站就成了** 🎉

---

## 方式二：Git 命令行（更快，以后更新方便）

### 第 1 步 · 建仓库
同方式一的第 1 步，但**不要勾** Add a README。

### 第 2 步 · 管理员 PowerShell 里执行

> 建议在 `C:\Users\guomi\OneDrive\文件\deepseek-harness\default-workspace\f6chem\gh-pages` 目录执行

```powershell
cd "C:\Users\guomi\OneDrive\文件\deepseek-harness\default-workspace\f6chem\gh-pages"

git init
git add index.html README.md 404.html
git config user.name "你的名字"
git config user.email "你的邮箱@example.com"
git commit -m "F6 化學筆記整合網"
git branch -M main
git remote add origin https://github.com/你的用户名/f6chem.git
git push -u origin main
```

推送时会要你输入 GitHub 密码 —— **密码位置要填 Personal Access Token，不是登录密码**：

1. 点 GitHub 头像 → **Settings**
2. 最下面左侧 **Developer settings**
3. **Personal access tokens** → **Tokens (classic)** → **Generate new token (classic)**
4. 勾选 `repo`（和 `gist` 随便），Expiration 选个时间
5. 生成后**复制那串 token**，它只显示一次
6. 粘贴时终端不会显示字符，是正常的，粘完直接回车

### 第 3 步 · 开启 Pages
同方式一的第 3、4 步。

---

## 更新内容后怎么重新发布

```powershell
cd "C:\Users\guomi\OneDrive\文件\deepseek-harness\default-workspace\f6chem\site"
& "C:\Users\guomi\.dsh\dsh-runtimes\dsh-primary-runtime\dependencies\python\python.exe" prep_ghpages.py
& "C:\Users\guomi\.dsh\dsh-runtimes\dsh-primary-runtime\dependencies\python\python.exe" build.py

cd ..\gh-pages
git add index.html
git commit -m "更新筆記內容"
git push
```

等 1-2 分钟，网址上的内容就更新了。

---

## 手机上怎么用

1. 打开 `https://你的用户名.github.io/f6chem/`
2. Safari 底部「分享」→「添加到主屏幕」
3. 桌面出现图标，以后点它就行

**好处**：不用电脑开着，出门也能用。

**要注意的**：进度存在**每个设备各自的浏览器**里。
- 手机做的题，iPad 上看不到
- 如果想接上，可以用 Safari 的 iCloud 同步书签功能，或我帮你加「导出/导入进度」功能

---

## 常见问题

**Q: 网址显示 404？**
A: Pages 还没部署完（等 1-3 分钟），或者 Settings → Pages 里 Source 没选对。

**Q: 上传时提示文件太大？**
A: GitHub 单文件限制 100 MB，我们只有 572 KB，没问题。

**Q: 想用自定义域名？**
A: Settings → Pages → Custom domain 填你的域名，需要先在域名服务商那边加 CNAME 记录。

**Q: 会被公开吗？**
A: 会。Public 仓库的内容谁都能看到 —— 但这是你自己的学习笔记，无所谓对吧 😄
如果你想改成用 GitHub 私有仓库 + Cloudflare Pages，可以跟我说。

---

## 文件清单（我已验证过能用）

| 文件 | 大小 | 作用 |
|---|---|---|
| `index.html` | 572.6 KB | 整个网站（11 課題 / 597 知識點 / 375 題 / 89 串連） |
| `README.md` | 0.6 KB | 说明 |
| `404.html` | 0.9 KB | 访问不存在的页面时的友好提示 |
| `.nojekyll` | 0 B | 让 GitHub 原样发布（网页上传可能传不上，无妨） |

**已验证**：13 项浏览器断言全 PASS、0 外部依赖、597 知识点 100% 带原 PDF 页码。
