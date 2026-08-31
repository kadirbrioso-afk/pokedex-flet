---
title: "Roadmap Senior: Pokédex en Python + Flet + PokeAPI"
description: Hoja de ruta completa para construir una aplicación GUI en Python con Flet que consuma PokeAPI, muestre información detallada de Pokémon y gestione listas interactivas por generación.
autor: Kadir
nivel: Intermedio-Avanzado
status: En desarrollo
tags:
  - developing
  - roadmap
---
---

# 🧭 Roadmap Senior: Pokédex en Python + Flet + PokeAPI

## 🎯 Objetivo general

Construir una aplicación de escritorio, y opcionalmente web, usando **Python + Flet**, que funcione como una **Pokédex interactiva** conectada a **PokeAPI**.

La aplicación deberá permitir:

1. Buscar Pokémon por nombre o ID.
2. Navegar por generaciones.
3. Mostrar una lista interactiva de Pokémon por generación.
4. Ver información detallada de cada Pokémon:
   - Imagen/sprite.
   - Tipos.
   - Habilidades.
   - Estadísticas base.
   - Altura y peso.
   - Experiencia base.
   - Movimientos.
   - Información de especie.
   - Cadena evolutiva.
   - Variantes, formas y datos adicionales.
5. Manejar estados de carga, errores, caché y experiencia de usuario.
6. Aplicar buenas prácticas de arquitectura, testing, empaquetado y distribución.

---

## 🧠 Enfoque pedagógico

Este roadmap no está pensado para “copiar y pegar código”, sino para que construyas una aplicación real dominando cada capa del problema:

- Python moderno.
- Programación asíncrona.
- Consumo de APIs REST.
- Modelado de datos.
- UI con Flet.
- Arquitectura de aplicaciones.
- Rendimiento.
- Testing.
- Empaquetado.
- UX.
- Mantenibilidad.

Cada fase incluye:

- Objetivo.
- Contenidos que debes dominar.
- Tareas concretas.
- Pistas senior.
- Criterios de aceptación.
- Retos adicionales.

No avances de fase si no puedes explicar con tus propias palabras qué problema resolviste y por qué lo resolviste así.

---

## 📦 Entregable final esperado

Al terminar el roadmap, deberías tener una aplicación similar a esta:

```text
┌────────────────────────────────────────────────────────────┐
│ Pokédex Flet                                      [Buscar] │
├───────────────┬────────────────────────────────────────────┤
│ Generaciones  │  Lista de Pokémon                          │
│               │                                            │
│ [1] Kanto     │  #001 Bulbasaur   [sprite]                 │
│ [2] Johto     │  #002 Ivysaur     [sprite]                 │
│ [3] Hoenn     │  #003 Venusaur    [sprite]                 │
│ [4] Sinnoh    │  #004 Charmander  [sprite]                 │
│ [5] Unova     │  ...                                       │
│ [6] Kalos     │                                            │
│ ...           │                                            │
├───────────────┴────────────────────────────────────────────┤
│ Detalle: Bulbasaur                                         │
│ [Info] [Stats] [Evoluciones] [Movimientos] [Especie]       │
│                                                            │
│ Tipos: grass / poison                                      │
│ Altura: 0.7 m                                              │
│ Peso: 6.9 kg                                               │
│ Habilidades: Overgrow / Chlorophyll                        │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

---

## 🧱 Stack recomendado

### Lenguaje
- Python 3.11 o superior.
- Idealmente Python 3.12+ si tu entorno lo soporta.

### UI
- Flet.
- Usa una versión reciente de Flet.
- Consulta la documentación oficial porque Flet evoluciona rápido.

### HTTP
- `httpx` recomendado para llamadas asíncronas.
- Alternativa: `aiohttp`.
- No uses `requests` bloqueante dentro de handlers de UI si no sabes lo que estás haciendo.

### Modelado de datos
- `pydantic` v2 recomendado.
- Alternativa: `dataclasses` + validación manual.

### Caché
- Memoria: `functools.lru_cache`, diccionarios o caché propia.
- Disco: SQLite, `diskcache`, JSON cache o caché HTTP.

### Testing
- `pytest`.
- `pytest-asyncio`.
- `respx` para mockear `httpx`.
- Fixtures JSON reales descargadas de PokeAPI.

### Calidad
- `ruff` para linting.
- `mypy` o `pyright` para tipado.
- `black` opcional.
- `pre-commit` opcional pero muy recomendable.

### Empaquetado
- `flet build`.
- `pyinstaller` si necesitas alternativas.
- GitHub Actions para builds automáticos.

---

## 🗺️ Arquitectura recomendada

No mezcles todo en `main.py`. Desde el principio, piensa en capas:

```text
┌────────────────────┐
│       UI Flet      │
│  vistas, controles │
└─────────┬──────────┘
          │ usa
┌─────────▼──────────┐
│   Estado/AppState  │
│ generación actual  │
│ pokemon seleccionado│
└─────────┬──────────┘
          │ consume
┌─────────▼──────────┐
│   Servicios        │
│ PokemonService     │
│ GenerationService  │
└─────────┬──────────┘
          │ llama
┌─────────▼──────────┐
│   API Client       │
│ PokeAPIClient      │
└─────────┬──────────┘
          │ HTTP
┌─────────▼──────────┐
│     PokeAPI        │
└────────────────────┘
```

### Estructura de proyecto sugerida

```text
pokedex_flet/
├── main.py
├── pyproject.toml
├── requirements.txt
├── README.md
├── assets/
│   ├── icons/
│   └── images/
├── app/
│   ├── __init__.py
│   ├── core/
│   │   ├── config.py
│   │   ├── logging.py
│   │   └── cache.py
│   ├── models/
│   │   ├── pokemon.py
│   │   ├── species.py
│   │   ├── generation.py
│   │   └── evolution.py
│   ├── services/
│   │   ├── pokeapi_client.py
│   │   ├── pokemon_service.py
│   │   └── generation_service.py
│   ├── state/
│   │   └── app_state.py
│   └── ui/
│       ├── theme.py
│       ├── components/
│       │   ├── pokemon_card.py
│       │   ├── stat_bar.py
│       │   ├── evolution_node.py
│       │   └── loading_view.py
│       └── views/
│           ├── home_view.py
│           ├── generation_view.py
│           ├── detail_view.py
│           └── settings_view.py
├── tests/
│   ├── fixtures/
│   ├── test_api_client.py
│   ├── test_parsers.py
│   └── test_services.py
└── scripts/
    ├── download_fixtures.py
    └── run_dev.sh
