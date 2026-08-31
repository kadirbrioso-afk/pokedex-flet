"""Cliente asíncrono para la PokeAPI."""

from __future__ import annotations

from typing import Any

import httpx

from app.core.config import AppConfig
from app.core.logging import get_logger

logger = get_logger(__name__)


class PokeAPIError(Exception):
    pass


class PokemonNotFoundError(PokeAPIError):
    pass


class NetworkError(PokeAPIError):
    pass


class PokeAPIClient:
    def __init__(
        self,
        config: AppConfig | None = None,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        self._config = config or AppConfig()
        if client is not None:
            self._client = client
        else:
            self._client = httpx.AsyncClient(
                base_url=self._config.pokeapi_base_url,
                timeout=httpx.Timeout(
                    self._config.request_timeout,
                    connect=self._config.connect_timeout,
                ),
            )

    async def get_generations(self) -> list[dict[str, Any]]:
        data = await self._get("/generation", params={"limit": 100})
        return data["results"]

    async def get_generation(self, identifier: str | int) -> dict[str, Any]:
        return await self._get(f"/generation/{identifier}")

    async def get_pokemon(self, identifier: str | int) -> dict[str, Any]:
        return await self._get(f"/pokemon/{identifier}")

    async def get_pokemon_species(self, identifier: str | int) -> dict[str, Any]:
        return await self._get(f"/pokemon-species/{identifier}")

    async def get_evolution_chain(self, chain_id: int) -> dict[str, Any]:
        return await self._get(f"/evolution-chain/{chain_id}")

    async def close(self) -> None:
        await self._client.aclose()

    async def __aenter__(self) -> PokeAPIClient:
        return self

    async def __aexit__(self, *exc: object) -> None:
        await self.close()

    async def _get(
        self,
        path: str,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        try:
            response = await self._client.get(path, params=params)
        except httpx.HTTPError as exc:
            logger.warning("Error de red pidiendo %s: %s", path, exc)
            raise NetworkError(str(exc)) from exc

        if response.status_code == httpx.codes.NOT_FOUND:
            raise PokemonNotFoundError(f"Recurso no encontrado: {path}")
        if response.status_code >= 400:
            raise PokeAPIError(
                f"PokeAPI respondió {response.status_code} para {path}"
            )
        return response.json()