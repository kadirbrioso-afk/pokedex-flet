"""Tests del módulo de internacionalización (i18n)."""

from __future__ import annotations

import pytest

from app.i18n import (
    _CATALOG,
    DEFAULT_LANGUAGE,
    LANGUAGES,
    Translator,
    set_language,
    t,
    translator,
)

ES_SAMPLE = "home.empty_query"
ES_TEXT = "Escribe un nombre o ID para buscar."
EN_TEXT = "Type a name or ID to search."


@pytest.fixture(autouse=True)
def _reset_translator() -> None:
    translator.set_lang(DEFAULT_LANGUAGE)


def test_languages_and_default() -> None:
    assert LANGUAGES == ("es", "en")
    assert DEFAULT_LANGUAGE == "es"


def test_translator_default_lang_is_es() -> None:
    assert translator.lang == "es"
    assert t(ES_SAMPLE) == ES_TEXT


def test_translator_switches_language() -> None:
    translator.set_lang("en")
    assert translator.lang == "en"
    assert t(ES_SAMPLE) == EN_TEXT


def test_translator_ignores_unknown_lang() -> None:
    translator.set_lang("fr")
    assert translator.lang == "es"
    assert t(ES_SAMPLE) == ES_TEXT


def test_translator_falls_back_to_es_when_lang_entry_missing() -> None:
    catalog = {"only.es": {"es": "texto"}}
    tr = Translator(lang="en", catalog=catalog)
    assert tr.t("only.es") == "texto"


def test_translator_returns_key_for_missing_entry() -> None:
    assert t("does.not.exist") == "does.not.exist"


def test_translator_formats_kwargs() -> None:
    assert t("home.not_found", name="pikachu") == "Pokémon «pikachu» no encontrado."


def test_translator_missing_kwarg_returns_raw_text() -> None:
    assert t("home.not_found") == "Pokémon «{name}» no encontrado."


def test_set_language_helper() -> None:
    set_language("en")
    assert translator.lang == "en"


def test_catalog_has_both_languages_for_every_key() -> None:
    for key, entry in _CATALOG.items():
        assert set(entry) == {"es", "en"}, key