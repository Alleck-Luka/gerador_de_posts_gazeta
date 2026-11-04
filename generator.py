from generator_normal import render_feed, render_story
from helper import gerar_base, limpar_nome_arquivo

categorias_politicas = ["Eleições 2026", "Política", "Poder"]

def gerar_post(titulo, categoria, bg_source):

    titulo_limpo = limpar_nome_arquivo(titulo)

    # Bases independentes
    base_feed = gerar_base(bg_source, 1080, 1350)
    base_story = gerar_base(bg_source, 1080, 1920)

    feed = render_feed(base_feed, titulo, categoria)
    story = render_story(base_story, titulo)

    titulo_feed = titulo_limpo + "Feed.png"
    titulo_story = titulo_limpo + "Story.png"

    feed.save(titulo_feed)
    story.save(titulo_story)

    return titulo_feed, titulo_story

# Testagem

gerar_post("Cetam abre 8 mil vagas para cursos gratuitos em Manaus: saiba como se inscrever saiba como se inscrever saiba como se inscrever", "Sociedade", "./assets/Feed Veritas.png")