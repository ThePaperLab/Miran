# 🌀 Miran Paper Publisher – Sistema Unificato

Questo sistema permette di:
- Pubblicare automaticamente le storie testuali generate dal GPTs sul canale Telegram @miranpaper
- Ricevere immagini da Telegram e sottoporle a moderazione manuale prima della pubblicazione

## 🔗 Endpoint

POST `/publish`  
Riceve una `domanda`, una `risposta` e un `timestamp` e li pubblica come messaggio formattato sul canale.

## 🤖 Bot Telegram

- Risponde solo a immagini.
- Quando riceve una foto:
  - Risponde all’utente con:

```
Hai mandato un’immagine. Non male.
Ma non posso caricarla così, sai com’è.

Prima deve passare il Giudizio dell’Occhio Terzo.
Un essere umano — o qualcosa che gli somiglia — la guarderà, ci rifletterà, magari prenderà un caffè. Poi deciderà se è degna del canale o se finirà tra i ricordi non pubblicati.

Ti aggiorno appena si muove qualcosa nell’ombra della moderazione.
```

- Se la foto viene **approvata**:
  - Pubblicata sul canale
  - All’utente arriva:

```
Il Custode ha vagliato. L’immagine è passata.
È stata pubblicata nel flusso visivo collettivo.
Canale: https://t.me/MiranPaper

Un’altra tessera si aggiunge al mosaico.
```

- Se la foto viene **rifiutata**:
  - All’utente arriva:

```
L’Occhio Terzo ha parlato.

L’immagine è stata trattenuta.
Non verrà pubblicata.

Motivo segnalato: incongruenza narrativa
(ma potrebbe anche solo aver avuto una brutta giornata).

Prova con un altro frammento. O aspetta che cambino i venti.
```

- Se l’utente invia altro (testo, audio, file):
  - Risposta automatica:

```
Interazione non conforme.

Questo nodo accetta soltanto frammenti visivi.
Altri segnali saranno ignorati.

Se cerchi parole, storie o risposte, devi varcare un’altra soglia:
→ https://chatgpt.com/g/g-67defc5af8f88191a4a3e593921b46be-miran-paper
```

## ⚙️ Variabili d’ambiente da configurare su Render

| Variabile     | Descrizione                         |
|---------------|-------------------------------------|
| `BOT_TOKEN`   | Token del bot Telegram              |
| `CHANNEL_ID`  | ID o @username del canale Telegram  |
| `ADMIN_ID`    | ID numerico Telegram dell’admin     |

✳️ Ottieni il tuo `ADMIN_ID` scrivendo a [@userinfobot](https://t.me/userinfobot)

## 🌐 URL di test webhook
Puoi testare la pubblicazione delle storie inviando `POST` a:
```
https://miran-0uep.onrender.com/publish
```
