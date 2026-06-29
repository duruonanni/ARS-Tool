import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { spawnSync } from 'child_process';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(__dirname, '..');
const releasePath = path.join(root, 'release', 'index.html');

const build = spawnSync(process.execPath, [path.join(root, 'scripts', 'build_release.mjs')], {
  cwd: root,
  stdio: 'inherit',
});
if (build.status !== 0) process.exit(build.status ?? 1);

if (!fs.existsSync(releasePath)) {
  console.error('FAIL: release/index.html missing after build');
  process.exit(1);
}

const stat = fs.statSync(releasePath);
if (stat.size < 500_000) {
  console.error(`FAIL: release/index.html too small (${stat.size} bytes)`);
  process.exit(1);
}

const html = fs.readFileSync(releasePath, 'utf8');
const pkg = JSON.parse(fs.readFileSync(path.join(root, 'package.json'), 'utf8'));

const checks = [
  [`const VERSION = '${pkg.version}'`, 'VERSION constant'],
  [`id="verTag">v${pkg.version}<`, 'verTag visible text'],
  ['.ver-tag{', 'ver-tag CSS'],
  ['function generateARS', 'generateARS'],
  ['location.protocol.startsWith', 'spec URL routing'],
  ['window.XLSX', 'SheetJS global'],
  ['JSZip', 'JSZip'],
];

for (const [needle, label] of checks) {
  if (!html.includes(needle)) {
    console.error(`FAIL: missing ${label} (${needle})`);
    process.exit(1);
  }
}

console.log(`PASS: build smoke (v${pkg.version}, ${(stat.size / 1024 / 1024).toFixed(2)} MB)`);
