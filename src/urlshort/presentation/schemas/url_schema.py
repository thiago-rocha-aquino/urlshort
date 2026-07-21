from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field, HttpUrl


class CreateUrlRequest(BaseModel):
    target: HttpUrl = Field(examples=["https://example.com/some/long/path"])
    custom_slug: str | None = Field(default=None, min_length=3, max_length=50)
    expires_at: datetime | None = None
    max_clicks: int | None = Field(default=None, ge=1)
    password: str | None = Field(default=None, min_length=4, max_length=128)


class ShortUrlResponse(BaseModel):
    id: int
    slug: str
    short_url: str
    target: str
    expires_at: datetime | None
    max_clicks: int | None
    click_count: int
    is_password_protected: bool
    is_active: bool
    created_at: datetime


class RedirectPasswordBody(BaseModel):
    password: str = Field(min_length=1)
