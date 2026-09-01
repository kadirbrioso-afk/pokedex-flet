"""Tests de la vista principal (HomeView), incluye modo offline."""

from __future__ import annotations

import io
import tempfile
from pathlib import Path
from typing import Any

import httpx
import respx
from PIL import Image

from app.core.config import AppConfig
from app.models.pokemon import PokemonDetail, PokemonSummary, PokemonType
from app.models.species import PokemonSpecies, PokemonVariety
from app.services.local_store import LocalStore
from app.services.sprite_cache import SpriteCache
from app.state.app_state import AppState
from app.ui.views.home_view import HomeView


def _png_bytes() -> bytes:
    buffer = io.BytesIO()
    Image.new("RGBA", (96, 96)).save(buffer, "PNG")
    return buffer.getvalue()


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

    async def get_pokemon(self, identifier: str | int) -> Any:
        data = self._cached.get(int(identifier))
        if data is None:
            raise ValueError(f"no pokemon {identifier}")
        return PokemonDetail(
            id=data["id"],
            name=data["name"],
            sprites=data.get("sprites", {}),
            types=[
                PokemonType(name=type_data["name"])
                for type_data in data.get("types", [])
            ],
        )


class FakeGenerationService:
    pass


def _make_home(store: LocalStore | None = None) -> HomeView:
    return HomeView(
        FakePage(),
        AppState(),
        FakePokemonService(),  # type: ignore[arg-type]
        FakeGenerationService(),  # type: ignore[arg-type]
        local_store=store,
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
    assert home._view_mode == "offline"
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


def test_set_favorites_lists_stored_favorites() -> None:
    store = LocalStore(config=AppConfig(data_dir=Path(tempfile.mkdtemp())))
    store.add_favorite(25, "pikachu", "https://example.com/p.png")
    home = _make_home(store=store)
    home.set_favorites(True)
    assert home._view_mode == "favorites"
    assert len(home._summaries) == 1
    assert home._summaries[0].id == 25


def test_favorite_summaries_empty_when_no_favorites() -> None:
    store = LocalStore(config=AppConfig(data_dir=Path(tempfile.mkdtemp())))
    home = _make_home(store=store)
    assert home._favorite_summaries() == []


async def test_pending_selection_assigns_from_list() -> None:
    home = _make_home()
    home.build()
    home._begin_pick("B")
    assert home._pending_side == "B"
    assert home._home_row is not None
    assert home._home_row.visible is True

    summary = PokemonSummary(id=25, name="pikachu")
    handler = home._make_pokemon_handler(summary)
    await handler(None)

    assert home._pending_side is None
    assert home._compare._right_name == "pikachu"  # noqa: SLF001
    assert home._compare_container.visible is True
    assert home._home_row.visible is False


def test_compare_open_and_close_toggles_visibility() -> None:
    home = _make_home()
    home.build()
    home.set_compare(True)
    assert home._compare_container.visible is True
    assert home._home_row.visible is False
    home.set_compare(False)
    assert home._compare_container.visible is False
    assert home._home_row.visible is True


def test_type_chart_open_and_close_toggles_visibility() -> None:
    home = _make_home()
    home.build()
    home.set_type_chart(True)
    assert home._type_chart_container.visible is True
    assert home._home_row.visible is False
    assert home._compare_container.visible is False
    home.set_type_chart(False)
    assert home._type_chart_container.visible is False
    assert home._home_row.visible is True


def test_views_are_mutually_exclusive() -> None:
    home = _make_home()
    home.build()
    home.set_compare(True)
    assert home._type_chart_container.visible is False
    home.set_type_chart(True)
    assert home._compare_container.visible is False
    assert home._type_chart_container.visible is True
    assert home._home_row.visible is False


def test_set_language_updates_state_and_chrome() -> None:
    home = _make_home()
    home.build()
    assert home._state.lang == "es"
    assert home._search_button.content == "Buscar"
    assert home._header_text.value == "Pokédex"

    home.set_language("en")

    assert home._state.lang == "en"
    assert home._search_button.content == "Search"
    assert home._prev_button.content == "Previous"
    assert home._search_field.hint_text == "Name or ID (e.g. pikachu, 25)"
    assert home._filter_field.hint_text == "Filter this generation…"

    home.set_language("es")
    assert home._search_button.content == "Buscar"


@respx.mock
async def test_resolve_summaries_localizes_sprites(tmp_path: Path) -> None:
    respx.get("https://example.com/p.png").mock(
        return_value=httpx.Response(200, content=_png_bytes())
    )
    home = _make_home()
    home._cache = SpriteCache(
        config=AppConfig(cache_dir=tmp_path / "cache", data_dir=tmp_path / "data")
    )
    summaries = [
        PokemonSummary(id=25, name="pikachu", sprite_url="https://example.com/p.png")
    ]

    await home._resolve_summaries(summaries)

    sprite = summaries[0].sprite_url
    assert sprite is not None
    assert sprite.startswith(str(tmp_path / "cache"))
    assert Path(sprite).is_file()
    await home._cache.close()


@respx.mock
async def test_resolve_summaries_keeps_url_on_failure(tmp_path: Path) -> None:
    respx.get("https://example.com/p.png").mock(
        side_effect=httpx.ConnectError("no network")
    )
    home = _make_home()
    home._cache = SpriteCache(
        config=AppConfig(cache_dir=tmp_path / "cache", data_dir=tmp_path / "data")
    )
    summaries = [
        PokemonSummary(id=25, name="pikachu", sprite_url="https://example.com/p.png")
    ]

    await home._resolve_summaries(summaries)

    assert summaries[0].sprite_url == "https://example.com/p.png"
    await home._cache.close()


async def test_resolve_summaries_skips_empty_sprites() -> None:
    home = _make_home()
    summaries = [PokemonSummary(id=99, name="no-sprite")]

    await home._resolve_summaries(summaries)

    assert summaries[0].sprite_url is None


@respx.mock
async def test_cache_detail_sprites_localizes_paths(tmp_path: Path) -> None:
    respx.get("https://example.com/a.png").mock(
        return_value=httpx.Response(200, content=_png_bytes())
    )
    home = _make_home()
    home._cache = SpriteCache(
        config=AppConfig(cache_dir=tmp_path / "cache", data_dir=tmp_path / "data")
    )
    pokemon = PokemonDetail(
        id=25,
        name="pikachu",
        sprites={
            "front_default": "https://example.com/a.png",
            "official_artwork": "https://example.com/a.png",
        },
    )

    await home._cache_detail_sprites(pokemon, None)

    sprites = pokemon.sprites
    assert sprites["front_default"].startswith(str(tmp_path / "cache"))
    assert sprites["official_artwork"].startswith(str(tmp_path / "cache"))
    await home._cache.close()


@respx.mock
async def test_form_changed_renders_selected_form(tmp_path: Path) -> None:
    respx.get("https://example.com/mega.png").mock(
        return_value=httpx.Response(200, content=_png_bytes())
    )
    home = _make_home(
        store=LocalStore(config=AppConfig(data_dir=tmp_path / "data"))
    )
    home._cache = SpriteCache(
        config=AppConfig(cache_dir=tmp_path / "cache", data_dir=tmp_path / "data")
    )
    home._pokemon_service._cached[10034] = {  # type: ignore[attr-defined]
        "id": 10034,
        "name": "charizard-mega-x",
        "sprites": {"front_default": "https://example.com/mega.png"},
        "types": [{"name": "dragon"}],
    }
    species = PokemonSpecies(
        id=6,
        name="charizard",
        names={},
        descriptions={},
        varieties=[
            PokemonVariety(name="charizard", pokemon_id=6, is_default=True),
            PokemonVariety(name="charizard-mega-x", pokemon_id=10034),
        ],
    )

    await home._change_form(species, None, 10034)

    assert home._detail_container.content is not None
    assert home._page.updated is True
    await home._cache.close()
