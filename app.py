from dotenv import load_dotenv
from flask import Flask, request
import requests
from generator import gerar_post
from io import BytesIO
import os

LIST_NAME = "Agendar Nas Redes Sociais"
load_dotenv()

API_KEY = os.getenv("API_KEY")
TOKEN = os.getenv("TOKEN")

app = Flask(__name__)

def anexar(card_id, caminho):
    url = f"https://api.trello.com/1/cards/{card_id}/attachments"

    with open(caminho, "rb") as f:
        requests.post(
            url,
            params={"key": API_KEY, "token": TOKEN},
            files={"file": f}
        )

def processar_card(card_id):
    url = f"https://api.trello.com/1/cards/{card_id}"

    params = {
        "key": API_KEY,
        "token": TOKEN,
        "attachments": "true"
    }

    response = requests.get(url, params=params)

    print("STATUS:", response.status_code)
    print("RESPOSTA:", response.text[:200])  # debug

    if response.status_code != 200:
        return

    card = response.json()

    titulo = card["name"]
    categoria = card["desc"]

    # pegar imagem
    imagem_url = None
    for att in card.get("attachments", []):
        if "image" in att["mimeType"]:
            imagem_url = att["url"]
            break
    print(imagem_url)
    if not imagem_url:
        return

    # baixar imagem
    response_img = requests.get(
        imagem_url,
        headers={
            "Authorization": f'OAuth oauth_consumer_key="{API_KEY}", oauth_token="{TOKEN}"'
        }
    )

    print("IMG STATUS:", response_img.status_code)
    print("IMG TYPE:", response_img.headers.get("Content-Type"))

    if "image" not in response_img.headers.get("Content-Type", ""):
        print("❌ Não é imagem:", response_img.text[:200])
        return

    img_bytes = BytesIO(response_img.content)

    # gerar post
    output = gerar_post(titulo, categoria, img_bytes)

    # anexar no card
    anexar(card_id, output)

@app.route("/trello-webhook", methods=["POST", "HEAD"])
def trello_webhook():
    if request.method == "HEAD":
        return "", 200  # Trello testa isso

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

if __name__ == "__main__":
    app.run(port=5000)