# Session Handoff

Status: Active  
Last updated: 2026-06-29

## Current state

- **Restructured** to `src/ui/` + `src/server/` + npm build → `release/index.html` (gitignored).
- Version **v1.0.0** in `package.json`; header shows `verTag`.
- Original monolith backed up at `archive/ALM_to_ARS_Converter.html`.
- GitLab `kongxiang2/ars-tool` — Profile **B** (WEB `:8093`, API `:3004`).
- `scripts/publish-static.sh` publishes `release/index.html`.

## Local workflow

```bash
npm install
npm run build
scripts\Start_Spec_Server.bat
```

## Not done yet

- [ ] AWP first deploy with **npm build** step on server
- [ ] Security group ticket for TCP `8093` if PC times out
- [ ] PC browser smoke after office network available

## Next actions

1. On AWP: `git pull` → `npm ci` → `npm run release:sync` → `bash scripts/publish-static.sh`
2. Follow `docs/SANDBOX_DEPLOYMENT.md` §3 for Supervisor + reverse proxy
3. Run `@xcloud-awp-deploy` smoke checklist when live

## Verification notes

- `npm run check` — py_compile + build smoke (VERSION, verTag, key functions)
- Local: `python src/server/lenovo_spec_server.py` + open `release/index.html`
- Sandbox: `curl -I http://10.62.81.112:8093/` and `curl http://127.0.0.1:3004/health`
