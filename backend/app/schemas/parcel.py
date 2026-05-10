from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class ParcelBase(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    location: str | None = Field(default=None, max_length=512)
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)


class ParcelCreate(ParcelBase):
    pass


class ParcelUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    location: str | None = Field(default=None, max_length=512)
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)


class ParcelPublic(ParcelBase):
    id: str
    user_id: str
    created_at: datetime


class ParcelListResponse(BaseModel):
    user_id: str
    total: int
    items: list[ParcelPublic]
