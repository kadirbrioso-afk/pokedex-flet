"""Parseo de respuestas JSON de PokeAPI a modelos de dominio."""

from __future__ import annotations

from typing import Any

from app.models.evolution import EvolutionChain, EvolutionNode
from app.models.generation import GenerationDetail, GenerationSummary
from app.models.pokemon import (
    PokemonAbility,
    PokemonDetail,
    PokemonMove,
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
    other = data.get("sprites", {}).get("other", {}) or {}
    official_artwork = other.get("official-artwork", {}).get("front_default")
    home = other.get("home", {}).get("front_default")
    if isinstance(official_artwork, str):
        sprites["official_artwork"] = official_artwork
    if isinstance(home, str):
        sprites["home"] = home

    moves: list[PokemonMove] = []
    seen: set[tuple[str, str, int | None]] = set()
    for entry in data.get("moves", []):
        move_name = entry.get("move", {}).get("name")
        if not move_name:
            continue
        details = entry.get("version_group_details") or []
        if details:
            method = details[0].get("move_learn_method", {}).get("name", "level-up")
            level = details[0].get("level_learned_at")
        else:
            method, level = "level-up", None
        key = (move_name, method, level)
        if key in seen:
            continue
        seen.add(key)
        moves.append(
            PokemonMove(name=move_name, learn_method=method, level=level)
        )

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
        moves=moves,
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
    growth_rate = data.get("growth_rate")
    egg_groups = [
        entry.get("name")
        for entry in data.get("egg_groups", [])
        if isinstance(entry.get("name"), str)
    ]
    evolution_chain = data.get("evolution_chain")
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
        gender_rate=data.get("gender_rate"),
        egg_groups=egg_groups,
        growth_rate=growth_rate.get("name") if growth_rate else None,
        generation=parse_id_from_url(generation_url),
        evolution_chain_url=evolution_chain.get("url")
        if isinstance(evolution_chain, dict)
        else None,
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


def _name_from(maybe_dict: Any) -> str | None:
    if isinstance(maybe_dict, dict):
        return maybe_dict.get("name")
    return str(maybe_dict) if maybe_dict else None


def _evolution_node_from_json(data: dict[str, Any]) -> EvolutionNode:
    species_url = data.get("species", {}).get("url")
    species_name = data.get("species", {}).get("name", "")
    pokemon_id = parse_id_from_url(species_url)

    min_level: int | None = None
    item: str | None = None
    trigger: str | None = None
    happiness = False
    trade = False
    min_happiness: int | None = None
    held_item: str | None = None
    time_of_day: str | None = None
    gender: int | None = None
    known_move: str | None = None
    location: str | None = None
    needs_overworld_rain = False
    relative_physical_stats: int | None = None

    for detail in data.get("evolution_details", []):
        trigger = detail.get("trigger", {}).get("name") or trigger
        min_level = detail.get("min_level") or min_level
        item_name = detail.get("item")
        if item_name:
            item = _name_from(item_name)
        held_item_name = detail.get("held_item")
        if held_item_name:
            held_item = _name_from(held_item_name)
        if trigger == "happiness":
            happiness = True
        if trigger == "trade":
            trade = True
        min_happiness = detail.get("min_happiness") or min_happiness
        time_of_day = detail.get("time_of_day") or time_of_day
        gender = detail.get("gender") or gender
        known_move_name = detail.get("known_move")
        if known_move_name:
            known_move = _name_from(known_move_name)
        location_name = detail.get("location")
        if location_name:
            location = _name_from(location_name)
        needs_overworld_rain = bool(detail.get("needs_overworld_rain"))
        relative_physical_stats = (
            detail.get("relative_physical_stats")
            or relative_physical_stats
        )

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
        min_happiness=min_happiness,
        held_item=held_item,
        time_of_day=time_of_day,
        gender=gender,
        known_move=known_move,
        location=location,
        needs_overworld_rain=needs_overworld_rain,
        relative_physical_stats=relative_physical_stats,
        children=children,
    )


def evolution_chain_from_json(data: dict[str, Any]) -> EvolutionChain:
    return EvolutionChain(
        id=data["id"],
        chain=_evolution_node_from_json(data["chain"]),
    )