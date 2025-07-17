"""FluxSort FastAPI application — thin adapter over core modules."""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .routes import scan, sort, history, taxonomy, settings, browse, ai

app = FastAPI(
    title="FluxSort API",
    version="2.0.0",
    description="Smart file organizer with AI-powered classification",
)

# Allow Vite dev-server (port 5173) during development.
# In production everything is same-origin so this is a no-op.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:8765",
        "http://127.0.0.1:8765",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── API routes ──────────────────────────────────────────────────────────────
app.include_router(browse.router, prefix="/api")
app.include_router(scan.router, prefix="/api")
app.include_router(sort.router, prefix="/api")
app.include_router(history.router, prefix="/api")
app.include_router(taxonomy.router, prefix="/api")
app.include_router(settings.router, prefix="/api")
app.include_router(ai.router, prefix="/api")

# ── Health ──────────────────────────────────────────────────────────────────
@app.get("/api/health")
async def health() -> dict:
    return {"status": "ok", "version": "2.0.0"}


# ── Static frontend (React build) ───────────────────────────────────────────
# Served last so /api/* routes always take priority.
_FRONTEND_DIST = Path(__file__).parent.parent.parent / "frontend" / "dist"
if _FRONTEND_DIST.exists():
    app.mount("/", StaticFiles(directory=str(_FRONTEND_DIST), html=True), name="frontend")
