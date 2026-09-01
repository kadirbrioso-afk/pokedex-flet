"""Vista de la tabla de tipos (debilidades, resistencias e inmunidades)."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import flet as ft

from app.i18n import t
from app.models.type_chart import TYPE_NAMES, TypeChartResult, TypeMultiplier
from app.services.pokeapi_client import NetworkError, PokeAPIError
from app.services.type_service import TypeService
from app.ui.components.error_message import build_error
from app.ui.components.loading_indicator import build_loading
from app.ui.theme import type_color

NO_TYPE = "—"


def _multiplier_text(value: float) -> str:
    if value == 0.0:
        return t("type.immune")
    if value == 1.0:
        return t("type.normal_damage")
    stripped = f"{value:g}"
    return f"x{stripped}"


def _multiplier_color(value: float) -> str:
    if value == 0.0:
        return "#37474F"
    if value > 1.0:
        return "#C62828"
    if value < 1.0:
        return "#2E7D32"
    return "#757575"


def _type_chip(entry: TypeMultiplier) -> ft.Row:
    return ft.Row(
        [
            ft.Container(
                content=ft.Text(
                    entry.attacking_type.replace("-", " ").title(),
                    color=ft.Colors.WHITE,
                    weight=ft.FontWeight.BOLD,
                    size=12,
                ),
                bgcolor=type_color(entry.attacking_type),
                border_radius=20,
                padding=ft.Padding.symmetric(horizontal=10, vertical=4),
            ),
            ft.Text(
                _multiplier_text(entry.multiplier),
                size=12,
                color=_multiplier_color(entry.multiplier),
                weight=ft.FontWeight.BOLD,
            ),
        ],
        spacing=8,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )


def _neutral_chip(name: str) -> ft.Row:
    attr = TypeMultiplier(attacking_type=name, multiplier=1.0)
    return _type_chip(attr)


def _section(title: str) -> ft.Text:
    return ft.Text(
        title,
        size=14,
        weight=ft.FontWeight.BOLD,
        color=ft.Colors.PRIMARY,
    )


def _group(title: str, entries: list[ft.Row]) -> ft.Column:
    if not entries:
        return ft.Column(
            [ft.Text("—", color=ft.Colors.GREY, size=13)],
            spacing=4,
        )
    return ft.Column(
        [_section(title), *entries],
        spacing=4,
    )


def build_type_chart(result: TypeChartResult) -> ft.Control:
    selected = " / ".join(t.replace("-", " ").title() for t in result.types)
    return ft.ListView(
        controls=[
            ft.Text(
                selected,
                size=18,
                weight=ft.FontWeight.BOLD,
                text_align=ft.TextAlign.CENTER,
            ),
            ft.Divider(height=12),
            _group(
                t("type.weakness"),
                [_type_chip(e) for e in result.weaknesses],
            ),
            ft.Divider(height=12),
            _group(
                t("type.resistance"),
                [_type_chip(e) for e in result.resistances],
            ),
            ft.Divider(height=12),
            _group(
                t("type.immunity"),
                [_type_chip(e) for e in result.immunities],
            ),
            ft.Divider(height=12),
            _group(
                t("type.neutral"),
                [_neutral_chip(name) for name in result.neutral],
            ),
        ],
        spacing=8,
        expand=True,
        padding=8,
    )


class TypeChartView:
    """Permite elegir uno o dos tipos y ver su tabla de debilidades."""

    def __init__(
        self,
        page: ft.Page,
        type_service: TypeService,
        on_close: Callable[[], Any] | None = None,
    ) -> None:
        self._page = page
        self._service = type_service
        self._on_close = on_close

        def options() -> list[ft.dropdown.Option]:
            return [
                ft.dropdown.Option(key=t, text=t.title()) for t in TYPE_NAMES
            ]

        none_option = ft.dropdown.Option(key=NO_TYPE, text=t("type.none"))

        self._type_a = ft.Dropdown(
            label=t("type.type1"),
            value="normal",
            options=options(),
            dense=True,
        )
        self._type_b = ft.Dropdown(
            label=t("type.type2"),
            value=NO_TYPE,
            options=[none_option, *options()],
            dense=True,
        )
        self._calculate_button = ft.FilledButton(
            t("type.calculate"),
            icon=ft.Icons.ONETWOTHREE,
            on_click=self._on_calculate,
        )
        self._close_button = ft.FilledTonalButton(
            t("type.back"),
            icon=ft.Icons.ARROW_BACK,
            on_click=self._on_close_clicked,
        )
        self._result = ft.Container(expand=True)

    def build(self) -> ft.Control:
        return ft.Column(
            [
                ft.Row(
                    [self._type_a, self._type_b],
                    spacing=8,
                ),
                ft.Row(
                    [self._calculate_button, self._close_button],
                    spacing=8,
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                self._result,
            ],
            spacing=8,
            expand=True,
        )

    def _on_close_clicked(self, _: Any) -> None:
        if self._on_close:
            self._on_close()

    def _on_calculate(self, _: Any) -> None:
        type_a = (self._type_a.value or "").strip().lower()
        type_b = (self._type_b.value or "").strip().lower()
        if type_b == NO_TYPE.lower():
            type_b = ""
        if not type_a:
            self._page.show_dialog(
                ft.SnackBar(ft.Text(t("type.need_type1")))
            )
            self._page.update()
            return
        self._page.run_task(self._run, type_a, type_b or None)

    async def _run(self, type_a: str, type_b: str | None) -> None:
        self._calculate_button.disabled = True
        self._result.content = build_loading(t("type.calculating"))
        self._page.update()
        try:
            result = await self._service.build_chart(type_a, type_b)
        except (NetworkError, PokeAPIError) as exc:
            self._result.content = build_error(t("type.error", error=str(exc)))
        else:
            self._result.content = build_type_chart(result)
        finally:
            self._calculate_button.disabled = False
            self._page.update()
