from PIL import ImageDraw, Image, ImageFont

from helper import escolher_logo

logo_branca = "./assets/logo_white.png"
logo_preta = "./assets/logo_black.png"

def render_feed(base, titulo, categoria):
    img = base.crop((0, 0, 1080, 1350)).convert("RGBA")
    draw = ImageDraw.Draw(img)

    WIDTH, HEIGHT = 1080, 1350

    # 🔹 gradiente feed (seu atual)
    gradient = Image.new("RGBA", (WIDTH, HEIGHT), (0,0,0,0))
    for y in range(HEIGHT):
        if 450 <= y < 1150:
            alpha = int(255 * ((y - 450) / (1150 - 450)))
            ImageDraw.Draw(gradient).line([(0,y),(WIDTH,y)], fill=(7,20,62,alpha))
        elif y >= 1150:
            ImageDraw.Draw(gradient).line([(0,y),(WIDTH,y)], fill=(7,20,62,255))

    img = Image.alpha_composite(img, gradient)
    draw = ImageDraw.Draw(img)

    cor_caixa = "#d51317"

    posicoes = [
        ("top-left", (137, 135, 437, 385)),
        ("top-middle", (WIDTH//2 - 150, 135, WIDTH//2 + 150, 385)),
        ("top-right", (WIDTH-143-300, 135, WIDTH-137, 385)),
    ]

    # --- Fonte ---
    font_titulo = ImageFont.truetype("./assets/Inter-VariableFont_opsz,wght.ttf", size=50)
    # print(font_titulo.get_variation_names())
    if b'Bold' in font_titulo.get_variation_names():
        font_titulo.set_variation_by_name('Bold')

    font_categoria = ImageFont.truetype("./assets/PlayfairDisplay-Bold.ttf", 50) # 12 pontos -> 16 pixels

    # --- Categoria (retângulo + texto) ---
    cat_x, cat_y = 141, 862
    padding = 15

    bbox = draw.textbbox((0,0), categoria, font=font_categoria)
    rect_w = bbox[2] + padding*2 + 30
    rect_h = bbox[3] + padding

    draw.rectangle(
        [cat_x, cat_y, cat_x + rect_w, cat_y + rect_h],
        fill=cor_caixa  # cor da categoria
    )

    draw.text(
        (cat_x + padding + 15, cat_y),
        categoria,
        fill="white",
        font=font_categoria
    )

    # --- Título com auto-resize (máx 3 linhas, alinhado à esquerda) ---

    def ajustar_fonte_titulo(draw, texto, font_path, max_width, max_lines, start_size):
        size = start_size

        while size > 20:  # limite de segurança
            font = ImageFont.truetype(font_path, size)

            # wrap
            words = texto.split()
            lines = []
            current = ""

            for word in words:
                test = f"{current} {word}".strip()
                w = draw.textbbox((0,0), test, font=font)[2]

                if w <= max_width:
                    current = test
                else:
                    lines.append(current)
                    current = word

            lines.append(current)

            if len(lines) <= max_lines:
                return font, lines

            size -= 1

        return font, lines  # fallback


    # 🔹 usar função
    font_titulo, lines = ajustar_fonte_titulo(
        draw,
        titulo,
        "./assets/Inter-VariableFont_opsz,wght.ttf",
        max_width=825,
        max_lines=3,
        start_size=50
    )

    # opcional: bold seguro
    if hasattr(font_titulo, "get_variation_names"):
        try:
            if b'Bold' in font_titulo.get_variation_names():
                font_titulo.set_variation_by_name('Bold')
        except:
            pass


    # 🔹 desenhar (ALINHADO À ESQUERDA)
    x_text = 137.94
    y_text = 979.43
    line_height = 70

    for line in lines:
        draw.text(
            (x_text, y_text),
            line,
            font=font_titulo,
            fill="white"
        )
        y_text += line_height


    #Linha vermelha gradiente

    x0, y0 = 135, 1203
    width, height = 750, 8

    r, g, b = (186, 7, 37)

    grad = Image.new("RGBA", (width, height), (0,0,0,0))
    draw_grad = ImageDraw.Draw(grad)

    mid_point = int(width * 0.8)

    for x in range(width):
        if x <= mid_point:
            # 100% → 75% (255 → 190)
            alpha = int(255 - (155 * (x / mid_point)))
        else:
            # 75% → 0% (190 → 0)
            alpha = int(100 * (1 - ((x - mid_point) / (width - mid_point))))

        draw_grad.line([(x, 0), (x, height)], fill=(r, g, b, alpha))

    img.alpha_composite(grad, (x0, y0))

    # --- Escolher logo ---
    pos, cor, grad = escolher_logo(img, posicoes)

    logo_path = logo_branca if cor == "branca" else logo_preta
    logo = Image.open(logo_path).convert("RGBA")

    # posição final

    if pos == "top-left":
        xy = (137, 135)

    elif pos == "top-middle":
        logo_w, logo_h = logo.size
        xy = (WIDTH//2 - logo_w//2, 135)

    else:
        logo_w, logo_h = logo.size
        xy = (WIDTH - logo_w - 437, 135)

    # xy = (137, 135)
    # logo_w, logo_h = logo.size
    # xy = (WIDTH//2 - logo_w//2, 135)
    # logo_w, logo_h = logo.size
    # xy = (WIDTH - 143 - logo_w, 135)

    img.paste(logo, xy, logo)

    return img

def render_story(base, titulo):
    img = base.copy().convert("RGBA")
    draw = ImageDraw.Draw(img)

    WIDTH, HEIGHT = 1080, 1920

    posicoes = [
        ("top-left", (137, 135, 437, 385)),
        ("top-middle", (WIDTH//2 - 150, 135, WIDTH//2 + 150, 385)),
        ("top-right", (WIDTH-143-300, 135, WIDTH-137, 385)),
    ]

    # gradiente novo
    gradient = Image.new("RGBA", (WIDTH, HEIGHT), (0,0,0,0))
    for y in range(HEIGHT):
        if 776 <= y < 1530:
            alpha = int(255 * ((y - 776) / (1530 - 776)))
            ImageDraw.Draw(gradient).line([(0,y),(WIDTH,y)], fill=(7,20,62,alpha))
        elif y >= 1530:
            ImageDraw.Draw(gradient).line([(0,y),(WIDTH,y)], fill=(7,20,62,255))

    img = Image.alpha_composite(img, gradient)
    draw = ImageDraw.Draw(img)

    # linha vermelha
    x0, y0 = 128, 1468
    width, height = 823, 8

    grad = Image.new("RGBA", (width, height), (0,0,0,0))
    draw_grad = ImageDraw.Draw(grad)

    center = width / 2
    falloff_start = 0.2
    curve_strength = 0.7

    for x in range(width):
        dist = abs(x - center) / center

        if dist < falloff_start:
            alpha = 255
        else:
            t = (dist - falloff_start) / (1 - falloff_start)
            alpha = int(255 * (1 - t**curve_strength))

        draw_grad.line([(x, 0), (x, height)], fill=(186, 7, 37, alpha))

    img.alpha_composite(grad, (x0, y0))

    # texto
    font = ImageFont.truetype("./assets/Inter-VariableFont_opsz,wght.ttf", 50)
    if hasattr(font, "get_variation_names") and b'Bold' in font.get_variation_names():
        font.set_variation_by_name('Bold')

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

    lines = wrap(titulo, 824)

    # 🔹 CONFIG DA CAIXA
    box_x = 129
    box_y = 1497
    box_w = 824
    box_h = 267
    line_height = 70

    # 🔹 altura total do texto
    total_h = len(lines) * line_height

    # 🔹 início Y (centralizado vertical)
    start_y = box_y + (box_h - total_h) // 2

    # 🔹 desenhar linhas centralizadas
    for i, line in enumerate(lines):
        text_w = draw.textbbox((0,0), line, font=font)[2]

        draw.text(
            (box_x + (box_w - text_w)//2, start_y + i * line_height),
            line,
            fill="white",
            font=font
        )

    # logo

    pos, cor, grad = escolher_logo(img, posicoes)
    logo_path = logo_branca if cor == "branca" else logo_preta

    logo = Image.open(logo_path).convert("RGBA")
    logo = logo.resize((176, 67), Image.Resampling.LANCZOS)

    # posição final

    if pos == "top-left":
        xy = (137, 135)

    elif pos == "top-middle":
        logo_w, logo_h = logo.size
        xy = (WIDTH//2 - logo_w//2, 135)

    else:
        logo_w, logo_h = logo.size
        xy = (WIDTH - logo_w - 437, 135)

    # xy = (137, 135)
    # logo_w, logo_h = logo.size
    # xy = (WIDTH//2 - logo_w//2, 135)
    # logo_w, logo_h = logo.size
    # xy = (WIDTH - 143 - logo_w, 135)

    img.paste(logo, xy, logo)

    return img