"""Descarga fixtures reales de PokeAPI para usar en tests deterministas.

Uso:
    uv run python scripts/download_fixtures.py
"""

from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

import httpx

from app.core.config import AppConfig

FIXTURES: dict[str, str] = {
    "pokemon_25.json": "pokemon/25",
    "pokemon-species_25.json": "pokemon-species/25",
    "evolution-chain_10.json": "evolution-chain/10",
    "generation_1.json": "generation/1",
}


async def main() -> None:
    config = AppConfig()
    fixtures_dir = Path(__file__).resolve().parent.parent / "tests" / "fixtures"
    fixtures_dir.mkdir(parents=True, exist_ok=True)

    async with httpx.AsyncClient(timeout=config.request_timeout) as client:
        for filename, path in FIXTURES.items():
            url = f"{config.pokeapi_base_url}/{path}"
            response = await client.get(url)
            response.raise_for_status()
            (fixtures_dir / filename).write_text(
                json.dumps(response.json(), ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            print(f"OK  {filename}")
    print(f"Fixtures guardadas en {fixtures_dir}")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        sys.exit(130)