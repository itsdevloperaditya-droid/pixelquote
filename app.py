"""
Text-to-Graphic Generator (Micro-SaaS)
Option B: Streamlit + Pillow — $0 cost, no AI image APIs.

Run with:
    python -m streamlit run app.py
"""

import io
import textwrap
from pathlib import Path

import streamlit as st
from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------------------
# Page config + styling
# ---------------------------------------------------------------------------
APP_NAME = "PixelQuote"

st.set_page_config(
    page_title=f"{APP_NAME} — Text-to-Graphic Generator",
    page_icon="🎨",
    layout="wide",
)

st.markdown(
    """
    <style>
    .stApp { background: #0f1117; }
    [data-testid="stSidebar"] { background: #161a23; }
    h1, h2, h3 { letter-spacing: -0.02em; }
    .theme-card {
        border-radius: 14px;
        padding: 14px 10px;
        text-align: center;
        font-weight: 700;
        font-size: 14px;
        margin-bottom: 4px;
    }
    .pro-badge {
        background: #f59e0b;
        color: #000;
        font-size: 11px;
        font-weight: 800;
        border-radius: 20px;
        padding: 2px 8px;
        margin-left: 6px;
    }
    div.stDownloadButton > button {
        background: linear-gradient(90deg, #7c3aed, #ec4899);
        color: white;
        font-weight: 800;
        font-size: 18px;
        border-radius: 12px;
        padding: 14px 20px;
        border: none;
        width: 100%;
    }
    div.stDownloadButton > button:hover { filter: brightness(1.1); color: white; }
    </style>
    """,
    unsafe_allow_html=True,
)

CANVAS_SIZE = 1080

THEMES = {
    "Tech Dark": {
        "description": "Deep purple/blue gradient, white sans",
        "pro": False,
        "gradient": [(30, 27, 75), (109, 40, 217)],  # #1e1b4b -> #6d28d9
        "solid": None,
        "text_color": (255, 255, 255),
        "sub_color": (203, 213, 225),
        "accent": (167, 139, 250),
        "serif": False,
        "border": None,
    },
    "Minimal Light": {
        "description": "Off-white, black serif",
        "pro": False,
        "gradient": None,
        "solid": (250, 249, 246),  # #FAF9F6
        "text_color": (17, 17, 17),
        "sub_color": (100, 100, 100),
        "accent": (17, 17, 17),
        "serif": True,
        "border": (230, 230, 230),
    },
    "Sunset Glow": {
        "description": "Warm orange/pink gradient, white",
        "pro": True,
        "gradient": [(255, 81, 47), (221, 36, 118)],  # #FF512F -> #DD2476
        "solid": None,
        "text_color": (255, 255, 255),
        "sub_color": (255, 228, 230),
        "accent": (255, 255, 255),
        "serif": False,
        "border": None,
    },
    "Neon Matrix": {
        "description": "Black + neon green accent",
        "pro": True,
        "gradient": None,
        "solid": (0, 0, 0),
        "text_color": (255, 255, 255),
        "sub_color": (57, 255, 20),
        "accent": (57, 255, 20),  # #39FF14
        "serif": False,
        "border": (57, 255, 20),
    },
}


# ---------------------------------------------------------------------------
# Fonts — cross-platform (Windows local + Streamlit Cloud Linux)
# ---------------------------------------------------------------------------
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
    # Fallback: PIL default (fixed size, but never crashes)
    try:
        return ImageFont.truetype("arial.ttf", size)
    except Exception:
        return ImageFont.load_default()


