# Integrations Guide

Trackable connects to external sources through a common adapter interface
(`server/app/integrations/base.py`). Every provider implements `fetch_items()` and
returns `NormalizedItem`s, which the sync service upserts into the unified `Item`
table — idempotently, keyed on `(owner, source, external_id)`.

## Demo mode (default)
With `DEMO_MODE=true` (the default), each provider returns realistic synthetic data so
the entire app is usable without any credentials. Connect a provider on the Integrations
page and click **Sync** to populate your dashboard.

To use live data, set `DEMO_MODE=false` in `server/.env` and supply per-connection
secrets when connecting each provider.

## Providers

### Canvas
- **Real mode:** Canvas REST API with a personal access token.
- **Secrets:** `token` (required), `base_url` (optional, defaults to `CANVAS_BASE_URL`).
- **How to get a token:** Canvas → Account → Settings → "New Access Token".
- Pulls assignments (with due dates and URLs) across your active courses.

### Google Calendar
- **Real mode:** parses your calendar's **secret iCal URL**.
- **Secrets:** `ical_url` (required).
- **How to get it:** Google Calendar → Settings → your calendar → "Secret address in
  iCal format".
- Full OAuth2 in-app is intentionally out of scope for the MVP (see
  [PROJECT_DESCRIPTION.md](../PROJECT_DESCRIPTION.md)).

### Gradescope
- **Real mode:** not enabled in this build (Gradescope has no official API; live
  scraping is brittle). Returns sample data in demo mode.
- **Workaround:** if your course exposes a Gradescope ICS feed, import it via the ICS
  provider.

### Course websites (ICS)
- **Real mode:** downloads and parses any iCalendar (`.ics`) feed.
- **Secrets:** `url` (required).
- Works with most LMS/course-website calendar exports.

## Adding a new provider
1. Create `server/app/integrations/<name>.py` subclassing `Integration`.
2. Implement `fetch_items()` (and `validate()` for required secrets).
3. Register it in `server/app/integrations/registry.py` and add the enum value in
   `server/app/models/enums.py:ProviderType`.
4. Add demo data in `server/app/integrations/demo_data.py`.
5. Add display metadata in `client/src/components/itemMeta.ts` and list it in
   `client/src/pages/Integrations.tsx`.
