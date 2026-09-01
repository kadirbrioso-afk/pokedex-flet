"""Tests del comparador de Pokémon (modelo, servicio y vista)."""

from __future__ import annotations

from typing import Any

from app.models.compare import PokemonComparison, build_comparison_side
from app.services.compare_service import CompareService
from app.services.pokemon_service import PokemonService
from app.ui.views.compare_view import build_comparison
from tests.test_services import FakePokeAPIClient


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
