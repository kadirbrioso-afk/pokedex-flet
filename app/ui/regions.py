"""Nombres amigables de las regiones por ID de generación."""

from __future__ import annotations

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


def region_name(generation_id: int, fallback: str = "") -> str:
    """Devuelve el nombre de región de una generación o el fallback."""
    return REGIONS.get(generation_id, fallback)