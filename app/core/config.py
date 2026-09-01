"""Configuración central de la aplicación."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

POKEAPI_BASE_URL = "https://pokeapi.co/api/v2"
SPRITE_BASE_URL = "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon"


@dataclass(frozen=True)
class AppConfig:
    app_name: str = "Pokédex Flet"
    app_version: str = "0.1.0"
    pokeapi_base_url: str = POKEAPI_BASE_URL
    sprite_base_url: str = SPRITE_BASE_URL
    request_timeout: float = 10.0
    connect_timeout: float = 5.0
    cache_ttl_seconds: int = 60 * 60 * 24
    semaphore_limit: int = 5
    max_retries: int = 2
    retry_backoff: float = 0.5
    cache_dir: Path = field(
        default_factory=lambda: Path.home() / ".cache" / "pokedex-flet"
    )
    data_dir: Path = field(
        default_factory=lambda: Path.home() / ".local" / "share" / "pokedex-flet"
    )