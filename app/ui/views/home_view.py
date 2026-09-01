"""Vista principal: búsqueda global y lista interactiva por generación."""

from __future__ import annotations

import asyncio
from collections.abc import Callable
from typing import Any

import flet as ft

from app.models.evolution import EvolutionChain
from app.models.generation import GenerationSummary
from app.models.pokemon import PokemonDetail, PokemonSummary
from app.models.species import PokemonSpecies
from app.services.compare_service import CompareService
from app.services.generation_service import GenerationService
from app.services.local_store import LocalStore
from app.services.pokeapi_client import (
    NetworkError,
    PokeAPIClient,
    PokeAPIError,
    PokemonNotFoundError,
)
from app.services.pokemon_service import PokemonService
from app.services.type_service import TypeService
from app.state.app_state import AppState
from app.ui.components.error_message import build_error
from app.ui.components.loading_indicator import build_loading
from app.ui.components.pokemon_card import build_pokemon_card
from app.ui.regions import region_name
from app.ui.views.compare_view import CompareView
from app.ui.views.detail_view import build_empty_detail, build_pokemon_detail
from app.ui.views.type_chart_view import TypeChartView

PAGE_SIZE = 50

VIEW_GENERATION = "generation"
VIEW_OFFLINE = "offline"
VIEW_FAVORITES = "favorites"


