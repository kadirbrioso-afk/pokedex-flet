"""Tests de los modelos de dominio."""

from __future__ import annotations

from app.models.pokemon import PokemonDetail, PokemonSummary


def test_pokemon_summary_accepts_minimal_data() -> None:
    summary = PokemonSummary(name="bulbasaur")
    assert summary.id is None
    assert summary.sprite_url is None


def test_pokemon_summary_full() -> None:
    summary = PokemonSummary(id=25, name="pikachu", generation_id=1)
    assert summary.id == 25
    assert summary.generation_id == 1


def test_pokemon_detail_accepts_partial_data() -> None:
    pokemon = PokemonDetail.model_validate({"id": 1, "name": "bulbasaur"})
    assert pokemon.types == []
    assert pokemon.stats == []
    assert pokemon.abilities == []
    assert pokemon.height is None