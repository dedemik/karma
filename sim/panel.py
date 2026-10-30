"""Paneller: görev çubuğu, menü çubuğu, dock, başlat menüsü ve sistem menüsü."""

from __future__ import annotations

import time
from tkinter import font as tkfont

from .apps import APP_CLASSES, APP_ORDER
from .draw import lighten, rounded, rounded_top
from .icons import draw_app_icon
from .themes import THEME_ORDER, THEMES

DAYS = ["Pzt", "Sal", "Çar", "Per", "Cum", "Cmt", "Paz"]
MONTHS = ["Oca", "Şub", "Mar", "Nis", "May", "Haz", "Tem", "Ağu", "Eyl", "Eki", "Kas", "Ara"]

# panel ikonuna gelince açılan pencere önizlemesi
PREVIEW_DELAY = 400
PREVIEW_HIDE_DELAY = 220
PREVIEW_W = 216
PREVIEW_H = 118


def clock_texts(style: str) -> tuple[str, str]:
    now = time.localtime()
    hm = time.strftime("%H:%M", now)
    long_date = f"{DAYS[now.tm_wday]} {now.tm_mday} {MONTHS[now.tm_mon - 1]}"
    if style == "taskbar":
        return hm, time.strftime("%d.%m.%Y", now)
    if style == "menubar":
        return f"{long_date}  {hm}", ""
    return f"{long_date}  {hm}", ""


# ------------------------------------------------------------------ genel çizim
def draw_panels(desktop) -> None:
    canvas = desktop.canvas
    canvas.delete("panel")
    theme = desktop.theme
    style = theme["panel"]["style"]

    if style == "taskbar":
        _taskbar(desktop)
    elif style == "menubar":
        _menubar(desktop)
    elif style == "gnome":
        _gnome_bar(desktop)

    if theme.get("dock"):
        _dock(desktop, theme["dock"])

    canvas.tag_raise("panel")


def _app_button(desktop, app_id: str, x: float, y: float, size: float,
                base_bg: str, hover_bg: str, dot_y: float | None = None) -> None:
    canvas = desktop.canvas
    theme = desktop.theme
    window = desktop.window_for(app_id)
    tag = f"papp-{app_id}"

    pill = rounded(canvas, x - 6, y - 6, x + size + 6, y + size + 6, 9,
                   fill=base_bg, outline="", tags=("panel",))
    draw_app_icon(canvas, app_id, x, y, size,
                  tags=("panel", tag), mono_family=theme["fonts"]["mono"][0])

    if dot_y is not None:
        color = theme["panel"]["accent"] if window and window is desktop.active else (
            theme["panel"]["fg"] if window else base_bg)
        if window:
            canvas.create_oval(x + size / 2 - 2, dot_y, x + size / 2 + 2, dot_y + 4,
                               fill=color, outline="", tags=("panel",))

    canvas.tag_bind(tag, "<Enter>", lambda _e: (
        canvas.itemconfig(pill, fill=hover_bg),
        schedule_preview(desktop, app_id, x, y, size),
    ))
    canvas.tag_bind(tag, "<Leave>", lambda _e: (
        canvas.itemconfig(pill, fill=base_bg),
        schedule_preview_hide(desktop, app_id),
    ))
    canvas.tag_bind(tag, "<Button-1>", lambda _e: desktop.activate_app(app_id))


# ------------------------------------------------------------------ önizleme
def schedule_preview(desktop, app_id: str, x: float, y: float, size: float) -> None:
    """İmleç panel ikonunda bekleyince kısa bir gecikmeyle kart açar."""
    desktop.cancel_preview()
    if desktop.window_for(app_id) is None:
        desktop._preview_target = None
        return
    desktop._preview_target = app_id
    desktop._preview_anchor = (float(x), float(y), float(size))

    def show() -> None:
        desktop.preview_job = None
        # Gecikme dolmadan imleç ikondan ayrıldıysa kart açma
        if desktop._preview_target != app_id:
            return
        show_preview(desktop, app_id)

    desktop.preview_job = desktop.root.after(PREVIEW_DELAY, show)


def schedule_preview_hide(desktop, app_id: str | None = None) -> None:
    """İkon ya da karttan çıkınca kartı kısa gecikmeyle kaldırır.

    Bekleyen gösterim hemen iptal edilmez; gösterim anında hedef uygulama hâlâ
    aynıysa kart açılır. Böylece silinen bir kartın ardından gelen gecikmiş
    <Leave> olayı yeni bir önizlemeyi bozamaz.
    """
    if app_id is None or desktop._preview_target == app_id:
        desktop._preview_target = None

    canvas = desktop.canvas
    if not canvas.find_withtag("preview"):
        return

    job = desktop.preview_hide_job
    if job:
        try:
            desktop.root.after_cancel(job)
        except Exception:
            pass
        desktop.preview_hide_job = None

    def hide() -> None:
        desktop.preview_hide_job = None
        if desktop._preview_target is not None:
            return
        desktop.cancel_preview()

    desktop.preview_hide_job = desktop.root.after(PREVIEW_HIDE_DELAY, hide)


