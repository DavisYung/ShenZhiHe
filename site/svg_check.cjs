const { chromium } = require('playwright-core');

(async () => {
  const browser = await chromium.launch({
    executablePath: 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe'
  });
  const page = await browser.newPage();
  await page.setViewportSize({ width: 800, height: 600 });
  
  const svgs = [
    { name: 'incenter', file: 'math_incenter.svg' },
    { name: 'circumcenter', file: 'math_circumcenter.svg' }
  ];
  
  const genDir = 'D:\\deepseek-harness\\default-workspace\\f6chem\\site\\img\\gen';
  const outDir = 'D:\\deepseek-harness\\default-workspace\\f6chem\\site\\_screenshot_check';
  
  const fs = require('fs');
  if (!fs.existsSync(outDir)) fs.mkdirSync(outDir, { recursive: true });
  
  for (const svg of svgs) {
    const filePath = 'file:///' + genDir + '\\' + svg.file;
    await page.goto(filePath);
    await page.waitForTimeout(300);
    const outPath = outDir + '\\' + svg.name + '_check.png';
    try {
      await page.screenshot({ path: outPath, fullPage: true });
      console.log('已截图: ' + outPath);
    } catch (e) {
      console.log('截图失败 ' + svg.name + ': ' + e.message);
    }
  }
  
  await browser.close();
  console.log('截图检测完成');
})().catch(e => { console.error('ERROR:', e.message); process.exit(1); });
