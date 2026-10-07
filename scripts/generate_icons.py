"""Generate PWA icons (runs once, needs Pillow)."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

OUT = Path(__file__).resolve().parent.parent / "static" / "images"


def make_icon(size, fname):
    img = Image.new("RGB", (size, size), "#0d1321")
    d = ImageDraw.Draw(img)
    # gradient-ish bands (dark navy -> blue)
    for i in range(size):
        r = int(13 + (11 - 13) * i / size)
        g = int(19 + (59 - 19) * i / size)
        b = int(33 + (143 - 33) * i / size)
        d.line([(0, i), (size, i)], fill=(r, g, b))
    m = size // 8
    # white plate
    d.ellipse([m, m, size - m, size - m], fill="#ffffff")
    # orange bowl
    b = size // 5
    d.ellipse([b, b, size - b, size - b], fill="#f59e0b")
    d.ellipse([b + size // 14, b + size // 20, size - b - size // 14, size - b - size // 6],
              fill="#ef4444")
    # green garnish dots
    r = max(2, size // 60)
    for cx, cy in [(0.42, 0.44), (0.55, 0.40), (0.50, 0.52), (0.60, 0.50)]:
        x, y = int(size * cx), int(size * cy)
        d.ellipse([x - r, y - r, x + r, y + r], fill="#16a34a")
    # MM text
    try:
        font = ImageFont.load_default(size=max(12, size // 6))
    except TypeError:
        font = ImageFont.load_default()
    txt = "MESS"
    box = d.textbbox((0, 0), txt, font=font)
    d.text(((size - (box[2] - box[0])) / 2, size * 0.74), txt, font=font, fill="#ffffff")
    OUT.mkdir(parents=True, exist_ok=True)
    img.save(OUT / fname)
    print("wrote", OUT / fname)


if __name__ == "__main__":
    make_icon(192, "icon-192.png")
    make_icon(512, "icon-512.png")
    make_icon(180, "apple-touch-icon.png")
    make_icon(32, "favicon.png")
