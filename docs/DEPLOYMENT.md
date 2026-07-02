# Deployment Guide

Trackable deploys as two pieces:

- **Backend** (FastAPI) → **Railway** (container, from `server/Dockerfile`)
- **Frontend** (Vite SPA) → **Vercel** (static build, `client/`)

## Security: fail-closed startup
The backend **refuses to start** in any non-development environment unless it is
configured securely (see `server/app/core/startup.py`). In production it requires:

- `SECRET_KEY` — strong, ≥32 chars, not the default.
- `ENCRYPTION_KEY` — a **separate** valid Fernet key (not derived from `SECRET_KEY`).
- `DEBUG=false`.
- `FRONTEND_ORIGIN` (and any `EXTRA_CORS_ORIGINS`) set to real, non-localhost, non-`*`
  origins.

SQLite in production produces a **warning** (not a hard failure): it works only if backed
by a persistent volume; managed Postgres is recommended.

"Production" = any `ENVIRONMENT` other than `development/dev/local/test/testing`. A
detected Railway environment is treated as production by default.

Generate keys:
```bash
# SECRET_KEY
python -c "import secrets; print(secrets.token_urlsafe(48))"
# ENCRYPTION_KEY (Fernet)
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

## Backend on Railway
1. Create a Railway project and a service from this repo.
2. Set the service **Root Directory** to `server` (so it uses `server/Dockerfile`).
3. (Recommended) Add a **Postgres** plugin — Railway injects `DATABASE_URL` automatically.
4. Set service **Variables**:
   - `ENVIRONMENT=production`
   - `DEBUG=false`
   - `SECRET_KEY=<generated>`
   - `ENCRYPTION_KEY=<generated Fernet key>`
   - `FRONTEND_ORIGIN=https://<your-app>.vercel.app`
   - `DEMO_MODE=true` (or `false` to enable live integrations)
   - `DATABASE_URL` is provided by the Postgres plugin; if you keep SQLite, attach a volume.
5. Railway provides `$PORT`; the Dockerfile's `CMD` binds uvicorn to it. Set the
   **healthcheck path** to `/api/health`.
6. Deploy and note the public URL (e.g. `https://trackable-api.up.railway.app`).

> Postgres is fully supported out of the box: `psycopg` (v3) ships in the image, and the
> app normalizes Railway's `postgres://` / `postgresql://` `DATABASE_URL` to the
> `postgresql+psycopg://` dialect automatically. Just add a Postgres plugin — no code or
> env changes needed.

### Database migrations (Alembic)
The production schema is owned by **Alembic**. The container's `CMD` runs
`alembic upgrade head` before starting uvicorn, so deploys apply migrations
automatically; the app refuses to serve in production if tables are missing.
`create_all` is used only for local dev and tests. To evolve the schema:

```bash
cd server
alembic revision -m "add my_column"   # write the migration
alembic upgrade head                   # apply locally
pytest tests/test_system_design.py -k migrations  # parity check vs models
```

### Single worker (required)
The MVP uses an **in-process** cache, rate limiter, and background sync scheduler, all
of which assume exactly one worker process. The Dockerfile starts uvicorn with
`--workers 1`, and the startup guard fails closed if `WEB_CONCURRENCY` (or
`UVICORN_WORKERS`/`GUNICORN_WORKERS`) is set above 1 in production. Do not scale to
multiple instances/replicas without first moving cache + rate limiting to Redis and
sync scheduling to a real queue.

### Data freshness
While the server runs, every active connection re-syncs automatically every
`SYNC_INTERVAL_MINUTES` (default: 30 minutes). Manual "Sync now" is an override.

## Frontend on Vercel
1. Import the repo into Vercel and set the **Root Directory** to `client`.
2. Vercel auto-detects Vite; `client/vercel.json` pins the build command, output
   directory, and the SPA rewrite (so client-side routes survive a refresh).
3. Set the **Environment Variable**:
   - `VITE_API_BASE_URL=https://<your-railway-backend-url>`
   (Build-time variable — the SPA calls the backend directly in production; there is no
   dev proxy.)
4. Deploy. Then make sure the backend's `FRONTEND_ORIGIN` matches the Vercel domain.

## Local container test
```bash
cd server
docker build -t trackable-api .
docker run --rm -p 8000:8000 \
  -e ENVIRONMENT=development \
  trackable-api
# -> http://localhost:8000/api/health
```
To rehearse production locally, pass the production variables shown above; the container
will refuse to start if any required one is missing or insecure.

## Post-deploy checklist
- [ ] Backend `/api/health` returns `{"status":"ok"}`.
- [ ] `FRONTEND_ORIGIN` exactly matches the Vercel domain (no trailing slash).
- [ ] `VITE_API_BASE_URL` points at the Railway URL.
- [ ] `SECRET_KEY` and `ENCRYPTION_KEY` are distinct, strong, and stored only as
      platform secrets (never committed).
- [ ] If using SQLite on Railway, a volume is attached; otherwise Postgres is configured.
