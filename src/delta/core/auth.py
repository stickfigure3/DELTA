"""Authentication service for DELTA platform."""

import secrets
from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from jose import JWTError, jwt

from delta.config import get_settings


class AuthService:
    """Handle authentication, password hashing, and JWT tokens."""
    
    def __init__(self):
        self.settings = get_settings()
        self.hasher = PasswordHasher(
            time_cost=self.settings.argon2_time_cost,
            memory_cost=self.settings.argon2_memory_cost,
            parallelism=self.settings.argon2_parallelism,
        )
    
    def hash_password(self, password: str) -> str:
        """Hash a password using Argon2id."""
        return self.hasher.hash(password)
    
    def verify_password(self, password: str, password_hash: str) -> bool:
        """Verify a password against its hash."""
        try:
            self.hasher.verify(password_hash, password)
            return True
        except VerifyMismatchError:
            return False
    
    def create_access_token(
        self,
        user_id: UUID,
        expires_delta: Optional[timedelta] = None,
    ) -> str:
        """Create a JWT access token."""
        if expires_delta is None:
            expires_delta = timedelta(minutes=self.settings.jwt_access_token_expire_minutes)
        
        expire = datetime.utcnow() + expires_delta
        to_encode = {
            "sub": str(user_id),
            "exp": expire,
            "type": "access",
        }
        
        return jwt.encode(
            to_encode,
            self.settings.jwt_secret_key,
            algorithm=self.settings.jwt_algorithm,
        )
    
    def create_refresh_token(self, user_id: UUID) -> str:
        """Create a JWT refresh token."""
        expires_delta = timedelta(days=self.settings.jwt_refresh_token_expire_days)
        expire = datetime.utcnow() + expires_delta
        
        to_encode = {
            "sub": str(user_id),
            "exp": expire,
            "type": "refresh",
        }
        
        return jwt.encode(
            to_encode,
            self.settings.jwt_secret_key,
            algorithm=self.settings.jwt_algorithm,
        )
    
    def verify_token(self, token: str, token_type: str = "access") -> Optional[UUID]:
        """Verify a JWT token and return the user ID."""
        try:
            payload = jwt.decode(
                token,
                self.settings.jwt_secret_key,
                algorithms=[self.settings.jwt_algorithm],
            )
            
            if payload.get("type") != token_type:
                return None
            
            user_id = payload.get("sub")
            if user_id is None:
                return None
            
            return UUID(user_id)
        except JWTError:
            return None
    
    def generate_api_key(self) -> tuple[str, str]:
        """Generate a new API key. Returns (full_key, key_hash)."""
        # Format: delta_sk_<random>
        key = f"delta_sk_{secrets.token_urlsafe(32)}"
        key_hash = self.hasher.hash(key)
        return key, key_hash
    
    def verify_api_key(self, key: str, key_hash: str) -> bool:
        """Verify an API key."""
        return self.verify_password(key, key_hash)
    
    def generate_verification_token(self) -> str:
        """Generate a random token for email verification."""
        return secrets.token_urlsafe(32)
    
    def generate_password_reset_token(self) -> str:
        """Generate a random token for password reset."""
        return secrets.token_urlsafe(32)


# Singleton instance
_auth_service: Optional[AuthService] = None


def get_auth_service() -> AuthService:
    """Get the auth service singleton."""
    global _auth_service
    if _auth_service is None:
        _auth_service = AuthService()
    return _auth_service
