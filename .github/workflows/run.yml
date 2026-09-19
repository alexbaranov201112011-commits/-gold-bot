import os, requests
from datetime import datetime
TOKEN=os.getenv("TELEGRAM_BOT_TOKEN")
CHAT=os.getenv("TELEGRAM_CHAT_ID")

def get_price():
    try:
        r=requests.get("https://api.gold-api.com/price/XAU",timeout=10).json()
        return float(r["price"])
    except:
        return 4420.0

def analyze(p):
    supp=4423.52
    res=4455.0
    if p<supp:
        return f"🔴 CALL: SELL GOLD\n💰 ${p:.2f}\nПричина: пробой {supp}\n🎯 TP: ${p-15:.2f}\n🛑 SL: ${supp+5:.2f}"
    elif p>res:
        return f"🟢 CALL: BUY GOLD\n💰 ${p:.2f}\nПричина: пробой {res}\n🎯 TP: ${p+15:.2f}\n🛑 SL: ${res-5:.2f}"
    else:
        return f"🟡 CALL: WAIT\n💰 ${p:.2f}\nФлэт между {supp} и {res}\nЖди пробоя"

def send(t):
    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage",json={"chat_id":CHAT,"text":t},timeout=15)

send(analyze(get_price()))
