import yfinance as yf
import telebot
import os
import pandas as pd

TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

def to_float(x):
    # фикс для ошибки 'Series'
    if isinstance(x, pd.Series):
        return float(x.iloc[0] if len(x)==1 else x.iloc[-1])
    try:
        return float(x)
    except:
        return float(x.iloc[-1])

def get_gold_analysis():
    try:
        data = yf.download("GC=F", period="5d", interval="15m", progress=False, auto_adjust=True)
        if data.empty:
            return "Ошибка: нет данных yfinance"

        # берем Close правильно
        close = data['Close']
        if isinstance(close, pd.DataFrame):
            close = close.squeeze()

        price = float(close.iloc[-1])
        ema9 = float(close.ewm(span=9).mean().iloc[-1])
        ema21 = float(close.ewm(span=21).mean().iloc[-1])

        daily = yf.download("GC=F", period="20d", interval="1d", progress=False, auto_adjust=True)
        d_high = daily['High']
        d_low = daily['Low']
        if isinstance(d_high, pd.DataFrame):
            d_high = d_high.squeeze()
            d_low = d_low.squeeze()
        adr = float((d_high - d_low).tail(14).mean())

        trend_strength = abs(ema9 - ema21)
        flat_threshold = price * 0.0015

        if adr < 35:
            return f"🟡 GOLD: ${price:.1f} | ADR: ${adr:.1f}\n\n⛔ НЕТ СИГНАЛА\nПричина: Волатильность низкая ADR {adr:.1f}"

        if trend_strength < flat_threshold:
            return f"🟡 GOLD: ${price:.1f}\nEMA9 {ema9:.1f} | EMA21 {ema21:.1f}\n\n⛔ ФЛЕТ, БЕЗ СДЕЛКИ\nТренд слабый {trend_strength:.1f}$ < {flat_threshold:.1f}$"

        is_long = ema9 > ema21
        direction = "📈 LONG" if is_long else "📉 SHORT"

        if is_long:
            sl = price - adr * 0.4
            tp1 = price + adr * 0.3
            tp2 = price + adr * 0.6
        else:
            sl = price + adr * 0.4
            tp1 = price - adr * 0.3
            tp2 = price - adr * 0.6

        return f"🟡 GOLD: ${price:.1f} | ADR: ${adr:.1f}\nEMA9: {ema9:.1f} | EMA21: {ema21:.1f}\n\n{direction} - СИГНАЛ ✅\nВход: ~${price:.1f}\nТП1: ${tp1:.1f}\nТП2: ${tp2:.1f}\nСЛ: ${sl:.1f}"

    except Exception as e:
        return f"Ошибка: {e}"

@bot.message_handler(commands=['gold'])
def gold_cmd(message):
    bot.send_chat_action(message.chat.id, 'typing')
    bot.reply_to(message, get_gold_analysis())

@bot.message_handler(commands=['start'])
def start_cmd(message):
    bot.reply_to(message, "Бот готов. Жми /gold")

print("Bot started...")
bot.infinity_polling(timeout=60, long_polling_timeout=60)
