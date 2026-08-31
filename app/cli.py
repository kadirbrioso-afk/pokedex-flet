"""CLI para probar el cliente de PokeAPI desde la terminal."""

from __future__ import annotations

import argparse
import asyncio
import json
import sys

from pydantic import BaseModel

from app.core.logging import setup_logging
from app.services.generation_service import GenerationService
from app.services.pokeapi_client import (
    NetworkError,
    PokeAPIClient,
    PokeAPIError,
    PokemonNotFoundError,
)
from app.services.pokemon_service import PokemonService


def _print_model(model: BaseModel) -> None:
    print(model.model_dump_json(indent=2))


async def _run(command: str, identifier: str) -> int:
    async with PokeAPIClient() as client:
        if command == "generations":
            generations = await GenerationService(client).get_generations()
            payload = [g.model_dump(mode="json") for g in generations]
            print(json.dumps(payload, indent=2))
            return 0

        if command == "generation":
            _print_model(await GenerationService(client).get_generation(identifier))
            return 0

        service = PokemonService(client)
        if command == "pokemon":
            _print_model(await service.get_pokemon(identifier))
        elif command == "species":
            _print_model(await service.get_species(identifier))
        elif command == "evolution_chain":
            _print_model(await service.get_evolution_chain(identifier))
        elif command == "details":
            pokemon, species = await service.get_pokemon_with_species(identifier)
            _print_model(pokemon)
            print()
            _print_model(species)
        else:
            print(f"Comando no válido: {command}", file=sys.stderr)
            return 2
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="pokedex",
        description="Cliente de línea de comandos para la PokeAPI.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("generations", help="Listar generaciones.")

    for name, help_text in [
        ("get-pokemon", "Detalle de un Pokémon por nombre o ID."),
        ("get-species", "Especie de un Pokémon por nombre o ID."),
        ("get-evolution-chain", "Cadena evolutiva por especie o ID."),
        ("get-generation", "Detalle de una generación por nombre o ID."),
        ("get-details", "Pokémon + especie en una sola llamada."),
    ]:
        sp = sub.add_parser(name, help=help_text)
        sp.add_argument("identifier", help="Nombre o ID.")

    return parser


def main(argv: list[str] | None = None) -> int:
    setup_logging()
    args = build_parser().parse_args(argv)

    command = args.command.replace("-", "_").removeprefix("get_")
    if command == "generations":
        command = "generations"
        identifier = ""
    else:
        identifier = args.identifier

    try:
        return asyncio.run(_run(command, identifier))
    except PokemonNotFoundError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    except NetworkError as exc:
        print(f"Error de red: {exc}", file=sys.stderr)
        return 1
    except PokeAPIError as exc:
        print(f"Error de la API: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())