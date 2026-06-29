# Decisions

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
