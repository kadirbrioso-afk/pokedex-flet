"""Modelo Pydantic de la especie de un Pokémon."""

from __future__ import annotations

from pydantic import BaseModel


class PokemonSpecies(BaseModel):
    id: int
    name: str
    spanish_name: str | None = None
    description: str | None = None
    habitat: str | None = None
    color: str | None = None
    shape: str | None = None
    capture_rate: int | None = None
    base_happiness: int | None = None
    generation: int | None = None
    evolution_chain_url: str | None = None