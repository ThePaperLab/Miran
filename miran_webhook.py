import os
from flask import Flask, request, jsonify
import telegram

app = Flask(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")

bot = telegram.Bot(token=BOT_TOKEN)

@app.route("/miran-hook", methods=["POST"])
def miran_hook():
    data = request.get_json(force=True)

    domanda = data.get("domanda", "")
    risposta = data.get("risposta", "")
    timestamp = data.get("timestamp", "")

    if not risposta:
        return jsonify({"error": "Risposta mancante"}), 400

    try:
        text = f"🌀 *Racconto dal GPTs di Miran* 🌀\n\n"                f"*Domanda:* {domanda}\n\n"                f"*Risposta:* {risposta}\n\n"                f"_Timestamp:_ {timestamp}"

        bot.send_message(chat_id=CHANNEL_ID, text=text, parse_mode=telegram.constants.ParseMode.MARKDOWN)
        return jsonify({"status": "ok"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/", methods=["GET"])
def index():
    return "Miran webhook online", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
