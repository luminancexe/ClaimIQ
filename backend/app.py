"""FastAPI Application Factory for ClaimIQ Phase 7 Backend API."""

from typing import Optional
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.config import BackendConfig
from backend.middleware.errors import RequestIdMiddleware, register_exception_handlers
from backend.routers import (
    health,
    auth,
    claims,
    qa,
    analytics,
    providers,
    payers,
    issues,
)

OPENAPI_TAGS = [
    {"name": "Health", "description": "Liveness, readiness, and connectivity diagnostics."},
    {"name": "Auth", "description": "JWT authentication, token refresh, and user profile."},
    {"name": "Claims", "description": "Claims management, line items, and lifecycle history."},
    {"name": "QA", "description": "Data quality rules, execution runs, results, and scores."},
    {"name": "Analytics", "description": "Financial exposure, KPIs, trends, and scorecards."},
    {"name": "Providers", "description": "Healthcare provider directory and quality scorecards."},
    {"name": "Payers", "description": "Insurance payer directory and adjudication scorecards."},
    {"name": "Issues", "description": "QA-detected data quality defect issues."},
]


def create_app(config: Optional[BackendConfig] = None) -> FastAPI:
    """Construct and configure the ClaimIQ FastAPI application."""
    cfg = config or BackendConfig()

    app = FastAPI(
        title="ClaimIQ API",
        version="0.7.0",
        description="ClaimIQ Healthcare Claims Data Quality & Operations Platform REST API",
        openapi_tags=OPENAPI_TAGS,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    # Store config in app state
    app.state.config = cfg

    # Add Request ID middleware
    app.add_middleware(RequestIdMiddleware)

    # Add CORS middleware
    origins = [o.strip() for o in cfg.cors_origins.split(",") if o.strip()]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins if origins else ["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["X-Request-ID"],
    )

    # Register standardized error handlers
    register_exception_handlers(app)

    # Register routers
    app.include_router(health.router)
    app.include_router(auth.router)
    app.include_router(claims.router)
    app.include_router(qa.router)
    app.include_router(analytics.router)
    app.include_router(providers.router)
    app.include_router(payers.router)
    app.include_router(issues.router)

    return app
