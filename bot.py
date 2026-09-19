import os, requests
from datetime import datetime

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML"}, timeout=10)

try:
    price = requests.get("https://api.gold-api.com/price/XAU", timeout=10).json().get("price", 4418)
    price = float(price)
except:
    price = 4418.20

signal = "🔴 SELL" if price < 4423 else "🟢 BUY"
now = datetime.now().strftime("%H:%M")

msg = f"🏆 <b>GOLD ${price:.2f}</b>\n{signal}\n⏰ {now} Aktau | 24/7 ✅"
send(msg)
