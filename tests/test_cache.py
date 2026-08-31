"""Tests de la caché TTL."""

from __future__ import annotations

import time

from app.core.cache import TTLCache


def test_cache_get_set() -> None:
    cache: TTLCache[int] = TTLCache(ttl_seconds=60)
    assert cache.get("a") is None
    cache.set("a", 42)
    assert cache.get("a") == 42


def test_cache_expiration() -> None:
    cache: TTLCache[str] = TTLCache(ttl_seconds=1)
    cache.set("k", "v")
    assert cache.get("k") == "v"
    time.sleep(1.1)
    assert cache.get("k") is None


def test_cache_clear() -> None:
    cache: TTLCache[int] = TTLCache(ttl_seconds=60)
    cache.set("a", 1)
    cache.clear()
    assert cache.get("a") is None


def test_cache_without_ttl() -> None:
    cache: TTLCache[int] = TTLCache(ttl_seconds=None)
    cache.set("a", 1)
    assert "a" in cache
    assert cache.get("a") == 1