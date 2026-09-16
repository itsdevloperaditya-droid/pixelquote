"""Pure Pillow 1080x1080 renderer — shared by FastAPI backend (no Streamlit dep)."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

APP_NAME = "PixelQuote"
CANVAS_SIZE = 1080

THEMES = {
    # ---------------- FREE (6) ----------------
    "Tech Dark": {
        "description": "Deep purple/blue gradient, white sans",
        "pro": False,
        "gradient": [(30, 27, 75), (109, 40, 217)],
        "solid": None,
        "text_color": (255, 255, 255),
        "sub_color": (203, 213, 225),
        "accent": (167, 139, 250),
        "serif": False,
        "frame": None,
    },
    "Minimal Light": {
        "description": "Off-white, black serif",
        "pro": False,
        "gradient": None,
        "solid": (250, 249, 246),
        "text_color": (17, 17, 17),
        "sub_color": (100, 100, 100),
        "accent": (17, 17, 17),
        "serif": True,
        "frame": "light",
    },
    "Ocean Depth": {
        "description": "Deep navy to teal, cyan accents",
        "pro": False,
        "gradient": [(12, 74, 110), (14, 116, 144)],
        "solid": None,
        "text_color": (255, 255, 255),
        "sub_color": (165, 243, 252),
        "accent": (103, 232, 249),
        "serif": False,
        "frame": None,
    },
    "Cream Paper": {
        "description": "Warm cream, coffee-brown serif",
        "pro": False,
        "gradient": None,
        "solid": (245, 239, 224),
        "text_color": (63, 50, 38),
        "sub_color": (138, 122, 99),
        "accent": (180, 83, 9),
        "serif": True,
        "frame": None,
    },
    "Charcoal": {
        "description": "Soft black solid, clean grey text",
        "pro": False,
        "gradient": None,
        "solid": (31, 41, 55),
        "text_color": (249, 250, 251),
        "sub_color": (156, 163, 175),
        "accent": (229, 231, 235),
        "serif": False,
        "frame": None,
    },
    "Lavender Mist": {
        "description": "Soft lavender gradient, deep purple",
        "pro": False,
        "gradient": [(237, 233, 254), (196, 181, 253)],
        "solid": None,
        "text_color": (46, 16, 101),
        "sub_color": (109, 40, 217),
        "accent": (124, 58, 237),
        "serif": False,
        "frame": None,
    },
    # ---------------- PRO (8) ----------------
    "Sunset Glow": {
        "description": "Warm orange/pink gradient, white",
        "pro": True,
        "gradient": [(255, 81, 47), (221, 36, 118)],
        "solid": None,
        "text_color": (255, 255, 255),
        "sub_color": (255, 228, 230),
        "accent": (255, 255, 255),
        "serif": False,
        "frame": None,
    },
    "Neon Matrix": {
        "description": "Black + neon green accent",
        "pro": True,
        "gradient": None,
        "solid": (0, 0, 0),
        "text_color": (255, 255, 255),
        "sub_color": (57, 255, 20),
        "accent": (57, 255, 20),
        "serif": False,
        "frame": "neon",
    },
    "Royal Gold": {
        "description": "Black-gold luxury, serif + gold frame",
        "pro": True,
        "gradient": [(12, 10, 9), (69, 26, 3)],
        "solid": None,
        "text_color": (254, 243, 199),
        "sub_color": (214, 169, 79),
        "accent": (251, 191, 36),
        "serif": True,
        "frame": "accent",
    },
    "Forest Pine": {
        "description": "Deep green gradient, fresh mint",
        "pro": True,
        "gradient": [(5, 46, 22), (22, 101, 52)],
        "solid": None,
        "text_color": (240, 253, 244),
        "sub_color": (187, 247, 208),
        "accent": (74, 222, 128),
        "serif": False,
        "frame": None,
    },
    "Crimson": {
        "description": "Dark maroon to red, bold serif",
        "pro": True,
        "gradient": [(69, 10, 10), (185, 28, 28)],
        "solid": None,
        "text_color": (255, 255, 255),
        "sub_color": (254, 202, 202),
        "accent": (252, 165, 165),
        "serif": True,
        "frame": None,
    },
    "Mono Ink": {
        "description": "Pure white, black frame, editorial",
        "pro": True,
        "gradient": None,
        "solid": (255, 255, 255),
        "text_color": (0, 0, 0),
        "sub_color": (82, 82, 82),
        "accent": (0, 0, 0),
        "serif": False,
        "frame": "accent",
    },
    "Midnight": {
        "description": "Near-black blue, sky neon frame",
        "pro": True,
        "gradient": None,
        "solid": (2, 6, 23),
        "text_color": (226, 232, 240),
        "sub_color": (56, 189, 248),
        "accent": (56, 189, 248),
        "serif": False,
        "frame": "accent",
    },
    "Peach Glow": {
        "description": "Soft peach to pink, warm dark text",
        "pro": True,
        "gradient": [(255, 237, 213), (249, 168, 212)],
        "solid": None,
        "text_color": (67, 20, 7),
        "sub_color": (154, 52, 18),
        "accent": (234, 88, 12),
        "serif": False,
        "frame": None,
    },
}


def _candidate_fonts(serif: bool, bold: bool):
    if serif:
        return [
            "C:/Windows/Fonts/georgiab.ttf" if bold else "C:/Windows/Fonts/georgia.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
            "C:/Windows/Fonts/timesbd.ttf" if bold else "C:/Windows/Fonts/times.ttf",
        ]
    return [
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]


def get_font(size: int, serif: bool = False, bold: bool = False):
    for path in _candidate_fonts(serif, bold):
        if Path(path).exists():
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue
    try:
        return ImageFont.truetype("arial.ttf", size)
    except Exception:
        return ImageFont.load_default()


def vertical_gradient(size, top, bottom):
    img = Image.new("RGB", (size, size), top)
    draw = ImageDraw.Draw(img)
    for y in range(size):
        t = y / (size - 1)
        r = int(top[0] + (bottom[0] - top[0]) * t)
        g = int(top[1] + (bottom[1] - top[1]) * t)
        b = int(top[2] + (bottom[2] - top[2]) * t)
        draw.line([(0, y), (size, y)], fill=(r, g, b))
    return img


def add_soft_glow(base: Image.Image, color=(255, 255, 255), alpha=28):
    s = base.size[0]
    overlay = Image.new("RGBA", base.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    d.ellipse([-s * 0.35, -s * 0.35, s * 0.55, s * 0.55], fill=color + (alpha,))
    d.ellipse([s * 0.45, s * 0.45, s * 1.35, s * 1.35], fill=color + (alpha,))
    return Image.alpha_composite(base.convert("RGBA"), overlay).convert("RGB")


def wrap_lines(text: str, draw, font, max_width: int):
    words = text.split()
    lines, current = [], ""
    for w in words:
        trial = (current + " " + w).strip()
        if draw.textlength(trial, font=font) <= max_width:
            current = trial
        else:
            if current:
                lines.append(current)
            current = w
            while draw.textlength(current, font=font) > max_width and len(current) > 1:
                for i in range(len(current) - 1, 0, -1):
                    if draw.textlength(current[:i] + "-", font=font) <= max_width:
                        lines.append(current[:i] + "-")
                        current = current[i:]
                        break
                else:
                    break
    if current:
        lines.append(current)
    return lines or [""]


def render_graphic(text: str, author_name: str = "", handle: str = "",
                   show_author: bool = True, theme_name: str = "Tech Dark",
                   font_size: int = 62, show_watermark: bool = True) -> Image.Image:
    theme = THEMES.get(theme_name, THEMES["Tech Dark"])
    S = CANVAS_SIZE

    if theme["gradient"]:
        img = vertical_gradient(S, theme["gradient"][0], theme["gradient"][1])
        img = add_soft_glow(img, color=(255, 255, 255), alpha=26)
    else:
        img = Image.new("RGB", (S, S), theme["solid"])

    draw = ImageDraw.Draw(img)

    frame = theme.get("frame")
    if frame == "neon":
        neon = theme["accent"]
        draw.rounded_rectangle([36, 36, S - 36, S - 36], radius=28, outline=neon, width=10)
        draw.rounded_rectangle([58, 58, S - 58, S - 58], radius=20, outline=neon, width=3)
    elif frame == "light":
        draw.rounded_rectangle([36, 36, S - 36, S - 36], radius=24, outline=(225, 225, 225), width=4)
    elif frame == "accent":
        draw.rounded_rectangle([48, 48, S - 48, S - 48], radius=20, outline=theme["accent"], width=5)

    serif = theme["serif"]
    main_font = get_font(font_size, serif=serif, bold=True)
    quote_font = get_font(180, serif=True, bold=True)
    author_font = get_font(44, serif=False, bold=True)
    handle_font = get_font(38, serif=False, bold=False)
    watermark_font = get_font(28, serif=False, bold=False)

    text_color = theme["text_color"]
    sub_color = theme["sub_color"]
    accent = theme["accent"]

    q = "\u201c"
    qb = draw.textbbox((0, 0), q, font=quote_font)
    qw = qb[2] - qb[0]
    draw.text(((S - qw) / 2, 120), q, font=quote_font, fill=accent)

    padding_x = 120
    max_w = S - padding_x * 2
    display_text = text.strip() if text.strip() else "Your words, beautifully styled."
    lines = wrap_lines(display_text, draw, main_font, max_w)

    line_heights, line_widths = [], []
    for ln in lines:
        bb = draw.textbbox((0, 0), ln, font=main_font)
        line_widths.append(bb[2] - bb[0])
        line_heights.append((bb[3] - bb[1]) + 18)
    total_h = sum(line_heights)

    while total_h > 560 and font_size > 32:
        font_size -= 4
        main_font = get_font(font_size, serif=serif, bold=True)
        lines = wrap_lines(display_text, draw, main_font, max_w)
        line_heights, line_widths = [], []
        for ln in lines:
            bb = draw.textbbox((0, 0), ln, font=main_font)
            line_widths.append(bb[2] - bb[0])
            line_heights.append((bb[3] - bb[1]) + 18)
        total_h = sum(line_heights)

    y = 500 - total_h / 2
    for ln, lh, lw in zip(lines, line_heights, line_widths):
        draw.text(((S - lw) / 2, y), ln, font=main_font, fill=text_color)
        y += lh

    if show_author and (author_name.strip() or handle.strip()):
        ay = 500 + total_h / 2 + 60
        draw.rounded_rectangle([S / 2 - 40, ay, S / 2 + 40, ay + 6], radius=3, fill=accent)
        ay += 28
        if author_name.strip():
            bb = draw.textbbox((0, 0), author_name.strip(), font=author_font)
            draw.text(((S - (bb[2] - bb[0])) / 2, ay), author_name.strip(),
                      font=author_font, fill=text_color)
            ay += (bb[3] - bb[1]) + 12
        if handle.strip():
            h = handle.strip()
            if not h.startswith("@"):
                h = "@" + h
            bb = draw.textbbox((0, 0), h, font=handle_font)
            draw.text(((S - (bb[2] - bb[0])) / 2, ay), h, font=handle_font, fill=sub_color)

    if show_watermark:
        wm = f"Made with {APP_NAME}"
        bb = draw.textbbox((0, 0), wm, font=watermark_font)
        ww = bb[2] - bb[0]
        draw.text((S - ww - 60, S - (bb[3] - bb[1]) - 60), wm, font=watermark_font, fill=sub_color)

    return img
