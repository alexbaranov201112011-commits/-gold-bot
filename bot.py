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
    # Проверяем новости по USD с ForexFactory
    try:
        # Время Актау UTC+5
        now_utc = datetime.utcnow()
        now_aktau = now_utc + timedelta(hours=5)

        # Основные часы новостей США: 16:30, 18:30, 20:00 по Актау
        news_hours = [16, 18, 19, 20] # часы когда часто новости
        # Если сейчас новостной час - предупреждаем
        if now_aktau.hour in news_hours and now_aktau.minute < 40:
            return f"⚠️ Сейчас новостное время ({now_aktau.hour}:{now_aktau.minute:02d} Актау). Возможна высокая волатильность."

        # Пробуем скачать календарь
        url = "https://nfs.faireconomy.media/ff_calendar_thisweek.json"
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            data = r.json()
            today_str = now_utc.strftime("%Y-%m-%d")
            for event in data:
                if event.get('date') == today_str and 'USD' in event.get('country','') and event.get('impact') == 'High':
                    event_time = event.get('time','')
                    title = event.get('title','')
                    # Если новость в ближайшие 2 часа
                    return f"🚨 СЕГОДНЯ НОВОСТИ USD: {title} в {event_time} UTC. Осторожно!"
        return None
    except:
        return None

def get_gold_analysis():
    try:
        news_warning = check_news()

        data = yf.download("GC=F", period="5d", interval="15m", progress=False, auto_adjust=True)
        if data.empty:
            return "Ошибка: нет данных yfinance"

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

        header = f"🟡 GOLD: ${price:.1f} | ADR: ${adr:.1f}\n"
        if news_warning:
            header += f"\n{news_warning}\n"

        if adr < 35:
            return header + f"\n⛔ НЕТ СИГНАЛА\nПричина: Волатильность низкая ADR {adr:.1f}"

        if trend_strength < flat_threshold:
            return header + f"EMA9 {ema9:.1f} | EMA21 {ema21:.1f}\n\n⛔ ФЛЕТ, БЕЗ СДЕЛКИ\nТренд слабый {trend_strength:.1f}$ < {flat_threshold:.1f}$"

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

        # Если есть новости - добавляем предупреждение но сигнал даем
        footer = "\n⚠️ Новости! Уменьши лот x2" if news_warning else ""
        return header + f"EMA9: {ema9:.1f} | EMA21: {ema21:.1f}\n\n{direction} - СИГНАЛ ✅{footer}\nВход: ~${price:.1f}\nТП1: ${tp1:.1f}\nТП2: ${tp2:.1f}\nСЛ: ${sl:.1f}"

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
