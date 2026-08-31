"""Smoke tests de los constructores de UI (sin ventana Flet)."""

from __future__ import annotations

import flet as ft

from app.models.evolution import EvolutionChain
from app.models.pokemon import PokemonSummary
from app.services.parsers import (
    evolution_chain_from_json,
    pokemon_detail_from_json,
    pokemon_species_from_json,
)
from app.ui.components.error_message import build_error
from app.ui.components.loading_indicator import build_loading
from app.ui.components.pokemon_card import build_pokemon_card
from app.ui.components.stat_bar import build_stat_bar
from app.ui.mock_data import mock_pokemon
from app.ui.views.detail_view import (
    build_detail,
    build_empty_detail,
    build_pokemon_detail,
)


def test_build_empty_detail() -> None:
    control = build_empty_detail()
    assert isinstance(control, ft.Container)


def test_build_detail_with_mock() -> None:
    summary = mock_pokemon(1)[0]
    assert isinstance(summary, PokemonSummary)
    control = build_detail(summary)
    assert isinstance(control, ft.Container)


def test_build_pokemon_card() -> None:
    summary = mock_pokemon(1)[0]
    control = build_pokemon_card(summary, on_click=None, selected=True)
    assert isinstance(control, ft.Container)


def test_build_pokemon_card_without_sprite() -> None:
    summary = PokemonSummary(id=10001, name="forms")
    control = build_pokemon_card(summary, on_click=None, selected=False)
    assert isinstance(control, ft.Container)


def test_build_loading_and_error() -> None:
    assert isinstance(build_loading(), ft.Container)
    assert isinstance(build_error("Algo falló"), ft.Container)


def test_build_stat_bar() -> None:
    assert isinstance(build_stat_bar("speed", 90), ft.Row)


def _build_chain() -> EvolutionChain:
    return evolution_chain_from_json(
        {
            "id": 10,
            "chain": {
                "species": {
                    "name": "pichu",
                    "url": "https://pokeapi.co/api/v2/pokemon-species/172/",
                },
                "evolution_details": [],
                "evolves_to": [
                    {
                        "species": {
                            "name": "pikachu",
                            "url": "https://pokeapi.co/api/v2/pokemon-species/25/",
                        },
                        "evolution_details": [
                            {"trigger": {"name": "level-up"}, "min_level": 2}
                        ],
                        "evolves_to": [],
                    }
                ],
            },
        }
    )


def _build_branching_chain() -> EvolutionChain:
    return evolution_chain_from_json(
        {
            "id": 67,
            "chain": {
                "species": {
                    "name": "eevee",
                    "url": "https://pokeapi.co/api/v2/pokemon-species/133/",
                },
                "evolution_details": [],
                "evolves_to": [
                    {
                        "species": {
                            "name": "vaporeon",
                            "url": "https://pokeapi.co/api/v2/pokemon-species/134/",
                        },
                        "evolution_details": [
                            {
                                "trigger": {"name": "use-item"},
                                "item": {"name": "water-stone"},
                            }
                        ],
                        "evolves_to": [],
                    },
                    {
                        "species": {
                            "name": "umbreon",
                            "url": "https://pokeapi.co/api/v2/pokemon-species/197/",
                        },
                        "evolution_details": [
                            {
                                "trigger": {"name": "level-up"},
                                "min_happiness": 220,
                                "time_of_day": "night",
                            }
                        ],
                        "evolves_to": [],
                    },
                ],
            },
        }
    )


def test_build_pokemon_detail_real_data(
    pikachu_json: dict, species_json: dict
) -> None:
    pokemon = pokemon_detail_from_json(pikachu_json)
    species = pokemon_species_from_json(species_json)
    control = build_pokemon_detail(pokemon, species)
    assert isinstance(control, ft.Container)
    assert isinstance(control.content, ft.Tabs)


def test_build_pokemon_detail_with_chain(
    pikachu_json: dict, species_json: dict
) -> None:
    pokemon = pokemon_detail_from_json(pikachu_json)
    species = pokemon_species_from_json(species_json)
    control = build_pokemon_detail(pokemon, species, chain=_build_chain())
    assert isinstance(control.content, ft.Tabs)


def test_build_pokemon_detail_with_branching_chain(
    pikachu_json: dict, species_json: dict
) -> None:
    pokemon = pokemon_detail_from_json(pikachu_json)
    species = pokemon_species_from_json(species_json)
    control = build_pokemon_detail(
        pokemon, species, chain=_build_branching_chain()
    )
    assert isinstance(control.content, ft.Tabs)


def test_build_pokemon_detail_with_click_callback(
    pikachu_json: dict, species_json: dict
) -> None:
    calls: list[int] = []

    def on_clicked(pokemon_id: int, name: str) -> None:
        calls.append(pokemon_id)

    pokemon = pokemon_detail_from_json(pikachu_json)
    species = pokemon_species_from_json(species_json)
    control = build_pokemon_detail(
        pokemon,
        species,
        chain=_build_chain(),
        on_pokemon_clicked=on_clicked,
    )
    assert isinstance(control.content, ft.Tabs)