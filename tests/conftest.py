"""Fixtures compartidos para los tests.

Carga datos reales de PokeAPI desde ``tests/fixtures/`` (descargados por
``scripts/download_fixtures.py``) para pruebas deterministas sin red.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"


def load_fixture(filename: str) -> dict:
    """Carga un archivo de fixture JSON y lo devuelve como dict."""
    path = FIXTURES_DIR / filename
    if not path.is_file():
        pytest.fail(
            f"No existe el fixture {path}. Ejecuta "
            f"`uv run python scripts/download_fixtures.py`."
        )
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.fixture
def pikachu_json() -> dict:
    return load_fixture("pokemon_25.json")


@pytest.fixture
def species_json() -> dict:
    return load_fixture("pokemon-species_25.json")


@pytest.fixture
def evolution_chain_json() -> dict:
    return load_fixture("evolution-chain_10.json")


@pytest.fixture
def generation_json() -> dict:
    return load_fixture("generation_1.json")