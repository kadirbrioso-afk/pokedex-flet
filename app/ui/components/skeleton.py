"""Esqueletos de carga (skeleton loaders) para la UI."""

from __future__ import annotations

import flet as ft

from app.ui.theme import border


def _block(width: int, height: int) -> ft.Container:
    return ft.Container(
        width=width,
        height=height,
        border_radius=8,
        bgcolor=ft.Colors.SURFACE_CONTAINER_HIGH,
    )


def _bar(width: int, height: int = 10) -> ft.Container:
    return _block(width, height)


def build_skeleton_card() -> ft.Container:
    """Tarjeta apagada que representa una entrada de Pokémon cargando."""
    return ft.Container(
        content=ft.Row(
            [
                _block(48, 48),
                ft.Column(
                    [
                        _bar(120),
                        _bar(80),
                    ],
                    spacing=6,
                ),
            ],
            spacing=12,
        ),
        border=border(1, ft.Colors.OUTLINE_VARIANT),
        border_radius=10,
        padding=8,
    )


def build_skeleton_list(count: int = 8) -> ft.Column:
    """Lista de tarjetas esqueleto para la carga de una generación."""
    return ft.Column(
        [build_skeleton_card() for _ in range(count)],
        spacing=6,
        scroll=ft.ScrollMode.AUTO,
    )


def build_skeleton_detail() -> ft.Container:
    """Esqueleto del panel de detalle mientras carga la información."""
    return ft.Container(
        content=ft.Column(
            [
                ft.Container(
                    content=_block(120, 120),
                    alignment=ft.Alignment.CENTER,
                ),
                _bar(80, 12),
                ft.Row(
                    [_bar(90, 22), _bar(40, 18)],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=8,
                ),
                _bar(160),
                ft.Divider(height=12),
                _bar(200),
                _bar(140),
                _bar(170),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10,
        ),
        padding=16,
        border=border(1, ft.Colors.OUTLINE_VARIANT),
        border_radius=12,
    )