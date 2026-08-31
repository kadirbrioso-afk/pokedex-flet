"""Estado compartido de la aplicación."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class AppState:
    selected_generation_id: int | None = None
    selected_pokemon_id: int | None = None
    last_search: str | None = None