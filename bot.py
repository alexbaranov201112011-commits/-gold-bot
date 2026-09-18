import os, yfinance as yf, requests

BOT_TOKEN = os.getenv("BOT_TOKEN") or os.getenv("TELEGRAM_BOT_TOKEN") or os.getenv("TELEGRAM__BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID") or os.getenv("TELEGRAM_CHAT_ID") or "6832635346"

def send(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        requests.post(url, json={"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML"}, timeout=10)
    except Exception as e:
        print(e)

try:
    df = yf.Ticker("GC=F").history(period="1d", interval="5m")
    if df.empty:
        df = yf.Ticker("XAUUSD=X").history(period="1d", interval="5m")
    price = float(df['Close'].iloc[-1])
    sma = float(df['Close'].tail(20).mean())
    signal = "BUY 📈 ЛОНГ" if price > sma else "SELL 📉 ШОРТ"

    text = f"🥇 <b>GOLD XAUUSD</b>\n\n💰 ${price:.2f}\n📊 SMA20: ${sma:.2f}\n🎯 {signal}\n\n⏰ Aktau | 24/7 ✅"
    send(text)
    print("OK sent")
except Exception as e:
    print(f"Error: {e}")
    send(f"⚠️ Рынок закрыт, ждем понедельника.\nОшибка: {e}")
