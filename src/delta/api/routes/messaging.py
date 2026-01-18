"""Messaging routes for agent-to-user communication."""

from uuid import UUID
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class SendEmailRequest(BaseModel):
    recipient: str
    subject: str
    content: str
    template_id: str | None = None


class SendSMSRequest(BaseModel):
    recipient: str
    content: str
    template_id: str | None = None


class MakeCallRequest(BaseModel):
    recipient: str
    message: str
    template_id: str | None = None


class CreateTemplateRequest(BaseModel):
    name: str
    message_type: str  # email, sms, voice_call
    subject_template: str | None = None
    content_template: str
    allowed_variables: list[str] | None = None


@router.post("/email")
async def send_email(agent_id: UUID, request: SendEmailRequest) -> dict:
    """Send an email on behalf of an agent."""
    return {
        "id": "message-id",
        "type": "email",
        "status": "sent",
        "recipient": request.recipient,
    }


@router.post("/sms")
async def send_sms(agent_id: UUID, request: SendSMSRequest) -> dict:
    """Send an SMS on behalf of an agent."""
    return {
        "id": "message-id",
        "type": "sms",
        "status": "sent",
        "recipient": request.recipient,
    }


@router.post("/call")
async def make_call(agent_id: UUID, request: MakeCallRequest) -> dict:
    """Make a voice call on behalf of an agent."""
    return {
        "id": "message-id",
        "type": "voice_call",
        "status": "initiated",
        "recipient": request.recipient,
    }


@router.get("/logs")
async def get_message_logs(agent_id: UUID | None = None) -> dict:
    """Get message logs, optionally filtered by agent."""
    return {"logs": [], "total": 0}


@router.get("/logs/{message_id}")
async def get_message_log(message_id: UUID) -> dict:
    """Get a specific message log."""
    return {"id": str(message_id), "status": "sent"}


# Templates
@router.post("/templates")
async def create_template(request: CreateTemplateRequest) -> dict:
    """Create a message template."""
    return {
        "id": "template-id",
        "name": request.name,
        "type": request.message_type,
    }


@router.get("/templates")
async def list_templates() -> dict:
    """List all message templates."""
    return {"templates": [], "total": 0}


@router.delete("/templates/{template_id}")
async def delete_template(template_id: UUID) -> dict:
    """Delete a message template."""
    return {"message": "Template deleted"}


# Rate limits
@router.get("/rate-limits")
async def get_rate_limits(agent_id: UUID) -> dict:
    """Get current rate limit status for an agent."""
    return {
        "agent_id": str(agent_id),
        "email": {"limit": 100, "used": 0, "remaining": 100},
        "sms": {"limit": 50, "used": 0, "remaining": 50},
        "voice_call": {"limit": 10, "used": 0, "remaining": 10},
    }
