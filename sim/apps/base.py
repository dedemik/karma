"""Uygulama tabanı: tema renkleriyle widget üreten yardımcılar."""

from __future__ import annotations

import tkinter as tk

from ..draw import lighten


class App:
    id = ""
    title = ""
    width = 760
    height = 520

    def __init__(self, desktop, state: dict | None = None) -> None:
        self.desktop = desktop
        self.theme = desktop.theme
        self.wt = self.theme["window"]
        self.fonts = self.theme["fonts"]
        self.state = state or {}
        self.window = None

    # ------------------------------------------------------------- widget'lar
    def frame(self, master, bg: str | None = None, **kwargs) -> tk.Frame:
        return tk.Frame(master, bg=bg or self.wt["bg"], bd=0,
                        highlightthickness=0, **kwargs)

    def label(self, master, text: str = "", muted: bool = False, bold: bool = False,
              big: bool = False, bg: str | None = None, **kwargs) -> tk.Label:
        font = self.fonts["big"] if big else (
            self.fonts["bold"] if bold else self.fonts["base"])
        kwargs.setdefault("anchor", "w")
        kwargs.setdefault("justify", "left")
        return tk.Label(master, text=text, bg=bg or self.wt["bg"],
                        fg=self.wt["muted"] if muted else self.wt["fg"],
                        font=font, **kwargs)

    def button(self, master, text: str, command, kind: str = "normal", **kwargs) -> tk.Button:
        wt = self.wt
        if kind == "accent":
            bg, fg = wt["accent"], "#0b0d12"
            hover = wt["accent_hover"]
        elif kind == "danger":
            bg, fg = wt["field"], wt["danger"]
            hover = lighten(wt["field"], 0.12)
        else:
            bg, fg = wt["field"], wt["fg"]
            hover = lighten(wt["field"], 0.12)

        button = tk.Button(
            master, text=text, command=command, bg=bg, fg=fg,
            activebackground=hover, activeforeground=fg,
            bd=0, relief="flat", highlightthickness=0, cursor="hand2",
            font=self.fonts["bold"], padx=12, pady=6, **kwargs,
        )
        button.bind("<Enter>", lambda _e: button.configure(bg=hover))
        button.bind("<Leave>", lambda _e: button.configure(bg=bg))
        return button

    def entry(self, master, **kwargs) -> tk.Entry:
        wt = self.wt
        return tk.Entry(
            master, bg=wt["field"], fg=wt["fg"],
            insertbackground=wt["accent"], relief="flat",
            highlightthickness=1, highlightbackground=wt["border"],
            highlightcolor=wt["accent"], font=self.fonts["base"], **kwargs,
        )

    def text(self, master, **kwargs) -> tk.Text:
        wt = self.wt
        kwargs.setdefault("wrap", "word")
        kwargs.setdefault("font", self.fonts["base"])
        return tk.Text(
            master, bg=wt["field"], fg=wt["fg"],
            insertbackground=wt["accent"], selectbackground=wt["accent"],
            selectforeground="#0b0d12", relief="flat", highlightthickness=0,
            bd=0, padx=12, pady=10, **kwargs,
        )

    def header(self, master, title: str, subtitle: str = "") -> tk.Frame:
        box = self.frame(master)
        self.label(box, title, big=True).pack(anchor="w")
        if subtitle:
            self.label(box, subtitle, muted=True).pack(anchor="w", pady=(2, 0))
        return box

    def separator(self, master) -> tk.Frame:
        line = tk.Frame(master, bg=self.wt["border"], height=1)
        line.pack_propagate(False)
        return line

    # ---------------------------------------------------------------- yaşam döngüsü
    def build(self, parent) -> None:
        raise NotImplementedError

    def get_state(self) -> dict:
        return {}

    def on_focus(self) -> None:
        """Pencere odaklandığında çağrılır."""
