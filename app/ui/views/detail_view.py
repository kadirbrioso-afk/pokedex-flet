"""Vista de detalle de un Pokémon organizada por pestañas."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import flet as ft

from app.i18n import t
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

_METHOD_LABELS: dict[str, str] = {
    "level-up": "detail.method.level",
    "machine": "detail.method.machine",
    "egg": "detail.method.egg",
    "tutor": "detail.method.tutor",
}

_MEDIA_SOURCES = [
    ("detail.media.normal", "front_default"),
    ("detail.media.shiny", "front_shiny"),
    ("detail.media.back", "back_default"),
    ("detail.media.back_shiny", "back_shiny"),
    ("detail.media.official", "official_artwork"),
    ("detail.media.home", "home"),
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
            t("detail.select_pokemon"),
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
        badges = [ft.Text(t("detail.no_types"), color=ft.Colors.GREY)]
    return ft.Row(badges, spacing=6)


def _info_row(label: str, value: str) -> ft.Row:
    return ft.Row(
        [
            ft.Text(label, size=12, color=ft.Colors.GREY),
            ft.Text(value, weight=ft.FontWeight.BOLD),
        ],
        spacing=8,
    )


def _display_name(
    pokemon: PokemonDetail,
    species: PokemonSpecies | None,
    lang: str = "es",
) -> str:
    if species is not None:
        localized = species.localized_name(lang)
        if localized:
            return localized
    return pokemon.name.replace("-", " ").title()


def _missing(value: str | None) -> str:
    return value or t("detail.not_available")


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


def _info_panel(
    pokemon: PokemonDetail,
    species: PokemonSpecies | None,
    is_favorite: bool = False,
    on_toggle_favorite: Callable[[], Any] | None = None,
    lang: str = "es",
) -> ft.Control:
    images: dict[str, str] = {
        "normal": pokemon.sprites.get("front_default")
        or pokemon.sprites.get("home")
        or "",
        "shiny": pokemon.sprites.get("front_shiny") or "",
        "artwork": pokemon.sprites.get("official_artwork")
        or pokemon.sprites.get("home")
        or "",
    }
    selected_key = "artwork" if images["artwork"] else "normal"
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
        label=t("detail.view_label"),
        options=[
            ft.dropdown.Option(key="normal", text=t("detail.view.normal")),
            ft.dropdown.Option(key="shiny", text=t("detail.view.shiny")),
            ft.dropdown.Option(key="artwork", text=t("detail.view.artwork")),
        ],
        on_select=on_view_select,
    )

    ability_text = ", ".join(
        ability.name.replace("-", " ").title()
        + (t("detail.hidden_suffix") if ability.is_hidden else "")
        for ability in pokemon.abilities
    ) or t("detail.not_available")
    missing = t("detail.not_available")
    experience = (
        str(pokemon.base_experience) if pokemon.base_experience else missing
    )
    height = f"{pokemon.height / 10:.1f} m" if pokemon.height else missing
    weight = f"{pokemon.weight / 10:.1f} kg" if pokemon.weight else missing
    description = (
        species.localized_description(lang) if species is not None else None
    )

    favorite = ft.IconButton(
        icon=ft.Icons.STAR if is_favorite else ft.Icons.STAR_BORDER,
        icon_color=ft.Colors.AMBER if is_favorite else ft.Colors.GREY,
        tooltip=(
            t("detail.favorite.remove") if is_favorite else t("detail.favorite.add")
        ),
        on_click=(lambda _: on_toggle_favorite()) if on_toggle_favorite else None,
    )

    return ft.Column(
        [
            main_image,
            view_dropdown,
            ft.Text(
                f"#{pokemon.id:03d}",
                size=12,
                color=ft.Colors.GREY,
            ),
            ft.Row(
                [
                    ft.Text(
                        _display_name(pokemon, species, lang),
                        size=24,
                        weight=ft.FontWeight.BOLD,
                        expand=True,
                    ),
                    favorite,
                ],
                spacing=8,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            _type_badges(pokemon),
            ft.Text(
                description,
                text_align=ft.TextAlign.CENTER,
            )
            if description
            else ft.Text(
                t("detail.no_description"),
                italic=True,
                color=ft.Colors.GREY,
            ),
            ft.Divider(height=12),
            _info_row(t("detail.base_experience"), experience),
            _info_row(t("detail.height"), height),
            _info_row(t("detail.weight"), weight),
            ft.Divider(height=12),
            _info_row(t("detail.abilities"), ability_text),
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
        ft.Text(t("detail.total", total=total), size=16, weight=ft.FontWeight.BOLD),
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


def _time_of_day_text(value: str) -> str:
    return {
        "day": t("detail.time.day"),
        "night": t("detail.time.night"),
        "dusk": t("detail.time.dusk"),
        "dawn": t("detail.time.dawn"),
    }.get(value, value.replace("-", " "))


def _evolution_gender_text(value: int) -> str:
    return {1: t("detail.gender.only_male"), 2: t("detail.gender.only_female")}.get(
        value, t("detail.gender.specific")
    )


def _relative_stats_text(value: int) -> str:
    if value == 1:
        return t("detail.relative.atk_gt_def")
    if value == -1:
        return t("detail.relative.atk_lt_def")
    return t("detail.relative.atk_eq_def")


def _item_title(name: str) -> str:
    return name.replace("-", " ").title()


def _condition_parts(node: EvolutionNode) -> list[str]:
    parts: list[str] = []
    trigger = node.trigger
    if node.trade or trigger == "trade":
        base = t("detail.cond.trade")
        if node.held_item:
            base += f" {t('detail.cond.holding')} {_item_title(node.held_item)}"
        parts.append(base)
    elif node.min_happiness is not None:
        parts.append(f"{t('detail.cond.friendship')} (min. {node.min_happiness})")
    elif node.happiness or trigger == "happiness":
        parts.append(t("detail.cond.friendship"))
    elif node.held_item:
        parts.append(f"{t('detail.cond.holding')} {_item_title(node.held_item)}")
    elif node.item:
        parts.append(f"{t('detail.cond.use')} {_item_title(node.item)}")
    elif node.min_level:
        parts.append(f"{t('detail.cond.level')} {node.min_level}")
    elif node.known_move:
        parts.append(f"{t('detail.cond.known_move')} {_item_title(node.known_move)}")
    elif node.location:
        parts.append(f"{t('detail.cond.at')} {_item_title(node.location)}")
    elif trigger == "level-up":
        parts.append(t("detail.cond.level_up"))
    elif trigger == "use-item":
        parts.append(t("detail.cond.use_item"))
    elif trigger == "shed":
        parts.append(t("detail.cond.shed"))
    elif trigger:
        parts.append(_item_title(trigger))

    if node.time_of_day:
        parts.append(_time_of_day_text(node.time_of_day))
    if node.gender:
        parts.append(_evolution_gender_text(node.gender))
    if node.relative_physical_stats is not None:
        parts.append(_relative_stats_text(node.relative_physical_stats))
    if node.needs_overworld_rain:
        parts.append(t("detail.cond.rain"))
    return parts


def _condition_arrow(node: EvolutionNode) -> ft.Control:
    parts = _condition_parts(node)
    text = " · ".join(parts) or t("detail.cond.evolves")
    arrow = ft.Text(
        f"↓ {text}",
        size=11,
        color=ft.Colors.GREY,
    )
    if parts:
        arrow.tooltip = ft.Tooltip(
            message="\n".join(parts),
            wait_duration=300,
        )
    return arrow


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
        controls.append(
            ft.Row(
                [
                    ft.Container(width=24 * depth + 28),
                    _condition_arrow(child),
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
            t("detail.evolution_none"),
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
        rows.append(ft.Text(t(label), weight=ft.FontWeight.BOLD, size=13))
        for move in moves:
            suffix = f" — {t('detail.level')} {move.level}" if move.level else ""
            rows.append(
                ft.Text(
                    f"• {move.name.replace('-', ' ').title()}{suffix}",
                    size=12,
                )
            )
    if not rows:
        rows = [
            ft.Text(
                t("detail.no_moves"),
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
        return t("detail.not_available")
    if gender_rate == -1:
        return t("detail.no_gender")
    female_pct = gender_rate / 8 * 100
    male_pct = 100 - female_pct
    return f"♂ {male_pct:.0f}% · ♀ {female_pct:.0f}%"


def _species_panel(
    pokemon: PokemonDetail,
    species: PokemonSpecies | None,
) -> ft.Control:
    if species is None:
        return ft.Text(
            t("detail.species_unavailable"),
            italic=True,
            color=ft.Colors.GREY,
        )
    cradle = ", ".join(
        group.replace("-", " ").title() for group in species.egg_groups
    )
    missing = t("detail.not_available")
    return ft.Column(
        [
            _info_row(t("detail.habitat"), _missing(species.habitat)),
            _info_row(t("detail.color"), _missing(species.color)),
            _info_row(t("detail.shape"), _missing(species.shape)),
            _info_row(t("detail.gender"), _gender_text(species.gender_rate)),
            _info_row(
                t("detail.capture_rate"),
                str(species.capture_rate) if species.capture_rate else missing,
            ),
            _info_row(
                t("detail.base_happiness"),
                str(species.base_happiness)
                if species.base_happiness
                else missing,
            ),
            _info_row(
                t("detail.base_experience"),
                str(pokemon.base_experience)
                if pokemon.base_experience
                else missing,
            ),
            _info_row(t("detail.growth_rate"), _missing(species.growth_rate)),
            _info_row(t("detail.egg_groups"), cradle or missing),
            _info_row(
                t("detail.generation"),
                str(species.generation) if species.generation else missing,
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
                    ft.Text(t(label)),
                ],
                spacing=10,
            )
        )
    if not rows:
        rows = [
            ft.Text(
                t("detail.no_media"),
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
    is_favorite: bool = False,
    on_toggle_favorite: Callable[[], Any] | None = None,
    lang: str = "es",
) -> ft.Container:
    panels: list[tuple[str, ft.Control]] = [
        (
            "detail.tab.info",
            _info_panel(pokemon, species, is_favorite, on_toggle_favorite, lang),
        ),
        ("detail.tab.stats", _stats_panel(pokemon)),
        ("detail.tab.evolution", _evolution_panel(chain, on_pokemon_clicked)),
        ("detail.tab.moves", _moves_panel(pokemon)),
        ("detail.tab.species", _species_panel(pokemon, species)),
        ("detail.tab.media", _media_panel(pokemon)),
    ]
    panels = [(t(label), content) for label, content in panels]
    return ft.Container(
        content=_tabs_from_panels(panels),
        padding=16,
        border=border(1, ft.Colors.OUTLINE_VARIANT),
        border_radius=12,
    )