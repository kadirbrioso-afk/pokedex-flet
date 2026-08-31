"""Tests de servicios con un cliente de API falso."""

from __future__ import annotations

import asyncio
from typing import Any

from app.services.pokemon_service import PokemonService


class FakePokeAPIClient:
    def __init__(
        self,
        pokemon: dict[str, Any] | None = None,
        species: dict[str, Any] | None = None,
    ) -> None:
        self._pokemon = pokemon or {}
        self._species = species or {}
        self.pokemon_calls = 0
        self.species_calls = 0

    async def get_pokemon(self, identifier: str | int) -> dict[str, Any]:
        self.pokemon_calls += 1
        await asyncio.sleep(0)
        return self._pokemon

    async def get_pokemon_species(self, identifier: str | int) -> dict[str, Any]:
        self.species_calls += 1
        await asyncio.sleep(0)
        return self._species

    async def get_generations(self) -> list[dict[str, Any]]:
        return []

    async def get_generation(self, identifier: str | int) -> dict[str, Any]:
        return {"id": identifier, "name": "generation-x", "pokemon_species": []}

    async def get_evolution_chain(self, chain_id: int) -> dict[str, Any]:
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