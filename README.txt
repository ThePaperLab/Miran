# Miran Paper Webhook

Questo è un semplice server Flask che riceve richieste POST da un GPT personalizzato (ChatGPT) e pubblica contenuti su un canale Telegram.

## 📦 Requisiti

- Python 3.8+
- Un bot Telegram creato tramite @BotFather
- Un canale Telegram dove il bot è admin

## 🔧 Variabili d'ambiente

- `BOT_TOKEN`: il token del tuo bot Telegram
- `CHANNEL_ID`: il nome del canale (es. @nomecanale)

## 🚀 Avvio locale

1. Installa le dipendenze:
   ```
   pip install -r requirements.txt
   ```

2. Esporta le variabili d'ambiente:
   ```
   export BOT_TOKEN='il_tuo_token'
   export CHANNEL_ID='@tuo_canale'
   ```

3. Avvia il server:
   ```
   python miran_webhook.py
   ```

## 🌐 Deployment su Render, Railway, ecc.

- Crea un nuovo web service con Python
- Imposta `BOT_TOKEN` e `CHANNEL_ID` tra le environment variables
- Punta il GPT Webhook all'URL `/miran-hook`
