"""Notlar: basit, tema uyumlu metin editörü."""

from __future__ import annotations

import time

from .base import App

VARS = {
    "text": (
        "Masaüstü simülasyonu\n"
        "====================\n\n"
        "Bu pencere tamamen tkinter ile çizildi.\n"
        "Tema değiştirince içerik korunur.\n\n"
        "- Panelden uygulama aç\n"
        "- Başlık çubuğundan sürükle\n"
        "- Ctrl+1 / Ctrl+2 / Ctrl+3 ile tema değiştir\n"
    )
}


class NotesApp(App):
    id = "notes"
    title = "Notlar"
    width = 700
    height = 500

    def build(self, parent) -> None:
        head = self.frame(parent)
        head.pack(fill="x", pady=(0, 10))

        titles = self.frame(head)
        titles.pack(side="left", fill="x", expand=True)
        self.header(titles, "Notlar", "notlar.txt").pack(anchor="w")

        self.button(head, "Kaydet", self._save, kind="accent").pack(side="right")

        self.editor = self.text(parent, undo=True)
        self.editor.insert("1.0", self.state.get("text", VARS["text"]))
        self.editor.pack(fill="both", expand=True)

        self.status = self.label(parent, "Hazır", muted=True)
        self.status.pack(anchor="w", pady=(8, 0))

    def _save(self) -> None:
        self.status.configure(text=f"Kaydedildi · {time.strftime('%H:%M:%S')} (simülasyon)")

    def get_state(self) -> dict:
        return {"text": self.editor.get("1.0", "end-1c")}

    def on_focus(self) -> None:
        self.editor.focus_set()
