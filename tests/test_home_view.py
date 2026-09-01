"""Tests de la vista principal (HomeView), incluye modo offline."""

from __future__ import annotations

from typing import Any

from app.models.pokemon import PokemonSummary
from app.state.app_state import AppState
from app.ui.views.home_view import HomeView


class FakePage:
    def __init__(self) -> None:
        self.updated = False

    def update(self) -> None:
        self.updated = True

    def show_dialog(self, _: Any) -> None:
        return None

    def run_task(self, coro: Any, *args: Any) -> Any:
        return coro


class FakePokemonService:
    def __init__(self) -> None:
        self._cached: dict[int, dict[str, Any]] = {
            25: {
                "id": 25,
                "name": "pikachu",
                "sprites": {"front_default": "https://example.com/p.png"},
            }
        }

    def cached_pokemon_ids(self) -> list[int]:
        return sorted(self._cached)

    def get_cached_pokemon(self, identifier: int) -> dict[str, Any] | None:
        return self._cached.get(identifier)


class FakeGenerationService:
    pass


def _make_home() -> HomeView:
    return HomeView(
        FakePage(),
        AppState(),
        FakePokemonService(),  # type: ignore[arg-type]
        FakeGenerationService(),  # type: ignore[arg-type]
    )


def test_offline_summaries_return_cached_pokemon() -> None:
    home = _make_home()
    summaries = home._offline_summaries()
    assert len(summaries) == 1
    summary: PokemonSummary = summaries[0]
    assert summary.id == 25
    assert summary.name == "pikachu"
    assert summary.sprite_url == "https://example.com/p.png"


def test_set_offline_builds_summary_list() -> None:
    home = _make_home()
    home.set_offline(True)
    assert home._offline is True
    assert len(home._summaries) == 1
    assert home._summaries[0].id == 25
    list_view = home._list_container.content
    assert list_view is not None
    assert home._page.updated


def test_offline_summaries_include_entry_without_sprites() -> None:
    home = _make_home()
    home._pokemon_service._cached[99] = {"id": 99, "name": "missing-sprite"}  # type: ignore[attr-defined]
    summaries = home._offline_summaries()
    by_id = {summary.id: summary for summary in summaries}
    assert by_id[99].name == "missing-sprite"
    assert by_id[99].sprite_url is None
