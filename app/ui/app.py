"""Punto de entrada de la interfaz Flet."""

from __future__ import annotations

import flet as ft

from app import __version__
from app.core.config import AppConfig
from app.ui.components.placeholder import build_placeholder
from app.ui.theme import build_theme


def start(page: ft.Page) -> None:
    config = AppConfig()
    page.title = f"{config.app_name} v{__version__}"
    page.theme = build_theme()
    page.theme_mode = ft.ThemeMode.SYSTEM
    page.padding = 16
    page.spacing = 16

    app_bar = ft.AppBar(
        title=ft.Text(config.app_name),
        center_title=True,
        bgcolor=ft.Colors.RED_700,
        color=ft.Colors.WHITE,
    )

    rail = ft.NavigationRail(
        selected_index=0,
        label_type=ft.NavigationRailLabelType.ALL,
        min_width=100,
        destinations=[
            ft.NavigationRailDestination(icon=ft.Icons.HOME, label="Inicio"),
            ft.NavigationRailDestination(icon=ft.Icons.LIST, label="Generaciones"),
            ft.NavigationRailDestination(icon=ft.Icons.MANAGE_SEARCH, label="Detalle"),
        ],
    )

    content = ft.Column(
        [
            ft.Text(
                "Semilla funcional lista",
                size=28,
                weight=ft.FontWeight.BOLD,
            ),
            build_placeholder(
                "Busca, navega por generaciones y abre el detalle desde aquí."
            ),
        ],
        expand=True,
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )

    page.appbar = app_bar
    page.add(
        ft.Row(
            [
                rail,
                ft.VerticalDivider(width=1),
                content,
            ],
            expand=True,
        )
    )