```

---

## 🌐 Endpoints clave de PokeAPI

Base URL:

```text
https://pokeapi.co/api/v2
```

### Endpoints principales

| Propósito             |                        Endpoint | Comentario                                                    |
| --------------------- | ------------------------------: | ------------------------------------------------------------- |
| Listar generaciones   |         `/generation?limit=100` | Útil para menú de generaciones.                               |
| Detalle de generación |      `/generation/{id_or_name}` | Incluye lista de especies de esa generación.                  |
| Pokémon               |         `/pokemon/{id_or_name}` | Datos principales: tipos, stats, habilidades, sprites.        |
| Especie               | `/pokemon-species/{id_or_name}` | Descripción, hábitat, género, nombres localizados, evolución. |
| Cadena evolutiva      |         `/evolution-chain/{id}` | Se obtiene desde `pokemon-species`.                           |
| Tipo                  |            `/type/{id_or_name}` | Debilidades, resistencias, movimientos asociados.             |
| Habilidad             |         `/ability/{id_or_name}` | Descripción y efectos.                                        |
| Movimiento            |            `/move/{id_or_name}` | Poder, precisión, tipo, clase.                                |
| Item                  |            `/item/{id_or_name}` | Opcional para objetos evolutivos.                             |

### Endpoints para listas

| Propósito | Endpoint | Comentario |
|---|---:|---|
| Pokémon planos | `/pokemon?limit=...&offset=...` | Lista global, pero no agrupa por generación. |
| Especies | `/pokemon-species?limit=...&offset=...` | Puede servir para búsquedas globales. |
| Generaciones | `/generation?limit=...` | Menú de generaciones. |

---

# 🚀 Fases del Roadmap

---

## Fase 0: Preparación del entorno y mentalidad profesional

### Objetivo

Crear un entorno de desarrollo limpio, versionado y profesional antes de escribir lógica de aplicación.

### Contenidos que debes dominar

- Instalación de Python.
- Entornos virtuales.
- `pip`, `requirements.txt` o `pyproject.toml`.
- Git básico.
- Estructura de proyectos Python.
- Terminal/consola.
- Editor de código: VS Code, PyCharm o Neovim.
- Configuración de intérprete en el editor.
- Activación de entornos virtuales en Windows, Linux y macOS.

### Tareas

1. Instalar Python 3.11+.
2. Crear carpeta del proyecto:

   ```text
   pokedex-flet
   ```

3. Crear repositorio Git.
4. Crear entorno virtual:

   ```bash
   python -m venv .venv
   ```

5. Activar entorno:

   Windows PowerShell:

   ```bash
   .venv\Scripts\Activate.ps1
   ```

   Linux/macOS:

   ```bash
   source .venv/bin/activate
   ```

6. Instalar dependencias iniciales:

   ```bash
   pip install flet httpx pydantic
   ```

7. Crear `requirements.txt` o `pyproject.toml`.
8. Crear `.gitignore` para Python.
9. Crear `README.md`.
10. Hacer primer commit.

### Pistas senior

- No instales paquetes globalmente.
- Fija versiones desde temprano.
- Si quieres una experiencia más moderna, investiga `uv`, `pip-tools` o `poetry`.
- Un buen `.gitignore` evita subir `.venv`, `__pycache__`, `.pytest_cache`, builds y artefactos.
- Crea un script simple para ejecutar la app.

### Criterios de aceptación

- El proyecto tiene Git.
- El entorno virtual funciona.
- Las dependencias están instaladas.
- Puedes ejecutar un script simple de Python.
- El editor reconoce el intérprete correcto.

### Reto extra

Crea un `Makefile` o scripts en `scripts/`:

```bash
make install
make run
make test
make lint
```

---

## Fase 1: Fundamentos de Python moderno

### Objetivo

Asegurar que dominas las herramientas del lenguaje que necesitarás para construir una aplicación seria.

### Contenidos que debes dominar

- Type hints.
- Dataclasses.
- Pydantic.
- Manejo de excepciones.
- Context managers.
- `asyncio`.
- `async` / `await`.
- `pathlib`.
- `logging`.
- JSON.
- Diccionarios, listas, comprensiones.
- Manejo de `None`.
- Inmutabilidad y estructuras de datos.
- Testing básico con `pytest`.

### Tareas

1. Crear un módulo `app/models/pokemon.py`.
2. Definir modelos simples usando Pydantic:

   ```python
   from pydantic import BaseModel

   class PokemonSummary(BaseModel):
       id: int
       name: str
       sprite_url: str | None = None
   ```

3. Crear una función que convierta un diccionario JSON en un modelo.
4. Escribir tests pequeños para ese parser.
5. Practicar con `asyncio`:

   ```python
   import asyncio

   async def main():
       print("Hola")
       await asyncio.sleep(1)
       print("Async")

   asyncio.run(main())
   ```

6. Configurar `logging` básico.

### Pistas senior

- No abuses de `Any`.
- Si usas Pydantic, aprovecha validadores para normalizar datos.
- Aprende la diferencia entre `list[str]`, `Optional[str]` y `str | None`.
- En APIs externas, nunca confíes en que un campo siempre vendrá.
- Diseña modelos para tu dominio, no copies literalmente toda la respuesta JSON.

### Criterios de aceptación

- Puedes explicar qué es un type hint y por qué ayuda.
- Puedes convertir JSON a objetos Python validados.
- Entiendes qué es una función asíncrona.
- Tienes al menos 3 tests pasando.

### Reto extra

Crea un modelo `PokemonDetail` que acepte un JSON parcial y no falle si faltan campos opcionales.

---

## Fase 2: Consumo de PokeAPI sin interfaz gráfica

### Objetivo

Construir un cliente de API robusto antes de mezclarlo con UI.

### Contenidos que debes dominar

- APIs REST.
- Métodos HTTP: GET.
- Códigos de estado: 200, 404, 429, 500.
- JSON.
- `httpx.AsyncClient`.
- Timeouts.
- Reintentos.
- Paginación.
- Manejo de errores de red.
- Serialización/deserialización.
- Testing con mocks.

### Tareas

1. Crear `app/services/pokeapi_client.py`.
2. Implementar una clase `PokeAPIClient`.
3. Métodos mínimos:

   ```python
   class PokeAPIClient:
       async def get_generations(self) -> list[GenerationSummary]: ...
       async def get_generation(self, identifier: str | int) -> GenerationDetail: ...
       async def get_pokemon(self, identifier: str | int) -> PokemonDetail: ...
       async def get_pokemon_species(self, identifier: str | int) -> PokemonSpecies: ...
       async def get_evolution_chain(self, chain_id: int) -> EvolutionChain: ...
   ```

4. Probar manualmente desde terminal:

   ```bash
   python -m app.cli get-pokemon pikachu
   python -m app.cli get-generation 1
   ```

5. Manejar errores:
   - Pokémon no encontrado.
   - Timeout.
   - Error de red.
   - Respuesta inesperada.

### Endpoints que debes probar

```text
GET https://pokeapi.co/api/v2/generation?limit=100
GET https://pokeapi.co/api/v2/generation/1
GET https://pokeapi.co/api/v2/pokemon/pikachu
GET https://pokeapi.co/api/v2/pokemon-species/pikachu
GET https://pokeapi.co/api/v2/evolution-chain/10
```

### Pistas senior

- Usa un único `httpx.AsyncClient` reutilizable si es posible.
- Configura timeout explícito:

  ```python
  timeout = httpx.Timeout(10.0, connect=5.0)
  ```

- No hagas `print` de todo el JSON; parsea solo lo necesario.
- Crea excepciones propias:

  ```python
  class PokeAPIError(Exception): ...
  class PokemonNotFoundError(PokeAPIError): ...
  class NetworkError(PokeAPIError): ...
  ```

- Parsea IDs desde URLs cuando la API devuelva recursos anidados.
- Ejemplo:

  ```text
  https://pokeapi.co/api/v2/pokemon-species/1/
  ```

  El ID es `1`.

- Si vas a hacer muchas llamadas, usa `asyncio.Semaphore` para limitar concurrencia.
- No descargues todos los Pokémon de golpe si no lo necesitas.

### Criterios de aceptación

- El cliente puede obtener generaciones.
- El cliente puede obtener un Pokémon por nombre e ID.
- El cliente puede obtener especie.
- El cliente puede obtener cadena evolutiva.
- Hay manejo de errores.
- Hay tests unitarios usando fixtures o mocks.

### Reto extra

Implementa caché simple en memoria:

```python
self._cache: dict[str, PokemonDetail] = {}
```

---

## Fase 3: Fundamentos de Flet

### Objetivo

Dominar la construcción de interfaces con Flet antes de integrar la API.

### Contenidos que debes dominar

- Concepto de `Page`.
- Controles básicos:
  - `Text`
  - `ElevatedButton`
  - `TextField`
  - `ListView`
  - `Column`
  - `Row`
  - `Card`
  - `Image`
  - `Tabs`
  - `AppBar`
  - `NavigationRail`
  - `Dropdown`
  - `ProgressRing`
  - `SnackBar`
  - `AlertDialog`
- Layouts:
  - `Row`
  - `Column`
  - `Stack`
  - `Container`
  - `ResponsiveRow`
- Eventos.
- Actualización de UI.
- Estado simple.
- Navegación entre vistas.
- Theming.
- Imágenes remotas.
- Controles asíncronos.

### Tareas

1. Crear una app Flet mínima:

   ```python
   import flet as ft

   def main(page: ft.Page):
       page.title = "Pokédex Flet"
       page.add(ft.Text("Hola PokeAPI"))

   ft.app(target=main)
   ```

2. Construir una maqueta estática:
   - Barra superior.
   - Menú lateral de generaciones.
   - Lista central.
   - Panel de detalle.

3. Crear componentes reutilizables:
   - `PokemonCard`.
   - `LoadingIndicator`.
   - `ErrorMessage`.
   - `StatBar`.

4. Implementar navegación simulada:
   - Click en generación cambia texto.
   - Click en Pokémon falso abre detalle falso.

### Pistas senior

- No pongas toda la UI en una sola función gigante.
- Divide componentes por archivo.
- Usa funciones que retornen controles.
- Piensa en estados visuales:
  - Cargando.
  - Vacío.
  - Error.
  - Datos disponibles.
- Usa `page.padding`, `spacing`, `alignment` y `expand` para layouts limpios.
- Si una lista puede ser larga, piensa en scroll y rendimiento desde el inicio.
- Evita reconstruir toda la página si solo cambia una sección.

### Criterios de aceptación

- La app abre sin errores.
- Existe una maqueta visual clara.
- Puedes simular selección de generación.
- Puedes simular selección de Pokémon.
- La UI no se ve como una prueba improvisada.

### Reto extra

Crea un modo oscuro/claro con un botón de toggle.

---

## Fase 4: MVP de búsqueda de Pokémon

### Objetivo

Integrar Flet con tu cliente de PokeAPI para buscar un Pokémon por nombre o ID.

### Contenidos que debes dominar

- Handlers asíncronos en UI.
- Manejo de estado de carga.
- Manejo de errores visible para usuario.
- Búsqueda por texto.
- Actualización incremental de controles.
- Separación UI/servicio.
- Uso de modelos en la vista.

### Tareas

1. Añadir un `TextField` de búsqueda.
2. Añadir botón buscar.
3. Al buscar:
   - Mostrar indicador de carga.
   - Llamar a `PokeAPIClient.get_pokemon()`.
   - Mostrar datos básicos:
     - ID.
     - Nombre.
     - Sprite.
     - Tipos.
     - Altura.
     - Peso.
     - Habilidades.
4. Si el Pokémon no existe:
   - Mostrar mensaje amigable.
5. Si hay error de red:
   - Mostrar error con opción de reintentar.

### Flujo esperado

```text
Usuario escribe "pikachu"
        ↓
