import yfinance as yf
import telebot
import os
import time
import threading

TOKEN = os.getenv("BOT_TOKEN") or os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID") or os.getenv("TELEGRAM_CHAT_ID")

bot = telebot.TeleBot(TOKEN)

def safe_float(x):
    try:
        if x is None: return 0.0
        # Если DataFrame с мульти-колонками
        if hasattr(x, 'values'):
            import pandas as pd
            if isinstance(x, pd.DataFrame):
                x = x.squeeze()
            if hasattr(x, 'iloc'):
                val = x.iloc[-1]
                if hasattr(val, 'iloc'):
                    val = val.iloc[0]
                return float(val)
        return float(x)
    except Exception as e:
        print(f"safe_float error {e} on {x}")
        return 0.0

def get_data():
    try:
        df = yf.download("GC=F", period="5d", interval="1h", progress=False, auto_adjust=True)
        print(f"DF shape {df.shape}, cols {df.columns.tolist()[:3]}")
        if df.empty:
            return None
        
        # Фикс для новой версии yfinance
        if isinstance(df.columns, pd.MultiIndex) if 'pd' in dir() else hasattr(df.columns, 'levels'):
            df.columns = df.columns.get_level_values(0)

        import pandas as pd
        c = df['Close']
        h = df['High']
        l = df['Low']
        
        daily_range = (h - l).rolling(14).mean()
        adr = safe_float(daily_range) * 6
        if adr < 10:
            adr = 35.0

        price = safe_float(c)
        if price == 0:
            print("PRICE 0, full tail:", df.tail(2).to_string())
            return None
            
        e9 = safe_float(c.ewm(span=9).mean())
        e21 = safe_float(c.ewm(span=21).mean())
        e50 = safe_float(c.ewm(span=50).mean())
        e200 = safe_float(c.ewm(span=200).mean())
        return price, e9, e21, e50, e200, adr
    except Exception as e:
        print(f"get_data error: {e}")
        return None

def get_levels(price, e9, e21, adr):
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
def start(m): bot.send_message(m.chat.id, "Бот запущен 24/7 ✅\nКоманда: /gold")

@bot.message_handler(commands=['gold'])
def gold_cmd(message):
    try:
        data = get_data()
        if not data:
            bot.send_message(message.chat.id, "Yahoo пока не дал данные, попробуй через 1 мин /gold")
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
        print(e)

def check_signals():
    while True:
        time.sleep(3600)
        try: get_data()
        except: pass

threading.Thread(target=check_signals, daemon=True).start()
print("Bot polling...")
bot.infinity_polling()
