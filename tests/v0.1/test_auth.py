"""Authentication tests for DELTA v0.1."""

import pytest
from uuid import uuid4

from delta.core.auth import AuthService, get_auth_service


class TestPasswordHashing:
    """Test Argon2id password hashing."""
    
    def test_hash_password(self):
        """Test that passwords are hashed."""
        service = AuthService()
        password = "secure_password_123"
        
        hashed = service.hash_password(password)
        
        assert hashed != password
        assert hashed.startswith("$argon2id$")
    
    def test_verify_correct_password(self):
        """Test that correct passwords verify."""
        service = AuthService()
        password = "secure_password_123"
        hashed = service.hash_password(password)
        
        assert service.verify_password(password, hashed) is True
    
    def test_verify_wrong_password(self):
        """Test that wrong passwords don't verify."""
        service = AuthService()
        password = "secure_password_123"
        hashed = service.hash_password(password)
        
        assert service.verify_password("wrong_password", hashed) is False


class TestJWTTokens:
    """Test JWT token creation and verification."""
    
    def test_create_access_token(self):
        """Test access token creation."""
        service = AuthService()
        user_id = uuid4()
        
        token = service.create_access_token(user_id)
        
        assert token is not None
        assert len(token) > 0
    
    def test_verify_access_token(self):
        """Test access token verification."""
        service = AuthService()
        user_id = uuid4()
        token = service.create_access_token(user_id)
        
        verified_id = service.verify_token(token, "access")
        
        assert verified_id == user_id
    
    def test_verify_invalid_token(self):
        """Test that invalid tokens return None."""
        service = AuthService()
        
        result = service.verify_token("invalid_token", "access")
        
        assert result is None
    
    def test_refresh_token(self):
        """Test refresh token creation and verification."""
        service = AuthService()
        user_id = uuid4()
        
        token = service.create_refresh_token(user_id)
        verified_id = service.verify_token(token, "refresh")
        
        assert verified_id == user_id


class TestAPIKeys:
    """Test API key generation and verification."""
    
    def test_generate_api_key(self):
        """Test API key generation."""
        service = AuthService()
        
        key, key_hash = service.generate_api_key()
        
        assert key.startswith("delta_sk_")
        assert key_hash.startswith("$argon2id$")
    
    def test_verify_api_key(self):
        """Test API key verification."""
        service = AuthService()
        key, key_hash = service.generate_api_key()
        
        assert service.verify_api_key(key, key_hash) is True
    
    def test_verify_wrong_api_key(self):
        """Test that wrong API keys don't verify."""
        service = AuthService()
        _, key_hash = service.generate_api_key()
        
        assert service.verify_api_key("delta_sk_wrong", key_hash) is False


class TestTokenGeneration:
    """Test verification and reset token generation."""
    
    def test_verification_token(self):
        """Test email verification token generation."""
        service = AuthService()
        
        token = service.generate_verification_token()
        
        assert token is not None
        assert len(token) > 20
    
    def test_password_reset_token(self):
        """Test password reset token generation."""
        service = AuthService()
        
        token = service.generate_password_reset_token()
        
        assert token is not None
        assert len(token) > 20


class TestSingleton:
    """Test service singleton pattern."""
    
    def test_get_auth_service_returns_same_instance(self):
        """Test that get_auth_service returns the same instance."""
        service1 = get_auth_service()
        service2 = get_auth_service()
        
        assert service1 is service2
