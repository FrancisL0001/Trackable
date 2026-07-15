"""Course-website provider: track assignments posted on a plain web page.

For courses with no calendar feed (many CS course sites just list assignments
in HTML), this provider fetches the page through the SSRF guard, strips it to
text, and asks a configured LLM (local Ollama or a hosted API — see
app/integrations/llm.py) to extract deadlines.

Design notes:
- ``external_id`` is a hash of the normalized title, so re-extraction updates
  existing items instead of duplicating them, and user edits/completions
  survive (see sync_service user-edit protection).
- The page text is hashed; if unchanged since the last sync, the LLM call is
  skipped entirely (``self.unchanged``) — the model only runs when the page
  actually changed.
- Extraction is best-effort: every item keeps a URL back to the page so the
  user can verify with one click.
"""
from __future__ import annotations

import hashlib
import re
from datetime import datetime, timezone
from html.parser import HTMLParser

from app.core.config import settings
from app.core.errors import IntegrationError
from app.core.ssrf import safe_get
from app.integrations import demo_data, llm
from app.integrations.base import Integration, NormalizedItem
from app.models.enums import ItemKind, ItemPriority, ProviderType

_SKIP_TAGS = {"script", "style", "noscript", "svg", "template", "iframe"}

_KIND_MAP = {
    "assignment": ItemKind.ASSIGNMENT,
    "exam": ItemKind.EXAM,
    "deadline": ItemKind.DEADLINE,
    "event": ItemKind.EVENT,
    "task": ItemKind.TASK,
}


class _TextExtractor(HTMLParser):
    """Visible text + anchor hrefs, so the model can attach links to items."""

    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []
        self._skip_depth = 0

    def handle_starttag(self, tag: str, attrs) -> None:
        if tag in _SKIP_TAGS:
            self._skip_depth += 1
        elif tag == "a" and self._skip_depth == 0:
            href = dict(attrs).get("href")
            if href and not href.startswith(("#", "javascript:")):
                self.parts.append(f"[link: {href}]")

    def handle_endtag(self, tag: str) -> None:
        if tag in _SKIP_TAGS and self._skip_depth > 0:
            self._skip_depth -= 1

    def handle_data(self, data: str) -> None:
        if self._skip_depth == 0 and data.strip():
            self.parts.append(data.strip())


def html_to_text(raw: bytes, max_chars: int | None = None) -> str:
    """Visible page text, capped to the configured model budget.

    The cap defaults to LLM_MAX_PAGE_CHARS — sized for the small default
    context window of local model servers (raise it for hosted models).
    """
    parser = _TextExtractor()
    parser.feed(raw.decode("utf-8", errors="replace"))
    text = re.sub(r"\s+", " ", " ".join(parser.parts)).strip()
    return text[: max_chars or settings.llm_max_page_chars]


def _stable_id(title: str) -> str:
    normalized = re.sub(r"\s+", " ", title.lower().strip())
    return "web-" + hashlib.sha1(normalized.encode()).hexdigest()[:16]


def _parse_due(value) -> datetime | None:
    if not value or not isinstance(value, str):
        return None
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    # Course pages rarely carry timezones; treat naive as UTC (app convention).
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


class WebPageIntegration(Integration):
    provider = ProviderType.WEB_PAGE

    def validate(self) -> None:
        if self.demo:
            return
        if not self.secrets.get("url"):
            raise IntegrationError("Course website connection requires a page URL.")
        if not llm.extraction_available():
            raise IntegrationError(
                "Course-website import needs an extraction model. Set LLM_BASE_URL "
                "to an OpenAI-compatible endpoint (e.g. a local Ollama at "
                "http://localhost:11434/v1) or set ANTHROPIC_API_KEY."
            )

    def fetch_items(self) -> list[NormalizedItem]:
        if self.demo:
            return demo_data.web_page_items()
        self.validate()
        url = self.secrets["url"]
        try:
            raw = safe_get(url)
        except Exception as exc:  # httpx errors and SSRF rejections
            if isinstance(exc, IntegrationError):
                raise
            raise IntegrationError(f"Could not fetch the course page: {exc}") from exc

        text = html_to_text(raw)
        if not text:
            raise IntegrationError("The course page has no readable text.")

        self.content_hash = hashlib.sha256(text.encode()).hexdigest()
        if self.previous_hash and self.previous_hash == self.content_hash:
            # Page unchanged since last sync: skip the model call entirely.
            self.unchanged = True
            return []

        items: list[NormalizedItem] = []
        seen: set[str] = set()
        for row in llm.extract_deadlines(text, url):
            title = str(row.get("title", "")).strip()[:500]
            if not title:
                continue
            external_id = _stable_id(title)
            if external_id in seen:
                continue
            seen.add(external_id)
            items.append(
                NormalizedItem(
                    external_id=external_id,
                    title=title,
                    kind=_KIND_MAP.get(str(row.get("kind", "")).lower(), ItemKind.ASSIGNMENT),
                    description=str(row.get("description") or "")[:2000],
                    # Item link if the model found one, else back to the page.
                    url=str(row.get("url") or url)[:1000],
                    due_at=_parse_due(row.get("due_at")),
                    priority=ItemPriority.MEDIUM,
                )
            )
        return items