Click en buscar
        ↓
UI muestra loading
        ↓
Servicio consulta PokeAPI
        ↓
Se parsea respuesta
        ↓
UI muestra tarjeta de Pokémon
```

### Pistas senior

- Deshabilita el botón mientras cargas.
- No bloquees el hilo de UI.
- Usa `async` en handlers si tu versión de Flet lo soporta correctamente.
- Si no estás seguro de cómo manejar tareas asíncronas en Flet, consulta la documentación de `page.run_task`, `async handler` o mecanismo equivalente.
- Muestra errores con `SnackBar`, `AlertDialog` o un banner.
- Guarda el último término buscado en estado.
- Normaliza el texto:

  ```python
  query = query.strip().lower()
  ```

- Si el usuario presiona Enter, también debería buscar.

### Criterios de aceptación

- Buscar `pikachu` funciona.
- Buscar `25` funciona.
- Buscar un Pokémon inexistente muestra error.
- La UI no se congela.
- Hay estado de carga visible.
- El código de UI no contiene llamadas HTTP directas.

### Reto extra

Añade autocompletado con nombres de Pokémon usando una lista cacheada.

---

## Fase 5: Lista interactiva de generaciones

### Objetivo

Construir la funcionalidad central solicitada: una lista interactiva de Pokémon por generación.

### Contenidos que debes dominar

- Endpoints de generación.
- Listas grandes.
- Paginación.
- Virtualización o lazy loading.
- Estado de selección.
- Filtros locales.
- Construcción de URLs de sprites.
- Concurrencia limitada.
- Componentes de lista reutilizables.

### Tareas

1. Obtener lista de generaciones:

   ```text
   GET /generation?limit=100
   ```

2. Mostrar generaciones en:
   - `NavigationRail`, o
   - `Dropdown`, o
   - `ListView` lateral.

3. Al seleccionar una generación:
   - Obtener detalle:

     ```text
     GET /generation/{id}
     ```

   - Mostrar especies de esa generación.

4. Para cada elemento de la lista mostrar:
   - ID si puedes obtenerlo.
   - Nombre.
   - Sprite si es posible.

5. Permitir:
   - Click en elemento para abrir detalle.
   - Filtrar por texto dentro de la generación.
   - Ordenar por ID o nombre.

### Problema importante: rendimiento

La respuesta de `/generation/{id}` puede incluir muchas especies. No debes hacer una llamada adicional por cada Pokémon si no es necesario.

### Estrategia recomendada

1. Usar `/generation/{id}` para obtener la lista de especies.
2. Extraer el ID desde la URL de cada especie.
3. Construir sprites directamente:

   ```text
   https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/{id}.png
   ```

4. Cargar sprites solo cuando sean visibles.
5. No pedir `/pokemon/{id}` hasta que el usuario abra el detalle.

### Pistas senior

- La URL de una especie puede ser:

  ```text
  https://pokeapi.co/api/v2/pokemon-species/1/
  ```

  Puedes extraer `1` con una función utilitaria.

- No hagas 151 llamadas al mismo tiempo.
- Si necesitas nombres localizados o más datos, usa `asyncio.Semaphore(5)` o similar.
- Crea un estado por generación:

  ```python
  selected_generation_id: int | None
  generation_pokemon_list: list[PokemonSummary]
  filtered_generation_pokemon_list: list[PokemonSummary]
  ```

- El filtro debe ser local y rápido si ya cargaste la lista.
- Si la lista es muy grande, divide la carga:
  - Mostrar primeras 50 especies.
  - Cargar más al hacer scroll.
  - O usar paginación con botones.
- Usa placeholders mientras cargan imágenes.
- Guarda en caché la lista de especies por generación.

### Criterios de aceptación

- Puedo elegir una generación.
- La lista de Pokémon de esa generación se muestra.
- La selección de generación se mantiene visualmente clara.
- El click en un Pokémon abre su detalle.
- Hay filtro de búsqueda dentro de la generación.
- No se bloquea la UI.
- La app no hace llamadas innecesarias.

### Reto extra

Añade botones:

```text
[Anterior] [Siguiente]
```

o scroll infinito para cargar más elementos.

---

## Fase 6: Vista de detalle completa

### Objetivo

Mostrar todo tipo de información útil de un Pokémon en una vista detallada y organizada por pestañas.

### Contenidos que debes dominar

- `Tabs` en Flet.
- Composición de componentes.
- Datos anidados.
- Transformación de datos.
- Visualización de stats.
- Imágenes múltiples.
- Estados vacíos.
- Concurrencia con `asyncio.gather`.
- Manejo de datos faltantes.

### Tareas

Crear una vista de detalle con pestañas:

1. Pestaña `Info`:
   - ID.
   - Nombre.
   - Nombre en español si existe.
   - Sprite normal.
   - Sprite shiny.
   - Tipos.
   - Altura.
   - Peso.
   - Experiencia base.
   - Habilidades.
   - Descripción breve.

2. Pestaña `Stats`:
   - HP.
   - Attack.
   - Defense.
   - Special Attack.
   - Special Defense.
   - Speed.
   - Total.
   - Barras visuales.

3. Pestaña `Evoluciones`:
   - Cadena evolutiva.
   - Condiciones.
   - Nivel.
   - Objeto.
   - Felicidad.
   - Intercambio.
   - Pokémon clicables.

4. Pestaña `Movimientos`:
   - Movimientos por nivel.
   - Movimientos por MT/MO.
   - Tipo.
   - Poder.
   - Precisión.
   - Categoría.
   - Filtro por versión o grupo.

5. Pestaña `Especie`:
   - Hábitat.
   - Color.
   - Forma.
   - Género.
   - Ratio de captura.
   - Felicidad base.
   - Experiencia base.
   - Ritmo de crecimiento.
   - Grupo huevo.
   - Generación.

6. Pestaña `Media` o `Extras`:
   - Sprite frontal.
   - Sprite trasero.
   - Sprite shiny.
   - Artwork oficial.
   - Icono.
   - Grito/sonido si decides implementarlo.

### Datos a combinar

Para un detalle completo, probablemente necesitarás:

```text
GET /pokemon/{id}
GET /pokemon-species/{id}
GET /evolution-chain/{evolution_chain_id}
```

### Pistas senior

- Puedes lanzar varias llamadas concurrentes:

  ```python
  pokemon, species = await asyncio.gather(
      client.get_pokemon(identifier),
      client.get_pokemon_species(identifier),
  )
  ```

- La cadena evolutiva suele venir en `species.evolution_chain.url`.
- No muestres JSON crudo al usuario.
- Convierte stats en una estructura amigable:

  ```python
  class StatView(BaseModel):
      name: str
      value: int
      max_value: int
  ```

- Usa colores distintos para stats:
  - HP verde.
  - Attack rojo.
  - Defense azul.
  - Speed amarillo.
- Si un dato no existe, muestra:

  ```text
  No disponible
  ```

- Los nombres localizados pueden venir en arrays. Busca `language.name == "es"`.
- Si no hay español, usa inglés como fallback.

### Criterios de aceptación

- La vista detalle muestra información real.
- Las pestañas funcionan.
- Las estadísticas se visualizan con barras.
- La cadena evolutiva es comprensible.
- Si un dato falta, la app no explota.
- El detalle carga sin congelar la UI.

### Reto extra

Añade un selector para ver:

```text
Normal | Shiny | Artwork
```

---

## Fase 7: Evoluciones y relaciones avanzadas

### Objetivo

Dominar datos recursivos y relaciones entre Pokémon, especies, evoluciones y objetos.

### Contenidos que debes dominar

- Estructuras arbóreas.
- Recursividad.
- Grafos simples.
- Normalización de datos.
- Navegación entre recursos.
- Modelado de condiciones evolutivas.
- Componentes UI recursivos.

### Tareas

1. Parsear la cadena evolutiva:

   ```text
   chain
     evolves_to
       evolves_to
   ```

2. Convertirla en una estructura plana o árbol amigable.
3. Mostrar cada nodo con:
   - Sprite.
   - Nombre.
   - ID.
   - Condiciones de evolución.

4. Hacer que cada Pokémon de la cadena sea clicable.
5. Mostrar condiciones:
   - Nivel mínimo.
   - Objeto.
   - Intercambio.
   - Felicidad.
   - Hora del día.
   - Género.
   - Movimiento aprendido.
   - Ubicación especial.

### Ejemplo conceptual

```text
Pichu
  ↓ felicidad
