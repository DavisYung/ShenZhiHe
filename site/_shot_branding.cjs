/* 截图：页脚声明与设置页免责声明区 */
const { chromium } = require("playwright-core");
const http = require("node:http");
const fs = require("node:fs");
const path = require("node:path");

const PKG = path.resolve(process.argv[2] || ".");
const OUT = path.resolve(process.argv[3] || ".");
const FILE = ["神智核.html", "index.html"].find((n) => fs.existsSync(path.join(PKG, n))) || "神智核.html";
const CHROME = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe";
const PORT = 8941;
const MIME = { ".html": "text/html; charset=utf-8", ".json": "application/manifest+json",
  ".js": "application/javascript", ".png": "image/png", ".ico": "image/x-icon", ".webp": "image/webp" };

const srv = http.createServer((req, res) => {
  const p = decodeURIComponent(req.url.split("?")[0]);
  let rel = p.replace(/^\//, ""); if (rel === "") rel = FILE;
  const t = path.join(PKG, rel);
  if (fs.existsSync(t) && fs.statSync(t).isFile()) {
    const d = fs.readFileSync(t);
    res.writeHead(200, { "Content-Type": MIME[path.extname(t)] || "application/octet-stream" });
    res.end(d);
  } else { res.writeHead(404); res.end("nf"); }
});
srv.listen(PORT, "127.0.0.1");

(async () => {
  const browser = await chromium.launch({ executablePath: CHROME, args: ["--no-sandbox"] });
  const page = await browser.newPage({ viewport: { width: 390, height: 844 } });
  await page.goto(`http://127.0.0.1:${PORT}/${encodeURIComponent(FILE)}`, { waitUntil: "load" });
  await page.waitForTimeout(3500);

  // 1. 首页滚到底看页脚
  await page.evaluate(() => { location.hash = "#/chem/home"; });
  await page.waitForTimeout(1500);
  await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
  await page.waitForTimeout(1200);
  await page.screenshot({ path: path.join(OUT, "b_footer.png") });
  console.log("  已截图 b_footer.png");

  // 2. 展开完整声明
  const expanded = await page.evaluate(() => {
    const d = document.querySelector("footer .fnote");
    if (d) { d.open = true; d.scrollIntoView({ block: "center" }); return true; }
    return false;
  });
  await page.waitForTimeout(1200);
  await page.screenshot({ path: path.join(OUT, "b_disclaimer_open.png") });
  console.log("  已截图 b_disclaimer_open.png  展开=" + expanded);

  // 3. 设置页的声明区
  await page.evaluate(() => { location.hash = "#/settings"; });
  await page.waitForTimeout(2000);
  const legal = await page.evaluate(() => {
    const el = document.getElementById("legalbox");
    if (el) { el.scrollIntoView({ block: "start" }); return el.innerText.slice(0, 400); }
    return null;
  });
  await page.waitForTimeout(1200);
  await page.screenshot({ path: path.join(OUT, "b_settings_legal.png") });
  console.log("  已截图 b_settings_legal.png");
  console.log("\n--- 设置页声明区文案 ---");
  console.log(legal || "(未找到 legalbox)");

  // 4. 版本号显示
  const ver = await page.evaluate(() => {
    const b = document.getElementById("brandver");
    return b ? b.textContent : "?";
  });
  console.log("\n  顶栏版本号: " + ver);

  await browser.close();
  srv.close();
  process.exit(0);
})();
