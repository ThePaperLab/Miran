import os
from flask import Flask, request
import telegram
from telegram import constants
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    CallbackQueryHandler, ContextTypes, filters
)
from telegram.request import HTTPXRequest
from httpx import Limits

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from uuid import uuid4

# Configurazioni
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID", "@miranpaper")
ADMIN_ID = int(os.getenv("ADMIN_ID", "123456789"))  # ID numerico Telegram dell'admin

# Ottimizzazione connessione Telegram
custom_request = HTTPXRequest(
    pool_limits=Limits(max_connections=40, max_keepalive_connections=20),
    connect_timeout=20.0,
    read_timeout=20.0
)
bot = telegram.Bot(token=BOT_TOKEN, request=custom_request)
application = ApplicationBuilder().token(BOT_TOKEN).request(custom_request).build()

# App Flask
app = Flask(__name__)

# Memoria richieste immagini
PENDING_REQUESTS = {}

@app.route("/")
def index():
    return "Miran Webhook attivo."

@app.route("/publish", methods=["POST"])
def publish_story():
    try:
        data = request.json
        risposta = data.get("risposta")
        print("📝 Ricevuta storia da pubblicare:")
        print(risposta)

        if not risposta:
            return "No content", 400

        text = f"🧩 *Una nuova tessera narrativa:*{risposta}"
        bot.send_message(chat_id=CHANNEL_ID, text=text, parse_mode=constants.ParseMode.MARKDOWN)
        return "OK", 200
    except Exception as e:
        print(f"❌ Errore durante la pubblicazione: {e}")
        return "Errore interno", 500

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        update = telegram.Update.de_json(request.get_json(force=True), bot)
        application.update_queue.put_nowait(update)
        return "OK", 200
    except Exception as e:
        print(f"❌ Errore webhook: {e}")
        return "Errore Webhook", 500

# Gestione comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Benvenutə nel nodo visivo di Miran. Inviami un'immagine per proporla al flusso collettivo."
    )

# Gestione immagini inviate
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo = update.message.photo[-1]
    file_id = photo.file_id
    user_id = update.message.from_user.id
    request_id = str(uuid4())
    PENDING_REQUESTS[request_id] = (file_id, user_id)

    keyboard = [
        [
            InlineKeyboardButton("✅ Pubblica", callback_data=f"approve|{request_id}"),
            InlineKeyboardButton("❌ Annulla", callback_data=f"reject|{request_id}")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await bot.send_photo(
        chat_id=ADMIN_ID,
        photo=file_id,
        caption="🖼️ Vuoi pubblicare questa immagine sul canale?",
        reply_markup=reply_markup
    )

    await update.message.reply_text(
        "Hai mandato un’immagine. Non male.
"
        "Ma non posso caricarla così, sai com’è.
"
        "Prima deve passare il Giudizio dell’Occhio Terzo.
"
        "Un essere umano — o qualcosa che gli somiglia — la guarderà, ci rifletterà, magari prenderà un caffè.
"
        "Poi deciderà se è degna del canale o se finirà tra i ricordi non pubblicati.
"
        "Ti aggiorno appena si muove qualcosa nell’ombra della moderazione."
    )

# Gestione contenuti non immagine
async def handle_other(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Interazione non conforme.
"
        "Questo nodo accetta soltanto frammenti visivi.
"
        "Altri segnali saranno ignorati.
"
        "Se cerchi parole, storie o risposte, devi varcare un’altra soglia:
"
        "→ https://chatgpt.com/g/g-67defc5af8f88191a4a3e593921b46be-miran-paper"
    )

# Approvazione immagini
async def handle_approval(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    action, request_id = query.data.split("|")
    data = PENDING_REQUESTS.pop(request_id, None)
    if not data:
        await query.edit_message_caption("❌ Richiesta non valida o già gestita.")
        return
    file_id, user_id = data
    if action == "approve":
        await bot.send_photo(chat_id=CHANNEL_ID, photo=file_id)
        await query.edit_message_caption("✅ Immagine pubblicata.")
        await bot.send_message(
            chat_id=user_id,
            text="Il Custode ha vagliato. L’immagine è passata.
"
                 "È stata pubblicata nel flusso visivo collettivo.
"
                 "Canale: https://t.me/MiranPaper
"
                 "Un’altra tessera si aggiunge al mosaico."
        )
    else:
        await query.edit_message_caption("🚫 Pubblicazione annullata.")
        await bot.send_message(
            chat_id=user_id,
            text="L’Occhio Terzo ha parlato.
"
                 "L’immagine è stata trattenuta.
"
                 "Non verrà pubblicata.
"
                 "Motivo segnalato: incongruenza narrativa
"
                 "(ma potrebbe anche solo aver avuto una brutta giornata).
"
                 "Prova con un altro frammento. O aspetta che cambino i venti."
        )

# Associazione handler al bot
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
application.add_handler(MessageHandler(~filters.PHOTO, handle_other))
application.add_handler(CallbackQueryHandler(handle_approval))

if __name__ == "__main__":
    import threading
    threading.Thread(target=lambda: app.run(host="0.0.0.0", port=10000)).start()
    application.run_polling()
