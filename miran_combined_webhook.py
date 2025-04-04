import os
import logging
from flask import Flask, request
from telegram import Bot
import asyncio
from threading import Thread

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Flask app
app = Flask(__name__)

# Variabili d'ambiente
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")

# Telegram bot
bot = Bot(BOT_TOKEN)

# Crea un event loop globale
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

@app.route("/")
def index():
    return "Miran Paper webhook attivo."

@app.route("/publish", methods=["POST"])
def publish():
    data = request.get_json()
    risposta = data.get("risposta", "").strip()
    if risposta:
        asyncio.run_coroutine_threadsafe(
            bot.send_message(chat_id=CHANNEL_ID, text=risposta),
            loop
        )
    return "", 200

if __name__ == "__main__":
    def run_loop():
        loop.run_forever()

    t = Thread(target=run_loop, daemon=True)
    t.start()

    app.run(host="0.0.0.0", port=10000, debug=True)
