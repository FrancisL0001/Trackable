"""Backend-agnostic LLM client for extracting deadlines from course-page text.

Two transports, chosen by configuration:

- ``LLM_BASE_URL``: any OpenAI-compatible chat endpoint. This covers local,
  keyless models via Ollama (http://localhost:11434/v1), LM Studio, and vLLM,
  as well as hosted OpenAI-compatible providers (``LLM_API_KEY`` optional).
- ``ANTHROPIC_API_KEY``: the Anthropic Messages API (used only when no
  ``LLM_BASE_URL`` is configured).

If neither is set, extraction is unavailable and the course-website provider
is demo-only.
"""
from __future__ import annotations

import json
import re
from datetime import datetime

import httpx

from app.core.config import settings
from app.core.errors import IntegrationError
from app.core.timeutils import utcnow

DEFAULT_ANTHROPIC_MODEL = "claude-haiku-4-5-20251001"
DEFAULT_OPENAI_COMPAT_MODEL = "qwen2.5:7b"
# Local models can be slow; give them room.
REQUEST_TIMEOUT = 120

# Instructions come AFTER the page text: local model servers (e.g. Ollama)
# truncate long prompts to a small context window from the front, and the
# instructions are the part that must survive.
_PROMPT = """\
PAGE TEXT from {source_url} (today is {today}):
{text}

END OF PAGE TEXT.

You extract coursework deadlines from the college course page text above.

Return ONLY a JSON object (no prose, no markdown fences) of this exact shape:
{{"items": [{{"title": string, "due_at": "YYYY-MM-DDTHH:MM:SS" or null,
"kind": "assignment" or "exam" or "deadline" or "event" or "task",
"url": absolute URL or null, "description": short string or ""}}]}}

Rules:
- Include assignments, projects, labs, exams, and hard deadlines. Skip lecture
  topics and readings without a due date.
- Infer the year from today's date (course pages rarely state it). If only a
  date is given, use 23:59:00 as the time.
- If the page has no deadlines, return {{"items": []}}.
- At most 50 items.
"""


def extraction_available() -> bool:
    return bool(settings.llm_base_url or settings.anthropic_api_key)


def extraction_backend() -> str:
    """Human-readable label of the configured backend (for status/notes)."""
    if settings.llm_base_url:
        return f"OpenAI-compatible ({settings.llm_base_url})"
    if settings.anthropic_api_key:
        return "Anthropic API"
    return "none"


def _chat_openai_compatible(prompt: str) -> str:
    headers = {"Content-Type": "application/json"}
    if settings.llm_api_key:
        headers["Authorization"] = f"Bearer {settings.llm_api_key}"
    url = settings.llm_base_url.rstrip("/") + "/chat/completions"
    resp = httpx.post(
        url,
        headers=headers,
        json={
            "model": settings.llm_model or DEFAULT_OPENAI_COMPAT_MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0,
            # Constrain small local models (Ollama/LM Studio/vLLM) to valid JSON.
            "response_format": {"type": "json_object"},
        },
        timeout=REQUEST_TIMEOUT,
    )
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]


def _chat_anthropic(prompt: str) -> str:
    resp = httpx.post(
        "https://api.anthropic.com/v1/messages",
        headers={
            "x-api-key": settings.anthropic_api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json",
        },
        json={
            "model": settings.llm_model or DEFAULT_ANTHROPIC_MODEL,
            "max_tokens": 4096,
            "messages": [{"role": "user", "content": prompt}],
        },
        timeout=REQUEST_TIMEOUT,
    )
    resp.raise_for_status()
    return resp.json()["content"][0]["text"]


def _parse_items(raw: str) -> list[dict]:
    """Extract the items list from a model response.

    Tolerates markdown fences, surrounding prose, and either shape:
    ``{"items": [...]}`` (requested) or a bare ``[...]`` array.
    """
    text = raw.strip()
    if text.startswith("```"):
        text = re.sub(r"^```[a-zA-Z]*\s*|\s*```$", "", text).strip()
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        # Fall back to the outermost JSON object/array embedded in prose.
        start = min((i for i in (text.find("{"), text.find("[")) if i != -1), default=-1)
        end = max(text.rfind("}"), text.rfind("]"))
        if start == -1 or end <= start:
            raise ValueError("no JSON in model response")
        data = json.loads(text[start : end + 1])
    if isinstance(data, dict):
        if "items" not in data:
            # Valid JSON but not our schema: the model ignored instructions.
            # Fail loudly rather than reporting a clean "no deadlines found".
            raise ValueError("model response does not follow the items schema")
        data = data["items"]
    if not isinstance(data, list):
        raise ValueError("model response has no items list")
    return [d for d in data if isinstance(d, dict) and d.get("title")]


def extract_deadlines(
    text: str, source_url: str, now: datetime | None = None
) -> list[dict]:
    """Ask the configured model for deadlines in the page text.

    Returns raw dicts (title/due_at/kind/url/description); the web_page
    integration maps them onto NormalizedItems.
    """
    if not extraction_available():
        raise IntegrationError(
            "No extraction model is configured. Set LLM_BASE_URL to an "
            "OpenAI-compatible endpoint (e.g. Ollama: http://localhost:11434/v1) "
            "or set ANTHROPIC_API_KEY."
        )
    prompt = _PROMPT.format(
        today=(now or utcnow()).strftime("%A, %B %d, %Y"),
        source_url=source_url,
        text=text,
    )
    try:
        if settings.llm_base_url:
            raw = _chat_openai_compatible(prompt)
        else:
            raw = _chat_anthropic(prompt)
    except httpx.HTTPError as exc:
        raise IntegrationError(f"Extraction model request failed: {exc}") from exc
    try:
        return _parse_items(raw)
    except (ValueError, json.JSONDecodeError) as exc:
        raise IntegrationError(
            f"Could not parse the extraction model's response: {exc}"
        ) from exc
