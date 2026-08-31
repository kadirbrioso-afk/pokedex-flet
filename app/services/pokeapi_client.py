"""Cliente asíncrono para la PokeAPI."""

from __future__ import annotations

import asyncio
from typing import Any

import httpx

from app.core.config import AppConfig
from app.core.logging import get_logger

logger = get_logger(__name__)

RETRYABLE_STATUS: frozenset[int] = frozenset({429, 500, 502, 503, 504})


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
        self._semaphore = asyncio.Semaphore(self._config.semaphore_limit)
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
        return await self._get_paginated("/generation", params={"limit": 100})

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
        for attempt in range(self._config.max_retries + 1):
            try:
                async with self._semaphore:
                    response = await self._client.get(path, params=params)
            except httpx.HTTPError as exc:
                logger.warning("Error de red pidiendo %s: %s", path, exc)
                if attempt < self._config.max_retries:
                    await self._backoff(attempt)
                    continue
                raise NetworkError(str(exc)) from exc

            if response.status_code == httpx.codes.NOT_FOUND:
                raise PokemonNotFoundError(f"Recurso no encontrado: {path}")
            if (
                response.status_code in RETRYABLE_STATUS
                and attempt < self._config.max_retries
            ):
                logger.warning(
                    "Respuesta %s pidiendo %s, reintento %s",
                    response.status_code,
                    path,
                    attempt + 1,
                )
                await self._backoff(attempt)
                continue
            if response.status_code >= 400:
                raise PokeAPIError(
                    f"PokeAPI respondió {response.status_code} para {path}"
                )
            return self._parse_json(response, path)
        raise PokeAPIError(f"Demasiados reintentos pidiendo {path}")

    async def _get_paginated(
        self,
        path: str,
        params: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        results: list[dict[str, Any]] = []
        current: str = path
        request_params: dict[str, Any] | None = params
        while True:
            data = await self._get(current, params=request_params)
            results.extend(data.get("results", []))
            next_url = data.get("next")
            if not next_url:
                break
            current = next_url
            request_params = None
        return results

    async def _backoff(self, attempt: int) -> None:
        await asyncio.sleep(self._config.retry_backoff * (attempt + 1))

    def _parse_json(
        self,
        response: httpx.Response,
        path: str,
    ) -> dict[str, Any]:
        try:
            return response.json()
        except ValueError as exc:
            raise PokeAPIError(f"Respuesta no válida para {path}") from exc