def _preview_click(desktop, app_id: str) -> None:
    desktop._preview_target = None
    desktop.cancel_preview()
    win = desktop.window_for(app_id)
    if win is not None:
        desktop.focus_window(win)


def show_preview(desktop, app_id: str) -> None:
    """Pencerenin küçük bir kart önizlemesini panel ikonunun üstüne çizer."""
    win = desktop.window_for(app_id)
    if win is None:
        return
    desktop.cancel_preview()

    canvas = desktop.canvas
    theme = desktop.theme
    wt = theme["window"]
    fonts = theme["fonts"]
    panel = theme["panel"]

    ax, ay, size = desktop._preview_anchor
    x1 = ax + size / 2 - PREVIEW_W / 2
    x1 = max(8.0, min(x1, desktop.width - PREVIEW_W - 8.0))
    y1 = ay - 12 - PREVIEW_H
    if y1 < 8:
        y1 = ay + size + 12
    x2, y2 = x1 + PREVIEW_W, y1 + PREVIEW_H
    tags = ("preview",)

    # kart
    rounded(canvas, x1 + 4, y1 + 6, x2 + 4, y2 + 6, 12,
            fill="#000000", outline="", stipple="gray75", tags=tags)
    rounded(canvas, x1, y1, x2, y2, 12, fill=wt["border"], outline="", tags=tags)
    rounded(canvas, x1 + 1, y1 + 1, x2 - 1, y2 - 1, 11,
            fill=panel["bg"], outline="", tags=tags)

    # minyatür pencere
    mx1, my1, mx2, my2 = x1 + 10, y1 + 10, x2 - 10, y2 - 30
    rounded(canvas, mx1, my1, mx2, my2, 8, fill=wt["border"], outline="", tags=tags)
    rounded(canvas, mx1 + 1, my1 + 1, mx2 - 1, my2 - 1, 7,
            fill=wt["field"], outline="", tags=tags)
    rounded_top(canvas, mx1 + 1, my1 + 1, mx2 - 1, my1 + 17, 7,
                fill=wt["title_bg"], outline="", tags=tags)
    for index, color in enumerate(("#ff5f57", "#febc2e", "#28c840")):
        cx = mx1 + 11 + index * 9
        canvas.create_oval(cx - 2, my1 + 7, cx + 2, my1 + 11,
                           fill=color, outline="", tags=tags)
    for index in range(3):
        line_y = my1 + 27 + index * 9
        canvas.create_line(mx1 + 10, line_y, mx2 - (10 + index * 16), line_y,
                           fill=lighten(wt["field"], 0.22), width=3,
                           capstyle="round", tags=tags)

    active = win is desktop.active
    status = "Etkin" if active else ("Küçültüldü" if win.minimized else "Açık")
    canvas.create_text(x1 + 12, y2 - 15, text=APP_CLASSES[app_id].title, anchor="w",
                       fill=panel["fg"], font=fonts["small"], tags=tags)
    canvas.create_text(x2 - 12, y2 - 15, text=status, anchor="e",
                       fill=panel["accent"] if active else panel["muted"],
                       font=fonts["small"], tags=tags)

    canvas.tag_raise("preview")
    def card_enter(_event) -> None:
        desktop._preview_target = app_id
        desktop.cancel_preview_jobs()

    canvas.tag_bind("preview", "<Enter>", card_enter)
    canvas.tag_bind("preview", "<Leave>",
                    lambda _e: schedule_preview_hide(desktop, app_id))
    canvas.tag_bind("preview", "<Button-1>", lambda _e: _preview_click(desktop, app_id))


def _win_logo(canvas, cx: float, cy: float, size: float, color: str, tags) -> None:
    s = size * 0.40
    gap = size * 0.10
    start = cx - (2 * s + gap) / 2
    for col in range(2):
        for row in range(2):
            x = start + col * (s + gap)
            y = cy - (2 * s + gap) / 2 + row * (s + gap)
            canvas.create_rectangle(x, y, x + s, y + s,
                                    fill=color, outline="", tags=tags)


