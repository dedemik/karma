"""Renkler, yazı tipleri ve ttk stilleri.

Tasarımı değiştirmek için tek yer: buradaki COLORS / FONTS sözlükleri
ve apply_theme() içindeki stiller.
"""

from tkinter import font as tkfont
from tkinter import ttk

COLORS = {
    "bg": "#1b1d24",          # pencere arka planı
    "surface": "#242732",     # kart / sekme yüzeyi
    "surface_alt": "#2d3140",  # giriş alanları, listeler
    "border": "#383d4f",
    "fg": "#e9eaf1",          # ana metin
    "muted": "#98a0b6",       # ikincil metin
    "accent": "#5b8cff",
    "accent_hover": "#7ba4ff",
    "accent_active": "#4674e0",
    "success": "#3ecf8e",
    "danger": "#ff6b6b",
}

PADDING = 16


def pick_family(root) -> str:
    """Sistemde var olan ilk yazı tipi ailesini seçer."""
    available = {name.lower() for name in tkfont.families(root)}
    for candidate in ("Inter", "Segoe UI", "Ubuntu", "Cantarell", "DejaVu Sans"):
        if candidate.lower() in available:
            return candidate
    return "TkDefaultFont"


def apply_theme(root) -> dict[str, tuple]:
    """ttk temasını kurar ve kullanılacak yazı tiplerini döndürür."""
    family = pick_family(root)
    fixed_family = tkfont.nametofont("TkFixedFont").actual("family")

    fonts = {
        "base": (family, 10),
        "small": (family, 9),
        "bold": (family, 10, "bold"),
        "header": (family, 20, "bold"),
        "subtitle": (family, 10),
        "mono": (fixed_family, 10),
    }

    style = ttk.Style(root)
    style.theme_use("clam")  # renkleri serbestçe değiştirebilmek için

    # Kök ve genel bileşenler
    root.configure(background=COLORS["bg"])
    style.configure(".", background=COLORS["bg"], foreground=COLORS["fg"],
                    font=fonts["base"], borderwidth=0, focuscolor=COLORS["accent"])
    style.configure("TFrame", background=COLORS["bg"])
    style.configure("Card.TFrame", background=COLORS["surface"])
    style.configure("Toolbar.TFrame", background=COLORS["surface"])
    style.configure("TLabel", background=COLORS["bg"], foreground=COLORS["fg"])
    style.configure("Card.TLabel", background=COLORS["surface"], foreground=COLORS["fg"])
    style.configure("Header.TLabel", background=COLORS["surface"],
                    foreground=COLORS["fg"], font=fonts["header"])
    style.configure("Subtitle.TLabel", background=COLORS["surface"],
                    foreground=COLORS["muted"], font=fonts["subtitle"])
    style.configure("Muted.TLabel", background=COLORS["bg"],
                    foreground=COLORS["muted"], font=fonts["small"])

    # Butonlar
    style.configure("TButton", background=COLORS["surface_alt"],
                    foreground=COLORS["fg"], padding=(14, 7),
                    font=fonts["bold"], relief="flat")
    style.map("TButton",
              background=[("pressed", COLORS["border"]), ("active", COLORS["border"])],
              foreground=[("disabled", COLORS["muted"])])

    style.configure("Accent.TButton", background=COLORS["accent"],
                    foreground="#0d1117")
    style.map("Accent.TButton",
              background=[("pressed", COLORS["accent_active"]),
                          ("active", COLORS["accent_hover"])])

    style.configure("Danger.TButton", background=COLORS["surface_alt"],
                    foreground=COLORS["danger"])
    style.map("Danger.TButton",
              background=[("active", COLORS["border"])],
              foreground=[("active", COLORS["danger"])])

    # Sekmeler
    style.configure("TNotebook", background=COLORS["bg"], borderwidth=0, tabmargins=(12, 8, 12, 0))
    style.configure("TNotebook.Tab", background=COLORS["bg"], foreground=COLORS["muted"],
                    padding=(18, 9), font=fonts["bold"], borderwidth=0)
    style.map("TNotebook.Tab",
              background=[("selected", COLORS["surface"])],
              foreground=[("selected", COLORS["fg"]), ("active", COLORS["fg"])],
              expand=[("selected", (0, 0, 0, 0))])

    # Giriş alanları
    style.configure("TEntry", fieldbackground=COLORS["surface_alt"],
                    foreground=COLORS["fg"], insertcolor=COLORS["fg"],
                    bordercolor=COLORS["border"], lightcolor=COLORS["border"],
                    darkcolor=COLORS["border"], padding=8)
    style.map("TEntry", bordercolor=[("focus", COLORS["accent"])])

    style.configure("TCombobox", fieldbackground=COLORS["surface_alt"],
                    background=COLORS["surface_alt"], foreground=COLORS["fg"],
                    arrowcolor=COLORS["muted"], bordercolor=COLORS["border"],
                    padding=6)
    style.map("TCombobox", fieldbackground=[("readonly", COLORS["surface_alt"])],
              foreground=[("readonly", COLORS["fg"])])

    style.configure("TCheckbutton", background=COLORS["surface"],
                    foreground=COLORS["fg"], focuscolor=COLORS["surface"])
    style.map("TCheckbutton", background=[("active", COLORS["surface"])],
              indicatorcolor=[("selected", COLORS["accent"])])

    style.configure("Horizontal.TScale", background=COLORS["surface"],
                    troughcolor=COLORS["surface_alt"], bordercolor=COLORS["border"])

    # Durum çubuğu
    style.configure("Status.TLabel", background=COLORS["surface"],
                    foreground=COLORS["muted"], font=fonts["small"], padding=(12, 6))

    # Ayırıcı
    style.configure("TSeparator", background=COLORS["border"])

    return fonts
