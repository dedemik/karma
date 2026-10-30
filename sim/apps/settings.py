"""Ayarlar: canlı tema seçici ve sistem bilgisi."""

from __future__ import annotations

import platform
import tkinter as tk

from ..themes import THEMES
from ..settings import settings_path
from .base import App

DESCRIPTIONS = {
    "win11": "Alt görev çubuğu, kutu kontroller",
    "macos": "Üst menü çubuğu, alt dock",
    "gnome": "Üst bar, yüzen dash",
}


class SettingsApp(App):
    id = "settings"
    title = "Ayarlar"
    width = 780
    height = 560

    def build(self, parent) -> None:
        self.header(parent, "Ayarlar", "Görünüm ve sistem").pack(fill="x", pady=(0, 14))

        self.label(parent, "Görünüm", bold=True).pack(anchor="w")

        cards = self.frame(parent)
        cards.pack(fill="x", pady=(8, 0))

        for index, (theme_id, theme) in enumerate(THEMES.items()):
            active = theme_id == self.desktop.theme_id
            card = tk.Frame(cards, bg=self.wt["field"], bd=0,
                            highlightthickness=2,
                            highlightbackground=self.wt["accent"] if active else self.wt["border"])
            card.grid(row=0, column=index, sticky="nsew", padx=(0, 10))
            cards.columnconfigure(index, weight=1, uniform="card")

            preview = tk.Frame(card, bg=theme["wallpaper"]["stops"][-1], height=64)
            preview.pack(fill="x")
            preview.pack_propagate(False)

            name = tk.Label(card, text=theme["label"], bg=self.wt["field"],
                            fg=self.wt["fg"], font=self.fonts["bold"])
            name.pack(anchor="w", padx=10, pady=(8, 0))

            desc = tk.Label(card, text=DESCRIPTIONS.get(theme_id, ""), bg=self.wt["field"],
                            fg=self.wt["muted"], font=self.fonts["small"],
                            wraplength=200, justify="left")
            desc.pack(anchor="w", padx=10, pady=(2, 10))

            note = "Şu an etkin" if active else "Geçiş yap"
            status = tk.Label(card, text=note, bg=self.wt["field"],
                              fg=self.wt["accent"] if active else self.wt["muted"],
                              font=self.fonts["small"])
            status.pack(anchor="w", padx=10, pady=(0, 10))

            handler = lambda _e=None, t=theme_id: self._switch(t)
            for widget in (card, preview, name, desc, status):
                widget.bind("<Button-1>", handler)
                widget.configure(cursor="hand2")

        self.separator(parent).pack(fill="x", pady=16)

        self.label(parent, "Sistem", bold=True).pack(anchor="w")

        options = self.frame(parent)
        options.pack(fill="x", pady=(8, 0))

        self.dark_var = tk.BooleanVar(value=True)
        self.sound_var = tk.BooleanVar(value=False)
        for var, text in ((self.dark_var, "Koyu mod"), (self.sound_var, "Arayüz sesleri")):
            check = tk.Checkbutton(
                options, text=text, variable=var, bg=self.wt["bg"], fg=self.wt["fg"],
                activebackground=self.wt["bg"], activeforeground=self.wt["fg"],
                selectcolor=self.wt["field"], bd=0, highlightthickness=0,
                font=self.fonts["base"], anchor="w", cursor="hand2",
                command=self._toggle,
            )
            check.pack(anchor="w")

        info = self.frame(parent)
        info.pack(fill="x", pady=(14, 0))

        rows = [
            ("Tema", self.theme["label"]),
            ("Sürüm", "SimOS 1.1 (simülasyon)"),
            ("Python", platform.python_version()),
            ("Çözünürlük", f"{self.desktop.width} × {self.desktop.height}"),
            ("Tercihler", str(settings_path())),
        ]
        for label_text, value in rows:
            row = self.frame(info)
            row.pack(fill="x", pady=2)
            self.label(row, label_text, muted=True, width=16).pack(side="left")
            self.label(row, value).pack(side="left")

        self.status = self.label(parent, "Hazır", muted=True)
        self.status.pack(anchor="w", pady=(16, 0))

    def _switch(self, theme_id: str) -> None:
        if theme_id == self.desktop.theme_id:
            self.status.configure(text="Bu tema zaten etkin.")
            return
        self.desktop.set_theme(theme_id)

    def _toggle(self) -> None:
        self.status.configure(
            text=f"Koyu mod: {'açık' if self.dark_var.get() else 'kapalı'} · "
                 f"Sesler: {'açık' if self.sound_var.get() else 'kapalı'} (simülasyon)"
        )
