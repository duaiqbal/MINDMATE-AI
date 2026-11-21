"""FastAPI application factory.

Registers /health plus the v1 routers. Auth wiring (current user from JWT) and
the Supabase-backed repository are provided via dependency overrides in
production; tests override them with fakes.

CORS allows only the configured frontend origins (default: the Vite dev server).
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import chat, consent, data_rights, health, memory, mood
from app.config import CorsSettings


def create_app(cors: CorsSettings | None = None) -> FastAPI:
    """Build and configure the FastAPI application."""
    app = FastAPI(title="MindMate AI", version="0.0.0")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=(cors or CorsSettings()).origins(),
        allow_methods=["GET", "POST", "PATCH", "DELETE"],
        allow_headers=["Content-Type", "Authorization"],
        allow_credentials=False,
    )
    app.include_router(health.router)
    app.include_router(chat.router)
    app.include_router(mood.router)
    app.include_router(memory.router)
    app.include_router(consent.router)
    app.include_router(data_rights.router)
    return app


app = create_app()