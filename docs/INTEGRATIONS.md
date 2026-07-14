# Integrations Guide

Trackable connects to external sources through a common adapter interface
(`server/app/integrations/base.py`). Every provider implements `fetch_items()` and
returns `NormalizedItem`s, which the sync service upserts into the unified `Item`
table — idempotently, keyed on `(owner, source, external_id)`.

## Demo mode (default)
With `DEMO_MODE=true` (the default), each provider returns realistic synthetic data so
the entire app is usable without any credentials. Connecting a provider on the
Integrations page immediately queues its first sync.

To use live data, set `DEMO_MODE=false` in `server/.env` and supply per-connection
secrets when connecting each provider. Providers that cannot sync live (currently
Gradescope) are hidden in live mode — `GET /api/integrations/providers` reports each
provider's `live_supported` capability so the client never offers a connection that
would always fail.

## Background sync
Sync never runs inside an API request. `POST /api/integrations/sync` (and connecting a
provider) queue background work; each connection tracks `sync_status`
(`idle → queued → running → ok | partial | error`), `last_synced_at`, `next_sync_at`,
and `last_sync_error`. A single in-process scheduler re-syncs every active connection
each `SYNC_INTERVAL_MINUTES` (default 30) while the server runs, so data stays fresh
without manual syncs. Partial results (e.g. a paginated Canvas response that hit the
page budget) are reported as `partial`, never silently as success.

## URL safety (SSRF protection)
Any provider URL the server fetches (`url`, `ical_url`, `base_url`) is constrained to
prevent server-side request forgery (`server/app/core/ssrf.py`):

- **https only** — `http://` and other schemes are rejected.
- The host must resolve to a **public IP**; loopback, private, link-local, multicast,
  reserved ranges, and the cloud metadata address `169.254.169.254` are blocked.
- Redirects are followed manually and **re-validated at every hop** (no blind redirects).
- A response size cap is enforced before parsing.
- For Canvas, redirects are disabled so the bearer token can never be forwarded to
  another origin, and the base URL is validated before the token is attached.

Scheme/host are checked when you save a connection (fast feedback); the full
DNS + IP check runs again at sync time.

## Providers

### Canvas
- **Real mode:** Canvas REST API with a personal access token.
- **Secrets:** `token` (required), `base_url` (optional, defaults to `CANVAS_BASE_URL`).
- **How to get a token:** Canvas → Account → Settings → "New Access Token".
- Pulls assignments (with due dates and URLs) across your active courses, following
  Canvas `Link`-header pagination (up to a 20-page budget per endpoint; hitting the
  budget marks the sync `partial` instead of silently truncating).

### Google Calendar (iCal feed)
- **Real mode:** parses your calendar's **secret iCal URL** — this is a feed import,
  not an OAuth account integration, and it is labeled that way in the product.
- **Secrets:** `ical_url` (required).
- **How to get it:** Google Calendar → Settings → your calendar → "Secret address in
  iCal format".
- No calendar selection, revocation, or incremental sync; full OAuth2 is intentionally
  out of scope for the MVP (see [PROJECT_DESCRIPTION.md](../PROJECT_DESCRIPTION.md)).

### Gradescope (demo-only)
- **Real mode:** not available (`live_supported: false`) — Gradescope has no official
  API and live scraping is brittle. The provider is hidden when `DEMO_MODE=false`, and
  the server rejects live connection attempts.
- **Workaround:** if your course exposes a Gradescope ICS feed, import it via the ICS
  provider.

### Course websites (ICS)
- **Real mode:** downloads and parses any iCalendar (`.ics`) feed.
- **Secrets:** `url` (required).
- Works with most LMS/course-website calendar exports.

## Field ownership: sync vs. user edits
Synced items mix provider-owned fields (`title`, `description`, `kind`, `course`,
`location`, `url`, `start_at`, `due_at`) with user-owned ones (`status`, `priority`,
`completed_at`). When a user edits a provider-owned field on a synced item, that field
is recorded in `Item.user_edited_fields` and **preserved on every future sync** — the
provider's version no longer overwrites it. User-owned fields are never touched by sync.

## Adding a new provider
1. Create `server/app/integrations/<name>.py` subclassing `Integration`.
2. Implement `fetch_items()` (and `validate()` for required secrets).
3. Register it in `server/app/integrations/registry.py` and add the enum value in
   `server/app/models/enums.py:ProviderType`.
4. Add demo data in `server/app/integrations/demo_data.py`.
5. Add display metadata in `client/src/components/itemMeta.ts` and list it in
   `client/src/pages/Integrations.tsx`.
