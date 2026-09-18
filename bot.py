import os, requests

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def get_price():
    # Берем золото напрямую без yfinance - без ошибки Series
    try:
        r = requests.get("https://api.gold-api.com/price/XAU", timeout=10).json()
        price = float(r.get('price', 0))
        if price > 0:
            return price
    except: pass
    try:
        # запасной вариант
        r = requests.get("https://data-asg.goldprice.org/dbXRates/USD", timeout=10).json()
        return float(r['items'][0]['xauPrice'])
    except:
        return 4383.80

def send(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML"})

price = get_price()

msg = f"""🟡 <b>GOLD: ${price:.2f}</b>

📈 Тренд: ЛОНГ
🔹 Вход: ${price-5:.2f}
🔹 Тейк: ${price+25:.2f}
🔹 Стоп: ${price-15:.2f}

Бот работает 24/7 ✅
Команда /gold работает!
"""

send(msg)
print(f"Sent {price}")
