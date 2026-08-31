"""Smoke tests de los constructores de UI (sin ventana Flet)."""

from __future__ import annotations

import flet as ft

from app.models.pokemon import PokemonSummary
from app.services.parsers import pokemon_detail_from_json, pokemon_species_from_json
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


def test_build_loading_and_error() -> None:
    assert isinstance(build_loading(), ft.Container)
    assert isinstance(build_error("Algo falló"), ft.Container)


def test_build_stat_bar() -> None:
    assert isinstance(build_stat_bar("speed", 90), ft.Row)


def test_build_pokemon_detail_real_data(
    pikachu_json: dict, species_json: dict
) -> None:
    pokemon = pokemon_detail_from_json(pikachu_json)
    species = pokemon_species_from_json(species_json)
    control = build_pokemon_detail(pokemon, species)
    assert isinstance(control, ft.Container)
    assert isinstance(control.content, ft.Column)