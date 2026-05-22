from generator_normal import render_feed, render_story
from generator_politica import render_feed_politica, render_story_politica
from helper import gerar_base, limpar_nome_arquivo

categorias_politicas = ["Eleições 2026", "Política", "Poder"]

def gerar_post(titulo, categoria, bg_source):

    titulo_limpo = limpar_nome_arquivo(titulo)
    base = gerar_base(bg_source)

    if(categoria in categorias_politicas):
        feed_politica = render_feed_politica(titulo, categoria, bg_source)
        story_politica = render_story_politica(titulo, categoria, bg_source)

        titulo_politica_feed = titulo_limpo + "F.png"
        titulo_politica_story = titulo_limpo + "S.png"

        feed_politica.save(titulo_politica_feed)
        story_politica.save(titulo_politica_story)
        return titulo_politica_feed, titulo_politica_story
    else:
        feed = render_feed(base, titulo, categoria)
        story = render_story(base, titulo)


        titulo_feed = titulo_limpo + "Feed.png"
        titulo_story = titulo_limpo + "Story.png"

        feed.save(titulo_feed)
        story.save(titulo_story)
        return titulo_feed, titulo_story

# Testagem

# gerar_post("Cetam abre 8 mil vagas para cursos gratuitos em Manaus: saiba como se inscrever saiba como se inscrever saiba como se inscrever", "Sociedade", "./assets/background.jpg")