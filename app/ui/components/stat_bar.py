"""Barra visual de una estadística."""

from __future__ import annotations

import flet as ft

STAT_COLORS: dict[str, str] = {
    "hp": ft.Colors.GREEN,
    "attack": ft.Colors.RED,
    "defense": ft.Colors.BLUE,
    "special-attack": ft.Colors.PURPLE,
    "special-defense": ft.Colors.TEAL,
    "speed": ft.Colors.AMBER,
}


def build_stat_bar(name: str, value: int, base: int = 255) -> ft.Row:
    ratio = min(value / base, 1.0)
    color = STAT_COLORS.get(name, ft.Colors.GREY)
    return ft.Row(
        [
            ft.Text(name.replace("-", " ").title(), width=120),
            ft.ProgressBar(
                value=ratio,
                color=color,
                bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
                bar_height=10,
                width=120,
            ),
            ft.Text(str(value), width=32, text_align=ft.TextAlign.RIGHT),
        ],
        spacing=8,
    )