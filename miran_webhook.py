from flask import Flask, request
import telegram
import os
import requests
from datetime import datetime
import tempfile

app = Flask(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID", "@miranpaper")
bot = telegram.Bot(token=BOT_TOKEN)

@app.route('/miran-hook', methods=['POST'])
def ricevi_e_pubblica():
    try:
        data = request.json
        print("📥 Ricevuto payload:", data)

        domanda = data.get('domanda')
        risposta = data.get('risposta')
        timestamp = data.get('timestamp', datetime.now().isoformat())
        immagine_url = data.get('immagine_url')

        if not domanda or not risposta:
            return {'status': 'error', 'details': 'Domanda o risposta mancanti'}, 400

        caption = f"🌬️ *Conversazione con Miran Paper*\n\n🗣️ *Domanda:*\n{domanda}\n\n🎙️ *Risposta:*\n{risposta}\n\n🕰️ {timestamp}"

        if immagine_url:
            print(f"📷 Tentativo di download immagine da: {immagine_url}")
            response = requests.get(immagine_url, stream=True)
            if response.status_code == 200:
                with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
                    for chunk in response.iter_content(1024):
                        tmp_file.write(chunk)
                    tmp_file_path = tmp_file.name
                print("✅ Immagine scaricata con successo")

                with open(tmp_file_path, 'rb') as photo:
                    bot.send_photo(
                        chat_id=CHANNEL_ID,
                        photo=photo,
                        caption=caption,
                        parse_mode=telegram.ParseMode.MARKDOWN
                    )
                os.remove(tmp_file_path)
                print("✅ Immagine pubblicata e file temporaneo rimosso")
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
            print("✅ Testo pubblicato con successo")

        return {'status': 'ok'}, 200

    except Exception as e:
        print("🔥 Errore generale:", str(e))
        return {'status': 'error', 'details': str(e)}, 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
