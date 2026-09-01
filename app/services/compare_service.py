"""Servicio de comparación de dos Pokémon."""

from __future__ import annotations

from app.models.compare import ComparisonSide, PokemonComparison, build_comparison_side
from app.models.evolution import EvolutionChain
from app.models.pokemon import PokemonDetail
from app.models.species import PokemonSpecies
from app.services.pokemon_service import PokemonService


class CompareService:
    def __init__(self, pokemon_service: PokemonService) -> None:
        self._pokemon_service = pokemon_service

    async def compare(
        self,
        left: str | int,
        right: str | int,
        lang: str = "es",
    ) -> PokemonComparison:
        """Resuelve los detalles de ambos Pokémon y construye la comparación."""
        left_parts = await self._pokemon_service.get_pokemon_detail_full(left)
        right_parts = await self._pokemon_service.get_pokemon_detail_full(right)
        return PokemonComparison(
            left=self._side(*left_parts, lang),
            right=self._side(*right_parts, lang),
        )

    def _side(
        self,
        pokemon: PokemonDetail,
        species: PokemonSpecies,
        chain: EvolutionChain | None,
        lang: str = "es",
    ) -> ComparisonSide:
        return build_comparison_side(pokemon, species, chain, lang)
