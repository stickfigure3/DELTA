"""User model and related schemas."""

from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import Boolean, Column, DateTime, Enum as SQLEnum, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    """Base class for all database models."""
    pass


class UserTier(str, Enum):
    """User subscription tiers."""
    FREE = "free"
    DEVELOPER = "developer"
    PRO = "pro"
    ENTERPRISE = "enterprise"


class UserStatus(str, Enum):
    """User account status."""
    PENDING = "pending"  # Email not verified
    ACTIVE = "active"
    SUSPENDED = "suspended"
    DELETED = "deleted"


class User(Base):
    """User database model."""
    
    __tablename__ = "users"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    
    # Profile
    name = Column(String(255), nullable=True)
    avatar_url = Column(Text, nullable=True)
    
    # Status & Tier
    status = Column(SQLEnum(UserStatus), default=UserStatus.PENDING, nullable=False)
    tier = Column(SQLEnum(UserTier), default=UserTier.FREE, nullable=False)
    
    # Token Management
    total_tokens_allocated = Column(Integer, default=1000, nullable=False)
    tokens_used_this_month = Column(Integer, default=0, nullable=False)
    token_reset_date = Column(DateTime, nullable=True)
    
    # Verification
    email_verified = Column(Boolean, default=False, nullable=False)
    email_verification_token = Column(String(255), nullable=True)
    email_verification_expires = Column(DateTime, nullable=True)
    
    # Password Reset
    password_reset_token = Column(String(255), nullable=True)
    password_reset_expires = Column(DateTime, nullable=True)
    
    # Stripe Integration
    stripe_customer_id = Column(String(255), nullable=True, unique=True)
    stripe_subscription_id = Column(String(255), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_login = Column(DateTime, nullable=True)
    
    # Relationships
    agents = relationship("Agent", back_populates="user", cascade="all, delete-orphan")
    api_keys = relationship("APIKey", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<User {self.email}>"


class APIKey(Base):
    """API Key for programmatic access."""
    
    __tablename__ = "api_keys"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(PGUUID(as_uuid=True), nullable=False, index=True)
    
    key_hash = Column(String(255), nullable=False, unique=True)
    key_prefix = Column(String(12), nullable=False)  # First 8 chars for identification
    name = Column(String(255), nullable=False)
    
    # Permissions & Limits
    scopes = Column(Text, nullable=True)  # JSON array of allowed scopes
    rate_limit_per_minute = Column(Integer, default=60)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    last_used = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="api_keys")

    def __repr__(self) -> str:
        return f"<APIKey {self.key_prefix}...>"


# Pydantic Schemas for API

class UserCreate(BaseModel):
    """Schema for user registration."""
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    name: Optional[str] = None


class UserLogin(BaseModel):
    """Schema for user login."""
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """Schema for user in API responses."""
    id: UUID
    email: str
    name: Optional[str]
    status: UserStatus
    tier: UserTier
    total_tokens_allocated: int
    tokens_used_this_month: int
    email_verified: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    """Schema for updating user profile."""
    name: Optional[str] = None
    avatar_url: Optional[str] = None


class TokenInfo(BaseModel):
    """Schema for token usage information."""
    total_allocated: int
    used_this_month: int
    remaining: int
    reset_date: Optional[datetime]
    
    @property
    def usage_percentage(self) -> float:
        if self.total_allocated == 0:
            return 0.0
        return (self.used_this_month / self.total_allocated) * 100


class APIKeyCreate(BaseModel):
    """Schema for creating an API key."""
    name: str = Field(..., min_length=1, max_length=255)
    scopes: Optional[list[str]] = None
    expires_in_days: Optional[int] = None


class APIKeyResponse(BaseModel):
    """Schema for API key in responses (with full key, only shown once)."""
    id: UUID
    key: str  # Full key, only returned on creation
    key_prefix: str
    name: str
    scopes: Optional[list[str]]
    is_active: bool
    created_at: datetime
    expires_at: Optional[datetime]


class APIKeyListItem(BaseModel):
    """Schema for API key in list responses (without full key)."""
    id: UUID
    key_prefix: str
    name: str
    scopes: Optional[list[str]]
    is_active: bool
    last_used: Optional[datetime]
    created_at: datetime
    expires_at: Optional[datetime]
    
    class Config:
        from_attributes = True
