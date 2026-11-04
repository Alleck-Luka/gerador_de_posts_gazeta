from dotenv import load_dotenv
from flask import Flask, request
import requests
from generator import gerar_post
from io import BytesIO
import os
import logging
from logging.handlers import RotatingFileHandler

LIST_NAME = "Agendar Nas Redes Sociais"
load_dotenv()

API_KEY = os.getenv("API_KEY")
TOKEN = os.getenv("TOKEN")

app = Flask(__name__)

# pasta de logs
os.makedirs("logs", exist_ok=True)

# configuração
handler = RotatingFileHandler(
    "logs/app.log",
    maxBytes=5_000_000,  # 5 MB
    backupCount=5,
    encoding="utf-8"
)

formatter = logging.Formatter(
    "[%(asctime)s] %(levelname)s in %(module)s: %(message)s"
)

handler.setFormatter(formatter)

app.logger.addHandler(handler)
app.logger.setLevel(logging.INFO)

def anexar(card_id, caminhos):
    url = f"https://api.trello.com/1/cards/{card_id}/attachments"

    feed_attachment_id = None

    try:
        for caminho in caminhos:
            with open(caminho, "rb") as f:
                response = requests.post(
                    url,
                    params={"key": API_KEY, "token": TOKEN},
                    files={"file": f}
                )

            data = response.json()

            # salva o attachment do feed
            if "Feed" in caminho:
                feed_attachment_id = data["id"]

            os.remove(caminho)

        # definir cover do card
        if feed_attachment_id:
            requests.put(
                f"https://api.trello.com/1/cards/{card_id}",
                params={
                    "key": API_KEY,
                    "token": TOKEN,
                    "idAttachmentCover": feed_attachment_id
                }
            )
    except Exception:
        app.logger.exception(f"Erro ao anexar!")
        return

def processar_card(card_id):
    url = f"https://api.trello.com/1/cards/{card_id}"

    params = {
        "key": API_KEY,
        "token": TOKEN,
        "attachments": "true"
    }

    response = requests.get(url, params=params)

    app.logger.info(f"STATUS: {response.status_code}")
    app.logger.info(f"RESPOSTA:", response.text[:200])


    if response.status_code != 200:
        return

    card = response.json()

    titulo = card["name"]

    categoria = card["labels"][0]["name"]
    
    app.logger.info(f"Processando card {card_id}")
    app.logger.info(f"Título: {titulo}")
    app.logger.info(f"Categoria: {categoria}")

    # pegar imagem
    imagem_url = None
    for att in card.get("attachments", []):
        if "image" in att["mimeType"]:
            imagem_url = att["url"]
            break
    if not imagem_url:
        app.logger.error(f"Erro ao obter imagem: {imagem_url}")
        return
    

    app.logger.info(f"Imagem: {imagem_url}")

    # baixar imagem
    try:
        response_img = requests.get(
            imagem_url,
            headers={
                "Authorization": f'OAuth oauth_consumer_key="{API_KEY}", oauth_token="{TOKEN}"'
            }
        )
    except Exception:
        app.logger.exception(f"Erro ao baixar imagem: {imagem_url}")
        return

    print("IMG STATUS:", response_img.status_code)
    print("IMG TYPE:", response_img.headers.get("Content-Type"))

    if "image" not in response_img.headers.get("Content-Type", ""):
        app.logger.error(f"Erro ao obter imagem: {imagem_url}")
        return

    img_bytes = BytesIO(response_img.content)

    output = gerar_post(titulo, categoria, img_bytes)

    # anexar no card
    anexar(card_id, output)

@app.route("/trello-webhook", methods=["GET", "POST", "HEAD"])
def trello_webhook():
    if request.method in ["HEAD", "GET"]:
        return "Webhook ativo", 200

    data = request.json
    if not data or "action" not in data:
        return "", 200

    action = data["action"]

    # evento: card movido
    if action["type"] == "updateCard":
        list_after = action["data"].get("listAfter", {}).get("name", "")

        if list_after == LIST_NAME:
            card_id = action["data"]["card"]["id"]
            processar_card(card_id)

    return "", 200

# if __name__ == "__main__":
#     app.run(port=5000)