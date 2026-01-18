"""Authentication routes."""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr

router = APIRouter()


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    name: str | None = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(request: RegisterRequest) -> dict:
    """Register a new user account."""
    # TODO: Implement user registration
    return {
        "message": "User registered successfully",
        "email": request.email,
    }


@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest) -> TokenResponse:
    """Login and get access tokens."""
    # TODO: Implement login
    return TokenResponse(
        access_token="placeholder",
        refresh_token="placeholder",
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(refresh_token: str) -> TokenResponse:
    """Refresh access token."""
    # TODO: Implement token refresh
    return TokenResponse(
        access_token="placeholder",
        refresh_token="placeholder",
    )


@router.post("/logout")
async def logout() -> dict:
    """Logout and invalidate tokens."""
    return {"message": "Logged out successfully"}


@router.post("/verify-email/{token}")
async def verify_email(token: str) -> dict:
    """Verify email address."""
    return {"message": "Email verified successfully"}


@router.post("/forgot-password")
async def forgot_password(email: EmailStr) -> dict:
    """Request password reset."""
    return {"message": "Password reset email sent"}


@router.post("/reset-password/{token}")
async def reset_password(token: str, new_password: str) -> dict:
    """Reset password with token."""
    return {"message": "Password reset successfully"}
