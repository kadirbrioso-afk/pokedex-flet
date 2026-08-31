"""Vista principal con navegación simulada (maqueta de la Fase 3)."""

from __future__ import annotations

import asyncio
from collections.abc import Callable
from typing import Any

import flet as ft

from app.models.generation import GenerationSummary
from app.models.pokemon import PokemonSummary
from app.services.pokeapi_client import (
    NetworkError,
    PokeAPIError,
    PokemonNotFoundError,
)
from app.services.pokemon_service import PokemonService
from app.state.app_state import AppState
from app.ui.components.error_message import build_error
from app.ui.components.loading_indicator import build_loading
from app.ui.components.pokemon_card import build_pokemon_card
from app.ui.mock_data import mock_generations, mock_pokemon
from app.ui.views.detail_view import (
    build_detail,
    build_empty_detail,
    build_pokemon_detail,
)


class HomeView:
    def __init__(
        self,
        page: ft.Page,
        state: AppState,
        pokemon_service: PokemonService,
    ) -> None:
        self._page = page
        self._state = state
        self._pokemon_service = pokemon_service
        self._generations = mock_generations()
        self._selected_index = 0
        self._header_text = ft.Text(size=18, weight=ft.FontWeight.BOLD)
        self._list_container = ft.Container(expand=True)
        self._detail_container = ft.Container(width=310)
        self._search_field = ft.TextField(
            hint_text="Nombre o ID (ej. pikachu, 25)",
            expand=True,
            dense=True,
            on_submit=self._on_search,
        )
        self._search_button = ft.FilledButton(
            "Buscar",
            icon=ft.Icons.SEARCH,
            on_click=self._on_search,
        )
        self._rail = ft.NavigationRail(
            selected_index=0,
            label_type=ft.NavigationRailLabelType.ALL,
            min_width=120,
            destinations=[
                ft.NavigationRailDestination(
                    icon=ft.Icons.GRID_VIEW,
                    label=f"{generation.id} · {generation.name}",
                )
                for generation in self._generations
            ],
            on_change=self._on_generation_selected,
        )

    def build(self) -> ft.Row:
        self._update_header()
        self._render_pokemon_list()
        self._detail_container.content = build_empty_detail()
        return ft.Row(
            [
                self._rail,
                ft.VerticalDivider(width=1),
                ft.Column(
                    [
                        ft.Row(
                            [self._search_field, self._search_button],
                            spacing=8,
                        ),
                        self._header_text,
                        self._list_container,
                    ],
                    expand=True,
                    spacing=8,
                ),
                ft.VerticalDivider(width=1),
                self._detail_container,
            ],
            expand=True,
            spacing=0,
        )

    def _current_generation(self) -> GenerationSummary:
        return self._generations[self._selected_index]

    def _update_header(self) -> None:
        generation = self._current_generation()
        self._header_text.value = f"Generación {generation.id} — {generation.name}"

    def _render_pokemon_list(self) -> None:
        generation = self._current_generation()
        controls: list[ft.Control] = []
        for summary in mock_pokemon(generation.id):
            controls.append(
                build_pokemon_card(
                    summary,
                    on_click=self._make_pokemon_handler(summary),
                    selected=summary.id == self._state.selected_pokemon_id,
                )
            )
        self._list_container.content = ft.ListView(
            controls=controls,
            spacing=6,
            expand=True,
            padding=4,
        )

    def _make_pokemon_handler(
        self,
        summary: PokemonSummary,
    ) -> Callable[[Any], None]:
        def handler(_: Any) -> None:
            self._state.selected_pokemon_id = summary.id
            self._detail_container.content = build_detail(summary)
            self._render_pokemon_list()
            self._page.update()

        return handler

    async def _on_generation_selected(self, event: Any) -> None:
        selected = event.control.selected_index
        if selected is None:
            return
        self._selected_index = selected
        self._update_header()
        self._list_container.content = build_loading()
        self._detail_container.content = build_empty_detail()
        self._page.update()
        await asyncio.sleep(0.4)
        self._render_pokemon_list()
        self._page.update()

    def _current_query(self) -> str:
        value = self._search_field.value or ""
        return value.strip().lower()

    def _set_search_loading(self, loading: bool) -> None:
        self._search_field.disabled = loading
        self._search_button.disabled = loading

    def _make_retry(self, query: str) -> Callable[[Any], Any]:
        async def retry(_: Any) -> None:
            self._search_field.value = query
            await self._on_search(None)

        return retry

    async def _on_search(self, _: Any) -> None:
        query = self._current_query()
        if not query:
            self._page.show_dialog(
                ft.SnackBar(ft.Text("Escribe un nombre o ID para buscar."))
            )
            self._page.update()
            return
        self._state.last_search = query
        self._set_search_loading(True)
        self._detail_container.content = build_loading("Buscando…")
        self._page.update()
        try:
            pokemon, species = await self._pokemon_service.get_pokemon_with_species(
                query
            )
        except PokemonNotFoundError:
            self._detail_container.content = build_error(
                f"No hay ningún Pokémon llamado «{query}»."
            )
        except (NetworkError, PokeAPIError) as exc:
            self._detail_container.content = build_error(
                f"Error al buscar: {exc}",
                on_retry=self._make_retry(query),
            )
        else:
            self._state.selected_pokemon_id = pokemon.id
            self._detail_container.content = build_pokemon_detail(pokemon, species)
        finally:
            self._set_search_loading(False)
            self._page.update()