class HomeView:
    def __init__(
        self,
        page: ft.Page,
        state: AppState,
        pokemon_service: PokemonService,
        generation_service: GenerationService,
        local_store: LocalStore | None = None,
        compare_service: CompareService | None = None,
        type_service: TypeService | None = None,
    ) -> None:
        self._page = page
        self._state = state
        self._pokemon_service = pokemon_service
        self._generation_service = generation_service
        self._store = local_store or LocalStore()
        self._generations: list[GenerationSummary] = []
        self._summaries: list[PokemonSummary] = []
        self._selected_index = 0
        self._filter_text = ""
        self._sort_by = "id"
        self._offset = 0
        self._view_mode = VIEW_GENERATION

        self._header_text = ft.Text(size=18, weight=ft.FontWeight.BOLD)
        self._list_container = ft.Container(expand=True)
        self._detail_container = ft.Container(width=360)
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
            on_change=self._on_search_change,
        )
        self._search_button = ft.FilledButton(
            "Buscar",
            icon=ft.Icons.SEARCH,
            on_click=self._on_search,
        )
        self._search_generation = 0
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
        self._compare_service = compare_service
        self._pending_side: str | None = None
        self._home_row: ft.Row | None = None
        self._compare = CompareView(
            page,
            compare_service or CompareService(pokemon_service),
            on_pick_a=self._make_begin_pick("A"),
            on_pick_b=self._make_begin_pick("B"),
            on_close=self._close_compare,
        )
        self._compare_container = ft.Container(
            content=self._compare.build(),
            expand=True,
            visible=False,
        )
        self._type_chart = TypeChartView(
            page,
            type_service or TypeService(PokeAPIClient()),
            on_close=self._close_type_chart,
        )
        self._type_chart_container = ft.Container(
            content=self._type_chart.build(),
            expand=True,
            visible=False,
        )

    def _make_begin_pick(self, side: str) -> Callable[[], Any]:
        def begin() -> None:
            self._begin_pick(side)

        return begin

    def _begin_pick(self, side: str) -> None:
        self._pending_side = side
        self._show_home_for_picking(f"Selecciona Pokémon {side} en la lista")
        self._page.update()

    def _assign_pending(self, name: str) -> None:
        if self._pending_side is None:
            return
        self._compare.set_side(self._pending_side, name)
        self._pending_side = None
        self.set_compare(True)

    def _close_compare(self) -> None:
        self.set_compare(False)

    def set_compare(self, on: bool) -> None:
        if on:
            self._pending_side = None
        self._set_active_view(active="compare" if on else "home")

    def set_type_chart(self, on: bool) -> None:
        if on:
            self._pending_side = None
        self._set_active_view(active="type_chart" if on else "home")

    def _close_type_chart(self) -> None:
        self.set_type_chart(False)

    def _set_active_view(self, active: str) -> None:
        """Muestra una única vista (home, compare o type_chart) mutuamente
        excluyente, evitando que se superpongan."""
        if self._home_row is None:
            return
        self._home_row.visible = active == "home"
        self._compare_container.visible = active == "compare"
        self._type_chart_container.visible = active == "type_chart"
        self._page.update()

    def _show_home_for_picking(self, header: str) -> None:
        if self._home_row is None:
            return
        self._set_active_view(active="home")
        self._header_text.value = header
        self._page.update()

    def build(self) -> ft.Stack:
        self._header_text.value = "Pokédex"
        self._list_container.content = build_loading("Cargando generaciones…")
        self._detail_container.content = build_empty_detail()
        self._home_row = ft.Row(
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
        self._home_row.visible = not self._compare_container.visible
        return ft.Stack(
            [self._home_row, self._compare_container, self._type_chart_container],
            expand=True,
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

    def set_offline(self, offline: bool) -> None:
        self._offset = 0
        self._filter_field.value = ""
        self._filter_text = ""
        if offline:
            self._view_mode = VIEW_OFFLINE
            self._header_text.value = "Modo offline — visitados"
            self._summaries = self._offline_summaries()
        else:
            self._restore_after_special_view()
        self._render_pokemon_list()
        self._page.update()

    def set_favorites(self, on: bool) -> None:
        self._offset = 0
        self._filter_field.value = ""
        self._filter_text = ""
        if on:
            self._view_mode = VIEW_FAVORITES
            self._header_text.value = f"Favoritos ({len(self._store.list_favorites())})"
            self._summaries = self._favorite_summaries()
        else:
            self._restore_after_special_view()
        self._render_pokemon_list()
        self._page.update()

    def _restore_after_special_view(self) -> None:
        self._view_mode = VIEW_GENERATION
        if self._generations:
            self._page.run_task(
                self._load_generation_summaries, self._selected_index
            )
        else:
            self._summaries = []

    def _offline_summaries(self) -> list[PokemonSummary]:
        summaries: list[PokemonSummary] = []
        for pokemon_id in self._pokemon_service.cached_pokemon_ids():
            data = self._pokemon_service.get_cached_pokemon(pokemon_id)
            if data is None:
                continue
            name = data.get("name", f"pokemon-{pokemon_id}")
            sprite = (
                data.get("sprites", {}).get("front_default")
                if isinstance(data.get("sprites"), dict)
                else None
            )
            summaries.append(
                PokemonSummary(
                    id=pokemon_id,
                    name=name,
                    sprite_url=sprite if isinstance(sprite, str) else None,
                )
            )
        return summaries

    def _favorite_summaries(self) -> list[PokemonSummary]:
        return [
            PokemonSummary(
                id=entry.id,
                name=entry.name,
                sprite_url=entry.sprite_url,
            )
            for entry in self._store.list_favorites()
        ]

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
        self._list_container.content = ft.Column(
            [
                ft.ProgressBar(),
                build_loading(f"Cargando generación {generation.id}…"),
            ],
            spacing=8,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
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
            if self._pending_side is not None:
                self._assign_pending(summary.name)
                return
            await self._open_detail(summary.id, summary.name)

        return handler

    async def _open_detail(self, pokemon_id: int, name: str) -> None:
        self._state.selected_pokemon_id = pokemon_id
        self._detail_container.content = build_loading("Cargando detalle…")
        self._render_pokemon_list()
        self._page.update()
        try:
            pokemon, species, chain = (
                await self._pokemon_service.get_pokemon_detail_full(pokemon_id)
            )
        except PokemonNotFoundError:
            self._detail_container.content = build_error(
                f"Pokémon «{name}» no encontrado."
            )
        except (NetworkError, PokeAPIError) as exc:
            self._detail_container.content = build_error(
                f"Error al cargar el detalle: {exc}",
                on_retry=self._make_detail_retry(pokemon_id, name),
            )
        else:
            self._store.add_recent(
                pokemon.id,
                pokemon.name,
                self._pokemon_sprite(pokemon),
            )
            self._detail_container.content = (
                self._build_detail_content(pokemon, species, chain)
            )
        self._page.update()

    def _pokemon_sprite(self, pokemon: PokemonDetail) -> str | None:
        return pokemon.sprites.get("front_default") or None

    def _build_detail_content(
        self,
        pokemon: PokemonDetail,
        species: PokemonSpecies | None,
        chain: EvolutionChain | None,
    ) -> ft.Control:
        return build_pokemon_detail(
            pokemon,
            species,
            chain,
            on_pokemon_clicked=self._open_detail,
            is_favorite=self._store.is_favorite(pokemon.id),
            on_toggle_favorite=self._make_toggle_favorite(pokemon, species, chain),
        )

    def _make_toggle_favorite(
        self,
        pokemon: PokemonDetail,
        species: PokemonSpecies | None,
        chain: EvolutionChain | None,
    ) -> Callable[[], Any]:
        def toggle() -> None:
            self._store.toggle_favorite(
                pokemon.id,
                pokemon.name,
                self._pokemon_sprite(pokemon),
            )
            if self._view_mode == VIEW_FAVORITES:
                self._summaries = self._favorite_summaries()
                self._header_text.value = (
                    f"Favoritos ({len(self._store.list_favorites())})"
                )
                self._render_pokemon_list()
            self._detail_container.content = (
                self._build_detail_content(pokemon, species, chain)
            )
            self._page.update()

        return toggle

    def _make_detail_retry(
        self,
        pokemon_id: int,
        name: str,
    ) -> Callable[[Any], Any]:
        async def retry(_: Any) -> None:
            await self._open_detail(pokemon_id, name)

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
        self._search_generation += 1
        await self._run_search(query)

    def _on_search_change(self, event: Any) -> None:
        query = self._current_query()
        if not query:
            self._search_generation += 1
            return
        generation = self._search_generation + 1
        self._search_generation = generation
        self._page.run_task(self._debounced_search, generation, query)

    async def _debounced_search(self, generation: int, query: str) -> None:
        await asyncio.sleep(0.3)
        if generation != self._search_generation:
            return
        await self._run_search(query)

    async def _run_search(self, query: str) -> None:
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
            self._store.add_search(query)
            await self._open_detail(pokemon.id, pokemon.name)
        finally:
            self._set_search_loading(False)
            self._page.update()