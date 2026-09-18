import os
import requests
import yfinance as yf

def send(text):
    token = os.environ.get("TELEGRAM_TOKEN") or os.environ.get("TOKEN") or ""
    chat = os.environ.get("TELEGRAM_CHAT_ID") or os.environ.get("CHAT_ID") or ""
    print(f"Checking token={bool(token)} chat={bool(chat)}")
    if not token or not chat:
        print("NO SECRETS FOUND - add them in Settings->Secrets")
        return
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    r = requests.post(url, data={"chat_id": chat, "text": text, "parse_mode": "HTML"})
    print(f"Telegram answer: {r.text}")

try:
    data = yf.Ticker("GC=F").history(period="1d")
    price = data["Close"].iloc[-1]
    print(f"Price {price}")
    send(f"✅ <b>БОТ ЗАПУЩЕН!</b>\n\nЗолото: ${price:.2f}\nБот работает 24/7")
except Exception as e:
    print(f"Error {e}")
