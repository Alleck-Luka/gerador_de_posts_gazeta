from PIL import Image, ImageDraw, ImageFont, ImageStat
from generator_normal import render_feed, render_story
from generator_politica import render_feed_politica, render_story_politica
from helper import gerar_base

def gerar_post(titulo, categoria, bg_source):
    base = gerar_base(bg_source)

    feed = render_feed(base, titulo, categoria)
    story = render_story(base, titulo)

    titulo_feed = "Feed " + titulo + ".png"
    titulo_story = "Story " + titulo + ".png"

    feed.save(titulo_feed, quality=95)
    story.save(titulo_story, quality=95)

    feed_politica = render_feed_politica(titulo, categoria, bg_source)
    titulo_politica_feed = "Feed Politica " + titulo + ".png"
    feed_politica.save(titulo_politica_feed)

    story_politica = render_story_politica(titulo, categoria, bg_source)
    titulo_politica_story = "Story Politica " + titulo + ".png"
    story_politica.save(titulo_politica_story)

    return titulo_feed, titulo_story, titulo_politica_feed, titulo_politica_story

# Testagem

gerar_post("Cetam abre 8 mil vagas para cursos gratuitos em Manaus: saiba como se inscrever", "Educação", "./assets/background.jpg")