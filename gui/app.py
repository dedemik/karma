"""Ana pencere: menü, araç çubuğu, sekmeler ve durum çubuğu."""

import datetime
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from .tabs import HomeTab, LogTab, SettingsTab
from .theme import COLORS, PADDING, apply_theme

APP_NAME = "Masaüstü Uygulaması"
APP_VERSION = "0.1.0"


class MainWindow(tk.Tk):
    def __init__(self) -> None:
        super().__init__()

        self.title(APP_NAME)
        self.geometry("980x660")
        self.minsize(780, 520)

        self.fonts = apply_theme(self)

        self._build_menu()
        self._build_toolbar()
        self._build_tabs()
        self._build_statusbar()
        self._bind_shortcuts()

        self.set_status("Hazır. Başlamak için bir sekme seç.")
        self._tick()

    # ------------------------------------------------------------------ menü
    def _build_menu(self) -> None:
        menubar = tk.Menu(self)

        file_menu = tk.Menu(menubar, tearoff=False)
        file_menu.add_command(label="Yeni", accelerator="Ctrl+N", command=self.new_file)
        file_menu.add_command(label="Aç…", accelerator="Ctrl+O", command=self.open_file)
        file_menu.add_command(label="Kaydet", accelerator="Ctrl+S", command=self.save_file)
        file_menu.add_separator()
        file_menu.add_command(label="Çıkış", accelerator="Ctrl+Q", command=self.destroy)
        menubar.add_cascade(label="Dosya", menu=file_menu)

        edit_menu = tk.Menu(menubar, tearoff=False)
        edit_menu.add_command(label="Geri al", accelerator="Ctrl+Z",
                              command=lambda: self._send("<<Undo>>"))
        edit_menu.add_command(label="Yinele", accelerator="Ctrl+Y",
                              command=lambda: self._send("<<Redo>>"))
        edit_menu.add_separator()
        edit_menu.add_command(label="Ayarlar", command=lambda: self._select_tab(1))
        menubar.add_cascade(label="Düzen", menu=edit_menu)

        help_menu = tk.Menu(menubar, tearoff=False)
        help_menu.add_command(label="Hakkında", command=self.show_about)
        menubar.add_cascade(label="Yardım", menu=help_menu)

        self.configure(menu=menubar)

    # ------------------------------------------------------------- araç çubuğu
    def _build_toolbar(self) -> None:
        bar = ttk.Frame(self, style="Toolbar.TFrame", padding=(12, 8))
        bar.pack(fill="x")

        ttk.Button(bar, text="＋ Yeni", command=self.new_file).pack(side="left")
        ttk.Button(bar, text="Aç", command=self.open_file).pack(side="left", padx=(8, 0))
        ttk.Button(bar, text="Kaydet", style="Accent.TButton",
                   command=self.save_file).pack(side="left", padx=(8, 0))

        ttk.Label(bar, text=f"v{APP_VERSION}", style="Muted.TLabel").pack(side="right")

    # ---------------------------------------------------------------- sekmeler
    def _build_tabs(self) -> None:
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=12, pady=(12, 8))

        self.home_tab = HomeTab(self.notebook, self)
        self.settings_tab = SettingsTab(self.notebook, self)
        self.log_tab = LogTab(self.notebook, self)

        self.notebook.add(self.home_tab, text="  Genel  ")
        self.notebook.add(self.settings_tab, text="  Ayarlar  ")
        self.notebook.add(self.log_tab, text="  Günlük  ")

    def _select_tab(self, index: int) -> None:
        self.notebook.select(index)

    # ------------------------------------------------------------ durum çubuğu
    def _build_statusbar(self) -> None:
        bar = ttk.Frame(self, style="Toolbar.TFrame")
        bar.pack(fill="x", side="bottom")

        self.status_label = ttk.Label(bar, text="", style="Status.TLabel")
        self.status_label.pack(side="left", fill="x", expand=True)

        self.clock_label = ttk.Label(bar, text="", style="Status.TLabel")
        self.clock_label.pack(side="right", padx=PADDING)

    def set_status(self, message: str, kind: str = "info") -> None:
        colors = {"info": COLORS["muted"], "success": COLORS["success"], "danger": COLORS["danger"]}
        self.status_label.configure(text=message, foreground=colors.get(kind, COLORS["muted"]))

    def _tick(self) -> None:
        self.clock_label.configure(text=datetime.datetime.now().strftime("%d.%m.%Y  %H:%M:%S"))
        self.after(1000, self._tick)

    # ------------------------------------------------------------- kısayollar
    def _bind_shortcuts(self) -> None:
        self.bind("<Control-n>", lambda _e: self.new_file())
        self.bind("<Control-o>", lambda _e: self.open_file())
        self.bind("<Control-s>", lambda _e: self.save_file())
        self.bind("<Control-q>", lambda _e: self.destroy())
        self.bind("<Control-Tab>", lambda _e: self._cycle_tab(1))
        self.bind("<Control-Shift-Tab>", lambda _e: self._cycle_tab(-1))

    def _cycle_tab(self, step: int) -> None:
        count = self.notebook.index("end")
        self.notebook.select((self.notebook.index("current") + step) % count)

    def _send(self, virtual_event: str) -> None:
        widget = self.focus_get()
        if isinstance(widget, (tk.Text, tk.Entry)):
            widget.event_generate(virtual_event)

    # ---------------------------------------------------------------- eylemler
    def new_file(self) -> None:
        # TODO: gerçek bir "yeni dosya" akışı ekle (ör. editörü temizle).
        self.log_tab.log("Yeni dosya oluşturuldu.")
        self.set_status("Yeni dosya hazır.")

    def open_file(self) -> None:
        path = filedialog.askopenfilename(
            title="Dosya aç",
            filetypes=[("Metin dosyaları", "*.txt *.md"), ("Tüm dosyalar", "*.*")],
        )
        if not path:
            return
        try:
            with open(path, encoding="utf-8") as handle:
                content = handle.read()
        except OSError as exc:
            messagebox.showerror("Açılamadı", str(exc))
            return

        self.log_tab.log(f"Dosya açıldı: {path} ({len(content)} karakter)")
        self.set_status(f"Açıldı: {path.split('/')[-1]}", kind="success")

    def save_file(self) -> None:
        path = filedialog.asksaveasfilename(
            title="Kaydet",
            defaultextension=".txt",
            filetypes=[("Metin dosyası", "*.txt"), ("Tüm dosyalar", "*.*")],
        )
        if not path:
            return
        try:
            with open(path, "w", encoding="utf-8") as handle:
                handle.write("")  # TODO: kaydedilecek gerçek içeriği yaz.
        except OSError as exc:
            messagebox.showerror("Kaydedilemedi", str(exc))
            return

        self.log_tab.log(f"Dosya kaydedildi: {path}")
        self.set_status(f"Kaydedildi: {path.split('/')[-1]}", kind="success")

    def show_about(self) -> None:
        messagebox.showinfo(
            "Hakkında",
            f"{APP_NAME}\nSürüm {APP_VERSION}\n\nPython + tkinter ile yazılmış bir masaüstü iskeleti.\n"
            "Yeni özellikler için gui/tabs.py dosyasına göz at.",
        )
