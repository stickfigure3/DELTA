"""FastAPI application for DELTA platform - Minimal Production Version."""

import os
from datetime import datetime
from fastapi import FastAPI, WebSocket, Query
from fastapi.middleware.cors import CORSMiddleware

__version__ = "0.1.0"

app = FastAPI(
    title="DELTA Platform",
    description="Cloud-based sandbox-as-a-service for self-improving LLM agents",
    version=__version__,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =============================================================================
# Core Endpoints (Always Available)
# =============================================================================

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": __version__,
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "DELTA Platform",
        "version": __version__,
        "status": "running",
        "docs": "/docs",
        "health": "/health",
    }


# =============================================================================
# Try to load full routes (graceful degradation)
# =============================================================================

routes_loaded = []
routes_failed = []

def try_load_route(module_path, router_attr, prefix, tags):
    """Try to load a route, gracefully handle failures."""
    global routes_loaded, routes_failed
    try:
        module = __import__(module_path, fromlist=[router_attr])
        router = getattr(module, router_attr)
        app.include_router(router, prefix=prefix, tags=tags)
        routes_loaded.append(prefix)
    except Exception as e:
        routes_failed.append({"prefix": prefix, "error": str(e)})

# Load routes
try_load_route("delta.api.routes.auth", "router", "/v1/auth", ["authentication"])
try_load_route("delta.api.routes.agents", "router", "/v1/agents", ["agents"])
try_load_route("delta.api.routes.sandboxes", "router", "/v1/sandboxes", ["sandboxes"])
try_load_route("delta.api.routes.exec", "router", "/v1/sandboxes", ["execution"])
try_load_route("delta.api.routes.files", "router", "/v1/sandboxes", ["files"])
try_load_route("delta.api.routes.messaging", "router", "/v1/messaging", ["messaging"])


@app.get("/v1/status")
async def api_status():
    """Check which routes are loaded."""
    return {
        "routes_loaded": routes_loaded,
        "routes_failed": routes_failed,
    }


# =============================================================================
# WebSocket (for agent-to-user communication)
# =============================================================================

# Simple in-memory message store
connections = {}
messages = {}


@app.websocket("/v1/ws/user/{agent_id}")
async def websocket_user(websocket: WebSocket, agent_id: str, user_id: str = Query("anonymous")):
    """WebSocket for users to watch their agent."""
    await websocket.accept()
    
    if agent_id not in connections:
        connections[agent_id] = {"users": set(), "agent": None}
    connections[agent_id]["users"].add(websocket)
    
    await websocket.send_json({"type": "connected", "agent_id": agent_id})
    
    try:
        while True:
            data = await websocket.receive_json()
            # Forward user message to agent
            if connections[agent_id]["agent"]:
                await connections[agent_id]["agent"].send_json({
                    "type": "user_message",
                    "content": data.get("content", ""),
                    "user_id": user_id,
                })
    except:
        connections[agent_id]["users"].discard(websocket)


@app.websocket("/v1/ws/agent/{agent_id}")
async def websocket_agent(websocket: WebSocket, agent_id: str, api_key: str = Query("test")):
    """WebSocket for agents to send messages to users."""
    await websocket.accept()
    
    if agent_id not in connections:
        connections[agent_id] = {"users": set(), "agent": None}
    connections[agent_id]["agent"] = websocket
    
    await websocket.send_json({"type": "connected", "agent_id": agent_id})
    
    try:
        while True:
            data = await websocket.receive_json()
            # Broadcast to all users watching this agent
            dead = set()
            for user_ws in connections[agent_id]["users"]:
                try:
                    await user_ws.send_json({
                        "type": "agent_message",
                        "content": data.get("content", ""),
                        "agent_id": agent_id,
                    })
                except:
                    dead.add(user_ws)
            connections[agent_id]["users"] -= dead
    except:
        connections[agent_id]["agent"] = None


@app.get("/v1/ws/stats")
async def ws_stats():
    """WebSocket stats."""
    return {
        "agents": list(connections.keys()),
        "total_connections": sum(len(c["users"]) + (1 if c["agent"] else 0) for c in connections.values()),
    }


# Startup message
print(f"DELTA Platform v{__version__} starting...")
print(f"Routes loaded: {routes_loaded}")
if routes_failed:
    print(f"Routes failed: {routes_failed}")
