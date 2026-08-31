"""Tests de servicios con un cliente de API falso."""

from __future__ import annotations

import asyncio
from typing import Any

from app.services.generation_service import GenerationService
from app.services.pokemon_service import PokemonService


class FakePokeAPIClient:
    def __init__(
        self,
        pokemon: dict[str, Any] | None = None,
        species: dict[str, Any] | None = None,
        generation: dict[str, Any] | None = None,
    ) -> None:
        self._pokemon = pokemon or {}
        self._species = species or {}
        self._generation = generation or {
            "id": 1,
            "name": "generation-i",
            "pokemon_species": [
                {
                    "name": "bulbasaur",
                    "url": "https://pokeapi.co/api/v2/pokemon-species/1/",
                },
            ],
        }
        self.pokemon_calls = 0
        self.species_calls = 0
        self.generation_calls = 0
        self.evolution_calls = 0

    async def get_pokemon(self, identifier: str | int) -> dict[str, Any]:
        self.pokemon_calls += 1
        await asyncio.sleep(0)
        return self._pokemon

    async def get_pokemon_species(self, identifier: str | int) -> dict[str, Any]:
        self.species_calls += 1
        await asyncio.sleep(0)
        return self._species

    async def get_generations(self) -> list[dict[str, Any]]:
        return [
            {"name": "generation-i", "url": "https://pokeapi.co/api/v2/generation/1/"}
        ]

    async def get_generation(self, identifier: str | int) -> dict[str, Any]:
        self.generation_calls += 1
        await asyncio.sleep(0)
        return self._generation

    async def get_evolution_chain(self, chain_id: int) -> dict[str, Any]:
        self.evolution_calls += 1
        return {
            "id": chain_id,
            "chain": {
                "species": {"name": "x", "url": ""},
                "evolution_details": [],
                "evolves_to": [],
            },
        }

    async def close(self) -> None:
        return None


async def test_get_pokemon_parses_model(
    pikachu_json: dict[str, Any],
) -> None:
    client = FakePokeAPIClient(pokemon=pikachu_json)
    service = PokemonService(client)

    pokemon = await service.get_pokemon("pikachu")

    assert pokemon.id == 25
    assert pokemon.name == "pikachu"
    assert client.pokemon_calls == 1


async def test_get_pokemon_is_cached(pikachu_json: dict[str, Any]) -> None:
    client = FakePokeAPIClient(pokemon=pikachu_json)
    service = PokemonService(client)

    first = await service.get_pokemon(25)
    second = await service.get_pokemon(25)

    assert first is second
    assert client.pokemon_calls == 1


async def test_get_pokemon_with_species_is_concurrent(
    pikachu_json: dict[str, Any],
    species_json: dict[str, Any],
) -> None:
    client = FakePokeAPIClient(pokemon=pikachu_json, species=species_json)
    service = PokemonService(client)

    pokemon, species = await service.get_pokemon_with_species("pikachu")

    assert pokemon.id == 25
    assert species.id == 25
    assert species.spanish_name == "Pikachu"
    assert client.pokemon_calls == 1
    assert client.species_calls == 1


async def test_get_pokemon_detail_full_includes_chain(
    pikachu_json: dict[str, Any],
    species_json: dict[str, Any],
) -> None:
    client = FakePokeAPIClient(pokemon=pikachu_json, species=species_json)
    service = PokemonService(client)

    pokemon, species, chain = await service.get_pokemon_detail_full("pikachu")

    assert pokemon.id == 25
    assert species.id == 25
    assert chain is not None
    assert chain.id == 10
    assert client.pokemon_calls == 1
    assert client.species_calls == 1
    assert client.evolution_calls == 1
    second = await service.get_pokemon_detail_full("pikachu")
    assert second[0] is pokemon
    assert second[1] is species
    assert second[2] is chain
    assert client.pokemon_calls == 1
    assert client.species_calls == 1
    assert client.evolution_calls == 1


async def test_get_pokemon_detail_full_without_chain(
    pikachu_json: dict[str, Any],
) -> None:
    species = {
        "id": 25,
        "name": "pikachu",
        "names": [],
        "flavor_text_entries": [],
        "evolution_chain": None,
    }
    client = FakePokeAPIClient(pokemon=pikachu_json, species=species)
    service = PokemonService(client)

    pokemon, species, chain = await service.get_pokemon_detail_full(25)

    assert pokemon.id == 25
    assert chain is None
    assert client.evolution_calls == 0


async def test_generation_summaries_build_sprite_urls() -> None:
    generation = {
        "id": 1,
        "name": "generation-i",
        "pokemon_species": [
            {"name": "bulbasaur", "url": "https://pokeapi.co/api/v2/pokemon-species/1/"},
            {"name": "forms", "url": "https://pokeapi.co/api/v2/pokemon-species/10001/"},
        ],
    }
    client = FakePokeAPIClient(generation=generation)
    service = GenerationService(client)

    summaries = await service.get_pokemon_summaries(1)

    assert len(summaries) == 2
    assert summaries[0].name == "bulbasaur"
    assert summaries[0].sprite_url is not None
    assert summaries[1].sprite_url is None
    assert summaries[0].generation_id == 1
    assert client.generation_calls == 1


async def test_generation_summaries_are_cached() -> None:
    client = FakePokeAPIClient()
    service = GenerationService(client)

    first = await service.get_pokemon_summaries(1)
    second = await service.get_pokemon_summaries(1)

    assert first == second
    assert client.generation_calls == 1


async def test_get_generations_parses_fake_payload() -> None:
    client = FakePokeAPIClient()
    service = GenerationService(client)

    generations = await service.get_generations()

    assert len(generations) == 1
    assert generations[0].id == 1
    assert generations[0].name == "generation-i"