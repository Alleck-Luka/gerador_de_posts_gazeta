
from PIL import Image, ImageDraw, ImageFont

from helper import gerar_base, ajustar_fonte_titulo


FEED_CLEAN = "./assets/Feed Veritas Clean.png"
STORY_CLEAN = "./assets/Story Veritas Clean.png"

FONT_PATH = "./assets/Montserrat-Bold.ttf"

COR_DESTAQUE = "#e30505"


def carregar_clean(path, base):
    clean = Image.open(path).convert("RGBA")

    if clean.size != base.size:
        raise ValueError(
            f"Dimensões incompatíveis: clean={clean.size}, base={base.size}"
        )

    return Image.alpha_composite(base.convert("RGBA"), clean)


def render_feed(base, titulo, categoria):
    img = carregar_clean(FEED_CLEAN, base)
    draw = ImageDraw.Draw(img)

    x = 80
    bottom_y = 1106
    line_height = 60
    max_width = 920

    font, lines = ajustar_fonte_titulo(
        draw,
        titulo,
        FONT_PATH,
        max_width=max_width,
        max_lines=20,
        start_size=49
    )

    if font is None:
        raise RuntimeError("Erro ao carregar fonte")

    total_height = len(lines) * line_height
    text_top = bottom_y - total_height

    # --- CATEGORIA ---
    font_categoria = ImageFont.truetype(FONT_PATH, 43)

    categoria = categoria.upper()

    padding_x = 24
    padding_y = 20

    bbox = draw.textbbox((0, 0), categoria, font=font_categoria)

    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    box_x = 80
    box_h = text_height + padding_y * 2
    box_w = text_width + padding_x * 2

    # Bottom do retângulo fica 40px acima do texto
    box_bottom = text_top - 40
    box_top = box_bottom - box_h

    draw.rounded_rectangle(
        (box_x, box_top, box_x + box_w, box_bottom),
        radius=10,
        fill=COR_DESTAQUE
    )

    draw.text(
        (
            box_x + padding_x,
            box_top + padding_y - bbox[1]
        ),
        categoria,
        font=font_categoria,
        fill="white"
    )

    # --- TÍTULO ---
    y = text_top

    for line in lines:
        draw.text(
            (x, y),
            line,
            font=font,
            fill="white"
        )
        y += line_height

    return img


def render_story(base, titulo):
    img = carregar_clean(STORY_CLEAN, base)
    draw = ImageDraw.Draw(img)

    x = 104
    bottom_y = 1430
    line_height = 60
    max_width = 872

    font = ImageFont.truetype(FONT_PATH, 60)

    font, lines = ajustar_fonte_titulo(
        draw,
        titulo,
        FONT_PATH,
        max_width=max_width,
        max_lines=20,
        start_size=60
    )

    if font is None:
        raise RuntimeError("Erro ao carregar fonte")

    total_height = len(lines) * line_height
    text_top = bottom_y - total_height

    # --- BARRA VERMELHA ---
    bar_width = 12
    bar_gap = 40
    bar_extra = 2

    bar_x = x - bar_gap - bar_width

    draw.rectangle(
        (
            bar_x,
            text_top - bar_extra,
            bar_x + bar_width,
            bottom_y + bar_extra
        ),
        fill=COR_DESTAQUE
    )

    # --- TÍTULO ---
    y = text_top

    for line in lines:
        draw.text(
            (x, y),
            line,
            font=font,
            fill="white"
        )
        y += line_height

    return img
