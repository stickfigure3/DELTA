"""Token usage tracking models."""

from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel
from sqlalchemy import Column, DateTime, Enum as SQLEnum, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID as PGUUID

from delta.models.user import Base


class TokenUsageType(str, Enum):
    """Types of token usage."""
    LLM_PROMPT = "llm_prompt"
    LLM_COMPLETION = "llm_completion"
    TOOL_EXECUTION = "tool_execution"
    FILE_OPERATION = "file_operation"
    MESSAGE_SEND = "message_send"


class TokenUsage(Base):
    """Track individual token usage events."""
    
    __tablename__ = "token_usage"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    agent_id = Column(PGUUID(as_uuid=True), ForeignKey("agents.id"), nullable=False, index=True)
    
    # Usage Details
    usage_type = Column(SQLEnum(TokenUsageType), nullable=False)
    tokens_used = Column(Integer, nullable=False)
    
    # Context
    task_id = Column(String(255), nullable=True)
    task_description = Column(Text, nullable=True)
    model = Column(String(100), nullable=True)  # e.g., "claude-3-opus"
    
    # Metadata
    metadata = Column(Text, nullable=True)  # JSON for additional data
    
    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)


class TokenAllocation(Base):
    """Track token allocations between users and agents."""
    
    __tablename__ = "token_allocations"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    agent_id = Column(PGUUID(as_uuid=True), ForeignKey("agents.id"), nullable=False, index=True)
    
    # Allocation
    amount = Column(Integer, nullable=False)
    reason = Column(Text, nullable=True)
    
    # Approval (for bot requests)
    requested_by_agent_id = Column(PGUUID(as_uuid=True), nullable=True)
    approved = Column(Integer, default=1)  # 1=approved, 0=pending, -1=denied
    approved_at = Column(DateTime, nullable=True)
    
    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


# Pydantic Schemas

class TokenUsageRecord(BaseModel):
    """Schema for token usage in API responses."""
    id: UUID
    agent_id: UUID
    usage_type: TokenUsageType
    tokens_used: int
    task_description: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class TokenSummary(BaseModel):
    """Summary of token usage."""
    total_allocated: int
    total_used: int
    remaining: int
    usage_by_agent: dict[str, int]
    usage_by_type: dict[str, int]


class TokenBudget(BaseModel):
    """Token budget configuration."""
    monthly_limit: int
    daily_limit: Optional[int] = None
    per_task_limit: Optional[int] = None
