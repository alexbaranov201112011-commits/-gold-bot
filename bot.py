import yfinance as yf
import pandas as pd
import os
import requests

TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def get_signal():
    data = yf.download("GC=F", period="1d", interval="5m")
    if data is None or len(data) < 20:
        return None

    # Берем Close и делаем из него обычный список
    close = data['Close']
    if isinstance(close, pd.DataFrame):
        close = close.iloc[:, 0]
    close = pd.Series(close)
    
    delta = close.diff()
    gain = delta.where(delta > 0, 0).rolling(14).mean()
    loss = -delta.where(delta < 0, 0).rolling(14).mean()
    rs = gain / (loss + 0.0001)
    rsi = 100 - (100 / (1 + rs))
    
    if isinstance(rsi, pd.DataFrame):
        rsi = rsi.iloc[:, 0]
    rsi = pd.Series(rsi)

    price = float(close.iloc[-1])
    rsi_last = float(rsi.iloc[-1])

    print(f"Price {price} RSI {rsi_last}")

    if rsi_last < 30:
        return f"BUY GOLD - {price:.2f} RSI {rsi_last:.1f}"
    if rsi_last > 70:
        return f"SELL GOLD - {price:.2f} RSI {rsi_last:.1f}"
    return None

def send(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": text})

sig = get_signal()
if sig:
    send(sig)
