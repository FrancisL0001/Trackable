# Trackable backend image — intended for Railway (or any container host).
# Build context must be the `server/` directory.
FROM python:3.13-slim AS base

# Faster, quieter, reproducible Python in containers.
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Install dependencies first for better layer caching. Copying only the project
# metadata means dependency installs are cached until pyproject.toml changes.
COPY pyproject.toml ./
COPY app ./app
RUN pip install --upgrade pip && pip install .

# Migration tooling (schema is applied at container start, see CMD).
COPY alembic.ini ./
COPY alembic ./alembic

# Run as an unprivileged user.
RUN useradd --create-home --uid 10001 appuser
USER appuser

# Railway injects $PORT; default to 8000 for local `docker run`.
ENV PORT=8000
EXPOSE 8000

# Lightweight container healthcheck hitting the liveness endpoint. urlopen raises
# (non-zero exit) on any non-2xx response. Single quotes avoid quote-escaping issues.
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import os,urllib.request; urllib.request.urlopen('http://127.0.0.1:'+os.environ.get('PORT','8000')+'/api/health', timeout=3)"

# Apply migrations, then serve. Exactly ONE worker: the in-process cache, rate
# limiter, and sync scheduler assume a single process (enforced at startup).
# Shell form so ${PORT} is expanded at runtime.
CMD alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port ${PORT} --workers 1