# ---------------------------------------------------------------------------
# Image generation (1080x1080)
# ---------------------------------------------------------------------------
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
    """Adds two large translucent circles for a premium gradient feel."""
    s = base.size[0]
    overlay = Image.new("RGBA", base.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    # top-left glow
    d.ellipse([-s * 0.35, -s * 0.35, s * 0.55, s * 0.55], fill=color + (alpha,))
    # bottom-right glow
    d.ellipse([s * 0.45, s * 0.45, s * 1.35, s * 1.35], fill=color + (alpha,))
    return Image.alpha_composite(base.convert("RGBA"), overlay).convert("RGB")


def wrap_lines(text: str, draw: ImageDraw.ImageDraw, font: ImageFont.FreeTypeFont, max_width: int):
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
            # hard-break a single超-long word
            while draw.textlength(current, font=font) > max_width and len(current) > 1:
                # binary-ish cut
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


def render_graphic(text: str, author_name: str, handle: str, show_author: bool,
                   theme_name: str, font_size: int) -> Image.Image:
    theme = THEMES[theme_name]
    S = CANVAS_SIZE

    # --- background ---
    if theme["gradient"]:
        img = vertical_gradient(S, theme["gradient"][0], theme["gradient"][1])
        img = add_soft_glow(img, color=(255, 255, 255), alpha=26)
    else:
        img = Image.new("RGB", (S, S), theme["solid"])

    draw = ImageDraw.Draw(img)

    # --- Neon / Minimal borders ---
    if theme_name == "Neon Matrix":
        neon = theme["accent"]
        # outer + inner neon frame
        draw.rounded_rectangle([36, 36, S - 36, S - 36], radius=28, outline=neon, width=10)
        draw.rounded_rectangle([58, 58, S - 58, S - 58], radius=20, outline=neon, width=3)
    elif theme_name == "Minimal Light":
        draw.rounded_rectangle([36, 36, S - 36, S - 36], radius=24, outline=(225, 225, 225), width=4)

    # --- fonts ---
    serif = theme["serif"]
    main_font = get_font(font_size, serif=serif, bold=True)
    quote_font = get_font(180, serif=True, bold=True)
    author_font = get_font(44, serif=False, bold=True)
    handle_font = get_font(38, serif=False, bold=False)
    watermark_font = get_font(28, serif=False, bold=False)

    text_color = theme["text_color"]
    sub_color = theme["sub_color"]
    accent = theme["accent"]

    # --- decorative opening quote ---
    # centered, translucent
    q = "\u201c"
    # Pillow has no opacity on RGB draw; emulate by blending color toward bg
    qb = draw.textbbox((0, 0), q, font=quote_font)
    qw = qb[2] - qb[0]
    draw.text(((S - qw) / 2, 120), q, font=quote_font, fill=accent)

    # --- main text (centered block) ---
    padding_x = 120
    max_w = S - padding_x * 2
    display_text = text.strip() if text.strip() else "Your words, beautifully styled."
    lines = wrap_lines(display_text, draw, main_font, max_w)

    # measure block
    line_heights, line_widths = [], []
    for ln in lines:
        bb = draw.textbbox((0, 0), ln, font=main_font)
        line_widths.append(bb[2] - bb[0])
        line_heights.append((bb[3] - bb[1]) + 18)  # line spacing
    total_h = sum(line_heights)

    # auto-shrink if overflow (keeps 1080 canvas safe for long text)
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

    # vertical center around y=500 (leaves room for author + watermark)
    y = 500 - total_h / 2
    for ln, lh, lw in zip(lines, line_heights, line_widths):
        draw.text(((S - lw) / 2, y), ln, font=main_font, fill=text_color)
        y += lh

    # --- author block ---
    if show_author and (author_name.strip() or handle.strip()):
        ay = 500 + total_h / 2 + 60
        # small accent divider
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

    # --- watermark (free-tier monetization hook) ---
    wm = f"Made with {APP_NAME}"
    bb = draw.textbbox((0, 0), wm, font=watermark_font)
    ww = bb[2] - bb[0]
    # subtle: blend toward bg by using sub_color at small size, bottom-right
    draw.text((S - ww - 60, S - (bb[3] - bb[1]) - 60), wm, font=watermark_font, fill=sub_color)

    return img


def image_to_png_bytes(img: Image.Image) -> bytes:
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


# ---------------------------------------------------------------------------
# Pro upsell dialog
# ---------------------------------------------------------------------------
@st.dialog("🔒 Premium themes coming soon!")
def pro_dialog(theme_name: str):
    st.write(
        f"**{theme_name}** is a Pro template.\n\n"
        "We're validating demand before adding payments. "
        "Drop your email soon to get early access — for now, enjoy the 2 free themes!"
    )
    st.info("Free plan includes Tech Dark + Minimal Light with watermark.")
    if st.button("Got it, keep creating ✨", use_container_width=True):
        st.rerun()


# ---------------------------------------------------------------------------
# UI — Control panel (left) + Live preview (right)
# ---------------------------------------------------------------------------
st.title(f"🎨 {APP_NAME} — Text-to-Graphic Generator")
st.caption("Turn quotes, tips & thoughts into pro 1:1 social graphics in 3 seconds. Zero cost. Instagram • LinkedIn • X ready (1080×1080 PNG).")

if "theme" not in st.session_state:
    st.session_state.theme = "Tech Dark"

col_controls, col_preview = st.columns([1, 1.15], gap="large")

with col_controls:
    st.subheader("1️⃣ Your content")
    text = st.text_area(
        "Text",
        value="Small steps every day compound into massive results. Start before you're ready.",
        max_chars=280,
        height=130,
        help="280 characters max — like a tweet.",
        label_visibility="collapsed",
        placeholder="Type or paste your quote, tip or thought…",
    )
    st.caption(f"{len(text)}/280 characters")

    show_author = st.toggle("Show author details", value=True)
    author_name, handle = "", ""
    if show_author:
        c1, c2 = st.columns(2)
        with c1:
            author_name = st.text_input("Author name", value="Alex Morgan", max_chars=40)
        with c2:
            handle = st.text_input("Username / handle", value="@alexbuilds", max_chars=40)

    st.subheader("2️⃣ Style")
    st.write("Pick a theme:")
    theme_names = list(THEMES.keys())
    # 2x2 grid
    for row in range(0, 4, 2):
        cols = st.columns(2)
        for i, name in enumerate(theme_names[row:row + 2]):
            meta = THEMES[name]
            with cols[i]:
                is_selected = st.session_state.theme == name
                label = f"{'✅ ' if is_selected else ''}{name}{' 🔒 Pro' if meta['pro'] else ''}"
                if st.button(label, key=f"theme_{name}", use_container_width=True,
                             type="primary" if is_selected else "secondary"):
                    if meta["pro"]:
                        pro_dialog(name)
                    else:
                        st.session_state.theme = name
                        st.rerun()
                st.caption(meta["description"])

    font_size = st.slider("Font size", min_value=36, max_value=110, value=62, step=2,
                          help="Adjust manually if text is too long or short.")

    st.info("💧 **Free plan:** tiny “Made with PixelQuote” watermark in the corner. Pro (soon) removes it + unlocks 🔒 themes.")

with col_preview:
    st.subheader("3️⃣ Live preview & export")
    active_theme = st.session_state.theme
    st.write(f"Canvas: **1080 × 1080** (1:1) • Theme: **{active_theme}**")

    img = render_graphic(text, author_name, handle, show_author, active_theme, font_size)
    st.image(img, caption=f"{active_theme} — scaled preview, export is full 1080p", use_container_width=True)

    png_bytes = image_to_png_bytes(img)
    st.download_button(
        "⬇️ Download Image (.png)",
        data=png_bytes,
        file_name=f"{APP_NAME.lower()}-{active_theme.lower().replace(' ', '-')}-1080x1080.png",
        mime="image/png",
        use_container_width=True,
    )
    st.caption("Tip: post the PNG natively to Instagram / LinkedIn / X for crisp quality.")

st.divider()
st.caption(f"Built with Streamlit + Pillow • 100% code-rendered, $0 running cost • {APP_NAME} Micro-SaaS MVP")
