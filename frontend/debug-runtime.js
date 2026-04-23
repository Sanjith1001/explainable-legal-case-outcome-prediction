const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  page.on('console', (msg) => console.log('[console]', msg.type(), msg.text()));
  page.on('pageerror', (err) => console.log('[pageerror]', err.message));
  page.on('request', (req) => {
    if (req.url().includes('localhost:3000/static') || req.url().includes('localhost:3000')) {
      console.log('[request]', req.method(), req.url());
    }
  });
  page.on('response', (res) => {
    if (res.url().includes('localhost:3000/static') || res.url().includes('localhost:3000')) {
      console.log('[response]', res.status(), res.url());
    }
  });
  await page.goto('http://localhost:3000', { waitUntil: 'domcontentloaded', timeout: 60000 });
  await page.waitForTimeout(3000);
  const rootHtml = await page.$eval('#root', el => el.innerHTML).catch(() => 'NO_ROOT');
  console.log('[root-html-length]', rootHtml.length);
  const scripts = await page.$$eval('script', els => els.map(s => ({src: s.src, type: s.type}))); 
  console.log('[scripts]', JSON.stringify(scripts));
  await browser.close();
})();
