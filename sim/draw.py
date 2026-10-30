"""Canvas çizim yardımcıları."""

from __future__ import annotations


def rounded(canvas, x1, y1, x2, y2, r, **kwargs):
    """Köşeleri yuvarlatılmış dikdörtgen (polygon + smooth)."""
    r = max(0, min(r, (x2 - x1) / 2, (y2 - y1) / 2))
    if r <= 0.5:
        return canvas.create_rectangle(x1, y1, x2, y2, **kwargs)
    points = [
        x1 + r, y1, x2 - r, y1, x2, y1, x2, y1 + r,
        x2, y2 - r, x2, y2, x2 - r, y2, x1 + r, y2,
        x1, y2, x1, y2 - r, x1, y1 + r, x1, y1,
    ]
    return canvas.create_polygon(points, smooth=True, splinesteps=24, **kwargs)


def rounded_top(canvas, x1, y1, x2, y2, r, **kwargs):
    """Üst köşeleri yuvarlatılmış, alt köşeleri düz şekil."""
    r = max(0, min(r, (x2 - x1) / 2, (y2 - y1) / 2))
    points = [
        x1, y2,
        x1, y1 + r, x1, y1, x1 + r, y1,
        x2 - r, y1, x2, y1, x2, y1 + r,
        x2, y2,
    ]
    return canvas.create_polygon(points, smooth=True, splinesteps=24, **kwargs)


# ---------------------------------------------------------------- renk işlemleri
def hex_to_rgb(value: str) -> tuple[int, int, int]:
    value = value.lstrip("#")
    return tuple(int(value[i:i + 2], 16) for i in (0, 2, 4))


def rgb_to_hex(rgb) -> str:
    return "#%02x%02x%02x" % tuple(max(0, min(255, int(v))) for v in rgb)


def mix(color_a: str, color_b: str, t: float) -> str:
    """İki rengi t (0..1) oranında karıştırır."""
    a, b = hex_to_rgb(color_a), hex_to_rgb(color_b)
    return rgb_to_hex(tuple(a[i] + (b[i] - a[i]) * t for i in range(3)))


def lighten(color: str, amount: float) -> str:
    return mix(color, "#ffffff", amount)


def darken(color: str, amount: float) -> str:
    return mix(color, "#000000", amount)
