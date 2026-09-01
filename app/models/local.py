"""Modelos de datos de usuario almacenados localmente."""

from __future__ import annotations

from datetime import UTC, datetime

from pydantic import BaseModel, Field


def _utc_now() -> float:
    return datetime.now(UTC).timestamp()


class FavoriteEntry(BaseModel):
    id: int
    name: str
    sprite_url: str | None = None
    added_at: float = Field(default_factory=_utc_now)


class RecentEntry(BaseModel):
    id: int
    name: str
    sprite_url: str | None = None
    viewed_at: float = Field(default_factory=_utc_now)
