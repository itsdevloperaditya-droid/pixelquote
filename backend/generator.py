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
    # ---------------- batch 2: category expansion (22 new) ----------------
    "Stone": {
        "description": "Warm gray solid, calm minimal",
        "pro": False,
        "gradient": None,
        "solid": (231, 229, 228),
        "text_color": (41, 37, 36),
        "sub_color": (120, 113, 108),
        "accent": (87, 83, 78),
        "serif": False,
        "frame": None,
    },
    "Aurora": {
        "description": "Teal to violet aurora gradient",
        "pro": True,
        "gradient": [(19, 78, 74), (109, 40, 217)],
        "solid": None,
        "text_color": (255, 255, 255),
        "sub_color": (153, 246, 228),
        "accent": (94, 234, 212),
        "serif": False,
        "frame": None,
    },
    "Arcade": {
        "description": "Retro arcade cabinet, hot yellow frame",
        "pro": False,
        "gradient": None,
        "solid": (26, 16, 51),
        "text_color": (254, 252, 232),
        "sub_color": (250, 204, 21),
        "accent": (250, 204, 21),
        "serif": False,
        "frame": "accent",
    },
    "Bloodzone": {
        "description": "Black-red intense gaming",
        "pro": True,
        "gradient": None,
        "solid": (10, 10, 10),
        "text_color": (254, 226, 226),
        "sub_color": (239, 68, 68),
        "accent": (220, 38, 38),
        "serif": False,
        "frame": "accent",
    },
    "Venom": {
        "description": "Toxic purple to green gradient",
        "pro": False,
        "gradient": [(59, 7, 100), (5, 46, 22)],
        "solid": None,
        "text_color": (245, 243, 255),
        "sub_color": (163, 230, 53),
        "accent": (163, 230, 53),
        "serif": False,
        "frame": None,
    },
    "Executive": {
        "description": "Classic navy, premium serif",
        "pro": False,
        "gradient": None,
        "solid": (30, 58, 95),
        "text_color": (255, 255, 255),
        "sub_color": (191, 219, 254),
        "accent": (226, 232, 240),
        "serif": True,
        "frame": None,
    },
    "Rose": {
        "description": "Soft rose gradient, romantic serif",
        "pro": False,
        "gradient": [(255, 241, 242), (254, 205, 211)],
        "solid": None,
        "text_color": (136, 19, 55),
        "sub_color": (190, 18, 60),
        "accent": (225, 29, 72),
        "serif": True,
        "frame": None,
    },
    "Sky": {
        "description": "Clear sky blue gradient, fresh",
        "pro": False,
        "gradient": [(224, 242, 254), (186, 230, 253)],
        "solid": None,
        "text_color": (12, 74, 110),
        "sub_color": (2, 132, 199),
        "accent": (2, 132, 199),
        "serif": False,
        "frame": None,
    },
    "Marigold": {
        "description": "Festive marigold cream, gold frame",
        "pro": False,
        "gradient": None,
        "solid": (255, 251, 235),
        "text_color": (124, 45, 18),
        "sub_color": (180, 83, 9),
        "accent": (217, 119, 6),
        "serif": True,
        "frame": "accent",
    },
    "Henna": {
        "description": "Mehendi green, festive cream text",
        "pro": False,
        "gradient": None,
        "solid": (54, 83, 20),
        "text_color": (254, 252, 232),
        "sub_color": (217, 249, 157),
        "accent": (190, 242, 100),
        "serif": False,
        "frame": None,
    },
    "Diwali Night": {
        "description": "Diya glow, purple night to ember",
        "pro": True,
        "gradient": [(46, 16, 101), (124, 45, 18)],
        "solid": None,
        "text_color": (254, 243, 199),
        "sub_color": (252, 211, 77),
        "accent": (251, 191, 36),
        "serif": True,
        "frame": "accent",
    },
    "Ink & Paper": {
        "description": "Ink italic serif on soft paper",
        "pro": False,
        "gradient": None,
        "solid": (253, 252, 248),
        "text_color": (32, 26, 23),
        "sub_color": (87, 83, 78),
        "accent": (68, 64, 60),
        "serif": True,
        "italic": True,
        "frame": None,
    },
    "Old Letter": {
        "description": "Vintage sepia letter, italic serif",
        "pro": False,
        "gradient": None,
        "solid": (239, 230, 213),
        "text_color": (74, 47, 29),
        "sub_color": (138, 109, 79),
        "accent": (146, 64, 14),
        "serif": True,
        "italic": True,
        "frame": "accent",
    },
    "Gulab": {
        "description": "Deep rose gradient, ishq italic serif",
        "pro": True,
        "gradient": [(76, 5, 25), (157, 23, 77)],
        "solid": None,
        "text_color": (255, 241, 242),
        "sub_color": (253, 164, 175),
        "accent": (251, 113, 133),
        "serif": True,
        "italic": True,
        "frame": None,
    },
    "Midnight Shayari": {
        "description": "Indigo night, silver italic serif",
        "pro": True,
        "gradient": None,
        "solid": (49, 46, 129),
        "text_color": (226, 232, 240),
        "sub_color": (165, 180, 252),
        "accent": (196, 181, 253),
        "serif": True,
        "italic": True,
        "frame": "accent",
    },
    "Terminal Amber": {
        "description": "Amber terminal on warm black",
        "pro": False,
        "gradient": None,
        "solid": (12, 10, 9),
        "text_color": (254, 243, 199),
        "sub_color": (251, 191, 36),
        "accent": (245, 158, 11),
        "serif": False,
        "frame": "accent",
    },
    "Blueprint": {
        "description": "Engineer blueprint blue, thin frame",
        "pro": False,
        "gradient": None,
        "solid": (30, 64, 175),
        "text_color": (255, 255, 255),
        "sub_color": (191, 219, 254),
        "accent": (219, 234, 254),
        "serif": False,
        "frame": "light",
    },
    "Carbon": {
        "description": "Code-editor dark, orange accents",
        "pro": True,
        "gradient": [(17, 24, 39), (3, 7, 18)],
        "solid": None,
        "text_color": (243, 244, 246),
        "sub_color": (251, 146, 60),
        "accent": (249, 115, 22),
        "serif": False,
        "frame": None,
    },
    "Mono Light": {
        "description": "Light code theme, clean slate",
        "pro": False,
        "gradient": None,
        "solid": (248, 250, 252),
        "text_color": (15, 23, 42),
        "sub_color": (100, 116, 139),
        "accent": (14, 165, 233),
        "serif": False,
        "frame": None,
    },
    "Desert": {
        "description": "Warm desert sand gradient",
        "pro": False,
        "gradient": [(254, 243, 199), (253, 186, 116)],
        "solid": None,
        "text_color": (69, 26, 3),
        "sub_color": (154, 52, 18),
        "accent": (194, 65, 12),
        "serif": False,
        "frame": None,
    },
    "Glacier": {
        "description": "Glacier ice cyan, calm",
        "pro": False,
        "gradient": [(236, 254, 255), (207, 250, 254)],
        "solid": None,
        "text_color": (22, 78, 99),
        "sub_color": (14, 116, 144),
        "accent": (6, 182, 212),
        "serif": False,
        "frame": None,
    },
    "Sakura Night": {
        "description": "Night blossom, purple to magenta",
        "pro": True,
        "gradient": [(59, 7, 100), (131, 24, 67)],
        "solid": None,
        "text_color": (252, 231, 243),
        "sub_color": (249, 168, 212),
        "accent": (244, 114, 182),
        "serif": True,
        "frame": None,
    },
}

