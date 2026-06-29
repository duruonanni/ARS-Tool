# Decisions

## 2026-06-29 - Source layout and release build

- Status: Active
- Context: Monolithic `ALM_to_ARS_Converter.html` (~1.15 MB) was hard to maintain in git; enterprise PoC expects `src/` + generated `release/`.
- Decision:
  - **Source** under `src/ui/` (template, CSS, app.js) and `src/server/lenovo_spec_server.py`.
  - **Build** via `npm run build` → single-file `release/index.html` (SheetJS + JSZip inlined from npm).
  - **`release/` gitignored**; Sandbox and local use require build after clone/pull.
  - **Version SSOT**: `package.json` `"version"`; synced to `app.js` and shown in UI `#verTag`.
  - **Archive**: original HTML frozen at `archive/ALM_to_ARS_Converter.html`.
  - **Publish**: `scripts/publish-static.sh` rsyncs `release/index.html`.
- Consequence:
  - AWP deploy adds `npm ci && npm run release:sync` before `publish-static.sh`.
  - Local launcher: `scripts/Start_Spec_Server.bat`.

## 2026-06-29 - Sandbox deploy profile

- Status: Active
- Context: ARS Tool needs xCloud Sandbox hosting for team trial; Lenovo spec lookup requires a server-side API (Profile B).
- Decision:
  - **Profile B** — static HTML + Python spec API (`lenovo_spec_server.py`) behind 1Panel reverse proxy.
  - **WEB_PORT** `8093`; **API_PORT** `3004` on Sandbox (`PORT` env overrides local default `9527`).
  - **SITE_CODE** `ars-tool`; source `/opt/ars-tool`; static via `scripts/publish-static.sh`.
  - GitLab: `https://gitlab.xpaas.lenovo.com/kongxiang2/ars-tool`.
  - Browser calls same-origin `/spec` when served over HTTP(S); local `file://` still uses `http://localhost:9527`.
- Consequence:
  - Operators follow `docs/SANDBOX_DEPLOYMENT.md` and `@xcloud-awp-deploy` checklists.
  - Push deploy scripts to GitLab before AWP `git pull` expects them.

## 2026-06-29 - Git remotes

- Status: Active
- Context: Upstream lives on GitHub; internal Sandbox uses GitLab.
- Decision:
  - `origin` → GitHub fork (`duruonanni/ARS-Tool`)
  - `upstream` → original (`DDDDie/ARS-Tool`)
  - `gitlab` → Lenovo GitLab (`kongxiang2/ars-tool`) for AWP deployment
- Consequence:
  - Feature work may sync from `upstream`; Sandbox deploys from `gitlab` only.
