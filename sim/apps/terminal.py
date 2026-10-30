"""Terminal: sahte bir kabuk. Tema değiştirmek ve uygulama açmak için de kullanılır."""

from __future__ import annotations

import platform
import time

from ..themes import THEME_ORDER, THEMES
from .base import App

WELCOME = [
    "SimOS 1.1 · tkinter kabuğu",
    "Yardım için 'help' yaz.",
    "",
]

HELP = [
    "Kullanılabilir komutlar:",
    "  help              bu listeyi göster",
    "  ls                dosyaları listele",
    "  whoami            kullanıcı adı",
    "  uname             sistem bilgisi",
    "  date              tarih / saat",
    "  neofetch          sistem özeti",
    "  themes            temaları listele",
    "  theme <id>        tema değiştir (win11 / macos / gnome)",
    "  open <uygulama>   uygulama aç (files, notes, calc, terminal, settings, about)",
    "  echo <metin>      metni yazdır",
    "  clear             ekranı temizle",
    "  exit              terminali kapat",
    "",
]


class TerminalApp(App):
    id = "terminal"
    title = "Terminal"
    width = 780
    height = 470

    def build(self, parent) -> None:
        self.lines = list(self.state.get("lines", WELCOME))

        self.output = self.text(parent, wrap="word", font=self.fonts["mono"])
        self.output.configure(bg=self.wt["field"], padx=12, pady=10)
        self.output.pack(fill="both", expand=True)
        self._render()

        row = self.frame(parent)
        row.pack(fill="x", pady=(10, 0))

        self.label(row, "kullanici@sim:~$", muted=True).pack(side="left")
        self.entry = self.entry(row)
        self.entry.pack(side="left", fill="x", expand=True, padx=(10, 0), ipady=4)
        self.entry.bind("<Return>", self._on_enter)
        self.entry.focus_set()

    # ------------------------------------------------------------------ çıktı
    def _write(self, line: str) -> None:
        self.lines.append(line)
        self.output.configure(state="normal")
        self.output.insert("end", line + "\n")
        self.output.see("end")
        self.output.configure(state="disabled")

    def _write_many(self, lines) -> None:
        for line in lines:
            self._write(line)

    def _render(self) -> None:
        self.output.configure(state="normal")
        self.output.delete("1.0", "end")
        for line in self.lines:
            self.output.insert("end", line + "\n")
        self.output.see("end")
        self.output.configure(state="disabled")

    # ---------------------------------------------------------------- komutlar
    def _on_enter(self, _event=None) -> None:
        command = self.entry.get().strip()
        self.entry.delete(0, "end")
        self._write(f"kullanici@sim:~$ {command}")
        if not command:
            return

        parts = command.split()
        name = parts[0].lower()
        args = parts[1:]

        if name == "help":
            self._write_many(HELP)
        elif name == "ls":
            self._write("Belgeler/  notlar.txt  okuma_listesi.md  ekran.png  muzik.mp3  arsiv.zip")
        elif name == "whoami":
            self._write("kullanici")
        elif name == "uname":
            self._write(f"SimOS 1.1 · Python {platform.python_version()} · tkinter")
        elif name == "date":
            self._write(time.strftime("%d.%m.%Y %H:%M:%S"))
        elif name == "echo":
            self._write(" ".join(args))
        elif name == "clear":
            self.lines.clear()
            self._write_many(WELCOME)
        elif name == "themes":
            current = self.desktop.theme_id
            for theme_id in THEME_ORDER:
                mark = "*" if theme_id == current else " "
                self._write(f" {mark} {theme_id:<8} {THEMES[theme_id]['label']}")
        elif name == "theme":
            target = args[0] if args else ""
            if target in THEMES:
                self._write(f"Tema değiştiriliyor: {THEMES[target]['label']}")
                self.desktop.set_theme(target)
                return
            self._write("Kullanım: theme win11 | macos | gnome")
        elif name == "open":
            target = args[0] if args else ""
            if target in ("files", "notes", "calc", "terminal", "settings", "about"):
                self._write(f"Açılıyor: {target}")
                self.desktop.open_app(target)
            else:
                self._write("Bilinmeyen uygulama. 'help' yaz.")
        elif name == "neofetch":
            self._write_many([
                "        ▄▄▄▄        kullanici@sim",
                "     ▄████████▄     -------------",
                f"    ███  ██  ███    OS: SimOS 1.1",
                f"    ███▄▄██▄▄███    Tema: {self.theme['label']}",
                f"     ▀████████▀     Python: {platform.python_version()}",
                f"        ▀▀▀▀        Ekran: {self.desktop.width}x{self.desktop.height}",
                "",
            ])
        elif name == "exit":
            self.window.close()
            return
        else:
            self._write(f"komut bulunamadı: {name} — 'help' yaz.")

    def get_state(self) -> dict:
        return {"lines": list(self.lines)}

    def on_focus(self) -> None:
        self.entry.focus_set()
