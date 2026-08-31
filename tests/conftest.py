"""Fixtures compartidos para los tests."""

from __future__ import annotations

import pytest


@pytest.fixture
def pikachu_json() -> dict:
    return {
        "id": 25,
        "name": "pikachu",
        "height": 4,
        "weight": 60,
        "base_experience": 112,
        "sprites": {
            "front_default": "https://example.com/pikachu.png",
            "back_default": None,
        },
        "types": [
            {"slot": 1, "type": {"name": "electric"}},
        ],
        "stats": [
            {"base_stat": 35, "stat": {"name": "hp"}},
            {"base_stat": 55, "stat": {"name": "attack"}},
        ],
        "abilities": [
            {"slot": 1, "is_hidden": False, "ability": {"name": "static"}},
        ],
    }


@pytest.fixture
def species_json() -> dict:
    return {
        "id": 25,
        "name": "pikachu",
        "names": [
            {"language": {"name": "en"}, "name": "Pikachu"},
            {"language": {"name": "es"}, "name": "Pikachu"},
        ],
        "flavor_text_entries": [
            {
                "language": {"name": "es"},
                "flavor_text": "Cuando se enfada\fdescarga\nenergía.",
            }
        ],
        "habitat": {"name": "forest"},
        "color": {"name": "yellow"},
        "shape": {"name": "quadruped"},
        "capture_rate": 190,
        "base_happiness": 50,
        "generation": {"url": "https://pokeapi.co/api/v2/generation/1/"},
        "evolution_chain": {"url": "https://pokeapi.co/api/v2/evolution-chain/10/"},
    }


@pytest.fixture
def evolution_chain_json() -> dict:
    return {
        "id": 10,
        "chain": {
            "species": {
                "name": "pichu",
                "url": "https://pokeapi.co/api/v2/pokemon-species/172/",
            },
            "evolution_details": [],
            "evolves_to": [
                {
                    "species": {
                        "name": "pikachu",
                        "url": "https://pokeapi.co/api/v2/pokemon-species/25/",
                    },
                    "evolution_details": [
                        {"trigger": {"name": "level-up"}, "min_level": 2}
                    ],
                    "evolves_to": [
                        {
                            "species": {
                                "name": "raichu",
                                "url": "https://pokeapi.co/api/v2/pokemon-species/26/",
                            },
                            "evolution_details": [
                                {
                                    "trigger": {"name": "use-item"},
                                    "item": {"name": "thunder-stone"},
                                }
                            ],
                            "evolves_to": [],
                        }
                    ],
                }
            ],
        },
    }