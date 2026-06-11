# Handoff: Seguin Morris × CTRL Solutions — Recruiting Intelligence Platform

You're picking up an in-progress build mid-stream. The previous chat shipped Phases 1–4 (scaffold → data model → Kanban → agent theater). Everything works and is deployed live. **Your job is craftsmanship, not features.** The user wants to push the visual, interaction, and design quality way past where it is now. Read this whole document before writing any code.

---

## 1. Project identity (one paragraph)

Internal bilingual (FR-default / EN) recruiting platform built **for** Seguin Morris (mechanical / refrigeration / HVAC-R contractor across QC, ON, MB, AB, BC, select US, Barbados) and **by** CTRL Solutions (the user's agency). Primary purpose: find, vet, rank, and contact Quebec frigoristes (refrigeration techs) and adjacent trades. The "Designed by CTRL Solutions" credit appears in a secondary footer position. The user is Frederic; GitHub `NUVoize`; he's working on Windows from his desktop right now but the project was originally scoped mobile-first via Codespaces.

---

## 2. What is LIVE right now

Both Railway services deployed and verified end-to-end:

| Service | URL | State |
|---|---|---|
| Web (Next.js) | https://web-production-3a057.up.railway.app | Healthy |
| API (FastAPI) | https://api-production-9de36.up.railway.app | Healthy |
| Postgres | Internal Railway | 20 tables, populated |
| Redis | Internal Railway | Configured, not used yet |

**What the user sees today on the live site:**

- `/fr` and `/en` — landing page with two CTAs (launch agents / view pipeline), language toggle, footer credit
- `/[locale]/run` — the "agent theater": click button → 5 agent cards stream live logs in a 5-col grid over ~30s → "View pipeline" CTA at end
- `/[locale]/candidates` — Kanban with 9 columns (new → to_review → contacted → interested → interview → offer → hired → rejected → archived), drag-and-drop with optimistic UI, slide-out detail panel with fit score, certifications, vetting reminder

**Live DB state:** ~18 candidates, 11+ agent runs with full step logs, 12 qualifications. Realistic Quebec data — Olivier Beaupré (Jobillico), Marie-Claude Fortin (Indeed), Léa Pelletier (CFP de Québec finissante), etc.

**The user just said the design "looks like random French names placed in columns" and wants the agent theater + Kanban + landing to feel premium.** That's your North Star.

---

## 3. Hard rules — never violate these

From the embedded project system prompt. These are non-negotiable:

1. **LLM provider** never hardcoded in agents — always through adapter (currently `LLM_PROVIDER=mock`)
2. **Gmail** never hardcoded in outreach — always through email adapter
3. **Scraping** never runs without checking `lead_sources.allowed_to_scrape = true` (default false)
4. **Outreach** never sent without explicit recruiter approval — drafts only
5. **Fit score** is advisory, never a hiring decision. Every candidate-facing summary must include: *"Le score est consultatif. Le recruteur valide les certifications avant toute décision."* This is in code already — don't remove it
6. **Audit logs** for every important action (table exists, not yet wired in)
7. **Role-based access** required (placeholder only right now, no auth implemented yet — Phase 5+)
8. **English-only strings forbidden** — every user-facing label uses translation keys in `messages/fr.json` + `messages/en.json`, FR is default
9. **Minimize sensitive personal data**
10. **No voice/phone assistant in v1** — text mockup only (Phase 8)
11. **Branding**: Seguin Morris logo + visual style up front, "Designed by CTRL Solutions" in secondary footer position

---

## 4. Tech stack — locked, don't change

```
Frontend:   Next.js 16.2.9 (App Router) + React 19 + Tailwind 4 + TS 5 + next-intl 4
Backend:    Python 3.12 FastAPI 0.136 + Pydantic 2.13 + SQLAlchemy 2.0 + Alembic 1.18 + psycopg 3
Workers:    Celery 5.6 + Redis 8.2 (mockup uses FastAPI BackgroundTasks via asyncio.create_task)
Database:   PostgreSQL 18 on Railway
Hosting:    Railway (api + web services, auto-deploy from main)
i18n:       next-intl, FR/EN, FR default
Drag-drop:  @dnd-kit (already in use on Kanban)
```

UI components are hand-rolled — **no shadcn/ui installed**, no component library beyond what's in `components/`. You may add shadcn/ui or any other library if it serves the design upgrade. Currently using only Tailwind utilities.

---

## 5. Local environment

```
Repo:           C:\DEV\CODEGOD\apps\seguin-morris-recruiting
GitHub:         https://github.com/NUVoize/seguin-morris-recruiting (private)
Branch:         main (Railway auto-deploys on push)
Python:         C:\Users\nivoi\AppData\Local\Programs\Python\Python312\python.exe (3.12.9)
Node:           C:\Program Files\nodejs\ (v24.14.0, npm 11.9.0)
API venv:       apps\api\.venv (already set up)
Web deps:       apps\web\node_modules (already installed)
Tests:          `cd apps\api; .\.venv\Scripts\python.exe -m pytest tests/` → 10 pass
Type-check web: `cd apps\web; npx --no-install tsc --noEmit` → 0 errors
```

User is on Windows with PowerShell. Claude Code is NOT installed. You drive via Windows-MCP:PowerShell + Desktop Commander.

---

## 6. Repo layout (key paths only)

```
apps/api/app/
  agents/                          NEW Phase 3
    base.py                        Agent abstract class, AgentContext, AgentStep
    orchestrator.py                DEFAULT_PIPELINE, run_pipeline(campaign_id)
    employment_source.py           Mock: Jobillico/Indeed/LinkedIn/Jobboom
    school_pipeline.py             Mock: 7 real CFP DEP centers
    lead_enrichment.py             Title normalization, source confidence
    candidate_vetting.py           DEP/CCQ/SF1/SF2/halocarbures/ASP30h detection
    fit_ranking.py                 Spec rubric (25/20/15/15/10/10/5)
  api/routes/
    agent_runs.py                  POST/GET/GET-by-id  NEW Phase 3
    candidates.py, campaigns.py, sources.py, health.py, auth.py
  models/                          20 SQLAlchemy models, all enums
  schemas/                         Pydantic input/output schemas
  alembic/versions/a51a71ba6885_initial_schema.py
  scripts/seed.py, seed_dev_candidates.py

apps/web/src/
  app/[locale]/
    layout.tsx, page.tsx           Landing (just refactored to lead with /run CTA)
    candidates/page.tsx            Kanban
    run/page.tsx                   NEW agent theater (server wrapper)
  components/
    pipeline/                      Kanban + cards + detail panel
    run/                           NEW
      AgentCard.tsx                One card, status pill, log feed
      AgentTheater.tsx             Orchestrates trigger + 800ms polling + state machine
  lib/api/
    client.ts                      Tiny typed fetch wrapper
    types.ts                       Mirrors Pydantic schemas (extended for AgentRun)
    candidates.ts, agentRuns.ts    Resource clients
  i18n/                            navigation, routing, request config
messages/
  fr.json                          ~140 keys, FR default
  en.json                          ~140 keys
```

---

## 7. Recent commit history (last 5 — context for what just happened)

```
cbdafe1  Phase 3: Agent theater UI                   (frontend)
280c883  Phase 3: Agent framework + live run API     (backend, 5 agents + orchestrator)
3de6ac3  fix(apps/web): buildCommand for devDeps     (Railway deploy fix)
ba05a45  fix(web): Node 20 + regen package-lock      (Railway deploy fix)
c5f207f  fix(api): Dockerfile CMD shell expansion    (Railway deploy fix)
```

---

## 8. What's NOT built yet (spec Phases 5–8)

You probably won't touch these — the user wants polish, not new features. But for awareness:

- Phase 5: LLM adapter (one real provider + mock fallback + admin setting)
- Phase 6: Outreach composer + Gmail integration + draft approval flow
- Phase 7: Reports / dashboard KPIs
- Phase 8: Assistant knowledge mockup (text-only chat over approved docs)

Also unimplemented even at MVP level: auth, RBAC, sources management UI, schools/events list pages, admin settings page, audit log viewer, retention worker. All are spec'd in the handoff PDF in the project files.

---

## 9. The user's actual ask for this session

The user said, paraphrased: *"I want to push it way further than I ever did before. Looks, style, quality, craftsmanship — everything."*

What that translates to in practice:

**The agent theater** (`/[locale]/run`) is the demo piece. It should feel like watching an operations console — the kind of thing that makes a client go "wow, this is a real product." Current implementation is functional but visually ordinary: white cards, neutral-200 borders, a small dark log box per agent, emoji icons. It needs:

- A stronger visual identity (typography hierarchy, distinctive accent, considered spacing)
- Motion design — the run feels static between updates; agents should appear to "wake up"
- Better information density — counts could be charts/sparklines, not pill chips
- Connecting visualization — right now 5 cards in a row; a flow diagram showing data moving between agents would tell the story
- Iconography upgrade — emojis read amateur. Lucide icons or custom SVG would lift it
- Sound? Subtle ticks/chimes on completion?
- The dark log feed inside white cards is jarring — pick a coherent palette

**The Kanban** (`/[locale]/candidates`) needs to feel less like Trello. Real recruiter products (Greenhouse, Lever, Ashby) have specific design language for candidate cards — pipeline progress chips, source-of-discovery badges, qualification icons, last-activity indicators. The slide-out detail panel could be much richer.

**The landing page** is currently a centered hero with two buttons. Fine for a demo, weak for a portfolio piece. Industrial / trustworthy / professional was the brief — none of those are landing well right now.

**Brand:** the Seguin Morris logo file is in `/mnt/project/images.png` — blue/orange wordmark. The current temp colors (#1F2937 / #0F766E / #F76316) don't use those brand colors. Pulling the logo and reflecting it through accents would tie the whole product together.

---

## 10. Tools and skills available to you

**Read this first**, before anything else, when you start designing:

```
/mnt/skills/public/frontend-design/SKILL.md
```

It's specifically about making distinctive, intentional visual design vs templated defaults. Exactly the user's brief.

Other relevant skills:

- `/mnt/skills/public/docx/`, `/pdf/`, `/pptx/`, `/xlsx/` — if you need to deliver design specs
- `/mnt/skills/examples/web-artifacts-builder/` — if you want to prototype components in a Claude artifact before integrating into Next.js
- The full handoff PDF + DOCX are at `/mnt/project/` (you have read access)
- The brand logo PNG is at `/mnt/project/images.png`
- The Quebec recruiting research PDF (regulatory detail, schools, channels) is also in `/mnt/project/`

**Don't generate Imagine UI mockups** — you have the real codebase, work directly in it.

**Don't use shadcn/ui via npm install without checking with the user first** — adds a dependency. You can copy individual primitives in directly if needed (Radix is fine).

---

## 11. Tooling gotchas (saved me ~2 hours, will save you the same)

These bit me during this build. Avoid them.

**Writing Python files via PowerShell:**
Use single-quoted heredoc + `[IO.File]::WriteAllText` as one Windows-MCP:PowerShell command body:

```powershell
$content = @'
...python code here...
'@
[IO.File]::WriteAllText("path", $content)
```

NOT `powershell -Command "@'...'@"` — the outer shell tries to parse the heredoc content as PowerShell and fails on `from`, `def`, etc.

**Paths with `[locale]`:**
PowerShell treats brackets as wildcards. Use `-LiteralPath` on `Get-Item`, `Get-Content`, `Test-Path`. `[IO.File]::WriteAllText` is fine because it's a .NET method that takes a literal string.

**Emojis in PowerShell heredocs:**
They get mojibake-encoded. Use TypeScript Unicode escapes instead: `'\u{1F50D}'` for the magnifying glass. The AGENT_ICONS object in `AgentTheater.tsx` already does this — follow that pattern.

**Python REPL via Desktop Commander interact_with_process:**
Blank lines in multi-line input terminate it prematurely with a `SyntaxError`. Either send statements one at a time, or use `exec("...")` with `\n`-escaped newlines on a single line.

**French accents through the shell:**
Same encoding issue. Use Python with explicit `\u` escapes (`"Termin\u00e9"`) and write JSON with `ensure_ascii=False` to a `utf-8` file. The strings will be correct on disk even if PowerShell's console displays mojibake when echoing them back.

**FastAPI TestClient + asyncio.create_task background tasks:**
Deadlocks. The orchestrator currently uses `asyncio.create_task` which works fine under uvicorn but not under TestClient. If you write integration tests for `/api/agent-runs`, hit a real uvicorn (port 8001) rather than TestClient.

**Railway auto-deploy:**
Pushes to `main` trigger redeploys of both `api` and `web` services. Backend takes ~3 min (Dockerfile + alembic upgrade). Frontend ~3–5 min (Nixpacks build with `npm install --include=dev && npm run build`). Use `git log -1 --oneline` and Railway's deployment list to verify which commit is live.

---

## 12. Verified-working data flow (so you can test changes confidently)

```
[Browser] POST /api/agent-runs
   ↓
[FastAPI] returns 202 with {started_at, agents: [...5 names...]}
   ↓  + asyncio.create_task(run_pipeline)
   ↓
[Orchestrator] sequentially executes 5 Agent subclasses
   ↓ each writes AgentRun row PENDING → RUNNING → COMPLETED
   ↓ each commits step-by-step JSON to output_summary
   ↓
[Browser] polls GET /api/agent-runs?since=<started_at>&limit=20 every 800ms
   ↓ stops when fit_ranking row shows status='completed'
   ↓
[Browser] renders 5 AgentCards with parsed steps + counts
   ↓ navigates to /candidates on user click
   ↓
[Kanban] shows candidates the agents just created, with fit scores 53–76
```

Run takes ~28–32 seconds end-to-end. CORS is locked to `https://web-production-3a057.up.railway.app` only.

---

## 13. Bilingual strings — already in place

`messages/fr.json` and `messages/en.json` have a `run.*` block with: agent names, status pills (En attente / En cours / Terminé / Échec / waiting), header text, discovered count (with plural rules), CTA labels, error messages. All with proper French accents. If you add UI strings, add keys to both files in the same shape — the `useTranslations('run')` hook in `AgentTheater.tsx` shows the pattern.

---

## 14. Specific design directions you might consider

(Pick what resonates with you and the user — these are sparks, not requirements.)

**Agent theater:**
- Replace the 5-column grid with a vertical flow showing data passing between agents (animated dotted line, count chips moving along it)
- Replace emoji icons with custom monoline SVG icons (consistent stroke, single color, sized to match the typography)
- Use a custom typeface for the log feed (something like JetBrains Mono or Berkeley Mono — through Google Fonts) instead of generic `font-mono`
- Add a "campaign chip" at the top of the page showing what's being recruited for (right now no campaign is selected — agents run with `campaign_id=null` which feels like a missed opportunity for context)
- Show provenance: when fit_ranking completes, briefly highlight where each candidate came from (Jobillico/Indeed/CFP de Québec/etc.) with source-colored dots
- Final state should celebrate — a subtle confetti, a "X candidats découverts" tally that counts up, the strong-match count specifically

**Kanban:**
- Source-of-discovery badge on each card (small Jobillico/Indeed/LinkedIn/CFP icon)
- Days-in-stage indicator (e.g. "3j" pill that goes amber after 7d, red after 14d)
- Fit score as a circular progress ring instead of a flat badge
- Hover state showing key qualifications (CCQ / SF1 / halocarbures) as inline chips
- The detail panel can become a full sheet with sections: identity, fit breakdown by rubric criterion (bar chart!), qualifications with confirmed/claimed/inferred status icons, source mentions with URLs, outreach history (empty for now), notes

**Landing:**
- A hero that actually says what the product DOES with an animated diagram (5 agent icons flowing into a candidate pipeline)
- Pull the Seguin Morris brand colors from the logo PNG (blue ~#1F3A8A, orange ~#F97316) and weave them through
- A "powered by CTRL Solutions" treatment in the footer that doesn't apologize — small, refined, confident
- The bilingual toggle should be a single switch, not two pills (cleaner)

**Global:**
- Pick ONE accent color and use it consistently — right now there's neutral-900, emerald-600, amber-300, red-700 sprinkled across pages. Should be 2 brand colors + neutrals only
- Establish a typographic scale (currently inconsistent — some `text-sm` here, `text-xs` there, no system)
- Add a top app shell / nav so the pages feel connected, not orphaned

---

## 15. What to absolutely NOT change

- The data model (20 tables, all relationships sound, migrations applied)
- The vetting reminder text on candidate cards / fit summaries
- The bilingual key structure (extend, don't restructure)
- The hard rules in §3
- The "Designed by CTRL Solutions" footer line — keep it secondary, professional
- The fit score rubric weights (25/20/15/15/10/10/5)
- The CORS lockdown (it's correct; don't loosen to `*`)
- The agent execution sequence (employment_source → school_pipeline → lead_enrichment → candidate_vetting → fit_ranking)

---

## 16. First moves I'd recommend

1. **Read** `/mnt/skills/public/frontend-design/SKILL.md` end to end before opening any code
2. **Open** the live site in a real browser — `https://web-production-3a057.up.railway.app/fr/run` — click the launch button, watch the run, end on the Kanban. Feel where it falls short
3. **Look** at the Seguin Morris logo (`/mnt/project/images.png`) and pull its actual blue+orange into a Tailwind theme extension
4. **Decide** on a typeface pair (one display, one body, one mono) and load them via `next/font/google`
5. **Establish** a design system file in `apps/web/src/styles/` — tokens, scale, the 2 brand colors + 8 neutral stops + 1 success + 1 warning + 1 danger
6. **Rebuild** the agent theater visual layer keeping the existing component contracts (AgentCard takes the same props — just look different)
7. **Then** propagate the system to landing + Kanban

This sequence keeps the working software working while you upgrade the surface. Don't refactor the data flow or the polling logic — they're correct, just unattractive.

---

## 17. If you get stuck on the encoding hellscape

Skip PowerShell entirely. Use this pattern:

```python
# Start a Python REPL once via Desktop Commander:start_process
python -i -u

# Then per-file, send single-line statements:
open(r"C:\path\file.tsx", "w", encoding="utf-8", newline="\n").write(open(r"C:\path\source-snippet.txt").read())
```

Or just use Windows-MCP:PowerShell with the `[IO.File]::WriteAllText` + single-quoted heredoc pattern documented in §11. That worked reliably for every file in this session once I figured it out.

---

## 18. Last note from the previous assistant

The user said this build is for "showing a potential client." That framing matters. It's not a school project that needs to pass an exam — it's a portfolio piece that needs to win business. The current state is *competent*. He wants *compelling*. The gap between those two is exactly the work you're being brought in to do. Don't waste tokens on more backend features — what's there works. Make what's there *look like it costs money*.

Good luck.
