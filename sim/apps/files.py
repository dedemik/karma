"""Dosyalar: sahte bir ana dizin ve metin önizlemesi."""

from __future__ import annotations

import tkinter as tk

from .base import App

FILES = [
    ("Belgeler/", "klasör", "—"),
    ("notlar.txt", "metin", "2,4 KB"),
    ("okuma_listesi.md", "metin", "1,1 KB"),
    ("ekran.png", "resim", "284 KB"),
    ("muzik.mp3", "ses", "4,2 MB"),
    ("arsiv.zip", "arşiv", "12 MB"),
]

CONTENTS = {
    "notlar.txt": (
        "Bugün yapılacaklar\n"
        "--------------------\n"
        "1. Masaüstü simülasyonuna tema geçişi ekle\n"
        "2. GNOME panelini düzelt\n"
        "3. Kahve al\n"
    ),
    "okuma_listesi.md": (
        "# Okuma listesi\n\n"
        "- The Art of Unix Programming\n"
        "- Design Patterns\n"
        "- Kısa Python Notları\n"
    ),
}


class FilesApp(App):
    id = "files"
    title = "Dosyalar"
    width = 760
    height = 540

    def build(self, parent) -> None:
        self.header(parent, "Dosyalar", "Ana dizin  ~/").pack(fill="x", pady=(0, 12))

        body = self.frame(parent)
        body.pack(fill="both", expand=True)

        self.listbox = tk.Listbox(
            body, bg=self.wt["field"], fg=self.wt["fg"],
            selectbackground=self.wt["accent"], selectforeground="#0b0d12",
            highlightthickness=0, bd=0, activestyle="none",
            font=self.fonts["base"], height=7,
        )
        for name, kind, size in FILES:
            self.listbox.insert("end", f"  {name:<26}{kind:>10}{size:>10}")
        self.listbox.pack(fill="x")
        self.listbox.bind("<Double-Button-1>", self._open_selected)

        self.label(body, "Çift tıkla: metin dosyalarını önizle", muted=True,
                   bg=self.wt["bg"]).pack(anchor="w", pady=(10, 6))

        self.preview = self.text(body, height=8, wrap="word")
        self.preview.insert("1.0", "Önizleme için bir dosyanın üzerine çift tıkla.")
        self.preview.configure(state="disabled")
        self.preview.pack(fill="both", expand=True)

        self.status = self.label(body, "", muted=True)
        self.status.pack(anchor="w", pady=(8, 0))

    def _open_selected(self, _event=None) -> None:
        selection = self.listbox.curselection()
        if not selection:
            return
        name, kind, size = FILES[selection[0]]
        if name.endswith("/"):
            self.status.configure(text=f"{name} açıldı (simülasyon)")
            return

        content = CONTENTS.get(name)
        if content is None:
            self.status.configure(text=f"{name} · {kind} · {size} — önizleme yok")
            return

        self.preview.configure(state="normal")
        self.preview.delete("1.0", "end")
        self.preview.insert("1.0", content)
        self.preview.configure(state="disabled")
        self.status.configure(text=f"{name} önizleniyor · {size}")
