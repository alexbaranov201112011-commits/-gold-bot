import os
import yfinance as yf
from telegram import Bot
import asyncio

TOKEN = os.environ.get("TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

async def main():
    bot = Bot(token=TOKEN)
    try:
        g = yf.Ticker("GC=F").history(period="1d")
        price = float(g['Close'].iloc[-1])
        text = f"🟡 GOLD: ${price:.2f}\nБот работает 24/7 ✅"
    except:
        text = "Gold Bot онлайн ✅ Работает!"
    await bot.send_message(chat_id=CHAT_ID, text=text)

asyncio.run(main())
