"""Indicador de carga reutilizable."""

from __future__ import annotations

import flet as ft


def build_loading(message: str = "Cargando…") -> ft.Container:
    return ft.Container(
        content=ft.Row(
            [
                ft.ProgressRing(width=26, height=26),
                ft.Text(message),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=12,
        ),
        padding=32,
        alignment=ft.Alignment.CENTER,
    )