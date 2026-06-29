# ARS Tool — Asset Recovery File Processing Assistant

Local browser tool for LOT / operations teams: convert ALM or customer asset lists into ARS Pick-up Request format and analyze recovery status.

## Project layout

| Path | Role |
|------|------|
| `src/ui/` | Editable HTML template, CSS, and app JavaScript |
| `src/server/lenovo_spec_server.py` | Local Python spec lookup API (bypasses CORS / WAF) |
| `scripts/` | Build, version bump, publish, local launchers |
| `release/index.html` | **Generated** single-file UI (`file://` + Sandbox); not in git |
| `archive/` | Frozen backup of the original monolithic HTML |
| `data/` | Sample input / output workbooks for testing |

Version SSOT: `package.json` `"version"` (shown in UI header as `verTag`).

## Build and run (Windows)

```bash
npm install
npm run build          # → release/index.html
```

1. `scripts\Start_Spec_Server.bat` — starts Python API and opens `release/index.html`
2. Or: `cd src\server` → `python lenovo_spec_server.py` (port `9527`)
3. Open `release\index.html` in a browser

Hosted pages use same-origin `/spec`; `file://` uses `http://localhost:9527`.

## Release commands

| Command | Purpose |
|---------|---------|
| `npm run build` | Sync version + build `release/index.html` |
| `npm run version:bump` | Patch-bump `package.json` + sync `app.js` |
| `npm run release:sync` | Bump (unless `ARS_SKIP_VERSION_BUMP=1`) + build |
| `npm run check` | `py_compile` server + build smoke test |

## xCloud Sandbox (Profile B)

- **WEB_PORT** `8093` · **API_PORT** `3004` · **SITE_CODE** `ars-tool`
- Source on server: `/opt/ars-tool`
- GitLab: `https://gitlab.xpaas.lenovo.com/kongxiang2/ars-tool`
- Deploy: `npm ci && npm run release:sync` then `scripts/publish-static.sh`
- Guide: [`docs/SANDBOX_DEPLOYMENT.md`](docs/SANDBOX_DEPLOYMENT.md)

## Remotes

| Remote | URL | Purpose |
|--------|-----|---------|
| `origin` | GitHub `duruonanni/ARS-Tool` | Public fork |
| `upstream` | GitHub `DDDDie/ARS-Tool` | Original author |
| `gitlab` | GitLab `kongxiang2/ars-tool` | xCloud AWP `git pull` |

## Docs

- [`ARS_Tool_说明与优化需求.md`](ARS_Tool_说明与优化需求.md) — business context and optimization backlog
- [`DECISIONS.md`](DECISIONS.md) — technical decisions
- [`SESSION_HANDOFF.md`](SESSION_HANDOFF.md) — session state
