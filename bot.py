import os, requests, yfinance as yf

def send(msg):
    token = os.getenv("TELEGRAM_TOKEN") or os.getenv("TOKEN")
    chat = os.getenv("TELEGRAM_CHAT_ID") or os.getenv("CHAT_ID")
    if not token or not chat:
        print("SECRETS NOT FOUND")
        return
    r = requests.post(f"https://api.telegram.org/bot{token}/sendMessage", data={"chat_id": chat, "text": msg, "parse_mode": "HTML"})
    print(r.text)

price = yf.Ticker("GC=F").history(period="1d")["Close"].iloc[-1]
send(f"✅ БОТ ЗАПУЩЕН!\nЗолото: ${price:.2f}\nБудет работать 24/7 каждые 15 мин")
print(f"Done price {price}")
