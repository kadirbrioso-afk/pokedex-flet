"""Modelos Pydantic del dominio Pokémon."""

from __future__ import annotations

from pydantic import BaseModel

from app.core.config import AppConfig


class PokemonSummary(BaseModel):
    id: int | None = None
    name: str
    sprite_url: str | None = None
    generation_id: int | None = None


class PokemonType(BaseModel):
    name: str
    slot: int = 1


class PokemonStat(BaseModel):
    name: str
    value: int


class PokemonAbility(BaseModel):
    name: str
    is_hidden: bool = False
    slot: int = 1


class PokemonDetail(BaseModel):
    id: int
    name: str
    display_name: str | None = None
    height: int | None = None
    weight: int | None = None
    base_experience: int | None = None
    sprites: dict[str, str | None] = {}
    types: list[PokemonType] = []
    stats: list[PokemonStat] = []
    abilities: list[PokemonAbility] = []


def sprite_url(pokemon_id: int | None) -> str | None:
    if pokemon_id is None:
        return None
    config = AppConfig()
    return f"{config.sprite_base_url}/{pokemon_id}.png"