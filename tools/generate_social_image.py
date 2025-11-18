"""Generate a branded 1080x1080 social image with CalorieApp logo and headline.

Usage:
  python tools/generate_social_image.py

Outputs:
  assets/social-media/2025-11-18-docs-update/square-1080x1080.png (overwrites)

If Pillow is missing:
  pip install pillow

Logo selection:
  Tries CalorieAppLogoTranspa.png then CalorieLogoTranspa.png in assets/images.
"""

from pathlib import Path
from datetime import datetime

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    raise SystemExit("Pillow not installed. Run: pip install pillow")

OUT_DIR = Path("assets/social-media/2025-11-18-docs-update")
OUT_DIR.mkdir(parents=True, exist_ok=True)
OUT_FILE = OUT_DIR / "square-1080x1080.png"

LOGO_DIR = Path("assets/images")
LOGO_CANDIDATES = ["CalorieAppLogoTranspa.png", "CalorieLogoTranspa.png"]

# Brand colors
NAVY = (30, 58, 138)      # #1E3A8A
GREEN = (0, 166, 81)      # #00A651
YELLOW = (252, 211, 77)   # #FCD34D

WIDTH = HEIGHT = 1080

def load_logo() -> Image.Image | None:
    for name in LOGO_CANDIDATES:
        p = LOGO_DIR / name
        if p.exists():
            try:
                return Image.open(p).convert("RGBA")
            except Exception:
                pass
    return None

def get_font(size: int) -> ImageFont.FreeTypeFont:
    # Try common fonts; fallback to default.
    for candidate in ["Montserrat-Bold.ttf", "Poppins-Bold.ttf", "Arial.ttf", "DejaVuSans-Bold.ttf"]:
        try:
            return ImageFont.truetype(candidate, size)
        except Exception:
            continue
    return ImageFont.load_default()

def main():
    base = Image.new("RGB", (WIDTH, HEIGHT), NAVY)
    draw = ImageDraw.Draw(base)

    # Background accent ring
    ring_margin = 90
    draw.ellipse(
        [ring_margin, ring_margin, WIDTH - ring_margin, HEIGHT - ring_margin],
        outline=GREEN,
        width=8,
    )

    # Subtle diagonal lines pattern
    for x in range(0, WIDTH, 140):
        draw.line([(x, 0), (x - 200, HEIGHT)], fill=(40, 75, 160), width=2)

    logo = load_logo()
    if logo:
        # Resize logo proportionally
        max_logo_w = 260
        ratio = max_logo_w / logo.width
        logo_h = int(logo.height * ratio)
        logo_resized = logo.resize((max_logo_w, logo_h), Image.LANCZOS)
        base.paste(logo_resized, (60, 60), logo_resized)
    else:
        # Fallback simple emblem
        draw.rectangle([60, 60, 320, 320], outline=GREEN, width=6)
        draw.text((80, 170), "CT", font=get_font(120), fill=GREEN)

    headline_font = get_font(92)
    sub_font = get_font(44)
    foot_font = get_font(30)

    headline = "CalorieApp Upgrade"
    subline = "Security  •  Speed  •  UX"
    # Center headline area
    head_w, head_h = draw.textbbox((0, 0), headline, font=headline_font)[2:]
    draw.text(
        ((WIDTH - head_w) / 2, HEIGHT / 2 - 140),
        headline,
        font=headline_font,
        fill=GREEN,
    )
    sub_w, sub_h = draw.textbbox((0, 0), subline, font=sub_font)[2:]
    draw.text(
        ((WIDTH - sub_w) / 2, HEIGHT / 2 - 40),
        subline,
        font=sub_font,
        fill=YELLOW,
    )

    footer = f"Docs & UX Hardening • {datetime.now().date()}"
    foot_w, foot_h = draw.textbbox((0, 0), footer, font=foot_font)[2:]
    draw.text(
        ((WIDTH - foot_w) / 2, HEIGHT - 140),
        footer,
        font=foot_font,
        fill=(200, 210, 230),
    )

    # Save
    base.save(OUT_FILE, "PNG")
    print(f"Generated: {OUT_FILE}")

if __name__ == "__main__":
    main()
