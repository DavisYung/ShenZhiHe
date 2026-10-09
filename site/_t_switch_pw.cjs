/* Playwright 版科目切换回归 —— 对照手写 CDP 版（_t_switchsubject.mjs，约 200 行）。
 * 用系统已装的 Chrome（channel 或 executablePath），不下载浏览器。
 */
const { chromium } = require("playwright-core");
const http = require("node:http");
const fs = require("node:fs");
const path = require("node:path");

const PKG = path.resolve(process.argv[2] || ".");
const OUT = path.resolve(process.argv[3] || ".");
const FILE = ["神智核.html", "index.html"].find((n) => fs.existsSync(path.join(PKG, n))) || "神智核.html";
const CHROME = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe";
const PORT = 8931;
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

const results = [];
const check = (n, ok, d = "") => { results.push([n, ok, d]); console.log((ok ? "  PASS  " : "  FAIL  ") + n + (d ? "   " + d : "")); };

(async () => {
  const browser = await chromium.launch({ executablePath: CHROME, args: ["--no-sandbox"] });
  const page = await browser.newPage({ viewport: { width: 390, height: 844 } });
  const base = `http://127.0.0.1:${PORT}/${encodeURIComponent(FILE)}`;
  await page.goto(base, { waitUntil: "load" });
  await page.waitForTimeout(3000);

  const state = () => page.evaluate(() => ({
    sub: (typeof SUB !== "undefined" && SUB) ? SUB.id : "?",
    hash: location.hash,
  }));
  const clickSubject = (name) => page.evaluate((n) => {
    const b = [...document.querySelectorAll("#subbar button")].find((x) => x.textContent.includes(n));
    if (b) { b.click(); return true; } return false;
  }, name);

  console.log("--- 物理各页 → 化學 ---");
  for (const h of ["#/phys/home", "#/phys/quiz", "#/phys/graph", "#/phys/review",
                   "#/phys/wrong", "#/phys/extras", "#/phys/t/heat1", "#/phys/unit/thermal"]) {
    await page.evaluate((x) => { location.hash = x; }, h);
    await page.waitForTimeout(800);
    await clickSubject("化學");
    await page.waitForTimeout(900);
    const s = await state();
    check(`  ${h} → 化學`, s.sub === "chem", `SUB=${s.sub} hash=${s.hash}`);
  }

  console.log("\n--- 化學各页 → 物理 ---");
  for (const h of ["#/chem/home", "#/chem/quiz", "#/chem/graph", "#/chem/t/1a"]) {
    await page.evaluate((x) => { location.hash = x; }, h);
    await page.waitForTimeout(800);
    await clickSubject("物理");
    await page.waitForTimeout(900);
    const s = await state();
    check(`  ${h} → 物理`, s.sub === "phys", `SUB=${s.sub} hash=${s.hash}`);
  }

  // 真机尺寸截图（手写 CDP 也能做，但这里一行搞定）
  await page.evaluate(() => { location.hash = "#/phys/home"; });
  await page.waitForTimeout(1200);
  await page.screenshot({ path: path.join(OUT, "pw_iphone.png") });
  console.log("  已截图 pw_iphone.png (390x844 = iPhone 15 尺寸)");

  // iPad 尺寸
  await page.setViewportSize({ width: 820, height: 1180 });
  await page.waitForTimeout(900);
  await page.screenshot({ path: path.join(OUT, "pw_ipad.png") });
  console.log("  已截图 pw_ipad.png (820x1180 = iPad Air 尺寸)");

  await browser.close();
  srv.close();

  const ok = results.filter((r) => r[1]).length;
  console.log("\n" + "=".repeat(56));
  console.log(`结果: ${ok}/${results.length} 通过`);
  if (ok !== results.length) {
    results.filter((r) => !r[1]).forEach((r) => console.log("  - " + r[0] + " " + r[2]));
    process.exit(1);
  }
  console.log("Playwright 版验证通过");
  process.exit(0);
})();
