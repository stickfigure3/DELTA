"""FastAPI application for DELTA platform."""

import os
from contextlib import asynccontextmanager
from datetime import datetime
from typing import AsyncGenerator

from fastapi import FastAPI, WebSocket, Query
from fastapi.middleware.cors import CORSMiddleware

# Version
__version__ = "0.1.0"


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager."""
    print(f"Starting DELTA platform v{__version__}")
    yield
    print("Shutting down DELTA platform")


app = FastAPI(
    title="DELTA Platform",
    description="Cloud-based sandbox-as-a-service for self-improving LLM agents",
    version=__version__,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import routes lazily to avoid startup errors
try:
    from delta.api.routes import auth, agents, sandboxes, files, exec, messaging
    app.include_router(auth.router, prefix="/v1/auth", tags=["authentication"])
    app.include_router(agents.router, prefix="/v1/agents", tags=["agents"])
    app.include_router(sandboxes.router, prefix="/v1/sandboxes", tags=["sandboxes"])
    app.include_router(exec.router, prefix="/v1/sandboxes", tags=["execution"])
    app.include_router(files.router, prefix="/v1/sandboxes", tags=["files"])
    app.include_router(messaging.router, prefix="/v1/messaging", tags=["messaging"])
except Exception as e:
    print(f"Warning: Could not load some routes: {e}")

# Import WebSocket handlers lazily
try:
    from delta.api.websocket.terminal import (
        manager as ws_manager,
        user_websocket_endpoint,
        agent_websocket_endpoint,
    )
    WS_ENABLED = True
except Exception as e:
    print(f"Warning: WebSocket not available: {e}")
    WS_ENABLED = False
    ws_manager = None


@app.get("/health")
async def health_check() -> dict:
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": __version__,
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.get("/")
async def root() -> dict:
    """Root endpoint with API information."""
    return {
        "name": "DELTA Platform",
        "version": __version__,
        "description": "Cloud-based sandbox-as-a-service for self-improving LLM agents",
        "docs": "/docs",
        "health": "/health",
        "websocket": {
            "user": "/v1/ws/user/{agent_id}?user_id={user_id}",
            "agent": "/v1/ws/agent/{agent_id}?api_key={api_key}",
        },
        "google_doc": "https://docs.google.com/document/d/1lGc8EZbQq5pW0jq3Lgl95sk9RQMQiHCXZjQMIdIdP98/edit",
    }


# =============================================================================
# WebSocket Endpoints - Agent-to-User Communication
# =============================================================================

if WS_ENABLED:
    @app.websocket("/v1/ws/user/{agent_id}")
    async def websocket_user(
        websocket: WebSocket,
        agent_id: str,
        user_id: str = Query(..., description="User ID"),
    ):
        """WebSocket endpoint for USERS to watch their agent's activity."""
        await user_websocket_endpoint(websocket, agent_id, user_id)

    @app.websocket("/v1/ws/agent/{agent_id}")
    async def websocket_agent(
        websocket: WebSocket,
        agent_id: str,
        api_key: str = Query(..., description="Agent API key"),
    ):
        """WebSocket endpoint for AGENTS to send messages to users."""
        await agent_websocket_endpoint(websocket, agent_id, api_key)

    @app.get("/v1/ws/stats")
    async def websocket_stats() -> dict:
        """Get WebSocket connection statistics."""
        return ws_manager.get_stats()
