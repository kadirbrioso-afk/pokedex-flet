"""Tarjeta de Pokémon para listas."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import flet as ft

from app.models.pokemon import PokemonSummary
from app.ui.theme import border


def _on_hover(event: ft.Event[ft.Container]) -> None:
    card = event.control
    hovered = event.data == "true"
    card.scale = 1.03 if hovered else 1.0
    card.shadow = (
        ft.BoxShadow(
            blur_radius=10,
            color=ft.Colors.BLACK38,
            offset=ft.Offset(0, 3),
        )
        if hovered
        else None
    )
    card.update()


def build_pokemon_card(
    summary: PokemonSummary,
    on_click: Callable[[Any], Any] | None = None,
    selected: bool = False,
) -> ft.Container:
    display_name = summary.name.replace("-", " ").title()
    sprite = (
        ft.Image(
            src=summary.sprite_url,
            width=48,
            height=48,
            fit=ft.BoxFit.CONTAIN,
            error_content=ft.Icon(
                ft.Icons.CATCHING_POKEMON,
                size=32,
                color=ft.Colors.GREY,
            ),
        )
        if summary.sprite_url
        else ft.Icon(ft.Icons.CATCHING_POKEMON, size=32, color=ft.Colors.GREY)
    )
    return ft.Container(
        content=ft.Row(
            [
                sprite,
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
        scale=1.0,
        shadow=None,
        animate_scale=ft.Animation(150, ft.AnimationCurve.EASE_OUT),
        on_hover=_on_hover,
        on_click=on_click,
    )