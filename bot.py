import yfinance as yf
import telebot
import os
import pandas as pd
import requests
from datetime import datetime, timedelta

TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

def to_float(x):
    if isinstance(x, pd.Series):
        return float(x.iloc[0] if len(x)==1 else x.iloc[-1])
    try:
        return float(x)
    except:
        return float(x.iloc[-1])

def check_news():
    try:
        now_utc = datetime.utcnow()
        now_aktau = now_utc + timedelta(hours=5)
        if now_aktau.hour in [16, 18, 19, 20] and now_aktau.minute < 40:
            return f"⚠️ Новостное время ({now_aktau.hour}:{now_aktau.minute:02d} Актау) - возможна волатильность"
        url = "https://nfs.faireconomy.media/ff_calendar_thisweek.json"
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            data = r.json()
            today_str = now_utc.strftime("%Y-%m-%d")
            for event in data:
                if event.get('date') == today_str and 'USD' in event.get('country','') and event.get('impact') == 'High':
                    return f"🚨 НОВОСТИ USD: {event.get('title','')} в {event.get('time','')} UTC"
        return None
    except:
        return None

def get_gold_analysis():
    try:
        news_warning = check_news()

        # Используем SPOT цену как у тебя в StarTrader
        data = yf.download("XAUUSD=X", period="5d", interval="15m", progress=False, auto_adjust=True)
        if data.empty:
            data = yf.download("GC=F", period="5d", interval="15m", progress=False, auto_adjust=True)
        if data.empty:
            return "❌ Ошибка: нет данных yfinance"

        close = data['Close']
        if isinstance(close, pd.DataFrame):
            close = close.squeeze()

        price = float(close.iloc[-1])
        ema9 = float(close.ewm(span=9).mean().iloc[-1])
        ema21 = float(close.ewm(span=21).mean().iloc[-1])

        daily = yf.download("XAUUSD=X", period="20d", interval="1d", progress=False, auto_adjust=True)
        if daily.empty:
            daily = yf.download("GC=F", period="20d", interval="1d", progress=False, auto_adjust=True)

        d_high = daily['High']
        d_low = daily['Low']
        if isinstance(d_high, pd.DataFrame):
            d_high = d_high.squeeze()
            d_low = d_low.squeeze()
        adr = float((d_high - d_low).tail(14).mean())

        trend_strength = abs(ema9 - ema21)
        flat_threshold = price * 0.0015

        header = f"🟡 GOLD SPOT: ${price:.2f} | ADR: ${adr:.1f}\n"
        if news_warning:
            header += f"\n{news_warning}\n"

        if adr < 20:
            return header + f"\n⛔ НЕТ СИГНАЛА\nПричина: Волатильность низкая ADR {adr:.1f}"

        if trend_strength < flat_threshold:
            return header + f"EMA9 {ema9:.2f} | EMA21 {ema21:.2f}\n\n⛔ ФЛЕТ, БЕЗ СДЕЛКИ\nТренд слабый {trend_strength:.2f}$ < {flat_threshold:.2f}$"

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

        footer = "\n⚠️ Новости! Уменьши лот x2" if news_warning else ""
        return (
            header +
            f"EMA9: {ema9:.2f} | EMA21: {ema21:.2f}\n\n"
            f"{direction} - СИГНАЛ ✅{footer}\n"
            f"Вход: ~${price:.2f}\n"
            f"ТП1: ${tp1:.2f}\n"
            f"ТП2: ${tp2:.2f}\n"
            f"СЛ: ${sl:.2f}"
        )

    except Exception as e:
        return f"Ошибка: {e}"

@bot.message_handler(commands=['gold'])
def gold_cmd(message):
    bot.send_chat_action(message.chat.id, 'typing')
    bot.reply_to(message, get_gold_analysis())

@bot.message_handler(commands=['start'])
def start_cmd(message):
    bot.reply_to(message, "Бот готов ✅ Жми /gold для анализа XAUUSD")

print("Bot started...")
bot.infinity_polling(timeout=60, long_polling_timeout=60)
