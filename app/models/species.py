"""Modelo Pydantic de la especie de un Pokémon."""

from __future__ import annotations

from pydantic import BaseModel


class PokemonSpecies(BaseModel):
    id: int
    name: str
    spanish_name: str | None = None
    description: str | None = None
    names: dict[str, str] = {}
    descriptions: dict[str, str] = {}
    habitat: str | None = None
    color: str | None = None
    shape: str | None = None
    capture_rate: int | None = None
    base_happiness: int | None = None
    gender_rate: int | None = None
    egg_groups: list[str] = []
    growth_rate: str | None = None
    generation: int | None = None
    evolution_chain_url: str | None = None

    def localized_name(self, lang: str) -> str | None:
        """Nombre localizado para ``lang`` con fallback a es/en."""
        return (
            self.names.get(lang)
            or self.names.get("es")
            or self.names.get("en")
            or self.spanish_name
        )

    def localized_description(self, lang: str) -> str | None:
        """Descripción localizada para ``lang`` con fallback a es/en."""
        return (
            self.descriptions.get(lang)
            or self.descriptions.get("es")
            or self.descriptions.get("en")
            or self.description
        )