"""Auth & user schemas."""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    full_name: str = Field(default="", max_length=200)
    timezone: str = Field(default="UTC", max_length=64)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    full_name: str
    timezone: str
    reminder_soon_days: int
    created_at: datetime


class UserUpdate(BaseModel):
    """User-editable profile & reminder preferences."""

    full_name: str | None = Field(default=None, max_length=200)
    timezone: str | None = Field(default=None, max_length=64)
    reminder_soon_days: int | None = Field(default=None, ge=1, le=30)


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut
