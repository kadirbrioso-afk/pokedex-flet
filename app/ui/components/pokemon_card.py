"""Tarjeta de Pokémon para listas."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import flet as ft

from app.models.pokemon import PokemonSummary
from app.ui.theme import border


def build_pokemon_card(
    summary: PokemonSummary,
    on_click: Callable[[Any], None] | None = None,
    selected: bool = False,
) -> ft.Container:
    display_name = summary.name.replace("-", " ").title()
    return ft.Container(
        content=ft.Row(
            [
                ft.Image(
                    src=summary.sprite_url or "",
                    width=48,
                    height=48,
                    fit=ft.BoxFit.CONTAIN,
                ),
                ft.Column(
                    [
                        ft.Text(
                            f"#{summary.id:03d}" if summary.id else "#---",
                            size=12,
                            color=ft.Colors.GREY,
                        ),
                        ft.Text(display_name, weight=ft.FontWeight.BOLD),
                    ],
                    spacing=0,
                ),
            ],
            spacing=12,
        ),
        bgcolor=(
            ft.Colors.SURFACE_CONTAINER_HIGH if selected else ft.Colors.TRANSPARENT
        ),
        border=border(
            1,
            ft.Colors.PRIMARY if selected else ft.Colors.OUTLINE_VARIANT,
        ),
        border_radius=10,
        padding=8,
        on_click=on_click,
    )