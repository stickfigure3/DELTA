"""Message logging models for agent communications."""

from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel
from sqlalchemy import Column, DateTime, Enum as SQLEnum, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID as PGUUID

from delta.models.user import Base


class MessageType(str, Enum):
    """Types of messages."""
    EMAIL = "email"
    SMS = "sms"
    VOICE_CALL = "voice_call"
    INTERNAL = "internal"  # Agent-to-agent


class MessageStatus(str, Enum):
    """Message delivery status."""
    PENDING = "pending"
    APPROVED = "approved"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    REJECTED = "rejected"


class MessageLog(Base):
    """Log of all messages sent by agents."""
    
    __tablename__ = "message_logs"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    agent_id = Column(PGUUID(as_uuid=True), ForeignKey("agents.id"), nullable=False, index=True)
    
    # Message Details
    message_type = Column(SQLEnum(MessageType), nullable=False)
    status = Column(SQLEnum(MessageStatus), default=MessageStatus.PENDING, nullable=False)
    
    # Content
    recipient = Column(String(255), nullable=False)
    subject = Column(String(500), nullable=True)  # For emails
    content = Column(Text, nullable=False)
    template_id = Column(String(100), nullable=True)  # Pre-approved template
    
    # Delivery Info
    external_id = Column(String(255), nullable=True)  # Twilio SID, SES ID, etc.
    error_message = Column(Text, nullable=True)
    
    # Tokens used for this message
    tokens_used = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    sent_at = Column(DateTime, nullable=True)
    delivered_at = Column(DateTime, nullable=True)


class MessageTemplate(Base):
    """Pre-approved message templates."""
    
    __tablename__ = "message_templates"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    
    # Template Details
    name = Column(String(255), nullable=False)
    message_type = Column(SQLEnum(MessageType), nullable=False)
    subject_template = Column(String(500), nullable=True)
    content_template = Column(Text, nullable=False)
    
    # Variables allowed in template
    allowed_variables = Column(Text, nullable=True)  # JSON array
    
    # Status
    is_active = Column(Integer, default=1)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# Pydantic Schemas

class SendMessageRequest(BaseModel):
    """Request to send a message."""
    template_id: Optional[str] = None
    recipient: str
    subject: Optional[str] = None
    content: Optional[str] = None
    variables: Optional[dict] = None


class MessageResponse(BaseModel):
    """Response after sending a message."""
    id: UUID
    status: MessageStatus
    message_type: MessageType
    recipient: str
    created_at: datetime
    sent_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class MessageTemplateCreate(BaseModel):
    """Create a message template."""
    name: str
    message_type: MessageType
    subject_template: Optional[str] = None
    content_template: str
    allowed_variables: Optional[list[str]] = None


class DailyMessageCount(BaseModel):
    """Daily message count for rate limiting."""
    email: int = 0
    sms: int = 0
    voice_call: int = 0
    
    def total(self) -> int:
        return self.email + self.sms + self.voice_call
