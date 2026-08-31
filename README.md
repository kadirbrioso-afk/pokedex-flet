# Pokédex Flet

Pokédex interactiva de escritorio (y web, opcionalmente) construida con **Python + Flet**, consumiendo **PokeAPI**.

Proyecto basado en el [roadmap](Roadmap_Pokedex_Flet.md) `Roadmap_Pokedex_Flet.md` (Fase 0 activa: scaffold + semilla funcional).

## Requisitos

- Python 3.14+
- [uv](https://docs.astral.sh/uv/)

## Instalación

```bash
uv sync
```

## Ejecución

```bash
uv run python main.py
```

## Calidad

```bash
uv run ruff check .
uv run mypy app
uv run pytest
```

## Estructura

```text
main.py                  # Entrypoint de la app Flet
app/
├── core/                # Config, logging, caché
├── models/              # Modelos Pydantic (Pokemon, Species, Generation, Evolution)
├── services/            # PokeAPIClient asíncrono + servicios con caché
├── state/               # Estado de la aplicación
└── ui/                  # Vistas y componentes Flet
tests/                   # Test unitarios
scripts/                 # Utilidades de desarrollo
assets/                  # Iconos e imágenes
```

## Roadmap

- [x] Fase 0: Entorno y esqueleto del proyecto.
- [ ] Fase 1: Modelos y Python moderno (en curso).
- [ ] Fases 2-10: Cliente API, UI, generaciones, detalle, evolución, rendimiento, calidad y release.

## Estado

Semilla funcional: la app abre una ventana con el layout base. Los modelos, el caché y el cliente de API están listos para construir las siguientes fases.