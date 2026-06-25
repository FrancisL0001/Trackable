"""Trackable FastAPI application entry point."""
from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.api import auth, dashboard, integrations, items
from app.core.config import settings
from app.core.database import init_db
from app.core.errors import TrackableError
from app.core.rate_limit import limiter


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title=f"{settings.app_name} API",
    version="0.1.0",
    description="Unified deadline & task tracker for college students.",
    lifespan=lifespan,
)

# --- Middleware --------------------------------------------------------------
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Exception handlers ------------------------------------------------------
@app.exception_handler(TrackableError)
async def handle_trackable_error(request: Request, exc: TrackableError) -> JSONResponse:
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})


@app.exception_handler(RateLimitExceeded)
async def handle_rate_limit(request: Request, exc: RateLimitExceeded) -> JSONResponse:
    return JSONResponse(
        status_code=429,
        content={"detail": "Rate limit exceeded. Please slow down and try again."},
    )


# --- Routers -----------------------------------------------------------------
app.include_router(auth.router)
app.include_router(items.router)
app.include_router(integrations.router)
app.include_router(dashboard.router)


@app.get("/api/health", tags=["health"])
def health() -> dict:
    return {"status": "ok", "app": settings.app_name, "demo_mode": settings.demo_mode}
