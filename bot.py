import yfinance as yf
import telebot
import os
import time
from datetime import datetime

TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

def get_gold_analysis():
    try:
        data = yf.download("GC=F", period="5d", interval="15m", progress=False)
        if data.empty:
            return None
            
        close = data['Close']
        high = data['High']
        low = data['Low']
        
        price = float(close.iloc[-1])
        ema9 = float(close.ewm(span=9).mean().iloc[-1])
        ema21 = float(close.ewm(span=21).mean().iloc[-1])
        
        # ADR 14 дней на дневке
        daily = yf.download("GC=F", period="20d", interval="1d", progress=False)
        adr = float((daily['High'] - daily['Low']).tail(14).mean())
        
        # --- ФИЛЬТРЫ ---
        trend_strength = abs(ema9 - ema21)
        flat_threshold = price * 0.0015  # 0.15% от цены
        
        if adr < 35:
            return f"🟡 GOLD: ${price:.1f} | ADR: ${adr:.1f}\n\n⛔ НЕТ СИГНАЛА\nПричина: Низкая волатильность (ADR {adr:.1f} < 35)\nЖдем движения."
        
        if trend_strength < flat_threshold:
            return f"🟡 GOLD: ${price:.1f} | ADR: ${adr:.1f}\nEMA9: {ema9:.1f} | EMA21: {ema21:.1f}\n\n⛔ ФЛЕТ, БЕЗ СДЕЛКИ\nEMA почти равны, нет тренда.\nЛучше не лезть."
        
        # Если фильтры прошли - даем сигнал
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
            
        return f"""🟡 GOLD: ${price:.1f} | ADR: ${adr:.1f}
EMA9: {ema9:.1f} | EMA21: {ema21:.1f}

{direction} - ЕСТЬ СИГНАЛ ✅

Вход: ~${price:.1f}
ТП1: ${tp1:.1f}
ТП2: ${tp2:.1f}
СЛ: ${sl:.1f}

Тренд сильный: {trend_strength:.1f}$"""

    except Exception as e:
        return f"Ошибка: {e}"

@bot.message_handler(commands=['gold'])
def gold_cmd(message):
    bot.send_chat_action(message.chat.id, 'typing')
    result = get_gold_analysis()
    bot.reply_to(message, result)

@bot.message_handler(commands=['start'])
def start_cmd(message):
    bot.reply_to(message, "Бот готов. Жми /gold")

print("Bot started...")
bot.infinity_polling(timeout=60, long_polling_timeout=60)
