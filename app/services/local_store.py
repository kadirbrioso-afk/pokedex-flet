"""Repositorio local de datos de usuario (favoritos, recientes e historial).

Persistencia en JSON bajo el directorio de datos de la aplicación
(``AppConfig.data_dir``). Se escribe de forma atómica (archivo temporal +
renombrado) para no corromper los datos si la app se cierra a mitad de escritura.
"""

from __future__ import annotations

import json
import os
import tempfile
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from app.core.config import AppConfig
from app.core.logging import get_logger
from app.models.local import FavoriteEntry, RecentEntry

logger = get_logger(__name__)

DEFAULT_FAVORITES_LIMIT = 200
DEFAULT_RECENTS_LIMIT = 50
DEFAULT_HISTORY_LIMIT = 20


def _utc_now() -> float:
    return datetime.now(UTC).timestamp()


class LocalStore:
    """Persistencia local de favoritos, recientes e historial de búsqueda."""

    def __init__(
        self,
        config: AppConfig | None = None,
        favorites_limit: int = DEFAULT_FAVORITES_LIMIT,
        recents_limit: int = DEFAULT_RECENTS_LIMIT,
        history_limit: int = DEFAULT_HISTORY_LIMIT,
    ) -> None:
        self._config = config or AppConfig()
        self._favorites_limit = favorites_limit
        self._recents_limit = recents_limit
        self._history_limit = history_limit
        self._file = self._config.data_dir / "local.json"
        self._favorites: list[FavoriteEntry] = []
        self._recents: list[RecentEntry] = []
        self._history: list[str] = []
        self._load()

    # ---- Favoritos -------------------------------------------------------

    def is_favorite(self, pokemon_id: int) -> bool:
        return any(fav.id == pokemon_id for fav in self._favorites)

    def add_favorite(
        self,
        pokemon_id: int,
        name: str,
        sprite_url: str | None = None,
    ) -> bool:
        if self.is_favorite(pokemon_id):
            return False
        self._favorites.append(
            FavoriteEntry(id=pokemon_id, name=name, sprite_url=sprite_url)
        )
        self._trim(self._favorites, self._favorites_limit)
        self._save()
        return True

    def remove_favorite(self, pokemon_id: int) -> bool:
        before = len(self._favorites)
        self._favorites = [
            fav for fav in self._favorites if fav.id != pokemon_id
        ]
        if len(self._favorites) != before:
            self._save()
            return True
        return False

    def toggle_favorite(
        self,
        pokemon_id: int,
        name: str,
        sprite_url: str | None = None,
    ) -> bool:
        """Marca o desmarca un favorito. Devuelve ``True`` si quedó favorito."""
        if self.is_favorite(pokemon_id):
            self.remove_favorite(pokemon_id)
            return False
        self.add_favorite(pokemon_id, name, sprite_url)
        return True

    def list_favorites(self) -> list[FavoriteEntry]:
        return list(self._favorites)

    # ---- Recientes --------------------------------------------------------

    def add_recent(
        self,
        pokemon_id: int,
        name: str,
        sprite_url: str | None = None,
    ) -> None:
        self._recents = [
            recent for recent in self._recents if recent.id != pokemon_id
        ]
        self._recents.insert(
            0,
            RecentEntry(id=pokemon_id, name=name, sprite_url=sprite_url),
        )
        self._trim(self._recents, self._recents_limit)
        self._save()

    def list_recents(self) -> list[RecentEntry]:
        return list(self._recents)

    # ---- Historial de búsqueda --------------------------------------------

    def add_search(self, query: str) -> None:
        query = query.strip().lower()
        if not query:
            return
        if query in self._history:
            self._history.remove(query)
        self._history.insert(0, query)
        del self._history[self._history_limit :]
        self._save()

    def list_searches(self) -> list[str]:
        return list(self._history)

    # ---- Migraciones / reset -----------------------------------------------

    def clear(self) -> None:
        self._favorites = []
        self._recents = []
        self._history = []
        self._save()

    # ---- Persistencia interna ----------------------------------------------

    def _load(self) -> None:
        try:
            if not self._file.is_file():
                return
            payload = json.loads(self._file.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            logger.warning("No se pudo leer local.json: %s", exc)
            return
        favorites = payload.get("favorites", [])
        recents = payload.get("recents", [])
        history = payload.get("history", [])
        self._favorites = self._parse_list(FavoriteEntry, favorites)
        self._recents = self._parse_list(RecentEntry, recents)
        self._history = [str(q) for q in history if isinstance(q, str)]

    def _parse_list(self, model: type[Any], items: list[Any]) -> list[Any]:
        parsed: list[Any] = []
        for item in items:
            if not isinstance(item, dict):
                continue
            try:
                parsed.append(model.model_validate(item))
            except (ValueError, KeyError):
                continue
        return parsed

    def _save(self) -> None:
        payload: dict[str, Any] = {
            "favorites": [
                fav.model_dump() for fav in self._favorites
            ],
            "recents": [
                recent.model_dump() for recent in self._recents
            ],
            "history": self._history,
        }
        try:
            self._file.parent.mkdir(parents=True, exist_ok=True)
            fd, tmp_name = tempfile.mkstemp(
                dir=str(self._file.parent),
                suffix=".tmp",
            )
            os.close(fd)
            tmp_path = Path(tmp_name)
            tmp_path.write_text(
                json.dumps(payload, ensure_ascii=False),
                encoding="utf-8",
            )
            tmp_path.replace(self._file)
        except OSError as exc:
            logger.warning("No se pudo escribir local.json: %s", exc)

    @staticmethod
    def _trim(entries: list[Any], limit: int) -> None:
        del entries[limit:]
