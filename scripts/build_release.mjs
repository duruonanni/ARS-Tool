import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { spawnSync } from 'child_process';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(__dirname, '..');

const sync = spawnSync(process.execPath, [path.join(root, 'scripts', 'sync_version.mjs')], {
  cwd: root,
  stdio: 'inherit',
});
if (sync.status !== 0) process.exit(sync.status ?? 1);

function readVendor(relPaths) {
  for (const rel of relPaths) {
    const p = path.join(root, 'node_modules', rel);
    if (fs.existsSync(p)) return fs.readFileSync(p, 'utf8').trim();
  }
  throw new Error(`Vendor not found. Tried: ${relPaths.join(', ')}`);
}

const xlsxJs = readVendor([
  'xlsx/dist/xlsx.full.min.js',
  'xlsx/dist/xlsx.min.js',
]);
const jszipJs = readVendor([
  'jszip/dist/jszip.min.js',
]);

const pkg = JSON.parse(fs.readFileSync(path.join(root, 'package.json'), 'utf8'));
const template = fs.readFileSync(path.join(root, 'src', 'ui', 'index.template.html'), 'utf8');
const css = fs.readFileSync(path.join(root, 'src', 'ui', 'styles.css'), 'utf8').trim();
const appJs = fs.readFileSync(path.join(root, 'src', 'ui', 'app.js'), 'utf8').trim();

const vendorBlock = `<script>\n${xlsxJs}\n</script>\n<script>\n${jszipJs}\n</script>`;

const PLACEHOLDER_VENDOR = '@@ARS_TOOL_VENDOR_SLOT_a7f3e9@@';
const PLACEHOLDER_STYLES = '@@ARS_TOOL_STYLES_SLOT_b2c8d1@@';
const PLACEHOLDER_APP = '@@ARS_TOOL_APP_SLOT_c4e6f0@@';
const PLACEHOLDER_VERSION = '@@ARS_TOOL_VERSION_SLOT_d8e2a1@@';

function spliceOnce(text, marker, insertion) {
  const i = text.indexOf(marker);
  if (i === -1) throw new Error(`Missing placeholder: ${marker}`);
  if (text.indexOf(marker, i + marker.length) !== -1) {
    throw new Error(`Placeholder appears more than once in template: ${marker}`);
  }
  return text.slice(0, i) + insertion + text.slice(i + marker.length);
}

let out = spliceOnce(template, PLACEHOLDER_VENDOR, vendorBlock);
out = spliceOnce(out, PLACEHOLDER_STYLES, css);
out = spliceOnce(out, PLACEHOLDER_VERSION, pkg.version);
out = spliceOnce(out, PLACEHOLDER_APP, `<script>\n${appJs}\n</script>`);

const releasePath = path.join(root, 'release', 'index.html');
fs.mkdirSync(path.dirname(releasePath), { recursive: true });
fs.writeFileSync(releasePath, out, 'utf8');
console.log(`Built: ${releasePath} (${(fs.statSync(releasePath).size / 1024 / 1024).toFixed(2)} MB)`);
