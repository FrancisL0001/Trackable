"""Item schemas for create/update/read and list filtering."""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.enums import ItemKind, ItemPriority, ItemStatus, ProviderType


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
    created_at: datetime
    updated_at: datetime
