// Optional browser integration test. Pass the installed Playwright package path as argv[3].
const assert = require('node:assert/strict');
const path = require('node:path');
const { pathToFileURL } = require('node:url');
const { chromium } = require(process.argv[3] || 'playwright');
(async () => {
  const browser = await chromium.launch({ channel: 'msedge', headless: true });
  try {
    const context = await browser.newContext({ offline: true });
    const page = await context.newPage();
    const errors = [], requests = [];
    page.on('pageerror', error => errors.push(String(error)));
    page.on('request', request => { if (/^https?:/.test(request.url())) requests.push(request.url()); });
    await page.goto(pathToFileURL(path.resolve(process.argv[2])).href);
    assert.equal(await page.locator('#results button').count(), 2);
    await page.locator('#search').fill('"id"'); // nested response attribute
    assert.equal(await page.locator('#results button').count(), 1);
    await page.locator('#results button').click();
    assert.match(await page.locator('#detail').innerText(), /GET \/projects/);
    assert.match(await page.locator('#notice').innerText(), /1/);
    await page.locator('#reset').click();
    await page.locator('#method').selectOption('POST');
    assert.equal(await page.locator('#results button').count(), 1);
    await page.locator('#category').selectOption('Projects');
    assert.equal(await page.locator('#results button').count(), 0);
    await page.locator('#reset').click();
    const before = await page.locator('#scene').getAttribute('transform');
    await page.locator('#zoom-in').click();
    assert.notEqual(await page.locator('#scene').getAttribute('transform'), before);
    await page.locator('#search').focus();
    await page.keyboard.press('Tab');
    assert.equal(await page.locator('#category').evaluate(node => node === document.activeElement), true);
    await page.screenshot({ path: path.join(path.dirname(process.argv[2]), 'viewer-check.png'), fullPage: true });
    assert.deepEqual(errors, []);
    assert.deepEqual(requests, []);
    assert.equal(await page.evaluate(() => typeof window.TRAILMAP_INJECTED), 'undefined');
    console.log('PASS: offline file URL, search, combined filters, details, hidden dependencies, zoom, keyboard focus, and no external requests.');
  } finally { await browser.close(); }
})().catch(error => { console.error(error); process.exitCode = 1; });
