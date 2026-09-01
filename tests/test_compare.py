"""Tests del comparador de Pokémon (modelo, servicio y vista)."""

from __future__ import annotations

from typing import Any

from app.models.compare import PokemonComparison, build_comparison_side
from app.services.compare_service import CompareService
from app.services.pokemon_service import PokemonService
from app.ui.views.compare_view import CompareView, build_comparison
from tests.test_services import FakePokeAPIClient


class FakePage:
    def __init__(self) -> None:
        self.updated = False

    def update(self) -> None:
        self.updated = True

    def show_dialog(self, _: Any) -> None:
        return None

    def run_task(self, coro: Any, *args: Any) -> Any:
        return coro


def _compare_view() -> CompareView:
    client = FakePokeAPIClient(pokemon={}, species={})  # type: ignore[arg-type]
    service = PokemonService(client)
    return CompareView(
        FakePage(),
        CompareService(service),
        on_pick_a=lambda: None,
        on_pick_b=lambda: None,
    )


def test_compare_view_side_selection() -> None:
    view = _compare_view()
    assert view.has_both() is False
    view.set_side("A", "pikachu")
    assert view.has_both() is False
    view.set_side("B", "charizard")
    assert view.has_both() is True


def test_compare_view_set_side_replaces_value() -> None:
    view = _compare_view()
    view.set_side("A", "pikachu")
    view.set_side("A", "raichu")
    assert view._left_name == "raichu"  # noqa: SLF001
    assert view._name_a.value == "raichu"  # noqa: SLF001


def test_compare_view_compare_requires_both_sides() -> None:
    view = _compare_view()
    view.set_side("A", "pikachu")
    view._on_compare(None)  # noqa: SLF001
    assert view.has_both() is False


async def test_build_comparison_side_maps_data(
    pikachu_json: dict[str, Any],
    species_json: dict[str, Any],
) -> None:
    client = FakePokeAPIClient(pokemon=pikachu_json, species=species_json)
    service = PokemonService(client)

    pokemon, species, chain = await service.get_pokemon_detail_full(25)
    side = build_comparison_side(pokemon, species, chain)

    assert side.id == 25
    assert side.name == "pikachu"
    assert side.display_name == "Pikachu"
    assert "electric" in side.types
    assert "lightning-rod" in side.abilities
    assert side.total_stats > 0
    assert side.stats.get("speed", 0) > 0


async def test_compare_service_returns_two_sides(
    pikachu_json: dict[str, Any],
    species_json: dict[str, Any],
    evolution_chain_json: dict[str, Any],
) -> None:
    client = FakePokeAPIClient(pokemon=pikachu_json, species=species_json)
    service = PokemonService(client)
    compare = CompareService(service)

    comparison = await compare.compare(25, 6)

    assert comparison.left.id == 25
    assert comparison.right.id == 25
    assert comparison.left.name == comparison.right.name


async def test_compare_service_includes_evolution_names(
    pikachu_json: dict[str, Any],
    species_json: dict[str, Any],
) -> None:
    client = FakePokeAPIClient(pokemon=pikachu_json, species=species_json)
    service = PokemonService(client)
    compare = CompareService(service)

    comparison = await compare.compare(25, 25)

    assert len(comparison.left.evolution_names) >= 1
    assert all(isinstance(name, str) for name in comparison.left.evolution_names)


async def test_build_comparison_produces_control(
    pikachu_json: dict[str, Any],
    species_json: dict[str, Any],
) -> None:
    client = FakePokeAPIClient(pokemon=pikachu_json, species=species_json)
    service = PokemonService(client)

    pokemon, species, chain = await service.get_pokemon_detail_full(25)
    side = build_comparison_side(pokemon, species, chain)
    comparison = PokemonComparison(left=side, right=side)

    control = build_comparison(comparison)
    assert control is not None


async def test_compare_service_calls_detail_full_twice(
    pikachu_json: dict[str, Any],
    species_json: dict[str, Any],
) -> None:
    client = FakePokeAPIClient(pokemon=pikachu_json, species=species_json)
    service = PokemonService(client)
    compare = CompareService(service)

    await compare.compare(25, 25)

    assert client.pokemon_calls == 1
    assert client.species_calls == 1
