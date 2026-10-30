"""Masaüstü: duvar kağıdı, simgeler, paneller ve pencere yönetimi."""

from __future__ import annotations

import tkinter as tk

from . import panel as panel_module
from .apps import APP_CLASSES, DESKTOP_APPS
from .icons import draw_app_icon
from .settings import load_settings, save_settings
from .themes import THEME_ORDER, THEMES, load_theme
from .wallpaper import draw_wallpaper
from .window import SimWindow


class Desktop:
    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("Bilgisayar Simülasyonu")
        self.root.configure(bg="#04060a")

        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        self.root.geometry(f"{screen_w}x{screen_h}+0+0")

        self.canvas = tk.Canvas(self.root, bg="#04060a", bd=0, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.root.update_idletasks()

        self._fullscreen = True
        try:
            self.root.attributes("-fullscreen", True)
        except tk.TclError:
            self._fullscreen = False
        self.root.update_idletasks()

        self.width = max(900, self.canvas.winfo_width())
        self.height = max(640, self.canvas.winfo_height())

        self.theme_id = ""
        self.theme: dict = {}
        self.windows: list[SimWindow] = []
        self.active: SimWindow | None = None
        self.popup = False
        self._cascade = 0
        self._photo = None
        self._resize_job = None

        # fare ile sürükleme / boyutlandırma yakalaması: (pencere, kip, veri)
        self._pointer_action: tuple[SimWindow, str, object] | None = None

        # panel ikonu üstünde bekleyince açılan pencere önizlemesi
        self.settings = load_settings()
        self.preview_job = None
        self.preview_hide_job = None
        self._preview_target: str | None = None
        self._preview_anchor = (0.0, 0.0, 1.0)

        self._bind_events()
        self.set_theme(self._initial_theme())
        self._boot()
        self._tick()
        self.root.after(400, self._apply_resize)

    def _initial_theme(self) -> str:
        """Kaydedilmiş tema geçerliyse onu, değilse Windows 11'i kullan."""
        saved = self.settings.get("theme")
        return saved if saved in THEMES else "win11"

    # ------------------------------------------------------------------ olaylar
    def _bind_events(self) -> None:
        self.root.protocol("WM_DELETE_WINDOW", self.quit_app)
        self.root.bind("<Escape>", self._on_escape)
        self.root.bind("<F11>", lambda _e: self.toggle_fullscreen())
        self.root.bind("<Control-q>", lambda _e: self.quit_app())
        for index, theme_id in enumerate(THEME_ORDER, start=1):
            self.root.bind(f"<Control-Key-{index}>",
                           lambda _e, t=theme_id: self.set_theme(t))

        self.canvas.bind("<Configure>", self._on_resize)
        self.canvas.bind("<Button-1>", self._on_canvas_click, add="+")
        self.canvas.bind("<B1-Motion>", self._on_pointer_motion)
        self.canvas.bind("<ButtonRelease-1>", self._on_pointer_release)
        self.root.bind_all("<ButtonPress-1>", self._on_global_click, add="+")

    # ---------------------------------------------------------- fare yakalaması
    def begin_pointer_action(self, win: SimWindow, mode: str, data=None) -> None:
        """Başlık sürükleme veya kenar boyutlandırma başladığında çağrılır.

        Hareket olayları pencere etiketine değil canvas'a bağlanır; böylece imleç
        tutamacın dışına çıksa bile sürükleme devam eder.
        """
        self._pointer_action = (win, mode, data)

    def _on_pointer_motion(self, event) -> None:
        action = self._pointer_action
        if not action:
            return
        win, mode, data = action
        if mode == "move":
            win._drag_move(event)
        elif mode == "resize":
            win._resize_move(event, data)

    def _on_pointer_release(self, _event=None) -> None:
        action, self._pointer_action = self._pointer_action, None
        if not action:
            return
        win, _mode, _data = action
        win.end_pointer_action()


    def _on_escape(self, _event=None) -> None:
        if self.popup:
            self.close_popup()
        else:
            self.toggle_fullscreen()

    def _on_global_click(self, event) -> None:
        if self.popup and event.widget is not self.canvas:
            self.close_popup()

        widget = event.widget
        while widget is not None:
            for win in self.windows:
                if not win.minimized and widget is win.frame:
                    self.focus_window(win)
                    return
            widget = getattr(widget, "master", None)

    def _on_canvas_click(self, _event=None) -> None:
        if not self.popup:
            return
        hit = self.canvas.find_withtag("current")
        if hit:
            tags = self.canvas.gettags(hit[0])
            keep = ("popup", "ltile-", "sysrow-", "plaunch", "papp-", "psys")
            if any(tag.startswith(keep) for tag in tags):
                return
        self.close_popup()

    # ------------------------------------------------------------------- tema
    def set_theme(self, theme_id: str) -> None:
        if theme_id not in THEMES or theme_id == self.theme_id:
            return

        snapshot = []
        active_app = self.active.app.id if self.active else None
        for win in self.windows:
            snapshot.append({
                "app": win.app.id,
                "geometry": (win.x, win.y, win.w, win.h),
                "state": win.app.get_state(),
                "minimized": win.minimized,
                "maximized": win.maximized,
                "restore": win._restore_geo,
            })

        self.close_popup()
        for win in self.windows:
            win.destroy()
        self.windows.clear()
        self.active = None

        self.theme_id = theme_id
        self.theme = load_theme(self.root, theme_id)
        self.root.configure(bg=self.theme["panel"]["bg"])

        self.draw_wallpaper()
        self.draw_desktop_icons()
        self.draw_panels()

        for item in snapshot:
            win = self.open_app(item["app"], state=item["state"],
                                geometry=item["geometry"], focus=False)
            if item.get("maximized"):
                win.maximized = True
                win._restore_geo = item.get("restore") or item["geometry"]
                x1, y1, x2, y2 = self.useful_area()
                win.set_geometry(x1, y1, x2 - x1, y2 - y1)
            if item["minimized"]:
                win.minimize()

        if active_app:
            win = self.window_for(active_app)
            if win and not win.minimized:
                self.focus_window(win)
        self.draw_panels()

        # tercihi hatırla (dosya yazılamazsa sessizce geç)
        self.settings["theme"] = theme_id
        save_settings(self.settings)

    # ----------------------------------------------------------------- çizimler
    def draw_wallpaper(self) -> None:
        self.canvas.delete("wallpaper")
        self._photo = draw_wallpaper(self.canvas, self.width, self.height,
                                     self.theme["wallpaper"])
        self.canvas.tag_lower("wallpaper")

    def draw_desktop_icons(self) -> None:
        canvas = self.canvas
        canvas.delete("deskicon")
        theme = self.theme
        fonts = theme["fonts"]
        side = theme["desktop"]["side"]
        size = 52
        top = 56 if theme["panel"]["position"] == "top" else 30
        x = self.width - 34 - size if side == "right" else 34

        for index, app_id in enumerate(DESKTOP_APPS):
            y = top + index * 102
            tags = ("deskicon", f"dicon-{app_id}")
            draw_app_icon(canvas, app_id, x, y, size, tags=tags,
                          mono_family=fonts["mono"][0])
            label = APP_CLASSES[app_id].title
            canvas.create_text(x + size / 2 + 1, y + size + 17, text=label,
                               fill="#000000", font=fonts["small"],
                               anchor="center", tags=tags)
            canvas.create_text(x + size / 2, y + size + 16, text=label,
                               fill=theme["desktop"]["fg"], font=fonts["small"],
                               anchor="center", tags=tags)
            canvas.tag_bind(f"dicon-{app_id}", "<Button-1>",
                            lambda _e, a=app_id: self.open_app(a))

        if self.windows:
            canvas.tag_lower("deskicon", self.windows[0].tag)

    def draw_panels(self) -> None:
        self.cancel_preview()
        panel_module.draw_panels(self)
        if self.canvas.find_withtag("boot"):
            self.canvas.tag_raise("boot")

    # ------------------------------------------------------------------ pencereler
    def window_for(self, app_id: str) -> SimWindow | None:
        for win in self.windows:
            if win.app.id == app_id:
                return win
        return None

    def open_app(self, app_id: str, state: dict | None = None,
                 geometry: tuple[int, int, int, int] | None = None,
                 focus: bool = True) -> SimWindow | None:
        app_class = APP_CLASSES.get(app_id)
        if app_class is None:
            return None

        existing = self.window_for(app_id)
        if existing:
            if existing.minimized:
                existing.restore()
            if focus:
                self.focus_window(existing)
            return existing

        if geometry:
            x, y, w, h = geometry
        elif app_id == "about":
            w, h = app_class.width, app_class.height
            x, y = (self.width - w) // 2, (self.height - h) // 2
        else:
            w, h = app_class.width, app_class.height
            self._cascade = (self._cascade + 1) % 7
            x = 130 + self._cascade * 34
            y = 88 + self._cascade * 26
            x = max(24, min(x, self.width - w - 24))
            y = max(24, min(y, self.height - h - 90))

        app = app_class(self, state)
        win = SimWindow(self, app, x, y, w, h)
        self.windows.append(win)

        if focus:
            self.focus_window(win)
        return win

    def focus_window(self, win: SimWindow) -> None:
        if win.minimized:
            win.restore()
        self.close_popup()

        if self.active is win:
            win.raise_()
            self.canvas.tag_raise("panel")
            return

        for other in self.windows:
            other.set_active(other is win)
        self.active = win
        win.raise_()
        self.draw_panels()
        win.app.on_focus()

    def close_window(self, win: SimWindow) -> None:
        if win in self.windows:
            self.windows.remove(win)
        if self.active is win:
            self.active = None
        win.destroy()
        self.draw_panels()

    def activate_app(self, app_id: str) -> None:
        win = self.window_for(app_id)
        if win is None:
            self.open_app(app_id)
        elif win.minimized:
            win.restore()
            self.focus_window(win)
        elif self.active is win:
            win.minimize()
        else:
            self.focus_window(win)

    # ---------------------------------------------------------------------- menüler
    def toggle_launcher(self) -> None:
        self.cancel_preview()
        if self.popup:
            self.close_popup()
        else:
            panel_module.open_launcher(self)

    def open_system_menu(self) -> None:
        self.cancel_preview()
        panel_module.open_system_menu(self)

    def close_popup(self) -> None:
        if self.popup:
            self.canvas.delete("popup")
            self.popup = False

    # ------------------------------------------------------------------ önizleme
    def cancel_preview_jobs(self) -> None:
        for attribute in ("preview_job", "preview_hide_job"):
            job = getattr(self, attribute, None)
            if job:
                try:
                    self.root.after_cancel(job)
                except tk.TclError:
                    pass
                setattr(self, attribute, None)

    def cancel_preview(self) -> None:
        """Bekleyen önizleme işlerini iptal et ve kartı kaldır."""
        self.cancel_preview_jobs()
        self.canvas.delete("preview")

    # ----------------------------------------------------------------------- sistem
    def useful_area(self) -> tuple[int, int, int, int]:
        theme = self.theme
        top = 0
        bottom = self.height
        panel = theme["panel"]
        if panel["position"] == "top":
            top = panel["height"]
        else:
            bottom = self.height - panel["height"]
        dock = theme.get("dock")
        if dock:
            bottom -= dock["height"] + dock["margin"] * 2
        return 12, top + 12, self.width - 12, bottom - 8

    def toggle_fullscreen(self) -> None:
        self._fullscreen = not self._fullscreen
        try:
            self.root.attributes("-fullscreen", self._fullscreen)
        except tk.TclError:
            return
        if not self._fullscreen:
            self.root.geometry(
                f"{self.root.winfo_screenwidth()}x{self.root.winfo_screenheight()}+0+0")
        self.root.after(150, self._apply_resize)
        self.root.after(500, self._apply_resize)

    def quit_app(self) -> None:
        self.root.destroy()

    # ------------------------------------------------------------------- yeniden boyut
    def _on_resize(self, event) -> None:
        if event.widget is not self.canvas:
            return
        if self._resize_job:
            self.root.after_cancel(self._resize_job)
        self._resize_job = self.root.after(150, self._apply_resize)

    def _apply_resize(self) -> None:
        self._resize_job = None
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        if width < 200 or height < 200:
            return
        if (width, height) == (self.width, self.height):
            return
        self.close_popup()
        self.width, self.height = width, height
        self.draw_wallpaper()
        self.draw_desktop_icons()
        self.draw_panels()
        for win in self.windows:
            if win.maximized:
                x1, y1, x2, y2 = self.useful_area()
                win.set_geometry(x1, y1, x2 - x1, y2 - y1)

    # -------------------------------------------------------------------- açılış / saat
    def _boot(self) -> None:
        canvas = self.canvas
        fonts = self.theme["fonts"]
        width = max(self.width, self.root.winfo_screenwidth())
        height = max(self.height, self.root.winfo_screenheight())
        canvas.create_rectangle(0, 0, width, height, fill="#05070b",
                                outline="", tags=("boot",))
        draw_app_icon(canvas, "about", width / 2 - 40, height / 2 - 120, 80,
                      tags=("boot",), mono_family=fonts["mono"][0])
        canvas.create_text(width / 2, height / 2 - 4, text="SimOS",
                           fill="#ffffff",
                           font=(fonts["huge"][0], 30, "bold"), tags=("boot",))
        canvas.create_text(width / 2, height / 2 + 34, text="başlatılıyor…",
                           fill="#9aa0b4", font=fonts["base"], tags=("boot",))
        canvas.tag_raise("boot")
        self.root.after(900, lambda: canvas.delete("boot"))

    def _tick(self) -> None:
        try:
            clock, date = panel_module.clock_texts(self.theme["panel"]["style"])
            self.canvas.itemconfigure("panel-clock", text=clock)
            self.canvas.itemconfigure("panel-date", text=date)
        except tk.TclError:
            pass
        self.root.after(1000, self._tick)

    # ------------------------------------------------------------------------ çalıştır
    def run(self) -> None:
        self.root.mainloop()
