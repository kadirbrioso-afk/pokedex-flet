"""Tests de los parseadores de PokeAPI."""

from __future__ import annotations

from app.models.evolution import EvolutionNode
from app.services.parsers import (
    evolution_chain_from_json,
    generation_detail_from_json,
    generation_summary_from_json,
    pokemon_detail_from_json,
    pokemon_species_from_json,
)


def test_parse_pikachu_detail(pikachu_json: dict) -> None:
    pokemon = pokemon_detail_from_json(pikachu_json)
    assert pokemon.id == 25
    assert pokemon.name == "pikachu"
    assert pokemon.types[0].name == "electric"
    assert pokemon.types[0].slot == 1
    assert {s.name for s in pokemon.stats} == {"hp", "attack"}
    assert pokemon.abilities[0].name == "static"
    assert pokemon.sprites["front_default"] == "https://example.com/pikachu.png"
    assert None not in pokemon.sprites.values()


def test_parse_moves_and_artwork(pikachu_json: dict) -> None:
    data = {**pikachu_json, "moves": []}
    data["moves"] = [
        {
            "move": {"name": "quick-attack"},
            "version_group_details": [
                {"level_learned_at": 11, "move_learn_method": {"name": "level-up"}}
            ],
        },
        {
            "move": {"name": "thunderbolt"},
            "version_group_details": [
                {"level_learned_at": 0, "move_learn_method": {"name": "machine"}}
            ],
        },
    ]
    data["sprites"] = {
        **data["sprites"],
        "other": {
            "official-artwork": {"front_default": "https://example.com/artwork.png"},
            "home": {"front_default": "https://example.com/home.png"},
        },
    }
    pokemon = pokemon_detail_from_json(data)
    assert len(pokemon.moves) == 2
    assert pokemon.moves[0].name == "quick-attack"
    assert pokemon.moves[0].learn_method == "level-up"
    assert pokemon.moves[0].level == 11
    assert pokemon.moves[1].learn_method == "machine"
    assert pokemon.sprites["official_artwork"] == "https://example.com/artwork.png"
    assert pokemon.sprites["home"] == "https://example.com/home.png"


def test_parse_species_spanish(species_json: dict) -> None:
    species = pokemon_species_from_json(species_json)
    assert species.id == 25
    assert species.spanish_name == "Pikachu"
    assert species.description is not None
    assert "á" in species.description or species.description
    assert species.habitat == "forest"
    assert species.color == "yellow"
    assert species.generation == 1
    assert species.evolution_chain_url.endswith("10/")


def test_parse_species_extras(species_json: dict) -> None:
    data = {
        **species_json,
        "gender_rate": 4,
        "egg_groups": [
            {"name": "field"},
            {"name": "fairy"},
        ],
        "growth_rate": {"name": "medium"},
    }
    species = pokemon_species_from_json(data)
    assert species.gender_rate == 4
    assert species.egg_groups == ["field", "fairy"]
    assert species.growth_rate == "medium"


def test_parse_species_without_optional(species_json: dict) -> None:
    minimal = {"id": 25, "name": "pikachu", "names": [], "flavor_text_entries": []}
    species = pokemon_species_from_json(minimal)
    assert species.habitat is None
    assert species.color is None
    assert species.gender_rate is None
    assert species.egg_groups == []
    assert species.growth_rate is None


def test_parse_evolution_chain(evolution_chain_json: dict) -> None:
    chain = evolution_chain_from_json(evolution_chain_json)
    assert chain.id == 10
    root = chain.chain
    assert root.pokemon_name == "pichu"
    assert root.pokemon_id == 172
    assert root.sprite_url is not None

    middle: EvolutionNode = root.children[0]
    assert middle.pokemon_name == "pikachu"
    assert middle.min_level == 2
    assert middle.trigger == "level-up"

    leaf = middle.children[0]
    assert leaf.pokemon_name == "raichu"
    assert leaf.item == "thunder-stone"
    assert leaf.trigger == "use-item"


def test_parse_generation_summary_from_results_entry() -> None:
    summary = generation_summary_from_json(
        {"name": "generation-i", "url": "https://pokeapi.co/api/v2/generation/1/"}
    )
    assert summary.id == 1
    assert summary.name == "generation-i"


def test_parse_generation() -> None:
    generation = generation_detail_from_json(
        {
            "id": 1,
            "name": "generation-i",
            "pokemon_species": [
                {"name": "bulbasaur", "url": "https://pokeapi.co/api/v2/pokemon-species/1/"},
                {"name": "ivysaur", "url": "https://pokeapi.co/api/v2/pokemon-species/2/"},
            ],
        }
    )
    assert generation.id == 1
    assert generation.species_ids() == [1, 2]