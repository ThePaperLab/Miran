from flask import Flask, request
import telegram
import os
import requests
from datetime import datetime
import base64

app = Flask(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID", "@miranpaper")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPO = os.getenv("GITHUB_REPO", "ThePaperLab/pubblicazioni-Miran")
GITHUB_BRANCH = "main"

bot = telegram.Bot(token=BOT_TOKEN)

def upload_to_github(image_bytes, filename):
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/publicazioni/{filename}"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    content = base64.b64encode(image_bytes).decode("utf-8")
    data = {
        "message": f"Add {filename}",
        "branch": GITHUB_BRANCH,
        "content": content
    }
    response = requests.put(url, headers=headers, json=data)
    if response.status_code == 201:
        return f"https://raw.githubusercontent.com/{GITHUB_REPO}/{GITHUB_BRANCH}/publicazioni/{filename}"
    else:
        print("❌ Errore upload GitHub:", response.text)
        return None

@app.route('/miran-hook', methods=['POST'])
def ricevi_e_pubblica():
    try:
        data = request.json
        print("📥 Payload ricevuto:", data)

        domanda = data.get('domanda')
        risposta = data.get('risposta')
        timestamp = data.get('timestamp', datetime.now().isoformat())
        immagine_url = data.get('immagine_url')

        if not domanda or not risposta:
            return {'status': 'error', 'details': 'Domanda o risposta mancanti'}, 400

        caption = f"🌬️ *Conversazione con Miran Paper*\n\n🗣️ *Domanda:*\n{domanda}\n\n🎙️ *Risposta:*\n{risposta}\n\n🕰️ {timestamp}"

        if immagine_url:
            print(f"📷 Scarico immagine da: {immagine_url}")
            response = requests.get(immagine_url)
            if response.status_code == 200:
                extension = immagine_url.split(".")[-1].split("?")[0]
                filename = f"{timestamp.replace(':', '-').replace('T', '_')}_miran.{extension}"
                image_bytes = response.content
                github_url = upload_to_github(image_bytes, filename)
                if github_url:
                    bot.send_photo(
                        chat_id=CHANNEL_ID,
                        photo=github_url,
                        caption=caption,
                        parse_mode=telegram.ParseMode.MARKDOWN
                    )
                    print("✅ Immagine inviata con successo")
                else:
                    return {'status': 'error', 'details': 'Errore caricamento GitHub'}, 500
            else:
                return {'status': 'error', 'details': 'Immagine non scaricabile'}, 400
        else:
            bot.send_message(
                chat_id=CHANNEL_ID,
                text=caption,
                parse_mode=telegram.ParseMode.MARKDOWN
            )
            print("✅ Solo testo inviato")

        return {'status': 'ok'}, 200

    except Exception as e:
        print("🔥 Errore generale:", str(e))
        return {'status': 'error', 'details': str(e)}, 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
