import os, requests, yfinance as yf
def send(text):
    token=os.getenv("TELEGRAM_TOKEN")
    chat=os.getenv("TELEGRAM_CHAT_ID")
    print(f"TOKEN exists: {bool(token)} CHAT exists: {bool(chat)}")
    if not token or not chat:
        print("SECRETS NOT FOUND!"); return
    url=f"https://api.telegram.org/bot{token}/sendMessage"
    r=requests.post(url, json={"chat_id":chat,"text":text})
    print(f"Telegram answer: {r.text}")
try:
    data=yf.download("GC=F", period="2d", interval="1h")
    price=float(data['Close'].iloc[-1])
    send(f"✅ БОТ ЗАПУЩЕН! Золото: ${price:.2f}")
except Exception as e:
    send(f"Ошибка бота: {e}")
    print(e)
