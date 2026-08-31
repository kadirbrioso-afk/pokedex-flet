"""Servicio de generaciones: combina el cliente de API con caché."""

from __future__ import annotations

from typing import Any

from app.core.cache import TTLCache
from app.core.config import AppConfig
from app.models.generation import GenerationDetail, GenerationSummary
from app.models.pokemon import PokemonSummary
from app.services.parsers import (
    generation_detail_from_json,
    generation_summary_from_json,
)
from app.services.pokeapi_client import PokeAPIClient


class GenerationService:
    def __init__(
        self,
        client: PokeAPIClient,
        config: AppConfig | None = None,
    ) -> None:
        self._client = client
        self._config = config or AppConfig()
        self._cache: TTLCache[Any] = TTLCache(self._config.cache_ttl_seconds)

    async def get_generations(self) -> list[GenerationSummary]:
        cache_key = "generations"
        cached = self._cache.get(cache_key)
        if cached is not None:
            return cached
        data = await self._client.get_generations()
        generations = [
            generation_summary_from_json(entry) for entry in data
        ]
        self._cache.set(cache_key, generations)
        return generations

    async def get_generation(self, identifier: str | int) -> GenerationDetail:
        cache_key = f"generation:{identifier}"
        cached = self._cache.get(cache_key)
        if cached is not None:
            return cached
        data = await self._client.get_generation(identifier)
        generation = generation_detail_from_json(data)
        self._cache.set(cache_key, generation)
        return generation

    async def get_pokemon_summaries(
        self,
        identifier: str | int,
    ) -> list[PokemonSummary]:
        generation = await self.get_generation(identifier)
        return generation.species_summaries()