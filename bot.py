import os, requests
import yfinance as yf

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML"}, timeout=15)

# Цена
try:
    r = requests.get("https://api.gold-api.com/price/XAU", timeout=10).json()
    price = float(r.get("price", 4418.2))
except:
    price = 4418.2

# SMA20
try:
    hist = yf.Ticker("GC=F").history(period="1mo", interval="1h")
    sma20 = float(hist['Close'].rolling(20).mean().iloc[-1])
except:
    sma20 = 4423.52

# Сигнал
if price < sma20:
    sig = "🔴 SELL 📉 ШОРТ"
else:
    sig = "🟢 BUY 📈 ЛОНГ"

msg = f"🏆 GOLD XAUUSD\n\n💰 ${price:.2f}\n📊 SMA20: ${sma20:.2f}\n🎯 {sig}\n\n⏰ Aktau | 24/7 ✅"
send(msg)
