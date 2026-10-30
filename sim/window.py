"""Simülasyondaki pencereler: sürükleme, odak, küçültme, büyütme, kapatma."""

from __future__ import annotations

import tkinter as tk

from .draw import lighten, rounded, rounded_top

# pencere boyutlandırma sınırları ve tutamaç bölgeleri
MIN_WIDTH = 340
MIN_HEIGHT = 240
RESIZE_ZONE = 6
RESIZE_CURSORS = {
    "r": "sb_h_double_arrow",
    "b": "sb_v_double_arrow",
    "br": "sizing",
}


class SimWindow:
    _counter = 0

    def __init__(self, desktop, app, x: int, y: int, width: int, height: int) -> None:
        SimWindow._counter += 1
        self.uid = SimWindow._counter
        self.desktop = desktop
        self.app = app
        self.canvas = desktop.canvas
        self.tag = f"win{self.uid}"
        self.chrome = f"chrome{self.uid}"

        self.x, self.y = int(x), int(y)
        self.w, self.h = int(width), int(height)
        self.minimized = False
        self.maximized = False
        self.active = False
        self._restore_geo: tuple[int, int, int, int] | None = None
        self._drag_offset: tuple[int, int] | None = None
        self._resize_origin: tuple[int, int, int, int] | None = None
        self._resize_edge: str | None = None

        theme = desktop.theme
        self.frame = tk.Frame(self.canvas, bg=theme["window"]["bg"],
                              bd=0, highlightthickness=0)
        self.content = self.canvas.create_window(
            0, 0, anchor="nw", window=self.frame, tags=(self.tag,)
        )

        app.window = self
        app.build(self.frame)

        self._place_content()
        self.redraw()

    # ------------------------------------------------------------------ düzen
    def _place_content(self) -> None:
        wt = self.desktop.theme["window"]
        pad = wt["pad"]
        tb = wt["titlebar"]
        self.frame.configure(bg=wt["bg"])
        self.canvas.coords(self.content, self.x + pad, self.y + tb + pad // 2)
        self.canvas.itemconfigure(
            self.content,
            width=max(160, self.w - pad * 2),
            height=max(100, self.h - tb - int(pad * 1.5)),
        )

    def set_geometry(self, x=None, y=None, w=None, h=None) -> None:
        if x is not None:
            self.x = int(x)
        if y is not None:
            self.y = int(y)
        if w is not None:
            self.w = int(w)
        if h is not None:
            self.h = int(h)
        self._place_content()
        self.redraw()

    # ------------------------------------------------------------------- çizim
    def redraw(self) -> None:
        if self.minimized:
            return

        c = self.canvas
        c.delete(self.chrome)

        wt = self.desktop.theme["window"]
        fonts = self.desktop.theme["fonts"]
        x, y, w, h = self.x, self.y, self.w, self.h
        r = wt["radius"]
        tb = wt["titlebar"]
        chrome = (self.chrome, self.tag)
        title_tags = (self.chrome, self.tag, f"{self.tag}-title")

        # gölge
        rounded(c, x + 4, y + 7, x + w + 4, y + h + 7, r,
                fill="#000000", outline="", stipple="gray75", tags=chrome)
        # gövde + kenarlık
        rounded(c, x, y, x + w, y + h, r, fill=wt["border"], outline="", tags=chrome)
        rounded(c, x + 1, y + 1, x + w - 1, y + h - 1, max(0, r - 1),
                fill=wt["bg"], outline="", tags=chrome)
        # başlık çubuğu
        title_bg = wt["title_bg"] if self.active else wt["title_bg_inactive"]
        title_fg = wt["title_fg"] if self.active else wt["title_fg_inactive"]
        rounded_top(c, x + 1, y + 1, x + w - 1, y + tb, max(0, r - 1),
                    fill=title_bg, outline="", tags=title_tags)
        c.create_line(x + 1, y + tb, x + w - 1, y + tb,
                      fill=wt["border"], tags=chrome)

        controls = wt["controls"]
        if controls == "mac":
            c.create_text(x + w / 2, y + tb / 2, text=self.app.title,
                          fill=title_fg, font=fonts["title"], anchor="center",
                          tags=title_tags)
        elif controls == "gnome":
            c.create_text(x + w / 2, y + tb / 2, text=self.app.title,
                          fill=title_fg, font=fonts["bold"], anchor="center",
                          tags=title_tags)
        else:
            c.create_text(x + 16, y + tb / 2, text=self.app.title,
                          fill=title_fg, font=fonts["title"], anchor="w",
                          tags=title_tags)

        self._draw_controls(controls, x, y, w, tb, wt, fonts, title_bg)
        self._draw_resize_zones(x, y, w, h, tb, wt)

        # içerik penceresinin altında kalsın
        c.tag_lower(self.chrome, self.content)

        # sürükleme (hareket olayları Desktop tarafından yakalanır)
        c.tag_bind(f"{self.tag}-title", "<Button-1>", self._drag_start)
        c.tag_bind(f"{self.tag}-title", "<Double-Button-1>", lambda e: self.toggle_maximize())

    def _draw_controls(self, controls, x, y, w, tb, wt, fonts, title_bg) -> None:
        c = self.canvas
        tag = self.tag

        if controls == "mac":
            cy = y + tb / 2
            for i, (name, color, action) in enumerate((
                ("close", "#ff5f57", self.close),
                ("min", "#febc2e", self.minimize),
                ("max", "#28c840", self.toggle_maximize),
            )):
                cx = x + 20 + i * 19
                item = c.create_oval(cx - 6, cy - 6, cx + 6, cy + 6,
                                     fill=color, outline="",
                                     tags=(self.chrome, self.tag, f"{tag}-{name}"))
                c.tag_bind(f"{tag}-{name}", "<Button-1>", lambda e, a=action: a())
                if name == "close":
                    c.tag_bind(f"{tag}-{name}", "<Enter>",
                               lambda e, it=item: c.itemconfig(it, fill="#ff8a84"))
                    c.tag_bind(f"{tag}-{name}", "<Leave>",
                               lambda e, it=item: c.itemconfig(it, fill="#ff5f57"))
            return

        if controls == "gnome":
            bx = x + w - 34
            by = y + tb / 2
            bg_item = rounded(c, bx - 15, by - 15, bx + 15, by + 15, 15,
                              fill=title_bg, outline="",
                              tags=(self.chrome, self.tag, f"{tag}-close"))
            self._x_glyph(bx, by, 5, wt["title_fg"],
                          (self.chrome, self.tag, f"{tag}-close-glyph", f"{tag}-close"))
            c.tag_bind(f"{tag}-close", "<Button-1>", lambda e: self.close())
            c.tag_bind(f"{tag}-close", "<Enter>",
                       lambda e: c.itemconfig(bg_item, fill=wt["danger"]))
            c.tag_bind(f"{tag}-close", "<Leave>",
                       lambda e: c.itemconfig(bg_item, fill=title_bg))
            return

        # Windows tarzı: sağ üstte üç kutu
        bw = 46
        start = x + w - bw * 3
        for i, (name, action) in enumerate((
            ("min", self.minimize), ("max", self.toggle_maximize), ("close", self.close),
        )):
            x1 = start + i * bw + 5
            y1 = y + 5
            x2 = start + (i + 1) * bw - 5
            y2 = y + tb - 5
            hover = wt["danger"] if name == "close" else lighten(title_bg, 0.16)
            item = rounded(c, x1, y1, x2, y2, 6, fill=title_bg, outline="",
                           tags=(self.chrome, self.tag, f"{tag}-{name}"))
            cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
            glyph_tag = (self.chrome, self.tag, f"{tag}-{name}-glyph", f"{tag}-{name}")
            if name == "min":
                c.create_line(cx - 5, cy + 1, cx + 5, cy + 1,
                              fill=wt["title_fg"], width=1, tags=glyph_tag)
            elif name == "max":
                c.create_rectangle(cx - 5, cy - 5, cx + 5, cy + 5,
                                   outline=wt["title_fg"], width=1, tags=glyph_tag)
            else:
                self._x_glyph(cx, cy, 5, wt["title_fg"], glyph_tag)

            c.tag_bind(f"{tag}-{name}", "<Button-1>", lambda e, a=action: a())
            c.tag_bind(f"{tag}-{name}", "<Enter>",
                       lambda e, it=item, f=hover: c.itemconfig(it, fill=f))
            c.tag_bind(f"{tag}-{name}", "<Leave>",
                       lambda e, it=item, f=title_bg: c.itemconfig(it, fill=f))

    def _x_glyph(self, cx, cy, size, color, tags) -> None:
        self.canvas.create_line(cx - size, cy - size, cx + size, cy + size,
                                fill=color, width=1, tags=tags)
        self.canvas.create_line(cx - size, cy + size, cx + size, cy - size,
                                fill=color, width=1, tags=tags)

    # ----------------------------------------------------------- boyutlandırma
    def _draw_resize_zones(self, x, y, w, h, tb, wt) -> None:
        """Sağ/bottom/alt-sağ kenarda görünmez boyutlandırma tutamaçları."""
        c = self.canvas
        inset = 4
        fill = wt["bg"]
        offset = RESIZE_ZONE + inset
        zones = {
            "r": (x + w - offset, y + tb + 2, x + w - inset, y + h - offset),
            "b": (x + inset, y + h - offset, x + w - offset, y + h - inset),
            "br": (x + w - offset, y + h - offset, x + w - inset, y + h - inset),
        }

        for edge, box in zones.items():
            zone_tag = f"{self.tag}-rz-{edge}"
            c.create_rectangle(*box, fill=fill, outline="",
                               tags=(self.chrome, self.tag, zone_tag))
            c.tag_bind(zone_tag, "<Button-1>",
                       lambda event, ed=edge: self._resize_start(event, ed))
            c.tag_bind(zone_tag, "<Enter>",
                       lambda event, ed=edge: self._set_cursor(RESIZE_CURSORS[ed]))
            c.tag_bind(zone_tag, "<Leave>", lambda event: self._set_cursor(""))

        # sağ alt köşede ince tutamaç çizgileri (tıklama da br bölgesine gider)
        br_tag = f"{self.tag}-rz-br"
        for first, second in (
            ((x + w - 14, y + h - 4), (x + w - 4, y + h - 14)),
            ((x + w - 10, y + h - 4), (x + w - 4, y + h - 10)),
        ):
            c.create_line(*first, *second, fill=wt["muted"], width=1,
                          tags=(self.chrome, self.tag, br_tag, f"{self.tag}-grip"))

    def _set_cursor(self, name: str) -> None:
        try:
            self.canvas.configure(cursor=name)
        except tk.TclError:
            pass

    def _resize_start(self, event, edge: str) -> None:
        self.desktop.focus_window(self)
        if self.maximized:
            self.toggle_maximize()
        self._drag_offset = None
        self._resize_edge = edge
        self._resize_origin = (event.x_root, event.y_root, self.w, self.h)
        self.desktop.begin_pointer_action(self, "resize", edge)
        self._set_cursor(RESIZE_CURSORS.get(edge, "sizing"))

    def _resize_move(self, event, edge: str | None = None) -> None:
        edge = edge or self._resize_edge
        if not edge or not self._resize_origin or self.minimized:
            return

        start_x, start_y, start_w, start_h = self._resize_origin
        dx = event.x_root - start_x
        dy = event.y_root - start_y
        max_w = max(MIN_WIDTH, self.desktop.width - self.x - 8)
        max_h = max(MIN_HEIGHT, self.desktop.height - self.y - 8)

        width, height = self.w, self.h
        if edge in ("r", "br"):
            width = max(MIN_WIDTH, min(start_w + dx, max_w))
        if edge in ("b", "br"):
            height = max(MIN_HEIGHT, min(start_h + dy, max_h))

        if (width, height) != (self.w, self.h):
            self.set_geometry(w=width, h=height)

    # ---------------------------------------------------------------- sürükleme
    def _drag_start(self, event) -> None:
        self.desktop.focus_window(self)
        self._resize_origin = None
        self._resize_edge = None
        self._drag_offset = (event.x_root - self.x, event.y_root - self.y)
        self.desktop.begin_pointer_action(self, "move")

    def _drag_move(self, event) -> None:
        if not self._drag_offset or self.minimized:
            return
        nx = event.x_root - self._drag_offset[0]
        ny = event.y_root - self._drag_offset[1]
        nx = max(-self.w + 120, min(nx, self.desktop.width - 120))
        ny = max(0, min(ny, self.desktop.height - 60))
        self.canvas.move(self.tag, nx - self.x, ny - self.y)
        self.x, self.y = nx, ny

    def end_pointer_action(self) -> None:
        """Fare bırakıldığında sürükleme/boyutlandırma durumunu temizler."""
        resized = self._resize_origin is not None
        self._drag_offset = None
        self._resize_origin = None
        self._resize_edge = None
        self._set_cursor("")
        if resized:
            self.redraw()

    # ------------------------------------------------------------------ eylemler
    def focus(self) -> None:
        self.desktop.focus_window(self)

    def set_active(self, active: bool) -> None:
        if self.active != active:
            self.active = active
            self.redraw()

    def raise_(self) -> None:
        self.canvas.tag_raise(self.tag)

    def minimize(self) -> None:
        self.minimized = True
        self.canvas.itemconfigure(self.tag, state="hidden")
        if self.desktop.active is self:
            self.desktop.active = None
        self.desktop.draw_panels()
        self.desktop.close_popup()

    def restore(self) -> None:
        self.minimized = False
        self.canvas.itemconfigure(self.tag, state="normal")
        self._place_content()
        self.redraw()

    def toggle_minimize(self) -> None:
        if self.minimized:
            self.restore()
            self.focus()
        else:
            self.minimize()

    def toggle_maximize(self) -> None:
        if self.desktop.active is not self:
            self.desktop.focus_window(self)
        if self.maximized and self._restore_geo:
            self.maximized = False
            self.set_geometry(*self._restore_geo)
        else:
            self._restore_geo = (self.x, self.y, self.w, self.h)
            self.maximized = True
            x1, y1, x2, y2 = self.desktop.useful_area()
            self.set_geometry(x1, y1, x2 - x1, y2 - y1)

    def close(self) -> None:
        self.desktop.close_window(self)

    def destroy(self) -> None:
        action = self.desktop._pointer_action
        if action and action[0] is self:
            self.desktop._pointer_action = None
        self._set_cursor("")
        self.canvas.delete(self.tag)
        try:
            self.frame.destroy()
        except tk.TclError:
            pass
