"""Servicio de Pokémon: combina el cliente de API con caché."""

from __future__ import annotations

import asyncio
from typing import Any

from app.core.cache import TTLCache
from app.core.config import AppConfig
from app.core.logging import get_logger
from app.models.evolution import EvolutionChain
from app.models.pokemon import PokemonDetail
from app.models.species import PokemonSpecies
from app.services.parsers import (
    evolution_chain_from_json,
    parse_id_from_url,
    pokemon_detail_from_json,
    pokemon_species_from_json,
)
from app.services.pokeapi_client import PokeAPIClient

logger = get_logger(__name__)


class PokemonService:
    def __init__(
        self,
        client: PokeAPIClient,
        config: AppConfig | None = None,
    ) -> None:
        self._client = client
        self._config = config or AppConfig()
        self._cache: TTLCache[Any] = TTLCache(self._config.cache_ttl_seconds)

    async def get_pokemon(self, identifier: str | int) -> PokemonDetail:
        cache_key = f"pokemon:{identifier}"
        cached = self._cache.get(cache_key)
        if cached is not None:
            logger.debug("Caché Pokémon %s", identifier)
            return cached
        data = await self._client.get_pokemon(identifier)
        pokemon = pokemon_detail_from_json(data)
        self._cache.set(cache_key, pokemon)
        return pokemon

    async def get_species(self, identifier: str | int) -> PokemonSpecies:
        cache_key = f"species:{identifier}"
        cached = self._cache.get(cache_key)
        if cached is not None:
            logger.debug("Caché especie %s", identifier)
            return cached
        data = await self._client.get_pokemon_species(identifier)
        species = pokemon_species_from_json(data)
        self._cache.set(cache_key, species)
        return species

    async def get_pokemon_with_species(
        self,
        identifier: str | int,
    ) -> tuple[PokemonDetail, PokemonSpecies]:
        pokemon, species = await asyncio.gather(
            self.get_pokemon(identifier),
            self.get_species(identifier),
        )
        return pokemon, species

    async def get_evolution_chain(self, identifier: str | int) -> EvolutionChain:
        cache_key = f"evolution-chain:{identifier}"
        cached = self._cache.get(cache_key)
        if cached is not None:
            return cached
        chain_id: str | int = identifier
        if isinstance(identifier, str) and not identifier.isdigit():
            species = await self.get_species(identifier)
            if species.evolution_chain_url is None:
                raise ValueError(f"Sin cadena evolutiva para {identifier}")
            chain_id = (
                parse_id_from_url(species.evolution_chain_url) or identifier
            )
        data = await self._client.get_evolution_chain(int(chain_id))
        chain = evolution_chain_from_json(data)
        self._cache.set(cache_key, chain)
        return chain