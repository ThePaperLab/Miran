from flask import Flask, request
import telegram
import os
from datetime import datetime

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

        if not domanda or not risposta:
            return {'status': 'error', 'details': 'Domanda o risposta mancanti'}, 400

        caption = f"{risposta}\n\n {timestamp}"

        bot.send_message(
            chat_id=CHANNEL_ID,
            text=caption,
            parse_mode=telegram.ParseMode.MARKDOWN
        )
        print("✅ Testo inviato con successo")

        return {'status': 'ok'}, 200

    except Exception as e:
        print("🔥 Errore generale:", str(e))
        return {'status': 'error', 'details': str(e)}, 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
