"""Vista de detalle de un Pokémon organizada por pestañas."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import flet as ft

from app.models.evolution import EvolutionChain, EvolutionNode
from app.models.pokemon import PokemonDetail, PokemonMove, PokemonSummary
from app.models.species import PokemonSpecies
from app.ui.components.stat_bar import build_stat_bar
from app.ui.theme import border, type_color

STAT_ORDER = [
    "hp",
    "attack",
    "defense",
    "special-attack",
    "special-defense",
    "speed",
]

_METHOD_ORDER = {
    "level-up": 0,
    "machine": 1,
    "egg": 2,
    "tutor": 3,
}

_METHOD_LABELS = {
    "level-up": "Por nivel",
    "machine": "Máquinas (MT/MO)",
    "egg": "Huevo",
    "tutor": "Tutor",
}

_MEDIA_SOURCES = [
    ("Normal", "front_default"),
    ("Shiny", "front_shiny"),
    ("Trasera", "back_default"),
    ("Trasera shiny", "back_shiny"),
    ("Oficial", "official_artwork"),
    ("Home", "home"),
]


def _mock_stats(pokemon_id: int) -> list[tuple[str, int]]:
    return [
        ("hp", 20 + pokemon_id % 100),
        ("attack", 30 + (pokemon_id * 3) % 120),
        ("defense", 30 + (pokemon_id * 5) % 110),
        ("speed", 40 + (pokemon_id * 7) % 130),
    ]


def build_empty_detail() -> ft.Container:
    return ft.Container(
        content=ft.Text(
            "Selecciona un Pokémon para ver su detalle",
            color=ft.Colors.GREY,
            text_align=ft.TextAlign.CENTER,
        ),
        padding=24,
        alignment=ft.Alignment.CENTER,
    )


def build_detail(summary: PokemonSummary) -> ft.Container:
    display_name = summary.name.replace("-", " ").title()
    stats = _mock_stats(summary.id or 0)
    return ft.Container(
        content=ft.Column(
            [
                ft.Image(
                    src=summary.sprite_url or "",
                    width=140,
                    height=140,
                    fit=ft.BoxFit.CONTAIN,
                ),
                ft.Text(
                    f"#{summary.id:03d}" if summary.id else "#---",
                    color=ft.Colors.GREY,
                ),
                ft.Text(display_name, size=26, weight=ft.FontWeight.BOLD),
                ft.Divider(height=16),
                *[build_stat_bar(name, value) for name, value in stats],
                ft.Divider(height=16),
                ft.Text(
                    "Maqueta estática · datos simulados",
                    italic=True,
                    size=11,
                    color=ft.Colors.GREY,
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=4,
        ),
        padding=16,
        border=border(1, ft.Colors.OUTLINE_VARIANT),
        border_radius=12,
    )


def _type_badges(pokemon: PokemonDetail) -> ft.Row:
    badges: list[ft.Control] = [
        ft.Container(
            content=ft.Text(
                type_name.name,
                color=ft.Colors.WHITE,
                weight=ft.FontWeight.BOLD,
                size=12,
            ),
            bgcolor=type_color(type_name.name),
            border_radius=20,
            padding=ft.Padding.symmetric(horizontal=10, vertical=4),
        )
        for type_name in pokemon.types
    ]
    if not badges:
        badges = [ft.Text("Sin tipos", color=ft.Colors.GREY)]
    return ft.Row(badges, spacing=6)


def _info_row(label: str, value: str) -> ft.Row:
    return ft.Row(
        [
            ft.Text(label, size=12, color=ft.Colors.GREY),
            ft.Text(value, weight=ft.FontWeight.BOLD),
        ],
        spacing=8,
    )


def _display_name(pokemon: PokemonDetail, species: PokemonSpecies | None) -> str:
    if species is not None and species.spanish_name:
        return species.spanish_name
    return pokemon.name.replace("-", " ").title()


def _missing(value: str | None) -> str:
    return value or "No disponible"


def _tabs_from_panels(panels: list[tuple[str, ft.Control]]) -> ft.Tabs:
    return ft.Tabs(
        length=len(panels),
        expand=True,
        content=ft.Column(
            expand=True,
            controls=[
                ft.TabBar(
                    scrollable=True,
                    tabs=[ft.Tab(label=label) for label, _ in panels],
                ),
                ft.TabBarView(
                    expand=True,
                    controls=[panel for _, panel in panels],
                ),
            ],
        ),
    )


def _info_panel(pokemon: PokemonDetail, species: PokemonSpecies | None) -> ft.Control:
    images: dict[str, str] = {
        "normal": pokemon.sprites.get("front_default")
        or pokemon.sprites.get("home")
        or "",
        "shiny": pokemon.sprites.get("front_shiny") or "",
        "artwork": pokemon.sprites.get("official_artwork")
        or pokemon.sprites.get("home")
        or "",
    }
    selected_key = "artwork" if images["artwork"] and not images["normal"] else "normal"
    main_image = ft.Image(
        src=images[selected_key],
        width=150,
        height=150,
        fit=ft.BoxFit.CONTAIN,
        error_content=ft.Icon(
            ft.Icons.CATCHING_POKEMON,
            size=80,
            color=ft.Colors.GREY,
        ),
    )

    def on_view_select(_: Any) -> None:
        key = view_dropdown.value or "normal"
        if key in images and images[key]:
            main_image.src = images[key]
            main_image.update()

    view_dropdown = ft.Dropdown(
        value=selected_key,
        width=150,
        dense=True,
        label="Vista",
        options=[
            ft.dropdown.Option(key="normal", text="Normal"),
            ft.dropdown.Option(key="shiny", text="Shiny"),
            ft.dropdown.Option(key="artwork", text="Artwork"),
        ],
        on_select=on_view_select,
    )

    ability_text = ", ".join(
        ability.name.replace("-", " ").title()
        + (" (oculta)" if ability.is_hidden else "")
        for ability in pokemon.abilities
    ) or "No disponible"
    experience = (
        str(pokemon.base_experience) if pokemon.base_experience else "No disponible"
    )
    height = f"{pokemon.height / 10:.1f} m" if pokemon.height else "No disponible"
    weight = f"{pokemon.weight / 10:.1f} kg" if pokemon.weight else "No disponible"
    description = species.description if species and species.description else None

    return ft.Column(
        [
            main_image,
            view_dropdown,
            ft.Text(
                f"#{pokemon.id:03d}",
                size=12,
                color=ft.Colors.GREY,
            ),
            ft.Text(
                _display_name(pokemon, species),
                size=24,
                weight=ft.FontWeight.BOLD,
            ),
            _type_badges(pokemon),
            ft.Text(
                description,
                text_align=ft.TextAlign.CENTER,
            )
            if description
            else ft.Text(
                "Sin descripción disponible",
                italic=True,
                color=ft.Colors.GREY,
            ),
            ft.Divider(height=12),
            _info_row("Experiencia base", experience),
            _info_row("Altura", height),
            _info_row("Peso", weight),
            ft.Divider(height=12),
            _info_row("Habilidades", ability_text),
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=6,
        scroll=ft.ScrollMode.AUTO,
        expand=True,
    )


def _stats_panel(pokemon: PokemonDetail) -> ft.Control:
    stats = {stat.name: stat.value for stat in pokemon.stats}
    total = sum(stats.values())
    rows: list[ft.Control] = [
        ft.Text(f"Total: {total}", size=16, weight=ft.FontWeight.BOLD),
    ]
    for name in STAT_ORDER:
        if name in stats:
            rows.append(build_stat_bar(name, stats[name]))
    return ft.Column(
        rows,
        spacing=6,
        scroll=ft.ScrollMode.AUTO,
        expand=True,
    )


def _condition_text(node: EvolutionNode) -> str:
    if node.trade:
        return "Intercambio"
    if node.happiness:
        return "Amistad"
    if node.min_level:
        return f"Nivel {node.min_level}"
    if node.item:
        return f"Usar {node.item.replace('-', ' ').title()}"
    if node.trigger == "use-item":
        return "Usar objeto"
    if node.trigger == "level-up":
        return "Subir de nivel"
    if node.trigger == "trade":
        return "Intercambio"
    if node.trigger == "happiness":
        return "Amistad"
    if node.trigger:
        return node.trigger.replace("-", " ").title()
    return "Evoluciona"


def _species_sprite(node: EvolutionNode) -> ft.Control:
    if node.sprite_url:
        return ft.Image(
            src=node.sprite_url,
            width=44,
            height=44,
            fit=ft.BoxFit.CONTAIN,
            error_content=ft.Icon(
                ft.Icons.CATCHING_POKEMON,
                size=28,
                color=ft.Colors.GREY,
            ),
        )
    return ft.Icon(ft.Icons.CATCHING_POKEMON, size=28, color=ft.Colors.GREY)


def _append_chain_level(
    node: EvolutionNode,
    controls: list[ft.Control],
    depth: int,
    on_pokemon_clicked: Callable[[int, str], Any] | None,
) -> None:
    ident = f"#{node.pokemon_id:03d}" if node.pokemon_id else "#---"

    def _clicked(_: Any) -> None:
        if on_pokemon_clicked and node.pokemon_id is not None:
            on_pokemon_clicked(node.pokemon_id, node.pokemon_name)

    card = ft.Container(
        content=ft.Row(
            [
                _species_sprite(node),
                ft.Column(
                    [
                        ft.Text(ident, size=11, color=ft.Colors.GREY),
                        ft.Text(
                            node.pokemon_name.replace("-", " ").title(),
                            weight=ft.FontWeight.BOLD,
                        ),
                    ],
                    spacing=0,
                ),
            ],
            spacing=10,
        ),
        border=border(1, ft.Colors.OUTLINE_VARIANT),
        border_radius=8,
        padding=6,
        on_click=_clicked if on_pokemon_clicked and node.pokemon_id else None,
    )
    controls.append(ft.Row([ft.Container(width=24 * depth), card], spacing=0))
    for child in node.children:
        condition = _condition_text(child)
        controls.append(
            ft.Row(
                [
                    ft.Container(width=24 * depth + 28),
                    ft.Text(f"↓ {condition}", size=11, color=ft.Colors.GREY),
                ],
                spacing=0,
            )
        )
        _append_chain_level(child, controls, depth + 1, on_pokemon_clicked)


def _evolution_panel(
    chain: EvolutionChain | None,
    on_pokemon_clicked: Callable[[int, str], Any] | None,
) -> ft.Control:
    if chain is None:
        return ft.Text(
            "Este Pokémon no tiene cadena evolutiva registrada.",
            italic=True,
            color=ft.Colors.GREY,
        )
    controls: list[ft.Control] = []
    _append_chain_level(chain.chain, controls, 0, on_pokemon_clicked)
    return ft.ListView(
        controls=controls,
        spacing=6,
        padding=4,
        expand=True,
    )


def _method_label(method: str) -> str:
    label = _METHOD_LABELS.get(method)
    if label is None:
        return method.replace("-", " ").title()
    return label


def _method_priority(method: str) -> int:
    return _METHOD_ORDER.get(method, 10)


def _moves_panel(pokemon: PokemonDetail) -> ft.Control:
    grouped: dict[str, list[PokemonMove]] = {}
    for move in pokemon.moves:
        grouped.setdefault(_method_label(move.learn_method), []).append(move)

    ordered_labels = sorted(grouped, key=_method_priority)
    rows: list[ft.Control] = []
    for label in ordered_labels:
        moves = grouped[label]
        if label == _METHOD_LABELS.get("level-up"):
            moves = sorted(
                moves,
                key=lambda move: (
                    move.level if move.level is not None else 0,
                    move.name,
                ),
            )
        rows.append(ft.Text(label, weight=ft.FontWeight.BOLD, size=13))
        for move in moves:
            suffix = f" — Nivel {move.level}" if move.level else ""
            rows.append(
                ft.Text(
                    f"• {move.name.replace('-', ' ').title()}{suffix}",
                    size=12,
                )
            )
    if not rows:
        rows = [
            ft.Text(
                "No hay movimientos registrados.",
                italic=True,
                color=ft.Colors.GREY,
            )
        ]
    return ft.ListView(
        controls=rows,
        spacing=4,
        padding=4,
        expand=True,
    )


def _gender_text(gender_rate: int | None) -> str:
    if gender_rate is None:
        return "No disponible"
    if gender_rate == -1:
        return "Sin género"
    female_pct = gender_rate / 8 * 100
    male_pct = 100 - female_pct
    return f"♂ {male_pct:.0f}% · ♀ {female_pct:.0f}%"


def _species_panel(
    pokemon: PokemonDetail,
    species: PokemonSpecies | None,
) -> ft.Control:
    if species is None:
        return ft.Text(
            "Datos de especie no disponibles.",
            italic=True,
            color=ft.Colors.GREY,
        )
    cradle = ", ".join(
        group.replace("-", " ").title() for group in species.egg_groups
    )
    return ft.Column(
        [
            _info_row("Hábitat", _missing(species.habitat)),
            _info_row("Color", _missing(species.color)),
            _info_row("Forma", _missing(species.shape)),
            _info_row("Género", _gender_text(species.gender_rate)),
            _info_row(
                "Ratio de captura",
                str(species.capture_rate) if species.capture_rate else "No disponible",
            ),
            _info_row(
                "Felicidad base",
                str(species.base_happiness)
                if species.base_happiness
                else "No disponible",
            ),
            _info_row(
                "Experiencia base",
                str(pokemon.base_experience)
                if pokemon.base_experience
                else "No disponible",
            ),
            _info_row("Crecimiento", _missing(species.growth_rate)),
            _info_row("Grupo huevo", cradle or "No disponible"),
            _info_row(
                "Generación",
                str(species.generation) if species.generation else "No disponible",
            ),
        ],
        spacing=6,
        scroll=ft.ScrollMode.AUTO,
        expand=True,
    )


def _media_panel(pokemon: PokemonDetail) -> ft.Control:
    rows: list[ft.Control] = []
    for label, key in _MEDIA_SOURCES:
        url = pokemon.sprites.get(key)
        if not url:
            continue
        rows.append(
            ft.Row(
                [
                    ft.Image(
                        src=url,
                        width=90,
                        height=90,
                        fit=ft.BoxFit.CONTAIN,
                        error_content=ft.Icon(
                            ft.Icons.CATCHING_POKEMON,
                            size=28,
                            color=ft.Colors.GREY,
                        ),
                    ),
                    ft.Text(label),
                ],
                spacing=10,
            )
        )
    if not rows:
        rows = [
            ft.Text(
                "Sin imágenes disponibles.",
                italic=True,
                color=ft.Colors.GREY,
            )
        ]
    return ft.ListView(
        controls=rows,
        spacing=4,
        padding=4,
        expand=True,
    )


def build_pokemon_detail(
    pokemon: PokemonDetail,
    species: PokemonSpecies | None = None,
    chain: EvolutionChain | None = None,
    on_pokemon_clicked: Callable[[int, str], Any] | None = None,
) -> ft.Container:
    panels: list[tuple[str, ft.Control]] = [
        ("Info", _info_panel(pokemon, species)),
        ("Stats", _stats_panel(pokemon)),
        ("Evolución", _evolution_panel(chain, on_pokemon_clicked)),
        ("Movs", _moves_panel(pokemon)),
        ("Especie", _species_panel(pokemon, species)),
        ("Media", _media_panel(pokemon)),
    ]
    return ft.Container(
        content=_tabs_from_panels(panels),
        padding=16,
        border=border(1, ft.Colors.OUTLINE_VARIANT),
        border_radius=12,
    )