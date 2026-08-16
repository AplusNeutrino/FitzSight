#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';
import { createRequire } from 'node:module';
import { pathToFileURL } from 'node:url';

const root = path.resolve(path.dirname(new URL(import.meta.url).pathname.replace(/^\/(.:)/, '$1')), '..');
const htmlPath = path.resolve(process.argv[2] || path.join(root, 'submission', 'deck-cn', 'index.html'));
const outputDir = path.resolve(process.argv[3] || path.join(root, 'build', 'deck-cn-rendered'));
const nodeModules = process.env.CODEX_NODE_MODULES || 'C:/Users/ZFY/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules';
const require = createRequire(path.join(nodeModules, 'package.json'));
const { chromium } = require('playwright');

const edge = process.env.FITZSIGHT_BROWSER || 'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe';
if (!fs.existsSync(htmlPath)) throw new Error(`Deck not found: ${htmlPath}`);
if (!fs.existsSync(edge)) throw new Error(`Browser not found: ${edge}`);
fs.mkdirSync(outputDir, { recursive: true });

const browser = await chromium.launch({
  executablePath: edge,
  headless: true,
  args: ['--allow-file-access-from-files', '--disable-web-security', '--use-angle=swiftshader'],
});
const context = await browser.newContext({
  viewport: { width: 1920, height: 1080 },
  deviceScaleFactor: 2,
  locale: 'zh-CN',
});
const page = await context.newPage();
await page.goto(pathToFileURL(htmlPath).href, { waitUntil: 'domcontentloaded' });
await Promise.race([
  page.evaluate(() => document.fonts?.ready),
  page.waitForTimeout(2400),
]);
await page.addStyleTag({ content: `
  #nav,#guide,#ppt-presenter,canvas.bg{display:none!important}
  [data-anim],.row-fill,.tl-node,.stack-block,.bar-tower,.sub-card,.col,.vrule,.kpi-cell,.card-fill,.card-accent,.card-ink{opacity:1!important;transform:none!important}
  *{animation:none!important;transition:none!important}
` });

const count = await page.locator('section.slide').count();
if (count !== 12) throw new Error(`Expected 12 slides, found ${count}`);
const report = [];
for (let i = 0; i < count; i += 1) {
  await page.evaluate((index) => {
    window.__lowPowerMode = true;
    if (typeof window.go === 'function') window.go(index, { force: true });
    document.querySelectorAll('section.slide').forEach((slide) => slide.classList.add('export-static'));
  }, i);
  await page.waitForTimeout(120);
  const metrics = await page.evaluate((index) => {
    const slide = document.querySelectorAll('section.slide')[index];
    const card = slide.querySelector('.canvas-card') || slide;
    const sr = slide.getBoundingClientRect();
    const cr = card.getBoundingClientRect();
    const visible = [...slide.querySelectorAll('*')].filter((el) => {
      const cs = getComputedStyle(el);
      const r = el.getBoundingClientRect();
      return cs.display !== 'none' && cs.visibility !== 'hidden' && Number(cs.opacity) > 0 && r.width > 2 && r.height > 2;
    });
    const overflow = visible.filter((el) => {
      const r = el.getBoundingClientRect();
      return r.left < sr.left - 1 || r.top < sr.top - 1 || r.right > sr.right + 1 || r.bottom > sr.bottom + 1;
    }).map((el) => ({ tag: el.tagName, cls: String(el.className).slice(0, 80) })).slice(0, 8);
    return {
      id: slide.dataset.slideId,
      layout: slide.dataset.layout,
      slide: { width: sr.width, height: sr.height },
      card: { left: cr.left, top: cr.top, right: cr.right, bottom: cr.bottom },
      overflow,
    };
  }, i);
  const file = path.join(outputDir, `slide-${String(i + 1).padStart(2, '0')}.png`);
  await page.screenshot({ path: file, type: 'png', animations: 'disabled' });
  report.push({ page: i + 1, file: path.basename(file), ...metrics });
}
await browser.close();

const bad = report.filter((item) => item.overflow.length);
fs.writeFileSync(path.join(outputDir, 'render-report.json'), JSON.stringify({ pages: count, overflow_pages: bad.map((x) => x.page), slides: report }, null, 2) + '\n');
if (bad.length) {
  console.error(JSON.stringify({ status: 'overflow', pages: bad.map((x) => x.page) }, null, 2));
  process.exit(1);
}
console.log(JSON.stringify({ status: 'PASS', pages: count, outputDir }, null, 2));
