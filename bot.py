import os
import yfinance as yf
import requests

# --- ЧИТАЕМ ВСЕ ВАРИАНТЫ СЕКРЕТОВ ---
BOT_TOKEN = (
    os.getenv("BOT_TOKEN") or 
    os.getenv("TELEGRAM_BOT_TOKEN") or 
    os.getenv("TELEGRAM__BOT_TOKEN") or 
    os.getenv("TELEGRAM_TOKEN") or
    os.getenv("BOT__TOKEN")
)
CHAT_ID = (
    os.getenv("CHAT_ID") or 
    os.getenv("TELEGRAM_CHAT_ID") or 
    os.getenv("TELEGRAM__CHAT_ID") or 
    "6832635346"
)

print(f"DEBUG: BOT_TOKEN exists={bool(BOT_TOKEN)}, CHAT_ID={CHAT_ID}")

def send_telegram(text):
    if not BOT_TOKEN:
        print("ERROR: No BOT_TOKEN found! Check Secrets")
        return
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        r = requests.post(url, json={"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML"})
        print(f"Telegram response: {r.status_code} - {r.text[:200]}")
    except Exception as e:
        print(f"Telegram error: {e}")

def get_gold_price():
    try:
        # Пробуем золото
        ticker = yf.Ticker("GC=F")
        data = ticker.history(period="1d", interval="1m")
        if data.empty:
            ticker = yf.Ticker("XAUUSD=X")
            data = ticker.history(period="1d", interval="1m")
        price = data['Close'].iloc[-1]
        return round(float(price), 2), data
    except Exception as e:
        print(f"Yfinance error: {e}")
        return None, None

# --- ОСНОВНАЯ ЛОГИКА ---
price, df = get_gold_price()

if price is None:
    msg = "⚠️ <b>Gold Bot</b>\nНе смог получить цену золота. Рынок закрыт (суббота) или ошибка yfinance.\n\nDEBUG: BOT_TOKEN exists={}\nCHAT_ID={}".format(bool(BOT_TOKEN), CHAT_ID)
    send_telegram(msg)
else:
    # Простой анализ
    try:
        sma20 = df['Close'].tail(20).mean()
        signal = "BUY 📈" if price > sma20 else "SELL 📉"
    except:
        signal = "NEUTRAL"
        sma20 = price

    msg = f"""<b>🥇 GOLD SIGNAL XAUUSD</b>

💰 Цена: <b>${price}</b>
📊 SMA20: ${round(sma20,2)}
🎯 Сигнал: <b>{signal}</b>

⏰ Время: Aktau
✅ Бот работает 24/7
CHAT_ID: {CHAT_ID}"""

    send_telegram(msg)

print("Done")
