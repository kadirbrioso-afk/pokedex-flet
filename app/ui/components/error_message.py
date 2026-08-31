"""Mensaje de error reutilizable."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import flet as ft


def build_error(
    message: str,
    on_retry: Callable[[Any], None] | None = None,
) -> ft.Container:
    content: list[ft.Control] = [
        ft.Icon(ft.Icons.ERROR_OUTLINE, size=40, color=ft.Colors.ERROR),
        ft.Text(message, text_align=ft.TextAlign.CENTER),
    ]
    if on_retry is not None:
        content.append(ft.FilledTonalButton("Reintentar", on_click=on_retry))
    return ft.Container(
        content=ft.Column(
            content,
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=12,
        ),
        bgcolor=ft.Colors.ERROR_CONTAINER,
        border_radius=12,
        padding=24,
        alignment=ft.Alignment.CENTER,
    )