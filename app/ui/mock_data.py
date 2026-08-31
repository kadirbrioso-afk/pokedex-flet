"""Datos estáticos para la maqueta de la Fase 3.

Los sprites apuntan a URLs estáticas de PokeAPI, pero no se hace
ninguna llamada HTTP: son datos simulados.
"""

from __future__ import annotations

from app.models.generation import GenerationSummary
from app.models.pokemon import PokemonSummary, sprite_url

REGIONS: dict[int, str] = {
    1: "Kanto",
    2: "Johto",
    3: "Hoenn",
    4: "Sinnoh",
    5: "Unova",
    6: "Kalos",
    7: "Alola",
    8: "Galar",
    9: "Paldea",
}

SPECIES: dict[int, list[tuple[int, str]]] = {
    1: [
        (1, "bulbasaur"),
        (2, "ivysaur"),
        (4, "charmander"),
        (7, "squirtle"),
        (25, "pikachu"),
        (133, "eevee"),
    ],
    2: [
        (152, "chikorita"),
        (155, "cyndaquil"),
        (158, "totodile"),
        (161, "sentret"),
        (175, "togepi"),
    ],
    3: [
        (252, "treecko"),
        (255, "torchic"),
        (258, "mudkip"),
        (280, "ralts"),
        (304, "aron"),
    ],
    4: [(387, "turtwig"), (390, "chimchar"), (393, "piplup"), (412, "burmy")],
    5: [(495, "snivy"), (498, "tepig"), (501, "oshawott"), (599, "klink")],
    6: [(650, "chespin"), (653, "fennekin"), (656, "froakie"), (661, "fletchling")],
    7: [(722, "rowlet"), (725, "litten"), (728, "popplio"), (731, "pikipek")],
    8: [(810, "grookey"), (813, "scorbunny"), (816, "sobble")],
    9: [(906, "sprigatito"), (909, "fuecoco"), (912, "quaxly"), (929, "dolliv")],
}


def mock_generations() -> list[GenerationSummary]:
    return [
        GenerationSummary(id=generation_id, name=REGIONS[generation_id])
        for generation_id in sorted(REGIONS)
    ]


def mock_pokemon(generation_id: int) -> list[PokemonSummary]:
    return [
        PokemonSummary(
            id=pokemon_id,
            name=name,
            sprite_url=sprite_url(pokemon_id),
            generation_id=generation_id,
        )
        for pokemon_id, name in SPECIES.get(generation_id, [])
    ]