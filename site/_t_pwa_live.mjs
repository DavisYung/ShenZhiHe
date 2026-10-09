/* PWA 端到端实测（真实 Chrome + CDP over WebSocket）
 *
 * 静态检查证明不了 PWA 真能用，这里实际验证：
 *   1. Service Worker 注册成功且进入 activated
 *   2. Cache Storage 里确实存下了 index.html 与图标
 *   3. **断网后仍能打开页面**（离线可用）—— 核心承诺
 *   4. manifest 被浏览器解析，图标可加载
 *
 * 用法: node _t_pwa_live.mjs <包目录>
 * 前置: 本脚本自带静态服务器，模拟 GitHub Pages 子路径 /仓库名/。
 */
import http from "node:http";
import fs from "node:fs";
import path from "node:path";
import { spawn } from "node:child_process";
import os from "node:os";

const PKG = path.resolve(process.argv[2] || ".");
const REPO = "shenzhine";
const PORT = 8771;
const CDP_PORT = 9341;
const CHROME = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe";

const results = [];
function check(name, ok, detail = "") {
  results.push({ name, ok, detail });
  console.log((ok ? "  PASS  " : "  FAIL  ") + name + (detail ? "   " + detail : ""));
}

const MIME = {
  ".html": "text/html; charset=utf-8",
  ".json": "application/manifest+json",
  ".js": "application/javascript",
  ".png": "image/png",
  ".ico": "image/x-icon",
};

/* 静态服务器：模拟 /仓库名/ 子路径 */
function startServer() {
  const srv = http.createServer((req, res) => {
    const urlPath = decodeURIComponent(req.url.split("?")[0]);
    const prefix = "/" + REPO + "/";
    let rel = null;
    if (urlPath.startsWith(prefix)) rel = urlPath.slice(prefix.length);
    else if (urlPath === "/" + REPO) rel = "index.html";
    if (rel === "" || rel === null) rel = rel === null ? null : "index.html";
    if (rel === null) {
      res.writeHead(404);
      res.end("not found");
      return;
    }
    const target = path.join(PKG, rel);
    if (fs.existsSync(target) && fs.statSync(target).isFile()) {
      const data = fs.readFileSync(target);
      res.writeHead(200, {
        "Content-Type": MIME[path.extname(target)] || "application/octet-stream",
        "Content-Length": data.length,
        // SW 需要正确的 scope 头；同源根部署时无需 Service-Worker-Allowed
      });
      res.end(data);
    } else {
      res.writeHead(404);
      res.end("not found");
    }
  });
  return new Promise((resolve) => srv.listen(PORT, "127.0.0.1", () => resolve(srv)));
}

/* 极简 CDP 客户端 */
class CDP {
  constructor(ws) {
    this.ws = ws;
    this.id = 0;
    this.pending = new Map();
    this.events = [];
    ws.addEventListener("message", (ev) => {
      const msg = JSON.parse(ev.data);
      if (msg.id && this.pending.has(msg.id)) {
        const { resolve, reject } = this.pending.get(msg.id);
        this.pending.delete(msg.id);
        if (msg.error) reject(new Error(JSON.stringify(msg.error)));
        else resolve(msg.result);
      } else if (msg.method) {
        this.events.push(msg);
      }
    });
  }
  send(method, params = {}, sessionId) {
    const id = ++this.id;
    const payload = { id, method, params };
    if (sessionId) payload.sessionId = sessionId;
    this.ws.send(JSON.stringify(payload));
    return new Promise((resolve, reject) => {
      this.pending.set(id, { resolve, reject });
      setTimeout(() => {
        if (this.pending.has(id)) {
          this.pending.delete(id);
          reject(new Error("CDP timeout: " + method));
        }
      }, 60000);
    });
  }
}

async function getWsUrl() {
  for (let i = 0; i < 60; i++) {
    try {
      const r = await fetch(`http://127.0.0.1:${CDP_PORT}/json/version`);
      const j = await r.json();
      if (j.webSocketDebuggerUrl) return j.webSocketDebuggerUrl;
    } catch {}
    await new Promise((r) => setTimeout(r, 500));
  }
  return null;
}

