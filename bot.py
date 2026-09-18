import yfinance as yf
import pandas as pd
import telebot
import os
import time
import threading

TOKEN = os.getenv("BOT_TOKEN") or os.getenv("TELEGRAM_TOKEN")
bot = telebot.TeleBot(TOKEN)

def safe_float(x):
    try:
        if x is None: return 0.0
        if isinstance(x, pd.DataFrame):
            x = x.squeeze()
        if hasattr(x, 'iloc'):
            val = x.iloc[-1]
            if hasattr(val, 'iloc'):
                val = float(val.iloc[0])
            else:
                val = float(val)
            return val
        return float(x)
    except:
        return 0.0

def get_data():
    df = yf.download("GC=F", period="5d", interval="1h", progress=False, auto_adjust=False)
    if df.empty: return None
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    c = df['Close']
    h = df['High']
    l = df['Low']

    adr = safe_float((h - l).rolling(14).mean()) * 6
    if adr < 10: adr = 35.0

    price = safe_float(c)
    if price == 0: return None

    return price, safe_float(c.ewm(9).mean()), safe_float(c.ewm(21).mean()), safe_float(c.ewm(50).mean()), safe_float(c.ewm(200).mean()), adr

def get_levels(price, e9, e21, adr):
    long = price > e21
    if long:
        return {'entry': price, 'sl': price-adr*0.4, 'tp1': price+adr*0.3, 'tp2': price+adr*0.6, 'tp3': price+adr*1.0}
    else:
        return {'entry': price, 'sl': price+adr*0.4, 'tp1': price-adr*0.3, 'tp2': price-adr*0.6, 'tp3': price-adr*1.0}

@bot.message_handler(commands=['start','gold'])
def gold_cmd(m):
    data = get_data()
    if not data:
        bot.send_message(m.chat.id, "Yahoo не отдал цену, нажми /gold еще раз через 10 сек")
        return
    price, e9, e21, e50, e200, adr = data
    lv = get_levels(price, e9, e21, adr)
    side = "ЛОНГ 📈" if price > e21 else "ШОРТ 📉"
    trend = "БЫЧИЙ" if e50 > e200 else "МЕДВЕЖИЙ"
    bot.send_message(m.chat.id, f"""🟡 GOLD: ${price:.1f} | ADR: ${adr:.1f}

1. СКАЛЬП: {side} | EMA9 ${e9:.1f} / EMA21 ${e21:.1f}
Вход {lv['entry']:.1f} | ТП1 {lv['tp1']:.1f} | ТП2 {lv['tp2']:.1f} | СЛ {lv['sl']:.1f}

2. ИНТРАДЕЙ: {side} | EMA50 ${e50:.1f}
Вход {lv['entry']:.1f} | ТП {lv['tp3']:.1f} | СЛ {lv['sl']:.1f}

3. ТРЕНД: {trend} | EMA50 ${e50:.1f} / EMA200 ${e200:.1f}

Бот 24/7 ✅""")

print("Bot polling...")
bot.infinity_polling()
