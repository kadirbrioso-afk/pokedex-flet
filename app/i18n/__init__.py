"""Internacionalización (i18n): traducciones ES/EN con fallbacks.

Proporciona un traductor simple con catálogos por idioma. Cada clave llega a
un texto en ``es`` y ``en``; ``t()`` devuelve el texto del idioma activo y, si
la clave o el idioma faltan, aplica un fallback (primero ``es`` y luego la
propia clave).
"""

from __future__ import annotations

LANGUAGES: tuple[str, ...] = ("es", "en")
DEFAULT_LANGUAGE = "es"

_CATALOG: dict[str, dict[str, str]] = {
    # AppBar
    "appbar.typechart": {"es": "Tabla de tipos", "en": "Type chart"},
    "appbar.compare": {"es": "Comparar Pokémon", "en": "Compare Pokémon"},
    "appbar.favorites": {"es": "Ver favoritos", "en": "View favorites"},
    "appbar.offline": {
        "es": "Modo offline (visitados)",
        "en": "Offline mode (visited)",
    },
    "appbar.theme": {"es": "Cambiar tema", "en": "Toggle theme"},
    "appbar.language": {"es": "Cambiar idioma", "en": "Change language"},
    # Home view
    "home.pokedex": {"es": "Pokédex", "en": "Pokédex"},
    "home.filter_hint": {
        "es": "Filtrar en esta generación…",
        "en": "Filter this generation…",
    },
    "home.sort_label": {"es": "Orden", "en": "Sort"},
    "home.sort.id": {"es": "Por ID", "en": "By ID"},
    "home.sort.name": {"es": "Por nombre", "en": "By name"},
    "home.results.zero": {"es": "0 resultados", "en": "0 results"},
    "home.pagination": {
        "es": "{start}–{end} de {total}",
        "en": "{start}–{end} of {total}",
    },
    "home.prev": {"es": "Anterior", "en": "Previous"},
    "home.next": {"es": "Siguiente", "en": "Next"},
    "home.search_hint": {
        "es": "Nombre o ID (ej. pikachu, 25)",
        "en": "Name or ID (e.g. pikachu, 25)",
    },
    "home.search": {"es": "Buscar", "en": "Search"},
    "home.loading": {"es": "Cargando…", "en": "Loading…"},
    "home.loading_generations": {
        "es": "Cargando generaciones…",
        "en": "Loading generations…",
    },
    "home.loading_generation": {
        "es": "Cargando generación {id}…",
        "en": "Loading generation {id}…",
    },
    "home.loading_detail": {"es": "Cargando detalle…", "en": "Loading detail…"},
    "home.searching": {"es": "Buscando…", "en": "Searching…"},
    "home.error_generations": {
        "es": "Error al cargar las generaciones: {error}",
        "en": "Error loading generations: {error}",
    },
    "home.error_generation": {
        "es": "Error al cargar la generación {id}: {error}",
        "en": "Error loading generation {id}: {error}",
    },
    "home.error_detail": {
        "es": "Error al cargar el detalle: {error}",
        "en": "Error loading detail: {error}",
    },
    "home.error_search": {
        "es": "Error al buscar: {error}",
        "en": "Error searching: {error}",
    },
    "home.not_found": {
        "es": "Pokémon «{name}» no encontrado.",
        "en": "Pokémon “{name}” not found.",
    },
    "home.no_results_filter": {
        "es": "Sin resultados para el filtro.",
        "en": "No results for the filter.",
    },
    "home.empty_query": {
        "es": "Escribe un nombre o ID para buscar.",
        "en": "Type a name or ID to search.",
    },
    "home.no_pokemon_named": {
        "es": "No hay ningún Pokémon llamado «{query}».",
        "en": "There is no Pokémon named “{query}”.",
    },
    "home.offline_header": {
        "es": "Modo offline — visitados",
        "en": "Offline mode — visited",
    },
    "home.favorites_header": {
        "es": "Favoritos ({count})",
        "en": "Favorites ({count})",
    },
    "home.generation_header": {
        "es": "Generación {id} — {region}",
        "en": "Generation {id} — {region}",
    },
    "home.pick_header": {
        "es": "Selecciona Pokémon {side} en la lista",
        "en": "Pick Pokémon {side} from the list",
    },
    # Detail view - tabs
    "detail.tab.info": {"es": "Info", "en": "Info"},
    "detail.tab.stats": {"es": "Stats", "en": "Stats"},
    "detail.tab.evolution": {"es": "Evolución", "en": "Evolution"},
    "detail.tab.moves": {"es": "Movs", "en": "Moves"},
    "detail.tab.species": {"es": "Especie", "en": "Species"},
    "detail.tab.media": {"es": "Media", "en": "Media"},
    # Detail view - common
    "detail.select_pokemon": {
        "es": "Selecciona un Pokémon para ver su detalle",
        "en": "Select a Pokémon to see its detail",
    },
    "detail.no_types": {"es": "Sin tipos", "en": "No types"},
    "detail.not_available": {"es": "No disponible", "en": "Not available"},
    "detail.no_description": {
        "es": "Sin descripción disponible",
        "en": "No description available",
    },
    "detail.base_experience": {
        "es": "Experiencia base",
        "en": "Base experience",
    },
    "detail.height": {"es": "Altura", "en": "Height"},
    "detail.weight": {"es": "Peso", "en": "Weight"},
    "detail.abilities": {"es": "Habilidades", "en": "Abilities"},
    "detail.hidden_suffix": {"es": " (oculta)", "en": " (hidden)"},
    "detail.total": {"es": "Total: {total}", "en": "Total: {total}"},
    "detail.view_label": {"es": "Vista", "en": "View"},
    "detail.view.normal": {"es": "Normal", "en": "Normal"},
    "detail.view.shiny": {"es": "Shiny", "en": "Shiny"},
    "detail.view.artwork": {"es": "Artwork", "en": "Artwork"},
    "detail.favorite.add": {
        "es": "Añadir a favoritos",
        "en": "Add to favorites",
    },
    "detail.favorite.remove": {
        "es": "Quitar de favoritos",
        "en": "Remove from favorites",
    },
    "detail.species_unavailable": {
        "es": "Datos de especie no disponibles.",
        "en": "No species data available.",
    },
    "detail.evolution_none": {
        "es": "Este Pokémon no tiene cadena evolutiva registrada.",
        "en": "This Pokémon has no registered evolution chain.",
    },
    "detail.no_media": {
        "es": "Sin imágenes disponibles.",
        "en": "No images available.",
    },
    # Detail view - species
    "detail.habitat": {"es": "Hábitat", "en": "Habitat"},
    "detail.color": {"es": "Color", "en": "Color"},
    "detail.shape": {"es": "Forma", "en": "Shape"},
    "detail.gender": {"es": "Género", "en": "Gender"},
    "detail.capture_rate": {
        "es": "Ratio de captura",
        "en": "Capture rate",
    },
    "detail.base_happiness": {
        "es": "Felicidad base",
        "en": "Base happiness",
    },
    "detail.growth_rate": {"es": "Crecimiento", "en": "Growth"},
    "detail.egg_groups": {"es": "Grupo huevo", "en": "Egg groups"},
    "detail.generation": {"es": "Generación", "en": "Generation"},
    "detail.no_gender": {"es": "Sin género", "en": "Genderless"},
    # Detail view - evolution
    "detail.cond.trade": {"es": "Intercambiar", "en": "Trade"},
    "detail.cond.holding": {"es": "sosteniendo", "en": "holding"},
    "detail.cond.friendship": {"es": "Amistad", "en": "Friendship"},
    "detail.cond.use": {"es": "Usar", "en": "Use"},
    "detail.cond.known_move": {"es": "Conociendo", "en": "Learning"},
    "detail.cond.at": {"es": "En", "en": "At"},
    "detail.cond.level": {"es": "Nivel", "en": "Level"},
    "detail.cond.level_up": {"es": "Subir de nivel", "en": "Level up"},
    "detail.cond.use_item": {"es": "Usar objeto", "en": "Use item"},
    "detail.cond.shed": {"es": "Desechar la piel", "en": "Shed skin"},
    "detail.cond.rain": {"es": "Bajo la lluvia", "en": "In the rain"},
    "detail.cond.evolves": {"es": "Evoluciona", "en": "Evolves"},
    "detail.time.day": {"es": "de día", "en": "during the day"},
    "detail.time.night": {"es": "de noche", "en": "at night"},
    "detail.time.dusk": {"es": "al atardecer", "en": "at dusk"},
    "detail.time.dawn": {"es": "al amanecer", "en": "at dawn"},
    "detail.gender.only_male": {"es": "solo macho", "en": "male only"},
    "detail.gender.only_female": {"es": "solo hembra", "en": "female only"},
    "detail.gender.specific": {
        "es": "con género específico",
        "en": "with specific gender",
    },
    "detail.relative.atk_gt_def": {
        "es": "con Ataque > Defensa",
        "en": "with Attack > Defense",
    },
    "detail.relative.atk_lt_def": {
        "es": "con Ataque < Defensa",
        "en": "with Attack < Defense",
    },
    "detail.relative.atk_eq_def": {
        "es": "con Ataque = Defensa",
        "en": "with Attack = Defense",
    },
    # Detail view - moves
    "detail.method.level": {"es": "Por nivel", "en": "By level"},
    "detail.method.machine": {
        "es": "Máquinas (MT/MO)",
        "en": "Machines (TM/HM)",
    },
    "detail.method.egg": {"es": "Huevo", "en": "Egg"},
    "detail.method.tutor": {"es": "Tutor", "en": "Tutor"},
    "detail.no_moves": {
        "es": "No hay movimientos registrados.",
        "en": "No moves registered.",
    },
    # Detail view - media
    "detail.media.normal": {"es": "Normal", "en": "Normal"},
    "detail.media.shiny": {"es": "Shiny", "en": "Shiny"},
    "detail.media.back": {"es": "Trasera", "en": "Back"},
    "detail.media.back_shiny": {"es": "Trasera shiny", "en": "Shiny back"},
    "detail.media.official": {"es": "Oficial", "en": "Official"},
    "detail.media.home": {"es": "Home", "en": "Home"},
    # Compare view
    "compare.title_a": {"es": "Pokémon A", "en": "Pokémon A"},
    "compare.title_b": {"es": "Pokémon B", "en": "Pokémon B"},
    "compare.pick_a": {"es": "Elegir A", "en": "Pick A"},
    "compare.pick_b": {"es": "Elegir B", "en": "Pick B"},
    "compare.compare": {"es": "Comparar", "en": "Compare"},
    "compare.back": {"es": "Volver", "en": "Back"},
    "compare.unset": {"es": "—", "en": "—"},
    "compare.no_types": {"es": "Sin tipos", "en": "No types"},
    "compare.need_both": {
        "es": "Selecciona ambos Pokémon (A y B) para comparar.",
        "en": "Select both Pokémon (A and B) to compare.",
    },
    "compare.comparing": {"es": "Comparando…", "en": "Comparing…"},
    "compare.not_found": {"es": "No encontrado: {error}", "en": "Not found: {error}"},
    "compare.error": {
        "es": "Error al comparar: {error}",
        "en": "Error comparing: {error}",
    },
    "compare.tie": {"es": "Empate", "en": "Tie"},
    "compare.wins": {"es": "Gana {side}", "en": "{side} wins"},
    "compare.no_chain": {"es": "Sin cadena", "en": "No chain"},
    "compare.total": {"es": "Total", "en": "Total"},
    "compare.stats": {"es": "Stats", "en": "Stats"},
    "compare.abilities": {"es": "Habilidades", "en": "Abilities"},
    "compare.evolution": {"es": "Evolución", "en": "Evolution"},
    "compare.total_stats": {
        "es": "Total de stats",
        "en": "Total stats",
    },
    # Type chart view
    "type.title": {"es": "Tabla de tipos", "en": "Type chart"},
    "type.type1": {"es": "Tipo 1", "en": "Type 1"},
    "type.type2": {"es": "Tipo 2 (opcional)", "en": "Type 2 (optional)"},
    "type.none": {"es": "Ninguno", "en": "None"},
    "type.calculate": {"es": "Calcular", "en": "Calculate"},
    "type.back": {"es": "Volver", "en": "Back"},
    "type.need_type1": {
        "es": "Selecciona al menos el Tipo 1.",
        "en": "Select at least Type 1.",
    },
    "type.calculating": {"es": "Calculando…", "en": "Calculating…"},
    "type.error": {
        "es": "Error al calcular: {error}",
        "en": "Error calculating: {error}",
    },
    "type.immune": {"es": "Inmune", "en": "Immune"},
    "type.normal_damage": {"es": "Normal", "en": "Normal"},
    "type.weakness": {
        "es": "Debilidades (daño recibido x2 o más)",
        "en": "Weaknesses (takes x2 or more)",
    },
    "type.resistance": {
        "es": "Resistencias (daño recibido a la mitad o menos)",
        "en": "Resistances (takes half or less)",
    },
    "type.immunity": {
        "es": "Inmunidades (no recibe daño)",
        "en": "Immunities (takes no damage)",
    },
    "type.neutral": {"es": "Daño normal (x1)", "en": "Normal damage (x1)"},
    # Components
    "common.retry": {"es": "Reintentar", "en": "Retry"},
    "common.loading": {"es": "Cargando…", "en": "Loading…"},
}

_FALLBACK_LANG = "es"


class Translator:
    """Traductor con idioma activo y catálogo bilingüe con fallbacks."""

    def __init__(
        self,
        lang: str = DEFAULT_LANGUAGE,
        catalog: dict[str, dict[str, str]] | None = None,
    ) -> None:
        self._lang = lang if lang in LANGUAGES else DEFAULT_LANGUAGE
        self._catalog = catalog if catalog is not None else _CATALOG

    @property
    def lang(self) -> str:
        return self._lang

    def set_lang(self, lang: str) -> None:
        if lang in LANGUAGES:
            self._lang = lang

    def t(self, key: str, **kwargs: object) -> str:
        entry = self._catalog.get(key)
        if entry is None:
            return key
        text = entry.get(self._lang) or entry.get(_FALLBACK_LANG) or key
        if kwargs:
            try:
                return text.format(**kwargs)
            except (KeyError, ValueError):
                return text
        return text


translator = Translator()


def t(key: str, **kwargs: object) -> str:
    """Traduce una clave usando el traductor por defecto (idioma activo)."""
    return translator.t(key, **kwargs)


def set_language(lang: str) -> None:
    translator.set_lang(lang)
