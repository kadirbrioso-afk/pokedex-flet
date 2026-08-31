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
    children: list[EvolutionNode] = []


class EvolutionChain(BaseModel):
    id: int
    chain: EvolutionNode