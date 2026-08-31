"""Tema y colores por tipo de Pokémon."""

from __future__ import annotations

import flet as ft

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


def build_theme() -> ft.Theme:
    return ft.Theme(color_scheme_seed=ft.Colors.RED)