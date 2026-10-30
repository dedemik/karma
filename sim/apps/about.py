"""Hakkında penceresi."""

from __future__ import annotations

import platform
import tkinter as tk

from ..icons import draw_app_icon
from .base import App


class AboutApp(App):
    id = "about"
    title = "Hakkında"
    width = 520
    height = 440

    def build(self, parent) -> None:
        wrap = self.frame(parent)
        wrap.pack(fill="both", expand=True)

        icon = tk.Canvas(wrap, width=96, height=96, bg=self.wt["bg"],
                         highlightthickness=0, bd=0)
        icon.pack(pady=(10, 12))
        draw_app_icon(icon, "about", 8, 8, 80, mono_family=self.fonts["mono"][0])

        self.label(wrap, "Bilgisayar Simülasyonu", big=True).pack()
        self.label(wrap, "SimOS 1.1", muted=True).pack(pady=(2, 14))

        text = (
            "Python + tkinter ile yazılmış bir masaüstü simülasyonu.\n"
            "Pencereler, paneller ve duvar kağıtları tamamen kod ile çiziliyor.\n\n"
            f"Tema: {self.theme['label']}\n"
            f"Python: {platform.python_version()}\n\n"
            "Kısayollar: Ctrl+1 / Ctrl+2 / Ctrl+3 tema, F11 tam ekran, Ctrl+Q çıkış."
        )
        label = self.label(wrap, text, justify="center")
        label.configure(anchor="center", wraplength=420)
        label.pack(pady=(0, 6))

        self.button(wrap, "Tamam", lambda: self.window.close(),
                    kind="accent").pack(pady=(12, 0))
