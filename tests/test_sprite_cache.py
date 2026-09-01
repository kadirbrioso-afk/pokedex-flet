"""Tests de la caché de sprites con Pillow (descarga + WebP)."""

from __future__ import annotations

import io
from pathlib import Path

import httpx
import respx
from PIL import Image

from app.core.config import AppConfig
from app.services.sprite_cache import SpriteCache

SPRITE_URL = "https://example.com/sprites/25.png"


def make_config(tmp_path: Path) -> AppConfig:
    return AppConfig(
        cache_dir=tmp_path / "cache",
        data_dir=tmp_path / "data",
        request_timeout=5.0,
    )


def _png_bytes(size: tuple[int, int] = (96, 96)) -> bytes:
    image = Image.new("RGBA", size, (255, 0, 0, 255))
    buffer = io.BytesIO()
    image.save(buffer, "PNG")
    return buffer.getvalue()


def test_cache_path_is_deterministic(tmp_path: Path) -> None:
    cache = SpriteCache(config=make_config(tmp_path))
    first = cache.cache_path(SPRITE_URL)
    second = cache.cache_path(SPRITE_URL)
    assert first == second
    assert first.suffix == ".webp"


def test_cache_path_varies_by_size(tmp_path: Path) -> None:
    cache = SpriteCache(config=make_config(tmp_path))
    assert cache.cache_path(SPRITE_URL) != cache.cache_path(SPRITE_URL, 320)


@respx.mock
async def test_ensure_returns_cached_file_without_network(tmp_path: Path) -> None:
    route = respx.get(SPRITE_URL).mock(
        side_effect=httpx.ConnectError("should not be called")
    )
    cache = SpriteCache(config=make_config(tmp_path))
    target = cache.cache_path(SPRITE_URL, 320)
    target.parent.mkdir(parents=True, exist_ok=True)
    Image.new("RGBA", (10, 10)).save(target, "WEBP")

    result = await cache.ensure(SPRITE_URL, 320)

    assert result == str(target)
    assert route.call_count == 0
    await cache.close()


@respx.mock
async def test_ensure_downloads_and_converts_to_webp(tmp_path: Path) -> None:
    route = respx.get(SPRITE_URL).mock(
        return_value=httpx.Response(200, content=_png_bytes())
    )
    cache = SpriteCache(config=make_config(tmp_path))

    first = await cache.ensure(SPRITE_URL)
    second = await cache.ensure(SPRITE_URL)

    assert first == second
    assert first.endswith(".webp")
    assert Path(first).is_file()
    assert route.call_count == 1
    with Image.open(Path(first)) as image:
        assert image.format == "WEBP"
        assert image.size == (96, 96)
    await cache.close()


@respx.mock
async def test_ensure_resizes_when_max_size_given(tmp_path: Path) -> None:
    respx.get(SPRITE_URL).mock(
        return_value=httpx.Response(200, content=_png_bytes((200, 100)))
    )
    cache = SpriteCache(config=make_config(tmp_path))

    result = await cache.ensure(SPRITE_URL, max_size=50)

    with Image.open(Path(result)) as image:
        assert image.size == (50, 25)
    await cache.close()


@respx.mock
async def test_ensure_returns_original_url_on_http_error(tmp_path: Path) -> None:
    respx.get(SPRITE_URL).mock(return_value=httpx.Response(500))
    cache = SpriteCache(config=make_config(tmp_path))

    result = await cache.ensure(SPRITE_URL)

    assert result == SPRITE_URL
    await cache.close()


@respx.mock
async def test_ensure_returns_original_url_on_network_error(tmp_path: Path) -> None:
    respx.get(SPRITE_URL).mock(side_effect=httpx.ConnectError("unreachable"))
    cache = SpriteCache(config=make_config(tmp_path))

    result = await cache.ensure(SPRITE_URL)

    assert result == SPRITE_URL
    await cache.close()


@respx.mock
async def test_ensure_returns_original_url_on_invalid_image(tmp_path: Path) -> None:
    respx.get(SPRITE_URL).mock(
        return_value=httpx.Response(200, content=b"<html>not an image</html>")
    )
    cache = SpriteCache(config=make_config(tmp_path))

    result = await cache.ensure(SPRITE_URL)

    assert result == SPRITE_URL
    await cache.close()


async def test_empty_url_returns_unchanged(tmp_path: Path) -> None:
    cache = SpriteCache(config=make_config(tmp_path))
    assert await cache.ensure("") == ""
    await cache.close()


async def test_local_path_returns_unchanged(tmp_path: Path) -> None:
    cache = SpriteCache(config=make_config(tmp_path))
    local = "/tmp/example/cached.webp"
    assert await cache.ensure(local) == local
    await cache.close()