def _apple(canvas, cx: float, cy: float, bg: str, tags) -> None:
    r = 5.5
    canvas.create_oval(cx - r, cy - r + 1, cx + r, cy + r + 1,
                       fill="#f4f4f7", outline="", tags=tags)
    canvas.create_polygon(cx + 1, cy - r - 2, cx + 6, cy - r - 6, cx + 5, cy - r + 1,
                          fill="#f4f4f7", outline="", smooth=True, tags=tags)
    canvas.create_oval(cx + r - 3, cy - 2, cx + r + 4, cy + 6,
                       fill=bg, outline="", tags=tags)


def _power(canvas, cx: float, cy: float, color: str, tags) -> None:
    r = 6
    canvas.create_arc(cx - r, cy - r, cx + r, cy + r, start=300, extent=300,
                      style="arc", outline=color, width=2, tags=tags)
    canvas.create_line(cx, cy - r - 1, cx, cy - 1, fill=color, width=2, tags=tags)


# --------------------------------------------------------------------- görev çubuğu
def _taskbar(desktop) -> None:
    canvas = desktop.canvas
    theme = desktop.theme
    panel = theme["panel"]
    fonts = theme["fonts"]
    w, h = desktop.width, desktop.height
    ph = panel["height"]
    y1 = h - ph

    canvas.create_rectangle(0, y1, w, y1 + 1, fill=panel["border"],
                            outline="", tags=("panel",))
    canvas.create_rectangle(0, y1 + 1, w, h, fill=panel["bg"],
                            outline="", tags=("panel",))

    # başlat düğmesi solda
    lx, ly = 18, y1 + (ph - 40) // 2
    pill = rounded(canvas, lx, ly, lx + 40, ly + 40, 8,
                   fill=panel["bg"], outline="", tags=("panel", "plaunch"))
    _win_logo(canvas, lx + 20, ly + 20, 22, "#4a9dff", ("panel", "plaunch"))
    canvas.tag_bind("plaunch", "<Enter>", lambda _e: canvas.itemconfig(pill, fill=lighten(panel["bg"], 0.14)))
    canvas.tag_bind("plaunch", "<Leave>", lambda _e: canvas.itemconfig(pill, fill=panel["bg"]))
    canvas.tag_bind("plaunch", "<Button-1>", lambda _e: desktop.toggle_launcher())

    # ortada uygulama ikonları
    size, gap = 30, 14
    total = len(APP_ORDER) * size + (len(APP_ORDER) - 1) * gap
    start = (w - total) / 2
    dot_y = y1 + ph - 8
    for index, app_id in enumerate(APP_ORDER):
        _app_button(desktop, app_id, start + index * (size + gap),
                    y1 + (ph - size) / 2, size, panel["bg"],
                    lighten(panel["bg"], 0.14), dot_y)

    # saat + tarih sağda
    clock, date = clock_texts("taskbar")
    canvas.create_text(w - 26, y1 + ph / 2 - 8, text=clock, anchor="e",
                       fill=panel["fg"], font=fonts["bold"],
                       tags=("panel", "panel-clock", "psys"))
    canvas.create_text(w - 26, y1 + ph / 2 + 9, text=date, anchor="e",
                       fill=panel["muted"], font=fonts["small"],
                       tags=("panel", "panel-date", "psys"))
    canvas.tag_bind("psys", "<Button-1>", lambda _e: desktop.open_system_menu())


# -------------------------------------------------------------------- menü çubuğu
def _menubar(desktop) -> None:
    canvas = desktop.canvas
    theme = desktop.theme
    panel = theme["panel"]
    fonts = theme["fonts"]
    w = desktop.width
    ph = panel["height"]
    cy = ph / 2

    canvas.create_rectangle(0, 0, w, ph, fill=panel["bg"], outline="", tags=("panel",))
    canvas.create_line(0, ph, w, ph, fill=panel["border"], tags=("panel",))

    _apple(canvas, 20, cy, panel["bg"], ("panel", "plaunch"))
    canvas.tag_bind("plaunch", "<Button-1>", lambda _e: desktop.toggle_launcher())

    canvas.create_text(34, cy, text=theme["label"], anchor="w",
                       fill=panel["fg"], font=fonts["bold"], tags=("panel",))

    measure = tkfont.Font(family=fonts["small"][0], size=fonts["small"][1])
    x = 34 + measure.measure(theme["label"]) + 24
    for label in ("Dosya", "Düzen", "Görünüm", "Yardım"):
        canvas.create_text(x, cy, text=label, anchor="w",
                           fill=panel["muted"], font=fonts["small"], tags=("panel",))
        x += measure.measure(label) + 20

    clock, _ = clock_texts("menubar")
    canvas.create_text(w - 16, cy, text=clock, anchor="e",
                       fill=panel["fg"], font=fonts["small"],
                       tags=("panel", "panel-clock"))
    canvas.create_text(w - 190, cy, text=theme["label"], anchor="e",
                       fill=panel["muted"], font=fonts["small"], tags=("panel", "psys"))
    canvas.tag_bind("psys", "<Button-1>", lambda _e: desktop.open_system_menu())


