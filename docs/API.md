# API Reference

Base URL: `http://localhost:8000`. Interactive docs (Swagger UI) at `/docs`.
All `/api/*` endpoints except auth require a `Authorization: Bearer <token>` header.

## Auth
| Method | Path | Body | Notes |
|---|---|---|---|
| POST | `/api/auth/register` | `{email, password, full_name?, timezone?}` | Returns `{access_token, user}` |
| POST | `/api/auth/login` | `{email, password}` | Returns `{access_token, user}` |
| GET | `/api/auth/me` | — | Current user |
| PATCH | `/api/auth/me` | `{full_name?, timezone?, reminder_soon_days?}` | Profile & reminder preferences |

## Items
| Method | Path | Notes |
|---|---|---|
| GET | `/api/items` | Filters: `kind, kinds (comma-separated), status, source, course, due_before, due_after, search`. Paginated: `limit` (≤500), `offset`; returns `{items, total, limit, offset, has_more}` |
| POST | `/api/items` | Create a manual item |
| GET | `/api/items/{id}` | Single item (owner-scoped) |
| PATCH | `/api/items/{id}` | Partial update |
| POST | `/api/items/{id}/complete?completed=true` | Toggle completion |
| DELETE | `/api/items/{id}` | Delete |

## Integrations
| Method | Path | Notes |
|---|---|---|
| GET | `/api/integrations/providers` | Provider capability metadata (`label`, `live_supported`, `note`) + demo flag + sync interval |
| GET | `/api/integrations/connections` | List connections with sync state (`sync_status`, `last_synced_at`, `next_sync_at`); secrets never returned |
| POST | `/api/integrations/connections` | `{provider, secrets?}` (upsert). Queues an initial background sync |
| POST | `/api/integrations/connections/{id}/active?active=false` | Enable/disable |
| DELETE | `/api/integrations/connections/{id}` | Disconnect |
| POST | `/api/integrations/sync` | **202**: queues a background sync of all active connections (rate limited). Poll `GET /connections` for progress |

Connections re-sync automatically every `SYNC_INTERVAL_MINUTES` (default 30) while the
server is running; manual sync is an override, not the only refresh path.

## Dashboard & extras
| Method | Path | Notes |
|---|---|---|
| GET | `/api/dashboard` | Stats + reminder buckets + next up (cached) |
| GET | `/api/reminders` | Overdue / today / soon / upcoming |
| GET | `/api/study-tips` | Contextual study tips |
| GET | `/api/health` | Liveness probe |

## Cross-cutting
- **Auth:** JWT (HS256), 7-day expiry by default.
- **Rate limiting:** default `200/min`; auth `20/min`; sync `10/min` (per user, or per IP
  when unauthenticated). Exceeding returns `429`.
- **Caching:** dashboard responses cached in-process for `CACHE_TTL_SECONDS`, invalidated
  on item/sync changes.
- **Errors:** consistent `{ "detail": "<message>" }` with appropriate status codes.
