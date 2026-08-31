"""Caché en memoria con expiración por TTL."""

from __future__ import annotations

import time


class TTLCache[T]:
    def __init__(self, ttl_seconds: int | None = None) -> None:
        self._ttl = ttl_seconds
        self._store: dict[str, tuple[float, T]] = {}

    def get(self, key: str) -> T | None:
        item = self._store.get(key)
        if item is None:
            return None
        expires_at, value = item
        if self._ttl is not None and time.monotonic() > expires_at:
            self._store.pop(key, None)
            return None
        return value

    def set(self, key: str, value: T) -> None:
        if self._ttl is None:
            self._store[key] = (0.0, value)
        else:
            self._store[key] = (time.monotonic() + self._ttl, value)

    def clear(self) -> None:
        self._store.clear()

    def __contains__(self, key: str) -> bool:
        return self.get(key) is not None