"""Duvar kağıdı üretimi (Pillow varsa yumuşak gradyan, yoksa canvas)."""

from __future__ import annotations

from .draw import hex_to_rgb, mix

try:  # Pillow opsiyonel
    from PIL import Image, ImageDraw, ImageFilter, ImageTk
    HAS_PIL = True
except ImportError:  # pragma: no cover
    HAS_PIL = False


def _sample(stops: list[str], pos: float) -> str:
    pos = max(0.0, min(1.0, pos))
    if len(stops) == 1:
        return stops[0]
    span = 1 / (len(stops) - 1)
    index = min(len(stops) - 2, int(pos / span))
    local = (pos - index * span) / span
    return mix(stops[index], stops[index + 1], local)


def make_image(width: int, height: int, spec: dict) -> "Image.Image":
    width, height = max(1, width), max(1, height)
    image = Image.new("RGB", (width, height))
    draw = ImageDraw.Draw(image)

    stops = spec.get("stops", ["#101018", "#1c2340"])
    for y in range(height):
        draw.line([(0, y), (width, y)], fill=hex_to_rgb(_sample(stops, y / (height - 1))))

    for blob in spec.get("blobs", []):
        cx = blob["center"][0] * width
        cy = blob["center"][1] * height
        radius = blob["radius"] * max(width, height)
        color = hex_to_rgb(blob.get("color", "#ffffff"))
        alpha = int(blob.get("alpha", 80))

        layer = Image.new("RGB", image.size, color)
        mask = Image.new("L", image.size, 0)
        ImageDraw.Draw(mask).ellipse(
            [cx - radius, cy - radius, cx + radius, cy + radius], fill=alpha
        )
        mask = mask.filter(ImageFilter.GaussianBlur(radius * 0.65))
        image = Image.composite(layer, image, mask)

    return image


def draw_wallpaper(canvas, width: int, height: int, spec: dict, tags=("wallpaper",)):
    """Duvar kağıdını çizer ve referansı döndürür (PhotoImage canlı tutulmalı)."""
    if HAS_PIL:
        image = make_image(width, height, spec)
        photo = ImageTk.PhotoImage(image)
        canvas.create_image(0, 0, image=photo, anchor="nw", tags=tags)
        return photo

    # Pillow yok: yatay şeritler + yumuşak daireler
    stops = spec.get("stops", ["#101018", "#1c2340"])
    step = max(2, height // 160)
    for y in range(0, height, step):
        canvas.create_rectangle(
            0, y, width, y + step,
            fill=_sample(stops, y / max(1, height - 1)), outline="", tags=tags,
        )
    for blob in spec.get("blobs", []):
        cx = blob["center"][0] * width
        cy = blob["center"][1] * height
        r = blob["radius"] * max(width, height)
        canvas.create_oval(
            cx - r, cy - r, cx + r, cy + r,
            fill=blob.get("color", "#ffffff"), outline="",
            stipple="gray50", tags=tags,
        )
    return None
