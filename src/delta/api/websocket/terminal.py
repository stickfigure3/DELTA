"""WebSocket terminal for agent-to-user real-time communication.

This is the core communication layer that allows:
1. AI agents to connect and send messages to users
2. Users to receive real-time updates from their agents
3. Bidirectional communication for interactive sessions
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, Optional, Set
from uuid import UUID, uuid4

from fastapi import WebSocket, WebSocketDisconnect
from pydantic import BaseModel


class Message(BaseModel):
    """A message in the agent-user communication."""
    id: str
    type: str  # "agent_message", "user_message", "system", "status"
    content: str
    sender: str  # "agent", "user", "system"
    agent_id: Optional[str] = None
    timestamp: str
    metadata: Optional[dict] = None


class ConnectionManager:
    """
    Manages WebSocket connections between agents and users.
    
    Connection Types:
    - User connections: Users watching their agent's activity
    - Agent connections: Agents sending updates to users
    
    Flow:
    1. User connects via WebSocket to watch an agent
    2. Agent connects via WebSocket to send messages
    3. Messages from agent are broadcast to all watching users
    """
    
    def __init__(self):
        # Map: agent_id -> set of user websockets watching that agent
        self.user_connections: Dict[str, Set[WebSocket]] = {}
        
        # Map: agent_id -> agent websocket
        self.agent_connections: Dict[str, WebSocket] = {}
        
        # Message history (in-memory for now, should be Redis in prod)
        self.message_history: Dict[str, list] = {}
        
        # Connection metadata
        self.connection_info: Dict[WebSocket, dict] = {}
    
    async def connect_user(self, websocket: WebSocket, agent_id: str, user_id: str):
        """Connect a user to watch an agent's activity."""
        await websocket.accept()
        
        if agent_id not in self.user_connections:
            self.user_connections[agent_id] = set()
        
        self.user_connections[agent_id].add(websocket)
        self.connection_info[websocket] = {
            "type": "user",
            "user_id": user_id,
            "agent_id": agent_id,
            "connected_at": datetime.utcnow().isoformat(),
        }
        
        # Send connection confirmation
        await self.send_to_user(websocket, Message(
            id=str(uuid4()),
            type="system",
            content=f"Connected to agent {agent_id}",
            sender="system",
            agent_id=agent_id,
            timestamp=datetime.utcnow().isoformat(),
        ))
        
        # Send recent message history
        if agent_id in self.message_history:
            for msg in self.message_history[agent_id][-50:]:  # Last 50 messages
                await self.send_to_user(websocket, Message(**msg))
    
    async def connect_agent(self, websocket: WebSocket, agent_id: str, api_key: str):
        """Connect an agent to send messages to users."""
        await websocket.accept()
        
        # TODO: Validate API key
        
        self.agent_connections[agent_id] = websocket
        self.connection_info[websocket] = {
            "type": "agent",
            "agent_id": agent_id,
            "connected_at": datetime.utcnow().isoformat(),
        }
        
        # Notify watching users
        await self.broadcast_to_users(agent_id, Message(
            id=str(uuid4()),
            type="status",
            content="Agent connected",
            sender="system",
            agent_id=agent_id,
            timestamp=datetime.utcnow().isoformat(),
        ))
    
    def disconnect(self, websocket: WebSocket):
        """Disconnect a websocket (user or agent)."""
        info = self.connection_info.get(websocket)
        if not info:
            return
        
        if info["type"] == "user":
            agent_id = info["agent_id"]
            if agent_id in self.user_connections:
                self.user_connections[agent_id].discard(websocket)
        
        elif info["type"] == "agent":
            agent_id = info["agent_id"]
            if agent_id in self.agent_connections:
                del self.agent_connections[agent_id]
        
        del self.connection_info[websocket]
    
    async def send_to_user(self, websocket: WebSocket, message: Message):
        """Send a message to a specific user."""
        try:
            await websocket.send_json(message.model_dump())
        except Exception:
            pass  # Connection might be closed
    
    async def broadcast_to_users(self, agent_id: str, message: Message):
        """Broadcast a message to all users watching an agent."""
        # Store in history
        if agent_id not in self.message_history:
            self.message_history[agent_id] = []
        self.message_history[agent_id].append(message.model_dump())
        
        # Keep only last 100 messages per agent
        if len(self.message_history[agent_id]) > 100:
            self.message_history[agent_id] = self.message_history[agent_id][-100:]
        
        # Broadcast to all watching users
        if agent_id in self.user_connections:
            dead_connections = set()
            for websocket in self.user_connections[agent_id]:
                try:
                    await websocket.send_json(message.model_dump())
                except Exception:
                    dead_connections.add(websocket)
            
            # Clean up dead connections
            for ws in dead_connections:
                self.disconnect(ws)
    
    async def send_from_agent(self, agent_id: str, content: str, msg_type: str = "agent_message", metadata: dict = None):
        """Send a message from an agent to all watching users."""
        message = Message(
            id=str(uuid4()),
            type=msg_type,
            content=content,
            sender="agent",
            agent_id=agent_id,
            timestamp=datetime.utcnow().isoformat(),
            metadata=metadata,
        )
        await self.broadcast_to_users(agent_id, message)
        return message
    
    async def send_from_user(self, agent_id: str, user_id: str, content: str):
        """Send a message from a user to the agent."""
        message = Message(
            id=str(uuid4()),
            type="user_message",
            content=content,
            sender="user",
            agent_id=agent_id,
            timestamp=datetime.utcnow().isoformat(),
            metadata={"user_id": user_id},
        )
        
        # Store in history
        if agent_id not in self.message_history:
            self.message_history[agent_id] = []
        self.message_history[agent_id].append(message.model_dump())
        
        # Send to agent if connected
        if agent_id in self.agent_connections:
            try:
                await self.agent_connections[agent_id].send_json(message.model_dump())
            except Exception:
                pass
        
        # Also broadcast back to all watching users
        await self.broadcast_to_users(agent_id, message)
        
        return message
    
    def get_stats(self) -> dict:
        """Get connection statistics."""
        return {
            "total_user_connections": sum(len(conns) for conns in self.user_connections.values()),
            "total_agent_connections": len(self.agent_connections),
            "agents_with_watchers": list(self.user_connections.keys()),
            "connected_agents": list(self.agent_connections.keys()),
        }


