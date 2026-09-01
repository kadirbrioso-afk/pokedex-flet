"""Servicio de tabla de tipos: combina el cliente de API con caché."""

from __future__ import annotations

from typing import Any

from app.core.cache import TTLCache
from app.core.config import AppConfig
from app.models.type_chart import (
    TypeChartResult,
    TypeDamages,
    combine_types,
)
from app.services.parsers import type_damages_from_json
from app.services.pokeapi_client import PokeAPIClient


class TypeService:
    def __init__(
        self,
        client: PokeAPIClient,
        config: AppConfig | None = None,
    ) -> None:
        self._client = client
        self._config = config or AppConfig()
        self._cache: TTLCache[Any] = TTLCache(self._config.cache_ttl_seconds)

    async def get_type(self, identifier: str | int) -> TypeDamages:
        cache_key = f"type:{identifier}"
        cached = self._cache.get(cache_key)
        if cached is not None:
            return cached
        data = await self._client.get_type(identifier)
        damages = type_damages_from_json(data)
        self._cache.set(cache_key, damages)
        return damages

    async def build_chart(
        self,
        type_a: str,
        type_b: str | None = None,
    ) -> TypeChartResult:
        first = await self.get_type(type_a)
        names = [first.name or type_a]
        second: TypeDamages | None = None
        if type_b and type_b != type_a:
            second = await self.get_type(type_b)
            names.append(second.name or type_b)
        return combine_types(names, first, second)
