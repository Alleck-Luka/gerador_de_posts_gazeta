from PIL import Image, ImageDraw, ImageFont, ImageStat

def gerar_post(titulo, categoria, bg_source):

    img = Image.open(bg_source).convert("RGB")

    # --- Config ---
    WIDTH, HEIGHT = 1080, 1350

    logo_branca = "./assets/logo_white.png"
    logo_preta = "./assets/logo_black.png"

    cor_caixa = "#d51317"

    posicoes = [
        ("top-left", (137, 135, 437, 385)),
        ("top-middle", (WIDTH//2 - 150, 135, WIDTH//2 + 150, 385)),
        ("top-right", (WIDTH-143-300, 135, WIDTH-137, 385)),
    ]

    # --- Funções ---

    def escolher_logo(img: Image.Image):
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

    def brilho_medio(img):
        stat = ImageStat.Stat(img.convert("L"))  # escala de cinza
        return stat.mean[0]  # 0 (preto) → 255 (branco)
    
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

        # 🔥 alinhado ao topo (top = 0)
        left = (new_width - target_w) // 2
        top = 0
        right = left + target_w
        bottom = top + target_h

        return img.crop((left, top, right, bottom))    

    # --- Base ---

    base = cover_top(img, 1080, 1920)

    feed_img = base.crop((0, 0, 1080, 1350))
    story_img = base


    # --- Gradiente (parte inferior) ---
    gradient = Image.new("RGBA", (WIDTH, HEIGHT), (0,0,0,0))
    for y in range(HEIGHT):
        if(y>= HEIGHT - 900 and y < HEIGHT - 200): #1350 - 900 = 450 -- Vai começar em 450 e terminar em 1150
            alpha = int(255 * ((y - 450) / (1150 - 450)))  # intensidade
            ImageDraw.Draw(gradient).line([(0,y), (WIDTH,y)], fill=(7,20,62,alpha))
        elif(y>= HEIGHT - 900 and y >= HEIGHT - 200):
            ImageDraw.Draw(gradient).line([(0,y), (WIDTH,y)], fill=(7,20,62,255))

    img = story_img.copy().convert("RGBA")
    draw = ImageDraw.Draw(img)

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

    img.paste(grad, (x0, y0), grad)

    # --- Escolher logo ---
    pos, cor, grad = escolher_logo(img)

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

    return output

# Testagem

gerar_post("Título teste de algumas palavras", "Teste", "./assets/background.jpg")