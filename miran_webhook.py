from flask import Flask, request
import telegram
import os
import requests
from datetime import datetime
import io

app = Flask(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID", "@miranpaper")
bot = telegram.Bot(token=BOT_TOKEN)

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

        caption = f"{risposta}\n\n {timestamp}"

        if immagine_url:
            print(f"📷 Scarico immagine da: {immagine_url}")
            response = requests.get(immagine_url)
            if response.status_code == 200:
                image_blob = io.BytesIO(response.content)
                timestamp_slug = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
                image_blob.name = f"miran_{timestamp_slug}.jpg"
                bot.send_photo(
                    chat_id=CHANNEL_ID,
                    photo=image_blob,
                    caption=caption,
                    parse_mode=telegram.ParseMode.MARKDOWN
                )
                print("✅ Immagine inviata con successo")
            else:
                print("❌ Errore nel download immagine:", response.status_code)
                return {'status': 'error', 'details': 'Immagine non scaricabile'}, 400
        else:
            print("📝 Nessuna immagine. Invio solo testo.")
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
