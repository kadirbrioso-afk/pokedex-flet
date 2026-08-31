"""Entrypoint de la Pokédex Flet."""

from __future__ import annotations

import flet as ft

from app.ui.app import start


def main(page: ft.Page) -> None:
    start(page)


if __name__ == "__main__":
    ft.run(main)