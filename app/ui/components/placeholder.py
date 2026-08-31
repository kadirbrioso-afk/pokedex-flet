"""Placeholder de contenido."""

from __future__ import annotations

import flet as ft


def build_placeholder(message: str) -> ft.Container:
    return ft.Container(
        content=ft.Text(
            message,
            size=16,
            color=ft.Colors.GREY,
            text_align=ft.TextAlign.CENTER,
        ),
        padding=24,
        alignment=ft.Alignment.CENTER,
    )