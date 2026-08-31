# Pokédex Flet

Pokédex interactiva de escritorio (y web, opcionalmente) construida con **Python + Flet**, consumiendo **PokeAPI**.

Proyecto basado en el [roadmap](Roadmap_Pokedex_Flet.md) `Roadmap_Pokedex_Flet.md`. Fases 0-7 completadas.

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

## CLI de pruebas (Fase 2)

Puedes probar el cliente de PokeAPI desde la terminal:

```bash
uv run pokedex get-pokemon pikachu
uv run pokedex get-species pikachu
uv run pokedex get-evolution-chain pikachu
uv run pokedex get-generation 1
uv run pokedex generations
```

Equivalentemente: `uv run python -m app.cli get-pokemon pikachu`.

El cliente implementa reintentos (429/5xx y errores de red), concurrencia limitada con semáforo, paginación y manejo de respuestas inválidas.

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
- [x] Fase 1: Modelos, Python moderno, asyncio y logging.
- [x] Fase 2: Cliente PokeAPI, errores, reintentos, paginación y CLI.
- [x] Fase 3: Maqueta estática Flet con navegación simulada.
  - Componentes reutilizables: `PokemonCard`, `LoadingIndicator`, `ErrorMessage`, `StatBar`.
  - Navegación simulada entre generaciones y detalle falso al hacer click.
  - Toggle de tema oscuro/claro (reto extra).
- [x] Fase 4: MVP de búsqueda de Pokémon.
  - `TextField` + botón Buscar (Enter también busca); query normalizada
    (`strip().lower()`) y último término en `AppState.last_search`.
  - Búsqueda real contra PokeAPI vía `PokemonService.get_pokemon_with_species`
    con indicador de carga y botón deshabilitado mientras consulta.
  - Detalle real: sprite, nombre ES, tipos coloreados, descripción, altura,
    peso, habilidades y barras de stats.
  - Errores amigables: no encontrado (`PokemonNotFoundError`) y error de red
    con botón Reintentar.
  - `PokeAPIClient` inyectado desde `app.py` y cerrado en `on_disconnect`.
- [x] Fase 5: Lista interactiva de generaciones.
  - Generaciones reales desde `/generation` en el `NavigationRail` con nombre de región.
  - Lista de Pokémon de `/generation/{id}` (1 llamada, cacheada); sprites por ID sin llamadas extra.
  - Filtro local por nombre/ID y orden por ID o nombre.
  - Paginación local (50 por página) con botones Anterior/Siguiente.
  - Click en un Pokémon abre el detalle real (loading + errores con reintento).
  - Sprite placeholder para formas (ID ≥ 10000).
- [x] Fase 6: Vista de detalle completa con pestañas.
  - `PokemonService.get_pokemon_detail_full` carga Pokémon, especie y cadena
    evolutiva en paralelo (`asyncio.gather`), cacheada.
  - Pestañas (TabBar/TabBarView): Info, Stats, Evolución, Movimientos,
    Especie y Media.
  - Info: sprite con selector Normal/Shiny/Artwork sin recargar, tipos,
    descripción ES, experiencia, altura, peso y habilidades.
  - Stats: barras en orden estándar (hp→speed) con total.
  - Evolución: cadena clicable (navega al detalle de cada eslabón) con
    condición de evolución (nivel, objeto, intercambio, amistad…).
  - Movimientos: agrupados por método de aprendizaje (por nivel, MT/MO,
    huevo, tutor) y nivel en el método de nivel.
  - Especie: hábitat, color, forma, género (♂/♀ % desde `gender_rate`),
    grupo huevo, crecimiento, ratio de captura y generación.
  - Media: galería de sprites frontales/traseros (normal y shiny), artwork
    oficial y Home.
- [x] Fase 7: Evoluciones y relaciones avanzadas.
  - `EvolutionNode` ampliado con condiciones completas: `min_happiness`,
    `held_item`, `time_of_day`, `gender` (macho/hembra), `known_move`,
    `location`, `needs_overworld_rain` y `relative_physical_stats`.
  - Parser de `evolution_details` extrae todas las condiciones sin romper
    cadenas ramificadas (verificado con Eevee: 8 ramas, piedras y hora).
  - Flechas de evolución con condiciones legibles (nivel, objeto,
    intercambio, amistad, hora, género, movimiento, ubicación, lluvia).
  - Reto extra: tooltip con las condiciones completas al pasar el ratón
    por la flecha evolutiva.

## Estado

Detalle completo con pestañas (info, stats, evolución, movimientos, especie y media) para cualquier Pokémon, con selector de sprite, cadena evolutiva navegable y datos en español. La app lista generaciones en vivo desde PokeAPI: navegación por región, lista filtrable y ordenable, paginación local, búsqueda global y detalle real al hacer click.