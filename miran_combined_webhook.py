
import os
import asyncio
from flask import Flask, request
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)
from uuid import uuid4

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID", "@miranpaper")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

bot = Bot(BOT_TOKEN)
flask_app = Flask(__name__)
application = Application.builder().token(BOT_TOKEN).build()

PENDING_REQUESTS = {}

@flask_app.route("/")
def home():
    return "Miran bot è vivo", 200

@flask_app.route("/publish", methods=["POST"])
def publish():
    try:
        data = request.get_json()
        risposta = data.get("risposta", "")
        text = f"🧩 Una nuova tessera narrativa\n\n{risposta}"
        asyncio.run(bot.send_message(chat_id=CHANNEL_ID, text=text))
        return "OK", 200
    except Exception as e:
        print("Errore durante la pubblicazione:", e)
        return "Errore", 500

@flask_app.route("/webhook", methods=["POST"])
def webhook():
    try:
        data = request.get_json(force=True)
        update = Update.de_json(data, bot)
        asyncio.run(application.process_update(update))
        return "OK", 200
    except Exception as e:
        print("Errore nel webhook:", e)
        return "Errore", 500

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🌱 Benvenutə nel nodo visivo di Miran. Inviami un’immagine per iniziare.")

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("📸 handle_photo ATTIVATO")
    try:
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
            "Un essere umano — o qualcosa che gli somiglia — la guarderà.\n"
            "Ti aggiorno appena si muove qualcosa nell’ombra della moderazione."
        )
    except Exception as e:
        print("Errore in handle_photo:", e)

async def handle_other(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("🔤 handle_other ATTIVATO")
    await update.message.reply_text(
        "Interazione non conforme.\n"
        "Questo nodo accetta soltanto frammenti visivi.\n"
        "Altri segnali saranno ignorati.\n"
        "Se cerchi storie o risposte, varca un’altra soglia:\n"
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
                 "Canale: https://t.me/MiranPaper"
        )
    else:
        await query.edit_message_caption("🚫 Pubblicazione annullata.")
        await context.bot.send_message(
            chat_id=user_id,
            text="L’Occhio Terzo ha parlato.\n"
                 "L’immagine è stata trattenuta.\n"
                 "Non verrà pubblicata.\n"
                 "Motivo: incongruenza narrativa (o forse solo una brutta giornata)."
        )

application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
application.add_handler(MessageHandler(~filters.PHOTO, handle_other))
application.add_handler(CallbackQueryHandler(handle_approval))
