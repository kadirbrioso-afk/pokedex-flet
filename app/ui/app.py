"""Punto de entrada de la interfaz Flet."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import flet as ft

from app import __version__
from app.core.config import AppConfig
from app.services.generation_service import GenerationService
from app.services.pokeapi_client import PokeAPIClient
from app.services.pokemon_service import PokemonService
from app.state.app_state import AppState
from app.ui.theme import build_theme
from app.ui.views.home_view import HomeView


def _build_app_bar(
    page: ft.Page,
    title: str,
    on_offline_toggle: Callable[[bool], Any] | None = None,
) -> ft.AppBar:
    dark_mode = False
    offline = False

    def toggle_theme(_: Any) -> None:
        nonlocal dark_mode
        dark_mode = not dark_mode
        page.theme_mode = ft.ThemeMode.DARK if dark_mode else ft.ThemeMode.LIGHT
        page.update()

    def toggle_offline(_: Any) -> None:
        nonlocal offline
        offline = not offline
        if on_offline_toggle:
            on_offline_toggle(offline)

    return ft.AppBar(
        title=ft.Text(title),
        center_title=True,
        bgcolor=ft.Colors.RED_700,
        color=ft.Colors.WHITE,
        actions=[
            ft.IconButton(
                icon=ft.Icons.CLOUD_OFF,
                icon_color=ft.Colors.WHITE,
                tooltip="Modo offline (visitados)",
                on_click=toggle_offline,
            ),
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
    page.window.icon = "icons/logo.ico"

    client = PokeAPIClient()

    async def on_disconnect(_: Any) -> None:
        await client.close()

    page.on_disconnect = on_disconnect
    home = HomeView(
        page,
        AppState(),
        PokemonService(client),
        GenerationService(client),
    )
    page.appbar = _build_app_bar(page, config.app_name, home.set_offline)
    page.add(home.build())
    page.run_task(home.load_initial)
    page.update()