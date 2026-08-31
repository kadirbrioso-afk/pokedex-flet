"""Tests de los modelos de dominio."""

from __future__ import annotations

from app.models.generation import GenerationDetail
from app.models.pokemon import PokemonDetail, PokemonSummary, sprite_url

GENERATION_JSON = {
    "id": 1,
    "name": "generation-i",
    "pokemon_species": [
        {"name": "bulbasaur", "url": "https://pokeapi.co/api/v2/pokemon-species/1/"},
        {"name": "ivysaur", "url": "https://pokeapi.co/api/v2/pokemon-species/2/"},
        {"name": "forms", "url": "https://pokeapi.co/api/v2/pokemon-species/10001/"},
    ],
}


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


def test_sprite_url_none_for_forms() -> None:
    assert sprite_url(25) is not None
    assert sprite_url(10001) is None
    assert sprite_url(None) is None


def test_generation_species_summaries() -> None:
    generation = GenerationDetail.model_validate(GENERATION_JSON)
    summaries = generation.species_summaries()

    assert [s.id for s in summaries] == [1, 2, 10001]
    assert summaries[0].name == "bulbasaur"
    assert summaries[0].sprite_url is not None
    assert summaries[0].generation_id == 1
    assert summaries[2].sprite_url is None