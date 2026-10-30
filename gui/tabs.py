"""Sekme içerikleri.

Her sekme bağımsız bir sınıf. Yeni bir sayfa eklemek için:
1) BaseTab'den türet,
2) build() içinde arayüzü kur,
3) gui/app.py içindeki _build_tabs() listesine ekle.
"""

import tkinter as tk
from tkinter import ttk

from .theme import COLORS, PADDING


class BaseTab(ttk.Frame):
    """Ortak başlık + açıklama düzeni."""

    title = "Sekme"
    description = ""

    def __init__(self, master, app):
        super().__init__(master, style="Card.TFrame", padding=PADDING)
        self.app = app

        header = ttk.Frame(self, style="Card.TFrame")
        header.pack(fill="x", pady=(4, 0))
        ttk.Label(header, text=self.title, style="Header.TLabel").pack(anchor="w")
        if self.description:
            ttk.Label(header, text=self.description, style="Subtitle.TLabel").pack(anchor="w", pady=(4, 0))

        ttk.Separator(self).pack(fill="x", pady=(PADDING, PADDING))

        self.body = ttk.Frame(self, style="Card.TFrame")
        self.body.pack(fill="both", expand=True)

        self.build()

    def build(self) -> None:
        """Alt sınıflar arayüzü burada kurar."""


class HomeTab(BaseTab):
    title = "Genel"
    description = "Örnek bileşenler: metin girişi, liste ve butonlar."

    def build(self) -> None:
        # --- Ekleme satırı -------------------------------------------------
        row = ttk.Frame(self.body, style="Card.TFrame")
        row.pack(fill="x")

        self.entry = ttk.Entry(row)
        self.entry.pack(side="left", fill="x", expand=True, ipady=2)
        self.entry.insert(0, "")
        self.entry.bind("<Return>", lambda _event: self.add_item())

        ttk.Button(row, text="Ekle", style="Accent.TButton",
                   command=self.add_item).pack(side="left", padx=(8, 0))
        ttk.Button(row, text="Temizle", style="Danger.TButton",
                   command=self.clear_items).pack(side="left", padx=(8, 0))

        # --- Liste ---------------------------------------------------------
        list_wrap = tk.Frame(self.body, bg=COLORS["border"], bd=0)
        list_wrap.pack(fill="both", expand=True, pady=(PADDING, 0))

        self.listbox = tk.Listbox(
            list_wrap,
            bg=COLORS["surface_alt"],
            fg=COLORS["fg"],
            selectbackground=COLORS["accent"],
            selectforeground="#0d1117",
            highlightthickness=0,
            borderwidth=0,
            activestyle="none",
            font=self.app.fonts["base"],
        )
        scroll = ttk.Scrollbar(list_wrap, orient="vertical", command=self.listbox.yview)
        self.listbox.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y", padx=1, pady=1)
        self.listbox.pack(side="left", fill="both", expand=True, padx=1, pady=1)

        self.listbox.bind("<Delete>", lambda _event: self.remove_selected())

        ttk.Label(self.body, text="İpucu: Enter ile ekle, Delete ile seçili öğeyi sil.",
                  style="Subtitle.TLabel").pack(anchor="w", pady=(8, 0))

    def add_item(self) -> None:
        text = self.entry.get().strip()
        if not text:
            self.app.set_status("Boş metin eklenemez.", kind="danger")
            return
        self.listbox.insert("end", text)
        self.entry.delete(0, "end")
        self.app.set_status(f"Eklendi: {text}", kind="success")

    def remove_selected(self) -> None:
        selection = self.listbox.curselection()
        if not selection:
            self.app.set_status("Silmek için listeden bir öğe seç.", kind="danger")
            return
        for index in reversed(selection):
            self.listbox.delete(index)
        self.app.set_status("Seçili öğe silindi.")

    def clear_items(self) -> None:
        if self.listbox.size() == 0:
            self.app.set_status("Liste zaten boş.")
            return
        self.listbox.delete(0, "end")
        self.app.set_status("Liste temizlendi.")