Pikachu
  ↓ piedra trueno
Raichu
```

### Pistas senior

- La API de evolución puede ser profunda y confusa.
- Crea un modelo propio:

  ```python
  class EvolutionNode(BaseModel):
      pokemon_name: str
      pokemon_id: int | None
      sprite_url: str | None
      min_level: int | None
      item: str | None
      trigger: str | None
      happiness: bool
      trade: bool
      children: list["EvolutionNode"]
  ```

- Cuidado con referencias circulares.
- Si un Pokémon no tiene evolución, muestra:

  ```text
  Este Pokémon no tiene cadena evolutiva registrada.
  ```

- Algunas cadenas tienen ramas múltiples. Ejemplo:

  ```text
        ↓ Vaporeon
  Eevee → Jolteon
        → Flareon
        → Espeon
        → Umbreon
        → ...
  ```

- No asumas que todas las cadenas son lineales.

### Criterios de aceptación

- La cadena evolutiva se muestra correctamente.
- Las condiciones son legibles.
- Se puede navegar entre Pokémon relacionados.
- Las cadenas ramificadas no rompen la UI.
- El componente de evolución es reutilizable.

### Reto extra

Añade tooltip con condiciones completas al pasar el mouse sobre una flecha evolutiva.

---

## Fase 8: Rendimiento, caché y experiencia de usuario

### Objetivo

Convertir una app funcional en una app fluida, profesional y agradable.

### Contenidos que debes dominar

- Caché en memoria.
- Caché en disco.
- Concurrencia limitada.
- Debounce.
- Lazy loading.
- Estados de carga.
- Placeholders.
- Manejo de imágenes remotas.
- Reducción de llamadas HTTP.
- Actualización parcial de UI.

### Tareas

1. Cachear:
   - Generaciones.
   - Listas por generación.
   - Detalles de Pokémon ya visitados.
   - Especies.
   - Cadenas evolutivas.

2. Implementar caché HTTP simple:

   ```python
   cache_key = f"pokemon:{identifier}"
   ```

3. Guardar respuestas JSON en disco:

   ```text
   .cache/api/pokemon/25.json
   ```

4. Añadir placeholders de imágenes.
5. Evitar recargar imágenes ya vistas.
6. Añadir debounce al buscador:

   ```text
   Usuario escribe "p"
   Espera 300 ms
   Si sigue escribiendo, cancela búsqueda anterior
   ```

7. Añadir indicador de progreso para listas grandes.
8. Añadir botón de recargar si falla red.

### Pistas senior

- No pidas el mismo Pokémon dos veces seguidas.
- Si el usuario vuelve atrás, restaura la lista desde caché.
- Usa TTL si quieres expirar caché:

  ```python
  expires_at = time.time() + 60 * 60 * 24
  ```

- Usa `asyncio.Semaphore` para limitar peticiones concurrentes.
- Si descargas sprites, guarda una versión local o usa caché del sistema.
- No hagas búsquedas remotas por cada tecla si no tienes un endpoint eficiente.
- Para listas grandes, filtra localmente si ya tienes los datos.
- Si la app va a funcionar offline, guarda recursos esenciales.

### Criterios de aceptación

- La segunda vez que abres un Pokémon carga casi instantáneo.
- La lista de generación no se recarga innecesariamente.
- El buscador no dispara demasiadas llamadas.
- Las imágenes no parpadean excesivamente.
- La app responde bien con red lenta.
- Hay estados visuales claros.

### Reto extra

Añade un modo offline que muestre solo Pokémon ya visitados.

---

## Fase 9: Testing, calidad y robustez

### Objetivo

Que la aplicación sea confiable, mantenible y verificable.

### Contenidos que debes dominar

- Unit testing.
- Testing asíncrono.
- Mocking.
- Fixtures.
- Cobertura.
- Integración continua.
- Linting.
- Type checking.
- Logging estructurado.
- Manejo de errores.
- Pruebas manuales.

### Tareas

1. Descargar fixtures reales de PokeAPI:

   ```text
   tests/fixtures/pokemon_25.json
   tests/fixtures/species_25.json
   tests/fixtures/evolution_chain_10.json
   tests/fixtures/generation_1.json
   ```

2. Crear tests para parsers:

   ```python
   def test_parse_pikachu():
       data = load_fixture("pokemon_25.json")
       pokemon = PokemonDetail.model_validate(data)
       assert pokemon.id == 25
       assert pokemon.name == "pikachu"
   ```

3. Testear cliente HTTP con `respx` o similar.
4. Testear servicios:
   - Búsqueda.
   - Generación.
   - Evolución.
5. Añadir tests de errores:
   - 404.
   - Timeout.
   - JSON inválido.
6. Configurar:

   ```bash
   ruff check .
   mypy app
   pytest
   ```

7. Crear GitHub Actions:

   ```yaml
   name: CI
   on: [push, pull_request]
   jobs:
     test:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v4
         - uses: actions/setup-python@v5
         - run: pip install -r requirements.txt
         - run: pytest
   ```

### Pistas senior

- No testees PokeAPI directamente en CI si puedes evitarlo.
- Usa fixtures para pruebas deterministas.
- Testea la lógica de parseo, que suele ser donde más errores hay.
- Si un campo puede venir `null`, escribe un test para eso.
- No pruebes solo el camino feliz.
- Crea un cliente falso:

  ```python
  class FakePokeAPIClient:
      async def get_pokemon(self, identifier):
          return sample_pikachu
  ```

- Esto facilita testear servicios y lógica de UI sin red.

### Criterios de aceptación

- Hay tests unitarios pasando.
- Los parsers están cubiertos.
- Los errores comunes están contemplados.
- El linting no falla.
- El type checker no falla o tiene errores controlados.
- Existe un pipeline CI básico.

### Reto extra

Añade cobertura con `pytest-cov` y pon un umbral mínimo, por ejemplo 70% en `app/services` y `app/models`.

---

## Fase 10: Empaquetado y distribución

### Objetivo

Convertir tu proyecto en una aplicación distribuible para usuarios finales.

### Contenidos que debes dominar

- Build de aplicaciones Flet.
- Assets.
- Iconos.
- Metadatos.
- Versionado.
- Dependencias de producción.
- Scripts de build.
- GitHub Releases.
- Artefactos.
- Pruebas en entorno limpio.

### Tareas

1. Añadir icono y nombre de aplicación.
2. Configurar versión:

   ```python
   __version__ = "0.1.0"
   ```

3. Crear build local:

   ```bash
   flet build
   ```

   Consulta la documentación actual de Flet para el comando exacto según plataforma:

   ```bash
   flet build windows
   flet build macos
   flet build linux
   flet build web
   ```

4. Probar el ejecutable generado.
5. Crear release en GitHub.
6. Documentar instalación para usuarios.
7. Añadir capturas de pantalla.
8. Crear changelog.

### Pistas senior

- Un build puede fallar por dependencias no fijadas.
- Prueba la app en una máquina limpia o contenedor si puedes.
- No asumas que porque funciona en desarrollo funcionará en producción.
- Revisa rutas de assets.
- Usa rutas relativas correctas.
- Si la app usa caché, define una carpeta adecuada por sistema operativo.
- Windows, macOS y Linux tienen rutas distintas para datos de aplicación.
- No guardes caché dentro de la carpeta del ejecutable si el sistema no lo permite.

### Criterios de aceptación

- Existe un ejecutable o build funcional.
- La app abre sin necesidad de tener el código fuente visible.
- Las imágenes y recursos cargan correctamente.
- El README explica cómo instalar.
- Hay una release versionada.

### Reto extra

Crea builds automáticos con GitHub Actions para al menos una plataforma.

---

# 🧩 Fases opcionales para convertir la app en un proyecto notable

---

## Fase 11: Favoritos y persistencia local

### Objetivo

Guardar datos del usuario localmente.

### Funcionalidades

- Marcar Pokémon favorito.
- Lista de favoritos.
- Persistencia en SQLite o JSON.
- Últimos Pokémon vistos.
- Historial de búsqueda.

### Contenidos

- SQLite.
- Serialización.
- Migraciones simples.
- Repositorio de datos locales.

---

## Fase 12: Comparador de Pokémon

### Objetivo

Permitir comparar dos o más Pokémon.

### Funcionalidades

- Seleccionar Pokémon A y B.
- Comparar stats con barras.
- Comparar tipos.
- Comparar habilidades.
- Comparar cadenas evolutivas.

### Contenidos

- Layouts comparativos.
- Selección múltiple.
- Estado compartido.
- Visualización de datos.

---

## Fase 13: Tabla de tipos

### Objetivo

Mostrar debilidades y resistencias.

### Funcionalidades

- Elegir uno o dos tipos.
- Calcular:
  - Debilidades.
  - Resistencias.
  - Inmunidades.
  - Daño normal.
- Mostrar tabla visual.

### Endpoints útiles

```text
/type/{type}
```

### Contenidos

- Lógica de multiplicadores.
- Combinación de tipos.
- Normalización de nombres.
- UI de matriz.

---

## Fase 14: Internacionalización

### Objetivo

Soportar varios idiomas.

### Funcionalidades

- Español e inglés.
- Selector de idioma.
- Nombres de Pokémon localizados.
- Descripciones localizadas.
- Textos de UI traducidos.

### Contenidos

- Archivos de traducción.
- Fallbacks.
- PokeAPI `names` y `flavor_text_entries`.
- Gestión de idiomas faltantes.

---

## Fase 15: Tema visual profesional

### Objetivo

Que la app se sienta pulida.

### Funcionalidades

- Modo oscuro.
- Colores por tipo de Pokémon.
- Tipografía consistente.
- Animaciones sutiles.
- Skeleton loaders.
- Iconos consistentes.

### Ejemplo de colores por tipo

| Tipo | Color sugerido |
|---|---|
| fire | Naranja/rojo |
| water | Azul |
| grass | Verde |
| electric | Amarillo |
| psychic | Rosa |
| ghost | Morado |
| steel | Gris |
| dragon | Índigo |
| fairy | Rosa suave |
| normal | Gris claro |

---

# 📚 Plan de estudio sugerido

## Plan de 8 semanas a tiempo parcial

### Semana 1: Fundamentos

- Python.
- Entorno.
- Git.
- Pydantic.
- Asyncio básico.

### Semana 2: Cliente PokeAPI

- httpx.
- Endpoints.
- Modelos.
- Errores.
- Tests básicos.

### Semana 3: Flet básico

- Controles.
- Layout.
- Eventos.
- Maqueta estática.

### Semana 4: MVP

- Buscador.
- Detalle básico.
- Estados de carga.
- Errores.

### Semana 5: Generaciones

- Menú de generaciones.
- Lista por generación.
- Filtro local.
- Sprites.

### Semana 6: Detalle completo

- Tabs.
- Stats.
- Especie.
- Movimientos.

### Semana 7: Evoluciones y rendimiento

- Cadena evolutiva.
- Caché.
- Lazy loading.
- Optimización.

### Semana 8: Calidad y release

- Testing.
- Linting.
- CI.
- Build.
- Documentación.

---

# ✅ Definition of Done del proyecto

Considera que el proyecto está terminado cuando:

- [ ] La app abre correctamente.
- [ ] Se pueden listar generaciones dinámicamente.
- [ ] Se puede seleccionar una generación.
- [ ] Se muestra una lista interactiva de Pokémon.
- [ ] Se puede filtrar la lista.
- [ ] Se puede abrir el detalle de un Pokémon.
- [ ] El detalle muestra información completa.
- [ ] Las estadísticas se visualizan correctamente.
- [ ] La cadena evolutiva funciona.
- [ ] Hay manejo de errores.
- [ ] Hay estados de carga.
- [ ] Hay caché básica.
- [ ] La app no bloquea la UI.
- [ ] Hay tests unitarios.
- [ ] Hay linting configurado.
- [ ] Hay README completo.
- [ ] Hay capturas de pantalla.
- [ ] Existe build ejecutable o instrucciones claras de instalación.
- [ ] El código está separado en módulos.
- [ ] No hay credenciales, tokens o datos sensibles en el repositorio.
- [ ] El proyecto puede ser explicado por ti mismo en una entrevista técnica.

---

# 🧪 Rúbrica de evaluación

Puedes evaluarte del 1 al 5 en cada punto.

## Nivel 1: Inicial

- La app abre.
- Hay un botón de búsqueda.
- Puedes buscar un Pokémon simple.

## Nivel 2: Funcional

- Hay generaciones.
- Hay lista por generación.
- Hay detalle básico.
- Hay manejo mínimo de errores.

## Nivel 3: Sólido

- La UI es clara.
- Hay caché.
- Hay estados de carga.
- Hay testing básico.
- El código está separado en capas.

## Nivel 4: Profesional

- La app es fluida.
- Hay testing robusto.
- Hay CI.
- Hay build.
- Hay documentación.
- Hay buena UX.

## Nivel 5: Destacado

- Favoritos.
- Comparador.
- Modo offline.
- Internacionalización.
- Tabla de tipos.
- Diseño pulido.
- Releases automatizados.
- Arquitectura limpia y explicable.

---

# ⚠️ Errores comunes que debes evitar

## 1. Hacer llamadas HTTP síncronas en la UI

Si usas una librería bloqueante dentro de un botón, la interfaz puede congelarse.

Solución:

- Usa `httpx.AsyncClient` o similar.
- Usa tareas asíncronas.
- Mantén la UI responsiva.

---

## 2. Querer descargar todos los Pokémon al inicio

No hagas esto como primera estrategia.

Mejor:

- Carga generaciones.
- Carga listas por generación cuando se seleccionen.
- Carga detalle cuando el usuario haga click.

---

## 3. Mostrar JSON crudo

La API devuelve datos complejos. Tu trabajo es transformarlos.

Ejemplo malo:

```text
{"name": "pikachu", "stats": [{"base_stat": 35, ...}]}
```

Ejemplo bueno:

```text
HP: 35
Attack: 55
Defense: 40
```

---

## 4. No manejar errores de red

La red falla. PokeAPI puede tardar. El usuario puede estar offline.

Debes manejar:

- Timeout.
- 404.
- 500.
- JSON inválido.
- Imagen no disponible.
- Campo faltante.

---

## 5. Acoplar UI y API

No hagas esto:

```text
Botón -> httpx -> parseo -> UI
```

Haz esto:

```text
Botón -> Servicio -> Cliente API -> Modelo -> UI
```

---

## 6. No cachear

Si el usuario abre Pikachu cinco veces, no deberías hacer cinco veces la misma petición.

---

## 7. Reconstruir toda la UI constantemente

Si solo cambió el panel de detalle, no reconstruyas toda la aplicación.

---

## 8. No pensar en listas largas

Una generación puede tener muchos Pokémon. Debes pensar en:

- Scroll.
- Lazy loading.
- Item height fijo.
- Paginación.
- Rendimiento de imágenes.

---

# 🧠 Preguntas de autoevaluación por fase

## Fase 0

- ¿Puedo explicar qué hace un entorno virtual?
- ¿Puedo recrear el entorno desde cero?
- ¿Mi repositorio está limpio?

## Fase 1

- ¿Puedo explicar la diferencia entre `dict` y modelo Pydantic?
- ¿Por qué conviene validar datos externos?
- ¿Qué significa `await`?

## Fase 2

- ¿Qué pasa si PokeAPI devuelve 404?
- ¿Cómo evito bloquear la app?
- ¿Qué es un timeout?
- ¿Por qué conviene parsear datos antes de usarlos?

## Fase 3

- ¿Puedo describir la jerarquía de controles?
- ¿Cómo actualizo un control sin recargar todo?
- ¿Qué componente debería usar para una lista larga?

## Fase 4

- ¿Dónde está la lógica de negocio?
- ¿La UI sabe demasiado de HTTP?
- ¿Qué pasa si el usuario busca un Pokémon vacío?

## Fase 5

- ¿Cómo evito hacer demasiadas llamadas?
- ¿Cómo filtro localmente?
- ¿Cómo construyo sprites sin pedir cada Pokémon?

## Fase 6

- ¿Cómo organizo información compleja?
- ¿Qué hago si falta un campo?
- ¿Cómo combino múltiples respuestas?

## Fase 7

- ¿Puedo modelar un árbol evolutivo?
- ¿Qué hago con evoluciones ramificadas?
- ¿Cómo hago clicable cada Pokémon?

## Fase 8

- ¿Dónde guardo caché?
- ¿Cuándo expira?
- ¿Cómo mejoro percepción de velocidad?

## Fase 9

- ¿Mis tests prueban comportamiento o implementación?
- ¿Puedo simular errores de red?
- ¿Qué partes son más frágiles?

## Fase 10

- ¿Un usuario puede ejecutar la app sin leer código?
- ¿El build incluye assets?
- ¿La versión es clara?

---

# 🛠️ Checklist técnico rápido

## Python

- [ ] Python 3.11+.
- [ ] Entorno virtual.
- [ ] Dependencias fijadas.
- [ ] Type hints.
- [ ] Logging.
- [ ] Configuración en módulo aparte.

## API

- [ ] Cliente asíncrono.
- [ ] Timeouts.
- [ ] Errores propios.
- [ ] Parseo con Pydantic.
- [ ] Caché.
- [ ] Tests con fixtures.

## UI

- [ ] Layout principal.
- [ ] Buscador.
- [ ] Generaciones.
- [ ] Lista interactiva.
- [ ] Detalle.
- [ ] Tabs.
- [ ] Loading.
- [ ] Error.
- [ ] Empty state.

## Datos

- [ ] Modelo `PokemonSummary`.
- [ ] Modelo `PokemonDetail`.
- [ ] Modelo `PokemonSpecies`.
- [ ] Modelo `GenerationSummary`.
- [ ] Modelo `GenerationDetail`.
- [ ] Modelo `EvolutionChain`.

## Calidad

- [ ] pytest.
- [ ] ruff.
- [ ] mypy.
- [ ] CI.
- [ ] README.
- [ ] Capturas.

## Release

- [ ] Versión.
- [ ] Changelog.
- [ ] Build.
- [ ] Instalación documentada.
- [ ] Ejecutable probado.

---

# 🧱 Modelo de datos sugerido

No tienes que implementarlo exactamente así, pero puede servirte como guía.

## Modelo mínimo para lista

```python
class PokemonSummary(BaseModel):
    id: int | None
    name: str
    sprite_url: str | None = None
    generation_id: int | None = None
