"""Punto de entrada de la interfaz Flet."""

from __future__ import annotations

from typing import Any

import flet as ft

from app import __version__
from app.core.config import AppConfig
from app.services.pokeapi_client import PokeAPIClient
from app.services.pokemon_service import PokemonService
from app.state.app_state import AppState
from app.ui.theme import build_theme
from app.ui.views.home_view import HomeView


def _build_app_bar(page: ft.Page, title: str) -> ft.AppBar:
    dark_mode = False

    def toggle_theme(_: Any) -> None:
        nonlocal dark_mode
        dark_mode = not dark_mode
        page.theme_mode = ft.ThemeMode.DARK if dark_mode else ft.ThemeMode.LIGHT
        page.update()

    return ft.AppBar(
        title=ft.Text(title),
        center_title=True,
        bgcolor=ft.Colors.RED_700,
        color=ft.Colors.WHITE,
        actions=[
            ft.IconButton(
                icon=ft.Icons.DARK_MODE,
                icon_color=ft.Colors.WHITE,
                tooltip="Cambiar tema",
                on_click=toggle_theme,
            ),
        ],
    )


def start(page: ft.Page) -> None:
    config = AppConfig()
    page.title = f"{config.app_name} v{__version__}"
    page.theme = build_theme()
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 8
    page.spacing = 8

    page.appbar = _build_app_bar(page, config.app_name)

    client = PokeAPIClient()

    async def on_disconnect(_: Any) -> None:
        await client.close()

    page.on_disconnect = on_disconnect
    page.add(HomeView(page, AppState(), PokemonService(client)).build())
    page.update()