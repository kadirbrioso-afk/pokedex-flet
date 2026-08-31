"""Vista principal: búsqueda global y lista interactiva por generación."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import flet as ft

from app.models.generation import GenerationSummary
from app.models.pokemon import PokemonSummary
from app.services.generation_service import GenerationService
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
from app.ui.regions import region_name
from app.ui.views.detail_view import build_empty_detail, build_pokemon_detail

PAGE_SIZE = 50


class HomeView:
    def __init__(
        self,
        page: ft.Page,
        state: AppState,
        pokemon_service: PokemonService,
        generation_service: GenerationService,
    ) -> None:
        self._page = page
        self._state = state
        self._pokemon_service = pokemon_service
        self._generation_service = generation_service
        self._generations: list[GenerationSummary] = []
        self._summaries: list[PokemonSummary] = []
        self._selected_index = 0
        self._filter_text = ""
        self._sort_by = "id"
        self._offset = 0

        self._header_text = ft.Text(size=18, weight=ft.FontWeight.BOLD)
        self._list_container = ft.Container(expand=True)
        self._detail_container = ft.Container(width=310)
        self._filter_field = ft.TextField(
            hint_text="Filtrar en esta generación…",
            prefix_icon=ft.Icons.FILTER_LIST,
            expand=True,
            dense=True,
            on_change=self._on_filter_change,
        )
        self._sort_dropdown = ft.Dropdown(
            value="id",
            width=150,
            dense=True,
            label="Orden",
            options=[
                ft.dropdown.Option(key="id", text="Por ID"),
                ft.dropdown.Option(key="name", text="Por nombre"),
            ],
            on_select=self._on_sort_change,
        )
        self._page_label = ft.Text("0 resultados")
        self._prev_button = ft.FilledTonalButton(
            "Anterior",
            icon=ft.Icons.NAVIGATE_BEFORE,
            on_click=self._on_prev_page,
        )
        self._next_button = ft.FilledTonalButton(
            "Siguiente",
            icon=ft.Icons.NAVIGATE_NEXT,
            on_click=self._on_next_page,
        )
        self._pagination_row = ft.Row(
            [
                self._prev_button,
                self._page_label,
                self._next_button,
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=16,
        )
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
                    label="Cargando…",
                )
            ],
            on_change=self._on_generation_selected,
        )

    def build(self) -> ft.Row:
        self._header_text.value = "Pokédex"
        self._list_container.content = build_loading("Cargando generaciones…")
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
                        ft.Row(
                            [self._filter_field, self._sort_dropdown],
                            spacing=8,
                        ),
                        self._list_container,
                        self._pagination_row,
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

    async def load_initial(self) -> None:
        self._rail.disabled = True
        self._page.update()
        try:
            generations = await self._generation_service.get_generations()
        except (NetworkError, PokeAPIError) as exc:
            self._list_container.content = build_error(
                f"Error al cargar las generaciones: {exc}",
                on_retry=self._make_generations_retry(),
            )
            self._page.update()
            return
        self._generations = sorted(generations, key=lambda gen: gen.id)
        self._rail.destinations = [
            ft.NavigationRailDestination(
                icon=ft.Icons.GRID_VIEW,
                label=f"{gen.id} · {region_name(gen.id, gen.name.title())}",
            )
            for gen in self._generations
        ]
        self._rail.disabled = False
        self._page.update()
        await self._load_generation_summaries(self._selected_index)

    def _current_generation(self) -> GenerationSummary | None:
        if not self._generations:
            return None
        return self._generations[self._selected_index]

    def _update_header(self, generation: GenerationSummary) -> None:
        region = region_name(generation.id, generation.name.title())
        self._header_text.value = f"Generación {generation.id} — {region}"

    def _visible_summaries(self) -> list[PokemonSummary]:
        summaries = self._summaries
        if self._filter_text:
            summaries = [
                summary
                for summary in summaries
                if self._filter_text in summary.name
                or (
                    summary.id is not None
                    and self._filter_text == str(summary.id)
                )
            ]
        if self._sort_by == "name":
            summaries = sorted(summaries, key=lambda summary: summary.name)
        else:
            summaries = sorted(
                summaries,
                key=lambda summary: summary.id if summary.id is not None else 0,
            )
        return summaries

    def _render_pokemon_list(self) -> None:
        visible = self._visible_summaries()
        total = len(visible)
        if self._offset >= total and total:
            self._offset = max(0, total - PAGE_SIZE)
        page_items = visible[self._offset : self._offset + PAGE_SIZE]

        if page_items:
            controls: list[ft.Control] = [
                build_pokemon_card(
                    summary,
                    on_click=self._make_pokemon_handler(summary),
                    selected=summary.id == self._state.selected_pokemon_id,
                )
                for summary in page_items
            ]
        else:
            controls = [
                ft.Text(
                    "Sin resultados para el filtro.",
                    color=ft.Colors.GREY,
                    italic=True,
                )
            ]

        self._list_container.content = ft.ListView(
            controls=controls,
            spacing=6,
            expand=True,
            padding=4,
            item_extent=68,
        )

        start = self._offset + 1 if total else 0
        end = min(self._offset + PAGE_SIZE, total)
        self._page_label.value = (
            f"{start}–{end} de {total}" if total else "0 resultados"
        )
        self._prev_button.disabled = self._offset <= 0
        self._next_button.disabled = self._offset + PAGE_SIZE >= total

    async def _load_generation_summaries(self, index: int) -> None:
        generation = self._generations[index]
        self._summaries = []
        self._offset = 0
        self._update_header(generation)
        self._list_container.content = build_loading(
            f"Cargando generación {generation.id}…"
        )
        self._detail_container.content = build_empty_detail()
        self._page.update()
        try:
            summaries = await self._generation_service.get_pokemon_summaries(
                generation.id
            )
        except (NetworkError, PokeAPIError) as exc:
            self._list_container.content = build_error(
                f"Error al cargar la generación {generation.id}: {exc}",
                on_retry=self._make_generation_retry(index),
            )
            self._page.update()
            return
        self._summaries = summaries
        self._render_pokemon_list()
        self._page.update()

    def _make_generations_retry(self) -> Callable[[Any], Any]:
        async def retry(_: Any) -> None:
            await self.load_initial()

        return retry

    def _make_generation_retry(
        self,
        index: int,
    ) -> Callable[[Any], Any]:
        async def retry(_: Any) -> None:
            await self._load_generation_summaries(index)

        return retry

    async def _on_generation_selected(self, event: Any) -> None:
        selected = event.control.selected_index
        if selected is None or selected == self._selected_index:
            return
        self._selected_index = selected
        self._filter_field.value = ""
        self._filter_text = ""
        self._offset = 0
        await self._load_generation_summaries(selected)

    def _on_filter_change(self, _: Any) -> None:
        self._filter_text = (self._filter_field.value or "").strip().lower()
        self._offset = 0
        self._render_pokemon_list()
        self._page.update()

    def _on_sort_change(self, _: Any) -> None:
        self._sort_by = self._sort_dropdown.value or "id"
        self._offset = 0
        self._render_pokemon_list()
        self._page.update()

    def _on_prev_page(self, _: Any) -> None:
        self._offset = max(0, self._offset - PAGE_SIZE)
        self._render_pokemon_list()
        self._page.update()

    def _on_next_page(self, _: Any) -> None:
        self._offset += PAGE_SIZE
        self._render_pokemon_list()
        self._page.update()

    def _make_pokemon_handler(
        self,
        summary: PokemonSummary,
    ) -> Callable[[Any], Any]:
        async def handler(_: Any) -> None:
            if summary.id is None:
                return
            self._state.selected_pokemon_id = summary.id
            self._detail_container.content = build_loading("Cargando detalle…")
            self._render_pokemon_list()
            self._page.update()
            try:
                pokemon, species = (
                    await self._pokemon_service.get_pokemon_with_species(
                        summary.id
                    )
                )
            except PokemonNotFoundError:
                self._detail_container.content = build_error(
                    f"Pokémon «{summary.name}» no encontrado."
                )
            except (NetworkError, PokeAPIError) as exc:
                self._detail_container.content = build_error(
                    f"Error al cargar el detalle: {exc}",
                    on_retry=self._make_detail_retry(summary),
                )
            else:
                self._detail_container.content = build_pokemon_detail(
                    pokemon, species
                )
            self._page.update()

        return handler

    def _make_detail_retry(
        self,
        summary: PokemonSummary,
    ) -> Callable[[Any], Any]:
        handler = self._make_pokemon_handler(summary)

        async def retry(_: Any) -> None:
            await handler(None)

        return retry

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