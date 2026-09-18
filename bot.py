import os, requests, yfinance as yf, pandas as pd

def get_signal():
    data = yf.download("GC=F", period="1mo", interval="1d", auto_adjust=True)
    if data is None or len(data) < 20:
        return None
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
    token = os.environ["TELEGRAM_TOKEN"]
    chat = os.environ["TELEGRAM_CHAT_ID"]
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    requests.post(url, data={"chat_id": chat, "text": text})

sig = get_signal()
if sig:
    send(sig)
else:
    send("Тест - бот работает! Цена проверена")
