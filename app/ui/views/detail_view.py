"""Vista de detalle de un Pokémon (maqueta estática de la Fase 3)."""

from __future__ import annotations

import flet as ft

from app.models.pokemon import PokemonDetail, PokemonSummary
from app.models.species import PokemonSpecies
from app.ui.components.stat_bar import build_stat_bar
from app.ui.theme import border, type_color


def _mock_stats(pokemon_id: int) -> list[tuple[str, int]]:
    return [
        ("hp", 20 + pokemon_id % 100),
        ("attack", 30 + (pokemon_id * 3) % 120),
        ("defense", 30 + (pokemon_id * 5) % 110),
        ("speed", 40 + (pokemon_id * 7) % 130),
    ]


def build_empty_detail() -> ft.Container:
    return ft.Container(
        content=ft.Text(
            "Selecciona un Pokémon para ver su detalle",
            color=ft.Colors.GREY,
            text_align=ft.TextAlign.CENTER,
        ),
        padding=24,
        alignment=ft.Alignment.CENTER,
    )


def build_detail(summary: PokemonSummary) -> ft.Container:
    display_name = summary.name.replace("-", " ").title()
    stats = _mock_stats(summary.id or 0)
    return ft.Container(
        content=ft.Column(
            [
                ft.Image(
                    src=summary.sprite_url or "",
                    width=140,
                    height=140,
                    fit=ft.BoxFit.CONTAIN,
                ),
                ft.Text(
                    f"#{summary.id:03d}" if summary.id else "#---",
                    color=ft.Colors.GREY,
                ),
                ft.Text(display_name, size=26, weight=ft.FontWeight.BOLD),
                ft.Divider(height=16),
                *[build_stat_bar(name, value) for name, value in stats],
                ft.Divider(height=16),
                ft.Text(
                    "Maqueta estática · datos simulados",
                    italic=True,
                    size=11,
                    color=ft.Colors.GREY,
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=4,
        ),
        padding=16,
        border=border(1, ft.Colors.OUTLINE_VARIANT),
        border_radius=12,
    )


def _type_badges(pokemon: PokemonDetail) -> ft.Row:
    badges: list[ft.Control] = [
        ft.Container(
            content=ft.Text(
                type_name.name,
                color=ft.Colors.WHITE,
                weight=ft.FontWeight.BOLD,
                size=12,
            ),
            bgcolor=type_color(type_name.name),
            border_radius=20,
            padding=ft.Padding.symmetric(horizontal=10, vertical=4),
        )
        for type_name in pokemon.types
    ]
    if not badges:
        badges = [ft.Text("Sin tipos", color=ft.Colors.GREY)]
    return ft.Row(badges, spacing=6)


def _info_row(label: str, value: str) -> ft.Row:
    return ft.Row(
        [
            ft.Text(label, size=12, color=ft.Colors.GREY),
            ft.Text(value, weight=ft.FontWeight.BOLD),
        ],
        spacing=8,
    )


def _display_name(pokemon: PokemonDetail, species: PokemonSpecies | None) -> str:
    if species is not None and species.spanish_name:
        return species.spanish_name
    return pokemon.name.replace("-", " ").title()


def build_pokemon_detail(
    pokemon: PokemonDetail,
    species: PokemonSpecies | None = None,
) -> ft.Container:
    height = f"{pokemon.height / 10:.1f} m" if pokemon.height else "No disponible"
    weight = f"{pokemon.weight / 10:.1f} kg" if pokemon.weight else "No disponible"
    description = species.description if species else None
    abilities = ", ".join(
        ability.name.replace("-", " ").title()
        + (" (oculta)" if ability.is_hidden else "")
        for ability in pokemon.abilities
    ) or "No disponible"

    stats_title = ft.Text("Estadísticas", size=14, weight=ft.FontWeight.BOLD)

    return ft.Container(
        content=ft.Column(
            [
                ft.Row(
                    [
                        ft.Image(
                            src=pokemon.sprites.get("front_default") or "",
                            width=130,
                            height=130,
                            fit=ft.BoxFit.CONTAIN,
                        ),
                        ft.Column(
                            [
                                ft.Text(
                                    f"#{pokemon.id:03d}",
                                    color=ft.Colors.GREY,
                                    size=12,
                                ),
                                ft.Text(
                                    _display_name(pokemon, species),
                                    size=24,
                                    weight=ft.FontWeight.BOLD,
                                ),
                                _type_badges(pokemon),
                            ],
                            spacing=4,
                        ),
                    ],
                    spacing=12,
                ),
                ft.Text(description) if description else ft.Text(
                    "Sin descripción disponible",
                    italic=True,
                    color=ft.Colors.GREY,
                ),
                ft.Divider(height=16),
                _info_row("Altura", height),
                _info_row("Peso", weight),
                ft.Divider(height=16),
                _info_row("Habilidades", abilities),
                ft.Divider(height=16),
                stats_title,
                *[build_stat_bar(stat.name, stat.value) for stat in pokemon.stats],
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=6,
            scroll=ft.ScrollMode.AUTO,
        ),
        padding=16,
        border=border(1, ft.Colors.OUTLINE_VARIANT),
        border_radius=12,
    )