class SettingsTab(BaseTab):
    title = "Ayarlar"
    description = "Form bileşenleri için örnek yerleşim."

    def build(self) -> None:
        form = ttk.Frame(self.body, style="Card.TFrame")
        form.pack(fill="x")
        form.columnconfigure(1, weight=1)

        # Metin alanı
        ttk.Label(form, text="Uygulama adı", style="Card.TLabel").grid(
            row=0, column=0, sticky="w", pady=6, padx=(0, 12))
        self.name_var = tk.StringVar(value="Masaüstü Uygulaması")
        ttk.Entry(form, textvariable=self.name_var).grid(
            row=0, column=1, sticky="ew", pady=6)

        # Açılır liste
        ttk.Label(form, text="Tema", style="Card.TLabel").grid(
            row=1, column=0, sticky="w", pady=6, padx=(0, 12))
        self.theme_var = tk.StringVar(value="Koyu")
        ttk.Combobox(form, textvariable=self.theme_var, values=["Koyu", "Açık", "Sistem"],
                     state="readonly").grid(row=1, column=1, sticky="ew", pady=6)

        # Onay kutuları
        self.autosave_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(form, text="Değişiklikleri otomatik kaydet",
                        variable=self.autosave_var).grid(
            row=2, column=1, sticky="w", pady=(12, 4))

        self.notify_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(form, text="Bildirimleri göster",
                        variable=self.notify_var).grid(
            row=3, column=1, sticky="w", pady=4)

        # Kaydırıcı
        ttk.Label(form, text="Yazı boyutu", style="Card.TLabel").grid(
            row=4, column=0, sticky="w", pady=(16, 6), padx=(0, 12))
        self.scale_var = tk.IntVar(value=10)
        ttk.Scale(form, from_=8, to=18, orient="horizontal",
                  variable=self.scale_var).grid(row=4, column=1, sticky="ew", pady=(16, 6))

        ttk.Separator(self.body).pack(fill="x", pady=PADDING)

        actions = ttk.Frame(self.body, style="Card.TFrame")
        actions.pack(fill="x")
        ttk.Button(actions, text="Kaydet", style="Accent.TButton",
                   command=self.save).pack(side="left")
        ttk.Button(actions, text="Sıfırla", command=self.reset).pack(side="left", padx=(8, 0))

    def save(self) -> None:
        # TODO: ayarları bir dosyaya (örn. settings.json) yaz.
        self.app.set_status(
            f"Ayarlar kaydedildi: {self.name_var.get()} / {self.theme_var.get()}",
            kind="success",
        )

    def reset(self) -> None:
        self.name_var.set("Masaüstü Uygulaması")
        self.theme_var.set("Koyu")
        self.autosave_var.set(True)
        self.notify_var.set(False)
        self.scale_var.set(10)
        self.app.set_status("Ayarlar varsayılana döndü.")


class LogTab(BaseTab):
    title = "Günlük"
    description = "Konsol yerine uygulama içi kayıt alanı."

    def build(self) -> None:
        wrap = tk.Frame(self.body, bg=COLORS["border"], bd=0)
        wrap.pack(fill="both", expand=True)

        self.text = tk.Text(
            wrap,
            bg=COLORS["surface_alt"],
            fg=COLORS["fg"],
            insertbackground=COLORS["fg"],
            selectbackground=COLORS["accent"],
            highlightthickness=0,
            borderwidth=0,
            wrap="word",
            padx=10,
            pady=10,
            font=self.app.fonts["mono"],
        )
        self.text.pack(fill="both", expand=True, padx=1, pady=1)

        bar = ttk.Frame(self.body, style="Card.TFrame")
        bar.pack(fill="x", pady=(PADDING, 0))
        ttk.Button(bar, text="Örnek satır ekle",
                   command=self.append_sample).pack(side="left")
        ttk.Button(bar, text="Temizle", style="Danger.TButton",
                   command=self.clear).pack(side="left", padx=(8, 0))

        self.log("Uygulama hazır.")

    def log(self, message: str) -> None:
        self.text.insert("end", f"{message}\n")
        self.text.see("end")

    def append_sample(self) -> None:
        import datetime

        self.log(f"[{datetime.datetime.now():%H:%M:%S}] Örnek kayıt eklendi.")

    def clear(self) -> None:
        self.text.delete("1.0", "end")
        self.app.set_status("Günlük temizlendi.")
