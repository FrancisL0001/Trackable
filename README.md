# Trackable

A productivity hub for college students. Trackable unifies **assignments, deadlines,
events, meetings, tasks, and job applications** into one fast, responsive timeline by
connecting to **Google Calendar, Canvas, Gradescope, and course websites** — then adds
reminders and study tips on top.

- 📅 Unified timeline across all your sources
- ✅ Manual tasks + auto-synced assignments & events (background sync every 30 min)
- 🔌 Integrations: Canvas, Google Calendar (iCal feed), ICS/course-website feeds — plus a Gradescope demo
- ⏰ Smart reminders (overdue / today / soon, with a configurable window) and 💡 study tips
- 📱 Works on mobile and desktop, light & dark themes

> **Demo mode:** Trackable runs fully without any external credentials. Integrations
> return realistic sample data until you provide real keys. See
> [PROJECT_DESCRIPTION.md](PROJECT_DESCRIPTION.md) for the why.

## Tech
- **Frontend:** Vite + React + TypeScript, React Router, TanStack Query, Vitest
- **Backend:** Python + FastAPI, SQLAlchemy (SQLite), JWT auth, SlowAPI rate limiting, Pytest

## Quick start

### Backend
```bash
cd server
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env          # optional; defaults work for demo mode
uvicorn app.main:app --reload # http://localhost:8000  (docs at /docs)
```

### Frontend
```bash
cd client
npm install
cp .env.example .env          # points at http://localhost:8000 by default
npm run dev                   # http://localhost:5173
```

Open http://localhost:5173, register an account, and connect a provider on the
Integrations page (demo providers are enabled by default) — the first sync runs
automatically and your dashboard fills up. Connections keep refreshing in the
background every 30 minutes while the server runs.

## Testing
```bash
# Backend
cd server && source .venv/bin/activate && pytest

# Frontend
cd client && npm test
```

## Project layout
```
server/   FastAPI backend (app/, tests/, Dockerfile)
client/   Vite React frontend (src/, tests via vitest, vercel.json)
docs/     Additional documentation
```

## Deployment
Backend → **Railway** (container via `server/Dockerfile`); frontend → **Vercel**
(static SPA from `client/`). The backend **fails closed**: in production it refuses to
start without a strong `SECRET_KEY`, a separate `ENCRYPTION_KEY`, `DEBUG=false`, and a
real `FRONTEND_ORIGIN`. Full steps in [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md).

## More docs
- [PROJECT_DESCRIPTION.md](PROJECT_DESCRIPTION.md) — vision, architecture, design decisions
- [testing.md](testing.md) — testing plan & strategy
- [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) — Railway + Vercel deployment
- [docs/API.md](docs/API.md) · [docs/INTEGRATIONS.md](docs/INTEGRATIONS.md)
