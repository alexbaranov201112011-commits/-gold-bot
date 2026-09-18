import os
import yfinance as yf
import requests

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def get_gold_data():
    try:
        data = yf.download("GC=F", period="3mo", interval="1d", auto_adjust=True)
        if data.empty:
            return None, "Нет данных"
        
        close = data['Close']
        # ИСПРАВЛЕНИЕ ОШИБКИ Series
        price = float(close.iloc[-1])
        
        ema20 = float(close.ewm(span=20).mean().iloc[-1])
        ema50 = float(close.ewm(span=50).mean().iloc[-1])
        
        trend = "📈 ЛОНГ" if ema20 > ema50 else "📉 ШОРТ"
        
        text = f"🟡 GOLD: ${price:.2f}\n{trend}\nEMA20: ${ema20:.2f}\nEMA50: ${ema50:.2f}\n\nБот работает 24/7 ✅"
        return text, None
    except Exception as e:
        return None, str(e)

def send(msg):
    if not TOKEN or not CHAT_ID: return
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg})
    except: pass

msg, err = get_gold_data()
if err:
    send(f"Ошибка бота: {err}")
else:
    send(msg)

print("Done")
