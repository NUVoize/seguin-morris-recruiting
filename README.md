# Seguin Morris — Recruiting Intelligence Platform

**Designed by CTRL Solutions** · Internal bilingual multi-agent recruiting intelligence platform for refrigeration, HVAC-R, mechanical service, and mechanical construction recruiting.

---

## What this is

An internal tool for Seguin Morris recruiters to **find, organize, vet, rank, contact, and track** qualified candidates — primarily *frigoristes* (refrigeration technicians) and adjacent HVAC-R / mechanical roles — across the company's regions in Canada and the U.S.

- Internal-only · multi-user · role-based access
- Bilingual UI (FR default, EN secondary)
- Multi-agent architecture with human-in-the-loop review
- Railway deployment

## Stack

| Layer | Choice |
| --- | --- |
| Frontend | Next.js (App Router) + Tailwind |
| Backend | Python FastAPI + Pydantic |
| ORM / Migrations | SQLAlchemy + Alembic |
| Workers | Celery + Redis |
| Scraping | Playwright *(only where source policy allows)* |
| Database | PostgreSQL |
| Hosting | Railway (services: web, api, worker, postgres, redis) |
| LLM | Swappable adapter (OpenAI, Anthropic, Gemini, Azure OpenAI, LM Studio) |
| Email | Gmail (v1 mock) → Microsoft 365 (v2), behind a single abstraction |

## Repository layout

```
seguin-morris-recruiting/
├── apps/
│   ├── api/         # FastAPI backend
│   ├── web/         # Next.js frontend
│   └── worker/      # Celery worker
├── packages/        # Shared types, config, UI tokens
├── infra/           # Railway, Docker, DB infrastructure
├── docs/            # Spec, blueprint, source policy, branding, API, reviews
└── assets/brand/    # Seguin Morris brand assets
```

## Build phases

1. **Scaffold** — repo, FastAPI health, Next.js shell, Postgres, Alembic ← *current*
2. Core data model — schema, migrations, seed roles, CRUD
3. Agent framework — orchestrator, AgentRun, mock agents
4. Candidate pipeline — list/detail, Kanban, fit score
5. LLM adapter — provider interface, one live provider, mock fallback
6. Outreach & email — templates, drafts, Gmail mock, M365-ready
7. Reports — dashboard, campaign, source, recruiter activity
8. Assistant mockup — knowledge docs, query page, bilingual answers

## Local development (quickstart)

Dev databases run on Railway — one paid project hosts a dev Postgres + dev Redis,
isolated from production. Copy the public connection URLs into a local `.env`.

```powershell
# 1. Create .env from the template, then paste your Railway dev URLs
copy .env.example .env
# Edit .env: set DATABASE_URL and REDIS_URL from your Railway dev project's
# DATABASE_PUBLIC_URL and REDIS_PUBLIC_URL service variables.

# 2. Backend
cd apps\api
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
alembic upgrade head        # once Phase 2 has migrations
uvicorn app.main:app --reload --port 8000

# 3. Frontend (in a separate shell)
cd apps\web
npm install
npm run dev
```

Backend health check: <http://localhost:8000/api/health>
Backend readiness: <http://localhost:8000/api/health/ready>
Frontend: <http://localhost:3000>

## Hard rules (non-negotiable)

1. LLM provider goes through the adapter — never hardcoded into agents.
2. Email provider goes through the adapter — Gmail today, M365 tomorrow.
3. Scraping only runs if `source.allowed_to_scrape = true`.
4. Outreach requires recruiter approval — no automatic sends.
5. AI fit score is **advisory**. Recruiter decides. No "hire" / "reject" language.
6. Audit logs on every important action.
7. Role-based access checks on every protected route.
8. Every user-facing label uses a translation key (FR default, EN secondary).
9. Minimize sensitive personal data.
10. v1 assistant is text-only. v2 voice/phone deferred.

## References

The Quebec recruiting domain (DEP / DEC / AEC programs, CCQ vs. service-vs-contractor regulatory split, SF-1 / SF-2 / halocarbures / RBQ 15.10, OQLF language compliance) is captured in `docs/`.

---

**Seguin Morris Recruiting Intelligence Platform** · Designed by CTRL Solutions
