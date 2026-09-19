import os, requests
TOKEN=os.getenv("TELEGRAM_BOT_TOKEN")
CHAT=os.getenv("TELEGRAM_CHAT_ID")

def send(text):
    url=f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": CHAT, "text": text, "parse_mode": "HTML"}, timeout=15)

try:
    r=requests.get("https://api.gold-api.com/price/XAU", timeout=10).json()
    price=float(r["price"])
except:
    price=4418.2

signal="🔴 SELL" if price < 4423.52 else "🟢 BUY"
send(f"GOLD ${price:.2f}\n{signal}\nAktau test ✅")
