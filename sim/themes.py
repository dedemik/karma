"""Tema tanımları: Windows 11, macOS ve GNOME.

Tek yerden görünüm: renkler, yazı tipleri, panel biçimi ve pencere kontrolleri.
"""

from __future__ import annotations

from copy import deepcopy
from tkinter import font as tkfont

BASE_FAMILIES = ["Inter", "Segoe UI", "Liberation Sans", "DejaVu Sans"]
MONO_FAMILIES = ["JetBrains Mono", "Fira Code", "DejaVu Sans Mono", "Liberation Mono"]


def _resolve_family(root, candidates: list[str]) -> str:
    available = {name.lower() for name in tkfont.families(root)}
    for candidate in candidates:
        if candidate.lower() in available:
            return candidate
    return "DejaVu Sans"


def build_fonts(root, families: list[str]) -> dict[str, tuple]:
    family = _resolve_family(root, families + BASE_FAMILIES)
    mono = _resolve_family(root, MONO_FAMILIES)
    return {
        "base": (family, 10),
        "small": (family, 9),
        "bold": (family, 10, "bold"),
        "title": (family, 11, "bold"),
        "big": (family, 15, "bold"),
        "huge": (family, 24, "bold"),
        "mono": (mono, 10),
        "mono_small": (mono, 9),
    }


THEMES: dict[str, dict] = {
    # ------------------------------------------------------------------ Windows
    "win11": {
        "label": "Windows 11",
        "families": ["Liberation Sans", "Segoe UI"],
        "accent": "#2f7cf6",
        "wallpaper": {
            "stops": ["#030b1c", "#0a2a5e", "#1a63c8", "#2f8ff0"],
            "blobs": [
                {"center": (0.74, 0.28), "radius": 0.42, "color": "#4f9dff", "alpha": 70},
                {"center": (0.18, 0.82), "radius": 0.55, "color": "#061a3d", "alpha": 150},
                {"center": (0.52, 0.55), "radius": 0.26, "color": "#9ecbff", "alpha": 40},
            ],
        },
        "desktop": {"side": "left", "fg": "#ffffff", "muted": "#c9dcff"},
        "window": {
            "bg": "#1a1d24", "border": "#2d3341", "field": "#12151b",
            "title_bg": "#232833", "title_bg_inactive": "#1a1d24",
            "title_fg": "#f1f4fa", "title_fg_inactive": "#8e97a9",
            "fg": "#eef1f7", "muted": "#97a1b5",
            "accent": "#2f7cf6", "accent_hover": "#4a90ff", "danger": "#ff6b6b",
            "radius": 10, "titlebar": 40, "pad": 12, "controls": "win",
        },
        "panel": {
            "style": "taskbar", "position": "bottom", "height": 56,
            "bg": "#12141a", "border": "#22262f",
            "fg": "#eef1f7", "muted": "#8f98ab", "accent": "#2f7cf6",
            "radius": 0, "margin": 0, "floating": False,
        },
        "dock": None,
    },
    # -------------------------------------------------------------------- macOS
    "macos": {
        "label": "macOS",
        "families": ["Liberation Sans", "DejaVu Sans"],
        "accent": "#0a84ff",
        "wallpaper": {
            "stops": ["#120a24", "#2a1145", "#5b2168", "#a63b74", "#e46a8a"],
            "blobs": [
                {"center": (0.22, 0.24), "radius": 0.40, "color": "#ff8a5c", "alpha": 70},
                {"center": (0.80, 0.72), "radius": 0.45, "color": "#ff5c9d", "alpha": 50},
                {"center": (0.55, 0.10), "radius": 0.34, "color": "#7b5cff", "alpha": 80},
            ],
        },
        "desktop": {"side": "right", "fg": "#ffffff", "muted": "#f2d9ff"},
        "window": {
            "bg": "#2b2c33", "border": "#43444e", "field": "#212227",
            "title_bg": "#32333b", "title_bg_inactive": "#282930",
            "title_fg": "#f5f5f7", "title_fg_inactive": "#9a9ba4",
            "fg": "#f2f2f5", "muted": "#a4a5b0",
            "accent": "#0a84ff", "accent_hover": "#4aa3ff", "danger": "#ff453a",
            "radius": 14, "titlebar": 38, "pad": 14, "controls": "mac",
        },
        "panel": {
            "style": "menubar", "position": "top", "height": 30,
            "bg": "#14151b", "border": "#26272f",
            "fg": "#f4f4f7", "muted": "#a9aab5", "accent": "#0a84ff",
            "radius": 0, "margin": 0, "floating": False,
        },
        "dock": {
            "height": 66, "icon": 42, "radius": 20, "margin": 10,
            "bg": "#22232b", "border": "#3a3b45",
            "fg": "#ffffff", "accent": "#0a84ff",
        },
    },
    # ------------------------------------------------------------------- GNOME
    "gnome": {
        "label": "GNOME",
        "families": ["Cantarell", "Ubuntu", "DejaVu Sans"],
        "accent": "#3584e4",
        "wallpaper": {
            "stops": ["#08131f", "#0d2f3d", "#146a6a", "#2aa198"],
            "blobs": [
                {"center": (0.30, 0.30), "radius": 0.42, "color": "#54d6c4", "alpha": 60},
                {"center": (0.78, 0.70), "radius": 0.48, "color": "#062a3c", "alpha": 140},
                {"center": (0.60, 0.20), "radius": 0.24, "color": "#d7fff4", "alpha": 35},
            ],
        },
        "desktop": {"side": "left", "fg": "#ffffff", "muted": "#c8f0ea"},
        "window": {
            "bg": "#242424", "border": "#3d3d3d", "field": "#1b1b1b",
            "title_bg": "#303030", "title_bg_inactive": "#262626",
            "title_fg": "#ffffff", "title_fg_inactive": "#9c9c9c",
            "fg": "#f2f2f2", "muted": "#a8a8a8",
            "accent": "#3584e4", "accent_hover": "#5a9df0", "danger": "#e01b24",
            "radius": 12, "titlebar": 44, "pad": 12, "controls": "gnome",
        },
        "panel": {
            "style": "gnome", "position": "top", "height": 34,
            "bg": "#0b0b0d", "border": "#1d1d20",
            "fg": "#f6f6f6", "muted": "#b5b5b8", "accent": "#3584e4",
            "radius": 0, "margin": 0, "floating": False,
        },
        "dock": {
            "height": 68, "icon": 44, "radius": 22, "margin": 10,
            "bg": "#1b1d22", "border": "#31343d",
            "fg": "#ffffff", "accent": "#3584e4",
        },
    },
}

THEME_ORDER = ["win11", "macos", "gnome"]


def load_theme(root, theme_id: str) -> dict:
    theme = deepcopy(THEMES[theme_id])
    theme["id"] = theme_id
    theme["fonts"] = build_fonts(root, theme["families"])
    return theme
