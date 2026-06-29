# ARS Tool — xCloud Sandbox Deployment

Status: **Active**  
Last updated: **2026-06-29**

Generic procedures: `@xcloud-awp-deploy` skill (`references/sandbox-standard.md`)  
Checklists: skill `assets/checklists/xcloud_awp_*.md`

---

## Instance variables

| Variable | Value |
|----------|-------|
| Profile | B |
| Sandbox host | `10.62.81.112` |
| Web port | `8093` |
| API port | `3004` |
| Site code | `ars-tool` |
| Source on server | `/opt/ars-tool` |
| 1Panel web root | `/opt/1panel/www/sites/ars-tool/index` |
| Git | `https://gitlab.xpaas.lenovo.com/kongxiang2/ars-tool.git` |
| Supervisor | `ars-tool-api` |

---

## Architecture

```text
/opt/ars-tool  --publish-static.sh-->  /opt/1panel/www/sites/ars-tool/index/index.html

Browser :8093
    │
    ▼
1Panel OpenResty (site code ars-tool)
    ├── /              → index.html (built from src/ui)
    └── /spec, /health → reverse proxy → 127.0.0.1:3004 (src/server/lenovo_spec_server.py)
```

| 目录 | 用途 |
|------|------|
| `/opt/ars-tool` | 源码、Python API、`.env`（**不是** 1Panel 网站根） |
| `/opt/1panel/www/sites/ars-tool/index` | 仅发布静态 HTML（`1000:1000`） |

---

## First deploy

### 1. Clone on AWP

```bash
sudo mkdir -p /opt/ars-tool
sudo chown prame001:wheel /opt/ars-tool
cd /opt/ars-tool
git clone https://gitlab.xpaas.lenovo.com/kongxiang2/ars-tool.git .
```

### 2. Build UI + 1Panel static site

`release/index.html` is **not** committed — build on the server after clone/pull:

```bash
cd /opt/ars-tool
npm ci
npm run release:sync    # patch-bump version + build; or ARS_SKIP_VERSION_BUMP=1 npm run build
```

**网站 → 创建网站** → **静态网站**

| Field | Value |
|-------|-------|
| 域名 | `10.62.81.112` |
| 端口 | `8093` |
| 代号 | `ars-tool` |

```bash
sudo ls -la /opt/1panel/www/sites/ars-tool/index/
bash scripts/publish-static.sh
curl -I http://10.62.81.112:8093/
```

### 3. Python API (Supervisor)

```bash
cd /opt/ars-tool
PORT=3004 python3 src/server/lenovo_spec_server.py &
curl http://127.0.0.1:3004/health
# stop foreground trial, then configure 1Panel process guard: ars-tool-api
```

1Panel **反向代理**（网站 `ars-tool`）:

| 路径 | 目标 |
|------|------|
| `/spec` | `127.0.0.1:3004` |
| `/health` | `127.0.0.1:3004` |

Proxy target: `127.0.0.1:3004` — **no** `http://` prefix.

Supervisor env: `PORT=3004`, working directory `/opt/ars-tool`.

### 4. Smoke

- AWP: `curl http://127.0.0.1:3004/health` → `{"ok": true}`
- AWP: `curl -I http://10.62.81.112:8093/` → 200
- PC (office): `Test-NetConnection 10.62.81.112 -Port 8093`
- Browser: upload sample from `data/alm_hardware.xlsx`, verify Lenovo spec lookup

---

## Routine update

```bash
cd /opt/ars-tool
git pull origin main
npm ci
npm run release:sync                    # or ARS_SKIP_VERSION_BUMP=1 npm run build
bash scripts/publish-static.sh          # publishes release/index.html
# 1Panel → restart ars-tool-api        # when src/server/lenovo_spec_server.py changed
```

---

## Project-specific notes

- **Node required on AWP** for `npm ci` + `npm run build` (devDependencies: `xlsx`, `jszip`).
- `release/` is gitignored; always build before `publish-static.sh`.
- Version SSOT: `package.json`; UI shows `vX.Y.Z` in the header.
- Local dev uses port `9527`; Sandbox uses `PORT=3004`.
- Sample workbooks under `data/` are for manual testing only.
