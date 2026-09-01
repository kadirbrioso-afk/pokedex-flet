"""Cliente asíncrono para la PokeAPI."""

from __future__ import annotations

import asyncio
import json
import time
from pathlib import Path
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

    async def get_type(self, identifier: str | int) -> dict[str, Any]:
        return await self._get(f"/type/{identifier}")

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
        cache_key = self._cache_key(path, params)
        cached = self._disk_cache_get(cache_key)
        if cached is not None:
            logger.debug("Caché disco %s", path)
            return cached
        data = await self._fetch(path, params)
        self._disk_cache_set(cache_key, data)
        return data

    async def _fetch(
        self,
        path: str,
        params: dict[str, Any] | None,
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

    def _cache_dir(self) -> Path:
        return self._config.cache_dir / "api"

    def list_cached_pokemon_ids(self) -> list[int]:
        """IDs de detalles de Pokémon cacheados en disco (para modo offline)."""
        pokemon_dir = self._cache_dir() / "pokemon"
        ids: list[int] = []
        try:
            for path in pokemon_dir.glob("*.json"):
                stem = path.stem
                if stem.isdigit():
                    ids.append(int(stem))
        except OSError:
            return []
        return sorted(ids)

    def get_cached_pokemon(self, identifier: int) -> dict[str, Any] | None:
        """Devuelve el JSON cacheado en disco de un detalle de Pokémon, o None."""
        key = f"/pokemon/{identifier}"
        return self._disk_cache_get(key)

    def _cache_key(self, path: str, params: dict[str, Any] | None) -> str:
        from urllib.parse import urlparse

        query = urlparse(path).query
        if params:
            pairs = sorted(
                f"{key}={value}" for key, value in params.items()
            )
            query = (query + "&" + "&".join(pairs)).strip("&")
        return f"{path}?{query}" if query else path

    def _disk_cache_get(self, key: str) -> dict[str, Any] | None:
        ttl = self._config.cache_ttl_seconds
        if ttl is None:
            return None
        cache_file = self._cache_dir() / f"{key.lstrip('/')}.json"
        try:
            if not cache_file.is_file():
                return None
            payload = cache_file.read_text(encoding="utf-8")
            envelope = json.loads(payload)
            expires_at = envelope.get("expires_at", 0.0)
            if time.time() > expires_at:
                cache_file.unlink()
                return None
            return envelope.get("data")
        except (OSError, ValueError) as exc:
            logger.debug("No se pudo leer caché disco %s: %s", key, exc)
            return None

    def _disk_cache_set(self, key: str, data: dict[str, Any]) -> None:
        ttl = self._config.cache_ttl_seconds
        if ttl is None:
            return
        cache_file = self._cache_dir() / f"{key.lstrip('/')}.json"
        try:
            cache_file.parent.mkdir(parents=True, exist_ok=True)
            envelope = {
                "expires_at": time.time() + ttl,
                "data": data,
            }
            cache_file.write_text(
                json.dumps(envelope), encoding="utf-8"
            )
        except OSError as exc:
            logger.debug("No se pudo escribir caché disco %s: %s", key, exc)