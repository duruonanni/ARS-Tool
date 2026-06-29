/**
 * One-time splitter: archive/ALM_to_ARS_Converter.html → src/ui/*
 * Run: node scripts/split_monolith.mjs
 */
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(__dirname, '..');
const src = path.join(root, 'archive', 'ALM_to_ARS_Converter.html');
const lines = fs.readFileSync(src, 'utf8').split(/\r?\n/);

function slice(start, end) {
  return lines.slice(start - 1, end).join('\n');
}

// CSS: lines 49-291 (inside <style>, exclude tags at 48 and 292)
const css = slice(49, 291);
fs.mkdirSync(path.join(root, 'src', 'ui'), { recursive: true });
fs.writeFileSync(path.join(root, 'src', 'ui', 'styles.css'), css + '\n', 'utf8');

// Body markup: 294-605 + 2785-2807
const bodyHtml = slice(294, 605) + '\n' + slice(2785, 2807);
const template = `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>ARS Tool</title>
<link rel="icon" type="image/svg+xml" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E%3Crect width='64' height='64' rx='12' fill='%23cc0000'/%3E%3Ctext x='32' y='44' text-anchor='middle' font-size='40' font-family='Arial,sans-serif' fill='white'%3E%E2%99%BB%3C/text%3E%3C/svg%3E">
@@ARS_TOOL_VENDOR_SLOT_a7f3e9@@
<style>
@@ARS_TOOL_STYLES_SLOT_b2c8d1@@
</style>
</head>
${bodyHtml}
@@ARS_TOOL_APP_SLOT_c4e6f0@@
</html>
`;
fs.writeFileSync(path.join(root, 'src', 'ui', 'index.template.html'), template, 'utf8');

// App JS: lines 607-2782 (inside <script> at 606-2783)
let appJs = slice(607, 2782);
const versionBlock = `const VERSION = '1.0.0'; // synced from package.json — do not hand-edit
if (document.getElementById('verTag')) {
  document.getElementById('verTag').textContent = 'v' + VERSION;
}

`;
appJs = versionBlock + appJs;
fs.writeFileSync(path.join(root, 'src', 'ui', 'app.js'), appJs + '\n', 'utf8');

// Patch header in template for verTag
const tplPath = path.join(root, 'src', 'ui', 'index.template.html');
let tpl = fs.readFileSync(tplPath, 'utf8');
tpl = tpl.replace(
  `<header>
  <div class="logo">&#9851;</div>
  <div>
    <h1>Asset Recovery File Processing Assistant</h1>
  </div>
</header>`,
  `<header>
  <div class="logo">&#9851;</div>
  <div style="flex:1">
    <h1>Asset Recovery File Processing Assistant</h1>
  </div>
  <span class="ver-tag" id="verTag"></span>
</header>`
);
fs.writeFileSync(tplPath, tpl, 'utf8');

// Add ver-tag CSS
const cssPath = path.join(root, 'src', 'ui', 'styles.css');
const cssContent = fs.readFileSync(cssPath, 'utf8');
if (!cssContent.includes('.ver-tag')) {
  fs.writeFileSync(
    cssPath,
    cssContent.trimEnd() + '\n.ver-tag{margin-left:auto;padding:2px 10px;border-radius:999px;background:rgba(255,255,255,.18);font-size:11px;font-weight:600;white-space:nowrap;align-self:center}\n',
    'utf8'
  );
}

console.log('Split complete → src/ui/');
