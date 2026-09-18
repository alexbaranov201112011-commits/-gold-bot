import yfinance as yf
import pandas as pd
import time
import os
import requests

TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def get_signal():
    # Скачиваем золото
    data = yf.download("GC=F", period="1d", interval="5m")
    if len(data) < 20:
        return None
    
    close = data['Close']
    
    # Простой RSI
    delta = close.diff()
    gain = delta.where(delta>0,0).rolling(14).mean()
    loss = -delta.where(delta<0,0).rolling(14).mean()
    rsi = 100 - (100/(1+gain/(loss+0.001)))
    rsi_last = float(rsi.iloc[-1])

    price = float(close.iloc[-1])
    
    if rsi_last < 30:
        return f"🟢 BUY GOLD\nЦена: {price:.2f}\nRSI: {rsi_last:.1f} (перепродан)"
    elif rsi_last > 70:
        return f"🔴 SELL GOLD\nЦена: {price:.2f}\nRSI: {rsi_last:.1f} (перекуплен)"
    else:
        return None

def send(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": text})

# Проверка 1 раз
signal = get_signal()
if signal:
    send(signal)
    print("Отправлен:", signal)
else:
    print("Сигнала нет, ждем")
