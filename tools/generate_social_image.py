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
    # Modern gradient background - navy to darker navy
    base = Image.new("RGB", (WIDTH, HEIGHT), NAVY)
    draw = ImageDraw.Draw(base)
    
    # Radial gradient effect from center
    from math import sqrt
    center_x, center_y = WIDTH // 2, HEIGHT // 2
    max_dist = sqrt(center_x**2 + center_y**2)
    
    for y in range(0, HEIGHT, 3):
        for x in range(0, WIDTH, 3):
            dist = sqrt((x - center_x)**2 + (y - center_y)**2)
            factor = 1 - (dist / max_dist) * 0.4
            r = int(NAVY[0] * factor)
            g = int(NAVY[1] * factor)
            b = int(NAVY[2] * factor)
            draw.rectangle([x, y, x+3, y+3], fill=(r, g, b))
    
    # Decorative geometric elements
    draw.polygon([(WIDTH, 0), (WIDTH-200, 0), (WIDTH, 200)], fill=GREEN)
    draw.polygon([(0, HEIGHT), (0, HEIGHT-200), (200, HEIGHT)], fill=YELLOW)
    
    # Glowing circular accents
    draw.ellipse([600, -150, 1250, 500], outline=GREEN, width=3)
    draw.ellipse([-100, 550, 550, 1200], outline=YELLOW, width=3)
    
    # Logo at top - smaller to make room for text
    logo = load_logo()
    if logo:
        max_logo_w = 200
        ratio = max_logo_w / logo.width
        logo_h = int(logo.height * ratio)
        logo_resized = logo.resize((max_logo_w, logo_h), Image.LANCZOS)
        base.paste(logo_resized, ((WIDTH - max_logo_w) // 2, 60), logo_resized)
    
    # MAIN HOOK - Huge attention-grabbing headline
    hook_font = get_font(120)
    hook = "Your Health"
    hook2 = "Meets Web3"
    
    h_bbox = draw.textbbox((0, 0), hook, font=hook_font)
    h_w = h_bbox[2] - h_bbox[0]
    h_x = (WIDTH - h_w) / 2
    
    # Glow effect
    for offset in range(6, 0, -2):
        draw.text((h_x + offset//2, 230 + offset//2), hook, font=hook_font, fill=(0, 166, 81, 40))
    draw.text((h_x, 230), hook, font=hook_font, fill=(255, 255, 255))
    
    h2_bbox = draw.textbbox((0, 0), hook2, font=hook_font)
    h2_w = h2_bbox[2] - h2_bbox[0]
    h2_x = (WIDTH - h2_w) / 2
    
    for offset in range(6, 0, -2):
        draw.text((h2_x + offset//2, 360 + offset//2), hook2, font=hook_font, fill=(252, 211, 77, 40))
    draw.text((h2_x, 360), hook2, font=get_font(120), fill=GREEN)
    
    # Version badge - stylish
    badge_font = get_font(56)
    badge = "v1.1.1 NOW LIVE"
    b_bbox = draw.textbbox((0, 0), badge, font=badge_font)
    b_w = b_bbox[2] - b_bbox[0]
    b_x = (WIDTH - b_w - 60) / 2
    
    # Badge background
    draw.rounded_rectangle(
        [b_x - 30, 500, b_x + b_w + 30, 570],
        radius=35,
        fill=YELLOW
    )
    draw.text((b_x, 510), badge, font=badge_font, fill=NAVY)
    
    # Value proposition - clear benefits
    benefit_font = get_font(42)
    benefits = [
        "🔐  Secure Wallet Management",
        "⚡  Lightning Fast Transactions",
        "🎯  Track Calories, Earn Tokens"
    ]
    
    y_pos = 640
    for benefit in benefits:
        b_bbox = draw.textbbox((0, 0), benefit, font=benefit_font)
        b_w = b_bbox[2] - b_bbox[0]
        draw.text(
            ((WIDTH - b_w) / 2, y_pos),
            benefit,
            font=benefit_font,
            fill=(255, 255, 255),
        )
        y_pos += 75
    
    # Call to action
    cta_font = get_font(50)
    cta = "Join the Movement"
    cta_bbox = draw.textbbox((0, 0), cta, font=cta_font)
    cta_w = cta_bbox[2] - cta_bbox[0]
    cta_x = (WIDTH - cta_w - 80) / 2
    
    # CTA button background
    draw.rounded_rectangle(
        [cta_x - 40, 930, cta_x + cta_w + 40, 1000],
        radius=35,
        fill=GREEN,
        outline=(255, 255, 255),
        width=3
    )
    draw.text((cta_x, 940), cta, font=cta_font, fill=(255, 255, 255))
    
    # Footer with social
    footer_font = get_font(32)
    footer = "CalorieToken  •  #Web3Health  •  #DeFi"
    f_bbox = draw.textbbox((0, 0), footer, font=footer_font)
    f_w = f_bbox[2] - f_bbox[0]
    draw.text(
        ((WIDTH - f_w) / 2, HEIGHT - 70),
        footer,
        font=footer_font,
        fill=(180, 210, 255),
    )
    
    # Corner brackets
    bracket_size = 60
    bracket_width = 4
    draw.line([(40, 40), (40, 40+bracket_size)], fill=GREEN, width=bracket_width)
    draw.line([(40, 40), (40+bracket_size, 40)], fill=GREEN, width=bracket_width)
    draw.line([(WIDTH-40, HEIGHT-40), (WIDTH-40, HEIGHT-40-bracket_size)], fill=YELLOW, width=bracket_width)
    draw.line([(WIDTH-40, HEIGHT-40), (WIDTH-40-bracket_size, HEIGHT-40)], fill=YELLOW, width=bracket_width)

    # Save
    base.save(OUT_FILE, "PNG")
    print(f"Generated: {OUT_FILE}")

if __name__ == "__main__":
    main()
