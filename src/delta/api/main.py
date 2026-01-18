"""FastAPI application for DELTA platform."""

from contextlib import asynccontextmanager
from datetime import datetime
from typing import AsyncGenerator

import structlog
from fastapi import FastAPI, WebSocket, Query
from fastapi.middleware.cors import CORSMiddleware

from delta import __version__
from delta.config import get_settings
from delta.api.routes import auth, agents, sandboxes, files, exec, messaging
from delta.api.websocket.terminal import (
    manager as ws_manager,
    user_websocket_endpoint,
    agent_websocket_endpoint,
)

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager."""
    settings = get_settings()
    logger.info("Starting DELTA platform", version=__version__, debug=settings.debug)

    # TODO: Initialize connections
    # - Database pool
    # - Redis connection
    # - Fly.io client
    # - AWS SES client
    # - Twilio client

    yield

    # Cleanup
    logger.info("Shutting down DELTA platform")


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
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/v1/auth", tags=["authentication"])
app.include_router(agents.router, prefix="/v1/agents", tags=["agents"])
app.include_router(sandboxes.router, prefix="/v1/sandboxes", tags=["sandboxes"])
app.include_router(exec.router, prefix="/v1/sandboxes", tags=["execution"])
app.include_router(files.router, prefix="/v1/sandboxes", tags=["files"])
app.include_router(messaging.router, prefix="/v1/messaging", tags=["messaging"])


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

@app.websocket("/v1/ws/user/{agent_id}")
async def websocket_user(
    websocket: WebSocket,
    agent_id: str,
    user_id: str = Query(..., description="User ID"),
):
    """
    WebSocket endpoint for USERS to watch their agent's activity.
    
    Connect: ws://host/v1/ws/user/{agent_id}?user_id={user_id}
    
    Receive messages:
        {"type": "agent_message", "content": "...", "sender": "agent", ...}
        {"type": "status", "content": "Agent connected", ...}
        {"type": "system", "content": "...", ...}
    
    Send messages:
        {"type": "message", "content": "Hello agent!"}
        {"type": "ping"}
    """
    await user_websocket_endpoint(websocket, agent_id, user_id)


@app.websocket("/v1/ws/agent/{agent_id}")
async def websocket_agent(
    websocket: WebSocket,
    agent_id: str,
    api_key: str = Query(..., description="Agent API key"),
):
    """
    WebSocket endpoint for AGENTS to send messages to users.
    
    Connect: ws://host/v1/ws/agent/{agent_id}?api_key={api_key}
    
    Send messages to users:
        {"type": "message", "content": "Hello user!", "msg_type": "agent_message"}
        {"type": "status", "content": "Processing your request..."}
    
    Receive messages from users:
        {"type": "user_message", "content": "...", "sender": "user", ...}
    """
    await agent_websocket_endpoint(websocket, agent_id, api_key)


@app.get("/v1/ws/stats")
async def websocket_stats() -> dict:
    """Get WebSocket connection statistics."""
    return ws_manager.get_stats()
