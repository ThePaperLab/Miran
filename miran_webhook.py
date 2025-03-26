from flask import Flask, request
import telegram
import os
from datetime import datetime

app = Flask(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID", "@miranpaper")  # Modifica se necessario
bot = telegram.Bot(token=BOT_TOKEN)

@app.route('/miran-hook', methods=['POST'])
def ricevi_e_pubblica():
    data = request.json
    domanda = data.get('domanda')
    risposta = data.get('risposta')
    timestamp = data.get('timestamp', datetime.now().isoformat())
    immagine_url = data.get('immagine_url')

    caption = f"🌬️ *Conversazione con Miran Paper*\n\n🗣️ *Domanda:*\n{domanda}\n\n🎙️ *Risposta:*\n{risposta}\n\n🕰️ {timestamp}"

    if immagine_url:
        # Pubblica l'immagine con la didascalia
        bot.send_photo(
            chat_id=CHANNEL_ID,
            photo=immagine_url,
            caption=caption,
            parse_mode=telegram.ParseMode.MARKDOWN
        )
    else:
        # Pubblica solo il testo
        bot.send_message(
            chat_id=CHANNEL_ID,
            text=caption,
            parse_mode=telegram.ParseMode.MARKDOWN
        )

    return {'status': 'ok'}, 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
