import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { spawnSync } from 'child_process';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(__dirname, '..');
const pkgPath = path.join(root, 'package.json');

const requested = process.argv[2];
const pkg = JSON.parse(fs.readFileSync(pkgPath, 'utf8'));
const current = pkg.version;

function bumpPatch(v) {
  const [major, minor, patch] = v.split('.').map(Number);
  return `${major}.${minor}.${patch + 1}`;
}

let next = requested;
if (next) {
  if (!/^\d+\.\d+\.\d+$/.test(next)) {
    throw new Error(`Invalid version: ${next}`);
  }
} else {
  next = bumpPatch(current);
}

if (next === current) {
  console.log(`Release version unchanged: v${current}`);
} else {
  pkg.version = next;
  fs.writeFileSync(pkgPath, `${JSON.stringify(pkg, null, 2)}\n`, 'utf8');
  console.log(`Release version bumped: v${current} -> v${next}`);
}

const sync = spawnSync(process.execPath, [path.join(root, 'scripts', 'sync_version.mjs')], {
  cwd: root,
  stdio: 'inherit',
});
if (sync.status !== 0) process.exit(sync.status ?? 1);
