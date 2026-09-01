"""Modelos de la tabla de tipos (debilidades, resistencias e inmunidades)."""

from __future__ import annotations

from pydantic import BaseModel

TYPE_NAMES: list[str] = [
    "normal",
    "fire",
    "water",
    "electric",
    "grass",
    "ice",
    "fighting",
    "poison",
    "ground",
    "flying",
    "psychic",
    "bug",
    "rock",
    "ghost",
    "dragon",
    "dark",
    "steel",
    "fairy",
]


class TypeMultiplier(BaseModel):
    attacking_type: str
    multiplier: float


class TypeDamages(BaseModel):
    """Relaciones de daño de un tipo defensivo, extraídas de /type/{type}."""

    name: str = ""
    double_damage_from: list[str] = []
    half_damage_from: list[str] = []
    no_damage_from: list[str] = []


class TypeChartResult(BaseModel):
    """Resultado de combinar uno o dos tipos defensivos."""

    types: list[str]
    weaknesses: list[TypeMultiplier] = []
    resistances: list[TypeMultiplier] = []
    immunities: list[TypeMultiplier] = []
    neutral: list[str] = []


def combine_types(
    type_names: list[str],
    first: TypeDamages,
    second: TypeDamages | None = None,
) -> TypeChartResult:
    """Calcula el multiplicador de cada tipo de ataque frente a la combinación
    de uno o dos tipos defensivos y lo clasifica en una tabla completa (todos
    los tipos aparecen en alguna categoría).

    Reglas de combinación:
    - un atacante en `double_damage_from` multiplica por 2.
    - un atacante en `half_damage_from` multiplica por 0.5.
    - un atacante en `no_damage_from` anula el daño (multiplicador 0).
    - los multiplicadores se multiplican entre los dos tipos defensivos.
    - un atacante que no aparece en ninguna relación se considera neutro (x1).
    """
    counts_by_type = {
        atk: _classify(first, second, atk) for atk in TYPE_NAMES
    }

    weaknesses: list[TypeMultiplier] = []
    resistances: list[TypeMultiplier] = []
    immunities: list[TypeMultiplier] = []
    neutral: list[str] = []
    for atk in TYPE_NAMES:
        mult = counts_by_type[atk]
        item = TypeMultiplier(attacking_type=atk, multiplier=mult)
        if mult > 1:
            weaknesses.append(item)
        elif mult == 0:
            immunities.append(item)
        elif mult < 1:
            resistances.append(item)
        else:
            neutral.append(atk)

    return TypeChartResult(
        types=list(type_names),
        weaknesses=weaknesses,
        resistances=resistances,
        immunities=immunities,
        neutral=neutral,
    )


def _classify(
    first: TypeDamages,
    second: TypeDamages | None,
    atk: str,
) -> float:
    mult = 1.0
    for dmg in (first, second):
        if dmg is None:
            break
        if atk in dmg.no_damage_from:
            mult = 0.0
        elif atk in dmg.double_damage_from:
            mult *= 2.0
        elif atk in dmg.half_damage_from:
            mult *= 0.5
    return mult
