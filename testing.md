# Trackable — Testing Plan & Strategy

This document is the long-term quality and regression log. It is independent of code
structure. Backend tests use **pytest**; frontend tests use **vitest** + Testing Library.

## Philosophy
- Test real behavior and invariants, not implementation details.
- Core logic (services, integrations, normalization) is tested without HTTP/React.
- API tests cover success **and** failure paths via FastAPI's TestClient.
- New bugs get a reproducing regression test before the fix.

## Key Behaviors & Invariants
### Auth
- Register creates a user; duplicate email is rejected (409).
- Login returns a JWT only for correct credentials; wrong password → 401.
- Protected endpoints reject missing/invalid tokens (401).
- Passwords are never stored in plaintext and never returned.

### Items (assignments/events/tasks/jobs/meetings)
- Creating a manual item persists it and scopes it to the owner.
- Users can only read/update/delete their own items (no cross-user access).
- Completing an item sets `completed_at`; toggling is idempotent per state.
- Listing supports filtering by kind, status, and date range.

### Integrations / Sync
- Each provider in demo mode returns deterministic, well-formed items.
- Sync upserts: re-syncing the same source does not create duplicates
  (idempotent on `(source, external_id)`).
- Disconnecting a provider stops it contributing items on next sync.
- Secrets submitted for a connection are never echoed back in API responses.

### Reminders
- Reminders are derived from item due dates relative to "now".
- Overdue, due-today, due-soon buckets are computed correctly across boundaries.

### Study tips
- Tips endpoint returns a non-empty, varied set; deterministic given a seed.

### Cross-cutting
- Rate limiter returns 429 after the configured threshold.
- Cache returns identical results within TTL and refreshes after expiry.
- CORS allows the configured frontend origin.

### Security hardening (added)
- Production config guard (`app/core/startup.py`): development never blocks; production
  fails closed on default/short `SECRET_KEY`, missing/invalid `ENCRYPTION_KEY`,
  `DEBUG=true`, and localhost/`*` CORS origins. SQLite in production warns, not fatal.
  (`tests/test_startup.py`)
- URL safety: only `http(s)` links are accepted on items; unsafe schemes
  (`javascript:`, `data:`, protocol-relative, malformed) are rejected (422) or stripped
  from synced data. Client `safeHref` renders links only for safe schemes.
  (`tests/test_urls.py`, `client/src/utils/url.test.ts`)
- SSRF protection for integration URLs (`app/core/ssrf.py`): https-only; blocks
  loopback/private/link-local/multicast/reserved IPs and the cloud metadata address;
  re-validates on redirect; size-capped. Connect-time scheme validation returns 400 for
  non-https/unsafe provider URLs. (`tests/test_ssrf.py`, `tests/test_integrations.py`)
- DATABASE_URL normalization: `postgres://` / `postgresql://` are rewritten to the
  `postgresql+psycopg://` dialect; SQLite untouched. (`tests/test_database_url.py`)

### Test isolation
- The rate limiter is disabled in pytest (process-global in-memory storage otherwise
  leaks across tests); rate limiting is verified at the HTTP layer instead.

## Edge Cases / Inputs That Must Never Break
- Empty/whitespace titles rejected with 422.
- Due dates in the past accepted (overdue) but flagged.
- Very long titles truncated/validated, not crashing.
- Timezone-aware vs naive datetimes normalized to UTC.
- Sync with zero connected providers returns empty, not error.

## Frontend Behaviors
- Auth context redirects unauthenticated users to /login.
- Dashboard renders loading, empty, and populated states.
- Forms validate required fields before submit.
- Responsive layout switches nav style at the mobile breakpoint.
- API client attaches the auth token and handles 401 by logging out.

## Bug Log
_(Register discovered bugs here with a clear description and the regression test added.)_
- _None yet._
