import os
import yfinance as yf
import requests

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def get_gold():
    data = yf.download("GC=F", period="3mo", interval="1d", auto_adjust=True)
    close = data['Close']
    # фикс для новой версии yfinance
    if hasattr(close, 'iloc'):
        try:
            price = float(close.iloc[-1])
        except:
            price = float(close.iloc[-1, 0])
    else:
        price = float(close[-1])
    
    e20 = float(close.ewm(span=20).mean().iloc[-1])
    e50 = float(close.ewm(span=50).mean().iloc[-1])
    trend = "📈 ЛОНГ - покупать" if e20 > e50 else "📉 ШОРТ - продавать"
    return f"🟡 GOLD: ${price:.2f}\n{trend}\nEMA20: ${e20:.2f}\nEMA50: ${e50:.2f}\n\nБот работает 24/7 ✅"

def send(t):
    try:
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", data={"chat_id": CHAT_ID, "text": t})
    except: pass

try:
    send(get_gold())
except Exception as e:
    send(f"Ошибка бота: {e}")