THEME_CATS = {
    "Minimal Light": "Minimal", "Mono Ink": "Minimal",
    "Cream Paper": "Minimal", "Stone": "Minimal",
    "Tech Dark": "Modern", "Ocean Depth": "Modern",
    "Lavender Mist": "Modern", "Aurora": "Modern",
    "Neon Matrix": "Gaming", "Arcade": "Gaming",
    "Bloodzone": "Gaming", "Venom": "Gaming",
    "Charcoal": "Professional", "Midnight": "Professional",
    "Executive": "Professional", "Crimson": "Professional",
    "Sunset Glow": "Beautiful", "Peach Glow": "Beautiful",
    "Rose": "Beautiful", "Sky": "Beautiful",
    "Royal Gold": "Traditional", "Marigold": "Traditional",
    "Henna": "Traditional", "Diwali Night": "Traditional",
    "Ink & Paper": "Poetry", "Old Letter": "Poetry",
    "Gulab": "Poetry", "Midnight Shayari": "Poetry",
    "Terminal Amber": "Technical", "Blueprint": "Technical",
    "Carbon": "Technical", "Mono Light": "Technical",
    "Forest Pine": "Nature", "Desert": "Nature",
    "Glacier": "Nature", "Sakura Night": "Nature",
}


def _candidate_fonts(serif: bool, bold: bool, italic: bool = False):
    if serif and italic:
        return [
            "C:/Windows/Fonts/georgiaz.ttf" if bold else "C:/Windows/Fonts/georgiai.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSerif-BoldItalic.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Italic.ttf",
        ]
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


def get_font(size: int, serif: bool = False, bold: bool = False, italic: bool = False):
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
    italic = theme.get("italic", False)
    main_font = get_font(font_size, serif=serif, bold=True, italic=italic)
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
        main_font = get_font(font_size, serif=serif, bold=True, italic=italic)
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
