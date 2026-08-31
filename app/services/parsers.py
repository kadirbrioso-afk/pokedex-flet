"""Parseo de respuestas JSON de PokeAPI a modelos de dominio."""

from __future__ import annotations

from typing import Any

from app.models.evolution import EvolutionChain, EvolutionNode
from app.models.generation import GenerationDetail, GenerationSummary
from app.models.pokemon import (
    PokemonAbility,
    PokemonDetail,
    PokemonStat,
    PokemonType,
    sprite_url,
)
from app.models.species import PokemonSpecies


def parse_id_from_url(url: str | None) -> int | None:
    if not url:
        return None
    try:
        return int(url.rstrip("/").split("/")[-1])
    except ValueError:
        return None


def pokemon_detail_from_json(data: dict[str, Any]) -> PokemonDetail:
    types = [
        PokemonType(
            name=entry["type"]["name"],
            slot=entry.get("slot", 1),
        )
        for entry in data.get("types", [])
    ]
    stats = [
        PokemonStat(name=entry["stat"]["name"], value=entry.get("base_stat", 0))
        for entry in data.get("stats", [])
    ]
    abilities = [
        PokemonAbility(
            name=entry["ability"]["name"],
            is_hidden=entry.get("is_hidden", False),
            slot=entry.get("slot", 1),
        )
        for entry in data.get("abilities", [])
    ]
    sprites: dict[str, str | None] = {
        key: value
        for key, value in data.get("sprites", {}).items()
        if isinstance(value, str)
    }
    return PokemonDetail(
        id=data["id"],
        name=data["name"],
        height=data.get("height"),
        weight=data.get("weight"),
        base_experience=data.get("base_experience"),
        sprites=sprites,
        types=types,
        stats=stats,
        abilities=abilities,
    )


def _localized_name(data: dict[str, Any]) -> str | None:
    for entry in data.get("names", []):
        if entry.get("language", {}).get("name") == "es":
            return entry.get("name")
    return None


def _description(data: dict[str, Any]) -> str | None:
    entries = data.get("flavor_text_entries", [])
    for entry in entries:
        if entry.get("language", {}).get("name") == "es":
            return entry["flavor_text"].replace("\n", " ").replace("\f", " ")
    for entry in entries:
        if entry.get("language", {}).get("name") == "en":
            return entry["flavor_text"].replace("\n", " ").replace("\f", " ")
    return None


def pokemon_species_from_json(data: dict[str, Any]) -> PokemonSpecies:
    generation_url = data.get("generation", {}).get("url")
    return PokemonSpecies(
        id=data["id"],
        name=data["name"],
        spanish_name=_localized_name(data),
        description=_description(data),
        habitat=data.get("habitat", {}).get("name") if data.get("habitat") else None,
        color=data.get("color", {}).get("name") if data.get("color") else None,
        shape=data.get("shape", {}).get("name") if data.get("shape") else None,
        capture_rate=data.get("capture_rate"),
        base_happiness=data.get("base_happiness"),
        generation=parse_id_from_url(generation_url),
        evolution_chain_url=data.get("evolution_chain", {}).get("url"),
    )


def generation_summary_from_json(data: dict[str, Any]) -> GenerationSummary:
    generation_id = data.get("id") or parse_id_from_url(data.get("url"))
    if generation_id is None:
        raise ValueError("ID de generación no disponible")
    return GenerationSummary(id=generation_id, name=data["name"])


def generation_detail_from_json(data: dict[str, Any]) -> GenerationDetail:
    return GenerationDetail(
        id=data["id"],
        name=data["name"],
        pokemon_species=data.get("pokemon_species", []),
    )


def _evolution_node_from_json(data: dict[str, Any]) -> EvolutionNode:
    species_url = data.get("species", {}).get("url")
    species_name = data.get("species", {}).get("name", "")
    pokemon_id = parse_id_from_url(species_url)

    min_level = None
    item: str | None = None
    trigger: str | None = None
    happiness = False
    trade = False

    for detail in data.get("evolution_details", []):
        trigger = detail.get("trigger", {}).get("name")
        min_level = detail.get("min_level")
        item_name = detail.get("item")
        if item_name:
            item = (
                item_name.get("name")
                if isinstance(item_name, dict)
                else str(item_name)
            )
        if trigger == "happiness":
            happiness = True
        if trigger == "trade":
            trade = True

    children = [
        _evolution_node_from_json(child)
        for child in data.get("evolves_to", [])
    ]
    return EvolutionNode(
        pokemon_name=species_name,
        pokemon_id=pokemon_id,
        sprite_url=sprite_url(pokemon_id),
        min_level=min_level,
        item=item,
        trigger=trigger,
        happiness=happiness,
        trade=trade,
        children=children,
    )


def evolution_chain_from_json(data: dict[str, Any]) -> EvolutionChain:
    return EvolutionChain(
        id=data["id"],
        chain=_evolution_node_from_json(data["chain"]),
    )