import { spawnSync } from 'child_process';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(__dirname, '..');

let failed = false;

const py = spawnSync('python', ['-m', 'py_compile', path.join(root, 'src', 'server', 'lenovo_spec_server.py')], {
  cwd: root,
  stdio: 'inherit',
});
if (py.status !== 0) failed = true;

const smoke = spawnSync(process.execPath, [path.join(root, 'tests', 'build_smoke.mjs')], {
  cwd: root,
  stdio: 'inherit',
});
if (smoke.status !== 0) failed = true;

process.exit(failed ? 1 : 0);
