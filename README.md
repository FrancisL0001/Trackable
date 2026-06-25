# Trackable

A productivity hub for college students. Trackable unifies **assignments, deadlines,
events, meetings, tasks, and job applications** into one fast, responsive timeline by
connecting to **Google Calendar, Canvas, Gradescope, and course websites** — then adds
reminders and study tips on top.

- 📅 Unified timeline across all your sources
- ✅ Manual tasks + auto-synced assignments & events
- 🔌 Integrations: Canvas, Google Calendar, Gradescope, ICS/course-website feeds
- ⏰ Smart reminders (overdue / today / soon) and 💡 study tips
- 📱 Works on mobile and desktop

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

Open http://localhost:5173, register an account, click **Sync** on the Integrations
page (demo providers are enabled by default), and your dashboard fills up.

## Testing
```bash
# Backend
cd server && source .venv/bin/activate && pytest

# Frontend
cd client && npm test
```

## Project layout
```
server/   FastAPI backend (app/, tests/)
client/   Vite React frontend (src/, tests via vitest)
docs/     Additional documentation
```

## More docs
- [PROJECT_DESCRIPTION.md](PROJECT_DESCRIPTION.md) — vision, architecture, design decisions
- [testing.md](testing.md) — testing plan & strategy
- [docs/](docs/) — deeper guides (integrations, API)
