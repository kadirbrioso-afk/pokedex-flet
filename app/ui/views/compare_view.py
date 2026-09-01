"""Vista del comparador de Pokémon."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import flet as ft

from app.models.compare import PokemonComparison
from app.services.compare_service import CompareService
from app.services.pokeapi_client import (
    NetworkError,
    PokeAPIError,
    PokemonNotFoundError,
)
from app.ui.components.error_message import build_error
from app.ui.components.loading_indicator import build_loading
from app.ui.theme import type_color
from app.ui.views.detail_view import STAT_ORDER


def _type_badge(type_name: str) -> ft.Container:
    return ft.Container(
        content=ft.Text(
            type_name,
            color=ft.Colors.WHITE,
            weight=ft.FontWeight.BOLD,
            size=12,
        ),
        bgcolor=type_color(type_name),
        border_radius=20,
        padding=ft.Padding.symmetric(horizontal=10, vertical=4),
    )


def _column(title: str, value: str) -> ft.Column:
    return ft.Column(
        [
            ft.Text(title, size=12, color=ft.Colors.GREY),
            ft.Text(value, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=4,
        expand=True,
    )


def _header_row(comparison: PokemonComparison) -> ft.Row:
    def cell(side: Any) -> ft.Column:
        sprite = (
            ft.Image(
                src=side.sprite_url,
                width=90,
                height=90,
                fit=ft.BoxFit.CONTAIN,
                error_content=ft.Icon(
                    ft.Icons.CATCHING_POKEMON,
                    size=40,
                    color=ft.Colors.GREY,
                ),
            )
            if side.sprite_url
            else ft.Icon(
                ft.Icons.CATCHING_POKEMON,
                size=40,
                color=ft.Colors.GREY,
            )
        )
        return ft.Column(
            [
                sprite,
                ft.Text(
                    f"#{side.id:03d}",
                    size=12,
                    color=ft.Colors.GREY,
                ),
                ft.Text(
                    side.display_name,
                    size=18,
                    weight=ft.FontWeight.BOLD,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Row(
                    [_type_badge(t) for t in side.types] or [
                        ft.Text("Sin tipos", color=ft.Colors.GREY)
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=4,
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=4,
            expand=True,
        )

    return ft.Row(
        [cell(comparison.left), cell(comparison.right)],
        alignment=ft.MainAxisAlignment.SPACE_EVENLY,
        spacing=8,
    )


def _stat_pair(label: str, left: int, right: int) -> ft.Row:
    band = max(left, right, 1)
    left_wins = left > right
    right_wins = right > left
    left_ratio = min(left / band, 1.0)
    right_ratio = min(right / band, 1.0)
    left_color = ft.Colors.GREEN if left_wins else ft.Colors.GREY
    right_color = ft.Colors.GREEN if right_wins else ft.Colors.GREY
    return ft.Row(
        [
            ft.Text(str(left), size=24, weight=ft.FontWeight.BOLD,
                    color=left_color, width=50, text_align=ft.TextAlign.RIGHT),
            ft.ProgressBar(
                value=left_ratio,
                color=ft.Colors.PRIMARY,
                bar_height=10,
                width=120,
            ),
            ft.Text(label.replace("-", " ").title(), size=13, width=110,
                    text_align=ft.TextAlign.CENTER),
            ft.ProgressBar(
                value=right_ratio,
                color=ft.Colors.PRIMARY,
                bar_height=10,
                width=120,
            ),
            ft.Text(str(right), size=24, weight=ft.FontWeight.BOLD,
                    color=right_color, width=50, text_align=ft.TextAlign.LEFT),
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=8,
    )


def _section(title: str) -> ft.Text:
    return ft.Text(
        title,
        size=14,
        weight=ft.FontWeight.BOLD,
        color=ft.Colors.PRIMARY,
    )


def _rows_pair(left_rows: list[ft.Control], right_rows: list[ft.Control]) -> ft.Row:
    return ft.Row(
        [
            ft.Column(
                left_rows,
                spacing=4,
                expand=True,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            ft.Column(
                right_rows,
                spacing=4,
                expand=True,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
        ],
        spacing=8,
        alignment=ft.MainAxisAlignment.SPACE_EVENLY,
    )


def _abilities_text(names: list[str]) -> str:
    return ", ".join(name.replace("-", " ").title() for name in names) or "—"


def _victory_badge(left: int, right: int) -> ft.Text:
    if left == right:
        return ft.Text("Empate", size=12, color=ft.Colors.GREY)
    winner = "A" if left > right else "B"
    return ft.Text(
        f"Gana {winner}",
        size=12,
        color=ft.Colors.GREEN,
        weight=ft.FontWeight.BOLD,
    )


def build_comparison(comparison: PokemonComparison) -> ft.Control:
    left = comparison.left
    right = comparison.right

    stat_rows: list[ft.Control] = []
    for stat_name in STAT_ORDER:
        if stat_name in left.stats or stat_name in right.stats:
            stat_rows.append(
                _stat_pair(
                    stat_name,
                    left.stats.get(stat_name, 0),
                    right.stats.get(stat_name, 0),
                )
            )

    evolution_left = " → ".join(left.evolution_names) or "Sin cadena"
    evolution_right = " → ".join(right.evolution_names) or "Sin cadena"

    total_left = _column("Total", str(left.total_stats))
    total_right = _column("Total", str(right.total_stats))
    total_verdict = _victory_badge(left.total_stats, right.total_stats)

    return ft.ListView(
        controls=[
            _header_row(comparison),
            ft.Divider(height=12),
            _section("Total de stats"),
            ft.Row(
                [
                    total_left,
                    total_verdict,
                    total_right,
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=12,
            ),
            ft.Divider(height=12),
            _section("Stats"),
            *stat_rows,
            ft.Divider(height=12),
            _section("Habilidades"),
            _rows_pair(
                [
                    ft.Text(
                        _abilities_text(left.abilities),
                        text_align=ft.TextAlign.CENTER,
                    )
                ],
                [
                    ft.Text(
                        _abilities_text(right.abilities),
                        text_align=ft.TextAlign.CENTER,
                    )
                ],
            ),
            ft.Divider(height=12),
            _section("Evolución"),
            _rows_pair(
                [ft.Text(evolution_left, text_align=ft.TextAlign.CENTER)],
                [ft.Text(evolution_right, text_align=ft.TextAlign.CENTER)],
            ),
        ],
        spacing=8,
        expand=True,
        padding=8,
    )


class CompareView:
    """Comparador de dos Pokémon, con selección de A y B desde la lista."""

    def __init__(
        self,
        page: ft.Page,
        compare_service: CompareService,
        on_pick_a: Callable[[], Any],
        on_pick_b: Callable[[], Any],
        on_close: Callable[[], Any] | None = None,
    ) -> None:
        self._page = page
        self._compare_service = compare_service
        self._on_close = on_close

        self._name_a = ft.Text("—", size=14, weight=ft.FontWeight.BOLD)
        self._name_b = ft.Text("—", size=14, weight=ft.FontWeight.BOLD)
        self._pick_a_button = ft.OutlinedButton(
            "Elegir A",
            icon=ft.Icons.ADD,
            on_click=self._make_pick(lambda: on_pick_a()),
        )
        self._pick_b_button = ft.OutlinedButton(
            "Elegir B",
            icon=ft.Icons.ADD,
            on_click=self._make_pick(lambda: on_pick_b()),
        )
        self._compare_button = ft.FilledButton(
            "Comparar",
            icon=ft.Icons.COMPARE_ARROWS,
            on_click=self._on_compare,
        )
        self._close_button = ft.FilledTonalButton(
            "Volver",
            icon=ft.Icons.ARROW_BACK,
            on_click=self._on_close_clicked,
        )
        self._result = ft.Container(expand=True)
        self._left_name: str | None = None
        self._right_name: str | None = None

    @staticmethod
    def _make_pick(callback: Callable[[], Any]) -> Callable[[Any], Any]:
        def pick(_: Any) -> None:
            callback()

        return pick

    def build(self) -> ft.Control:
        return ft.Column(
            [
                ft.Container(
                    content=ft.Row(
                        [
                            self._side_block(
                                "Pokémon A", self._name_a, self._pick_a_button
                            ),
                            self._side_block(
                                "Pokémon B", self._name_b, self._pick_b_button
                            ),
                        ],
                        spacing=16,
                    ),
                    padding=8,
                    border_radius=10,
                ),
                ft.Row(
                    [self._compare_button, self._close_button],
                    spacing=8,
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                self._result,
            ],
            spacing=8,
            expand=True,
        )

    @staticmethod
    def _side_block(
        label: str,
        name: ft.Text,
        button: ft.Control,
    ) -> ft.Column:
        return ft.Column(
            [
                ft.Text(label, size=12, color=ft.Colors.GREY),
                name,
                button,
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=4,
            expand=True,
        )

    def set_side(self, side: str, name: str) -> None:
        """Asigna el Pokémon elegido de la lista a un lado (\"A\" o \"B\")."""
        if side.upper() == "A":
            self._left_name = name
            self._name_a.value = name
        else:
            self._right_name = name
            self._name_b.value = name

    def has_both(self) -> bool:
        return bool(self._left_name and self._right_name)

    def _on_close_clicked(self, _: Any) -> None:
        if self._on_close:
            self._on_close()

    def _on_compare(self, _: Any) -> None:
        left = self._left_name
        right = self._right_name
        if not left or not right:
            self._page.show_dialog(
                ft.SnackBar(
                    ft.Text("Selecciona ambos Pokémon (A y B) para comparar.")
                )
            )
            self._page.update()
            return
        self._page.run_task(self._run_compare, left, right)

    async def _run_compare(self, left: str, right: str) -> None:
        self._compare_button.disabled = True
        self._result.content = build_loading("Comparando…")
        self._page.update()
        try:
            comparison = await self._compare_service.compare(left, right)
        except PokemonNotFoundError as exc:
            self._result.content = build_error(f"No encontrado: {exc}")
        except (NetworkError, PokeAPIError) as exc:
            self._result.content = build_error(f"Error al comparar: {exc}")
        else:
            self._result.content = build_comparison(comparison)
        finally:
            self._compare_button.disabled = False
            self._page.update()
