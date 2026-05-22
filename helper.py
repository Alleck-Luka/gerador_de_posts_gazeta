from PIL import ImageFont, Image, ImageStat, ImageChops

type Posicao = tuple[str, tuple[int, int, int, int]]  

import re

def limpar_nome_arquivo(nome):
    nome = re.sub(r'[<>:"/\\|?*]', '', nome)
    nome = nome.strip()
    return nome[:100]  # evita nomes gigantes

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

def score_logo(area: Image.Image, logo_color: str):
    gray = area.convert("L")
    stat = ImageStat.Stat(gray)

    media = stat.mean[0]
    desvio = stat.stddev[0]

    hist = gray.histogram()

    escuros = sum(hist[:80])
    claros = sum(hist[175:])

    total = sum(hist)

    pct_escuro = escuros / total
    pct_claro = claros / total

    # -------------------------
    # CONTRASTE BASE
    # -------------------------

    if logo_color == "branca":
        contraste = 255 - media
        dominancia = pct_escuro
    else:
        contraste = media
        dominancia = pct_claro

    # -------------------------
    # DISTÂNCIA DO CINZA MÉDIO
    # -------------------------

    distancia_meio = abs(media - 127)

    # -------------------------
    # PENALIDADE DE TEXTURA
    # -------------------------

    penalidade_textura = desvio * 1.4

    score = (
        contraste * 1.8
        + dominancia * 120
        + distancia_meio * 1.2
        - penalidade_textura
    )

    return score

# Escolhe a logo baseado em melhor contraste entre uma lista de posições posicoes: list[Posicao]
def escolher_logo(img: Image.Image, posicoes):

    if not posicoes:
        return "top-left", "branca", False

    melhor = None

    for nome, box in posicoes:
        area = img.crop(box)

        branca = score_logo(area, "branca")
        preta = score_logo(area, "preta")

        if branca > preta:
            cor = "branca"
            score = branca
        else:
            cor = "preta"
            score = preta

        # contraste local
        desvio = ImageStat.Stat(area.convert("L")).stddev[0]

        print(desvio)
        gray = area.convert("L")
        stat = ImageStat.Stat(gray)

        media = stat.mean[0]
        desvio = stat.stddev[0]

        print("media:", media)
        print("desvio:", desvio)

        precisa_gradiente = (
            abs(media - 127) < 45
            or desvio > 45
        )

        atual = {
            "pos": nome,
            "cor": cor,
            "score": score,
            "grad": precisa_gradiente
        }

        if melhor is None or atual["score"] > melhor["score"]:
            melhor = atual
    
    if melhor is None:
        return "top-left", "branca", False
    
    if melhor["cor"] == "preta":
        melhor["grad"] = False

    return melhor["pos"], melhor["cor"], melhor["grad"]