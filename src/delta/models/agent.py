"""Agent model and related schemas."""

from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field
from sqlalchemy import Boolean, Column, DateTime, Enum as SQLEnum, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import relationship

from delta.models.user import Base


class AgentType(str, Enum):
    """Types of agents."""
    MAIN = "main"           # Full-featured agent with all permissions
    BOT = "bot"             # Limited bot with specific task
    MESSENGER = "messenger" # Ultra-limited, can only send messages


class AgentStatus(str, Enum):
    """Agent lifecycle status."""
    CREATING = "creating"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPED = "stopped"
    ERROR = "error"


class Agent(Base):
    """Agent database model."""
    
    __tablename__ = "agents"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    parent_agent_id = Column(PGUUID(as_uuid=True), ForeignKey("agents.id"), nullable=True)
    
    # Identity
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    agent_type = Column(SQLEnum(AgentType), default=AgentType.MAIN, nullable=False)
    
    # Status
    status = Column(SQLEnum(AgentStatus), default=AgentStatus.CREATING, nullable=False)
    
    # Sandbox Configuration
    fly_machine_id = Column(String(255), nullable=True)
    fly_app_name = Column(String(255), nullable=True)
    template = Column(String(50), default="python-3.12")
    memory_mb = Column(Integer, default=512)
    cpu_cores = Column(Integer, default=1)
    
    # Token Management
    token_budget = Column(Integer, default=100, nullable=False)
    tokens_used = Column(Integer, default=0, nullable=False)
    
    # Permissions (for bots)
    allowed_channels = Column(Text, nullable=True)  # JSON: ["email", "sms"]
    task_description = Column(Text, nullable=True)
    max_messages_per_day = Column(Integer, default=10)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_active = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="agents")
    parent = relationship("Agent", remote_side=[id], backref="child_agents")

    def __repr__(self) -> str:
        return f"<Agent {self.name} ({self.agent_type})>"


# Pydantic Schemas

class AgentConfig(BaseModel):
    """Configuration for creating an agent."""
    template: str = "python-3.12"
    memory_mb: int = Field(default=512, ge=256, le=4096)
    cpu_cores: int = Field(default=1, ge=1, le=4)
    token_budget: int = Field(default=100, ge=1)


class AgentCreate(BaseModel):
    """Schema for creating an agent."""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    config: Optional[AgentConfig] = None


class BotCreate(BaseModel):
    """Schema for creating a bot agent."""
    name: str = Field(..., min_length=1, max_length=255)
    task_description: str = Field(..., min_length=10)
    allowed_channels: list[str] = Field(default=["email"])
    token_budget: int = Field(default=50, ge=1, le=500)
    max_messages_per_day: int = Field(default=10, ge=1, le=100)


class AgentResponse(BaseModel):
    """Schema for agent in API responses."""
    id: UUID
    name: str
    description: Optional[str]
    agent_type: AgentType
    status: AgentStatus
    template: str
    memory_mb: int
    token_budget: int
    tokens_used: int
    created_at: datetime
    last_active: Optional[datetime]
    
    class Config:
        from_attributes = True


class AgentTokenRequest(BaseModel):
    """Schema for requesting more tokens."""
    amount: int = Field(..., ge=1)
    reason: str = Field(..., min_length=5)
