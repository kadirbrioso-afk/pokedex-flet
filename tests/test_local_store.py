"""Tests del repositorio local (favoritos, recientes e historial)."""

from __future__ import annotations

from pathlib import Path

from app.core.config import AppConfig
from app.services.local_store import LocalStore


def make_store(
    tmp_path: Path,
    favorites_limit: int = 200,
    recents_limit: int = 50,
    history_limit: int = 20,
) -> LocalStore:
    return LocalStore(
        config=AppConfig(data_dir=tmp_path),
        favorites_limit=favorites_limit,
        recents_limit=recents_limit,
        history_limit=history_limit,
    )


def test_add_and_check_favorite(tmp_path: Path) -> None:
    store = make_store(tmp_path)
    assert store.add_favorite(25, "pikachu", "https://x/25.png") is True
    assert store.is_favorite(25) is True
    assert store.is_favorite(6) is False


def test_add_favorite_is_idempotent(tmp_path: Path) -> None:
    store = make_store(tmp_path)
    assert store.add_favorite(25, "pikachu") is True
    assert store.add_favorite(25, "pikachu") is False
    assert len(store.list_favorites()) == 1


def test_toggle_favorite_removes(tmp_path: Path) -> None:
    store = make_store(tmp_path)
    store.add_favorite(25, "pikachu")
    assert store.toggle_favorite(25, "pikachu") is False
    assert store.is_favorite(25) is False
    assert store.toggle_favorite(25, "pikachu") is True
    assert store.is_favorite(25) is True


def test_remove_favorite(tmp_path: Path) -> None:
    store = make_store(tmp_path)
    store.add_favorite(25, "pikachu")
    assert store.remove_favorite(25) is True
    assert store.remove_favorite(25) is False


def test_favorites_limit_trims_oldest(tmp_path: Path) -> None:
    store = make_store(tmp_path, favorites_limit=2)
    store.add_favorite(1, "bulbasaur")
    store.add_favorite(4, "charmander")
    store.add_favorite(7, "squirtle")
    ids = [entry.id for entry in store.list_favorites()]
    assert ids == [1, 4]


def test_add_recent_deduplicates_and_moves_to_front(tmp_path: Path) -> None:
    store = make_store(tmp_path)
    store.add_recent(25, "pikachu")
    store.add_recent(6, "charizard")
    store.add_recent(25, "pikachu")
    ids = [entry.id for entry in store.list_recents()]
    assert ids == [25, 6]


def test_search_history_deduplicates_and_orders(tmp_path: Path) -> None:
    store = make_store(tmp_path)
    store.add_search("  Pikachu  ")
    store.add_search("bulbasaur")
    store.add_search("pikachu")
    assert store.list_searches() == ["pikachu", "bulbasaur"]


def test_search_history_ignores_empty(tmp_path: Path) -> None:
    store = make_store(tmp_path)
    store.add_search("   ")
    assert store.list_searches() == []


def test_history_limit(tmp_path: Path) -> None:
    store = make_store(tmp_path, history_limit=2)
    store.add_search("a")
    store.add_search("b")
    store.add_search("c")
    assert store.list_searches() == ["c", "b"]


def test_data_persists_across_instances(tmp_path: Path) -> None:
    store = make_store(tmp_path)
    store.add_favorite(25, "pikachu", "https://x/25.png")
    store.add_recent(6, "charizard")
    store.add_search("pikachu")

    reloaded = make_store(tmp_path)
    assert [(f.id, f.name) for f in reloaded.list_favorites()] == [(25, "pikachu")]
    assert [(r.id, r.name) for r in reloaded.list_recents()] == [(6, "charizard")]
    assert reloaded.list_searches() == ["pikachu"]


def test_clear_removes_all(tmp_path: Path) -> None:
    store = make_store(tmp_path)
    store.add_favorite(25, "pikachu")
    store.add_recent(6, "charizard")
    store.add_search("pikachu")
    store.clear()
    assert store.list_favorites() == []
    assert store.list_recents() == []
    assert store.list_searches() == []


def test_corrupt_file_is_ignored(tmp_path: Path) -> None:
    target = tmp_path / "local.json"
    target.write_text("{not valid json", encoding="utf-8")
    store = make_store(tmp_path)
    assert store.list_favorites() == []
