import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(__dirname, '..');
const pkg = JSON.parse(fs.readFileSync(path.join(root, 'package.json'), 'utf8'));
const appPath = path.join(root, 'src', 'ui', 'app.js');

const version = pkg.version;
if (!/^\d+\.\d+\.\d+$/.test(version)) {
  throw new Error(`Invalid package.json version: ${version}`);
}

let app = fs.readFileSync(appPath, 'utf8');
const re = /const VERSION = '[0-9]+\.[0-9]+\.[0-9]+'; \/\/ synced from package\.json — do not hand-edit/;
if (!re.test(app)) {
  throw new Error(`VERSION line not found in ${appPath}`);
}
app = app.replace(re, `const VERSION = '${version}'; // synced from package.json — do not hand-edit`);
fs.writeFileSync(appPath, app, 'utf8');
console.log(`Synced VERSION → ${version} in src/ui/app.js`);
