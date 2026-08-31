"""Modelos Pydantic de la cadena evolutiva."""

from __future__ import annotations

from pydantic import BaseModel


class EvolutionNode(BaseModel):
    pokemon_name: str
    pokemon_id: int | None = None
    sprite_url: str | None = None
    min_level: int | None = None
    item: str | None = None
    trigger: str | None = None
    happiness: bool = False
    trade: bool = False
    min_happiness: int | None = None
    held_item: str | None = None
    time_of_day: str | None = None
    gender: int | None = None
    known_move: str | None = None
    location: str | None = None
    needs_overworld_rain: bool = False
    relative_physical_stats: int | None = None
    children: list[EvolutionNode] = []


class EvolutionChain(BaseModel):
    id: int
    chain: EvolutionNode