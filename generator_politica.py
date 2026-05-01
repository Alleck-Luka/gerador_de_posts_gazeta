from PIL import Image, ImageDraw, ImageFont, ImageChops
from helper import ajustar_fonte_titulo, aplicar_overlay_local, cover_crop

def render_story_politica(titulo, categoria, bg_source):

    WIDTH, HEIGHT = 1080, 1920

    # --- Base branca ---
    img = Image.new("RGBA", (WIDTH, HEIGHT), "#fefbfc")
    draw = ImageDraw.Draw(img)

    # --- Fundo vermelho ---
    draw.rectangle(
        [-39, 1545, -39 + 1170, 1545 + 481],
        fill="#d51317"
    )

    # --- Imagem principal (igual feed: cover + crop) ---
    bg = Image.open(bg_source).convert("RGB")
    bg = cover_crop(bg, 1018, 1382)

    img.paste(bg, (31, 237))

    # --- Retângulo azul ---
    draw.rectangle(
        [30, 1411, 30 + 1018, 1411 + 402],
        fill="#07143e"
    )

    # --- Categoria ---
    draw.rectangle(
        [234, 1353, 234 + 591, 1353 + 117],
        fill="#d51317"
    )

    font_cat = ImageFont.truetype("./assets/Montserrat-Bold.ttf", 90)

    bbox = draw.textbbox((0,0), categoria, font=font_cat)
    text_w = bbox[2]
    text_h = bbox[3]

    draw.text(
        (234 + (591 - text_w)//2, 1353 + (100 - text_h)//2),
        categoria,
        fill="#fafafc",
        font=font_cat
    )

    # --- Título (centralizado vertical + horizontal) ---
    font = ImageFont.truetype("./assets/Montserrat-SemiBold.ttf", 60)

    def wrap(text, max_w):
        words = text.split()
        lines, cur = [], ""

        for w in words:
            test = f"{cur} {w}".strip()
            if draw.textbbox((0,0), test, font=font)[2] <= max_w:
                cur = test
            else:
                lines.append(cur)
                cur = w
        lines.append(cur)
        return lines

    lines = wrap(titulo, 944)

    line_height = 65
    total_h = len(lines) * line_height
    start_y = 1503 + (262 - total_h) // 2

    for i, line in enumerate(lines):
        w = draw.textbbox((0,0), line, font=font)[2]

        draw.text(
            (62 + (944 - w)//2, start_y + i * line_height),
            line,
            fill="white",
            font=font
        )

    # --- Dots top ---
    # def aplicar_opacidade(img_rgba, opacity):
    #     alpha = img_rgba.split()[3]
    #     alpha = alpha.point(lambda p: int(p * opacity))
    #     img_rgba.putalpha(alpha)
    #     return img_rgba

    # dots_top = Image.open("./assets/story_dots_politica_cima.png").convert("RGBA")
    # dots_top = dots_top.resize((433, 202), Image.Resampling.LANCZOS)
    # dots_top = aplicar_opacidade(dots_top, 0.4)
    # img.alpha_composite(dots_top, (853, 229))

    # --- Dots bottom ---
    # dots_bottom = Image.open("./assets/story_dots_politica_baixo.png").convert("RGBA")
    # dots_bottom = dots_bottom.resize((147, 315), Image.Resampling.LANCZOS)
    # dots_bottom = aplicar_opacidade(dots_bottom, 0.4)
    # img.alpha_composite(dots_bottom, (-24, 1142))

    # --- Dots TOP (story) ---
    dots_top = Image.open("./assets/story_dots_politica_cima.png").convert("RGBA")
    dots_top = dots_top.resize((433, 202), Image.Resampling.LANCZOS)

    aplicar_overlay_local(img, dots_top, 853, 229)


    # --- Dots BOTTOM (story) ---
    dots_bottom = Image.open("./assets/story_dots_politica_baixo.png").convert("RGBA")
    dots_bottom = dots_bottom.resize((147, 315), Image.Resampling.LANCZOS)

    aplicar_overlay_local(img, dots_bottom, -24, 1142)    

    # --- Logo ---
    logo = Image.open("./assets/logo_gazeta_politica.png").convert("RGBA")
    logo = logo.resize((337, 118), Image.Resampling.LANCZOS)

    img.alpha_composite(logo, (372, 72))

    return img.convert("RGB")

def render_feed_politica(titulo, categoria, bg_source):
    from PIL import Image, ImageDraw, ImageFont

    WIDTH, HEIGHT = 2000, 2500

    # --- Base branca ---
    img = Image.new("RGBA", (WIDTH, HEIGHT), "#fefbfc")
    draw = ImageDraw.Draw(img)

    # --- Fundo vermelho inferior ---
    draw.rectangle(
        [0, 1908, 2000, 1908 + 592],
        fill="#d51317"
    )

    # --- Imagem principal ---
    bg = Image.open(bg_source).convert("RGB")

    bg = cover_crop(bg, 1818, 1535)
    img.paste(bg, (91, 262))

    # --- Retângulo azul ---
    draw.rectangle(
        [92, 1796, 92 + 1816, 1796 + 503],
        fill="#07143e"
    )

    # --- Retângulo vermelho (categoria fundo) ---
    draw.rectangle(
        [666, 1739, 666 + 649, 1739 + 129],
        fill="#d51317"
    )

    # --- Fonte categoria ---
    font_cat = ImageFont.truetype("./assets/Montserrat-Bold.ttf", 100)

    draw.text(
        (831, 1740),
        categoria,
        fill="#fafafc",
        font=font_cat
    )

    # --- Título ---
    font_titulo, lines = ajustar_fonte_titulo(
        draw,
        titulo,
        "./assets/Montserrat-SemiBold.ttf",
        max_width=1703,
        max_lines=3,
        start_size=92
    )

    x_base = 148  # ou 148.59 arredondado
    box_width = 1703

    y = 1914

    for line in lines:
        w = draw.textbbox((0,0), line, font=font_titulo)[2]

        draw.text(
            (x_base + (box_width - w)//2, y),
            line,
            fill="white",
            font=font_titulo
        )
        y += 110

    # --- Dots TOP ---
    dots_top = Image.open("./assets/feed_dots_politica_cima.png").convert("RGBA")
    dots_top = dots_top.resize((433, 202), Image.Resampling.LANCZOS)

    aplicar_overlay_local(img, dots_top, 1745, 319)


    # --- Dots BOTTOM ---
    dots_bottom = Image.open("./assets/feed_dots_politica_baixo.png").convert("RGBA")
    dots_bottom = dots_bottom.resize((147, 315), Image.Resampling.LANCZOS)

    aplicar_overlay_local(img, dots_bottom, 87, 1079)

    # --- Logo ---
    logo = Image.open("./assets/logo_gazeta_politica.png").convert("RGBA")
    logo = logo.resize((413, 145), Image.Resampling.LANCZOS)

    img.alpha_composite(logo, (794, 71))

    return img.convert("RGB")