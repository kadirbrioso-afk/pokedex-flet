"""Vista de detalle de un Pokémon (maqueta estática de la Fase 3)."""

from __future__ import annotations

import flet as ft

from app.models.pokemon import PokemonSummary
from app.ui.components.stat_bar import build_stat_bar
from app.ui.theme import border


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
                    fit=ft.ImageFit.CONTAIN,
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