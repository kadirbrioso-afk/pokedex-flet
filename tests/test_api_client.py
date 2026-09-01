"""Tests del PokeAPIClient con respx."""

from __future__ import annotations

import tempfile
from pathlib import Path

import httpx
import pytest
import respx

from app.core.config import AppConfig
from app.services.pokeapi_client import (
    NetworkError,
    PokeAPIClient,
    PokeAPIError,
    PokemonNotFoundError,
)

API = "https://pokeapi.co/api/v2"


def make_config(
    max_retries: int = 2,
    cache_dir: Path | None = None,
    cache_ttl_seconds: int | None = 86400,
) -> AppConfig:
    return AppConfig(
        pokeapi_base_url=API,
        max_retries=max_retries,
        retry_backoff=0.0,
        cache_dir=cache_dir or Path(tempfile.mkdtemp(prefix="pokedex-test-")),
        cache_ttl_seconds=cache_ttl_seconds,
    )


def pokemon_payload() -> dict:
    return {"id": 25, "name": "pikachu", "types": [], "stats": [], "abilities": []}


@respx.mock
async def test_disk_cache_persists_between_client_instances(
    tmp_path: Path,
) -> None:
    route = respx.get(f"{API}/pokemon/25").mock(
        return_value=httpx.Response(200, json=pokemon_payload())
    )
    config = make_config(cache_dir=tmp_path)
    first = PokeAPIClient(config=config)
    await first.get_pokemon(25)
    await first.close()

    second = PokeAPIClient(config=config)
    data = await second.get_pokemon(25)
    await second.close()

    assert data["id"] == 25
    assert route.call_count == 1
    cache_file = tmp_path / "api" / "pokemon" / "25.json"
    assert cache_file.is_file()


@respx.mock
async def test_disk_cache_returns_cached_without_network(tmp_path: Path) -> None:
    config = make_config(cache_dir=tmp_path)
    import json

    cache_file = tmp_path / "api" / "pokemon" / "25.json"
    cache_file.parent.mkdir(parents=True, exist_ok=True)
    cache_file.write_text(
        json.dumps({"expires_at": 10**12, "data": pokemon_payload()}),
        encoding="utf-8",
    )

    client = PokeAPIClient(config=config)
    data = await client.get_pokemon(25)
    await client.close()

    assert data["id"] == 25


@respx.mock
async def test_cached_pokemon_listing(tmp_path: Path) -> None:
    respx.get(f"{API}/pokemon/25").mock(
        return_value=httpx.Response(200, json=pokemon_payload())
    )
    respx.get(f"{API}/pokemon/6").mock(
        return_value=httpx.Response(
            200,
            json={**pokemon_payload(), "id": 6, "name": "charizard"},
        )
    )
    config = make_config(cache_dir=tmp_path)
    client = PokeAPIClient(config=config)
    await client.get_pokemon(25)
    await client.get_pokemon(6)
    await client.close()

    assert client.list_cached_pokemon_ids() == [6, 25]
    cached = client.get_cached_pokemon(6)
    assert cached is not None
    assert cached["name"] == "charizard"


@respx.mock
async def test_get_pokemon_success() -> None:
    respx.get(f"{API}/pokemon/25").mock(
        return_value=httpx.Response(200, json=pokemon_payload())
    )
    client = PokeAPIClient(config=make_config())

    data = await client.get_pokemon(25)

    assert data["id"] == 25
    assert respx.calls.last.request.url.path == "/api/v2/pokemon/25"
    await client.close()


@respx.mock
async def test_get_pokemon_404() -> None:
    respx.get(f"{API}/pokemon/fake").mock(return_value=httpx.Response(404))
    client = PokeAPIClient(config=make_config())

    with pytest.raises(PokemonNotFoundError):
        await client.get_pokemon("fake")
    await client.close()


@respx.mock
async def test_network_error_is_raised() -> None:
    respx.get(f"{API}/pokemon/25").mock(
        side_effect=httpx.ConnectError("connection refused")
    )
    client = PokeAPIClient(config=make_config(max_retries=0))

    with pytest.raises(NetworkError):
        await client.get_pokemon(25)
    await client.close()


@respx.mock
async def test_timeout_is_retried_then_network_error() -> None:
    route = respx.get(f"{API}/pokemon/25").mock(
        side_effect=httpx.ReadTimeout("timed out")
    )
    client = PokeAPIClient(config=make_config(max_retries=1))

    with pytest.raises(NetworkError):
        await client.get_pokemon(25)
    assert route.call_count == 2
    await client.close()


@respx.mock
async def test_retries_on_500_then_succeeds() -> None:
    route = respx.get(f"{API}/pokemon/25").mock(
        side_effect=[
            httpx.Response(500),
            httpx.Response(200, json=pokemon_payload()),
        ]
    )
    client = PokeAPIClient(config=make_config(max_retries=2))

    data = await client.get_pokemon(25)

    assert data["id"] == 25
    assert route.call_count == 2
    await client.close()


@respx.mock
async def test_raises_after_retries_exhausted() -> None:
    route = respx.get(f"{API}/pokemon/25").mock(
        side_effect=[
            httpx.Response(429),
            httpx.Response(429),
            httpx.Response(429),
        ]
    )
    client = PokeAPIClient(config=make_config(max_retries=2))

    with pytest.raises(PokeAPIError):
        await client.get_pokemon(25)
    assert route.call_count == 3
    await client.close()


@respx.mock
async def test_invalid_json_raises_pokeapi_error() -> None:
    respx.get(f"{API}/pokemon/25").mock(
        return_value=httpx.Response(200, content=b"<html>not json</html>")
    )
    client = PokeAPIClient(config=make_config())

    with pytest.raises(PokeAPIError, match="Respuesta no válida"):
        await client.get_pokemon(25)
    await client.close()


@respx.mock
async def test_generations_follows_pagination() -> None:
    respx.get(f"{API}/generation", params={"limit": "100"}).mock(
        return_value=httpx.Response(
            200,
            json={
                "results": [
                    {"name": "generation-i", "url": f"{API}/generation/1/"}
                ],
                "next": f"{API}/generation?offset=1&limit=1",
            },
        )
    )
    respx.get(f"{API}/generation", params={"offset": "1", "limit": "1"}).mock(
        return_value=httpx.Response(
            200,
            json={
                "results": [
                    {"name": "generation-ii", "url": f"{API}/generation/2/"}
                ],
                "next": None,
            },
        )
    )
    client = PokeAPIClient(config=make_config())

    generations = await client.get_generations()

    assert [g["name"] for g in generations] == ["generation-i", "generation-ii"]
    await client.close()


async def test_context_manager_closes_client() -> None:
    with respx.mock:
        respx.get(f"{API}/pokemon/25").mock(
            return_value=httpx.Response(200, json=pokemon_payload())
        )
        async with PokeAPIClient(config=make_config()) as client:
            data = await client.get_pokemon(25)
        assert data["id"] == 25