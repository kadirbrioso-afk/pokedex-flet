"""Modelos Pydantic de generaciones de Pokémon."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class GenerationSummary(BaseModel):
    id: int
    name: str


class GenerationDetail(BaseModel):
    id: int
    name: str
    pokemon_species: list[dict[str, Any]] = []

    def species_ids(self) -> list[int]:
        ids: list[int] = []
        for entry in self.pokemon_species:
            url = entry.get("url", "")
            try:
                ids.append(int(url.rstrip("/").split("/")[-1]))
            except (ValueError, IndexError):
                continue
        return ids