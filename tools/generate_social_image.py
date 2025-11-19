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
    """Return a scalable TrueType font of the requested size.

    Tries project fonts, Windows fonts, and Pillow-bundled DejaVu before
    falling back to bitmap default (last resort).
    """
    import os
    import PIL

    candidates: list[str] = []

    # 1) Project-local fonts (if you add any later)
    assets_fonts = Path("assets/fonts")
    if assets_fonts.exists():
        for name in [
            "Inter-Black.ttf",
            "Poppins-ExtraBold.ttf",
            "Montserrat-ExtraBold.ttf",
            "Montserrat-Bold.ttf",
            "Poppins-Bold.ttf",
        ]:
            p = assets_fonts / name
            if p.exists():
                candidates.append(str(p))

    # 2) Common names (if resolvable on PATH)
    candidates += [
        "Montserrat-Bold.ttf",
        "Poppins-Bold.ttf",
        "Arial.ttf",
        "arial.ttf",
        "arialbd.ttf",
        "Verdana.ttf",
        "verdana.ttf",
        "verdanab.ttf",
        "SegoeUI-Bold.ttf",
        "segoeuib.ttf",
        "DejaVuSans-Bold.ttf",
        "DejaVuSans.ttf",
    ]

    # 3) Windows Fonts directory (explicit paths)
    windir = os.environ.get("WINDIR") or os.environ.get("SystemRoot")
    if windir:
        fonts_dir = os.path.join(windir, "Fonts")
        for name in [
            "arialbd.ttf",
            "arial.ttf",
            "verdanab.ttf",
            "verdana.ttf",
            "segoeuib.ttf",
            "segoeui.ttf",
        ]:
            p = os.path.join(fonts_dir, name)
            if os.path.exists(p):
                candidates.append(p)

    # 4) Pillow bundled DejaVu
    try:
        pil_fonts_dir = os.path.join(os.path.dirname(PIL.__file__), "fonts")
        for name in ["DejaVuSans-Bold.ttf", "DejaVuSans.ttf"]:
            p = os.path.join(pil_fonts_dir, name)
            if os.path.exists(p):
                candidates.append(p)
    except Exception:
        pass

    tried = []
    for cand in candidates:
        try:
            return ImageFont.truetype(cand, size)
        except Exception as e:
            tried.append((cand, str(e)))
            continue

    # Last resort
    return ImageFont.load_default()

def main():
    """Generate extremely large, high-impact text covering most of the image."""
    base = Image.new("RGB", (WIDTH, HEIGHT), NAVY)
    draw = ImageDraw.Draw(base)

    # Very subtle center lightening for depth (performance-friendly)
    from math import sqrt
    cx, cy = WIDTH // 2, HEIGHT // 2
    max_d = sqrt(cx**2 + cy**2)
    for y in range(0, HEIGHT, 8):
        for x in range(0, WIDTH, 8):
            d = sqrt((x - cx)**2 + (y - cy)**2)
            fade = 1 - (d / max_d) * 0.18
            r = int(NAVY[0] * fade)
            g = int(NAVY[1] * fade)
            b = int(NAVY[2] * fade)
            draw.rectangle([x, y, x+8, y+8], fill=(r, g, b))

    # Helper: fit font size to width
    def fit_font(text: str, target_w: int, base_size: int = 100) -> ImageFont.FreeTypeFont:
        size = base_size
        font = get_font(size)
        # Measure once
        w = draw.textbbox((0, 0), text, font=font)[2]
        # If too large, shrink until fits
        if w > target_w:
            while size > 20:
                size -= 4
                font = get_font(size)
                w = draw.textbbox((0, 0), text, font=font)[2]
                if w <= target_w:
                    break
            return font
        # Else grow until close to target
        while size < 420:
            size += 4
            next_font = get_font(size)
            w2 = draw.textbbox((0, 0), text, font=next_font)[2]
            if w2 >= target_w * 0.98:
                return next_font if w2 <= target_w else font
            font = next_font
        return font

    # Huge lines
    line1 = "YOUR HEALTH"
    line2 = "MEETS WEB3"
    l1_font = fit_font(line1, WIDTH - 80, 160)
    l2_font = fit_font(line2, WIDTH - 80, 160)

    l1_box = draw.textbbox((0, 0), line1, font=l1_font)
    l2_box = draw.textbbox((0, 0), line2, font=l2_font)
    total_h = (l1_box[3]-l1_box[1]) + (l2_box[3]-l2_box[1]) + 140
    start_y = (HEIGHT - total_h) / 2 - 20

    # Line 1 with soft glow
    l1_w = l1_box[2]-l1_box[0]
    base_x1 = (WIDTH - l1_w)/2
    for o in range(14, 0, -4):
        draw.text((base_x1 + o/2, start_y + o/2), line1, font=l1_font, fill=(0,166,81,35))
    draw.text((base_x1, start_y), line1, font=l1_font, fill=(255,255,255))

    # Line 2 with inverse glow
    l2_w = l2_box[2]-l2_box[0]
    y2 = start_y + (l1_box[3]-l1_box[1]) + 140
    base_x2 = (WIDTH - l2_w)/2
    for o in range(14, 0, -4):
        draw.text((base_x2 + o/2, y2 + o/2), line2, font=l2_font, fill=(252,211,77,40))
    draw.text((base_x2, y2), line2, font=l2_font, fill=GREEN)

    # Version badge stretched wide
    badge = "v1.1.1  •  NOW LIVE"
    badge_font = fit_font(badge, WIDTH - 140, 90)
    b_box = draw.textbbox((0,0), badge, font=badge_font)
    b_w = b_box[2]-b_box[0]
    b_h = b_box[3]-b_box[1]
    badge_y = y2 + (l2_box[3]-l2_box[1]) + 110
    draw.rounded_rectangle([
        (WIDTH - b_w - 160)/2,
        badge_y,
        (WIDTH + b_w + 160)/2,
        badge_y + b_h + 90
    ], radius=65, fill=YELLOW)
    draw.text(((WIDTH - b_w)/2, badge_y + 40), badge, font=badge_font, fill=NAVY)

    # Footer
    footer = "#CalorieApp  #Web3Health"
    foot_font = get_font(60)
    f_box = draw.textbbox((0,0), footer, font=foot_font)
    f_w = f_box[2]-f_box[0]
    draw.text(((WIDTH - f_w)/2, HEIGHT - 180), footer, font=foot_font, fill=(170,190,215))

    base.save(OUT_FILE, "PNG")
    print(f"Generated: {OUT_FILE}\nLine widths: {l1_w}, {l2_w}")

if __name__ == "__main__":
    main()
