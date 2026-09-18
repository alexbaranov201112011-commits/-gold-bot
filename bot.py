import yfinance as yf
import telebot
import os
import pandas as pd
import requests
from datetime import datetime, timedelta

TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise ValueError("BOT_TOKEN не найден")
bot = telebot.TeleBot(TOKEN)

def check_news():
    try:
        now_utc = datetime.utcnow()
        now_aktau = now_utc + timedelta(hours=5)
        # Ручной блок волатильности по Актау
        if now_aktau.hour in [16, 18, 19, 20] and now_aktau.minute < 40:
            return f"⚠️ Новостное окно {now_aktau.hour}:{now_aktau.minute:02d} Актау - пропуск"

        url = "https://nfs.faireconomy.media/ff_calendar_thisweek.json"
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            data = r.json()
            today_str = now_utc.strftime("%Y-%m-%d")
            for event in data:
                if event.get('date') == today_str and 'USD' in event.get('country','') and event.get('impact') == 'High':
                    return f"🚨 USD NEWS: {event.get('title','')} в {event.get('time','')} UTC"
        return None
    except:
        return None

def get_gold_analysis():
    try:
        news_warning = check_news()

        # 1. Реальный спот
        real_spot = None
        try:
            r = requests.get("https://api.gold-api.com/price/XAU", timeout=5).json()
            real_spot = float(r.get('price', 0))
        except:
            pass

        # 2. Данные 15m
        data = yf.download("GC=F", period="5d", interval="15m", progress=False, auto_adjust=True)
        if data.empty:
            return "❌ Нет данных Yahoo"

        close = data['Close']
        if isinstance(close, pd.DataFrame):
            close = close.squeeze()

        yahoo_price = float(close.iloc[-1])
        ema9_yahoo = float(close.ewm(span=9).mean().iloc[-1])
        ema21_yahoo = float(close.ewm(span=21).mean().iloc[-1])

        if real_spot and 3000 < real_spot < 6000:
            diff = real_spot - yahoo_price
            price = real_spot
            ema9 = ema9_yahoo + diff
            ema21 = ema21_yahoo + diff
            source = "SPOT REAL"
        else:
            price = yahoo_price
            ema9 = ema9_yahoo
            ema21 = ema21_yahoo
            source = "FUTURES"

        # 3. ADR
        daily = yf.download("GC=F", period="20d", interval="1d", progress=False, auto_adjust=True)
        d_high = daily['High']
        d_low = daily['Low']
        if isinstance(d_high, pd.DataFrame):
            d_high = d_high.squeeze()
            d_low = d_low.squeeze()
        adr = float((d_high - d_low).tail(14).mean())

        trend_strength = abs(ema9 - ema21)
        flat_threshold = price * 0.003

        header = f"🟡 GOLD {source}: ${price:.2f} | ADR: ${adr:.1f}\n"
        if news_warning:
            header += f"\n{news_warning}\n"

        if adr < 25:
            return header + f"\n⛔ НЕТ СИГНАЛА\nADR {adr:.1f} - рынок мертвый"

        if trend_strength < flat_threshold:
            return header + f"EMA9 {ema9:.2f} | EMA21 {ema21:.2f}\n\n⛔ ФЛЕТ, БЕЗ СДЕЛКИ\nСила {trend_strength:.2f}$ < {flat_threshold:.2f}$"

        # БЛОК НОВОСТЕЙ
        if news_warning:
            return header + f"EMA9 {ema9:.2f} | EMA21 {ema21:.2f}\n\n⛔ НОВОСТИ - ПРОПУСКАЕМ СИГНАЛ"

        is_long = ema9 > ema21
        direction = "📈 LONG" if is_long else "📉 SHORT"

        if is_long:
            sl = price - adr * 0.4
            tp1 = price + adr * 0.3
            tp2 = price + adr * 0.6
            tp3 = price + adr * 0.9
        else:
            sl = price + adr * 0.4
            tp1 = price - adr * 0.3
            tp2 = price - adr * 0.6
            tp3 = price - adr * 0.9

        return (
            header +
            f"EMA9: {ema9:.2f} | EMA21: {ema21:.2f}\n\n"
            f"{direction} - СИГНАЛ ✅\n"
            f"Вход: ~${price:.2f}\n"
            f"ТП1: ${tp1:.2f} (50%)\n"
            f"ТП2: ${tp2:.2f} (30%)\n"
            f"ТП3: ${tp3:.2f} (20%)\n"
            f"СЛ: ${sl:.2f}\n\n"
            f"Лот 0.06 = 0.03 / 0.018 / 0.012"
        )
    except Exception as e:
        return f"Ошибка: {e}"

@bot.message_handler(commands=['start'])
def start_cmd(message):
    bot.reply_to(message, "Бот готов ✅\n/gold - анализ золота с 3 ТП\nНовости блокируются автоматически")

@bot.message_handler(commands=['gold'])
def gold_cmd(message):
    bot.send_chat_action(message.chat.id, 'typing')
    bot.reply_to(message, get_gold_analysis())

# --- ЗАПУСК ---
if __name__ == "__main__":
    # На GitHub Actions только проверка, без висения
    if os.getenv("GITHUB_ACTIONS"):
        print("✅ Check OK - code valid")
        print(get_gold_analysis())
    else:
        print("🚀 Bot polling 24/7 started")
        bot.infinity_polling(none_stop=True, timeout=60)