async function main() {
  const srv = await startServer();
  const base = `http://127.0.0.1:${PORT}/${REPO}/`;
  console.log("包目录: " + PKG);
  console.log("模拟仓库: " + base + "\n");

  const prof = path.join(os.tmpdir(), "sz_pwa_prof_" + Date.now());
  fs.mkdirSync(prof, { recursive: true });

  const chrome = spawn(CHROME, [
    "--headless=new", "--disable-gpu", "--no-sandbox",
    `--remote-debugging-port=${CDP_PORT}`,
    `--user-data-dir=${prof}`,
    "--no-first-run", "--no-default-browser-check",
    "--window-size=390,844",
    base,
  ], { stdio: "ignore" });

  let ws;
  try {
    const wsUrl = await getWsUrl();
    if (!wsUrl) {
      check("Chrome CDP 可用", false, "连不上调试端口");
      throw new Error("no cdp");
    }
    check("Chrome CDP 可用", true);

    ws = new WebSocket(wsUrl);
    await new Promise((res, rej) => {
      ws.addEventListener("open", res, { once: true });
      ws.addEventListener("error", rej, { once: true });
    });
    const cdp = new CDP(ws);

    // 连到页面 target
    const { targetInfos } = await cdp.send("Target.getTargets");
    const page = targetInfos.find((t) => t.type === "page");
    if (!page) throw new Error("找不到页面 target");
    const { sessionId } = await cdp.send("Target.attachToTarget", {
      targetId: page.targetId, flatten: true,
    });
    await cdp.send("Page.enable", {}, sessionId);
    await cdp.send("Runtime.enable", {}, sessionId);

    const evalJs = async (expr, awaitPromise = false) => {
      const r = await cdp.send("Runtime.evaluate", {
        expression: expr, awaitPromise, returnByValue: true,
      }, sessionId);
      if (r.exceptionDetails) throw new Error(r.exceptionDetails.text + " :: " + expr);
      return r.result.value;
    };

    // ---------- 1. 页面能打开 ----------
    const title = await evalJs("document.title");
    check("页面打开且有标题", !!title && title.indexOf("神智核") >= 0, "title=" + title);
    const h1 = await evalJs("(document.querySelector('h1')||{}).textContent||''");
    check("首页内容已渲染", h1.indexOf("神智核") >= 0 || (await evalJs("document.body.innerText.length")) > 200);

    // ---------- 2. Service Worker 注册 ----------
    // 等 SW 注册完成（最多 20 秒）
    const swState = await evalJs(`(async () => {
      if (!('serviceWorker' in navigator)) return 'NO_API';
      for (let i = 0; i < 40; i++) {
        const reg = await navigator.serviceWorker.getRegistration();
        if (reg) {
          if (reg.active) return 'activated:' + (reg.active.scriptURL||'');
          if (reg.installing) { await new Promise(r=>setTimeout(r,500)); continue; }
          if (reg.waiting) return 'waiting';
        }
        await new Promise(r=>setTimeout(r,500));
      }
      const reg = await navigator.serviceWorker.getRegistration();
      return reg ? ('registered:' + (reg.active ? 'active' : 'notactive')) : 'NONE';
    })()`, true);
    check("Service Worker 注册并 activated", String(swState).startsWith("activated:"),
      "state=" + swState);
    check("SW 路径正确（相对路径解析到本站）",
      String(swState).indexOf("/" + REPO + "/service-worker.js") >= 0,
      String(swState));

    // ---------- 3. 缓存内容 ----------
    const cacheInfo = await evalJs(`(async () => {
      const names = await caches.keys();
      const out = {names: names, entries: []};
      for (const n of names) {
        const c = await caches.open(n);
        const keys = await c.keys();
        out.entries.push(...keys.map(k => k.url));
      }
      return out;
    })()`, true);
    check("创建了缓存", cacheInfo.names.length > 0, "caches=" + JSON.stringify(cacheInfo.names));
    const ents = cacheInfo.entries || [];
    check("缓存含 index.html", ents.some((u) => /index\.html$|\/$/.test(u)),
      "共 " + ents.length + " 项");
    check("缓存含图标", ents.some((u) => /icon-192\.png$/.test(u)));

    // ---------- 4. manifest 解析 ----------
    const mf = await evalJs(`(async () => {
      const r = await fetch('./manifest.json');
      const j = await r.json();
      return {name: j.name, start: j.start_url, icons: j.icons.length};
    })()`, true);
    check("manifest 可被解析", mf && mf.icons > 0, JSON.stringify(mf));

    // ---------- 5. 断网后仍能打开（核心） ----------
    await cdp.send("Network.enable", {}, sessionId);
    await cdp.send("Network.emulateNetworkConditions", {
      offline: true, latency: 0, downloadThroughput: 0, uploadThroughput: 0,
    }, sessionId);

    // 真的断网后重新导航到同一地址
    const navOk = await (async () => {
      try {
        await cdp.send("Page.navigate", { url: base }, sessionId);
        await new Promise((r) => setTimeout(r, 5000));
        const t = await evalJs("document.title");
        const len = await evalJs("document.body.innerText.length");
        return { title: t, len };
      } catch (e) {
        return { title: null, len: 0, err: String(e) };
      }
    })();
    check("**断网后仍能打开页面**", navOk.title && navOk.title.indexOf("神智核") >= 0,
      "title=" + navOk.title + " 文本长度=" + navOk.len + (navOk.err ? " err=" + navOk.err : ""));

    // 断网后内容仍可用（不只是白屏）
    const offlineUsable = await evalJs(
      "document.body.innerText.indexOf('神智核') >= 0 || document.querySelectorAll('.tcard,.subcard,button').length > 0");
    check("断网后页面内容可用（非白屏）", offlineUsable === true);

    // 恢复网络，避免影响后续
    await cdp.send("Network.emulateNetworkConditions", {
      offline: false, latency: 0, downloadThroughput: -1, uploadThroughput: -1,
    }, sessionId);
  } catch (e) {
    check("测试执行未抛异常", false, String(e));
  } finally {
    try { ws && ws.close(); } catch {}
    chrome.kill();
    srv.close();
    await new Promise((r) => setTimeout(r, 500));
    try { fs.rmSync(prof, { recursive: true, force: true }); } catch {}
  }

  const ok = results.filter((r) => r.ok).length;
  console.log("\n" + "=".repeat(60));
  console.log(`结果: ${ok}/${results.length} 通过`);
  if (ok !== results.length) {
    console.log("失败项:");
    results.filter((r) => !r.ok).forEach((r) => console.log("  - " + r.name + "  " + r.detail));
    process.exit(1);
  }
  console.log("PWA 实测通过（含离线可用）");
  process.exit(0);
}

main().catch((e) => {
  console.error("致命错误:", e);
  process.exit(1);
});
