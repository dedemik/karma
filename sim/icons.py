"""Uygulama ikonları: canvas üzerine çizilen vektörel kutucuklar."""

from __future__ import annotations

import math

from .draw import lighten, rounded

TILE_COLORS = {
    "files": "#f0b429",
    "notes": "#5b8cff",
    "calc": "#2fc4a4",
    "terminal": "#22262f",
    "settings": "#7d879b",
    "about": "#a07bff",
}

GLYPH = "#ffffff"


def draw_app_icon(canvas, app_id: str, x: float, y: float, size: float,
                  tags=(), mono_family: str = "DejaVu Sans Mono") -> int:
    """(x, y) sol üst köşe olacak şekilde yuvarlak köşeli uygulama ikonu çizer."""
    color = TILE_COLORS.get(app_id, "#5b8cff")
    s = float(size)

    # gövde
    rounded(canvas, x, y, x + s, y + s, s * 0.26, fill=color, outline="", tags=tags)
    # üst ışık
    rounded(canvas, x + 1, y + 1, x + s - 1, y + s * 0.55, s * 0.24,
            fill="", outline=lighten(color, 0.18), tags=tags)

    def px(fx):
        return x + s * fx

    def py(fy):
        return y + s * fy

    if app_id == "files":
        points = [
            px(0.18), py(0.36), px(0.43), py(0.36), px(0.49), py(0.29),
            px(0.82), py(0.29), px(0.82), py(0.72), px(0.18), py(0.72),
        ]
        canvas.create_polygon(points, fill=GLYPH, outline="",
                              smooth=False, tags=tags)
        canvas.create_line(px(0.22), py(0.47), px(0.78), py(0.47),
                           fill=color, width=max(1, int(s * 0.05)), tags=tags)
    elif app_id == "notes":
        rounded(canvas, px(0.29), py(0.19), px(0.71), py(0.81), s * 0.06,
                fill=GLYPH, outline="", tags=tags)
        for i, fy in enumerate((0.34, 0.46, 0.58, 0.70)):
            width = 0.30 if i < 3 else 0.18
            canvas.create_line(px(0.35), py(fy), px(0.35 + width), py(fy),
                               fill=color, width=max(1, int(s * 0.04)), tags=tags)
    elif app_id == "calc":
        rounded(canvas, px(0.24), py(0.20), px(0.76), py(0.80), s * 0.08,
                fill=GLYPH, outline="", tags=tags)
        rounded(canvas, px(0.30), py(0.27), px(0.70), py(0.40), s * 0.03,
                fill=color, outline="", tags=tags)
        for row in range(3):
            for col in range(3):
                cx = px(0.34 + col * 0.16)
                cy = py(0.50 + row * 0.10)
                r = s * 0.025
                canvas.create_oval(cx - r, cy - r, cx + r, cy + r,
                                   fill=color, outline="", tags=tags)
    elif app_id == "terminal":
        canvas.create_text(px(0.5), py(0.52), text=">_", fill=GLYPH,
                           font=(mono_family, max(7, int(s * 0.28)), "bold"),
                           tags=tags)
    elif app_id == "settings":
        r_out, r_in = s * 0.30, s * 0.15
        for i in range(8):
            angle = math.radians(i * 45)
            x1 = px(0.5) + math.cos(angle) * r_in
            y1 = py(0.5) + math.sin(angle) * r_in
            x2 = px(0.5) + math.cos(angle) * r_out
            y2 = py(0.5) + math.sin(angle) * r_out
            canvas.create_line(x1, y1, x2, y2, fill=GLYPH,
                               width=max(2, int(s * 0.10)), capstyle="round", tags=tags)
        rr = s * 0.13
        canvas.create_oval(px(0.5) - rr, py(0.5) - rr, px(0.5) + rr, py(0.5) + rr,
                           outline=GLYPH, width=max(2, int(s * 0.07)), tags=tags)
    elif app_id == "about":
        rr = s * 0.30
        canvas.create_oval(px(0.5) - rr, py(0.5) - rr, px(0.5) + rr, py(0.5) + rr,
                           outline=GLYPH, width=max(2, int(s * 0.06)), tags=tags)
        canvas.create_text(px(0.5), py(0.5), text="i", fill=GLYPH,
                           font=(mono_family, max(8, int(s * 0.34)), "bold"), tags=tags)
    return color
