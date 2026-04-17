from PIL import Image, ImageDraw, ImageFont, ImageStat

logo_branca = "./assets/logo_white.png"
logo_preta = "./assets/logo_black.png"

type Posicao = tuple[str, tuple[int, int, int, int]]

# Retorna um crop da imagem horizontalmente centrada e alinhada ao topo
def cover_top(img, target_w, target_h):
    img_ratio = img.width / img.height
    target_ratio = target_w / target_h

    if img_ratio > target_ratio:
        # mais larga → corta lados
        new_height = target_h
        new_width = int(img_ratio * new_height)
    else:
        # mais alta → corta embaixo
        new_width = target_w
        new_height = int(new_width / img_ratio)

    img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

    # alinhado ao topo (top = 0)
    left = (new_width - target_w) // 2
    top = 0
    right = left + target_w
    bottom = top + target_h

    return img.crop((left, top, right, bottom))    

def brilho_medio(img):
    stat = ImageStat.Stat(img.convert("L"))  # escala de cinza
    return stat.mean[0]  # 0 (preto) → 255 (branco)

# Escolhe a logo baseado em melhor contraste entre uma lista de posições posicoes: list[Posicao]
def escolher_logo(img: Image.Image, posicoes: list[Posicao]):
    melhor = {}

    for nome, box in posicoes:
        area = img.crop(box)
        brilho = brilho_medio(area)

        # contraste ideal: longe do meio (~127)
        contraste = abs(brilho - 127)

        if not melhor or contraste > melhor["contraste"]:
            melhor = {
                "pos": nome,
                "box": box,
                "brilho": brilho,
                "contraste": contraste
            }

    # decidir cor da logo
    if melhor["brilho"] < 140:
        cor = "branca"
    else:
        cor = "preta"

    # decidir se precisa gradiente
    precisa_gradiente = melhor["contraste"] < 40

    return melhor["pos"], cor, precisa_gradiente

# Gera a imagem de background bg_source: StrOrBytesPath | IO[bytes]
def gerar_base(bg_source):
    img = Image.open(bg_source).convert("RGB")

    def cover_top(img, target_w, target_h):
        img_ratio = img.width / img.height
        target_ratio = target_w / target_h

        if img_ratio > target_ratio:
            new_height = target_h
            new_width = int(img_ratio * new_height)
        else:
            new_width = target_w
            new_height = int(new_width / img_ratio)

        img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

        left = (new_width - target_w) // 2
        return img.crop((left, 0, left + target_w, target_h))

    return cover_top(img, 1080, 1920)

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

    # --- Título (com quebra de linha simples) ---
    def wrap_text(text, font, max_width):
        lines = []
        words = text.split()
        current = ""

        for word in words:
            test = current + " " + word if current else word
            w = draw.textbbox((0,0), test, font=font)[2]
            if w <= max_width:
                current = test
            else:
                lines.append(current)
                current = word

        lines.append(current)
        return lines

    lines = wrap_text(titulo, font_titulo, 825)

    y_text = 979.43
    for line in lines:
        draw.text((137.94, y_text), line, font=font_titulo, fill="white")
        y_text += 70


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

    # no final:
    output = "post.png"
    img.convert("RGB").save(output, quality=95)

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
    if b'Bold' in font.get_variation_names():
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

    y = 1497
    for line in lines:
        draw.text((129, y), line, fill="white", font=font)
        y += 70

    

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

def gerar_post(titulo, categoria, bg_source):
    base = gerar_base(bg_source)

    feed = render_feed(base, titulo, categoria)
    story = render_story(base, titulo)

    feed.save("feed.png", quality=95)
    story.save("story.png", quality=95)

    return "feed.png", "story.png"

# Testagem

gerar_post("Título teste de algumas palavras", "Teste", "./assets/background.jpg")