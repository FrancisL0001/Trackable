# Trackable — Project Description (Internal Source of Truth)

## Vision
Trackable is a productivity hub for college students. It consolidates assignments,
deadlines, events, meetings, tasks, and job applications into a single, fast,
responsive (mobile + desktop) app. It connects to the tools students already use —
Google Calendar, Canvas (LMS), Gradescope, and arbitrary course websites (via
calendar/ICS feeds) — normalizes everything into a unified timeline, and layers on
reminders and study tips.

## Goals
- One unified inbox/timeline of everything due, across many sources.
- Frictionless onboarding: connect accounts, auto-sync, done.
- Helpful, not noisy: smart reminders + actionable study tips.
- Production-ready quality at small scale (target ~1000 users), not hyperscale.
- Strong separation of concerns; testable core logic independent of FastAPI/React.

## Scope & Audience
College students juggling multiple courses and external deadlines.
Target capacity: ~1000 users. This drives technology choices: SQLite is sufficient,
in-process caching and rate limiting are acceptable, no need for distributed infra.

## Architecture
Two components, each independently runnable:

### Backend (`server/`) — Python + FastAPI
- **Layered**: `models` (SQLAlchemy ORM) → `services` (business logic, no transport) →
  `api` (routers, thin handlers) . Pydantic `schemas` define all request/response
  contracts. Core logic and integration adapters are testable without HTTP.
- **Integrations** (`integrations/`): a common `Integration` adapter interface with
  concrete providers: Canvas (REST + token), Google Calendar (OAuth2/ICS), Gradescope
  (scrape), and a generic ICS importer for course websites. Each provider can run in
  **demo mode** returning realistic synthetic data so the whole app is runnable with
  zero external credentials.
- **Sync service** pulls from connected providers and upserts normalized `Item`s.
- **Cross-cutting**: JWT auth, SlowAPI rate limiting, in-memory TTL cache, structured
  error handling, CORS.
- **Persistence**: SQLite via SQLAlchemy (file DB; easily swappable to Postgres later).

### Frontend (`client/`) — Vite + React + TypeScript
- **Multi-page** via React Router: Login/Register, Dashboard, Calendar, Assignments,
  Tasks, Events, Integrations/Settings, Study Tips.
- **Responsive**: mobile (bottom nav) and desktop (sidebar) layouts from one codebase.
- **Server state** via TanStack Query; **auth state** via React Context.
- Thin typed API client wrapping `fetch`. Design system with CSS variables (light/dark).

## Key Design Decisions (non-obvious)
1. **Demo mode by default.** Real integrations need OAuth secrets / live accounts /
   scraping that cannot be provisioned in a generic environment. To keep the product
   *runnable end-to-end*, every provider has a demo implementation gated by env flags.
   Real credentials activate real clients. This keeps the integration *architecture*
   real and production-shaped while remaining demonstrable.
2. **Unified `Item` model.** Assignments/events/tasks/jobs/meetings are stored as one
   polymorphic `Item` with a `kind` discriminator + `source` provenance. This makes the
   timeline, reminders, and filtering uniform. Manual user tasks are first-class Items.
3. **SQLite + SQLAlchemy.** Sufficient for ~1000 users; zero-ops; swap to Postgres by
   changing one URL. Alembic omitted for MVP (create_all); noted as future work.
4. **In-process cache + rate limit.** Single-instance deployment assumed at this scale.
   Redis noted as the scale-out path.
5. **Gradescope has no official API** — the provider is structured for scraping but ships
   demo data; real scraping requires user-supplied credentials and is best-effort.

## Security
- Passwords hashed with bcrypt (passlib). JWT (HS256) access tokens.
- Integration secrets stored encrypted at rest (Fernet) in the DB, never returned to
  the client. `.env` holds the app secret + encryption key.
- Rate limiting on auth and sync endpoints.

## Out of Scope (MVP)
- Push/email notification delivery (reminders are computed + surfaced in-app; delivery
  hooks are stubbed behind a service interface).
- Real-time websockets, multi-tenant orgs, mobile native apps.
- Database migrations tooling (Alembic) — using create_all for now.

## Future Work
- Postgres + Alembic migrations; Redis cache/rate-limit; background scheduler (APScheduler/Celery)
  for periodic sync + notification delivery; full OAuth flows in-app; ML-based priority ranking.
