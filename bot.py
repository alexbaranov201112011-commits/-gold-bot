import os, yfinance as yf, requests

BOT_TOKEN = os.getenv("BOT_TOKEN") or os.getenv("TELEGRAM_BOT_TOKEN") or os.getenv("TELEGRAM__BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID") or os.getenv("TELEGRAM_CHAT_ID") or "6832635346"

def send(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML"})

try:
    df = yf.Ticker("GC=F").history(period="1d", interval="5m")
    if df.empty: df = yf.Ticker("XAUUSD=X").history(period="1d", interval="5m")
    price = float(df['Close'].iloc[-1])
    sma20 = float(df['Close'].tail(20).mean())
    signal = "BUY 📈 ЛОНГ - СИГНАЛ" if price > sma20 else "SELL 📉 ШОРТ - СИГНАЛ"
    
    msg = f"""🥇 <b>GOLD SIGNAL XAUUSD</b>

💰 Цена: <b>${price:.2f}</b>
📊 SMA20: ${sma20:.2f}
🎯 Сигнал: <b>{signal}</b>

⏰ Aktau | Бот 24/7 ✅"""
    send(msg)
    print(f"Sent {price}")
except Exception as e:
    send(f"⚠️ Бот ошибка: {e}\nРынок закрыт, ждем открытия в понедельник.")
    print(e)