# Global connection manager
manager = ConnectionManager()


async def user_websocket_endpoint(websocket: WebSocket, agent_id: str, user_id: str):
    """
    WebSocket endpoint for users to watch their agent.
    
    Usage:
        ws://localhost:8000/v1/ws/user/{agent_id}?user_id={user_id}
    """
    await manager.connect_user(websocket, agent_id, user_id)
    
    try:
        while True:
            # Receive messages from user
            data = await websocket.receive_json()
            
            if data.get("type") == "message":
                # User sending a message to the agent
                await manager.send_from_user(agent_id, user_id, data.get("content", ""))
            
            elif data.get("type") == "ping":
                await websocket.send_json({"type": "pong"})
    
    except WebSocketDisconnect:
        manager.disconnect(websocket)


async def agent_websocket_endpoint(websocket: WebSocket, agent_id: str, api_key: str):
    """
    WebSocket endpoint for agents to send messages to users.
    
    Usage:
        ws://localhost:8000/v1/ws/agent/{agent_id}?api_key={api_key}
    """
    await manager.connect_agent(websocket, agent_id, api_key)
    
    try:
        while True:
            # Receive commands from agent
            data = await websocket.receive_json()
            
            if data.get("type") == "message":
                # Agent sending a message to users
                await manager.send_from_agent(
                    agent_id,
                    data.get("content", ""),
                    data.get("msg_type", "agent_message"),
                    data.get("metadata"),
                )
            
            elif data.get("type") == "status":
                # Agent sending a status update
                await manager.send_from_agent(
                    agent_id,
                    data.get("content", ""),
                    "status",
                    data.get("metadata"),
                )
            
            elif data.get("type") == "ping":
                await websocket.send_json({"type": "pong"})
    
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        
        # Notify users that agent disconnected
        await manager.broadcast_to_users(agent_id, Message(
            id=str(uuid4()),
            type="status",
            content="Agent disconnected",
            sender="system",
            agent_id=agent_id,
            timestamp=datetime.utcnow().isoformat(),
        ))
