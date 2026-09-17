import os, yfinance as yf
from telegram import Bot
import asyncio

TOKEN = os.environ.get("TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

def get_signal():
    data = yf.Ticker("GC=F").history(period="5d", interval="15m")
    if len(data) < 50: return None
    close = data['Close']
    ema20 = close.ewm(span=20).mean().iloc[-1]
    ema50 = close.ewm(span=50).mean().iloc[-1]
    price = close.iloc[-1]
    
    # RSI
    delta = close.diff()
    gain = delta.where(delta>0,0).rolling(14).mean().iloc[-1]
    loss = -delta.where(delta<0,0).rolling(14).mean().iloc[-1]
    rsi = 100 - (100/(1+gain/(loss+0.0001)))

    if ema20 > ema50 and rsi < 70:
        return f"🟢 BUY SIGNAL GOLD\nЦена: ${price:.2f}\nEMA20: {ema20:.2f} > EMA50: {ema50:.2f}\nRSI: {rsi:.1f}\nSL: ${price*0.997:.2f} | TP: ${price*1.003:.2f}"
    elif ema20 < ema50 and rsi > 30:
        return f"🔴 SELL SIGNAL GOLD\nЦена: ${price:.2f}\nEMA20: {ema20:.2f} < EMA50: {ema50:.2f}\nRSI: {rsi:.1f}\nSL: ${price*1.003:.2f} | TP: ${price*0.997:.2f}"
    else:
        return f"⚪️ GOLD: ${price:.2f}\nОжидание... RSI {rsi:.1f}\nEMA20 {ema20:.2f} / EMA50 {ema50:.2f}"

async def main():
    bot = Bot(token=TOKEN)
    text = get_signal()
    await bot.send_message(chat_id=CHAT_ID, text=text)
    print("Sent!")

asyncio.run(main())
