# ARS Tool — Asset Recovery File Processing Assistant

Local browser tool for LOT / operations teams: convert ALM or customer asset lists into ARS Pick-up Request format and analyze recovery status.

## Components

| Path | Role |
|------|------|
| `Asset Recovery File Processing/ALM_to_ARS_Converter.html` | Single-page UI (SheetJS / JSZip) |
| `Asset Recovery File Processing/lenovo_spec_server.py` | Local Python spec lookup API (bypasses CORS / WAF) |
| `Asset Recovery File Processing/Start_Spec_Server.bat` | Windows launcher |
| `data/` | Sample input / output workbooks for testing |

## Local use (Windows)

1. `cd "Asset Recovery File Processing"`
2. `python lenovo_spec_server.py` (listens on `http://localhost:9527`)
3. Open `ALM_to_ARS_Converter.html` in a browser, or run `Start_Spec_Server.bat`

## xCloud Sandbox (Profile B)

- **WEB_PORT** `8093` · **API_PORT** `3004` · **SITE_CODE** `ars-tool`
- Source on server: `/opt/ars-tool`
- GitLab: `https://gitlab.xpaas.lenovo.com/kongxiang2/ars-tool`
- Deploy guide: [`docs/SANDBOX_DEPLOYMENT.md`](docs/SANDBOX_DEPLOYMENT.md)

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
