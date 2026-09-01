"""Tests de los modelos de dominio."""

from __future__ import annotations

from app.models.generation import GenerationDetail
from app.models.pokemon import PokemonDetail, PokemonSummary, sprite_url
from app.models.species import PokemonSpecies

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


def test_species_localized_name_fallback() -> None:
    species = PokemonSpecies(
        id=25,
        name="pikachu",
        spanish_name="Pikachu",
        names={"es": "Pikachu", "en": "Pikachu", "ja": "ピカチュウ"},
    )
    assert species.localized_name("ja") == "ピカチュウ"
    assert species.localized_name("en") == "Pikachu"
    assert species.localized_name("fr") == "Pikachu"
    assert species.localized_name("de") == "Pikachu"


def test_species_localized_name_falls_back_to_spanish() -> None:
    species = PokemonSpecies(id=1, name="bulbasaur", spanish_name="Bulbasaur")
    assert species.localized_name("en") == "Bulbasaur"
    assert species.localized_name("fr") == "Bulbasaur"


def test_species_localized_description_fallback() -> None:
    species = PokemonSpecies(
        id=25,
        name="pikachu",
        description="Descripción ES",
        descriptions={"en": "Description EN"},
    )
    assert species.localized_description("en") == "Description EN"
    assert species.localized_description("es") == "Description EN"
    assert species.localized_description("fr") == "Description EN"


def test_species_localized_description_no_entries() -> None:
    species = PokemonSpecies(id=1, name="bulbasaur")
    assert species.localized_description("es") is None
    assert species.localized_name("es") is None