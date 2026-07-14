"""Item schemas for create/update/read and list filtering."""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.core.urls import is_safe_web_url
from app.models.enums import ItemKind, ItemPriority, ItemStatus, ProviderType


def _validate_url(value: str | None) -> str | None:
    """Allow empty, otherwise require a safe http(s) URL."""
    if value is None or value == "":
        return value
    cleaned = value.strip()
    if not is_safe_web_url(cleaned):
        raise ValueError("url must be a valid http(s) link")
    return cleaned


class ItemBase(BaseModel):
    title: str = Field(min_length=1, max_length=500)
    description: str = Field(default="", max_length=5000)
    kind: ItemKind = ItemKind.TASK
    priority: ItemPriority = ItemPriority.MEDIUM
    course: str = Field(default="", max_length=200)
    location: str = Field(default="", max_length=300)
    url: str = Field(default="", max_length=1000)
    start_at: datetime | None = None
    due_at: datetime | None = None

    @field_validator("title")
    @classmethod
    def title_not_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("title must not be blank")
        return v.strip()

    @field_validator("url")
    @classmethod
    def url_is_safe(cls, v: str) -> str:
        return _validate_url(v) or ""


class ItemCreate(ItemBase):
    status: ItemStatus = ItemStatus.TODO


class ItemUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=500)
    description: str | None = Field(default=None, max_length=5000)
    kind: ItemKind | None = None
    status: ItemStatus | None = None
    priority: ItemPriority | None = None
    course: str | None = Field(default=None, max_length=200)
    location: str | None = Field(default=None, max_length=300)
    url: str | None = Field(default=None, max_length=1000)
    start_at: datetime | None = None
    due_at: datetime | None = None

    @field_validator("title")
    @classmethod
    def title_not_blank(cls, v: str | None) -> str | None:
        if v is not None and not v.strip():
            raise ValueError("title must not be blank")
        return v.strip() if v else v

    @field_validator("url")
    @classmethod
    def url_is_safe(cls, v: str | None) -> str | None:
        return _validate_url(v)


class ItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str
    kind: ItemKind
    status: ItemStatus
    priority: ItemPriority
    course: str
    location: str
    url: str
    start_at: datetime | None
    due_at: datetime | None
    completed_at: datetime | None
    source: ProviderType
    external_id: str
    # Provider-owned fields the user has overridden; sync preserves these.
    user_edited_fields: list[str] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime


class ItemPage(BaseModel):
    """Paginated list response — truncation is visible, never silent."""

    items: list[ItemOut]
    total: int
    limit: int
    offset: int
    has_more: bool