# ------------------------------------------------------------------------ GNOME
def _gnome_bar(desktop) -> None:
    canvas = desktop.canvas
    theme = desktop.theme
    panel = theme["panel"]
    fonts = theme["fonts"]
    w = desktop.width
    ph = panel["height"]
    cy = ph / 2

    canvas.create_rectangle(0, 0, w, ph, fill=panel["bg"], outline="", tags=("panel",))

    canvas.create_text(14, cy, text="Etkinlikler", anchor="w",
                       fill=panel["fg"], font=fonts["bold"], tags=("panel", "plaunch"))
    canvas.tag_bind("plaunch", "<Button-1>", lambda _e: desktop.toggle_launcher())

    clock, _ = clock_texts("gnome")
    canvas.create_text(w / 2, cy, text=clock, anchor="center",
                       fill=panel["fg"], font=fonts["small"],
                       tags=("panel", "panel-clock"))

    canvas.create_text(w - 34, cy, text=theme["label"], anchor="e",
                       fill=panel["muted"], font=fonts["small"], tags=("panel", "psys"))
    _power(canvas, w - 18, cy, panel["fg"], ("panel", "psys"))
    canvas.tag_bind("psys", "<Button-1>", lambda _e: desktop.open_system_menu())


# ------------------------------------------------------------------------- dock
def _dock(desktop, dock: dict) -> None:
    canvas = desktop.canvas
    w, h = desktop.width, desktop.height
    size = dock["icon"]
    gap = 14
    pad = 14
    count = len(APP_ORDER)
    dock_w = count * size + (count - 1) * gap + pad * 2
    x1 = (w - dock_w) / 2
    y2 = h - dock["margin"]
    y1 = y2 - dock["height"]

    rounded(canvas, x1 + 4, y1 + 6, x1 + dock_w + 4, y2 + 6, dock["radius"],
            fill="#000000", outline="", stipple="gray75", tags=("panel",))
    rounded(canvas, x1, y1, x1 + dock_w, y2, dock["radius"],
            fill=dock["border"], outline="", tags=("panel",))
    rounded(canvas, x1 + 1, y1 + 1, x1 + dock_w - 1, y2 - 1, dock["radius"] - 1,
            fill=dock["bg"], outline="", tags=("panel",))

    dot_y = y2 - 8
    for index, app_id in enumerate(APP_ORDER):
        x = x1 + pad + index * (size + gap)
        y = y1 + (dock["height"] - size) / 2 - 2
        _app_button(desktop, app_id, x, y, size, dock["bg"],
                    lighten(dock["bg"], 0.14), dot_y)


# ------------------------------------------------------------------- başlat menüsü
def open_launcher(desktop) -> None:
    canvas = desktop.canvas
    desktop.close_popup()
    theme = desktop.theme
    panel = theme["panel"]
    fonts = theme["fonts"]
    w, h = desktop.width, desktop.height

    cols, rows = 3, 2
    tile_w, tile_h = 122, 108
    pad = 18
    box_w = cols * tile_w + pad * 2
    box_h = 50 + rows * tile_h + pad // 2

    x1 = (w - box_w) / 2
    if panel["position"] == "bottom":
        y2 = h - panel["height"] - 12
        y1 = y2 - box_h
    else:
        y1 = panel["height"] + 12
        y2 = y1 + box_h

    radius = 16
    rounded(canvas, x1 + 5, y1 + 7, x1 + box_w + 5, y1 + box_h + 7, radius,
            fill="#000000", outline="", stipple="gray75", tags=("popup",))
    rounded(canvas, x1, y1, x1 + box_w, y1 + box_h, radius,
            fill=theme["window"]["border"], outline="", tags=("popup",))
    rounded(canvas, x1 + 1, y1 + 1, x1 + box_w - 1, y1 + box_h - 1, radius - 1,
            fill=panel["bg"], outline="", tags=("popup",))
    canvas.create_text(x1 + pad, y1 + 27, text="Uygulamalar", anchor="w",
                       fill=panel["fg"], font=fonts["title"], tags=("popup",))

    for index, app_id in enumerate(APP_ORDER):
        col, row = index % cols, index // cols
        tx = x1 + pad + col * tile_w
        ty = y1 + 50 + row * tile_h
        tag = f"ltile-{app_id}"

        hover = rounded(canvas, tx + 2, ty + 2, tx + tile_w - 2, ty + tile_h - 10, 12,
                        fill=panel["bg"], outline="", tags=("popup", tag))
        draw_app_icon(canvas, app_id, tx + (tile_w - 44) / 2, ty + 10, 44,
                      tags=("popup", tag), mono_family=fonts["mono"][0])
        canvas.create_text(tx + tile_w / 2, ty + tile_h - 28,
                           text=APP_CLASSES[app_id].title, fill=panel["fg"],
                           font=fonts["small"], tags=("popup", tag))

        canvas.tag_bind(tag, "<Enter>",
                        lambda _e, it=hover: canvas.itemconfig(it, fill=lighten(panel["bg"], 0.15)))
        canvas.tag_bind(tag, "<Leave>",
                        lambda _e, it=hover: canvas.itemconfig(it, fill=panel["bg"]))
        canvas.tag_bind(tag, "<Button-1>",
                        lambda _e, a=app_id: (desktop.close_popup(), desktop.open_app(a)))

    desktop.popup = True
    canvas.tag_raise("popup")


