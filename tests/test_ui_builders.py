"""Smoke tests de los constructores de UI (sin ventana Flet)."""

from __future__ import annotations

import flet as ft

from app.i18n import t
from app.models.evolution import EvolutionChain
from app.models.pokemon import PokemonDetail, PokemonSummary
from app.models.species import PokemonSpecies, PokemonVariety
from app.models.type_chart import TypeDamages, combine_types
from app.services.parsers import (
    evolution_chain_from_json,
    pokemon_detail_from_json,
    pokemon_species_from_json,
)
from app.ui.components.error_message import build_error
from app.ui.components.loading_indicator import build_loading
from app.ui.components.pokemon_card import build_pokemon_card
from app.ui.components.skeleton import (
    build_skeleton_card,
    build_skeleton_detail,
    build_skeleton_list,
)
from app.ui.components.stat_bar import build_stat_bar
from app.ui.mock_data import mock_pokemon
from app.ui.theme import FONT_FAMILY, build_theme, card_border
from app.ui.views.detail_view import (
    _display_name,
    _info_panel,
    build_detail,
    build_empty_detail,
    build_pokemon_detail,
)
from app.ui.views.type_chart_view import _multiplier_text, build_type_chart


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


def test_pokemon_card_has_hover_animation() -> None:
    summary = mock_pokemon(1)[0]
    control = build_pokemon_card(summary, on_click=None, selected=False)
    assert isinstance(control.scale, float)
    assert control.on_hover is not None
    assert control.animate_scale is not None


def test_build_skeleton_card_and_list() -> None:
    card = build_skeleton_card()
    assert isinstance(card, ft.Container)
    listing = build_skeleton_list(count=6)
    assert isinstance(listing, ft.Column)
    assert len(listing.controls) == 6


def test_build_skeleton_detail() -> None:
    detail = build_skeleton_detail()
    assert isinstance(detail, ft.Container)


def test_build_theme_sets_typography() -> None:
    theme = build_theme()
    assert theme.font_family == FONT_FAMILY
    assert theme.card_theme is not None
    assert theme.appbar_theme is not None


def test_card_border_variants() -> None:
    assert card_border().top.color == ft.Colors.OUTLINE_VARIANT
    assert card_border(selected=True).top.color == ft.Colors.PRIMARY
    assert card_border(on_surface=True).top.color == ft.Colors.OUTLINE


def test_detail_main_image_defaults_to_artwork(pikachu_json: dict) -> None:
    pokemon = pokemon_detail_from_json(pikachu_json)
    panel = _info_panel(pokemon, None)
    assert isinstance(panel, ft.Column)
    main_image = panel.controls[0]
    assert isinstance(main_image, ft.Image)
    assert main_image.src == pokemon.sprites["official_artwork"]
    dropdown = panel.controls[1]
    assert isinstance(dropdown, ft.Dropdown)
    assert dropdown.value == "artwork"


def _species_with_varieties() -> PokemonSpecies:
    return PokemonSpecies(
        id=6,
        name="charizard",
        names={},
        descriptions={},
        varieties=[
            PokemonVariety(name="charizard", pokemon_id=6, is_default=True),
            PokemonVariety(name="charizard-mega-x", pokemon_id=10034),
            PokemonVariety(name="charizard-mega-y", pokemon_id=10035),
        ],
    )


def test_form_selector_is_added_when_multiple_varieties() -> None:
    pokemon = PokemonDetail(id=6, name="charizard")
    species = _species_with_varieties()
    callback_calls: list[int] = []

    def on_form_changed(pokemon_id: int) -> None:
        callback_calls.append(pokemon_id)

    panel = _info_panel(pokemon, species, on_form_changed=on_form_changed)
    assert isinstance(panel, ft.Column)
    form_dropdown = next(
        c
        for c in panel.controls
        if isinstance(c, ft.Dropdown) and c.label == t("detail.form.label")
    )
    assert isinstance(form_dropdown, ft.Dropdown)
    assert form_dropdown.value == "6"
    assert len(form_dropdown.options) == 3


def test_form_selector_not_added_for_single_form() -> None:
    pokemon = PokemonDetail(id=25, name="pikachu")
    species = PokemonSpecies(
        id=25,
        name="pikachu",
        names={},
        descriptions={},
        varieties=[PokemonVariety(name="pikachu", pokemon_id=25, is_default=True)],
    )
    panel = _info_panel(pokemon, species, on_form_changed=lambda _: None)
    assert isinstance(panel, ft.Column)
    form_labels = [
        c.label
        for c in panel.controls
        if isinstance(c, ft.Dropdown)
    ]
    assert t("detail.form.label") not in form_labels


def test_form_selector_hidden_without_callback() -> None:
    pokemon = PokemonDetail(id=6, name="charizard")
    species = _species_with_varieties()
    panel = _info_panel(pokemon, species)
    assert isinstance(panel, ft.Column)
    form_labels = [
        c.label
        for c in panel.controls
        if isinstance(c, ft.Dropdown)
    ]
    assert t("detail.form.label") not in form_labels


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


def test_display_name_uses_localized_language() -> None:
    pokemon = pokemon_detail_from_json(
        {"id": 25, "name": "pikachu", "sprites": {}}
    )
    species = PokemonSpecies(
        id=25,
        name="pikachu",
        spanish_name="Pikachu",
        names={"es": "Pikachu", "en": "Pikachu", "ja": "ピカチュウ"},
    )
    assert _display_name(pokemon, species, "ja") == "ピカチュウ"
    assert _display_name(pokemon, species, "en") == "Pikachu"
    assert _display_name(pokemon, species, "es") == "Pikachu"


def test_display_name_falls_back_without_species() -> None:
    pokemon = pokemon_detail_from_json(
        {"id": 25, "name": "pikachu", "sprites": {}}
    )
    assert _display_name(pokemon, None, "en") == "Pikachu"


def test_build_type_chart() -> None:
    fire = TypeDamages(
        name="fire",
        double_damage_from=["ground", "rock", "water"],
        half_damage_from=["bug", "steel", "fire", "grass", "ice", "fairy"],
        no_damage_from=[],
    )
    result = combine_types(["fire"], fire)
    control = build_type_chart(result)
    assert isinstance(control, ft.ListView)
    assert isinstance(control.controls, list)
    assert len(control.controls) > 0


def test_multiplier_text_formatting() -> None:
    assert _multiplier_text(0.0) == "Inmune"
    assert _multiplier_text(1.0) == "Normal"
    assert _multiplier_text(2.0) == "x2"
    assert _multiplier_text(4.0) == "x4"
    assert _multiplier_text(0.5) == "x0.5"
    assert _multiplier_text(0.25) == "x0.25"