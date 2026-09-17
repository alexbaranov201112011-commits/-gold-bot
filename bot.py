import os, yfinance as yf
from telegram.ext import Application, CommandHandler
from datetime import datetime
TOKEN=os.environ.get("TOKEN")
CHAT_ID=int(os.environ.get("CHAT_ID","6832635346"))
async def get_sig():
    data=yf.download("GC=F",period="1d",interval="5m",progress=False)
    c=float(data['Close'].iloc[-1])
    data['E20']=data['Close'].ewm(20).mean()
    data['E50']=data['Close'].ewm(50).mean()
    e20=float(data['E20'].iloc[-1]); e50=float(data['E50'].iloc[-1])
    sig="🔔 BUY" if e20>e50 else "🔔 SELL"
    sl=c-10 if "BUY" in sig else c+10
    tp=c+20 if "BUY" in sig else c-20
    return f"{sig} XAUUSD 0.25 лот\nВход: {c:.2f}\nSL: {sl:.2f}\nTP: {tp:.2f}\n⏰ {datetime.now().strftime('%H:%M')} | YouTrade"
async def start(u,c): await u.message.reply_text("Бот работает! /signal")
async def signal_cmd(u,c): await u.message.reply_text(await get_sig())
async def job(c): await c.bot.send_message(chat_id=CHAT_ID,text=await get_sig())
def main():
    app=Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start",start))
    app.add_handler(CommandHandler("signal",signal_cmd))
    app.job_queue.run_repeating(job,interval=3600,first=15)
    app.run_polling()
if __name__=="__main__": main()
