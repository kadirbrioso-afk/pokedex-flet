# Changelog

Todas las fases del proyecto `pokedex-flet`. Formato basado en [Keep a Changelog](https://keepachangelog.com/).

## [Unreleased]

### Formas especiales y megavoluciones
- **Selector de formas en el detalle**: las especies con varias variedades
  (mega, gmax, Deoxys, etc.) muestran un desplegable «Forma» en la ficha.
  Cambiar de forma recarga la entrada de `PokeAPI` (p. ej. `/pokemon/10034/`
  para Mega Charizard X) y muestra el skeleton mientras carga.
- **Modelo `varieties`**: `PokemonSpecies` ahora parsea `varieties` de
  `pokemon-species` (nombre por pantalla + `pokemon_id` + `is_default`);
  nuevo `PokemonVariety`.
- **`sprite_url` sin filtro**: se permite el sprite de formas con ID 10000+
  (los assets de GitHub de PokeAPI sí están disponibles).
- **Favoritos estables**: los favoritos/recientes siempre usan el ID y sprite
  **default** de la especie, sin importar la forma activa.
- **Fix async**: el cambio de forma se ejecuta mediante `page.run_task` para
  no bloquear el evento; guard en `SpriteCache.ensure` para rutas locales.

### Caché de sprites local + artwork por defecto
- **Caché de imágenes con Pillow**: nuevo `SpriteCache` descarga cada sprite
  de PokeAPI una sola vez y lo guarda como WebP en `~/.cache/pokedex-flet/sprites`
  (~95% menos de datos que los PNG originales). Las siguientes visitas se sirven
  desde disco sin red, y la app funciona con imágenes aunque no haya conexión.
- **Integración con la UI**: la lista de generación, el detalle, la cadena
  evolutiva y los modos offline/favoritos resuelven las imágenes a rutas
  locales antes de renderizar; concurrencia limitada por semáforo.
- **Artwork por defecto**: la imagen principal del detalle y el desplegable de
  vistas seleccionan ahora "Artwork" (arte oficial de alta resolución) en lugar
  del sprite clásico si está disponible.
- **Degradación segura**: si la descarga o conversión falla, se devuelve la URL
  original y la UI mantiene el icono de respaldo (sin caché no rompe nada).

### Fase 15 - Tema visual profesional
- **Tipografía consistente**: fuente unificada en todo el tema
  (`Theme.font_family`), `CardTheme` (esquinas redondeadas y elevación) y
  `AppBarTheme` aplicados a nivel de tema.
- **Modo oscuro**: la app arranca en el tema del sistema
  (`ThemeMode.SYSTEM`) y el botón de la AppBar sigue alternando claro/oscuro.
- **Colores por tipo**: `TYPE_COLORS` (18 tipos) ya usados en badges,
  comparador y tabla de tipos (funcionalidad existente integrada en el tema).
- **Skeleton loaders**: nuevo `app/ui/components/skeleton.py` con tarjetas,
  lista y detalle «esqueleto» que se muestran mientras cargan las
  generaciones y el detalle de un Pokémon.
- **Animaciones sutiles**: las tarjetas de la lista tienen elevarse/scale y
  sombra al pasar el cursor (transición de 150 ms).
- **Iconos consistentes**: icono común (CATCHING_POKEMON) para sprites
  ausentes en listas, detalle y evoluciones.
- **Versión 0.2.0**: primera release menor (última fase del roadmap).

### Fase 14 - Internacionalización (ES/EN)
- Nuevo módulo `app/i18n`: catálogo bilingüe con más de 150 claves, clase
  `Translator` (idioma activo), funciones `t()`/`set_language()` y fallbacks a
  `es` y a la propia clave.
- `PokemonSpecies` ahora guarda `names` y `descriptions` (dicts por idioma)
  además de `spanish_name`/`description` (backward compatible), con
  `localized_name(lang)` y `localized_description(lang)` con fallbacks.
- Selector de idioma en la AppBar (botón TRANSLATE): alterna ES/EN y
  re-renderiza la vista activa (home, comparador o tabla de tipos).
- La vista de detalle se muestra localizada (tabs, campos, nombre y descripción
  de especie en el idioma activo).
- El comparador y la tabla de tipos traducen sus textos y usan el idioma activo
  para los nombres (`CompareService.compare(..., lang=...)`).

### Fase 11 - Favoritos y persistencia local
- Nuevo `LocalStore` (repositorio JSON atómico en
  `~/.local/share/pokedex-flet/local.json`) que persiste favoritos, últimos
  vistos e historial de búsqueda.
- Botón de estrella en el detalle para (des)marcar favorito.
- Botón «Favoritos» en la AppBar que lista los Pokémon marcados.
- Registro de recientes (cada visita) e historial de búsqueda (cada búsqueda
  exitosa).
- `AppConfig.data_dir` añadido; modelos `FavoriteEntry`/`RecentEntry`.

### Fase 12 - Comparador de Pokémon
- `CompareService` y modelo `PokemonComparison` con dos lados (A/B), cada uno
  con stats, tipos, habilidades y nombres de evolución.
- Vista comparador (`CompareView`) accesible desde la AppBar: selectores A y B
  con prefill de los últimos vistos, comparación de stats con barras lado a
  lado (ganador en verde), total, tipos, habilidades y cadenas evolutivas.
- `HomeView` ahora usa un `Stack` para superponer la vista de comparación sobre
  la principal.

### Fase 12 - arreglos del comparador
- Se elimina la superposición de vistas: la lista principal y el comparador son
  ahora mutuamente excluyentes (al abrir el comparador se oculta la lista, y
  viceversa), sin solaparse.
- La selección de Pokémon A y B se hace **desde la lista**: botones «Elegir A» y
  «Elegir B» en el comparador; al pulsarlos vuelves a la lista para escoger el
  Pokémon (con aviso «Selecciona Pokémon A/B»), y al hacer clic en uno se asigna
  al lado correspondiente y se muestra la comparación.

### Fase 13 - Tabla de tipos
- Nuevo `TypeService` y modelo `TypeChartResult` que combinan uno o dos tipos
  defensivos y calculan las debilidades (x2/x4), resistencias (x0.5/x0.25),
  inmunidades (x0) y daño normal (x1) contra los 18 tipos de ataque del juego
  (endpoint `/type/{type}`).
- Vista «Tabla de tipos» accesible desde la AppBar (botón GRID_ON): selector de
  uno o dos tipos y tabla visual con badges de color según la relación de daño
  recibido, con leyenda y multiplicadores.
- Fixtures reales de tipos (`type_10/11/3/8.json`) añadidos al descargador y
  cobertura del servicio y la lógica de combinación.

## [0.1.0] - 2026-09-01

Fases 0-9 completadas y Fase 10 (empaquetado y distribución).

### Fase 10 - Empaquetado y distribución
- Metadatos de build Flet (`[tool.flet]`) en `pyproject.toml`: `product`, `org`, `company`, `description` y exclusión de `tests`/`scripts`/`.github`/`.venv`/`build`/`docs` del paquete.
- `CHANGELOG.md` con el historial de fases.
- Documentación de instalación y build para usuarios finales en `README.md`.
- Workflow CI de build (`.github/workflows/release.yml`) que compila el ejecutable Linux en `ubuntu-latest` y sube el artefacto.

### Fase 9 - Fixtures reales, cobertura y CI
- Fixtures JSON reales de PokeAPI trackeados en git y cargados desde archivo en `tests/conftest.py`.
- Cobertura (91.97%) con `pytest-cov` y umbral del 70% sobre `app/services` + `app/models`.
- Workflow `ci.yml` (GitHub Actions): ruff, mypy y pytest.

### Fase 8 - Caché en disco, debounce y modo offline
- Caché en disco bajo `~/.cache/pokedex-flet/api/` con TTL.
- Debounce de 300 ms en el buscador.
- Modo offline: navegación y búsqueda sobre datos cacheados.
- `ProgressBar` al cargar listas grandes.

### Fase 7 - Condiciones de evolución avanzadas y tooltips
- `EvolutionNode` ampliado: `min_happiness`, `held_item`, `time_of_day`, `gender`, `known_move`, `location`, `needs_overworld_rain`, `relative_physical_stats`.
- Condiciones legibles en español y tooltips multifila en la cadena evolutiva.

### Fase 6 - Vista de detalle con pestañas
- Detalle completo con 6 pestañas: Info, Stats, Evolución, Movs, Especie y Media.
- Selector de sprite (Normal | Shiny | Artwork), stats con total, evoluciones clicables.
- Información de especie: género %, grupos huevo, ratio de crecimiento, movimientos por método.

### Fase 5 - Lista interactiva de generaciones
- Vista de generaciones con filtro, orden y paginación en vivo, `GenerationService` inyectado.

### Fase 4 - MVP de búsqueda
- Búsqueda real de Pokémon contra PokeAPI desde la UI.

### Fase 3 - Maqueta Flet
- Navegación simulada y estructura base de la interfaz.

### Fase 2 - Cliente PokeAPI robusto y CLI
- Cliente `httpx` asíncrono con reintentos y manejo de errores.
- Comando CLI `pokedex`.

### Fase 1 - Asyncio, logging y context managers
- Base `asyncio`, logging estructurado y gestión de recursos con context managers.

### Fase 0 - Bootstrap
- Scaffold del proyecto con `uv`, estructura y tooling.
