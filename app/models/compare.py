"""Modelos de la comparación de Pokémon."""

from __future__ import annotations

from pydantic import BaseModel

from app.models.evolution import EvolutionChain, EvolutionNode
from app.models.pokemon import PokemonDetail
from app.models.species import PokemonSpecies


def _evolution_names(chain: EvolutionChain | None) -> list[str]:
    names: list[str] = []

    def walk(node: EvolutionNode) -> None:
        names.append(node.pokemon_name.replace("-", " ").title())
        for child in node.children:
            walk(child)

    if chain is not None:
        walk(chain.chain)
    return names


def _display_name(
    pokemon: PokemonDetail, species: PokemonSpecies | None, lang: str = "es"
) -> str:
    if species is not None:
        localized = species.localized_name(lang)
        if localized:
            return localized
    return pokemon.name.replace("-", " ").title()


class ComparisonSide(BaseModel):
    id: int
    name: str
    display_name: str
    sprite_url: str | None = None
    types: list[str] = []
    abilities: list[str] = []
    stats: dict[str, int] = {}
    total_stats: int = 0
    evolution_names: list[str] = []


class PokemonComparison(BaseModel):
    left: ComparisonSide
    right: ComparisonSide


def build_comparison_side(
    pokemon: PokemonDetail,
    species: PokemonSpecies | None,
    chain: EvolutionChain | None,
    lang: str = "es",
) -> ComparisonSide:
    """Construye un lado de la comparación a partir de un detalle resuelto."""
    stats = {stat.name: stat.value for stat in pokemon.stats}
    return ComparisonSide(
        id=pokemon.id,
        name=pokemon.name,
        display_name=_display_name(pokemon, species, lang),
        sprite_url=pokemon.sprites.get("front_default") or None,
        types=[type_.name for type_ in pokemon.types],
        abilities=[ability.name for ability in pokemon.abilities],
        stats=stats,
        total_stats=sum(stats.values()),
        evolution_names=_evolution_names(chain),
    )
