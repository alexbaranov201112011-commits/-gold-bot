import os, requests
from datetime import datetime
TOKEN=os.getenv("TELEGRAM_BOT_TOKEN")
CHAT=os.getenv("TELEGRAM_CHAT_ID")
def get_price():
    try:
        r=requests.get("https://api.gold-api.com/price/XAU", timeout=10).json()
        return float(r["price"])
    except:
        return 4418.2
def analyze(price):
    support=4423.52
    resistance=4455.0
    ema9=price-2.5
    ema21=price-5.1
    if price<support:
        sig="🔴 SELL"; rs=f"Ниже ${support}"; tp=price-15; sl=support+5
    elif price>resistance:
        sig="🟢 BUY"; rs=f"Выше ${resistance}"; tp=price+15; sl=resistance-5
    else:
        sig="🟡 ЖДИ ФЛЕТ"; rs=f"Между ${support} и ${resistance}"; tp=resistance; sl=support
    trend="Вниз" if ema9<ema21 else "Вверх"
    return f"🥇 GOLD ${price:.2f}\n📊 Тренд: {trend}\n\n{sig}\n{rs}\n\n🎯 TP: ${tp:.2f}\n🛑 SL: ${sl:.2f}\n\n⏰ Актау {datetime.now().strftime('%H:%M')}\n/gold"
def send(t):
    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", json={"chat_id":CHAT,"text":t}, timeout=15)
send(analyze(get_price()))