```

## Modelo para detalle

```python
class PokemonType(BaseModel):
    name: str
    slot: int

class PokemonStat(BaseModel):
    name: str
    value: int

class PokemonAbility(BaseModel):
    name: str
    is_hidden: bool
    slot: int

class PokemonDetail(BaseModel):
    id: int
    name: str
    display_name: str | None = None
    height: int | None = None
    weight: int | None = None
    base_experience: int | None = None
    sprites: dict[str, str | None] = {}
    types: list[PokemonType] = []
    stats: list[PokemonStat] = []
    abilities: list[PokemonAbility] = []
```

## Modelo para especie

```python
class PokemonSpecies(BaseModel):
    id: int
    name: str
    spanish_name: str | None = None
    description: str | None = None
    habitat: str | None = None
    color: str | None = None
    shape: str | None = None
    capture_rate: int | None = None
    base_happiness: int | None = None
    generation: str | None = None
    evolution_chain_url: str | None = None
```

## Modelo para evolución

```python
class EvolutionNode(BaseModel):
    pokemon_name: str
    pokemon_id: int | None = None
    sprite_url: str | None = None
    min_level: int | None = None
    item: str | None = None
    trigger: str | None = None
    children: list["EvolutionNode"] = []
```

---

# 🧭 Flujo de trabajo recomendado

## Para cada funcionalidad nueva

1. Entiende el requisito.
2. Identifica endpoints necesarios.
3. Prueba endpoints manualmente.
4. Guarda una respuesta JSON de ejemplo.
5. Crea modelo Pydantic.
6. Crea parser.
7. Escribe tests del parser.
8. Integra en servicio.
9. Conecta con UI.
10. Añade estados de carga/error.
11. Pulir UX.
12. Documenta.
13. Commit pequeño.

---

# 📝 Convención de commits sugerida

Usa mensajes claros:

```text
feat: add generation list view
feat: add pokemon search service
fix: handle 404 when pokemon not found
perf: cache pokemon detail responses
test: add evolution chain parser tests
docs: add installation instructions
chore: update dependencies
```

---

# 🧪 Escenarios de prueba manual

Debes probar al menos estos casos:

## Búsqueda

- Buscar `pikachu`.
- Buscar `25`.
- Buscar `PIKACHU` con mayúsculas.
- Buscar con espacios.
- Buscar un Pokémon inexistente.
- Buscar con texto vacío.

## Generaciones

- Abrir generación 1.
- Abrir generación 2.
- Cambiar rápidamente entre generaciones.
- Filtrar dentro de una generación.
- Seleccionar un Pokémon después de filtrar.

## Detalle

- Abrir Pokémon con evolución.
- Abrir Pokémon sin evolución.
- Abrir Pokémon con múltiples formas.
- Abrir Pokémon shiny.
- Abrir Pokémon con datos faltantes.

## Red

- Probar sin internet.
- Probar con red lenta simulada.
- Cancelar búsqueda mientras carga.
- Reintentar después de error.

## Rendimiento

- Abrir 20 Pokémon seguidos.
- Volver atrás y abrir uno ya visto.
- Hacer scroll rápido en lista grande.
- Cambiar de pestaña en detalle.

---

# 🧠 Mentalidad senior durante el proyecto

No te limites a “hacer que funcione”. Pregúntate siempre:

- ¿Esto es mantenible?
- ¿Esto es testeable?
- ¿Esto escala si la lista crece?
- ¿Esto falla elegantemente?
- ¿El usuario entiende lo que está pasando?
- ¿Estoy haciendo llamadas innecesarias?
- ¿Estoy transformando datos o solo mostrando JSON?
- ¿Podría otra persona entender mi código?
- ¿Qué pasaría si PokeAPI cambia?
- ¿Qué pasaría si la red falla?
- ¿Qué pasaría si el usuario hace click muchas veces?
- ¿Qué pasaría si un campo viene vacío?
- ¿Este componente se puede reutilizar?
- ¿Esta función hace una sola cosa?
- ¿Este módulo tiene una responsabilidad clara?

---

# 🏁 Resultado final esperado

Al terminar este roadmap, no solo tendrás una Pokédex funcional. Habrás practicado:

- Python moderno.
- Programación asíncrona.
- Consumo de APIs externas.
- Modelado de datos.
- Arquitectura limpia.
- UI con Flet.
- Manejo de estados.
- UX.
- Caché.
- Rendimiento.
- Testing.
- CI.
- Empaquetado.
- Documentación.
- Release de software.

Ese es el verdadero objetivo del proyecto.

---

# 📌 Nota final del tutor

Este roadmap está diseñado para que lo recorras de forma incremental. No intentes construir toda la aplicación el primer día.

Construye primero:

```text
Cliente API -> Modelos -> UI básica -> Lista por generación -> Detalle -> Evoluciones -> Optimización -> Testing -> Release
```

Cada fase debe dejar una evidencia concreta:

- Código funcionando.
- Tests.
- Commits.
- Documentación.
- Capturas.
- Decisiones técnicas explicables.

Si completas todas las fases y puedes defender cada decisión, no solo habrás hecho una app bonita: habrás construido un proyecto de nivel profesional.