import flet as ft


# Main palette
BACKGROUND = "#F8FAF8"
SURFACE = "#FFFFFF"
SURFACE_MUTED = "#F2F4F2"

PRIMARY = "#168543"
PRIMARY_SOFT = "#DDF2E4"

SECONDARY = "#3976C5"
SECONDARY_SOFT = "#E6EFFA"

TEXT_PRIMARY = "#172019"
TEXT_SECONDARY = "#6B726D"

OUTLINE = "#E3E8E4"

# Component-specific surfaces
RACKET_CARD_BG = "#EEF4F7"
STRING_ICON_BG = "#DDF2E4"
GRIP_ICON_BG = "#E3EEFB"

# Shared dimensions
PAGE_PADDING = 18
SECTION_SPACING = 16
CARD_RADIUS = 16


def build_theme() -> ft.Theme:
    return ft.Theme(
        use_material3=True,
        scaffold_bgcolor=BACKGROUND,
        color_scheme=ft.ColorScheme(
            primary=PRIMARY,
            on_primary=ft.Colors.WHITE,
            primary_container=PRIMARY_SOFT,
            on_primary_container=TEXT_PRIMARY,
            secondary=SECONDARY,
            secondary_container=SECONDARY_SOFT,
            surface=SURFACE,
            on_surface=TEXT_PRIMARY,
            outline=OUTLINE,
        ),
        navigation_bar_theme=ft.NavigationBarTheme(
            bgcolor=SURFACE,
            indicator_color=PRIMARY_SOFT,
            elevation=0,
        ),
    )
