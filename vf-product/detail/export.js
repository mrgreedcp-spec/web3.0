// 把 detail.html 导出为电商详情页长图 + 按模块切片
// 用法：node vf-product/detail/export.js
// 输出：vf-product/detail/out/detail-full.jpg 以及 out/slices/01.jpg ~ 11.jpg
const path = require('path');
const fs = require('fs');
const { chromium } = require('playwright');

const WIDTH = 750; // 与 detail.html 中 --w 保持一致
const QUALITY = 88;

(async () => {
  const dir = __dirname;
  const out = path.join(dir, 'out');
  const slices = path.join(out, 'slices');
  fs.mkdirSync(slices, { recursive: true });

  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: WIDTH, height: 1200 } });
  await page.goto('file://' + path.join(dir, 'detail.html'));
  await page.evaluate(() => document.fonts.ready);

  await page.screenshot({ path: path.join(out, 'detail-full.jpg'), fullPage: true, type: 'jpeg', quality: QUALITY });

  const ids = await page.$$eval('section.m', els => els.map(e => e.id));
  for (const id of ids) {
    const name = id.replace(/^s/, '') + '.jpg';
    await page.locator('#' + id).screenshot({ path: path.join(slices, name), type: 'jpeg', quality: QUALITY });
  }
  const h = await page.evaluate(() => document.body.scrollHeight);
  console.log(`full: ${WIDTH}x${h}, slices: ${ids.length}`);
  await browser.close();
})();
