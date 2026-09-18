import yfinance as yf
import telebot
import os
import time
import threading

TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID") # твой id

bot = telebot.TeleBot(TOKEN)

def safe_float(x):
    try:
        if hasattr(x, 'iloc'):
            return float(x.iloc[-1])
        return float(x)
    except:
        return 0.0

def get_data():
    df = yf.download("GC=F", period="1mo", interval="1h", progress=False)
    if df.empty:
        return None
    c = df['Close']
    h = df['High']
    l = df['Low']
    
    # ADR - средний дневной диапазон, на H1 умножаем на 6
    daily_range = (h - l).rolling(14).mean()
    adr = safe_float(daily_range) * 6
    if adr < 10:
        adr = 35.0 # страховка если данные кривые

    price = safe_float(c)
    e9 = safe_float(c.ewm(span=9).mean())
    e21 = safe_float(c.ewm(span=21).mean())
    e50 = safe_float(c.ewm(span=50).mean())
    e200 = safe_float(c.ewm(span=200).mean())
    return price, e9, e21, e50, e200, adr

def get_levels(price, e9, e21, adr):
    # Логика по ADR как у профи
    is_long = price > e21
    if is_long:
        entry = price
        sl = price - adr * 0.4
        tp1 = price + adr * 0.3
        tp2 = price + adr * 0.6
        tp3 = price + adr * 1.0
    else:
        entry = price
        sl = price + adr * 0.4
        tp1 = price - adr * 0.3
        tp2 = price - adr * 0.6
        tp3 = price - adr * 1.0
    return {'entry': entry, 'sl': sl, 'tp1': tp1, 'tp2': tp2, 'tp3': tp3}

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Бот запущен 24/7 ✅\nКоманда: /gold")

@bot.message_handler(commands=['gold'])
def gold_cmd(message):
    try:
        data = get_data()
        if not data:
            bot.send_message(message.chat.id, "Ошибка данных Yahoo")
            return
        price, e9, e21, e50, e200, adr = data
        levels = get_levels(price, e9, e21, adr)
        side = "ЛОНГ 📈" if price > e21 else "ШОРТ 📉"
        trend = "БЫЧИЙ" if e50 > e200 else "МЕДВЕЖИЙ"

        text = f"""🟡 GOLD: ${price:.1f} | ADR: ${adr:.1f}

1. СКАЛЬП (15м-1ч):
{side} | EMA9: ${e9:.1f} / EMA21: ${e21:.1f}
Вход: ${levels['entry']:.1f} | ТП1: ${levels['tp1']:.1f} | ТП2: ${levels['tp2']:.1f} | СЛ: ${levels['sl']:.1f}

2. ИНТРАДЕЙ (сегодня):
{side} | Цена vs EMA50: ${e50:.1f}
Вход: ${levels['entry']:.1f} | ТП: ${levels['tp3']:.1f} | СЛ: ${levels['sl']:.1f}

3. ТРЕНД (неделя):
{trend} | EMA50: ${e50:.1f} / EMA200: ${e200:.1f}

Бот работает 24/7 ✅"""
        bot.send_message(message.chat.id, text)
    except Exception as e:
        bot.send_message(message.chat.id, f"Ошибка: {e}")

def check_signals():
    while True:
        try:
            time.sleep(3600) # проверка каждый час для H1
            data = get_data()
            if not data: continue
            price, e9, e21, e50, e200, adr = data
            # Тут твоя логика авто-сигналов если надо
        except Exception as e:
            print(f"Loop error: {e}")
            time.sleep(60)

threading.Thread(target=check_signals, daemon=True).start()
print("Bot polling started...")
bot.infinity_polling()
