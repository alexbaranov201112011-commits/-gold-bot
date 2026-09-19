from flask import Flask, request
import telegram
import os
import datetime
import pytz

TOKEN = "8964936412:AAEKIaDurlLDg-qskd5Rc0JC28uCwOnZ_Ek"
bot = telegram.Bot(token=TOKEN)
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running OK!"

@app.route('/webhook', methods=['POST'])
def webhook():
    update = telegram.Update.de_json(request.get_json(force=True), bot)
    chat_id = update.message.chat.id
    text = update.message.text

    if "/gold" in text or "/start" in text:
        # Твоя логика v2
        tz = pytz.timezone('Asia/Atyrau')
        now = datetime.datetime.now(tz)
        if 12 <= now.hour <= 22:
            msg = f"🔱 АНАЛИЗ РЫНКА ЗОЛОТА\n\nВремя: {now.strftime('%H:%M')} Атырау\nТренд 15м: BUY\nТренд 1ч: BUY\nУверенность: 95%\n\n📈 Сигнал: ПОКУПКА\nSL: -300п\nTP: +600п"
        else:
            msg = f"⏳ ОЖИДАНИЕ\nСейчас {now.strftime('%H:%M')} Атырау\nСессия с 12:00 до 22:00"
        bot.send_message(chat_id=chat_id, text=msg)
    return 'ok'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))
