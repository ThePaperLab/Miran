import os
from flask import Flask, request
from telegram import Bot, Update, InputFile, InlineKeyboardButton, InlineKeyboardMarkup, constants
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
import asyncio
from uuid import uuid4

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))  # ID numerico
CHANNEL_ID = os.getenv("CHANNEL_ID")

app = Flask(__name__)
bot = Bot(BOT_TOKEN)
pending_requests = {}

@app.route('/')
def index():
    return 'Miran Paper webhook attivo.'

@app.route('/publish', methods=['POST'])
def publish():
    data = request.get_json()
    risposta = data.get("risposta", "").strip()
    if risposta:
        asyncio.run(bot.send_message(chat_id=CHANNEL_ID, text="📜 Una nuova tessera narrativa"))
        asyncio.run(bot.send_message(chat_id=CHANNEL_ID, text=risposta))
    return '', 200

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    update = Update.de_json(data, bot)
    asyncio.create_task(application.process_update(update))
    return '', 200

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Benvenutə nel nodo visivo di Miran."
        "Inviami un'immagine per proporla al flusso collettivo."
        "Tutto passa prima attraverso l’Occhio Terzo."
    )

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo = update.message.photo[-1]
    file_id = photo.file_id
    user_id = update.message.from_user.id
    request_id = str(uuid4())
    pending_requests[request_id] = (file_id, user_id)

    keyboard = [
        [InlineKeyboardButton("✅ Pubblica", callback_data=f"approve|{request_id}"),
         InlineKeyboardButton("❌ Rifiuta", callback_data=f"reject|{request_id}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await bot.send_photo(chat_id=ADMIN_ID, photo=file_id, caption="🖼️ Vuoi pubblicare questa immagine sul canale?", reply_markup=reply_markup)

    await update.message.reply_text(
        "Hai mandato un’immagine. Non male."
        "Ma non posso caricarla così, sai com’è."
        "Prima deve passare il Giudizio dell’Occhio Terzo."
        "Un essere umano — o qualcosa che gli somiglia — la guarderà, ci rifletterà, magari prenderà un caffè."
        "Poi deciderà se è degna del canale o se finirà tra i ricordi non pubblicati."
        "Ti aggiorno appena si muove qualcosa nell’ombra della moderazione."
    )

async def handle_other(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Interazione non conforme."
        "Questo nodo accetta soltanto frammenti visivi."
        "Altri segnali saranno ignorati."
        "Se cerchi parole, storie o risposte, devi varcare un’altra soglia:"
        "→ https://chatgpt.com/g/g-67defc5af8f88191a4a3e593921b46be-miran-paper"
    )

async def handle_approval(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    action, request_id = query.data.split("|")

    data = pending_requests.pop(request_id, None)
    if not data:
        await query.edit_message_caption("❌ Richiesta non valida o già gestita.")
        return

    file_id, user_id = data

    if action == "approve":
        await bot.send_photo(chat_id=CHANNEL_ID, photo=file_id)
        await query.edit_message_caption("✅ Immagine pubblicata.")
        await bot.send_message(
            chat_id=user_id,
            text="Il Custode ha vagliato. L’immagine è passata."
                 "È stata pubblicata nel flusso visivo collettivo."
                 "Canale: https://t.me/MiranPaper"
                 "Un’altra tessera si aggiunge al mosaico."
        )
    else:
        await query.edit_message_caption("🚫 Pubblicazione annullata.")
        await bot.send_message(
            chat_id=user_id,
            text="L’Occhio Terzo ha parlato."
                 "L’immagine è stata trattenuta."
                 "Non verrà pubblicata."
                 "Motivo segnalato: incongruenza narrativa"
                 "(ma potrebbe anche solo aver avuto una brutta giornata)."
                 "Prova con un altro frammento. O aspetta che cambino i venti."
        )

def setup_bot():
    global application
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    application.add_handler(MessageHandler(~filters.PHOTO, handle_other))
    application.add_handler(CallbackQueryHandler(handle_approval))

if __name__ == "__main__":
    setup_bot()
    app.run(host="0.0.0.0", port=10000)
