"""Modelos Pydantic de generaciones de Pokémon."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel

from app.models.pokemon import PokemonSummary, sprite_url


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

    def species_summaries(self) -> list[PokemonSummary]:
        summaries: list[PokemonSummary] = []
        for entry in self.pokemon_species:
            url = entry.get("url", "")
            try:
                species_id = int(url.rstrip("/").split("/")[-1])
            except (ValueError, IndexError):
                continue
            name = entry.get("name")
            if not name:
                continue
            summaries.append(
                PokemonSummary(
                    id=species_id,
                    name=name,
                    sprite_url=sprite_url(species_id),
                    generation_id=self.id,
                )
            )
        return summaries