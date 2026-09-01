"""Tema y colores por tipo de Pokémon."""

from __future__ import annotations

import flet as ft

FONT_FAMILY = "DejaVu Sans"

TYPE_COLORS: dict[str, str] = {
    "normal": "#A8A77A",
    "fire": "#EE8130",
    "water": "#6390F0",
    "electric": "#F7D02C",
    "grass": "#7AC74C",
    "ice": "#96D9D6",
    "fighting": "#C22E28",
    "poison": "#A33EA1",
    "ground": "#E2BF65",
    "flying": "#A98FF3",
    "psychic": "#F95587",
    "bug": "#A6B91A",
    "rock": "#B6A136",
    "ghost": "#735797",
    "dragon": "#6F35FC",
    "dark": "#705746",
    "steel": "#B7B7CE",
    "fairy": "#D685AD",
}


def type_color(type_name: str) -> str:
    return TYPE_COLORS.get(type_name, "#6C757D")


def border(width: int, color: str) -> ft.Border:
    side = ft.BorderSide(width, color)
    return ft.Border(top=side, right=side, bottom=side, left=side)


def card_border(
    selected: bool = False,
    on_surface: bool = False,
) -> ft.Border:
    color = (
        ft.Colors.PRIMARY
        if selected
        else (ft.Colors.OUTLINE if on_surface else ft.Colors.OUTLINE_VARIANT)
    )
    return border(1, color)


def build_theme() -> ft.Theme:
    return ft.Theme(
        color_scheme_seed=ft.Colors.RED,
        font_family=FONT_FAMILY,
        card_theme=ft.CardTheme(
            elevation=2,
            shape=ft.RoundedRectangleBorder(radius=12),
            clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
        ),
        appbar_theme=ft.AppBarTheme(
            bgcolor=ft.Colors.RED,
            color=ft.Colors.WHITE,
            center_title=True,
            elevation=2,
        ),
    )