# ------------------------------------------------------------------- sistem menüsü
def open_system_menu(desktop) -> None:
    canvas = desktop.canvas
    desktop.close_popup()
    theme = desktop.theme
    panel = theme["panel"]
    fonts = theme["fonts"]
    w, h = desktop.width, desktop.height

    box_w = 300
    row_h = 38
    header = 46
    box_h = header + len(THEME_ORDER) * row_h + 14 + 2 * row_h + 12
    x2 = w - 14
    x1 = x2 - box_w
    if panel["position"] == "bottom":
        y2 = h - panel["height"] - 10
        y1 = y2 - box_h
    else:
        y1 = panel["height"] + 10
        y2 = y1 + box_h

    radius = 14
    rounded(canvas, x1 + 5, y1 + 7, x1 + box_w + 5, y1 + box_h + 7, radius,
            fill="#000000", outline="", stipple="gray75", tags=("popup",))
    rounded(canvas, x1, y1, x1 + box_w, y1 + box_h, radius,
            fill=theme["window"]["border"], outline="", tags=("popup",))
    rounded(canvas, x1 + 1, y1 + 1, x1 + box_w - 1, y1 + box_h - 1, radius - 1,
            fill=panel["bg"], outline="", tags=("popup",))
    canvas.create_text(x1 + 18, y1 + 25, text="Sistem", anchor="w",
                       fill=panel["fg"], font=fonts["title"], tags=("popup",))

    def row(tag: str, y: float, label: str, action, accent: str | None = None,
            check: bool = False) -> None:
        hover = rounded(canvas, x1 + 8, y, x1 + box_w - 8, y + row_h - 6, 8,
                        fill=panel["bg"], outline="", tags=("popup", tag))
        if check:
            canvas.create_oval(x1 + 22, y + row_h / 2 - 9, x1 + 32, y + row_h / 2 + 1,
                               outline=panel["accent"], width=2, tags=("popup", tag))
            canvas.create_oval(x1 + 25, y + row_h / 2 - 6, x1 + 29, y + row_h / 2 - 2,
                               fill=panel["accent"], outline="", tags=("popup", tag))
        canvas.create_text(x1 + 44, y + row_h / 2 - 3, text=label, anchor="w",
                           fill=accent or panel["fg"], font=fonts["base"],
                           tags=("popup", tag))
        canvas.tag_bind(tag, "<Enter>",
                        lambda _e, it=hover: canvas.itemconfig(it, fill=lighten(panel["bg"], 0.15)))
        canvas.tag_bind(tag, "<Leave>",
                        lambda _e, it=hover: canvas.itemconfig(it, fill=panel["bg"]))
        canvas.tag_bind(tag, "<Button-1>", lambda _e: action())

    y = y1 + header
    for theme_id in THEME_ORDER:
        row(f"sysrow-theme-{theme_id}", y, THEMES[theme_id]["label"],
            lambda t=theme_id: desktop.set_theme(t),
            check=(theme_id == desktop.theme_id))
        y += row_h

    canvas.create_line(x1 + 14, y + 6, x1 + box_w - 14, y + 6,
                       fill=panel["border"], tags=("popup",))
    y += 12

    row("sysrow-fullscreen", y, "Tam ekranı değiştir", desktop.toggle_fullscreen)
    y += row_h
    row("sysrow-quit", y, "Çıkış", desktop.quit_app, accent=theme["window"]["danger"])

    desktop.popup = True
    canvas.tag_raise("popup")
