"""Caché local de sprites: descarga única + conversión a WebP con Pillow.

Cada sprite se descarga de PokeAPI una sola vez, se redimensiona opcionalmente
y se guarda como WebP en el directorio de caché. Las llamadas posteriores
devuelven la ruta local (rápida, funciona sin conexión). Si algo falla, se
devuelve la URL original: la UI degrada al comportamiento sin caché.
"""

from __future__ import annotations

import asyncio
import hashlib
import io
from pathlib import Path

import httpx
from PIL import Image

from app.core.config import AppConfig
from app.core.logging import get_logger

logger = get_logger(__name__)


class SpriteCache:
    def __init__(
        self,
        config: AppConfig | None = None,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        self._config = config or AppConfig()
        self._client = client
        self._owns_client = client is None
        self._semaphore = asyncio.Semaphore(self._config.semaphore_limit)
        self._cache_dir = self._config.cache_dir / "sprites"

    def _http_client(self) -> httpx.AsyncClient:
        client = self._client
        if client is None:
            client = httpx.AsyncClient(
                timeout=httpx.Timeout(self._config.request_timeout)
            )
            self._client = client
        return client

    def cache_path(self, url: str, max_size: int | None = None) -> Path:
        key = hashlib.sha256(url.encode("utf-8")).hexdigest()[:16]
        suffix = f"-{max_size}" if max_size else ""
        return self._cache_dir / f"{key}{suffix}.webp"

    async def ensure(self, url: str, max_size: int | None = None) -> str:
        """Devuelve la ruta local (WebP) del sprite o la URL original si falla."""
        if not url or not (url.startswith("http://") or url.startswith("https://")):
            return url
        target = self.cache_path(url, max_size)
        if target.is_file():
            return str(target)
        try:
            data = await self._download(url)
            self._convert(data, target, max_size)
        except (httpx.HTTPError, OSError, ValueError) as exc:
            logger.warning("Caché de sprite falló para %s: %s", url, exc)
            return url
        return str(target)

    async def close(self) -> None:
        if self._owns_client and self._client is not None:
            await self._client.aclose()
            self._client = None

    async def _download(self, url: str) -> bytes:
        async with self._semaphore:
            response = await self._http_client().get(url)
            response.raise_for_status()
            return response.content

    def _convert(self, data: bytes, target: Path, max_size: int | None) -> None:
        opened = Image.open(io.BytesIO(data))
        image = opened.convert("RGBA") if opened.mode != "RGBA" else opened
        if max_size:
            image.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
        target.parent.mkdir(parents=True, exist_ok=True)
        image.save(target, "WEBP", quality=85)