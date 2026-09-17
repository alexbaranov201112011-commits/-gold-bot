import os, yfinance as yf
from telegram import Bot
import asyncio

TOKEN = os.environ.get("TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

def get_data():
    df = yf.Ticker("GC=F").history(period="5d", interval="15m")
    if len(df) < 60: return None, None
    close = df['Close']
    ema20 = close.ewm(span=20).mean()
    ema50 = close.ewm(span=50).mean()
    price = close.iloc[-1]
    
    delta = close.diff()
    gain = delta.where(delta>0,0).rolling(14).mean()
    loss = -delta.where(delta<0,0).rolling(14).mean()
    rsi = 100 - (100/(1+gain/(loss+0.0001)))
    
    # ADX для флета
    high, low = df['High'], df['Low']
    tr = (high - low).abs()
    atr = tr.rolling(14).mean().iloc[-1]
    adx_strong = atr > (price * 0.001)  # волатильность есть
    
    return {
        "price": price,
        "ema20": ema20.iloc[-1],
        "ema50": ema50.iloc[-1],
        "rsi": rsi.iloc[-1],
        "strong": adx_strong,
        "prev_ema20": ema20.iloc[-2],
        "prev_ema50": ema50.iloc[-2]
    }, df

def build_signal(d):
    p = d["price"]
    # Пересечение
    cross_up = d["prev_ema20"] <= d["prev_ema50"] and d["ema20"] > d["ema50"]
    cross_down = d["prev_ema20"] >= d["prev_ema50"] and d["ema20"] < d["ema50"]
    
    if not d["strong"]:
        return None, "WAIT"  # боковик, не торгуем

    if cross_up and 35 < d["rsi"] < 68:
        msg = f"🟢 BUY GOLD @ ${p:.2f}\nПересечение EMA20 вверх\nRSI: {d['rsi']:.1f}\nSL: ${p*0.996:.2f} (-0.4%)\nTP1: ${p*1.004:.2f} TP2: ${p*1.008:.2f}"
        return msg, "BUY"
    if cross_down and 32 < d["rsi"] < 65:
        msg = f"🔴 SELL GOLD @ ${p:.2f}\nПересечение EMA20 вниз\nRSI: {d['rsi']:.1f}\nSL: ${p*1.004:.2f} (+0.4%)\nTP1: ${p*0.996:.2f} TP2: ${p*0.992:.2f}"
        return msg, "SELL"
    return None, "WAIT"

async def main():
    bot = Bot(token=TOKEN)
    d, _ = get_data()
    if not d:
        return
    msg, sig = build_signal(d)
    
    # Читаем прошлый сигнал
    last = ""
    try:
        with open("last_signal.txt","r") as f: last = f.read().strip()
    except: pass

    if sig == "WAIT":
        print(f"WAIT - RSI {d['rsi']:.1f}")
        return

    if sig != last and msg:
        await bot.send_message(chat_id=CHAT_ID, text=msg)
        with open("last_signal.txt","w") as f: f.write(sig)
        print(f"Sent {sig}")
    else:
        print(f"No new signal, last {last} now {sig}")

asyncio.run(main())
