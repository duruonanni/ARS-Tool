# Session Handoff

Status: Active  
Last updated: 2026-06-29

## Current state

- Source pushed to GitLab `kongxiang2/ars-tool` for xCloud AWP deploy.
- Profile **B** registered: WEB `:8093`, API `:3004`, SITE_CODE `ars-tool`.
- xCloud deploy scaffolding added (`docs/SANDBOX_DEPLOYMENT.md`, `scripts/publish-static.sh`).
- HTML updated: hosted pages use same-origin `/spec` (1Panel API proxy).

## Not done yet

- [ ] AWP first deploy (1Panel site, Supervisor for Python API, smoke on Sandbox + PC)
- [ ] Security group ticket for TCP `8093` if PC times out
- [ ] PC browser smoke after office network available

## Next actions

1. On AWP: `git clone https://gitlab.xpaas.lenovo.com/kongxiang2/ars-tool.git /opt/ars-tool`
2. Follow `docs/SANDBOX_DEPLOYMENT.md` §3
3. Run `@xcloud-awp-deploy` smoke checklist when live

## Verification notes

- Local: `python lenovo_spec_server.py` + open HTML → spec lookup works
- Sandbox (after deploy): `curl -I http://10.62.81.112:8093/` and `curl http://127.0.0.1:3004/health` on AWP
