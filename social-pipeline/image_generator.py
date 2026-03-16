#!/usr/bin/env python3
"""Generate tweet-style text card images for Instagram carousels.

Modeled after @yourchatgptguide — clean white background, bold black text,
logo/handle header. Fully automated, no manual design work needed.
"""

import textwrap
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

# Canvas settings
WIDTH = 1080
HEIGHT = 1080
BG_COLOR = "#FFFFFF"
TEXT_COLOR = "#1A1A1A"
SUBTLE_COLOR = "#888888"
ACCENT_COLOR = "#2563EB"  # Blue accent for highlighted text

# Font paths (adjust if you have custom fonts installed)
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_REGULAR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

OUTPUT_DIR = Path(__file__).parent / "output"


def _wrap_text(text: str, font: ImageFont.FreeTypeFont, max_width: int, draw: ImageDraw.Draw) -> list[str]:
    """Word-wrap text to fit within max_width pixels."""
    words = text.split()
    lines = []
    current_line = ""

    for word in words:
        test_line = f"{current_line} {word}".strip()
        bbox = draw.textbbox((0, 0), test_line, font=font)
        if bbox[2] - bbox[0] <= max_width:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line)
            current_line = word

    if current_line:
        lines.append(current_line)

    return lines


def generate_text_card(
    headline: str,
    body: str = "",
    handle: str = "@youraiaccount",
    account_name: str = "AI Tips & Tricks",
    slide_number: int | None = None,
    total_slides: int | None = None,
    output_path: str | None = None,
) -> Path:
    """Generate a single tweet-style text card image.

    Args:
        headline: Bold main text (the hook or key point)
        body: Optional supporting text below the headline
        handle: Social media handle shown in header
        account_name: Display name shown in header
        slide_number: Optional slide number for carousel
        total_slides: Optional total slide count
        output_path: Custom output path. Auto-generated if None.

    Returns:
        Path to the generated image file.
    """
    OUTPUT_DIR.mkdir(exist_ok=True)

    img = Image.new("RGB", (WIDTH, HEIGHT), BG_COLOR)
    draw = ImageDraw.Draw(img)

    margin = 80
    content_width = WIDTH - (margin * 2)

    # Fonts
    font_handle = ImageFont.truetype(FONT_BOLD, 28)
    font_username = ImageFont.truetype(FONT_REGULAR, 24)
    font_headline = ImageFont.truetype(FONT_BOLD, 52)
    font_body = ImageFont.truetype(FONT_REGULAR, 38)
    font_slide = ImageFont.truetype(FONT_REGULAR, 22)

    y = margin

    # --- Header: account name + handle ---
    # Draw a simple circle placeholder for logo
    logo_size = 56
    logo_x = margin
    logo_y = y
    draw.ellipse(
        [logo_x, logo_y, logo_x + logo_size, logo_y + logo_size],
        fill=TEXT_COLOR,
    )
    # "AI" text in the circle
    font_logo = ImageFont.truetype(FONT_BOLD, 22)
    logo_bbox = draw.textbbox((0, 0), "AI", font=font_logo)
    logo_text_w = logo_bbox[2] - logo_bbox[0]
    logo_text_h = logo_bbox[3] - logo_bbox[1]
    draw.text(
        (logo_x + (logo_size - logo_text_w) // 2, logo_y + (logo_size - logo_text_h) // 2 - 2),
        "AI",
        fill=BG_COLOR,
        font=font_logo,
    )

    text_x = logo_x + logo_size + 16
    draw.text((text_x, y + 2), account_name, fill=TEXT_COLOR, font=font_handle)
    draw.text((text_x, y + 32), handle, fill=SUBTLE_COLOR, font=font_username)

    # Slide counter (top right)
    if slide_number and total_slides:
        counter = f"{slide_number}/{total_slides}"
        counter_bbox = draw.textbbox((0, 0), counter, font=font_slide)
        counter_w = counter_bbox[2] - counter_bbox[0]
        draw.text(
            (WIDTH - margin - counter_w, y + 10),
            counter,
            fill=SUBTLE_COLOR,
            font=font_slide,
        )

    y += logo_size + 60

    # --- Headline ---
    headline_lines = _wrap_text(headline.upper(), font_headline, content_width, draw)
    for line in headline_lines:
        draw.text((margin, y), line, fill=TEXT_COLOR, font=font_headline)
        bbox = draw.textbbox((margin, y), line, font=font_headline)
        y += (bbox[3] - bbox[1]) + 16

    y += 30

    # --- Body text ---
    if body:
        body_lines = _wrap_text(body, font_body, content_width, draw)
        for line in body_lines:
            draw.text((margin, y), line, fill=TEXT_COLOR, font=font_body)
            bbox = draw.textbbox((margin, y), line, font=font_body)
            y += (bbox[3] - bbox[1]) + 12

    # --- Save ---
    if output_path:
        out = Path(output_path)
    else:
        name = f"slide_{slide_number or 1}.png"
        out = OUTPUT_DIR / name

    img.save(out, "PNG")
    return out


def generate_carousel(slides: list[dict], **kwargs) -> list[Path]:
    """Generate all slides for a carousel.

    Args:
        slides: List of dicts with 'headline' and optional 'body' keys.
        **kwargs: Passed to generate_text_card (handle, account_name, etc.)

    Returns:
        List of paths to generated slide images.
    """
    total = len(slides)
    paths = []
    for i, slide in enumerate(slides, 1):
        path = generate_text_card(
            headline=slide["headline"],
            body=slide.get("body", ""),
            slide_number=i,
            total_slides=total,
            **kwargs,
        )
        paths.append(path)
    return paths


# --- Quick test ---
if __name__ == "__main__":
    test_slides = [
        {"headline": "5 AI Tools You're Sleeping On", "body": ""},
        {"headline": "Perplexity AI", "body": "Like Google, but it actually answers your question. No ads, no fluff."},
        {"headline": "NotebookLM", "body": "Paste any article, PDF, or YouTube link. It gives you a full summary in seconds."},
        {"headline": "Gamma", "body": "Turns a one-line idea into a full slide deck. Presentation prep in 2 minutes."},
        {"headline": "Ideogram", "body": "Free AI image generator that actually gets text right. Logos, thumbnails, social posts."},
        {"headline": "Save this. Try one tonight.", "body": "You don't need to be technical. You just need to start."},
    ]

    paths = generate_carousel(test_slides, handle="@youraiaccount", account_name="AI Tips & Tricks")
    for p in paths:
        print(f"Generated: {p}")
