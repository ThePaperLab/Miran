
import os
import asyncio
import telegram
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, constants
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)
from flask import Flask, request
from uuid import uuid4

# Config
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
ADMIN_ID = int(os.getenv("ADMIN_ID"))
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

application = ApplicationBuilder().token(BOT_TOKEN).build()
bot = application.bot
flask_app = Flask(__name__)
PENDING_REQUESTS = {}

@flask_app.route("/webhook", methods=["POST"])
def webhook():
    update = telegram.Update.de_json(request.get_json(force=True), bot)
    application.update_queue.put_nowait(update)
    return "OK", 200

@flask_app.route("/publish", methods=["POST"])
def publish():
    try:
        data = request.get_json()
        domanda = data.get("domanda", "")
        risposta = data.get("risposta", "")
        timestamp = data.get("timestamp", "")
        text = f"*Una nuova tessera narrativa:*" 
                f"{risposta}"             
        asyncio.run(bot.send_message(chat_id=CHANNEL_ID, text=text, parse_mode=constants.ParseMode.MARKDOWN))
        return "OK", 200
    except Exception as e:
        print("Errore durante la pubblicazione:", e)
        return "Errore", 500

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Benvenutə nel nodo visivo di Miran.\n"
        "Inviami un'immagine per proporla al flusso collettivo.\n"
        "Tutto passa prima attraverso l’Occhio Terzo."
    )

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

    await context.bot.send_photo(
        chat_id=ADMIN_ID,
        photo=file_id,
        caption="🖼️ Vuoi pubblicare questa immagine sul canale?",
        reply_markup=reply_markup
    )

    await update.message.reply_text(
        "Hai mandato un’immagine. Non male.\n"
        "Ma non posso caricarla così, sai com’è.\n"
        "Prima deve passare il Giudizio dell’Occhio Terzo.\n"
        "Un essere umano — o qualcosa che gli somiglia — la guarderà, ci rifletterà, magari prenderà un caffè.\n"
        "Poi deciderà se è degna del canale o se finirà tra i ricordi non pubblicati.\n"
        "Ti aggiorno appena si muove qualcosa nell’ombra della moderazione."
    )

async def handle_other(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Interazione non conforme.\n"
        "Questo nodo accetta soltanto frammenti visivi.\n"
        "Altri segnali saranno ignorati.\n"
        "Se cerchi parole, storie o risposte, devi varcare un’altra soglia:\n"
        "→ https://chatgpt.com/g/g-67defc5af8f88191a4a3e593921b46be-miran-paper"
    )

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
        await context.bot.send_photo(chat_id=CHANNEL_ID, photo=file_id)
        await query.edit_message_caption("✅ Immagine pubblicata.")
        await context.bot.send_message(
            chat_id=user_id,
            text="Il Custode ha vagliato. L’immagine è passata.\n"
                 "È stata pubblicata nel flusso visivo collettivo.\n"
                 "Canale: https://t.me/MiranPaper\n"
                 "Un’altra tessera si aggiunge al mosaico."
        )
    else:
        await query.edit_message_caption("🚫 Pubblicazione annullata.")
        await context.bot.send_message(
            chat_id=user_id,
            text="L’Occhio Terzo ha parlato.\n"
                 "L’immagine è stata trattenuta.\n"
                 "Non verrà pubblicata.\n"
                 "Motivo segnalato: incongruenza narrativa\n"
                 "(ma potrebbe anche solo aver avuto una brutta giornata).\n"
                 "Prova con un altro frammento. O aspetta che cambino i venti."
        )

if __name__ == "__main__":
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    application.add_handler(MessageHandler(~filters.PHOTO, handle_other))
    application.add_handler(CallbackQueryHandler(handle_approval))

    loop = asyncio.get_event_loop()
    loop.run_until_complete(application.initialize())
    loop.run_until_complete(bot.set_webhook(WEBHOOK_URL))
    flask_app.run(host="0.0.0.0", port=10000)
