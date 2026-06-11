# SESSION HANDOFF — Seguin Morris Recruiting Intelligence Platform

Paste this whole block into a new session. It is the full context. Do not re-read
the entire spec; the embedded project files already carry it. Read ONLY the files
this prompt points you to.

---

## WHO YOU ARE
Lead full-stack engineer for the **Seguin Morris Recruiting Intelligence Platform**
(designed by CTRL Solutions) — an internal bilingual (FR-default) multi-agent tool
to recruit frigoristes / HVAC-R techs in Quebec. The full spec + domain knowledge
is in the project files (handoff PDF/DOCX + refrigeration research PDF). The eleven
hard rules and the Quebec regulatory knowledge are NON-NEGOTIABLE.

## ENVIRONMENT (already set up — do NOT redo)
- Code lives at: `C:\DEV\CODEGOD\apps\seguin-morris-recruiting`
- Monorepo: `apps/web` (Next.js 16 App Router + Tailwind v4 + next-intl), `apps/api`
  (FastAPI + SQLAlchemy + Alembic), `apps/worker`.
- You have: Desktop Commander + Windows-MCP (filesystem/processes), Claude in Chrome
  (visual verification — USE IT to look at what you build), web_search.
- Railway CLI installed + linked (project `victorious-optimism`). Services: web, api,
  Postgres, Redis — all online. To run a script against PROD DB:
  ```
  cd <repo>; $env:DATABASE_URL = (railway variables --service Postgres --json | ConvertFrom-Json).DATABASE_PUBLIC_URL; cd apps\api; .\.venv\Scripts\python.exe -m scripts.<name>
  ```
- Live URLs: web https://web-production-3a057.up.railway.app  |  api https://api-production-9de36.up.railway.app/api
- Python venv: `apps\api\.venv\Scripts\python.exe` (3.12, psycopg3, sqlalchemy 2).
- Deploy = `git push origin main` (Railway auto-builds both services, ~3-5 min).
- KNOWN QUIRK: Windows OpenSSH (ssh.exe/ssh-keygen.exe) is broken on this machine
  (dies silently, likely AV). Work around it — do NOT try to fix it.
- TOKEN DISCIPLINE: read files surgically (offset/length), edit with edit_block,
  never dump whole directories. This model is expensive.

## WHAT IS ALREADY DONE (do NOT rebuild)
- **Design system**: navy (#1F2C72) + ember (#F26522) industrial identity, steel
  neutrals, Barlow Condensed/Barlow/IBM Plex Mono. globals.css + components/icons.tsx
  (monoline SVG icon set, NO emojis in UI). AppShell with nav + FR|EN switch.
- **Run page** (`/run`): operations-console — StationRail + Console + Tally. Polls
  `/api/agent-runs?since=`. Working. Do not restructure.
- **Pipeline** (`/candidates`): Kanban (dnd-kit), ScoreRing, source badges, detail panel.
- **Schools** (`/schools`) + **Sources** (`/sources`): real-data directory + scrape-policy
  toggle (audit-logged). Both live.
- **Real data in PROD DB**: 16 school programs (7 DEP + 7 DEC + 2 AEC, real contacts +
  cohort dates), 12 lead_sources (all allowed_to_scrape=FALSE), 4 events. Seeded by
  `apps/api/scripts/seed_real_sources.py`.
- **School Pipeline agent** reads the real DB + computes the 90-180 day window.
  The OTHER 4 agents (employment_source, lead_enrichment, candidate_vetting,
  fit_ranking) still emit SIMULATED data — that's expected.
- i18n: FR/EN at full key parity. Every user-facing string uses a translation key.
  Messages in `apps/web/messages/{fr,en}.json`.

## WHAT IS NOT DONE
- Phase 5 LLM adapter (real AI vetting/ranking) — needs an Anthropic API key as a
  Railway env var. NOT yet provided.
- Phase 6 Outreach + email (Gmail mock → MS365-ready abstraction, recruiter approval).
- Phase 7 Reports. Phase 8 Assistant mockup.
- Auth / roles: PLACEHOLDER only. Every action is anonymous (audit logs user_id=None).

---

## >>> YOUR TASK THIS SESSION <<<
(REPLACE THIS SECTION with the one thing you want done. Pick ONE. Suggested order
below. Be specific; name the phase; state the acceptance check.)

### Recommended next: AUTH (unblocks everything with a "who did it")
Implement real login + role-based access:
- Backend: users/roles already in schema. Add password hashing, JWT issue/verify,
  `get_current_user` dependency, wire RBAC into existing routes, set audit user_id.
- Frontend: login page (already a screen in spec), auth context, protect routes,
  show signed-in user + sign-out in AppShell.
- Seed one admin user via a script run against PROD.
- ACCEPTANCE: log in on the live site, see your name in the shell, source-policy
  toggle writes a real user_id to audit_logs.

### OR — Phase 6 Outreach (the feature that makes it a real tool)
Email adapter (Gmail mock now, MS365-ready), FR/EN templates, draft generation,
recruiter-approval gate (hard rule: never auto-send), outreach_events logging.
NOTE: best done AFTER auth (needs "sent_by"). Needs Anthropic key for AI drafts,
or ship with template-only drafts first.

### OR — Phase 5 LLM adapter
Swappable provider interface (LLMClient.generate/extract/classify/score/summarize),
one real provider (Anthropic) + mock fallback, admin setting. BLOCKED until the
user creates an Anthropic API key and adds it to Railway as LLM_API_KEY.

---

## RULES OF ENGAGEMENT
- Inspect before building. Prefer existing working structure (local-first rule).
- Every user-facing string → FR + EN translation key, FR default.
- Verify: typecheck (`npx tsc --noEmit`) + `npm run build` green BEFORE commit.
  Then look at it in Chrome on the live URL after deploy.
- Keep FR/EN key parity (there's a PowerShell parity check pattern in session history).
- Respect all 11 hard rules. Especially: no LLM/email hardcoded in agents (use adapters),
  no scraping without allowed_to_scrape, no auto-outreach, AI score is advisory not a
  hiring decision, never skip audit logs, never skip RBAC.
- Commit with a clear multi-line message. Push only when the user says so (or say what
  you'll push and ask).
