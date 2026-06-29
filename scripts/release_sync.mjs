import { spawnSync } from 'child_process';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(__dirname, '..');
const releasePath = path.join(root, 'release', 'index.html');

function run(script) {
  const result = spawnSync(process.execPath, [path.join(root, 'scripts', script)], {
    cwd: root,
    stdio: 'inherit',
  });
  if (result.status !== 0) process.exit(result.status ?? 1);
}

if (process.env.ARS_SKIP_VERSION_BUMP !== '1') {
  run('bump_release_version.mjs');
} else {
  run('sync_version.mjs');
}

run('build_release.mjs');

if (!fs.existsSync(releasePath)) {
  throw new Error(`Built release not found: ${releasePath}`);
}

const pkg = JSON.parse(fs.readFileSync(path.join(root, 'package.json'), 'utf8'));
const html = fs.readFileSync(releasePath, 'utf8');
if (!html.includes(`const VERSION = '${pkg.version}'`)) {
  throw new Error(`Release HTML VERSION does not match package.json v${pkg.version}`);
}

console.log(`Release ready: v${pkg.version} → ${releasePath}`);
