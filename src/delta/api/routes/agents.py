"""Agent management routes."""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

router = APIRouter()


class CreateAgentRequest(BaseModel):
    name: str
    description: Optional[str] = None
    template: str = "python-3.12"
    memory_mb: int = 512
    token_budget: int = 100


class CreateBotRequest(BaseModel):
    name: str
    task_description: str
    allowed_channels: list[str] = ["email"]
    token_budget: int = 50
    max_messages_per_day: int = 10


class TokenRequestPayload(BaseModel):
    amount: int
    reason: str


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_agent(request: CreateAgentRequest) -> dict:
    """Create a new main agent."""
    # TODO: Implement agent creation with Fly.io
    return {
        "id": "placeholder-id",
        "name": request.name,
        "status": "creating",
        "template": request.template,
    }


@router.get("/")
async def list_agents() -> dict:
    """List all agents for the current user."""
    return {"agents": [], "total": 0}


@router.get("/{agent_id}")
async def get_agent(agent_id: UUID) -> dict:
    """Get agent details."""
    return {"id": str(agent_id), "status": "running"}


@router.delete("/{agent_id}")
async def delete_agent(agent_id: UUID) -> dict:
    """Delete an agent."""
    return {"message": "Agent deleted"}


@router.post("/{agent_id}/pause")
async def pause_agent(agent_id: UUID) -> dict:
    """Pause an agent."""
    return {"id": str(agent_id), "status": "paused"}


@router.post("/{agent_id}/resume")
async def resume_agent(agent_id: UUID) -> dict:
    """Resume a paused agent."""
    return {"id": str(agent_id), "status": "running"}


# Bot management
@router.post("/{agent_id}/bots", status_code=status.HTTP_201_CREATED)
async def create_bot(agent_id: UUID, request: CreateBotRequest) -> dict:
    """Create a bot under a main agent."""
    return {
        "id": "bot-placeholder-id",
        "parent_agent_id": str(agent_id),
        "name": request.name,
        "task": request.task_description,
        "status": "running",
    }


@router.get("/{agent_id}/bots")
async def list_bots(agent_id: UUID) -> dict:
    """List all bots under an agent."""
    return {"bots": [], "total": 0}


# Token management
@router.get("/{agent_id}/tokens")
async def get_token_usage(agent_id: UUID) -> dict:
    """Get token usage for an agent."""
    return {
        "agent_id": str(agent_id),
        "budget": 100,
        "used": 0,
        "remaining": 100,
    }


@router.post("/{agent_id}/tokens/allocate")
async def allocate_tokens(agent_id: UUID, bot_id: UUID, amount: int) -> dict:
    """Allocate tokens from main agent to a bot."""
    return {
        "from_agent": str(agent_id),
        "to_bot": str(bot_id),
        "amount": amount,
        "status": "allocated",
    }


@router.post("/{agent_id}/tokens/request")
async def request_tokens(agent_id: UUID, request: TokenRequestPayload) -> dict:
    """Bot requests more tokens from parent agent."""
    return {
        "request_id": "placeholder",
        "agent_id": str(agent_id),
        "amount": request.amount,
        "reason": request.reason,
        "status": "pending",
    }
