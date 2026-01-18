"""SDK models and schemas."""

from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class AgentStatus(str, Enum):
    CREATING = "creating"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPED = "stopped"
    ERROR = "error"


class AgentType(str, Enum):
    MAIN = "main"
    BOT = "bot"
    MESSENGER = "messenger"


class SandboxConfig(BaseModel):
    """Configuration for a sandbox."""
    template: str = "python-3.12"
    memory_mb: int = Field(default=512, ge=256, le=4096)
    cpu_cores: int = Field(default=1, ge=1, le=4)
    persist: bool = True
    timeout_seconds: int = 3600


class AgentConfig(BaseModel):
    """Configuration for an agent."""
    template: str = "python-3.12"
    memory_mb: int = Field(default=512, ge=256, le=4096)
    cpu_cores: int = Field(default=1, ge=1, le=4)
    token_budget: int = Field(default=100, ge=1)
    description: Optional[str] = None


class TokenBudget(BaseModel):
    """Token budget configuration."""
    total: int
    used: int = 0
    
    @property
    def remaining(self) -> int:
        return self.total - self.used
    
    @property
    def usage_percentage(self) -> float:
        if self.total == 0:
            return 0.0
        return (self.used / self.total) * 100


class ExecResult(BaseModel):
    """Result of command execution."""
    exit_code: int
    stdout: str
    stderr: str
    duration_ms: int


class FileInfo(BaseModel):
    """File information."""
    name: str
    path: str
    size: int
    is_dir: bool
    modified_at: Optional[datetime] = None


class FileContent(BaseModel):
    """File content response."""
    path: str
    content: str
    size: int


class Agent(BaseModel):
    """Agent information."""
    id: UUID
    name: str
    agent_type: AgentType
    status: AgentStatus
    template: str
    memory_mb: int
    token_budget: int
    tokens_used: int
    created_at: datetime
    last_active: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class Sandbox(BaseModel):
    """Sandbox information."""
    id: UUID
    agent_id: UUID
    status: AgentStatus
    template: str
    ip_address: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class MessageResult(BaseModel):
    """Result of sending a message."""
    id: UUID
    message_type: str
    status: str
    recipient: str
    tokens_used: int
    sent_at: Optional[datetime] = None
