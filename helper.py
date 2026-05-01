from PIL import ImageFont, Image, ImageStat, ImageChops

type Posicao = tuple[str, tuple[int, int, int, int]]  

def aplicar_overlay_local(base_img, layer_img, x, y):
    w, h = layer_img.size

    # recorte da base
    base_crop = base_img.crop((x, y, x + w, y + h)).convert("RGB")
    layer_rgb = layer_img.convert("RGB")

    # aplica overlay
    blended = ImageChops.overlay(base_crop, layer_rgb)

    # usa alpha original como máscara
    mask = layer_img.split()[3]

    # cola de volta
    base_img.paste(blended, (x, y), mask)

def ajustar_fonte_titulo(draw, texto, font_path, max_width, max_lines, start_size):
  size = start_size

  font = None
  lines = []

  while size > 20:
      font = ImageFont.truetype(font_path, size)

      words = texto.split()
      lines = []
      current = ""

      for word in words:
          test = f"{current} {word}".strip()
          w = draw.textbbox((0, 0), test, font=font)[2]

          if w <= max_width:
              current = test
          else:
              lines.append(current)
              current = word

      if current:
          lines.append(current)

      if len(lines) <= max_lines:
          return font, lines  # ✅ sucesso

      size -= 1

  # 🔥 fallback garantido
  return font, lines

def cover_crop(img, target_w, target_h):
  img_ratio = img.width / img.height
  target_ratio = target_w / target_h

  if img_ratio > target_ratio:
      # imagem mais larga
      new_height = target_h
      new_width = int(img_ratio * new_height)
  else:
      # imagem mais alta
      new_width = target_w
      new_height = int(new_width / img_ratio)

  img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

  # 🔥 crop central
  left = (new_width - target_w) // 2
  top = (new_height - target_h) // 2

  return img.crop((left, top, left + target_w, top + target_h))

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

def brilho_medio(img):
    stat = ImageStat.Stat(img.convert("L"))  # escala de cinza
    return stat.mean[0]  # 0 (preto) → 255 (branco)