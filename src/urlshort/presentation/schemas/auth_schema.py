from __future__ import annotations

from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    email: EmailStr = Field(examples=["alice@example.com"])
    password: str = Field(min_length=8, max_length=128, examples=["s3nha-forte"])
    name: str = Field(min_length=1, max_length=120, examples=["Alice"])


class LoginRequest(BaseModel):
    email: EmailStr = Field(examples=["alice@example.com"])
    password: str = Field(min_length=1, max_length=128)


class RefreshRequest(BaseModel):
    refresh_token: str = Field(min_length=10)


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: int
    email: str
    name: str
    is_active: bool
