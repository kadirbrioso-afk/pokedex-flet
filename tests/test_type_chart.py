"""Tests de la tabla de tipos (modelos, parser y servicio)."""

from __future__ import annotations

from typing import Any

from app.models.type_chart import (
    TYPE_NAMES,
    TypeChartResult,
    TypeDamages,
    combine_types,
)
from app.services.parsers import type_damages_from_json
from app.services.type_service import TypeService
from tests.test_services import FakePokeAPIClient


def _names(multipliers: list[Any]) -> list[str]:
    return [m.attacking_type for m in multipliers]


def test_type_names_has_eighteen_types() -> None:
    assert len(TYPE_NAMES) == 18
    assert "fire" in TYPE_NAMES and "fairy" in TYPE_NAMES


def test_combine_single_type_fire() -> None:
    fire = TypeDamages(
        name="fire",
        double_damage_from=["ground", "rock", "water"],
        half_damage_from=["bug", "steel", "fire", "grass", "ice", "fairy"],
        no_damage_from=[],
    )
    result = combine_types(["fire"], fire)
    assert isinstance(result, TypeChartResult)
    assert result.types == ["fire"]
    assert _names(result.weaknesses) == ["water", "ground", "rock"]
    assert _names(result.resistances) == [
        "fire", "grass", "ice", "bug", "steel", "fairy",
    ]
    assert result.immunities == []
    assert result.neutral == [
        "normal", "electric", "fighting", "poison", "flying",
        "psychic", "ghost", "dragon", "dark",
    ]


def test_combine_two_types_fire_water() -> None:
    fire = TypeDamages(
        name="fire",
        double_damage_from=["ground", "rock", "water"],
        half_damage_from=["bug", "steel", "fire", "grass", "ice", "fairy"],
        no_damage_from=[],
    )
    water = TypeDamages(
        name="water",
        double_damage_from=["grass", "electric"],
        half_damage_from=["steel", "fire", "water", "ice"],
        no_damage_from=[],
    )
    result = combine_types(["fire", "water"], fire, water)
    assert _names(result.weaknesses) == ["electric", "ground", "rock"]
    assert _names(result.resistances) == [
        "fire", "ice", "bug", "steel", "fairy",
    ]
    assert result.immunities == []
    assert result.neutral == [
        "normal", "water", "grass", "fighting", "poison", "flying",
        "psychic", "ghost", "dragon", "dark",
    ]


def test_combine_multiplier_value_for_double_weakness() -> None:
    fire = TypeDamages(name="fire", double_damage_from=["rock"])
    rock = TypeDamages(name="rock", double_damage_from=["rock"])
    result = combine_types(["fire", "rock"], fire, rock)
    fire_weak = next(w for w in result.weaknesses if w.attacking_type == "rock")
    assert fire_weak.multiplier == 4.0


def test_combine_immunity_overrides() -> None:
    normal = TypeDamages(
        name="normal",
        double_damage_from=["fighting"],
        half_damage_from=[],
        no_damage_from=["ghost"],
    )
    ghost = TypeDamages(
        name="ghost",
        double_damage_from=["ghost", "dark"],
        half_damage_from=[],
        no_damage_from=["normal", "fighting"],
    )
    result = combine_types(["normal", "ghost"], normal, ghost)
    immunities = {m.attacking_type for m in result.immunities}
    assert "ghost" in immunities
    for atk in ("ghost",):
        m = next(x for x in result.immunities if x.attacking_type == atk)
        assert m.multiplier == 0.0


def test_combine_no_damage_relations_are_all_neutral() -> None:
    result = combine_types(["normal"], TypeDamages(name="normal"))
    assert result.weaknesses == []
    assert result.resistances == []
    assert result.immunities == []
    assert result.neutral == TYPE_NAMES


def test_parser_handles_real_fire_payload(type_fire_json: dict[str, Any]) -> None:
    damages = type_damages_from_json(type_fire_json)
    assert damages.name == "fire"
    assert set(damages.double_damage_from) == {"ground", "rock", "water"}
    assert "fairy" in damages.half_damage_from
    assert damages.no_damage_from == []


async def test_type_service_get_type_caches(type_fire_json: dict[str, Any]) -> None:
    client = FakePokeAPIClient(types={"fire": type_fire_json})
    service = TypeService(client)  # type: ignore[arg-type]
    first = await service.get_type("fire")
    second = await service.get_type("fire")
    assert first.name == "fire"
    assert client.type_calls == 1
    assert first == second


async def test_type_service_build_chart_two_types(
    type_fire_json: dict[str, Any],
    type_water_json: dict[str, Any],
) -> None:
    client = FakePokeAPIClient(
        types={"fire": type_fire_json, "water": type_water_json}
    )
    service = TypeService(client)  # type: ignore[arg-type]
    result = await service.build_chart("fire", "water")
    assert "electric" in _names(result.weaknesses)
    assert "water" in result.neutral
    assert "grass" in result.neutral


async def test_type_service_build_chart_single_type(
    type_fire_json: dict[str, Any],
) -> None:
    client = FakePokeAPIClient(types={"fire": type_fire_json})
    service = TypeService(client)  # type: ignore[arg-type]
    result = await service.build_chart("fire", None)
    assert result.types == ["fire"]
    assert "water" in _names(result.weaknesses)


async def test_type_service_build_chart_ignores_repeated_type(
    type_fire_json: dict[str, Any],
) -> None:
    client = FakePokeAPIClient(types={"fire": type_fire_json})
    service = TypeService(client)  # type: ignore[arg-type]
    result = await service.build_chart("fire", "fire")
    assert result.types == ["fire"]
